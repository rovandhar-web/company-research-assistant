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
    "Generate a structured company research brief for interviews, networking, and client meetings."
)

st.divider()

# Input
user_input = st.text_area(
    "Company Name or Job Description",
    placeholder="Enter a company name or paste a job description",
    height=150
)


# Build the instruction prompt sent to the model
def build_prompt(text):
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
if st.button("Generate Research Brief", type="primary"):
    if not user_input.strip():
        st.warning("Please enter a company name or job description.")
    else:
        try:
            with st.spinner("Generating research brief..."):
                response = client.chat.completions.create(
                    model="deepseek/deepseek-chat-v3-0324",
                    messages=[
                        {"role": "user", "content": build_prompt(user_input)}
                    ]
                )
                result = response.choices[0].message.content
                # Save the brief so it stays on screen and can be downloaded
                st.session_state["brief"] = result
                st.session_state["brief_input"] = user_input.strip()
        except Exception as e:
            st.error(f"Error: {e}")

# Show the brief (if one exists), with download and clear options
if "brief" in st.session_state:
    st.divider()
    st.markdown(st.session_state["brief"])
    st.caption("⚠️ AI-generated — please verify important facts before relying on them.")

    # Build a clean filename from whatever the user searched
    raw_name = st.session_state.get("brief_input", "research")
    safe_name = "".join(c if c.isalnum() else "_" for c in raw_name).strip("_")[:40]
    file_name = f"{safe_name or 'research'}_brief.md"

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
            st.rerun()

# Footer
st.markdown("---")
st.caption("Built by Rovan Dhar")