import streamlit as st
from openai import OpenAI

# Page config (must be the first Streamlit command)
st.set_page_config(
    page_title="Company Research Assistant",
    page_icon="📊",
    layout="centered"
)

# --- Load the API key safely ---
# If the key is missing, show a friendly message instead of crashing the whole app.
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
    # plain text file
    return file.read().decode("utf-8", errors="ignore")


# Build the instruction prompt based on the chosen mode
def build_prompt(text, selected_mode):
    if selected_mode == "Analyze a job description":
        return f"""
You are an expert career coach and recruiter.
Analyze the following job description and create a concise preparation brief
to help a candidate prepare for applying and interviewing.

Job description:
{text}

Format EXACTLY using these sections:

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

Keep the output practical, concise, and interview-focused.
"""
    return f"""
You are an expert business research analyst.
Create a concise one-page research brief.

Input:
{text}

Format EXACTLY using these sections:

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

Keep the output practical, concise, and interview-focused.
"""


# Title
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

if mode == "Research a company":
    user_text = st.text_area(
        "Company Name",
        placeholder="Enter a company name (e.g., Apple)",
        height=120
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
    button_label = "Analyze Job Description"

# Generate button
if st.button(button_label, type="primary"):
    final_input = ""
    error_shown = False

    # In JD mode, prefer an uploaded file; otherwise use the typed/pasted text
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
                            {"role": "user", "content": build_prompt(final_input, mode)}
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
    st.markdown(st.session_state["brief"])
    st.caption("⚠️ AI-generated — please verify important facts before relying on them.")

    # Choose a sensible file name based on the mode used
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