"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          AskMNIT — Premium Student Dashboard & AI Assistant                 ║
║          Single-file Streamlit Application · MNIT Jaipur                   ║
║          Stack: Python + Streamlit + Anthropic Claude API                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

SETUP:
    pip install streamlit anthropic pdfplumber pandas
    export ANTHROPIC_API_KEY="your-key-here"
    streamlit run app.py
"""

import streamlit as st
import anthropic
import json
import datetime
import re
import math
import pandas as pd
from io import BytesIO

# ─── PDF Parsing Libraries ────────────────────────────────────────────────────
# Priority: pdfplumber > PyPDF2. Install via: pip install pdfplumber
try:
    import pdfplumber
    PDF_LIB = "pdfplumber"
except ImportError:
    try:
        import PyPDF2
        PDF_LIB = "pypdf2"
    except ImportError:
        PDF_LIB = None


# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION  (must be first Streamlit call)
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AskMNIT — Smart Campus Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help":     "https://mnit.ac.in",
        "Report a bug": None,
        "About":        "AskMNIT v1.0 — Premium Student Portal for MNIT Jaipur",
    },
)


# ══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS — GLASSMORPHIC DARK THEME
# Font: Syne (display) + DM Sans (body) for a modern, premium engineering feel
# ══════════════════════════════════════════════════════════════════════════════
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Reset & Base ─────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; }

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
}

/* ── App Background ──────────────────────────────────────────────────────── */
.stApp {
    background:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(59,130,246,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 100%, rgba(139,92,246,0.10) 0%, transparent 55%),
        #080812 !important;
    min-height: 100vh;
}

/* ── Hide Streamlit Defaults ─────────────────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }
.viewerBadge_container__1QSob { display: none !important; }

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: rgba(6, 6, 18, 0.97) !important;
    border-right: 1px solid rgba(79, 158, 255, 0.12) !important;
    backdrop-filter: blur(24px) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}
[data-testid="stSidebar"] .block-container {
    padding: 0 !important;
}

/* ── Main content ────────────────────────────────────────────────────────── */
.main .block-container {
    padding: 1.5rem 2.5rem 3rem 2.5rem !important;
    max-width: 1440px !important;
}

/* ── Glass Card ──────────────────────────────────────────────────────────── */
.glass-card {
    background: rgba(255, 255, 255, 0.035);
    border: 1px solid rgba(255, 255, 255, 0.075);
    border-radius: 20px;
    padding: 1.4rem 1.6rem;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    margin-bottom: 1rem;
    transition: border-color 0.25s, box-shadow 0.25s;
}
.glass-card:hover {
    border-color: rgba(79, 158, 255, 0.22);
    box-shadow: 0 8px 40px rgba(79, 158, 255, 0.06);
}

/* ── Neon Title ──────────────────────────────────────────────────────────── */
.neon-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 2.1rem;
    font-weight: 800;
    background: linear-gradient(135deg, #60A5FA 0%, #A78BFA 55%, #38BDF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.3px;
    line-height: 1.2;
}
.neon-subtitle {
    color: rgba(255, 255, 255, 0.38);
    font-size: 0.875rem;
    font-weight: 400;
    margin-top: 0.2rem;
}

/* ── Section Heading ─────────────────────────────────────────────────────── */
.section-heading {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: white;
    margin-bottom: 1rem;
}

/* ── Metric Card ─────────────────────────────────────────────────────────── */
.metric-card {
    background: rgba(79, 158, 255, 0.05);
    border: 1px solid rgba(79, 158, 255, 0.18);
    border-radius: 18px;
    padding: 1.3rem 1.2rem;
    text-align: center;
    transition: all 0.28s ease;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #4F9EFF, #A78BFA);
    opacity: 0.6;
}
.metric-card:hover {
    background: rgba(79, 158, 255, 0.09);
    transform: translateY(-2px);
    box-shadow: 0 16px 40px rgba(79, 158, 255, 0.12);
}
.metric-icon  { font-size: 1.3rem; margin-bottom: 0.5rem; }
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.9rem;
    font-weight: 700;
    color: #60A5FA;
    line-height: 1.1;
}
.metric-label {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.42);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 0.3rem;
}

/* ── Timeline ────────────────────────────────────────────────────────────── */
.timeline-item {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 0.9rem 1rem;
    border-radius: 14px;
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.055);
    margin-bottom: 0.6rem;
    transition: all 0.25s;
}
.timeline-item.live {
    background: rgba(79, 158, 255, 0.08);
    border-color: rgba(79, 158, 255, 0.28);
    box-shadow: 0 0 20px rgba(79, 158, 255, 0.07);
}
.timeline-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    background: rgba(255,255,255,0.15);
    flex-shrink: 0;
    margin-top: 5px;
}
.timeline-item.live .timeline-dot { background: #34D399; box-shadow: 0 0 8px #34D399; }
.timeline-time { font-size: 0.78rem; font-weight: 600; color: #60A5FA; min-width: 95px; padding-top: 1px; }
.timeline-content { flex: 1; }
.timeline-subject { font-weight: 600; color: #fff; font-size: 0.9rem; }
.timeline-venue   { color: rgba(255,255,255,0.4); font-size: 0.77rem; margin-top: 2px; }

/* ── Event Cards ─────────────────────────────────────────────────────────── */
.event-card {
    background: rgba(139,92,246,0.05);
    border: 1px solid rgba(139,92,246,0.18);
    border-radius: 14px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.65rem;
    display: flex;
    align-items: flex-start;
    gap: 0.9rem;
    transition: all 0.25s;
}
.event-card:hover { border-color: rgba(139,92,246,0.35); transform: translateX(2px); }
.event-date {
    background: rgba(139,92,246,0.18);
    border-radius: 10px;
    padding: 0.35rem 0.7rem;
    font-size: 0.72rem;
    font-weight: 600;
    color: #A78BFA;
    white-space: nowrap;
    flex-shrink: 0;
}
.event-title { font-weight: 600; color: #fff; font-size: 0.87rem; }
.event-desc  { color: rgba(255,255,255,0.42); font-size: 0.75rem; margin-top: 2px; }

/* ── Badges ──────────────────────────────────────────────────────────────── */
.badge {
    display: inline-block;
    padding: 0.18rem 0.6rem;
    border-radius: 20px;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.4px;
}
.badge-blue   { background: rgba(96,165,250,0.14); color: #60A5FA; border: 1px solid rgba(96,165,250,0.28); }
.badge-green  { background: rgba(52,211,153,0.14); color: #34D399; border: 1px solid rgba(52,211,153,0.28); }
.badge-purple { background: rgba(167,139,250,0.14); color: #A78BFA; border: 1px solid rgba(167,139,250,0.28); }
.badge-orange { background: rgba(251,146,60,0.14); color: #FB923C; border: 1px solid rgba(251,146,60,0.28); }
.badge-red    { background: rgba(248,113,113,0.14); color: #F87171; border: 1px solid rgba(248,113,113,0.28); }

/* ── Chat Header ─────────────────────────────────────────────────────────── */
.chat-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.1rem 1.4rem;
    background: rgba(79, 158, 255, 0.05);
    border: 1px solid rgba(79, 158, 255, 0.15);
    border-radius: 20px;
    margin-bottom: 0.8rem;
}
.chat-avatar {
    width: 46px; height: 46px;
    border-radius: 50%;
    background: linear-gradient(135deg, #4F9EFF 0%, #A78BFA 100%);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    flex-shrink: 0;
    box-shadow: 0 0 20px rgba(79,158,255,0.3);
}
.ai-name   { font-family: 'Syne', sans-serif; font-weight: 700; color: #fff; font-size: 0.95rem; }
.ai-status { color: #34D399; font-size: 0.72rem; display: flex; align-items: center; gap: 4px; }
.status-dot { width:7px; height:7px; border-radius:50%; background:#34D399; box-shadow:0 0 6px #34D399; }

/* ── Sidebar Nav Button ──────────────────────────────────────────────────── */
div[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 12px !important;
    color: rgba(255,255,255,0.5) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 0.65rem 1rem !important;
    transition: all 0.2s !important;
    box-shadow: none !important;
    width: 100%;
}
div[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(79,158,255,0.09) !important;
    border-color: rgba(79,158,255,0.2) !important;
    color: #60A5FA !important;
    transform: none !important;
}

/* Active sidebar button override — applied via container class */
.sidebar-active .stButton > button {
    background: rgba(79,158,255,0.13) !important;
    border-color: rgba(79,158,255,0.3) !important;
    color: #60A5FA !important;
}

/* ── Main CTA Buttons ────────────────────────────────────────────────────── */
.main .stButton > button {
    background: linear-gradient(135deg, #3B82F6 0%, #6366F1 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.48rem 1.4rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.87rem !important;
    transition: all 0.28s ease !important;
    box-shadow: 0 4px 18px rgba(59,130,246,0.28) !important;
}
.main .stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 28px rgba(59,130,246,0.42) !important;
}
.main .stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Inputs ──────────────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: white !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: rgba(79,158,255,0.45) !important;
    box-shadow: 0 0 0 3px rgba(79,158,255,0.08) !important;
}
.stSelectbox > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: white !important;
}

/* ── Labels ──────────────────────────────────────────────────────────────── */
label, .stSelectbox label, .stTextInput label,
.stNumberInput label, [data-testid="stMarkdownContainer"] p {
    color: rgba(255,255,255,0.6) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.84rem !important;
}

/* ── Tabs ────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 14px !important;
    padding: 4px !important;
    gap: 2px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    color: rgba(255,255,255,0.45) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    padding: 0.4rem 1rem !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(79,158,255,0.14) !important;
    color: #60A5FA !important;
}

/* ── DataFrames ──────────────────────────────────────────────────────────── */
.stDataFrame { border-radius: 16px !important; overflow: hidden; }
[data-testid="stDataFrameResizable"] { border-radius: 16px !important; }

/* ── File Uploader ───────────────────────────────────────────────────────── */
[data-testid="stFileUploader"] > div {
    background: rgba(255,255,255,0.02) !important;
    border: 1px dashed rgba(79,158,255,0.28) !important;
    border-radius: 16px !important;
    transition: all 0.25s;
}
[data-testid="stFileUploader"] > div:hover {
    border-color: rgba(79,158,255,0.5) !important;
    background: rgba(79,158,255,0.04) !important;
}

/* ── Alerts ──────────────────────────────────────────────────────────────── */
.stSuccess > div { background: rgba(52,211,153,0.07) !important; border-radius: 12px !important; border: 1px solid rgba(52,211,153,0.2) !important; }
.stInfo    > div { background: rgba(96,165,250,0.07) !important; border-radius: 12px !important; border: 1px solid rgba(96,165,250,0.2) !important; }
.stWarning > div { background: rgba(251,146,60,0.07) !important; border-radius: 12px !important; border: 1px solid rgba(251,146,60,0.2) !important; }
.stError   > div { background: rgba(248,113,113,0.07) !important; border-radius: 12px !important; border: 1px solid rgba(248,113,113,0.2) !important; }

/* ── Chat Messages ───────────────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 16px !important;
}

/* ── Headings ────────────────────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {
    color: white !important;
    font-family: 'Syne', sans-serif !important;
}

/* ── Divider ─────────────────────────────────────────────────────────────── */
hr { border-color: rgba(255,255,255,0.07) !important; margin: 1rem 0 !important; }

/* ── Scrollbar ───────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb { background: rgba(79,158,255,0.25); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(79,158,255,0.45); }

/* ── Progress bar ────────────────────────────────────────────────────────── */
.stProgress > div > div { background: linear-gradient(90deg, #3B82F6, #A78BFA) !important; border-radius: 4px !important; }

/* ── GPA course row ──────────────────────────────────────────────────────── */
.gpa-row {
    display: flex; align-items: center; gap: 0.6rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}

/* ── Attendance bar ──────────────────────────────────────────────────────── */
.att-bar-bg {
    height: 5px;
    background: rgba(255,255,255,0.07);
    border-radius: 3px;
    margin-top: 5px;
    overflow: hidden;
}
.att-bar-fill { height: 100%; border-radius: 3px; transition: width 0.5s ease; }

/* ── code inline ─────────────────────────────────────────────────────────── */
code {
    background: rgba(79,158,255,0.12) !important;
    color: #60A5FA !important;
    border-radius: 5px !important;
    padding: 1px 5px !important;
    font-size: 0.82em !important;
}

/* ── Spinner ─────────────────────────────────────────────────────────────── */
.stSpinner > div { border-top-color: #4F9EFF !important; }
</style>
"""


