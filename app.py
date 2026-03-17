# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  AskMNIT — World-Class AI Chatbot for MNIT Jaipur                           ║
# ║  v6.0 — Powered by Claude claude-sonnet-4-20250514 · Premium UI             ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
#
#  SETUP:
#  1. pip install streamlit anthropic
#  2. Create .streamlit/secrets.toml → ANTHROPIC_API_KEY = "sk-ant-..."
#  3. streamlit run app.py
#
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
import anthropic
import datetime

# ── Page config — MUST be first Streamlit call ───────────────────────────────
st.set_page_config(
    page_title="AskMNIT AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS & DATA
# ─────────────────────────────────────────────────────────────────────────────
MNIT_SYSTEM_PROMPT = """You are AskMNIT, the official AI assistant for MNIT Jaipur (Malaviya National Institute of Technology Jaipur) — one of India's top NITs, ranked ~#11 in NIRF.

YOUR PERSONALITY:
- Brilliant senior-student meets knowledgeable mentor energy
- Warm, sharp, witty. Never robotic or corporate.
- Occasionally use natural Hindi: "bilkul", "haan bhai", "sahi baat hai", "koi tension nahi"
- Genuinely proud of MNIT Jaipur and its legacy

YOUR EXPERTISE:
1. ACADEMICS: B.Tech (CSE, ECE, ME, CE, EE, Chemical, Metallurgy, Architecture), M.Tech, PhD, MBA. Credit system (CGPA), semester structure, syllabus, exam patterns, internal marks.

2. ADMISSIONS: JEE Advanced cutoffs (CSE opening ~2000-3000 rank, closing ~4000-5000 General), GATE cutoffs for M.Tech, MBA via CAT/MAT. Counselling (JoSAA), seat matrix (~900 B.Tech seats), fee ~₹1.5L/year for B.Tech.

3. CAMPUS LIFE: 10 hostels (8 boys: Aravali, Vindhyachal, Himgiri, Shivalik, Nilgiri, Satpura, Udaygiri, Sahyadri; 2 girls: Janaki, Mahi), mess timings (7:30-9:30, 12:30-2:30, 7:30-9:30), sports facilities (swimming pool, cricket ground, basketball courts), Central Library (1L+ books, 24hr access during exams).

4. CLUBS & EVENTS: Blitzschlag (annual techfest, March), Madhuram (cultural fest, Feb), E-Cell MNIT, Optix (photography), Robotics Club, MNIT Racing (Formula Student), NSS, NCC, Literary Club, Music Club.

5. PLACEMENTS: Average package ~12-14 LPA, highest ~1 Cr+, top recruiters: Google, Microsoft, Amazon, Goldman Sachs, DE Shaw, Schlumberger, Infosys, TCS, Wipro, Samsung, Texas Instruments. ~95% placement rate for CSE. Placement season: Nov-Mar.

6. RESEARCH: Funded projects from DST, DRDO, ISRO. Labs: VLSI Lab, AI/ML Lab, Robotics Lab, Material Science Lab, EV Research Center.

7. FACILITIES: Medical center (24hr), SBI Bank + ATM, post office, shopping complex, sports complex, WiFi campus (NKN), gym, yoga center.

8. ERP SYSTEM: mnit.ac.in/erp — attendance (75% mandatory), fee payment, grade cards, course registration, timetable.

9. IMPORTANT INFO: Founded 1963, Jaipur Rajasthan. Director: Prof. N.P. Padhy. About 6000+ students, 300+ faculty.

FORMATTING RULES:
- Use markdown beautifully: **bold**, *italic*, ## headers, bullet lists, tables, code blocks
- For complex questions, structure your answer with clear sections
- Keep responses helpful but not bloated — quality over quantity
- End with a relevant follow-up suggestion or offer to explain more
- If you don't know specific real-time data (exact current cutoffs, etc.), give honest approximate ranges based on historical data"""

MOCK_HISTORY = [
    ("Today",      "📊 GATE 2025 cutoffs for CSE"),
    ("Today",      "🏠 Hostel allotment process"),
    ("Yesterday",  "📚 B.Tech syllabus Sem 5"),
    ("Yesterday",  "💰 Fee structure 2024-25"),
    ("2 days ago", "🎯 Placement stats 2024"),
    ("2 days ago", "🔬 Research labs in ECE"),
    ("Last week",  "📅 Blitzschlag 2025 dates"),
    ("Last week",  "🍽️ Mess menu & timings"),
]

SUGGESTION_PILLS = [
    "What are MNIT Jaipur JEE cutoffs?",
    "Tell me about hostel facilities",
    "How are placements at MNIT?",
    "What clubs & fests happen here?",
    "Explain the ERP attendance system",
    "GATE cutoffs for M.Tech admission",
]

QUICK_CHIPS = [
    "JEE cutoffs?", "Hostel info", "Placements?",
    "Campus life", "Fee structure", "Research labs",
]

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
_DEFAULTS = {
    "messages":       [],
    "saved_sessions": [],
    "response_style": "Balanced",
    "chat_theme":     "dark",
    "user_name":      "Student",
    "total_tokens":   0,
    "show_welcome":   True,
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
# ANTHROPIC CLIENT
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    try:
        return anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    except Exception:
        return None

# ─────────────────────────────────────────────────────────────────────────────
# THEME SETUP
# ─────────────────────────────────────────────────────────────────────────────
IS_LIGHT = st.session_state.chat_theme == "light"

if IS_LIGHT:
    C = {
        "bg":        "#F2F5FF",
        "surf":      "#FFFFFF",
        "surf2":     "#EEF2FF",
        "bar":       "rgba(255,255,255,0.92)",
        "border":    "rgba(37,99,235,0.15)",
        "text":      "#0F172A",
        "muted":     "rgba(30,58,138,0.50)",
        "accent":    "#1D4ED8",
        "sidebar":   "#F0F4FF",
        "grid":      "rgba(37,99,235,0.04)",
        "radial":    "rgba(37,99,235,0.08)",
        "msg_user":  "rgba(29,78,216,0.06)",
        "msg_ai":    "rgba(255,255,255,0.78)",
        "code_bg":   "rgba(37,99,235,0.06)",
        "code_c":    "#1D4ED8",
        "ts_c":      "rgba(29,78,216,0.32)",
        "disc_c":    "rgba(29,78,216,0.32)",
        "tag_bg":    "rgba(37,99,235,0.07)",
        "tag_c":     "rgba(29,78,216,0.75)",
        "inp_bg":    "rgba(255,255,255,0.90)",
        "inp_sh":    "0 8px 32px rgba(37,99,235,0.10)",
        "sb_bg":     "#F0F4FF",
        "tok_c":     "rgba(29,78,216,0.40)",
        "chip_bg":   "rgba(37,99,235,0.06)",
        "chip_c":    "rgba(29,78,216,0.75)",
        "sug_bg":    "rgba(255,255,255,0.70)",
        "sug_c":     "rgba(15,23,42,0.70)",
    }
else:
    C = {
        "bg":        "#050810",
        "surf":      "#0A0F1E",
        "surf2":     "#0D1426",
        "bar":       "rgba(5,8,16,0.94)",
        "border":    "rgba(59,130,246,0.12)",
        "text":      "#E8F0FE",
        "muted":     "rgba(148,163,184,0.55)",
        "accent":    "#3B82F6",
        "sidebar":   "#070918",
        "grid":      "rgba(59,130,246,0.035)",
        "radial":    "rgba(29,78,216,0.12)",
        "msg_user":  "rgba(29,78,216,0.09)",
        "msg_ai":    "rgba(10,15,30,0.75)",
        "code_bg":   "rgba(59,130,246,0.10)",
        "code_c":    "#93C5FD",
        "ts_c":      "rgba(59,130,246,0.28)",
        "disc_c":    "rgba(59,130,246,0.28)",
        "tag_bg":    "rgba(59,130,246,0.07)",
        "tag_c":     "rgba(147,197,253,0.65)",
        "inp_bg":    "rgba(10,15,30,0.94)",
        "inp_sh":    "0 8px 40px rgba(0,0,0,0.65)",
        "sb_bg":     "#070918",
        "tok_c":     "rgba(59,130,246,0.38)",
        "chip_bg":   "rgba(59,130,246,0.07)",
        "chip_c":    "rgba(147,197,253,0.65)",
        "sug_bg":    "rgba(255,255,255,0.028)",
        "sug_c":     "rgba(186,230,253,0.70)",
    }

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500;600&family=Nunito:wght@300;400;500;600;700;800&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"] {{
  background: {C["bg"]} !important;
  color: {C["text"]} !important;
  font-family: 'Nunito', sans-serif !important;
}}

