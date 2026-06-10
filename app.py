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

# Adapt the input box and button to the chosen mode
if mode == "Research a company":
    input_label = "Company Name"
    input_placeholder = "Enter a company name (e.g., Apple)"
    button_label = "Generate Research Brief"
else:
    input_label = "Job Description"
    input_placeholder = "Paste the full job description here"
    button_label = "Analyze Job Description"

user_input = st.text_area(input_label, placeholder=input_placeholder, height=180)


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


# Generate button
if st.button(button_label, type="primary"):
    if not user_input.strip():
        st.warning("Please enter a company name or paste a job description.")
    else:
        try:
            with st.spinner("Working on it..."):
                response = client.chat.completions.create(
                    model="deepseek/deepseek-chat-v3-0324",
                    messages=[
                        {"role": "user", "content": build_prompt(user_input, mode)}
                    ]
                )
                result = response.choices[0].message.content
                st.session_state["brief"] = result
                st.session_state["brief_input"] = user_input.strip()
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