# ══════════════════════════════════════════════════════════════════════════════
# STATIC DATA
# ══════════════════════════════════════════════════════════════════════════════

# Default demo schedule — displayed if no PDF is uploaded
DEFAULT_SCHEDULE = [
    {"day": "Monday",    "time": "08:00–08:55", "subject": "Data Structures & Algorithms",  "venue": "LT-3",  "code": "CS301"},
    {"day": "Monday",    "time": "09:00–09:55", "subject": "Computer Networks",             "venue": "LT-3",  "code": "CS302"},
    {"day": "Monday",    "time": "11:00–11:55", "subject": "Operating Systems",             "venue": "LT-1",  "code": "CS303"},
    {"day": "Monday",    "time": "14:00–15:55", "subject": "DBMS Lab",                      "venue": "CL-2",  "code": "CS304L"},
    {"day": "Tuesday",   "time": "08:00–08:55", "subject": "Theory of Computation",         "venue": "LT-5",  "code": "CS305"},
    {"day": "Tuesday",   "time": "09:00–09:55", "subject": "Data Structures & Algorithms",  "venue": "LT-3",  "code": "CS301"},
    {"day": "Tuesday",   "time": "11:00–11:55", "subject": "Software Engineering",          "venue": "LT-2",  "code": "CS306"},
    {"day": "Wednesday", "time": "08:00–08:55", "subject": "Computer Networks",             "venue": "LT-4",  "code": "CS302"},
    {"day": "Wednesday", "time": "10:00–11:55", "subject": "Algorithms Lab",                "venue": "CL-1",  "code": "CS301L"},
    {"day": "Wednesday", "time": "14:00–14:55", "subject": "Operating Systems",             "venue": "LT-1",  "code": "CS303"},
    {"day": "Thursday",  "time": "08:00–08:55", "subject": "Theory of Computation",         "venue": "LT-5",  "code": "CS305"},
    {"day": "Thursday",  "time": "09:00–09:55", "subject": "DBMS",                          "venue": "LT-2",  "code": "CS307"},
    {"day": "Thursday",  "time": "11:00–12:55", "subject": "Networks Lab",                  "venue": "NL-1",  "code": "CS302L"},
    {"day": "Friday",    "time": "08:00–08:55", "subject": "Software Engineering",          "venue": "LT-2",  "code": "CS306"},
    {"day": "Friday",    "time": "09:00–09:55", "subject": "DBMS",                          "venue": "LT-2",  "code": "CS307"},
    {"day": "Friday",    "time": "11:00–11:55", "subject": "Data Structures & Algorithms",  "venue": "LT-3",  "code": "CS301"},
]

CAMPUS_EVENTS = [
    {"date": "Mar 28",  "title": "Hackathon 2025 — TechVenture",     "desc": "24-hr national hackathon · Prizes worth ₹2L",         "tag": "Tech"},
    {"date": "Apr 02",  "title": "Annual Cultural Fest — Vividha",    "desc": "3-day music, dance & drama extravaganza",              "tag": "Cultural"},
    {"date": "Apr 07",  "title": "Guest Lecture: AI & Future of CS",  "desc": "Auditorium · Open for all students",                  "tag": "Academic"},
    {"date": "Apr 12",  "title": "Sports Week 2025 Begins",           "desc": "Inter-branch cricket, football, badminton",            "tag": "Sports"},
    {"date": "Apr 18",  "title": "Placement Orientation — TNP Cell",  "desc": "Resume building & mock interview sessions",           "tag": "Placement"},
    {"date": "Apr 24",  "title": "Open Source Day — IEEE MNIT",       "desc": "Contribute to open-source projects, mentored sessions","tag": "Tech"},
]

ERP_LINKS = [
    {"name": "Student ERP Portal",   "url": "https://erp.mnit.ac.in",          "desc": "Fees, Exam Forms, Academic Records", "icon": "🏛️"},
    {"name": "Course Registration",  "url": "https://erp.mnit.ac.in/student",  "desc": "Add/Drop courses for this semester", "icon": "📋"},
    {"name": "Fee Payment Portal",   "url": "https://erp.mnit.ac.in/fees",     "desc": "Tuition, hostel, and misc fees",     "icon": "💳"},
    {"name": "Result & Transcript",  "url": "https://erp.mnit.ac.in/result",   "desc": "Semester results and grade cards",   "icon": "📊"},
    {"name": "Library OPAC",         "url": "https://opac.mnit.ac.in",         "desc": "Search and reserve library books",   "icon": "📚"},
    {"name": "Placement Cell (TNP)", "url": "https://placement.mnit.ac.in",    "desc": "Job listings, internship postings",  "icon": "💼"},
]

PYQ_DATA = {
    "CSE": {
        "Data Structures & Algorithms": ["2024 ETE", "2024 MTE", "2023 ETE", "2023 MTE", "2022 ETE"],
        "Computer Networks":            ["2024 ETE", "2024 MTE", "2023 ETE", "2023 MTE"],
        "Operating Systems":            ["2024 ETE", "2023 MTE", "2023 ETE", "2022 ETE"],
        "Theory of Computation":        ["2024 ETE", "2024 MTE", "2023 ETE"],
        "DBMS":                         ["2024 ETE", "2023 MTE", "2023 ETE"],
        "Software Engineering":         ["2024 ETE", "2024 MTE"],
    },
    "ECE": {
        "Signals & Systems":     ["2024 ETE", "2024 MTE", "2023 ETE"],
        "Digital Electronics":   ["2024 ETE", "2023 MTE", "2023 ETE"],
        "Microprocessors":       ["2024 ETE", "2024 MTE", "2023 ETE"],
        "VLSI Design":           ["2024 ETE", "2023 ETE"],
    },
    "ME":  {
        "Thermodynamics":        ["2024 ETE", "2023 MTE", "2023 ETE"],
        "Fluid Mechanics":       ["2024 ETE", "2023 ETE"],
        "Machine Design":        ["2024 ETE", "2024 MTE"],
    },
    "EE":  {
        "Power Systems":         ["2024 ETE", "2024 MTE", "2023 ETE"],
        "Electrical Machines":   ["2024 ETE", "2023 ETE"],
        "Control Systems":       ["2024 ETE", "2024 MTE"],
    },
    "CE":  {
        "Structural Analysis":   ["2024 ETE", "2023 ETE"],
        "Soil Mechanics":        ["2024 ETE", "2024 MTE"],
    },
}

