import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path=".env")

api_key = os.getenv("OPENROUTER_API_KEY")

# Configure OpenRouter client
client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

# Page config
st.set_page_config(
    page_title="Company Research Assistant",
    page_icon="📊",
    layout="centered"
)

# Title
st.title("📊 Company Research Assistant")

st.markdown(
    "Generate a structured company research brief for interviews, networking, and client meetings."
)

# Input
user_input = st.text_area(
    "Company Name or Job Description",
    placeholder="Enter a company name or paste a job description",
    height=150
)

# Button
if st.button("Generate Research Brief"):

    if not user_input.strip():
        st.warning("Please enter a company name or job description.")

    else:

        prompt = f"""
You are an expert business research analyst.

Create a concise one-page research brief.

Input:
{user_input}

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

        try:

            with st.spinner("Generating research brief..."):

                response = client.chat.completions.create(
                    model="deepseek/deepseek-chat-v3-0324",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                result = response.choices[0].message.content

                st.markdown(result)

        except Exception as e:
            st.error(f"Error: {e}")

# Footer
st.markdown("---")
st.caption("Built by Rovan Dhar")