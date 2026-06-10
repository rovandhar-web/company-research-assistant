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
    #MainMenu, footer, header {visibility: hidden;}
    html, body, [class*="css"], .stMarkdown, .stTextInput, .stTextArea, .stRadio {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .block-container {max-width: 820px; padding-top: 3rem; padding-bottom: 4rem;}
    .hero {margin-bottom: 2rem;}
    .hero h1 {font-size: 2.7rem; font-weight: 700; letter-spacing: -0.03em; color: #1D1D1F; margin: 0 0 0.6rem 0; line-height: 1.05;}
    .hero p {font-size: 1.08rem; color: #6E6E73; margin: 0; line-height: 1.55; max-width: 640px;}
    .brief-card {background: #FFFFFF; border: 1px solid #EFE7DD; border-left: 4px solid #C2552F; border-radius: 14px; padding: 1.4rem 1.7rem; margin: 1.1rem 0; box-shadow: 0 1px 4px rgba(60,40,20,0.05);}
    .brief-card h3 {margin: 0 0 0.7rem 0; font-size: 1.2rem; font-weight: 700; color: #1D1D1F; letter-spacing: -0.01em;}
    .brief-card ul, .brief-card ol {margin: 0; padding-left: 1.15rem;}
    .brief-card li {margin-bottom: 0.45rem; line-height: 1.6; color: #3A3A3C;}
    .brief-card p {line-height: 1.6; color: #3A3A3C; margin: 0 0 0.5rem 0;}
    .brief-title {font-size: 1.6rem; font-weight: 700; letter-spacing: -0.02em; color: #1D1D1F; margin: 0.5rem 0 1.2rem 0;}
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

client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")


# ---------------- Helpers ----------------

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


def fmt_money(n):
    if n is None:
        return None
    try:
        n = float(n)
    except Exception:
        return None
    for div, suf in [(1e12, "T"), (1e9, "B"), (1e6, "M")]:
        if abs(n) >= div:
            return f"${n / div:.1f}{suf}"
    return f"${n:,.0f}"


def fmt_pct(n):
    if n is None:
        return None
    try:
        return f"{float(n) * 100:.1f}%"
    except Exception:
        return None


def fmt_int(n):
    if n is None:
        return None
    try:
        return f"{int(n):,}"
    except Exception:
        return None


def split_ticker(text):
    """Pull a leading 'TICKER: XXX' line out of the model output."""
    lines = text.split("\n")
    ticker = None
    for i, line in enumerate(lines):
        s = line.strip()
        if s.upper().startswith("TICKER:"):
            val = s.split(":", 1)[1].strip().upper()
            if val and val != "NONE":
                ticker = val
            rest = "\n".join(lines[:i] + lines[i + 1:]).strip()
            return ticker, rest
    return None, text


def get_financials(ticker):
    """Best-effort fetch of real metrics from Yahoo Finance. Never raises."""
    data = {"market_cap": None, "revenue": None, "gross_margin": None,
            "employees": None, "revenue_history": []}
    try:
        import yfinance as yf
        t = yf.Ticker(ticker)
        try:
            info = t.info or {}
        except Exception:
            info = {}
        data["market_cap"] = info.get("marketCap")
        data["revenue"] = info.get("totalRevenue")
        data["gross_margin"] = info.get("grossMargins")
        data["employees"] = info.get("fullTimeEmployees")
        try:
            fin = t.income_stmt
            if fin is not None and "Total Revenue" in fin.index:
                series = fin.loc["Total Revenue"].dropna()
                hist = []
                for col, val in series.items():
                    try:
                        year = col.year
                    except Exception:
                        year = str(col)
                    hist.append((year, float(val)))
                hist.sort(key=lambda x: str(x[0]))
                data["revenue_history"] = hist[-5:]
        except Exception:
            pass
    except Exception:
        pass
    return data


def build_prompt(text, selected_mode, user_context=""):
    if selected_mode == "Analyze a job description":
        base = f"""
You are an expert career coach and recruiter.
Analyze the following job description and create a concise preparation brief.

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
- 3-5 specific, honest points about fit, gaps, and what to emphasize
""" if user_context.strip() else ""
        return base + tail + "\n\nIMPORTANT: No title, intro, or closing remarks. Output only the '## ' sections."

    base = f"""
You are an expert business research analyst.
Create a concise one-page research brief.

Input:
{text}

On the VERY FIRST line, output 'TICKER: ' followed by the company's stock ticker symbol
if it is publicly traded (e.g. 'TICKER: AAPL'), or 'TICKER: NONE' if it is private or you are unsure.
Then the sections, each starting with '## ' on its own line:

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
- 3-5 specific points connecting the company's situation to their stated goal
""" if user_context.strip() else ""
    return base + tail + "\n\nIMPORTANT: After the TICKER line, output only the '## ' sections — no other title or closing remarks."


def parse_sections(text):
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
    try:
        import markdown as md
        sections = parse_sections(markdown_text)
        if not sections:
            st.markdown(markdown_text)
            return
        for title, body in sections:
            body_html = md.markdown(body, extensions=["extra"]) if body else ""
            st.markdown(
                f'<div class="brief-card"><h3>{html.escape(title)}</h3>{body_html}</div>',
                unsafe_allow_html=True,
            )
    except Exception:
        st.markdown(markdown_text)


def render_metrics(fin):
    """STEP 1 (temporary native look): show real numbers to confirm the data feed works."""
    if not fin:
        return
    tiles = [
        ("Market cap", fmt_money(fin.get("market_cap"))),
        ("Revenue (TTM)", fmt_money(fin.get("revenue"))),
        ("Gross margin", fmt_pct(fin.get("gross_margin"))),
        ("Employees", fmt_int(fin.get("employees"))),
    ]
    if not any(v for _, v in tiles):
        st.info("Live financials weren't available for this company (it may be private, or the free data source is busy right now).")
        return
    cols = st.columns(4)
    for col, (label, value) in zip(cols, tiles):
        with col:
            st.metric(label, value if value else "—")
    hist = fin.get("revenue_history") or []
    if len(hist) >= 2:
        try:
            import pandas as pd
            df = pd.DataFrame(
                {"Revenue": [v for _, v in hist]},
                index=[str(y) for y, _ in hist],
            )
            st.caption("Annual revenue")
            st.bar_chart(df)
        except Exception:
            pass


# ---------------- UI ----------------

st.markdown(
    '<div class="hero"><h1>Company Research Assistant</h1>'
    '<p>Research a company or analyze a job description, and get a structured, '
    'tailored brief for interviews, networking, and client meetings.</p></div>',
    unsafe_allow_html=True,
)

mode = st.radio(
    "What would you like to do?",
    ["Research a company", "Analyze a job description"],
    horizontal=True
)

user_text = ""
uploaded_file = None
user_context = ""

if mode == "Research a company":
    user_text = st.text_area("Company Name", placeholder="Enter a company name (e.g., Apple)", height=120)
    user_context = st.text_input("Your goal (optional)", placeholder="e.g., interviewing for a strategy analyst role")
    button_label = "Generate Research Brief"
else:
    uploaded_file = st.file_uploader("Upload a job description (PDF, Word, or .txt) — optional", type=["pdf", "docx", "txt"])
    st.caption("…or paste the job description below instead.")
    user_text = st.text_area("Job Description", placeholder="Paste the full job description here", height=180)
    user_context = st.text_area("Your background (optional)", placeholder="Paste a short summary of your experience (or your resume text) for tailored advice", height=120)
    button_label = "Analyze Job Description"

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
                        messages=[{"role": "user", "content": build_prompt(final_input, mode, user_context)}],
                    )
                    result = response.choices[0].message.content

                    financials = None
                    if mode == "Research a company":
                        ticker, result = split_ticker(result)
                        if ticker:
                            financials = get_financials(ticker)

                    st.session_state["brief"] = result
                    st.session_state["brief_input"] = final_input.strip()
                    st.session_state["brief_mode"] = mode
                    st.session_state["financials"] = financials
            except Exception as e:
                st.error(f"Error: {e}")

if "brief" in st.session_state:
    st.markdown("<div class='brief-title'>Your Brief</div>", unsafe_allow_html=True)
    if st.session_state.get("brief_mode") == "Research a company":
        render_metrics(st.session_state.get("financials"))
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
        st.download_button("⬇️ Download brief (.md)", data=st.session_state["brief"], file_name=file_name, mime="text/markdown")
    with col2:
        if st.button("🗑️ Clear"):
            for k in ("brief", "brief_input", "brief_mode", "financials"):
                st.session_state.pop(k, None)
            st.rerun()
