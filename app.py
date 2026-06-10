import streamlit as st
from openai import OpenAI

# Page config (must be the first Streamlit command)
st.set_page_config(
    page_title="Company Research Assistant",
    page_icon="📊",
    layout="centered"
)

# Small cosmetic touch: hide Streamlit's default menu and footer for a cleaner look
st.markdown(
    "<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>",
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

Format EXACTLY using these sections (put '## ' before each heading):

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

Add one FINAL section tailored to them:

## How You Fit & What to Emphasize
- 3-5 specific, honest points: where their background fits the role, any gaps to address, and what to emphasize in their application and interview
""" if user_context.strip() else ""
        return base + tail + "\n\nKeep the output practical, concise, and interview-focused."

    base = f"""
You are an expert business research analyst.
Create a concise one-page research brief.

Input:
{text}

Format EXACTLY using these sections (put '## ' before each heading):

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

Add one FINAL section tailored to them:

## How This Maps to Your Goal
- 3-5 specific points connecting the company's situation to their stated goal, and how to use them in an interview or meeting
""" if user_context.strip() else ""
    return base + tail + "\n\nKeep the output practical, concise, and interview-focused."


# Pick an icon for a section based on its title
SECTION_ICONS = {
    "company overview": "🏢",
    "business model": "💰",
    "recent developments": "📰",
    "key challenges": "⚠️",
    "competitive landscape": "⚔️",
    "smart questions": "❓",
    "role expectations": "🎯",
    "key skills": "🛠️",
    "interview focus": "🔍",
    "likely interview questions": "💬",
    "how you fit": "🤝",
    "how this maps": "🧭",
}


def icon_for(title):
    t = title.lower()
    for key, emoji in SECTION_ICONS.items():
        if key in t:
            return emoji
    return "📌"


def render_brief(markdown_text):
    """Split the brief into '## ' sections and show each as its own card."""
    sections = []
    current_title = None
    current_body = []
    for line in markdown_text.split("\n"):
        if line.strip().startswith("## "):
            if current_title is not None:
                sections.append((current_title, "\n".join(current_body).strip()))
            current_title = line.strip()[3:].strip()
            current_body = []
        elif current_title is not None:
            current_body.append(line)
    if current_title is not None:
        sections.append((current_title, "\n".join(current_body).strip()))

    if not sections:
        st.markdown(markdown_text)
        return

    for title, body in sections:
        with st.container(border=True):
            st.markdown(f"### {icon_for(title)} {title}")
            if body:
                st.markdown(body)


# ---------------- UI ----------------

st.title("📊 Company Research Assistant")
st.markdown(
    "Research a company or analyze a job description, and get a structured brief "
    "for interviews, networking, and client meetings."
)

st.divider()

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
    st.divider()
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

# Footer
st.markdown("---")
st.caption("Built by Rovan Dhar")