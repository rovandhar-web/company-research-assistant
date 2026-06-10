import html
import streamlit as st
from openai import OpenAI


def _make_icon():
    """Draw the Vantage logo (mint tile + ascending bars) for use as the browser-tab icon."""
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([8, 8, 248, 248], radius=56, fill=(52, 224, 161, 255))
    for x_left, top in [(68, 140), (114, 110), (160, 80)]:
        d.rounded_rectangle([x_left, top, x_left + 28, 188], radius=6, fill=(6, 35, 26, 255))
    return img


try:
    PAGE_ICON = _make_icon()
except Exception:
    PAGE_ICON = "📊"

st.set_page_config(page_title="Vantage — Company Research", page_icon=PAGE_ICON, layout="centered")

DASHBOARD_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
#MainMenu, footer, header {visibility: hidden;}
.stApp {background: #0A0E0D;}
html, body, [class*="css"], .stMarkdown, .stTextInput, .stTextArea, .stRadio {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.block-container {max-width: 940px; padding-top: 2rem; padding-bottom: 4rem;}

/* Brand header + logo */
.vh-header {display:flex; align-items:center; gap:0.65rem; margin-bottom:2rem;}
.vh-logo {width:38px; height:38px; border-radius:11px; background:#34E0A1; display:flex;
    align-items:flex-end; justify-content:center; gap:3px; padding-bottom:9px;}
.vh-logo span {width:4px; background:#06231A; border-radius:2px; display:block;}
.vh-logo .b1 {height:8px;} .vh-logo .b2 {height:14px;} .vh-logo .b3 {height:20px;}
.vh-brand {font-weight:800; font-size:1.2rem; color:#EAF2EF; letter-spacing:-0.01em;}

/* Input intro */
.vh-h2 {font-size:2.4rem; font-weight:800; letter-spacing:-0.035em; color:#EAF2EF; margin:0 0 0.5rem 0; line-height:1.05;}
.vh-sub {color:#7C8B86; font-size:1.02rem; margin:0 0 1.4rem 0; max-width:560px; line-height:1.5;}
.field-lbl {color:#7C8B86; font-size:0.72rem; letter-spacing:0.12em; text-transform:uppercase; font-weight:600; margin-bottom:0.4rem;}
.try-lbl {color:#5E6B66; font-size:0.85rem; padding-top:0.5rem;}
.vh-help {color:#5E6B66; font-size:0.82rem; margin-top:0.6rem;}

/* Brief header */
.vh-eyebrow {display:flex; align-items:center; gap:0.5rem; color:#7C8B86; font-size:0.74rem;
    letter-spacing:0.16em; text-transform:uppercase; margin-bottom:0.7rem; font-weight:600;}
.vh-dot {width:8px; height:8px; border-radius:50%; background:#34E0A1;}
.vh-title {font-size:2.7rem; font-weight:800; letter-spacing:-0.035em; color:#EAF2EF; margin:0;
    line-height:1.05; display:flex; align-items:center; gap:0.8rem; flex-wrap:wrap;}
.vh-badge {font-size:0.8rem; font-weight:600; color:#34E0A1; background:#13241D;
    padding:0.35rem 0.75rem; border-radius:8px; letter-spacing:0.03em;}
.vh-tagline {color:#8A9994; font-size:1.05rem; margin:0.9rem 0 2rem 0; max-width:700px; line-height:1.55;}

.vh-tiles {display:grid; grid-template-columns:repeat(4, 1fr); gap:0.9rem; margin-bottom:0.9rem;}
.vh-tile {background:#111715; border:1px solid #1E2A26; border-radius:14px; padding:1.1rem 1.2rem;}
.vh-tile .lbl {color:#7C8B86; font-size:0.7rem; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:0.55rem; font-weight:600;}
.vh-tile .val {color:#EAF2EF; font-size:1.85rem; font-weight:700; letter-spacing:-0.02em; line-height:1;}
.vh-tile .delta {font-size:0.82rem; font-weight:600; margin-top:0.45rem;}
.vh-up {color:#34E0A1;} .vh-down {color:#F2785C;} .vh-flat {color:#7C8B86;}

.vh-charts {display:grid; grid-template-columns:1fr 1fr; gap:0.9rem; margin:0.9rem 0 1.6rem 0;}
.vh-chart {background:#111715; border:1px solid #1E2A26; border-radius:16px; padding:1.3rem 1.4rem;}
.vh-chart .lbl {color:#7C8B86; font-size:0.7rem; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:1.1rem; font-weight:600;}
.vh-bars {display:flex; align-items:flex-end; gap:0.7rem; height:150px;}
.vh-barwrap {flex:1; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; height:100%;}
.vh-bar {width:78%; background:#34E0A1; border-radius:6px 6px 0 0;}
.vh-barlbl {color:#7C8B86; font-size:0.72rem; margin-top:0.5rem;}
.vh-donut {width:150px; height:150px; border-radius:50%; display:flex; align-items:center; justify-content:center; margin:0.3rem auto;}
.vh-hole {width:104px; height:104px; border-radius:50%; background:#111715; display:flex; flex-direction:column; align-items:center; justify-content:center;}
.vh-hole .big {color:#EAF2EF; font-size:1.55rem; font-weight:700;}
.vh-hole .sub {color:#7C8B86; font-size:0.62rem; letter-spacing:0.12em; text-transform:uppercase; margin-top:0.15rem;}

.vh-grid {display:grid; grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); gap:0.9rem;}
.vh-card {background:#111715; border:1px solid #1E2A26; border-radius:16px; padding:1.4rem 1.6rem;}
.vh-card h3 {margin:0 0 0.8rem 0; font-size:1.12rem; font-weight:700; color:#EAF2EF;}
.vh-card ul, .vh-card ol {margin:0; padding-left:1.1rem;}
.vh-card li {color:#C2CFCA; line-height:1.65; margin-bottom:0.45rem;}
.vh-card p {color:#C2CFCA; line-height:1.65; margin:0 0 0.5rem 0;}
.vh-card strong {color:#EAF2EF;}
.vh-pills {display:flex; flex-wrap:wrap; gap:0.5rem;}
.vh-pill {background:#0E1412; border:1px solid #1E2A26; color:#C2CFCA; padding:0.4rem 0.85rem; border-radius:999px; font-size:0.85rem;}
.vh-foot {color:#5E6B66; font-size:0.8rem; margin-top:1.6rem;}
</style>
"""

try:
    api_key = st.secrets["OPENROUTER_API_KEY"]
except Exception:
    api_key = None
if not api_key:
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)
    st.error("⚠️ This app isn't fully configured yet — the OpenRouter API key is missing. "
             "If you're the owner, add OPENROUTER_API_KEY under your app's Settings → Secrets.")
    st.stop()
client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")


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


def split_meta(text):
    meta = {"ticker": None, "tagline": None, "competitors": []}
    keep = []
    header_zone = True
    for line in text.split("\n"):
        s = line.strip()
        up = s.upper()
        if header_zone and up.startswith("TICKER:"):
            val = s.split(":", 1)[1].strip()
            if val.upper() != "NONE":
                meta["ticker"] = val.upper()
            continue
        if header_zone and up.startswith("TAGLINE:"):
            meta["tagline"] = s.split(":", 1)[1].strip()
            continue
        if header_zone and up.startswith("COMPETITORS:"):
            comps = s.split(":", 1)[1].strip()
            meta["competitors"] = [c.strip() for c in comps.split(",") if c.strip()][:6]
            continue
        if s.startswith("#"):
            header_zone = False
        keep.append(line)
    return meta, "\n".join(keep).strip()


def get_financials(ticker):
    data = {"market_cap": None, "revenue": None, "gross_margin": None,
            "employees": None, "revenue_history": [], "name": None, "exchange": None}
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
        data["name"] = info.get("longName") or info.get("shortName")
        data["exchange"] = info.get("fullExchangeName") or info.get("exchange")
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

First output exactly these three lines, each on its own line:
TICKER: the company's stock ticker symbol if publicly traded (e.g. AAPL), otherwise NONE
TAGLINE: one punchy sentence capturing the company's core strategic angle
COMPETITORS: 3-5 main competitor names, comma-separated

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
    return base + tail + "\n\nIMPORTANT: After the three header lines, output only the '## ' sections — no other title or closing remarks."


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


def build_dashboard_html(brief_md, meta, fin, fallback_name):
    import markdown as md
    fin = fin or {}
    parts = [DASHBOARD_CSS]
    parts.append('<div class="vh-eyebrow"><span class="vh-dot"></span>Intelligence Brief</div>')

    name = fin.get("name") or fallback_name
    badge = ""
    if meta.get("ticker"):
        ex = fin.get("exchange") or ""
        label = (ex + " · " if ex else "") + meta["ticker"]
        badge = f'<span class="vh-badge">{html.escape(label)}</span>'
    parts.append(f'<div class="vh-title">{html.escape(name)}{badge}</div>')
    if meta.get("tagline"):
        parts.append(f'<div class="vh-tagline">{html.escape(meta["tagline"])}</div>')

    mc, rev, gm, emp = fmt_money(fin.get("market_cap")), fmt_money(fin.get("revenue")), \
        fmt_pct(fin.get("gross_margin")), fmt_int(fin.get("employees"))
    if any([mc, rev, gm, emp]):
        rev_delta = ""
        hist = fin.get("revenue_history") or []
        if len(hist) >= 2 and hist[-2][1]:
            d = (hist[-1][1] - hist[-2][1]) / hist[-2][1] * 100
            cls = "vh-up" if d >= 0 else "vh-down"
            rev_delta = f'<div class="delta {cls}">{"+" if d >= 0 else ""}{d:.1f}% YoY</div>'

        def tile(label, value, delta=""):
            return (f'<div class="vh-tile"><div class="lbl">{label}</div>'
                    f'<div class="val">{value or "—"}</div>{delta}</div>')
        parts.append('<div class="vh-tiles">'
                     + tile("Market cap", mc)
                     + tile("Revenue (TTM)", rev, rev_delta)
                     + tile("Gross margin", gm)
                     + tile("Employees", emp)
                     + '</div>')

    chart_blocks = []
    if fin.get("gross_margin") is not None:
        pct = float(fin["gross_margin"]) * 100
        chart_blocks.append(
            f'<div class="vh-chart"><div class="lbl">Profitability</div>'
            f'<div class="vh-donut" style="background: conic-gradient(#34E0A1 0% {pct:.0f}%, #1E2A26 {pct:.0f}% 100%);">'
            f'<div class="vh-hole"><div class="big">{pct:.1f}%</div><div class="sub">Gross margin</div></div></div></div>')
    hist = fin.get("revenue_history") or []
    if len(hist) >= 2:
        maxv = max(v for _, v in hist) or 1
        bars = ""
        for year, val in hist:
            h = max(6, int(val / maxv * 120))
            bars += (f'<div class="vh-barwrap"><div class="vh-bar" style="height:{h}px;"></div>'
                     f'<div class="vh-barlbl">{html.escape(str(year))}</div></div>')
        chart_blocks.append(f'<div class="vh-chart"><div class="lbl">Annual revenue</div>'
                            f'<div class="vh-bars">{bars}</div></div>')
    if chart_blocks:
        parts.append('<div class="vh-charts">' + "".join(chart_blocks) + '</div>')

    cards = '<div class="vh-grid">'
    for title, body in parse_sections(brief_md):
        if "competitive" in title.lower() and meta.get("competitors"):
            inner = '<div class="vh-pills">' + "".join(
                f'<span class="vh-pill">{html.escape(c)}</span>' for c in meta["competitors"]) + '</div>'
        else:
            inner = md.markdown(body, extensions=["extra"]) if body else ""
        cards += f'<div class="vh-card"><h3>{html.escape(title)}</h3>{inner}</div>'
    cards += '</div>'
    parts.append(cards)
    parts.append('<div class="vh-foot">AI-generated · verify key facts. Financials via Yahoo Finance.</div>')
    return "\n".join(parts)


# ---------------- UI ----------------
st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)

# Single brand header with a proper logo mark (ascending bars)
st.markdown(
    '<div class="vh-header"><div class="vh-logo"><span class="b1"></span><span class="b2"></span>'
    '<span class="b3"></span></div><div class="vh-brand">Vantage</div></div>',
    unsafe_allow_html=True,
)

# Intro
st.markdown(
    '<div class="vh-eyebrow"><span class="vh-dot"></span>New Brief</div>'
    '<div class="vh-h2">What are you preparing for?</div>'
    '<div class="vh-sub">Choose a mode, name your subject, and Vantage builds a structured brief in seconds.</div>',
    unsafe_allow_html=True,
)

mode = st.segmented_control(
    "Mode", ["Research a company", "Analyze a job description"],
    default="Research a company", label_visibility="collapsed",
)
if not mode:
    mode = "Research a company"

user_text = ""
uploaded_file = None
user_context = ""


def _set_company(value):
    st.session_state["company"] = value


with st.container(border=True):
    if mode == "Research a company":
        st.markdown("<div class='field-lbl'>Company name</div>", unsafe_allow_html=True)
        user_text = st.text_input(
            "Company name", key="company", label_visibility="collapsed",
            placeholder="Enter a company name (e.g., Apple)",
        )
        chip_cols = st.columns([0.5, 1, 1, 1, 1])
        chip_cols[0].markdown("<div class='try-lbl'>Try</div>", unsafe_allow_html=True)
        for col, cname in zip(chip_cols[1:], ["Apple", "Nvidia", "Stripe", "Patagonia"]):
            col.button(cname, key=f"try_{cname}", on_click=_set_company, args=(cname,), use_container_width=True)

        st.markdown("<div class='field-lbl' style='margin-top:1.1rem;'>Your goal · optional</div>", unsafe_allow_html=True)
        goal = st.segmented_control(
            "Goal", ["Interview prep", "Networking", "Client meeting", "Investor research"],
            default=None, label_visibility="collapsed",
        )
        custom_goal = st.text_input(
            "Custom goal", key="custom_goal", label_visibility="collapsed",
            placeholder="…or describe your goal in your own words",
        )
        goal_map = {
            "Interview prep": "preparing for a job interview",
            "Networking": "preparing for a networking conversation",
            "Client meeting": "preparing for a client meeting",
            "Investor research": "researching as a potential investor",
        }
        if custom_goal.strip():
            user_context = custom_goal.strip()
        elif goal:
            user_context = goal_map.get(goal, "")
    else:
        uploaded_file = st.file_uploader("Upload a job description (PDF, Word, or .txt) — optional", type=["pdf", "docx", "txt"])
        st.caption("…or paste the job description below instead.")
        user_text = st.text_area("Job Description", label_visibility="collapsed",
                                  placeholder="Paste the full job description here", height=170)
        user_context = st.text_area("Your background (optional)", label_visibility="collapsed",
                                     placeholder="Paste a short summary of your experience for tailored advice", height=110)

go = st.button("Generate brief", type="primary")
st.markdown("<div class='vh-help'>~15 seconds · everything stays editable after</div>", unsafe_allow_html=True)

if go:
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
                with st.spinner("Building your brief..."):
                    response = client.chat.completions.create(
                        model="deepseek/deepseek-chat-v3-0324",
                        messages=[{"role": "user", "content": build_prompt(final_input, mode, user_context)}],
                    )
                    result = response.choices[0].message.content
                    meta = {"ticker": None, "tagline": None, "competitors": []}
                    financials = None
                    if mode == "Research a company":
                        meta, result = split_meta(result)
                        if meta.get("ticker"):
                            financials = get_financials(meta["ticker"])
                    st.session_state["brief"] = result
                    st.session_state["brief_meta"] = meta
                    st.session_state["brief_input"] = final_input.strip()
                    st.session_state["brief_mode"] = mode
                    st.session_state["financials"] = financials
            except Exception as e:
                st.error(f"Error: {e}")

if "brief" in st.session_state:
    st.divider()
    if st.session_state.get("brief_mode") == "Research a company":
        st.markdown(
            build_dashboard_html(
                st.session_state["brief"],
                st.session_state.get("brief_meta") or {},
                st.session_state.get("financials"),
                st.session_state.get("brief_input", "Company"),
            ),
            unsafe_allow_html=True,
        )
    else:
        import markdown as md
        out = ['<div class="vh-eyebrow"><span class="vh-dot"></span>Interview Prep</div>'
               '<div class="vh-title">Job Description Analysis</div><div class="vh-grid">']
        for title, body in parse_sections(st.session_state["brief"]):
            inner = md.markdown(body, extensions=["extra"]) if body else ""
            out.append(f'<div class="vh-card"><h3>{html.escape(title)}</h3>{inner}</div>')
        out.append('</div><div class="vh-foot">AI-generated · verify key facts.</div>')
        st.markdown("\n".join(out), unsafe_allow_html=True)

    if st.session_state.get("brief_mode") == "Research a company":
        raw_name = st.session_state.get("brief_input", "company")
        safe_name = "".join(c if c.isalnum() else "_" for c in raw_name).strip("_")[:40]
        file_name = f"{safe_name or 'company'}_brief.md"
    else:
        file_name = "job_description_analysis.md"

    col1, col2 = st.columns(2)
    with col1:
        st.download_button("⬇️ Export brief (.md)", data=st.session_state["brief"], file_name=file_name, mime="text/markdown")
    with col2:
        if st.button("🗑️ Clear"):
            for k in ("brief", "brief_meta", "brief_input", "brief_mode", "financials"):
                st.session_state.pop(k, None)
            st.rerun()
