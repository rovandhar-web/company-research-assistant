# 📊 Vantage

> An AI research assistant that turns a company name — or a job description — into a structured, interview-ready brief in seconds, complete with live financial data.

<img width="1361" height="807" alt="image" src="https://github.com/user-attachments/assets/0de655ad-e6e8-4cca-a1d4-174307404abd" />
<img width="1508" height="729" alt="image" src="https://github.com/user-attachments/assets/787e551c-74ba-4569-b6c8-40bb86cc3c09" />

**🔗 Try it live:** https://vantage-research.streamlit.app/


---

## The problem it solves

Preparing for an interview, a client meeting, or a networking call usually means a dozen browser tabs and a scramble the night before. **Vantage** turns that into one step: name a company (or paste a job posting) and get a clean, structured brief organised the way you'd actually want to think before walking into the room.

## What it does

**🏢 Company mode** — enter a company name and get an "Intelligence Brief":
- **Live financial snapshot** — market cap, revenue, gross margin, and headcount pulled from real public data, plus an annual-revenue chart and a profitability gauge.
- **Qualitative analysis** — company overview, business model, recent developments, key challenges, and a competitive landscape.
- **Smart questions to ask** in an interview or meeting.

**🎯 Job-description mode** — upload (PDF / Word / text) or paste a job posting and get:
- Role expectations, key skills, and interview focus areas.
- Likely interview questions.
- A **tailored "How You Fit"** section when you add your own background.

**Across both modes:** an optional goal/background input tailors the advice to *you*, and every brief can be **exported** as a Markdown file.

## Screenshot

> <img width="1490" height="717" alt="image" src="https://github.com/user-attachments/assets/750a2f5c-d678-438d-a61e-8cf29818b155" />
> `![Vantage dashboard](screenshot.png)`

## How it works

| Layer | Choice |
|---|---|
| **UI** | [Streamlit](https://streamlit.io/) with a custom dark dashboard (HTML/CSS) |
| **Language** | Python |
| **AI model** | An LLM via [OpenRouter](https://openrouter.ai/) (DeepSeek V3) |
| **Live data** | Public company financials via [yfinance](https://github.com/ranaroussi/yfinance) |
| **Document parsing** | `pypdf` and `python-docx` for uploaded job descriptions |
| **Hosting** | Streamlit Community Cloud |

The app sends a structured prompt to the model, pulls real financials for public companies, and renders everything into a hand-styled dashboard. The API key is never stored in code — it's injected securely at runtime via Streamlit's secrets manager.

## Running it locally

1. **Clone the repository**
   ```bash
   git clone https://github.com/rovandhar-web/company-research-assistant.git
   cd company-research-assistant
   ```
2. **Install the dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Add your OpenRouter API key** — create a file at `.streamlit/secrets.toml`:
   ```toml
   OPENROUTER_API_KEY = "your-key-here"
   ```
   (A free key is available at [openrouter.ai](https://openrouter.ai/). This file is git-ignored and should never be committed.)
4. **Run the app**
   ```bash
   streamlit run app.py
   ```

## Roadmap

- Live news and source citations to keep "Recent Developments" current.
- Richer comparisons across companies.
- Saved/shareable briefs.

## A note on accuracy

Financial figures are pulled live from public sources and may lag or differ from official filings; qualitative sections are AI-generated. Every brief is a **research starting point** — verify important facts before relying on them.

## About

Built by **Rovan Dhar**, an SRCC graduate focused on business and strategy, exploring practical applications of AI for business, research, and client-facing work — part of a portfolio of business-focused AI tools aimed at analyst, strategy, consulting, and client-solutions roles.

- **GitHub:** [@rovandhar-web](https://github.com/rovandhar-web)