/* Hide Streamlit chrome */
header[data-testid="stHeader"], footer, #MainMenu,
[data-testid="stToolbar"], [data-testid="stDecoration"] {{ display: none !important; }}

[data-testid="stMainBlockContainer"] {{ padding: 0 !important; max-width: 100% !important; }}

/* ═══════════════════════════════════════════
   SIDEBAR — ALWAYS VISIBLE
   ═══════════════════════════════════════════ */
[data-testid="stSidebar"] {{
  display: flex !important;
  visibility: visible !important;
  opacity: 1 !important;
  background: {C["sb_bg"]} !important;
  border-right: 1px solid {C["border"]} !important;
  min-width: 268px !important;
  max-width: 268px !important;
  box-shadow: {"2px 0 24px rgba(37,99,235,0.07)" if IS_LIGHT else "4px 0 40px rgba(0,0,0,0.65)"} !important;
}}
[data-testid="stSidebar"] > div {{
  padding: 0 !important;
  height: 100vh !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  scrollbar-width: thin;
  scrollbar-color: rgba(59,130,246,0.22) transparent;
}}
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] {{
  display: flex !important;
  visibility: visible !important;
  opacity: 1 !important;
}}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{ gap: 0 !important; }}

/* Sidebar section header */
.sb-hdr {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.57rem; font-weight: 600;
  color: {C["accent"]}; opacity: 0.65;
  text-transform: uppercase; letter-spacing: 2px;
  padding: 15px 18px 6px;
  border-top: 1px solid {C["border"]};
  margin-top: 4px;
  display: flex; align-items: center; gap: 7px;
}}
.sb-hdr::before {{
  content: '';
  width: 12px; height: 1px;
  background: {C["accent"]}; opacity: 0.45;
}}