IMPORTANT_DATES = [
    ("Jan 06, 2025",   "Even Semester Begins",              "badge-blue"),
    ("Feb 24–Mar 01",  "Mid-Term Examinations (MTE)",        "badge-orange"),
    ("Mar 10",         "Last day to withdraw courses",       "badge-purple"),
    ("Apr 28–May 10",  "End-Term Examinations (ETE)",        "badge-orange"),
    ("May 15",         "Result Declaration",                 "badge-green"),
    ("May 20",         "Summer Vacation Begins",             "badge-blue"),
]

GRADE_POINTS = {"O": 10, "A+": 10, "A": 9, "B+": 8, "B": 7, "C+": 6, "C": 5, "D": 4, "F": 0}

TAG_COLORS = {
    "Tech": "badge-blue", "Cultural": "badge-purple", "Academic": "badge-green",
    "Sports": "badge-orange", "Placement": "badge-blue",
}


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
def init_session_state():
    defaults = {
        "active_tab":       "Dashboard",
        "student_name":     "Student",
        "student_branch":   "Computer Science & Engineering",
        "student_id":       "2021KUEC2XXX",
        "student_semester": "6th Semester",
        "schedule":         [],
        "pdf_parsed":       False,
        "attendance":       {},   # {subject: {"present": int, "total": int}}
        "messages":         [],   # chat history
        "gpa_courses":      [
            {"name": "Data Structures", "credits": 4, "grade": "A"},
            {"name": "Computer Networks","credits": 4, "grade": "B+"},
            {"name": "Operating Systems","credits": 4, "grade": "A"},
            {"name": "Software Engg.",   "credits": 3, "grade": "O"},
            {"name": "DBMS",             "credits": 4, "grade": "A+"},
        ],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
# PDF SCHEDULE PARSER
# ══════════════════════════════════════════════════════════════════════════════
def parse_pdf_schedule(uploaded_file):
    """
    Parse a timetable PDF and return a list of schedule entries.

    Each entry is a dict:
        {"day": str, "time": str, "subject": str, "venue": str, "code": str}

    ╔═══════════════════════════════════════════════════════════════════╗
    ║  CUSTOMIZATION GUIDE                                              ║
    ║                                                                   ║
    ║  1. TABLE-BASED PDF (most MNIT/NIT ERP exports):                 ║
    ║     Edit  _parse_table_rows()  — adjust col indices              ║
    ║     to match your table's column order.                           ║
    ║                                                                   ║
    ║  2. TEXT-BASED PDF (plain-text timetable):                        ║
    ║     Edit  _parse_text_schedule() — adjust the regex              ║
    ║     to match your PDF's time format.                              ║
    ║                                                                   ║
    ║  3. GRID-STYLE (Days as columns, slots as rows):                  ║
    ║     See _parse_grid_table() below.                                ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """
    schedule = []
    raw_text = ""

    # ── Step 1 : Extract content ──────────────────────────────────────────────
    if PDF_LIB == "pdfplumber":
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    # ── Try table extraction first ──────────────────────────
                    # CUSTOMIZE: change table_settings to match your PDF grid
                    tables = page.extract_tables(table_settings={
                        "vertical_strategy":   "lines",   # try "text" for borderless tables
                        "horizontal_strategy": "lines",   # try "text" for borderless tables
                        "snap_tolerance":      3,
                    })
                    for tbl in tables:
                        parsed = _parse_table_rows(tbl)
                        schedule.extend(parsed)
                        if not parsed:
                            # Fallback: check if it looks like a grid (days as columns)
                            schedule.extend(_parse_grid_table(tbl))

                    # ── Always collect text as fallback ─────────────────────
                    raw_text += (page.extract_text() or "") + "\n"

        except Exception as e:
            st.warning(f"pdfplumber error: {e}")

    elif PDF_LIB == "pypdf2":
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                raw_text += (page.extract_text() or "") + "\n"
        except Exception as e:
            st.warning(f"PyPDF2 error: {e}")

    # ── Step 2 : Regex fallback on raw text ───────────────────────────────────
    if not schedule and raw_text.strip():
        schedule = _parse_text_schedule(raw_text)

    # ── Step 3 : Return result ────────────────────────────────────────────────
    if not schedule:
        st.info(
            "⚠️ Could not auto-parse your PDF. "
            "Using the demo schedule. Customize `parse_pdf_schedule()` in app.py."
        )
        return DEFAULT_SCHEDULE

    return schedule


def _parse_table_rows(table):
    """
    Helper A — Row-per-class tables (one class per row).

    Expected columns: Day | Time | Subject | Venue | Code (optional)
    CUSTOMIZE: change col_* index values to match your column order.
    """
    entries = []
    if not table or len(table) < 2:
        return entries

    # Auto-detect column positions from header row
    header = [str(c).strip().lower() if c else "" for c in (table[0] or [])]

    # CUSTOMIZE these fallback indices if auto-detection fails
    col_day  = next((i for i, h in enumerate(header) if "day"  in h), 0)
    col_time = next((i for i, h in enumerate(header) if "time" in h or "slot" in h), 1)
    col_subj = next((i for i, h in enumerate(header) if "sub"  in h or "course" in h or "name" in h), 2)
    col_ven  = next((i for i, h in enumerate(header) if "ven"  in h or "room"   in h or "loc"  in h), 3)
    col_code = next((i for i, h in enumerate(header) if "code" in h), -1)

    for row in table[1:]:
        if not row or all(c is None or str(c).strip() == "" for c in row):
            continue
        try:
            safe = lambda idx: str(row[idx] or "").strip() if row and idx < len(row) else ""
            day     = safe(col_day)
            time_   = safe(col_time)
            subject = safe(col_subj)
            venue   = safe(col_ven) or "TBA"
            code    = safe(col_code) if col_code >= 0 else ""

            if subject and time_:
                entries.append({"day": day or "Unknown", "time": time_,
                                 "subject": subject, "venue": venue, "code": code})
        except (IndexError, ValueError):
            continue
    return entries


def _parse_grid_table(table):
    """
    Helper B — Grid-style tables (time slots as rows, days as columns).

    Row 0: ["", "Monday", "Tuesday", ...]
    Col 0: time strings like "08:00-08:55"
    CUSTOMIZE: ensure days in header match weekday names.
    """
    entries = []
    if not table or len(table) < 2:
        return entries

    header = [str(c).strip() if c else "" for c in (table[0] or [])]
    days   = header[1:]   # skip the first "time" column

    for row in table[1:]:
        if not row:
            continue
        time_ = str(row[0] or "").strip()
        if not time_:
            continue
        for col_idx, day in enumerate(days, start=1):
            if col_idx >= len(row):
                continue
            cell = str(row[col_idx] or "").strip()
            if cell:
                # CUSTOMIZE: split on newline if cell contains "Subject\nVenue"
                parts   = cell.split("\n", 1)
                subject = parts[0].strip()
                venue   = parts[1].strip() if len(parts) > 1 else "TBA"
                if subject:
                    entries.append({"day": day, "time": time_,
                                     "subject": subject, "venue": venue, "code": ""})
    return entries


def _parse_text_schedule(text):
    """
    Helper C — Plain-text fallback using regex.

    CUSTOMIZE the time_pattern to match your PDF's time format.
    Supported formats:
        08:00-08:55  Data Structures  LT-3
        8:00AM - 8:55AM  Networks  Room 205
    """
    entries = []
    lines   = text.split("\n")

    # CUSTOMIZE: adjust regex to your time format
    time_pattern = re.compile(
        r"(\d{1,2}[:.]\d{2}\s*(?:AM|PM)?)\s*[-–to]+\s*(\d{1,2}[:.]\d{2}\s*(?:AM|PM)?)"
        r"\s+(.+?)(?:\s{2,}|\t)(.+)",
        re.IGNORECASE,
    )
    day_pattern = re.compile(
        r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|"
        r"Mon|Tue|Wed|Thu|Fri|Sat)\b",
        re.IGNORECASE,
    )
    day_map = {
        "mon": "Monday",  "monday": "Monday",  "tue": "Tuesday",  "tuesday": "Tuesday",
        "wed": "Wednesday","wednesday":"Wednesday","thu":"Thursday","thursday":"Thursday",
        "fri": "Friday",  "friday":  "Friday",  "sat": "Saturday", "saturday":"Saturday",
    }

    current_day = "Monday"
    for line in lines:
        line = line.strip()
        if not line:
            continue
        dm = day_pattern.match(line)
        if dm:
            current_day = day_map.get(dm.group(1).lower(), current_day)
        tm = time_pattern.search(line)
        if tm:
            s, e, subj, venue = tm.group(1), tm.group(2), tm.group(3), tm.group(4)
            entries.append({
                "day": current_day,
                "time": f"{s.strip()}–{e.strip()}",
                "subject": subj.strip(),
                "venue":   venue.strip(),
                "code":    "",
            })
    return entries


# ══════════════════════════════════════════════════════════════════════════════
# HELPER UTILITIES
# ══════════════════════════════════════════════════════════════════════════════
def get_active_schedule():
    return st.session_state.schedule or DEFAULT_SCHEDULE

def get_today_schedule():
    today = datetime.datetime.now().strftime("%A")
    return [s for s in get_active_schedule() if s.get("day","").lower() == today.lower()]

def is_class_now(time_str):
    """Return True if current time falls within the given HH:MM–HH:MM slot."""
    now = datetime.datetime.now().time()
    try:
        parts = re.split(r"[-–—]", time_str)
        if len(parts) < 2:
            return False
        def parse_t(s):
            s = s.strip().replace(".", ":").replace(" ", "")
            for fmt in ("%H:%M", "%I:%M%p", "%I:%M %p"):
                try:
                    return datetime.datetime.strptime(s, fmt).time()
                except ValueError:
                    pass
            return None
        start, end = parse_t(parts[0]), parse_t(parts[1])
        return (start and end) and (start <= now <= end)
    except Exception:
        return False

def get_unique_subjects():
    """Return {subject: code} dict deduplicated from schedule."""
    seen = {}
    for item in get_active_schedule():
        subj = item.get("subject", "")
        if subj and subj not in seen:
            seen[subj] = item.get("code", "")
    return seen

def compute_overall_attendance():
    att = st.session_state.attendance
    if not att:
        return 0.0, 0, 0
    total_p = sum(v["present"] for v in att.values())
    total_t = sum(v["total"]   for v in att.values())
    pct     = round(total_p / total_t * 100, 1) if total_t else 0.0
    return pct, total_p, total_t

def circular_svg(pct, size=160):
    """Generate a premium SVG circular progress ring."""
    r  = 60
    c  = 2 * math.pi * r
    d  = max(0, min(pct, 100)) / 100 * c
    g  = c - d
    color = "#34D399" if pct >= 75 else ("#FBBF24" if pct >= 60 else "#F87171")
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 160 160" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="pg" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%"   stop-color="{color}"/>
          <stop offset="100%" stop-color="#A78BFA"/>
        </linearGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
          <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
      </defs>
      <circle cx="80" cy="80" r="{r}" fill="none"
              stroke="rgba(255,255,255,0.055)" stroke-width="11"/>
      <circle cx="80" cy="80" r="{r}" fill="none"
              stroke="url(#pg)" stroke-width="11"
              stroke-linecap="round"
              stroke-dasharray="{d:.2f} {g:.2f}"
              transform="rotate(-90 80 80)"
              filter="url(#glow)"/>
      <text x="80" y="74" text-anchor="middle"
            font-family="Syne,sans-serif" font-size="21" font-weight="700"
            fill="white">{pct}%</text>
      <text x="80" y="92" text-anchor="middle"
            font-family="DM Sans,sans-serif" font-size="10" fill="rgba(255,255,255,0.42)">
        Attendance
      </text>
    </svg>"""

def calculate_sgpa(courses):
    tw, tc = 0, 0
    for c in courses:
        gp = GRADE_POINTS.get(c.get("grade","F"), 0)
        cr = int(c.get("credits", 0))
        tw += gp * cr
        tc += cr
    return (round(tw / tc, 2) if tc else 0.0), tc


# ══════════════════════════════════════════════════════════════════════════════
# AI ASSISTANT
# ══════════════════════════════════════════════════════════════════════════════
SYSTEM_PROMPT = """You are AskMNIT, the official AI assistant for students at MNIT Jaipur
(Malaviya National Institute of Technology Jaipur) — one of India's premier NITs.

Your persona: A knowledgeable, warm senior student-mentor who also knows all admin details.

You have deep expertise in:
• MNIT's 10-point grading system: O/A+=10, A=9, B+=8, B=7, C+=6, C=5, D=4, F=0
• Semester structure: MTE (Mid-Term Exam), ETE (End-Term Exam); min 75% attendance or debarred
• Departments: CSE, ECE, ME, EE, CE, Chemical, Metallurgy, Architecture, MBA, MCA
• Hostels: Alaknanda, Banas, Chambal (boys), Mahi, Luni (girls), New Hostel Complex
• Student activities: SAC, NSS, NCC, IEEE MNIT, ACM, GDSC, Vividha (cultural), TechVenture (tech fest)
• ERP portal at erp.mnit.ac.in, OPAC library system, TNP (placement) cell
• Campus facilities: CL (computer labs), NL (network lab), LT (lecture theatres), Main Building, Auditorium, Sports Complex
• PhD, M.Tech, B.Tech, MBA, MCA programmes
• GATE-based M.Tech admissions, JEE-based B.Tech admissions, DASA

You help with:
1. Academic doubts (subject concepts, study tips, exam prep, project ideas, code debugging)
2. Campus information (hostels, messes, clubs, fests, scholarships)
3. Administrative queries (ERP, forms, attendance, leaves, certificates)
4. Career guidance (placements, internships, GATE, higher studies abroad)
5. General study planning and productivity

Rules:
- Always respond in Markdown with clear structure
- Be concise but thorough; use bullet points for lists
- When unsure about current details, direct to mnit.ac.in or relevant offices
- Add an MNIT-specific tip or resource whenever relevant
"""

def get_ai_response(user_message: str) -> str:
    """Stream a response from Claude and return the full text."""
    try:
        client = anthropic.Anthropic()

        # Build system prompt with student context
        system = SYSTEM_PROMPT
        if st.session_state.student_name != "Student":
            system += (
                f"\n\nCurrent student context:\n"
                f"- Name: {st.session_state.student_name}\n"
                f"- Branch: {st.session_state.student_branch}\n"
                f"- Semester: {st.session_state.student_semester}\n"
                f"- ID: {st.session_state.student_id}"
            )

        # Keep last 20 messages for context window
        api_msgs = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[-20:]
        ]
        api_msgs.append({"role": "user", "content": user_message})

        full = ""
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=system,
            messages=api_msgs,
        ) as stream:
            for text in stream.text_stream:
                full += text
        return full

    except anthropic.AuthenticationError:
        return (
            "⚠️ **Authentication Error**\n\n"
            "Set your API key:\n```bash\nexport ANTHROPIC_API_KEY='sk-ant-...'\n```"
        )
    except anthropic.RateLimitError:
        return "⚠️ **Rate limit reached.** Please wait a moment and try again."
    except Exception as e:
        return f"⚠️ **Error:** `{e}`"


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
NAV_ITEMS = [
    ("🏠", "Dashboard",  "Dashboard Home"),
    ("🤖", "AI Chat",    "AskMNIT Assistant"),
    ("🎓", "ERP Portal", "ERP & Services"),
    ("📚", "Academics",  "Notes & Timetable"),
    ("📝", "PYQs",       "Previous Year Qs"),
    ("📅", "Attendance", "Attendance Tracker"),
    ("🧮", "GPA Calc",   "GPA / CGPA Tool"),
    ("⚙️", "Profile",    "Student Profile"),
]

def render_sidebar():
    with st.sidebar:
        # ── Brand ─────────────────────────────────────────────────────────────
        st.markdown("""
        <div style="padding:1.6rem 1.4rem 1rem 1.4rem;">
            <div style="display:flex;align-items:center;gap:0.7rem;margin-bottom:0.3rem;">
                <div style="width:36px;height:36px;border-radius:50%;
                            background:linear-gradient(135deg,#3B82F6,#8B5CF6);
                            display:flex;align-items:center;justify-content:center;
                            font-size:1.1rem;box-shadow:0 0 16px rgba(59,130,246,0.4);">🎓</div>
                <div>
                    <div style="font-family:'Syne',sans-serif;font-size:1.25rem;font-weight:800;
                                background:linear-gradient(135deg,#60A5FA,#A78BFA);
                                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                                background-clip:text;line-height:1.1;">AskMNIT</div>
                    <div style="font-size:0.62rem;color:rgba(255,255,255,0.3);
                                letter-spacing:2px;text-transform:uppercase;">
                        Smart Campus Portal
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Student mini card ──────────────────────────────────────────────────
        att_pct, _, _ = compute_overall_attendance()
        att_color = "#34D399" if att_pct >= 75 else ("#FBBF24" if att_pct > 0 else "rgba(255,255,255,0.3)")
        st.markdown(f"""
        <div style="margin:0 1rem 1.2rem;padding:0.85rem 1rem;
                    background:rgba(79,158,255,0.06);
                    border:1px solid rgba(79,158,255,0.18);border-radius:14px;">
            <div style="font-weight:600;color:white;font-size:0.87rem;">
                👤 {st.session_state.student_name}
            </div>
            <div style="color:rgba(255,255,255,0.4);font-size:0.74rem;margin-top:2px;">
                {st.session_state.student_branch[:28]}{'…' if len(st.session_state.student_branch)>28 else ''}
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-top:6px;">
                <span style="color:rgba(255,255,255,0.3);font-size:0.7rem;">
                    {st.session_state.student_id}
                </span>
                <span style="color:{att_color};font-size:0.72rem;font-weight:600;">
                    {att_pct}% att.
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Navigation ─────────────────────────────────────────────────────────
        st.markdown("""
        <div style="padding:0 0.8rem 0.4rem;font-size:0.65rem;
                    color:rgba(255,255,255,0.25);text-transform:uppercase;letter-spacing:1.5px;">
            Navigation
        </div>
        """, unsafe_allow_html=True)

        for icon, key, label in NAV_ITEMS:
            active = st.session_state.active_tab == key
            prefix = "▸ " if active else "  "
            with st.container():
                if active:
                    st.markdown('<div class="sidebar-active">', unsafe_allow_html=True)
                if st.button(f"{icon}  {prefix}{label}", key=f"nav_{key}", use_container_width=True):
                    st.session_state.active_tab = key
                    st.rerun()
                if active:
                    st.markdown("</div>", unsafe_allow_html=True)

        # ── Footer ─────────────────────────────────────────────────────────────
        st.markdown("""
        <div style="margin-top:auto;padding:1.5rem 1.2rem 1rem;
                    border-top:1px solid rgba(255,255,255,0.05);">
            <div style="font-size:0.68rem;color:rgba(255,255,255,0.22);text-align:center;">
                AskMNIT v1.0 · MNIT Jaipur<br>
                <span style="color:rgba(96,165,250,0.45);">Powered by Claude Sonnet AI</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD HOME
# ══════════════════════════════════════════════════════════════════════════════
def render_dashboard():
    now  = datetime.datetime.now()
    hour = now.hour
    greet = "Good Morning" if hour < 12 else "Good Afternoon" if hour < 17 else "Good Evening"
    fname = st.session_state.student_name.split()[0]

    st.markdown(f"""
    <div style="margin-bottom:1.8rem;">
        <div class="neon-title">{greet}, {fname}! 👋</div>
        <div class="neon-subtitle">
            {now.strftime('%A, %B %d, %Y')} &nbsp;·&nbsp; MNIT Jaipur
            &nbsp;·&nbsp; {st.session_state.student_semester}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Metric row ────────────────────────────────────────────────────────────
    att_pct, att_p, att_t = compute_overall_attendance()
    today_cls  = get_today_schedule()
    n_subjects = len(get_unique_subjects())

    c1, c2, c3, c4 = st.columns(4)
    for col, val, label, icon in [
        (c1, str(len(today_cls)),            "Today's Classes",    "📅"),
        (c2, f"{att_pct}%",                  "Overall Attendance", "✅"),
        (c3, str(n_subjects),                "Active Subjects",    "📚"),
        (c4, now.strftime("%I:%M %p"),        "Current Time",      "🕐"),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">{icon}</div>
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([3, 2], gap="large")

    # ── Today's schedule ──────────────────────────────────────────────────────
    with left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;">
            <div class="section-heading" style="margin:0;">📅 Today's Schedule</div>
            <span class="badge badge-blue">{now.strftime('%A')}</span>
        </div>""", unsafe_allow_html=True)

        if today_cls:
            for cls in today_cls:
                live     = is_class_now(cls["time"])
                lv_class = "live" if live else ""
                lv_badge = ('<span class="badge badge-green" style="margin-left:6px;'
                            'font-size:0.62rem;vertical-align:middle;">● LIVE</span>'
                            if live else "")
                code_tag = (f'<span style="color:rgba(96,165,250,0.6);font-size:0.73rem;">'
                            f'{cls.get("code","")}</span>' if cls.get("code") else "")
                st.markdown(f"""
                <div class="timeline-item {lv_class}">
                    <div class="timeline-dot"></div>
                    <div class="timeline-time">{cls['time']}</div>
                    <div class="timeline-content">
                        <div class="timeline-subject">{cls['subject']} {lv_badge}</div>
                        <div class="timeline-venue">
                            📍 {cls.get('venue','TBA')} &nbsp; {code_tag}
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center;padding:2.5rem 1rem;color:rgba(255,255,255,0.3);">
                <div style="font-size:2.5rem;margin-bottom:0.6rem;">🎉</div>
                <div style="font-size:0.95rem;font-weight:600;color:rgba(255,255,255,0.5);">
                    No classes today!
                </div>
                <div style="font-size:0.8rem;margin-top:0.3rem;">Enjoy your free day.</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        # ── Campus Bulletin ───────────────────────────────────────────────────
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-heading">🎪 Campus Bulletin</div>', unsafe_allow_html=True)
        for evt in CAMPUS_EVENTS[:4]:
            tc = TAG_COLORS.get(evt["tag"], "badge-blue")
            st.markdown(f"""
            <div class="event-card">
                <div>
                    <div class="event-date">{evt['date']}</div>
                    <span class="badge {tc}" style="margin-top:5px;display:inline-block;">
                        {evt['tag']}
                    </span>
                </div>
                <div>
                    <div class="event-title">{evt['title']}</div>
                    <div class="event-desc">{evt['desc']}</div>
                </div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Attendance ring ───────────────────────────────────────────────────
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;padding:1.2rem;">
            <div class="section-heading" style="margin-bottom:0.8rem;">📊 Attendance</div>
            {circular_svg(att_pct)}
            <div style="color:rgba(255,255,255,0.38);font-size:0.75rem;margin-top:0.4rem;">
                {att_p} present / {att_t} total
            </div>
            {'<div style="color:#34D399;font-size:0.77rem;margin-top:4px;font-weight:600;">✓ Eligible for exams</div>' if att_pct >= 75 and att_t > 0 else '<div style="color:#F87171;font-size:0.77rem;margin-top:4px;font-weight:600;">⚠ Below 75% threshold</div>' if att_t > 0 else ""}
        </div>""", unsafe_allow_html=True)

    # ── Quick action bar ──────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">⚡ Quick Actions</div>', unsafe_allow_html=True)
    qa1, qa2, qa3, qa4, qa5 = st.columns(5)
    quick = [
        (qa1, "AI Assistant",  "AI Chat"),
        (qa2, "Attendance",    "Attendance"),
        (qa3, "GPA Calc",      "GPA Calc"),
        (qa4, "ERP Portal",    "ERP Portal"),
        (qa5, "Upload Schedule","Profile"),
    ]
    for col, label, tab in quick:
        with col:
            if st.button(label, key=f"qa_{tab}", use_container_width=True):
                st.session_state.active_tab = tab
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AI ASSISTANT CHAT
# ══════════════════════════════════════════════════════════════════════════════
QUICK_PROMPTS = [
    ("📋", "What's the minimum attendance rule at MNIT?"),
    ("🏆", "Tell me about upcoming campus fests"),
    ("💼", "Top tips for placement preparation at MNIT"),
    ("📚", "Make me a 2-week study plan for DSA exam"),
    ("🏠", "How to apply for hostel room change?"),
    ("🔑", "How do I reset my ERP portal password?"),
]

def render_chat():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <div class="neon-title">🤖 AskMNIT Assistant</div>
        <div class="neon-subtitle">Your AI-powered campus companion — powered by Claude</div>
    </div>""", unsafe_allow_html=True)

    # ── Header card ───────────────────────────────────────────────────────────
    st.markdown("""
    <div class="chat-header">
        <div class="chat-avatar">🎓</div>
        <div>
            <div class="ai-name">AskMNIT AI</div>
            <div class="ai-status">
                <span class="status-dot"></span> Online &nbsp;·&nbsp; Ready to help
            </div>
        </div>
        <div style="margin-left:auto;display:flex;gap:0.5rem;align-items:center;">
            <span class="badge badge-blue">Claude Sonnet</span>
            <span class="badge badge-purple">MNIT Context</span>
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Quick prompts ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style="margin:0.4rem 0 0.6rem;color:rgba(255,255,255,0.3);
                font-size:0.68rem;text-transform:uppercase;letter-spacing:1.2px;">
        Quick Questions
    </div>""", unsafe_allow_html=True)

    cols = st.columns(3)
    for i, (icon, prompt) in enumerate(QUICK_PROMPTS):
        short = prompt[:38] + "…" if len(prompt) > 38 else prompt
        with cols[i % 3]:
            if st.button(f"{icon} {short}", key=f"qp_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.spinner("AskMNIT is thinking…"):
                    resp = get_ai_response(prompt)
                st.session_state.messages.append({"role": "assistant", "content": resp})
                st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Chat history ──────────────────────────────────────────────────────────
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align:center;padding:3.5rem 1rem;color:rgba(255,255,255,0.25);">
            <div style="font-size:3rem;margin-bottom:0.8rem;">💬</div>
            <div style="font-size:1rem;font-weight:600;color:rgba(255,255,255,0.45);">
                Ask me anything about MNIT!
            </div>
            <div style="font-size:0.82rem;margin-top:0.4rem;">
                Academics · Campus Life · Admin Help · Study Tips · Career Guidance
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            avatar = "🎓" if msg["role"] == "assistant" else "👤"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

    # ── Input ─────────────────────────────────────────────────────────────────
    if prompt := st.chat_input("Ask AskMNIT anything… (e.g. 'How to apply for leave?')"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        with st.chat_message("assistant", avatar="🎓"):
            with st.spinner(""):
                response = get_ai_response(prompt)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    # ── Clear ─────────────────────────────────────────────────────────────────
    if st.session_state.messages:
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state.messages = []
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ERP PORTAL
# ══════════════════════════════════════════════════════════════════════════════
def render_erp():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <div class="neon-title">🎓 ERP Portal</div>
        <div class="neon-subtitle">Quick access to all MNIT digital services & important dates</div>
    </div>""", unsafe_allow_html=True)

    # ── Links grid ────────────────────────────────────────────────────────────
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">🔗 Official MNIT Links</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    for i, lnk in enumerate(ERP_LINKS):
        with (c1 if i % 2 == 0 else c2):
            st.markdown(f"""
            <a href="{lnk['url']}" target="_blank" style="text-decoration:none;">
            <div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.07);
                        border-radius:16px;padding:1.1rem 1.2rem;margin-bottom:0.85rem;
                        cursor:pointer;transition:all 0.25s;"
                 onmouseover="this.style.borderColor='rgba(96,165,250,0.35)';
                              this.style.background='rgba(96,165,250,0.06)';
                              this.style.transform='translateY(-1px)'"
                 onmouseout="this.style.borderColor='rgba(255,255,255,0.07)';
                             this.style.background='rgba(255,255,255,0.025)';
                             this.style.transform='translateY(0)'">
                <div style="font-size:1.4rem;margin-bottom:0.5rem;">{lnk['icon']}</div>
                <div style="font-weight:600;color:white;font-size:0.88rem;">{lnk['name']}</div>
                <div style="color:rgba(255,255,255,0.42);font-size:0.76rem;margin-top:3px;">
                    {lnk['desc']}
                </div>
                <div style="color:#60A5FA;font-size:0.7rem;margin-top:7px;">
                    {lnk['url']} ↗
                </div>
            </div></a>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Important dates ───────────────────────────────────────────────────────
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">📅 Academic Calendar 2024–25 (Even Semester)</div>', unsafe_allow_html=True)
    for date, event, badge in IMPORTANT_DATES:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:1rem;padding:0.65rem 0;
                    border-bottom:1px solid rgba(255,255,255,0.04);">
            <div style="min-width:130px;font-size:0.79rem;font-weight:600;
                        color:rgba(255,255,255,0.55);">{date}</div>
            <div style="color:white;font-size:0.84rem;flex:1;">{event}</div>
            <span class="badge {badge}">{badge.replace('badge-','').title()}</span>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ACADEMICS & NOTES
# ══════════════════════════════════════════════════════════════════════════════
def render_academics():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <div class="neon-title">📚 Academics & Notes</div>
        <div class="neon-subtitle">Resources, timetable, and subject-wise study tools</div>
    </div>""", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["📖 Subject Resources", "📋 Full Timetable", "📆 Weekly View"])

    with t1:
        subjects = list(get_unique_subjects().keys())
        if not subjects:
            subjects = ["Data Structures", "Computer Networks", "Operating Systems",
                        "Theory of Computation", "DBMS", "Software Engineering"]
        icons = ["📘","📗","📙","📕","📓","📔","📒","📃"]
        c1, c2, c3 = st.columns(3)
        for i, subj in enumerate(subjects[:9]):
            with [c1, c2, c3][i % 3]:
                st.markdown(f"""
                <div class="glass-card" style="text-align:center;cursor:pointer;min-height:140px;">
                    <div style="font-size:1.9rem;margin-bottom:0.5rem;">{icons[i%len(icons)]}</div>
                    <div style="font-weight:600;color:white;font-size:0.85rem;margin-bottom:0.7rem;">
                        {subj}
                    </div>
                    <div style="display:flex;gap:4px;justify-content:center;flex-wrap:wrap;">
                        <span class="badge badge-blue">Notes</span>
                        <span class="badge badge-purple">Slides</span>
                        <span class="badge badge-green">PYQs</span>
                    </div>
                </div>""", unsafe_allow_html=True)

    with t2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-heading">Complete Weekly Timetable</div>', unsafe_allow_html=True)
        sched = get_active_schedule()
        df = pd.DataFrame(sched)[["day","time","subject","venue","code"]].copy()
        df.columns = ["Day","Time","Subject","Venue","Code"]
        day_order = {"Monday":0,"Tuesday":1,"Wednesday":2,"Thursday":3,"Friday":4,"Saturday":5}
        df["_ord"] = df["Day"].map(lambda d: day_order.get(d, 9))
        df = df.sort_values(["_ord","Time"]).drop(columns="_ord")
        st.dataframe(df, use_container_width=True, hide_index=True, height=420)
        st.markdown("</div>", unsafe_allow_html=True)

    with t3:
        sched = get_active_schedule()
        days  = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
        for day in days:
            day_cls = [s for s in sched if s.get("day","").lower() == day.lower()]
            if not day_cls:
                continue
            st.markdown(f"""
            <div style="font-weight:700;color:#60A5FA;font-size:0.78rem;
                        text-transform:uppercase;letter-spacing:1.2px;
                        margin:1.1rem 0 0.5rem;">
                {day}
            </div>""", unsafe_allow_html=True)
            for cls in day_cls:
                live     = is_class_now(cls["time"]) and day == datetime.datetime.now().strftime("%A")
                lv_class = "live" if live else ""
                st.markdown(f"""
                <div class="timeline-item {lv_class}">
                    <div class="timeline-dot"></div>
                    <div class="timeline-time" style="min-width:110px;">{cls['time']}</div>
                    <div class="timeline-content">
                        <div class="timeline-subject">{cls['subject']}</div>
                        <div class="timeline-venue">📍 {cls.get('venue','TBA')}</div>
                    </div>
                </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PYQs
# ══════════════════════════════════════════════════════════════════════════════
def render_pyqs():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <div class="neon-title">📝 Previous Year Questions</div>
        <div class="neon-subtitle">Browse and download PYQs sorted by branch, subject, and exam type</div>
    </div>""", unsafe_allow_html=True)

    branch   = st.selectbox("Select Branch", list(PYQ_DATA.keys()), key="pyq_br")
    subjects = PYQ_DATA.get(branch, {})

    st.markdown("<br>", unsafe_allow_html=True)
    for subj, files in subjects.items():
        st.markdown(f"""
        <div class="glass-card">
            <div style="display:flex;align-items:center;justify-content:space-between;
                        margin-bottom:0.9rem;">
                <div style="font-weight:600;color:white;font-size:0.9rem;">📘 {subj}</div>
                <span class="badge badge-blue">{len(files)} papers</span>
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:0.45rem;">""",
        unsafe_allow_html=True)
        for f in files:
            year, etype = f.split()
            bc = "badge-purple" if etype == "MTE" else "badge-orange"
            st.markdown(f"""
                <div class="badge {bc}" style="padding:0.38rem 0.85rem;cursor:pointer;
                     font-size:0.73rem;">📄 {year} {etype}</div>""",
            unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card" style="border-color:rgba(79,158,255,0.2);">
        <div style="color:rgba(255,255,255,0.45);font-size:0.81rem;">
            💡 <strong style="color:rgba(255,255,255,0.7);">Pro Tip:</strong>
            Link each badge to your institution's Drive folder or SharePoint to enable
            direct PDF downloads. Replace file name strings with actual URLs.
        </div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ATTENDANCE TRACKER
# ══════════════════════════════════════════════════════════════════════════════
def render_attendance():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <div class="neon-title">📅 Attendance Tracker</div>
        <div class="neon-subtitle">Track per-subject attendance · Minimum 75% mandatory</div>
    </div>""", unsafe_allow_html=True)

    # Ensure all subjects are initialised
    for subj in get_unique_subjects():
        if subj not in st.session_state.attendance:
            st.session_state.attendance[subj] = {"present": 0, "total": 0}

    att_pct, att_p, att_t = compute_overall_attendance()

    # ── Top row ───────────────────────────────────────────────────────────────
    r1, r2 = st.columns([1, 3], gap="large")
    with r1:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;padding:1.6rem 1rem;">
            {circular_svg(att_pct, 180)}
            <div style="margin-top:0.7rem;color:rgba(255,255,255,0.38);font-size:0.76rem;">
                {att_p} attended · {att_t} held
            </div>
            {'<div style="color:#34D399;font-size:0.8rem;font-weight:600;margin-top:6px;">✓ Safe Zone</div>' if att_pct >= 75 else '<div style="color:#F87171;font-size:0.8rem;font-weight:600;margin-top:6px;">⚠ Danger Zone</div>' if att_t > 0 else '<div style="color:rgba(255,255,255,0.28);font-size:0.78rem;margin-top:6px;">No records yet</div>'}
        </div>""", unsafe_allow_html=True)

        # Classes needed to reach 75%
        if 0 < att_pct < 75 and att_t > 0:
            needed = math.ceil((0.75 * att_t - att_p) / 0.25)
            st.markdown(f"""
            <div style="background:rgba(248,113,113,0.07);border:1px solid rgba(248,113,113,0.2);
                        border-radius:12px;padding:0.7rem;text-align:center;
                        font-size:0.78rem;color:#F87171;margin-top:-0.5rem;">
                Attend next <strong>{needed}</strong> classes to reach 75%
            </div>""", unsafe_allow_html=True)

    with r2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-heading">Subject-wise Attendance</div>', unsafe_allow_html=True)

        subjects = get_unique_subjects()
        if subjects:
            hdr = st.columns([3, 1, 1, 1, 1])
            for h, c in zip(["Subject","Att%","Present/Total","Mark Present","Mark Absent"], hdr):
                with c:
                    st.markdown(f"<div style='font-size:0.68rem;color:rgba(255,255,255,0.3);"
                                f"text-transform:uppercase;letter-spacing:0.8px;padding:0.2rem 0;'>"
                                f"{h}</div>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:0.4rem 0 0.6rem;'>", unsafe_allow_html=True)

            for subj in subjects:
                a    = st.session_state.attendance.get(subj, {"present":0,"total":0})
                pct  = round(a["present"]/a["total"]*100, 1) if a["total"] else 0.0
                clr  = "#34D399" if pct >= 75 else ("#FBBF24" if pct >= 60 else "#F87171")

                s1, s2, s3, s4, s5 = st.columns([3, 1, 1, 1, 1])
                with s1:
                    short_subj = subj[:26]+"…" if len(subj) > 26 else subj
                    st.markdown(f"""
                    <div style="padding:0.35rem 0;">
                        <div style="color:white;font-weight:500;font-size:0.84rem;">{short_subj}</div>
                        <div class="att-bar-bg">
                            <div class="att-bar-fill"
                                 style="width:{pct}%;background:{clr};"></div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                with s2:
                    st.markdown(f"<div style='color:{clr};font-weight:700;font-size:0.88rem;"
                                f"padding-top:0.4rem;text-align:center;'>{pct}%</div>",
                                unsafe_allow_html=True)
                with s3:
                    st.markdown(f"<div style='color:rgba(255,255,255,0.4);font-size:0.8rem;"
                                f"padding-top:0.45rem;text-align:center;'>"
                                f"{a['present']}/{a['total']}</div>", unsafe_allow_html=True)
                with s4:
                    if st.button("✅", key=f"p_{subj}", use_container_width=True,
                                 help="Mark Present"):
                        st.session_state.attendance[subj]["present"] += 1
                        st.session_state.attendance[subj]["total"]   += 1
                        st.rerun()
                with s5:
                    if st.button("❌", key=f"a_{subj}", use_container_width=True,
                                 help="Mark Absent"):
                        st.session_state.attendance[subj]["total"] += 1
                        st.rerun()
        else:
            st.markdown("""
            <div style="text-align:center;color:rgba(255,255,255,0.3);padding:2rem;">
                No subjects yet. Upload your timetable in the Profile section.
            </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    if att_t > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        rc1, rc2, _ = st.columns([1, 1, 3])
        with rc1:
            if st.button("🔄 Reset All Attendance", key="rst_att"):
                st.session_state.attendance = {}
                st.rerun()
        with rc2:
            if st.button("📊 Export Summary", key="exp_att"):
                rows = []
                for subj, a in st.session_state.attendance.items():
                    pct = round(a["present"]/a["total"]*100,1) if a["total"] else 0.0
                    rows.append({"Subject": subj, "Present": a["present"],
                                 "Total":   a["total"], "Attendance%": pct})
                if rows:
                    df = pd.DataFrame(rows)
                    csv = df.to_csv(index=False)
                    st.download_button("⬇️ Download CSV", data=csv,
                                       file_name="attendance.csv", mime="text/csv")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: GPA CALCULATOR
# ══════════════════════════════════════════════════════════════════════════════
def render_gpa():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <div class="neon-title">🧮 GPA Calculator</div>
        <div class="neon-subtitle">SGPA & CGPA on MNIT's 10-point grading scale</div>
    </div>""", unsafe_allow_html=True)

    t1, t2 = st.tabs(["📊 SGPA — This Semester", "🎯 CGPA — Cumulative"])

    with t1:
        st.markdown("""
        <div style="background:rgba(79,158,255,0.05);border:1px solid rgba(79,158,255,0.15);
                    border-radius:14px;padding:0.7rem 1rem;margin-bottom:1rem;font-size:0.79rem;
                    color:rgba(255,255,255,0.5);">
            Scale: <strong style="color:#60A5FA;">O/A+</strong>=10 &nbsp;
            <strong style="color:#60A5FA;">A</strong>=9 &nbsp;
            <strong style="color:#60A5FA;">B+</strong>=8 &nbsp;
            <strong style="color:#60A5FA;">B</strong>=7 &nbsp;
            <strong style="color:#60A5FA;">C+</strong>=6 &nbsp;
            <strong style="color:#60A5FA;">C</strong>=5 &nbsp;
            <strong style="color:#60A5FA;">D</strong>=4 &nbsp;
            <strong style="color:#F87171;">F</strong>=0
        </div>""", unsafe_allow_html=True)

        n = st.number_input("Number of courses", 1, 12,
                            value=len(st.session_state.gpa_courses), key="n_crs")
        courses = st.session_state.gpa_courses
        while len(courses) < n:
            courses.append({"name": f"Course {len(courses)+1}", "credits": 4, "grade": "A"})
        while len(courses) > n:
            courses.pop()
        st.session_state.gpa_courses = courses

        grade_opts = list(GRADE_POINTS.keys())
        col_h = st.columns([3,1,1,1])
        for h, c in zip(["Course Name","Credits","Grade","Grade Points"], col_h):
            with c:
                st.markdown(f"<div style='font-size:0.7rem;color:rgba(255,255,255,0.35);"
                            f"text-transform:uppercase;letter-spacing:0.8px;padding:0.3rem 0;'>"
                            f"{h}</div>", unsafe_allow_html=True)
        st.markdown("<hr style='margin:0.2rem 0 0.5rem;'>", unsafe_allow_html=True)

        for i, crs in enumerate(courses):
            c1, c2, c3, c4 = st.columns([3,1,1,1])
            with c1:
                courses[i]["name"] = st.text_input(
                    "", value=crs["name"], key=f"cn{i}", label_visibility="collapsed")
            with c2:
                courses[i]["credits"] = st.number_input(
                    "", 1, 6, int(crs["credits"]), key=f"cr{i}", label_visibility="collapsed")
            with c3:
                idx = grade_opts.index(crs["grade"]) if crs["grade"] in grade_opts else 2
                courses[i]["grade"] = st.selectbox(
                    "", grade_opts, index=idx, key=f"gr{i}", label_visibility="collapsed")
            with c4:
                gp  = GRADE_POINTS.get(courses[i]["grade"], 0)
                clr = "#34D399" if gp >= 8 else ("#FBBF24" if gp >= 6 else "#F87171")
                st.markdown(f"<div style='color:{clr};font-weight:700;font-size:0.95rem;"
                            f"padding-top:0.5rem;text-align:center;'>{gp}</div>",
                            unsafe_allow_html=True)

        st.session_state.gpa_courses = courses
        sgpa, tot_cr = calculate_sgpa(courses)
        clr = "#34D399" if sgpa >= 8 else ("#FBBF24" if sgpa >= 6 else "#F87171")

        st.markdown(f"""
        <div style="background:rgba(59,130,246,0.07);border:1px solid rgba(59,130,246,0.22);
                    border-radius:18px;padding:1.6rem;text-align:center;margin-top:1.2rem;">
            <div style="font-size:0.72rem;color:rgba(255,255,255,0.4);text-transform:uppercase;
                        letter-spacing:1.2px;margin-bottom:0.4rem;">Calculated SGPA</div>
            <div style="font-family:'Syne',sans-serif;font-size:3.8rem;font-weight:800;
                        color:{clr};line-height:1;">{sgpa}</div>
            <div style="color:rgba(255,255,255,0.35);font-size:0.8rem;margin-top:0.4rem;">
                {tot_cr} total credits · Out of 10.00
            </div>
            {'<div style="color:#34D399;font-size:0.8rem;font-weight:600;margin-top:6px;">🏆 Excellent — First Division with Distinction</div>' if sgpa>=9 else '<div style="color:#60A5FA;font-size:0.8rem;margin-top:6px;">✓ First Division</div>' if sgpa>=7 else '<div style="color:#FBBF24;font-size:0.8rem;margin-top:6px;">Second Division</div>' if sgpa>=6 else ''}
        </div>""", unsafe_allow_html=True)

    with t2:
        st.markdown("""
        <div class="glass-card">
            <div class="section-heading">Enter SGPA for each completed semester</div>
        """, unsafe_allow_html=True)
        n_sem = st.number_input("Completed Semesters", 1, 8, 4, key="n_sem")
        sgpas, credits = [], []

        per_row = 4
        for batch_start in range(0, n_sem, per_row):
            batch = list(range(batch_start, min(batch_start + per_row, n_sem)))
            cols  = st.columns(len(batch))
            for j, i in enumerate(batch):
                with cols[j]:
                    s = st.number_input(f"Sem {i+1} SGPA",   0.0, 10.0, 8.0, 0.01, key=f"ss{i}")
                    c = st.number_input(f"Sem {i+1} Credits", 1,   30,   22,  key=f"sc{i}")
                    sgpas.append(s); credits.append(c)

        tot  = sum(credits)
        cgpa = round(sum(s*c for s,c in zip(sgpas,credits))/tot,2) if tot else 0.0
        clr  = "#34D399" if cgpa >= 8 else ("#FBBF24" if cgpa >= 6 else "#F87171")

        st.markdown(f"""
        </div>
        <div style="background:rgba(139,92,246,0.07);border:1px solid rgba(139,92,246,0.22);
                    border-radius:18px;padding:1.6rem;text-align:center;margin-top:0.5rem;">
            <div style="font-size:0.72rem;color:rgba(255,255,255,0.4);text-transform:uppercase;
                        letter-spacing:1.2px;margin-bottom:0.4rem;">Cumulative CGPA</div>
            <div style="font-family:'Syne',sans-serif;font-size:3.8rem;font-weight:800;
                        color:{clr};line-height:1;">{cgpa}</div>
            <div style="color:rgba(255,255,255,0.35);font-size:0.8rem;margin-top:0.4rem;">
                Over {tot} credits across {n_sem} semester{'s' if n_sem>1 else ''}
            </div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: STUDENT PROFILE
# ══════════════════════════════════════════════════════════════════════════════
BRANCHES = [
    "Computer Science & Engineering",
    "Electronics & Communication Engineering",
    "Mechanical Engineering",
    "Electrical Engineering",
    "Civil Engineering",
    "Chemical Engineering",
    "Metallurgical & Materials Engineering",
    "Architecture",
]
SEMESTERS = ["1st","2nd","3rd","4th","5th","6th","7th","8th"]

def render_profile():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <div class="neon-title">⚙️ Student Profile</div>
        <div class="neon-subtitle">Manage your details and upload your timetable PDF</div>
    </div>""", unsafe_allow_html=True)

    left, right = st.columns([1,1], gap="large")

    # ── Profile form ──────────────────────────────────────────────────────────
    with left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-heading">👤 Personal Information</div>', unsafe_allow_html=True)

        name   = st.text_input("Full Name",       st.session_state.student_name,   key="p_name")
        branch = st.selectbox("Branch / Department", BRANCHES,
                              index=BRANCHES.index(st.session_state.student_branch)
                              if st.session_state.student_branch in BRANCHES else 0,
                              key="p_branch")
        c1, c2 = st.columns(2)
        with c1:
            cid = st.text_input("College ID", st.session_state.student_id, key="p_id")
        with c2:
            cur_sem = st.session_state.student_semester.split()[0]
            sem = st.selectbox("Semester", SEMESTERS,
                               index=SEMESTERS.index(cur_sem) if cur_sem in SEMESTERS else 5,
                               key="p_sem")

        if st.button("💾 Save Profile", key="save_prof", use_container_width=True):
            st.session_state.student_name     = name
            st.session_state.student_branch   = branch
            st.session_state.student_id       = cid
            st.session_state.student_semester = f"{sem} Semester"
            st.success("✅ Profile saved!")

        st.markdown("</div>", unsafe_allow_html=True)

        # ── App info card ──────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="glass-card" style="border-color:rgba(139,92,246,0.2);">
            <div class="section-heading">ℹ️ App Information</div>
            <div style="display:grid;gap:0.55rem;">
                {_info_row("Version",      "v1.0.0",        "badge-blue")}
                {_info_row("AI Engine",    "Claude Sonnet", "badge-purple")}
                {_info_row("Framework",    "Streamlit",     "badge-green")}
                {_info_row("PDF Parser",   PDF_LIB or "Not installed",
                           "badge-green" if PDF_LIB else "badge-orange")}
                {_info_row("Schedule",
                           f"{len(get_active_schedule())} entries loaded",
                           "badge-green" if st.session_state.pdf_parsed else "badge-blue")}
            </div>
        </div>""", unsafe_allow_html=True)

    # ── PDF upload ────────────────────────────────────────────────────────────
    with right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-heading">📄 Upload Weekly Schedule</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="color:rgba(255,255,255,0.38);font-size:0.79rem;margin-bottom:1rem;">
            Upload the timetable PDF from MNIT ERP. The app will auto-extract
            your class schedule. See customization notes below if parsing fails.
        </div>""", unsafe_allow_html=True)

        if PDF_LIB is None:
            st.warning("Install PDF library: `pip install pdfplumber`")

        uploaded = st.file_uploader("Drop your timetable PDF here", type=["pdf"],
                                    key="sched_pdf",
                                    help="Download from erp.mnit.ac.in → My Timetable")

        if uploaded:
            with st.spinner("🔍 Parsing your schedule…"):
                parsed = parse_pdf_schedule(uploaded)
            if parsed:
                st.session_state.schedule   = parsed
                st.session_state.pdf_parsed = True
                st.session_state.attendance = {}   # reset on new schedule
                st.success(f"✅ Parsed {len(parsed)} class entries successfully!")
                st.markdown("<div style='margin-top:0.8rem;font-size:0.78rem;"
                            "color:rgba(255,255,255,0.4);'>Preview (first 5):</div>",
                            unsafe_allow_html=True)
                for e in parsed[:5]:
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.03);border-radius:10px;
                                padding:0.45rem 0.9rem;margin-bottom:4px;font-size:0.79rem;">
                        <span style="color:#60A5FA;font-weight:600;">{e.get('day','')}</span>
                        <span style="color:rgba(255,255,255,0.3);margin:0 0.4rem;">|</span>
                        <span style="color:white;">{e.get('time','')}</span>
                        <span style="color:rgba(255,255,255,0.3);margin:0 0.4rem;">|</span>
                        <span style="color:white;">{e.get('subject','')}</span>
                        <span style="color:rgba(255,255,255,0.3);margin:0 0.3rem;">@</span>
                        <span style="color:#A78BFA;">{e.get('venue','')}</span>
                    </div>""", unsafe_allow_html=True)
        elif st.session_state.pdf_parsed:
            n = len(st.session_state.schedule)
            st.markdown(f"""
            <div style="background:rgba(52,211,153,0.07);border:1px solid rgba(52,211,153,0.2);
                        border-radius:12px;padding:0.75rem 1rem;font-size:0.8rem;color:#34D399;">
                ✅ Schedule active · {n} class entries loaded
            </div>""", unsafe_allow_html=True)

        # ── Customization hint ─────────────────────────────────────────────────
        st.markdown("""
        <div style="margin-top:1rem;padding:0.9rem 1rem;
                    background:rgba(79,158,255,0.05);
                    border:1px solid rgba(79,158,255,0.18);
                    border-radius:12px;font-size:0.76rem;color:rgba(255,255,255,0.45);">
            <strong style="color:rgba(255,255,255,0.65);">📌 Customization Guide</strong><br><br>
            The parser lives in <code>parse_pdf_schedule()</code> in <code>app.py</code>:<br><br>
            • <code>_parse_table_rows()</code> — adjust col indices for row-per-class tables<br>
            • <code>_parse_grid_table()</code> — for grid PDFs (days as columns)<br>
            • <code>_parse_text_schedule()</code> — tune the regex for plain-text PDFs<br><br>
            Each helper is fully commented with CUSTOMIZE markers.
        </div>""", unsafe_allow_html=True)

        if st.session_state.pdf_parsed:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Clear Schedule & Use Demo", key="clear_sched"):
                st.session_state.schedule   = []
                st.session_state.pdf_parsed = False
                st.session_state.attendance = {}
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


def _info_row(label, val, badge_cls):
    return (f"<div style='display:flex;justify-content:space-between;"
            f"align-items:center;font-size:0.81rem;padding:0.1rem 0;'>"
            f"<span style='color:rgba(255,255,255,0.45);'>{label}</span>"
            f"<span class='badge {badge_cls}'>{val}</span></div>")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ROUTER
# ══════════════════════════════════════════════════════════════════════════════
def main():
    init_session_state()
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    render_sidebar()

    tab = st.session_state.active_tab
    dispatch = {
        "Dashboard":  render_dashboard,
        "AI Chat":    render_chat,
        "ERP Portal": render_erp,
        "Academics":  render_academics,
        "PYQs":       render_pyqs,
        "Attendance": render_attendance,
        "GPA Calc":   render_gpa,
        "Profile":    render_profile,
    }
    dispatch.get(tab, render_dashboard)()


if __name__ == "__main__":
    main()
