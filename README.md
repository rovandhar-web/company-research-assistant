📊 Company Research Assistant
An AI-powered tool that turns a company name or a job description into a structured, interview-ready research brief in seconds.
<img width="1435" height="817" alt="image" src="https://github.com/user-attachments/assets/428d38c3-1119-4cb8-b890-600e815b1afc" />
<img width="1477" height="793" alt="image" src="https://github.com/user-attachments/assets/121a9382-6cdd-4a06-982a-636c9c70d079" />
<img width="1044" height="685" alt="image" src="https://github.com/user-attachments/assets/804c3cfe-4e1c-4805-aafd-de2bd0eff8fa" />
<img width="1181" height="807" alt="image" src="https://github.com/user-attachments/assets/679113e4-4a6c-4707-b439-364c1c703eaf" />

🔗 Try it live: https://company-research-assistant-9xgzkukzlvmpgc7qed6hn8.streamlit.app/

The problem it solves
Preparing for an interview, a client meeting, or a networking call usually means opening a dozen tabs, skimming the company website, scanning news, and trying to stitch it all into something coherent — often the night before. It is slow, unstructured, and easy to walk in underprepared.
Company Research Assistant compresses that into one step: type a company name (or paste a job description) and get back a clean, one-page brief organised the way you'd actually want to think about a company before walking into the room.
What it does
Enter a company name or paste a job description, click Generate Research Brief, and the app produces a structured brief with six sections:

Company Overview — what the company is and does, at a glance
Business Model — how it makes money and where its value comes from
Recent Developments — notable moves, themes, and direction
Key Challenges — risks and pressures worth understanding
Competitive Landscape — who it competes with and how
Smart Questions to Ask — three thoughtful questions to raise in an interview or meeting

The result is meant as a fast, structured starting point for your own preparation — not a final source of truth. (See Roadmap for how live data and citations are being added.)

Screenshot
<img width="1314" height="780" alt="image" src="https://github.com/user-attachments/assets/4f5d90a4-9aa3-4ebe-8658-dd4f665f0f99" />

How it works
The app is intentionally simple and transparent:

Layer                      Choice
Frontend / UI              Streamlit
Language                   PythonAI 
AI model                   An LLM accessed via OpenRouter (currently DeepSeek V3)
Hosting                    Streamlit Community Cloud

When you submit a company or job description, the app sends a carefully structured prompt to the model asking for the six sections above, then renders the response in the browser. The API key is never stored in the code — it is injected securely at runtime through Streamlit's secrets manager.
Running it locally
You only need this if you want to run your own copy.

**1. Clone the repository**
bash   git clone https://github.com/rovandhar-web/company-research-assistant.git
   cd company-research-assistant

**2. Install the dependencies**
bash   pip install -r requirements.txt

**3. Add your OpenRouter API key.**
Create a file at .streamlit/secrets.toml containing:
toml   OPENROUTER_API_KEY = "your-key-here"
(A free key is available from openrouter.ai. This file is git-ignored and should never be committed.)

4. Run the app
bash   streamlit run app.py

Roadmap
This project is being improved in small, deliberate, production-safe steps:

v1.1 — Polish & reliability: professional UI styling, downloadable briefs, friendlier error handling, and pinned dependencies for a stable deployment.
v1.2 — Dedicated job-description mode: role expectations, key skills, interview focus areas, and role-specific questions tailored to a pasted job description.
v2.0 — Live intelligence: real-time company information with sources and citations, to keep briefs current and reduce reliance on model memory.

About
Built by Rovan Dhar, an SRCC graduate focused on business and strategy, exploring practical applications of AI for business, research, and client-facing work.
This project is part of a portfolio of business-focused AI tools aimed at analyst, strategy, consulting, and client-solutions roles.

GitHub: @rovandhar-web


Briefs are AI-generated and intended as a research starting point. Always verify important facts before relying on them.