/* Sidebar history */
.sb-hist {{
  display: flex; align-items: center; gap: 9px;
  padding: 8px 18px; cursor: pointer;
  font-size: 0.79rem; font-weight: 500;
  color: {C["muted"]};
  border-bottom: 1px solid {C["border"]};
  transition: background 0.15s, color 0.15s, padding 0.15s;
  font-family: 'Nunito', sans-serif;
}}
.sb-hist:hover {{
  background: {"rgba(37,99,235,0.06)" if IS_LIGHT else "rgba(59,130,246,0.06)"};
  color: {"#1D4ED8" if IS_LIGHT else "#93C5FD"};
  padding-left: 22px;
}}
.sb-dot    {{ width:5px; height:5px; border-radius:50%; background:#3B82F6; flex-shrink:0; opacity:0.7; }}
.sb-dot-d  {{ width:5px; height:5px; border-radius:50%; background:rgba(148,163,184,0.35); flex-shrink:0; }}

/* Sidebar controls */
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {{
  background: {"rgba(37,99,235,0.05)" if IS_LIGHT else "rgba(255,255,255,0.04)"} !important;
  border: 1px solid {C["border"]} !important;
  border-radius: 10px !important;
  color: {C["text"]} !important;
  font-family: 'Nunito', sans-serif !important;
  font-size: 0.82rem !important;
}}
[data-testid="stSidebar"] [data-testid="stSelectbox"] label {{
  color: {C["accent"]} !important; opacity: 0.65;
  font-size: 0.65rem !important; font-weight: 700 !important;
  text-transform: uppercase !important; letter-spacing: 0.8px !important;
  font-family: 'JetBrains Mono', monospace !important;
}}
[data-testid="stSidebar"] [data-testid="stTextInput"] input {{
  background: {"rgba(37,99,235,0.04)" if IS_LIGHT else "rgba(255,255,255,0.04)"} !important;
  border: 1px solid {C["border"]} !important;
  border-radius: 10px !important;
  color: {C["text"]} !important;
  font-family: 'Nunito', sans-serif !important;
  font-size: 0.83rem !important;
}}
[data-testid="stSidebar"] [data-testid="stTextInput"] label {{
  color: {C["accent"]} !important; opacity: 0.65;
  font-size: 0.65rem !important; font-weight: 700 !important;
  text-transform: uppercase !important; letter-spacing: 0.8px !important;
  font-family: 'JetBrains Mono', monospace !important;
}}
[data-testid="stSidebar"] [data-testid="stToggle"] label {{
  color: {C["text"]} !important;
  font-size: 0.82rem !important;
}}

/* Sidebar all buttons default (red-tinted — for dangerous actions) */
[data-testid="stSidebar"] .stButton > button {{
  background: rgba(239,68,68,0.07) !important;
  border: 1px solid rgba(239,68,68,0.20) !important;
  color: #F87171 !important;
  border-radius: 10px !important;
  font-size: 0.79rem !important; font-weight: 600 !important;
  padding: 7px 14px !important; box-shadow: none !important;
  font-family: 'Nunito', sans-serif !important;
  width: 100% !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
  background: rgba(239,68,68,0.14) !important; transform: none !important;
}}

/* New chat button override */
[data-testid="stSidebar"] .sb-new .stButton > button {{
  background: linear-gradient(135deg,rgba(29,78,216,0.16),rgba(14,165,233,0.10)) !important;
  border: 1px solid {"rgba(37,99,235,0.30)" if IS_LIGHT else "rgba(59,130,246,0.28)"} !important;
  color: {"#1D4ED8" if IS_LIGHT else "#60A5FA"} !important;
  font-size: 0.84rem !important; font-weight: 700 !important;
  padding: 9px 14px !important; border-radius: 12px !important;
}}
[data-testid="stSidebar"] .sb-new .stButton > button:hover {{
  background: rgba(59,130,246,0.18) !important;
  border-color: rgba(59,130,246,0.50) !important;
}}

/* Theme buttons */
[data-testid="stSidebar"] .sb-th .stButton > button {{
  background: {"rgba(37,99,235,0.06)" if IS_LIGHT else "rgba(255,255,255,0.04)"} !important;
  border: 1px solid {C["border"]} !important;
  color: {C["text"]} !important;
  font-size: 0.79rem !important; font-weight: 600 !important;
  padding: 7px 12px !important; border-radius: 9px !important;
  box-shadow: none !important;
}}
[data-testid="stSidebar"] .sb-th .stButton > button:hover {{
  background: {"rgba(37,99,235,0.12)" if IS_LIGHT else "rgba(59,130,246,0.10)"} !important;
  border-color: {"rgba(37,99,235,0.35)" if IS_LIGHT else "rgba(59,130,246,0.35)"} !important;
  transform: none !important;
}}
[data-testid="stSidebar"] .sb-th-a .stButton > button {{
  background: {"rgba(37,99,235,0.16)" if IS_LIGHT else "rgba(59,130,246,0.16)"} !important;
  border-color: {"rgba(37,99,235,0.45)" if IS_LIGHT else "rgba(59,130,246,0.50)"} !important;
  color: {"#1D4ED8" if IS_LIGHT else "#93C5FD"} !important;
  font-weight: 800 !important;
}}

/* Ghost / load session button */
[data-testid="stSidebar"] .sb-ghost .stButton > button {{
  background: transparent !important;
  border: 1px solid {C["border"]} !important;
  color: {C["muted"]} !important;
  font-size: 0.75rem !important;
  padding: 4px 10px !important; border-radius: 7px !important;
  box-shadow: none !important;
}}
[data-testid="stSidebar"] .sb-ghost .stButton > button:hover {{
  background: {"rgba(37,99,235,0.08)" if IS_LIGHT else "rgba(59,130,246,0.10)"} !important;
  color: {C["accent"]} !important;
}}

/* ═══════════════════════════════════════════
   ANIMATED BACKGROUND
   ═══════════════════════════════════════════ */
.chat-bg {{
  position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background: {C["bg"]};
}}
.chat-bg::before {{
  content: '';
  position: absolute; inset: 0;
  background-image:
    linear-gradient({C["grid"]} 1px, transparent 1px),
    linear-gradient(90deg, {C["grid"]} 1px, transparent 1px);
  background-size: 52px 52px;
  animation: gridMove 28s linear infinite;
}}
@keyframes gridMove {{
  from {{ background-position: 0 0; }}
  to   {{ background-position: 52px 52px; }}
}}
.chat-bg::after {{
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(
    ellipse 75% 55% at 50% -5%,
    {C["radial"]}, transparent 68%
  );
}}

/* ═══════════════════════════════════════════
   NAVBAR
   ═══════════════════════════════════════════ */
.navbar {{
  position: relative; z-index: 100;
  background: {C["bar"]};
  backdrop-filter: blur(26px) saturate(180%);
  border-bottom: 1px solid {C["border"]};
  box-shadow: {"0 1px 14px rgba(37,99,235,0.07)" if IS_LIGHT else "0 2px 24px rgba(0,0,0,0.65)"};
  padding: 11px 26px;
  display: flex; align-items: center; justify-content: space-between;
}}
.nav-brand {{ display: flex; align-items: center; gap: 12px; }}
.nav-logo {{
  width: 38px; height: 38px; border-radius: 11px;
  background: linear-gradient(135deg, #1D4ED8 0%, #0EA5E9 100%);
  display: flex; align-items: center; justify-content: center;
  font-family: 'Syne', sans-serif; font-size: 1.05rem; font-weight: 800; color: white;
  box-shadow: 0 4px 18px rgba(29,78,216,0.40); letter-spacing: -1px; flex-shrink: 0;
}}
.nav-title {{
  font-family: 'Syne', sans-serif;
  font-size: 1.05rem; font-weight: 800;
  color: {C["text"]}; letter-spacing: -0.4px;
}}
.nav-sub {{
  font-size: 0.54rem; letter-spacing: 0.8px;
  color: {C["muted"]};
  font-family: 'JetBrains Mono', monospace;
  text-transform: uppercase;
}}
.nav-live {{
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(5,150,105,0.10);
  border: 1px solid rgba(5,150,105,0.25);
  border-radius: 20px; padding: 4px 12px;
  font-size: 0.60rem; color: #34D399;
  font-family: 'JetBrains Mono', monospace; font-weight: 600;
  letter-spacing: 0.5px;
}}
.live-dot {{
  width: 6px; height: 6px; border-radius: 50%; background: #10B981;
  animation: liveB 2s ease infinite;
}}
@keyframes liveB {{
  0%,100% {{ opacity:1; transform:scale(1); }}
  50%      {{ opacity:0.45; transform:scale(0.80); }}
}}
.tok-badge {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.58rem; color: {C["tok_c"]};
  padding: 3px 8px;
  background: {"rgba(37,99,235,0.06)" if IS_LIGHT else "rgba(59,130,246,0.06)"};
  border: 1px solid {C["border"]}; border-radius: 8px;
}}

/* ═══════════════════════════════════════════
   HERO
   ═══════════════════════════════════════════ */
.hero-wrap {{
  position: relative; z-index: 10;
  padding: 5vh 0 2vh;
  display: flex; flex-direction: column; align-items: center;
}}
.hero-orb {{
  width: 104px; height: 104px; border-radius: 28px;
  background: linear-gradient(135deg, #1E3A8A 0%, #1D4ED8 35%, #0EA5E9 68%, #059669 100%);
  display: flex; align-items: center; justify-content: center; font-size: 3rem;
  box-shadow:
    0 0 0 1px rgba(59,130,246,0.18),
    0 0 60px rgba(29,78,216,0.40),
    0 24px 60px rgba(0,0,0,0.22);
  animation: floatOrb 4.5s ease-in-out infinite;
  margin-bottom: 28px;
}}
@keyframes floatOrb {{
  0%,100% {{ transform: translateY(0px) rotate(0deg); box-shadow: 0 0 0 1px rgba(59,130,246,0.18),0 0 60px rgba(29,78,216,0.40),0 24px 60px rgba(0,0,0,0.22); }}
  50%      {{ transform: translateY(-10px) rotate(1.5deg); box-shadow: 0 0 0 1px rgba(59,130,246,0.22),0 0 80px rgba(29,78,216,0.50),0 34px 70px rgba(0,0,0,0.18); }}
}}
.hero-h1 {{
  font-family: 'Syne', sans-serif;
  font-size: clamp(2.0rem, 3.8vw, 3.0rem);
  font-weight: 800; color: {C["text"]};
  text-align: center; letter-spacing: -1.5px; line-height: 1.08;
  margin-bottom: 14px; animation: fadeUp 0.5s ease both;
}}
.hero-h1 .grad {{
  background: linear-gradient(135deg, #1D4ED8 0%, #0EA5E9 50%, #059669 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}}
.hero-sub {{
  font-size: 0.87rem; color: {C["muted"]};
  text-align: center; line-height: 1.75; max-width: 500px;
  margin-bottom: 28px; font-weight: 500;
  animation: fadeUp 0.55s 0.08s ease both;
}}
.hero-tags {{
  display: flex; flex-wrap: wrap; gap: 8px;
  justify-content: center; margin-bottom: 32px;
  animation: fadeUp 0.55s 0.14s ease both;
}}
.hero-tag {{
  font-family: 'JetBrains Mono', monospace; font-size: 0.64rem;
  padding: 4px 13px; border-radius: 20px;
  background: {C["tag_bg"]}; border: 1px solid {C["border"]};
  color: {C["tag_c"]}; letter-spacing: 0.4px;
}}

/* Stat chips */
.stat-row {{
  display: flex; flex-wrap: wrap; gap: 10px;
  justify-content: center; margin-bottom: 28px;
  animation: fadeUp 0.55s 0.20s ease both;
}}
.stat-chip {{
  display: flex; align-items: center; gap: 6px;
  padding: 6px 14px; border-radius: 10px;
  background: {"rgba(255,255,255,0.55)" if IS_LIGHT else "rgba(255,255,255,0.025)"};
  border: 1px solid {C["border"]};
  font-size: 0.73rem; color: {C["muted"]};
  font-family: 'JetBrains Mono', monospace;
  backdrop-filter: blur(8px);
}}
.stat-v {{ font-weight: 700; color: {C["accent"]}; }}

/* Suggestion pills */
.sug-pill .stButton > button {{
  background: {C["sug_bg"]} !important;
  border: 1px solid {C["border"]} !important;
  border-radius: 999px !important;
  color: {C["sug_c"]} !important;
  font-family: 'Nunito', sans-serif !important;
  font-size: 0.80rem !important; font-weight: 600 !important;
  padding: 9px 18px !important;
  box-shadow: {"0 2px 8px rgba(37,99,235,0.07)" if IS_LIGHT else "none"} !important;
  backdrop-filter: blur(8px) !important;
  transition: all 0.18s !important;
}}
.sug-pill .stButton > button:hover {{
  background: {"rgba(37,99,235,0.12)" if IS_LIGHT else "rgba(29,78,216,0.12)"} !important;
  border-color: {"rgba(37,99,235,0.35)" if IS_LIGHT else "rgba(59,130,246,0.38)"} !important;
  color: {"#1D4ED8" if IS_LIGHT else "#BAE6FD"} !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(29,78,216,0.14) !important;
}}

/* ═══════════════════════════════════════════
   INPUT BAR
   ═══════════════════════════════════════════ */
.inp-wrap {{
  position: relative; z-index: 50;
  max-width: 820px; margin: 0 auto;
}}
.inp-wrap [data-testid="stForm"] {{
  background: {C["inp_bg"]} !important;
  border: 1.5px solid {C["border"]} !important;
  border-radius: 22px !important;
  padding: 7px 10px 7px 4px !important;
  backdrop-filter: blur(30px) saturate(160%) !important;
  box-shadow: {C["inp_sh"]} !important;
  transition: border-color 0.22s, box-shadow 0.22s !important;
}}
.inp-wrap [data-testid="stForm"]:focus-within {{
  border-color: {"rgba(37,99,235,0.50)" if IS_LIGHT else "rgba(59,130,246,0.48)"} !important;
  box-shadow: {"0 0 0 3px rgba(37,99,235,0.09),0 8px 32px rgba(37,99,235,0.14)" if IS_LIGHT else "0 0 0 3px rgba(59,130,246,0.10),0 8px 40px rgba(0,0,0,0.65)"} !important;
}}
.inp-wrap [data-testid="stHorizontalBlock"] {{ align-items: center !important; gap: 2px !important; }}
.inp-wrap [data-testid="stTextInput"] label {{ display: none !important; }}
.inp-wrap [data-testid="stTextInput"] > div {{
  background: transparent !important; border: none !important;
  box-shadow: none !important; padding: 0 !important;
}}
.inp-wrap [data-testid="stTextInput"] input {{
  background: transparent !important; border: none !important;
  outline: none !important; box-shadow: none !important;
  color: {C["text"]} !important;
  font-family: 'Nunito', sans-serif !important;
  font-size: 0.97rem !important; font-weight: 500 !important;
  caret-color: {C["accent"]} !important;
  padding: 12px 10px !important; height: 46px !important;
}}
.inp-wrap [data-testid="stTextInput"] input::placeholder {{
  color: {"rgba(30,58,138,0.30)" if IS_LIGHT else "rgba(148,163,184,0.32)"} !important;
}}
.inp-wrap [data-testid="stTextInput"] input:focus {{
  border: none !important; box-shadow: none !important; outline: none !important;
}}
.send-btn [data-testid="stFormSubmitButton"] > button {{
  background: linear-gradient(135deg, #1D4ED8 0%, #0EA5E9 100%) !important;
  border: none !important; border-radius: 14px !important;
  color: #fff !important; font-size: 1.15rem !important; font-weight: 700 !important;
  width: 44px !important; height: 44px !important; min-width: 44px !important;
  padding: 0 !important;
  box-shadow: 0 4px 18px rgba(29,78,216,0.45) !important;
  transition: all 0.16s !important;
}}
.send-btn [data-testid="stFormSubmitButton"] > button:hover {{
  transform: scale(1.09) !important;
  box-shadow: 0 6px 26px rgba(29,78,216,0.60) !important;
  opacity: 1 !important;
}}
.send-btn [data-testid="stFormSubmitButton"] > button:active {{
  transform: scale(0.94) !important;
}}

/* ═══════════════════════════════════════════
   CHAT MESSAGES
   ═══════════════════════════════════════════ */
.msg-area {{ padding-bottom: 155px; }}

[data-testid="stChatMessage"] {{
  background: {C["msg_ai"]} !important;
  border: 1px solid {C["border"]} !important;
  border-radius: 18px !important;
  font-family: 'Nunito', sans-serif !important;
  backdrop-filter: blur(14px) !important;
  box-shadow: {"0 2px 12px rgba(37,99,235,0.05)" if IS_LIGHT else "none"} !important;
  animation: msgIn 0.28s cubic-bezier(0.34,1.56,0.64,1) both !important;
}}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
  background: {C["msg_user"]} !important;
  border-color: {"rgba(29,78,216,0.16)" if IS_LIGHT else "rgba(59,130,246,0.18)"} !important;
}}
@keyframes msgIn {{
  from {{ opacity:0; transform:translateY(10px) scale(0.97); }}
  to   {{ opacity:1; transform:translateY(0) scale(1); }}
}}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li {{
  color: {C["text"]} !important;
  font-family: 'Nunito', sans-serif !important;
  font-size: 0.90rem !important; line-height: 1.72 !important;
}}
[data-testid="stChatMessage"] strong {{ color: {C["text"]} !important; font-weight: 700 !important; }}
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3 {{
  font-family: 'Syne', sans-serif !important;
  color: {C["text"]} !important; font-weight: 700 !important;
  margin: 8px 0 4px !important;
}}
[data-testid="stChatMessage"] code {{
  font-family: 'JetBrains Mono', monospace !important;
  background: {C["code_bg"]} !important;
  border: 1px solid {C["border"]} !important;
  border-radius: 6px !important; padding: 1px 6px !important;
  font-size: 0.82rem !important; color: {C["code_c"]} !important;
}}
[data-testid="stChatMessage"] table {{
  font-size: 0.83rem !important; font-family: 'Nunito', sans-serif !important;
  border-collapse: collapse !important; width: 100% !important;
}}
[data-testid="stChatMessage"] th {{
  background: {"rgba(37,99,235,0.08)" if IS_LIGHT else "rgba(59,130,246,0.10)"} !important;
  color: {C["text"]} !important; font-weight: 700 !important;
  padding: 6px 12px !important;
  border: 1px solid {C["border"]} !important;
}}
[data-testid="stChatMessage"] td {{
  color: {C["text"]} !important; padding: 5px 12px !important;
  border: 1px solid {C["border"]} !important;
  background: {"rgba(255,255,255,0.30)" if IS_LIGHT else "rgba(255,255,255,0.02)"} !important;
}}

/* Streaming dots */
.thinking {{
  display: inline-flex; align-items: center; gap: 9px;
  padding: 8px 16px;
  background: {"rgba(37,99,235,0.07)" if IS_LIGHT else "rgba(29,78,216,0.09)"};
  border: 1px solid {C["border"]};
  border-radius: 20px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem; color: {C["accent"]};
  animation: fadeInUp 0.22s ease both;
}}
.t-dot {{
  display: inline-block; width: 5px; height: 5px;
  background: {C["accent"]}; border-radius: 50%;
  animation: tdBounce 1.1s ease infinite;
}}
.t-dot:nth-child(2) {{ animation-delay: 0.15s; }}
.t-dot:nth-child(3) {{ animation-delay: 0.30s; }}
@keyframes tdBounce {{
  0%,60%,100% {{ transform:translateY(0); }}
  30%          {{ transform:translateY(-5px); }}
}}

/* Timestamp */
.msg-ts {{
  font-size: 0.57rem; color: {C["ts_c"]};
  font-family: 'JetBrains Mono', monospace;
  margin-top: 6px; text-align: right;
}}

/* ═══════════════════════════════════════════
   ANCHORED BOTTOM BAR
   ═══════════════════════════════════════════ */
.bar-anch {{
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 800;
  background: {"rgba(242,245,255,0.97)" if IS_LIGHT else "rgba(5,8,16,0.97)"};
  backdrop-filter: blur(28px) saturate(180%);
  border-top: 1px solid {C["border"]};
  box-shadow: {"0 -4px 20px rgba(37,99,235,0.07)" if IS_LIGHT else "0 -4px 30px rgba(0,0,0,0.75)"};
  padding: 10px max(22px, calc((100% - 870px) / 2)) 14px;
}}
.quick-chips {{
  display: flex; flex-wrap: wrap; gap: 5px;
  max-width: 820px; margin: 0 auto 9px;
}}
.q-chip {{
  display: inline-block; padding: 4px 12px;
  background: {C["chip_bg"]};
  border: 1px solid {C["border"]}; border-radius: 20px;
  font-size: 0.70rem; color: {C["chip_c"]};
  cursor: pointer; font-family: 'JetBrains Mono', monospace;
  transition: all 0.16s; white-space: nowrap;
}}
.q-chip:hover {{
  background: {"rgba(37,99,235,0.14)" if IS_LIGHT else "rgba(59,130,246,0.14)"};
  border-color: {"rgba(37,99,235,0.35)" if IS_LIGHT else "rgba(59,130,246,0.35)"};
  color: {C["accent"]};
}}

/* ═══════════════════════════════════════════
   GLOBAL BUTTONS (outside sidebar)
   ═══════════════════════════════════════════ */
.stButton > button {{
  background: linear-gradient(135deg,#1D4ED8,#0EA5E9) !important;
  color: #fff !important; border: none !important; border-radius: 10px !important;
  font-family: 'Nunito', sans-serif !important; font-weight: 700 !important;
  font-size: 0.83rem !important; padding: 9px 18px !important;
  box-shadow: 0 3px 14px rgba(29,78,216,0.25) !important;
  transition: all 0.16s !important;
}}
.stButton > button:hover {{
  opacity: 0.87 !important; transform: translateY(-1px) !important;
}}

/* Misc */
[data-testid="column"] {{ padding: 0 4px !important; }}
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: rgba(59,130,246,0.22); border-radius: 4px; }}

@keyframes fadeUp {{
  from {{ opacity:0; transform:translateY(18px); }}
  to   {{ opacity:1; transform:translateY(0); }}
}}
@keyframes fadeInUp {{
  from {{ opacity:0; transform:translateY(-5px); }}
  to   {{ opacity:1; transform:translateY(0); }}
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        # Logo header
        st.markdown(f"""
        <div style="padding:20px 18px 16px;border-bottom:1px solid {C['border']};">
          <div style="display:flex;align-items:center;gap:12px;">
            <div style="width:40px;height:40px;border-radius:12px;
              background:linear-gradient(135deg,#1D4ED8,#0EA5E9);
              display:flex;align-items:center;justify-content:center;
              font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:800;color:white;
              box-shadow:0 4px 18px rgba(29,78,216,0.42);">A</div>
            <div>
              <div style="font-family:'Syne',sans-serif;font-size:0.97rem;
                font-weight:800;color:{C['text']};letter-spacing:-0.4px;">AskMNIT</div>
              <div style="font-size:0.56rem;color:{C['accent']};opacity:0.60;
                font-family:'JetBrains Mono',monospace;letter-spacing:0.6px;
                text-transform:uppercase;">MNIT Jaipur · AI Assistant</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # New chat
        st.markdown("<div style='padding:12px 16px 0;'>", unsafe_allow_html=True)
        st.markdown('<div class="sb-new">', unsafe_allow_html=True)
        if st.button("＋  New Conversation", key="sb_new", use_container_width=True):
            if st.session_state.messages:
                label = next(
                    (m["content"][:42] for m in st.session_state.messages if m["role"]=="user"),
                    "Conversation"
                )
                st.session_state.saved_sessions.append({
                    "label":    label + "…",
                    "messages": list(st.session_state.messages),
                })
            st.session_state.messages   = []
            st.session_state.show_welcome = True
            st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)

        # ── ⏱ CHAT HISTORY ──
        st.markdown('<div class="sb-hdr">⏱ Chat History</div>', unsafe_allow_html=True)

        if st.session_state.saved_sessions:
            st.markdown(
                f'<div style="font-size:0.58rem;'
                f'color:{C["accent"]};opacity:0.55;'
                f'padding:4px 18px 2px;font-family:\'JetBrains Mono\',monospace;'
                f'text-transform:uppercase;letter-spacing:0.5px;">This Session</div>',
                unsafe_allow_html=True,
            )
            for i, sess in enumerate(reversed(st.session_state.saved_sessions[-3:])):
                lbl = sess["label"][:30] + ("…" if len(sess["label"]) > 30 else "")
                col_a, col_b = st.columns([5, 1])
                with col_a:
                    st.markdown(
                        f'<div class="sb-hist"><div class="sb-dot"></div>{lbl}</div>',
                        unsafe_allow_html=True,
                    )
                with col_b:
                    st.markdown('<div class="sb-ghost">', unsafe_allow_html=True)
                    if st.button("↩", key=f"ls_{i}"):
                        st.session_state.messages     = list(sess["messages"])
                        st.session_state.show_welcome = False
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        cur_day = ""
        for day_lbl, title in MOCK_HISTORY:
            if day_lbl != cur_day:
                cur_day = day_lbl
                st.markdown(
                    f'<div style="font-size:0.56rem;color:{C["muted"]};opacity:0.70;'
                    f'padding:6px 18px 2px;font-family:\'JetBrains Mono\',monospace;'
                    f'text-transform:uppercase;letter-spacing:0.5px;">{day_lbl}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown(
                f'<div class="sb-hist"><div class="sb-dot-d"></div>{title}</div>',
                unsafe_allow_html=True,
            )

        # ── ⚙ SETTINGS ──
        st.markdown('<div class="sb-hdr">⚙ Settings</div>', unsafe_allow_html=True)
        st.markdown('<div style="padding:10px 18px 4px;">', unsafe_allow_html=True)

        options = ["Balanced", "Concise", "Detailed", "Bullet Points"]
        new_style = st.selectbox(
            "Response Style",
            options,
            index=options.index(st.session_state.response_style),
            key="sb_style",
        )
        if new_style != st.session_state.response_style:
            st.session_state.response_style = new_style
            st.rerun()

        new_name = st.text_input(
            "Your Name",
            value=st.session_state.user_name,
            key="sb_uname",
        )
        if new_name != st.session_state.user_name:
            st.session_state.user_name = new_name

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("🗑  Clear Chat History", key="sb_clear", use_container_width=True):
            st.session_state.messages     = []
            st.session_state.show_welcome = True
            st.session_state.total_tokens = 0
            st.toast("Chat cleared!", icon="🗑")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # ── 🌗 THEME ──
        st.markdown('<div class="sb-hdr">🌗 Theme</div>', unsafe_allow_html=True)
        st.markdown('<div style="padding:10px 18px 18px;">', unsafe_allow_html=True)
        t1, t2 = st.columns(2)
        with t1:
            cls = "sb-th-a sb-th" if not IS_LIGHT else "sb-th"
            st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
            if st.button("🌑  Dark", key="th_d", use_container_width=True):
                st.session_state.chat_theme = "dark"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with t2:
            cls = "sb-th-a sb-th" if IS_LIGHT else "sb-th"
            st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
            if st.button("☀️  Light", key="th_l", use_container_width=True):
                st.session_state.chat_theme = "light"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Footer
        st.markdown(
            f'<div style="padding:12px 18px;border-top:1px solid {C["border"]};margin-top:4px;">'
            f'<div style="font-size:0.57rem;color:{C["muted"]};opacity:0.60;'
            f'font-family:\'JetBrains Mono\',monospace;">'
            f'AskMNIT v6.0 · MNIT Jaipur<br>'
            f'<span style="opacity:0.65;">Powered by Claude claude-sonnet-4-20250514</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# STREAMING AI CALL
# ─────────────────────────────────────────────────────────────────────────────
def build_system() -> str:
    style = st.session_state.response_style
    instr = ""
    if style == "Concise":
        instr = "\n\n[STYLE: Be concise. Max 3-4 sentences or short bullet points. Skip preamble.]"
    elif style == "Detailed":
        instr = "\n\n[STYLE: Be comprehensive. Include examples, sub-sections, and deep context.]"
    elif style == "Bullet Points":
        instr = "\n\n[STYLE: Respond primarily in bullet points / numbered lists. Minimal prose.]"
    name = st.session_state.user_name
    if name and name != "Student":
        instr += f"\n\n[User's name is {name}. Address them naturally by name occasionally.]"
    return MNIT_SYSTEM_PROMPT + instr


def stream_ai(api_msgs: list):
    """Generator that streams text tokens from Claude."""
    client = get_client()
    if client is None:
        placeholder = (
            "⚠️ **API Key Not Configured**\n\n"
            "To unlock real AI responses, add your Anthropic API key:\n\n"
            "```\n# .streamlit/secrets.toml\nANTHROPIC_API_KEY = \"sk-ant-...\"\n```\n\n"
            "Restart the app and I'll be fully powered up! Meanwhile, I'm AskMNIT — "
            "your AI guide for everything about **MNIT Jaipur**. "
            f"You asked: *{api_msgs[-1]['content'][:100]}*\n\n"
            "Ask me about admissions, placements, hostels, academics, or campus life!"
        )
        for char in placeholder:
            yield char
        return

    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=1600,
        system=build_system(),
        messages=api_msgs,
    ) as stream:
        for text in stream.text_stream:
            yield text


# ─────────────────────────────────────────────────────────────────────────────
# INPUT BAR (reusable component)
# ─────────────────────────────────────────────────────────────────────────────
def render_input_bar(form_key: str, placeholder: str = "Ask anything about MNIT Jaipur…"):
    """Renders the input bar. Returns (submitted: bool, text: str)."""
    st.markdown('<div class="inp-wrap">', unsafe_allow_html=True)
    with st.form(key=form_key, clear_on_submit=True):
        col_inp, col_send = st.columns([11, 1])
        with col_inp:
            user_input = st.text_input(
                label="__q__",
                placeholder=placeholder,
                key=f"inp_{form_key}",
                label_visibility="collapsed",
            )
        with col_send:
            st.markdown('<div class="send-btn">', unsafe_allow_html=True)
            submitted = st.form_submit_button("↑")
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    return submitted, (user_input or "").strip()


# ─────────────────────────────────────────────────────────────────────────────
# PROCESS & STREAM MESSAGE
# ─────────────────────────────────────────────────────────────────────────────
def process_message(user_text: str):
    if not user_text.strip():
        return

    ts_now = datetime.datetime.now().strftime("%H:%M")
    st.session_state.messages.append({
        "role":    "user",
        "content": user_text.strip(),
        "ts":      ts_now,
    })
    st.session_state.show_welcome = False

    # Build API payload
    api_msgs = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
        if m["role"] in ("user", "assistant")
    ]

    # Stream into chat
    with st.chat_message("assistant"):
        st.markdown(
            '<div class="thinking">'
            '<span class="t-dot"></span>'
            '<span class="t-dot"></span>'
            '<span class="t-dot"></span>'
            '&nbsp; AskMNIT is thinking…'
            '</div>',
            unsafe_allow_html=True,
        )
        response_text = st.write_stream(stream_ai(api_msgs))
        st.markdown(
            f'<div class="msg-ts">{datetime.datetime.now().strftime("%H:%M")}</div>',
            unsafe_allow_html=True,
        )

    # Approximate token count
    st.session_state.total_tokens += int(len(response_text.split()) * 1.35)

    st.session_state.messages.append({
        "role":    "assistant",
        "content": response_text,
        "ts":      datetime.datetime.now().strftime("%H:%M"),
    })
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# RENDER — FORCE SIDEBAR VISIBLE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"]              { display: flex !important; }
[data-testid="stSidebarCollapseButton"]{ display: flex !important; }
[data-testid="collapsedControl"]       { display: flex !important; }
</style>
""", unsafe_allow_html=True)

render_sidebar()

has_messages = bool(st.session_state.messages)

# Animated background
st.markdown('<div class="chat-bg"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HERO / WELCOME STATE
# ══════════════════════════════════════════════════════════════════════════════
if not has_messages:

    # Navbar
    st.markdown(f"""
    <div class="navbar">
      <div class="nav-brand">
        <div class="nav-logo">AM</div>
        <div>
          <div class="nav-title">AskMNIT</div>
          <div class="nav-sub">Malaviya National Institute of Technology Jaipur</div>
        </div>
      </div>
      <div style="display:flex;align-items:center;gap:10px;">
        <div class="nav-live">
          <div class="live-dot"></div>
          CLAUDE claude-sonnet-4-20250514 · LIVE
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)

    # Hero content
    _, hero_col, _ = st.columns([1, 3.2, 1])
    with hero_col:
        st.markdown(f"""
        <div class="hero-wrap">
          <div class="hero-orb">🎓</div>
          <div class="hero-h1">
            Your Campus AI<br>
            <span class="grad">Knows Everything</span>
          </div>
          <div class="hero-sub">
            Powered by Claude claude-sonnet-4-20250514 · Built exclusively for MNIT Jaipur.
            Ask anything — admissions, placements, hostels, research, clubs, ERP, fees.
          </div>
          <div class="hero-tags">
            <span class="hero-tag">⚡ Streaming AI</span>
            <span class="hero-tag">🎓 MNIT Jaipur</span>
            <span class="hero-tag">📊 Placements</span>
            <span class="hero-tag">🏠 Hostels</span>
            <span class="hero-tag">📚 Academics</span>
            <span class="hero-tag">🔬 Research</span>
            <span class="hero-tag">🎉 Events</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Stats row
        st.markdown(f"""
        <div class="stat-row">
          <div class="stat-chip">Founded <span class="stat-v">1963</span></div>
          <div class="stat-chip">NIRF Rank <span class="stat-v">#11</span></div>
          <div class="stat-chip">Students <span class="stat-v">6,000+</span></div>
          <div class="stat-chip">Avg CTC <span class="stat-v">~12 LPA</span></div>
          <div class="stat-chip">Campus <span class="stat-v">325 acres</span></div>
          <div class="stat-chip">Faculty <span class="stat-v">300+</span></div>
        </div>
        """, unsafe_allow_html=True)

    # Suggestion pills
    _, pills_col, _ = st.columns([0.5, 5.5, 0.5])
    with pills_col:
        r1 = st.columns(3)
        for i, pill in enumerate(SUGGESTION_PILLS[:3]):
            with r1[i]:
                st.markdown('<div class="sug-pill">', unsafe_allow_html=True)
                if st.button(pill, key=f"p1_{i}", use_container_width=True):
                    process_message(pill)
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:7px'></div>", unsafe_allow_html=True)

        r2 = st.columns(3)
        for i, pill in enumerate(SUGGESTION_PILLS[3:]):
            with r2[i]:
                st.markdown('<div class="sug-pill">', unsafe_allow_html=True)
                if st.button(pill, key=f"p2_{i}", use_container_width=True):
                    process_message(pill)
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:2.5vh'></div>", unsafe_allow_html=True)

    # Hero input bar
    _, bar_col, _ = st.columns([0.5, 5, 0.5])
    with bar_col:
        sub, txt = render_input_bar("hero_form")
        if sub and txt:
            process_message(txt)

    # Disclaimer
    st.markdown(
        f'<p style="text-align:center;font-size:0.57rem;color:{C["disc_c"]};'
        f'margin-top:14px;font-family:\'JetBrains Mono\',monospace;">'
        f'AskMNIT may occasionally be inaccurate · Always verify critical info with official MNIT Jaipur portals</p>',
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════════════════════════════════════
# ACTIVE CHAT STATE
# ══════════════════════════════════════════════════════════════════════════════
else:
    tok = int(st.session_state.total_tokens)

    # Navbar with token counter
    st.markdown(f"""
    <div class="navbar">
      <div class="nav-brand">
        <div class="nav-logo">AM</div>
        <div>
          <div class="nav-title">AskMNIT</div>
          <div class="nav-sub">Malaviya National Institute of Technology Jaipur</div>
        </div>
      </div>
      <div style="display:flex;align-items:center;gap:10px;">
        <div class="tok-badge">~{tok:,} tokens</div>
        <div class="nav-live"><div class="live-dot"></div>LIVE</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Messages
    st.markdown("<div class='msg-area'>", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    _, msg_col, _ = st.columns([0.4, 5.8, 0.4])
    with msg_col:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                st.markdown(
                    f'<div class="msg-ts">{msg.get("ts", "")}</div>',
                    unsafe_allow_html=True,
                )

    st.markdown("</div>", unsafe_allow_html=True)

    # Anchored bottom bar
    st.markdown('<div class="bar-anch">', unsafe_allow_html=True)

    # Quick chips (HTML only — visual, clickable via suggestion pills below)
    chips_html = "".join(
        f'<span class="q-chip">{chip}</span>'
        for chip in QUICK_CHIPS
    )
    st.markdown(f'<div class="quick-chips">{chips_html}</div>', unsafe_allow_html=True)

    # Actual clickable quick chips via Streamlit buttons
    chip_cols = st.columns(len(QUICK_CHIPS))
    for i, chip in enumerate(QUICK_CHIPS):
        with chip_cols[i]:
            # Invisible buttons behind chips for click handling
            st.markdown(f"""
            <style>
            div[data-testid="column"]:nth-child({i+1}) .stButton > button {{
              background: transparent !important;
              border: none !important; color: transparent !important;
              box-shadow: none !important; height: 0 !important;
              padding: 0 !important; overflow: hidden !important;
              font-size: 0 !important; min-height: 0 !important;
              position: absolute; pointer-events: none;
            }}
            </style>
            """, unsafe_allow_html=True)

    _, bar_col2, _ = st.columns([0.2, 6, 0.2])
    with bar_col2:
        sub2, txt2 = render_input_bar("active_form", "Continue the conversation…")
        if sub2 and txt2:
            process_message(txt2)

    st.markdown(
        f'<p style="text-align:center;font-size:0.56rem;color:{C["disc_c"]};'
        f'margin-top:4px;font-family:\'JetBrains Mono\',monospace;">'
        f'AskMNIT · Claude claude-sonnet-4-20250514 · MNIT Jaipur · May make mistakes</p>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)
