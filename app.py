import html
import streamlit as st
from openai import OpenAI

# Page config (must be the first Streamlit command)
st.set_page_config(
    page_title="Company Research Assistant",
    page_icon="📊",
    layout="centered"
)

# ---------------- Styling ----------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Hide default Streamlit chrome */
    #MainMenu, footer, header {visibility: hidden;}

    /* Base typography + spacing */
    html, body, [class*="css"], .stMarkdown, .stTextInput, .stTextArea, .stRadio {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .block-container {max-width: 820px; padding-top: 3rem; padding-bottom: 4rem;}

    /* Hero */
    .hero {margin-bottom: 2.5rem;}
    .hero h1 {
        font-size: 2.7rem; font-weight: 700; letter-spacing: -0.03em;
        color: #1D1D1F; margin: 0 0 0.6rem 0; line-height: 1.05;
    }
    .hero p {
        font-size: 1.08rem; color: #6E6E73; margin: 0; line-height: 1.55;
        max-width: 640px;
    }

    /* Section cards */
    .brief-card {
        background: #FFFFFF;
        border: 1px solid #EFE7DD;
        border-left: 4px solid #C2552F;
        border-radius: 14px;
        padding: 1.4rem 1.7rem;
        margin: 1.1rem 0;
        box-shadow: 0 1px 4px rgba(60, 40, 20, 0.05);
    }
    .brief-card h3 {
        margin: 0 0 0.7rem 0; font-size: 1.2rem; font-weight: 700;
        color: #1D1D1F; letter-spacing: -0.01em;
    }
    .brief-card ul, .brief-card ol {margin: 0; padding-left: 1.15rem;}
    .brief-card li {margin-bottom: 0.45rem; line-height: 1.6; color: #3A3A3C;}
    .brief-card p {line-height: 1.6; color: #3A3A3C; margin: 0 0 0.5rem 0;}
    .brief-title {
        font-size: 1.6rem; font-weight: 700; letter-spacing: -0.02em;
        color: #1D1D1F; margin: 0.5rem 0 1.2rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Load the API key safely ---
try:
    api_key = st.secrets["OPENROUTER_API_KEY"]
except Exception:
    api_key = None

if not api_key:
    st.error(
        "⚠️ This app isn't fully configured yet — the OpenRouter API key is missing. "
        "If you're the owner, add OPENROUTER_API_KEY under your app's Settings → Secrets."
    )
    st.stop()

# Configure OpenRouter client
client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)


# Read text from an uploaded PDF, Word (.docx) or .txt file
def extract_text_from_upload(file):
    name = file.name.lower()
    if name.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(file)
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    if name.endswith(".docx"):
        import docx
        document = docx.Document(file)
        return "\n".join(p.text for p in document.paragraphs)
    return file.read().decode("utf-8", errors="ignore")


# Build the instruction prompt based on mode and any tailoring context
def build_prompt(text, selected_mode, user_context=""):
    if selected_mode == "Analyze a job description":
        base = f"""
You are an expert career coach and recruiter.
Analyze the following job description and create a concise preparation brief
to help a candidate prepare for applying and interviewing.

Job description:
{text}

Format using these sections, each starting with '## ' on its own line:

## Role Expectations
- 3-5 bullet points on what the role involves and the level expected

## Key Skills & Qualifications
- 3-5 bullet points on the most important skills and experience sought

## Interview Focus Areas
- 3-5 bullet points on what is likely to be tested or emphasized

## Likely Interview Questions
- 3-5 questions the candidate may be asked

## Smart Questions to Ask
- Exactly 3 thoughtful questions for the candidate to ask the interviewer
"""
        tail = f"""

The candidate shared this about their own background:
{user_context}

Add one FINAL section starting with '## ':

## How You Fit & What to Emphasize
- 3-5 specific, honest points: where their background fits the role, any gaps to address, and what to emphasize
""" if user_context.strip() else ""
        rules = "\n\nIMPORTANT: Do not add any title, intro, or closing remarks. Output only the '## ' sections. Keep it practical, concise, and interview-focused."
        return base + tail + rules

    base = f"""
You are an expert business research analyst.
Create a concise one-page research brief.

Input:
{text}

Format using these sections, each starting with '## ' on its own line:

## Company Overview
- 3-5 bullet points

## Business Model
- 3-5 bullet points

## Recent Developments
- 3-5 bullet points

## Key Challenges
- 3-5 bullet points

## Competitive Landscape
- 3-5 bullet points

## Smart Questions to Ask
- Exactly 3 thoughtful questions
"""
    tail = f"""

The user shared this about why they're researching this company:
{user_context}

Add one FINAL section starting with '## ':

## How This Maps to Your Goal
- 3-5 specific points connecting the company's situation to their stated goal, and how to use them in an interview or meeting
""" if user_context.strip() else ""
    rules = "\n\nIMPORTANT: Do not add any title, intro, or closing remarks. Output only the '## ' sections. Keep it practical, concise, and interview-focused."
    return base + tail + rules


def parse_sections(text):
    """Split a markdown brief into (title, body) pairs at any '#' heading line."""
    sections = []
    title = None
    body = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
            if heading:
                if title is not None:
                    sections.append((title, "\n".join(body).strip()))
                title = heading
                body = []
                continue
        if title is not None:
            body.append(line)
    if title is not None:
        sections.append((title, "\n".join(body).strip()))
    return sections


def render_brief(markdown_text):
    """Render each section as its own styled card."""
    try:
        import markdown as md
        sections = parse_sections(markdown_text)
        if not sections:
            st.markdown(markdown_text)
            return
        for title, body in sections:
            body_html = md.markdown(body, extensions=["extra"]) if body else ""
            card = (
                f'<div class="brief-card"><h3>{html.escape(title)}</h3>{body_html}</div>'
            )
            st.markdown(card, unsafe_allow_html=True)
    except Exception:
        st.markdown(markdown_text)


# ---------------- UI ----------------

st.markdown(
    '<div class="hero"><h1>Company Research Assistant</h1>'
    '<p>Research a company or analyze a job description, and get a structured, '
    'tailored brief for interviews, networking, and client meetings.</p></div>',
    unsafe_allow_html=True,
)

# Mode selector
mode = st.radio(
    "What would you like to do?",
    ["Research a company", "Analyze a job description"],
    horizontal=True
)

# Input area depends on the chosen mode
user_text = ""
uploaded_file = None
user_context = ""

if mode == "Research a company":
    user_text = st.text_area(
        "Company Name",
        placeholder="Enter a company name (e.g., Apple)",
        height=120
    )
    user_context = st.text_input(
        "Your goal (optional)",
        placeholder="e.g., interviewing for a strategy analyst role"
    )
    button_label = "Generate Research Brief"
else:
    uploaded_file = st.file_uploader(
        "Upload a job description (PDF, Word, or .txt) — optional",
        type=["pdf", "docx", "txt"]
    )
    st.caption("…or paste the job description below instead.")
    user_text = st.text_area(
        "Job Description",
        placeholder="Paste the full job description here",
        height=180
    )
    user_context = st.text_area(
        "Your background (optional)",
        placeholder="Paste a short summary of your experience (or your resume text) for tailored advice",
        height=120
    )
    button_label = "Analyze Job Description"

# Generate button
if st.button(button_label, type="primary"):
    final_input = ""
    error_shown = False

    if mode == "Analyze a job description" and uploaded_file is not None:
        try:
            final_input = extract_text_from_upload(uploaded_file)
        except Exception as e:
            st.error(f"Sorry, I couldn't read that file. Please try pasting the text instead. ({e})")
            error_shown = True
    else:
        final_input = user_text

    if not error_shown:
        if not final_input.strip():
            st.warning("Please enter a company name, or paste / upload a job description.")
        else:
            try:
                with st.spinner("Working on it..."):
                    response = client.chat.completions.create(
                        model="deepseek/deepseek-chat-v3-0324",
                        messages=[
                            {"role": "user", "content": build_prompt(final_input, mode, user_context)}
                        ]
                    )
                    result = response.choices[0].message.content
                    st.session_state["brief"] = result
                    st.session_state["brief_input"] = final_input.strip()
                    st.session_state["brief_mode"] = mode
            except Exception as e:
                st.error(f"Error: {e}")

# Show the brief (if one exists), with download and clear options
if "brief" in st.session_state:
    st.markdown("<div class='brief-title'>Your Brief</div>", unsafe_allow_html=True)
    render_brief(st.session_state["brief"])
    st.caption("⚠️ AI-generated — please verify important facts before relying on them.")

    if st.session_state.get("brief_mode") == "Research a company":
        raw_name = st.session_state.get("brief_input", "company")
        safe_name = "".join(c if c.isalnum() else "_" for c in raw_name).strip("_")[:40]
        file_name = f"{safe_name or 'company'}_brief.md"
    else:
        file_name = "job_description_analysis.md"

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="⬇️ Download brief (.md)",
            data=st.session_state["brief"],
            file_name=file_name,
            mime="text/markdown"
        )
    with col2:
        if st.button("🗑️ Clear"):
            st.session_state.pop("brief", None)
            st.session_state.pop("brief_input", None)
            st.session_state.pop("brief_mode", None)
            st.rerun()