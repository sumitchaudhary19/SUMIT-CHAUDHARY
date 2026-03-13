# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║         AskMNIT  —  Current Student Dashboard  (Session-State Driven)        ║
# ║                                                                              ║
# ║  Features:                                                                   ║
# ║   • Branch-aware subject database (Common + Branch subjects)                 ║
# ║   • Attendance tracker per subject with real-time percentage updates         ║
# ║   • PDF schedule analyzer (process_schedule_pdf placeholder)                 ║
# ║   • Digital Planner with live countdown to next class                        ║
# ║   • Edit Profile: Name, College ID, Semester, Branch (dropdown)              ║
# ║   • Sidebar navigation (7 sections)                                          ║
# ║   • Floating AskMNIT AI chatbot                                              ║
# ║   • Strict dark mode — no "Welcome" / "Professional Dashboard" text           ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import streamlit as st
import datetime
import random
import re

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be the very first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AskMNIT — Student Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═════════════════════════════════════════════════════════════════════════════
# GLOBAL DATA: BRANCH → SUBJECT DATABASE
# ═════════════════════════════════════════════════════════════════════════════
COMMON_SUBJECTS = [
    "Mathematics I/II",
    "Physics",
    "Chemistry",
    "Computer Programming",
    "Basic Electrical",
    "Basic Electronics",
    "Basic Mechanical",
    "Engineering Drawing",
    "Environmental Science",
    "Technical Communication",
    "Basic Economics",
]

BRANCH_SUBJECTS: dict[str, list[str]] = {
    "CSE":       ["Discrete Mathematics", "Problem Solving using C"],
    "AI & ML":   ["Mathematics for AI", "Data Structures and Algorithms"],
    "ECE":       ["Signals and Systems", "Electronic Devices and Circuits"],
    "Civil":     ["Mechanics of Solid", "Engineering Geology"],
    "Metallurgy":["Engineering Materials", "Mineral Processing"],
}

BRANCHES = ["CSE", "AI & ML", "ECE", "Civil", "Metallurgy"]

SEMESTERS = [f"Semester {i}" for i in range(1, 9)]

# ── Day-to-short mapping for schedule
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# ═════════════════════════════════════════════════════════════════════════════
# PDF SCHEDULE ANALYZER PLACEHOLDER
# ═════════════════════════════════════════════════════════════════════════════
def process_schedule_pdf(file, branch: str) -> dict:
    """
    Placeholder that simulates PDF extraction.

    In production, replace the internals with:
        import pdfplumber
        with pdfplumber.open(file) as pdf:
            text = "\\n".join(page.extract_text() for page in pdf.pages)
        # parse text into schedule dict

    Returns a dict:  { "Monday": [...slots...], "Tuesday": [...], ... }
    Each slot: { "time": "09:30", "subject": str, "room": str, "type": str }
    """
    branch_subj = BRANCH_SUBJECTS.get(branch, [])
    all_subj = COMMON_SUBJECTS[:4] + branch_subj  # pick subset for demo

    random.seed(42)  # deterministic demo output
    schedule: dict[str, list[dict]] = {}

    for day in DAYS[:6]:   # Mon-Sat
        slots = []
        times = ["08:00", "09:30", "11:00", "12:00", "14:00", "15:30"]
        chosen = random.sample(times, k=random.randint(2, 4))
        chosen.sort()
        for t in chosen:
            subj = random.choice(all_subj)
            room = random.choice(["LT-1", "LT-2", "Lab-A", "Lab-B", "CR-3", "CR-5"])
            stype = random.choice(["Lecture", "Lecture", "Lab", "Tutorial"])
            slots.append({"time": t, "subject": subj, "room": room, "type": stype})
        schedule[day] = slots

    return schedule


def get_today_schedule(full_schedule: dict) -> list[dict]:
    """Return today's slots from the full schedule dict."""
    today_name = datetime.datetime.now().strftime("%A")   # e.g. "Monday"
    return full_schedule.get(today_name, [])


def get_next_class(today_slots: list[dict]) -> dict | None:
    """Return the next upcoming class slot, or None if all are done."""
    now = datetime.datetime.now()
    for slot in today_slots:
        h, m = map(int, slot["time"].split(":"))
        class_dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if class_dt > now:
            diff = class_dt - now
            minutes = int(diff.total_seconds() // 60)
            return {**slot, "minutes_away": minutes, "class_dt": class_dt}
    return None


# ═════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════════════════════════════════
def get_subjects_for_branch(branch: str) -> list[str]:
    return COMMON_SUBJECTS + BRANCH_SUBJECTS.get(branch, [])


def build_attendance_for_subjects(subjects: list[str]) -> dict[str, dict]:
    """Create fresh attendance record for each subject."""
    return {s: {"present": 0, "total": 0} for s in subjects}


def att_pct(rec: dict) -> float:
    return round(rec["present"] / rec["total"] * 100, 1) if rec["total"] > 0 else 0.0


def overall_pct(att: dict) -> float:
    tp = sum(r["present"] for r in att.values())
    tt = sum(r["total"]   for r in att.values())
    return round(tp / tt * 100, 1) if tt > 0 else 0.0


def status_info(pct: float) -> tuple[str, str, str]:
    """(label, text_color, bg_rgba)"""
    if pct >= 75:
        return "Safe ✅",     "#10B981", "rgba(16,185,129,0.12)"
    elif pct >= 65:
        return "Low ⚠️",     "#F59E0B", "rgba(245,158,11,0.12)"
    else:
        return "Critical 🔴", "#EF4444", "rgba(239,68,68,0.12)"


def subj_color(pct: float) -> str:
    return "#10B981" if pct >= 75 else "#F59E0B" if pct >= 65 else "#EF4444"


def initials(name: str) -> str:
    return "".join(w[0].upper() for w in name.split()[:2]) if name else "??"


# ═════════════════════════════════════════════════════════════════════════════
# SESSION STATE — initialise all keys once
# ═════════════════════════════════════════════════════════════════════════════
_default_branch    = "CSE"
_default_subjects  = get_subjects_for_branch(_default_branch)

_DEFAULTS: dict = {
    # Navigation
    "nav_page":         "My Dashboard",

    # Profile
    "student_name":     "Sumit Chaudhary",
    "college_id":       "2022UMT1234",
    "semester":         "Semester 6",
    "branch":           _default_branch,
    "editing_profile":  False,

    # Attendance (keyed by subject name)
    "attendance":       build_attendance_for_subjects(_default_subjects),

    # PDF schedule
    "schedule_loaded":  False,
    "full_schedule":    {},
    "pdf_filename":     "",

    # Planner (manual overrides for today)
    "planner_overrides": {},   # { "HH:MM": "custom note" }
    "planner_input_time": "09:30",
    "planner_input_note": "",

    # Notes
    "notes_text": "• Mid-sem revision starts Monday\n• Submit fee by 17 Mar\n• Collect hall ticket from ERP",

    # Quick links feedback
    "ql_feedback": "",

    # AI chatbot
    "show_ai":      False,
    "ai_messages":  [],
    "ai_pending":   False,
}

for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ═════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS  — Terminal-dark aesthetic
# Fonts: Syne Mono (display/headers) + Outfit (body)
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne+Mono&family=Outfit:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg:       #050A13;
    --surface:  #0A1220;
    --surface2: #0F1A2E;
    --border:   rgba(255,255,255,0.07);
    --border2:  rgba(255,255,255,0.13);
    --accent:   #3B82F6;
    --accent2:  #6366F1;
    --cyan:     #22D3EE;
    --green:    #10B981;
    --amber:    #F59E0B;
    --red:      #EF4444;
    --text:     #E2E8F0;
    --muted:    rgba(148,163,184,0.55);
    --mono:     'Syne Mono', monospace;
    --sans:     'Outfit', sans-serif;
}

*,html,body { box-sizing:border-box; margin:0; padding:0; }

html,body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"] {
    font-family: var(--sans) !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}

/* ── Chrome removal ── */
header[data-testid="stHeader"],
footer, #MainMenu,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display:none !important; }

/* ── Main padding ── */
[data-testid="stMainBlockContainer"] {
    padding: 0 24px 100px 24px !important;
    max-width: 100% !important;
}

/* ─────────────────────────────────────
   SIDEBAR
───────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid rgba(59,130,246,0.18) !important;
    min-width: 216px !important;
    max-width: 216px !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }

/* ─────────────────────────────────────
   TEXT INPUTS & TEXTAREAS
───────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
    font-size: 0.87rem !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(59,130,246,0.55) !important;
    box-shadow: 0 0 0 2.5px rgba(59,130,246,0.14) !important;
    outline: none !important;
}
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label {
    color: var(--muted) !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.6px !important;
    font-family: var(--sans) !important;
}

/* ─────────────────────────────────────
   SELECTBOX
───────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
}
[data-testid="stSelectbox"] label {
    color: var(--muted) !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.6px !important;
    font-family: var(--sans) !important;
}

/* ─────────────────────────────────────
   FILE UPLOADER
───────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: rgba(59,130,246,0.04) !important;
    border: 1px dashed rgba(59,130,246,0.28) !important;
    border-radius: 12px !important;
    padding: 8px !important;
}
[data-testid="stFileUploader"] label {
    color: var(--muted) !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    font-family: var(--sans) !important;
}

/* ─────────────────────────────────────
   BUTTONS — base
───────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg,#2563EB,#4F46E5) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 9px !important;
    font-family: var(--sans) !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 9px 16px !important;
    box-shadow: 0 3px 14px rgba(37,99,235,0.22) !important;
    transition: all 0.16s ease !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 5px 20px rgba(37,99,235,0.30) !important;
}
.stButton > button:active { transform: scale(0.97) !important; }

/* ── Nav buttons ── */
.nav-btn .stButton > button {
    background: transparent !important;
    color: rgba(148,163,184,0.65) !important;
    border: none !important;
    box-shadow: none !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 10px 14px !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
}
.nav-btn .stButton > button:hover {
    background: rgba(59,130,246,0.10) !important;
    color: #BAE6FD !important;
    transform: none !important;
}
.nav-btn-active .stButton > button {
    background: rgba(59,130,246,0.14) !important;
    color: #60A5FA !important;
    border-left: 2px solid #3B82F6 !important;
    font-weight: 700 !important;
    box-shadow: none !important;
}
.nav-btn-active .stButton > button:hover {
    transform: none !important;
    background: rgba(59,130,246,0.20) !important;
}

/* ── Ghost ── */
.ghost-btn .stButton > button {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid var(--border2) !important;
    color: rgba(226,232,240,0.55) !important;
    box-shadow: none !important;
}
.ghost-btn .stButton > button:hover {
    background: rgba(59,130,246,0.10) !important;
    color: var(--text) !important;
}

/* ── Present (green) ── */
.present-btn .stButton > button {
    background: linear-gradient(135deg,#065F46,#10B981) !important;
    box-shadow: 0 2px 10px rgba(16,185,129,0.20) !important;
    padding: 6px 12px !important;
    font-size: 0.76rem !important;
    border-radius: 7px !important;
}

/* ── Absent (red) ── */
.absent-btn .stButton > button {
    background: linear-gradient(135deg,#7F1D1D,#EF4444) !important;
    box-shadow: 0 2px 10px rgba(239,68,68,0.18) !important;
    padding: 6px 12px !important;
    font-size: 0.76rem !important;
    border-radius: 7px !important;
}

/* ── Save (amber) ── */
.save-btn .stButton > button {
    background: linear-gradient(135deg,#92400E,#F59E0B) !important;
    box-shadow: 0 2px 10px rgba(245,158,11,0.20) !important;
    padding: 7px 13px !important;
    font-size: 0.78rem !important;
}

/* ── Edit (subtle) ── */
.edit-btn .stButton > button {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid var(--border2) !important;
    color: rgba(148,163,184,0.65) !important;
    box-shadow: none !important;
    font-size: 0.72rem !important;
    padding: 4px 10px !important;
}
.edit-btn .stButton > button:hover {
    color: #BAE6FD !important;
    background: rgba(59,130,246,0.10) !important;
}

/* ── Quick links ── */
.ql-btn .stButton > button {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid var(--border2) !important;
    color: rgba(186,230,253,0.65) !important;
    box-shadow: none !important;
    text-align: left !important;
    justify-content: flex-start !important;
    font-size: 0.80rem !important;
    padding: 9px 14px !important;
    border-radius: 9px !important;
}
.ql-btn .stButton > button:hover {
    background: rgba(59,130,246,0.10) !important;
    border-color: rgba(59,130,246,0.30) !important;
    color: #BAE6FD !important;
    transform: none !important;
}

/* ── Logout ── */
.logout-btn .stButton > button {
    background: rgba(239,68,68,0.09) !important;
    border: 1px solid rgba(239,68,68,0.20) !important;
    color: #FCA5A5 !important;
    box-shadow: none !important;
    font-size: 0.80rem !important;
}
.logout-btn .stButton > button:hover {
    background: rgba(239,68,68,0.18) !important;
}

/* ── Floating AI ── */
.floating-ai-btn .stButton > button {
    background: linear-gradient(135deg,#059669,#10B981) !important;
    border-radius: 999px !important;
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    padding: 13px 26px !important;
    box-shadow: 0 6px 30px rgba(16,185,129,0.42) !important;
    font-family: var(--mono) !important;
    letter-spacing: 0.3px !important;
}
.floating-ai-btn .stButton > button:hover {
    box-shadow: 0 8px 40px rgba(16,185,129,0.58) !important;
    transform: translateY(-2px) scale(1.02) !important;
}

/* ─────────────────────────────────────
   PROGRESS BAR
───────────────────────────────────── */
[data-testid="stProgress"] > div > div {
    border-radius: 99px !important;
    background: linear-gradient(90deg,#2563EB,#22D3EE) !important;
}
[data-testid="stProgress"] > div {
    background: rgba(255,255,255,0.07) !important;
    border-radius: 99px !important;
    height: 6px !important;
}

/* ─────────────────────────────────────
   CHAT
───────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.025) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    font-family: var(--sans) !important;
}
[data-testid="stChatInput"] > div {
    background: rgba(10,18,32,0.98) !important;
    border: 1px solid rgba(59,130,246,0.28) !important;
    border-radius: 14px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
}
[data-testid="stChatInput"] button[data-testid="stChatInputSubmitButton"] {
    background: linear-gradient(135deg,#2563EB,#4F46E5) !important;
    border-radius: 8px !important;
}

/* ─────────────────────────────────────
   EXPANDER
───────────────────────────────────── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.018) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}
summary {
    font-family: var(--sans) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    color: var(--text) !important;
}

/* ─────────────────────────────────────
   MISC
───────────────────────────────────── */
h1,h2,h3,h4 {
    font-family: var(--mono) !important;
    color: var(--text) !important;
    font-weight: 400 !important;
}
hr { border-color: var(--border) !important; }
[data-testid="stMarkdown"] p,
[data-testid="stMarkdown"] li {
    color: rgba(226,232,240,0.72) !important;
    font-family: var(--sans) !important;
}
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(59,130,246,0.24);
    border-radius: 4px;
}
[data-testid="column"] { padding: 0 5px !important; }

/* ── Scan-line texture overlay (decorative) ── */
[data-testid="stMainBlockContainer"]::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        0deg,
        rgba(0,0,0,0.03) 0px,
        rgba(0,0,0,0.03) 1px,
        transparent 1px,
        transparent 3px
    );
    pointer-events: none;
    z-index: 0;
}
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════════════════════
NAV_ITEMS = [
    ("⬡", "My Dashboard"),
    ("📅", "My Schedule"),
    ("📚", "Academics"),
    ("📝", "Study Material"),
    ("📂", "PYQs"),
    ("💰", "Fee Portal"),
    ("🍱", "Mess Menu"),
]

with st.sidebar:
    # ── Brand ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="padding:20px 16px 16px;border-bottom:1px solid rgba(59,130,246,0.14);">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:32px;height:32px;border-radius:8px;
                        background:linear-gradient(135deg,#2563EB,#4F46E5);
                        display:flex;align-items:center;justify-content:center;
                        font-size:1.0rem;box-shadow:0 4px 14px rgba(37,99,235,0.32);">
                &#127891;
            </div>
            <div>
                <div style="font-family:'Syne Mono',monospace;font-weight:400;
                            font-size:0.88rem;color:#E2E8F0;letter-spacing:0.2px;">
                    AskMNIT
                </div>
                <div style="font-size:0.58rem;color:rgba(148,163,184,0.48);margin-top:1px;">
                    Student Portal
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Branch chip
    branch_color = {"CSE":"#3B82F6","AI & ML":"#8B5CF6","ECE":"#06B6D4",
                    "Civil":"#F59E0B","Metallurgy":"#10B981"}.get(
                    st.session_state.branch, "#6366F1")
    st.markdown(
        '<div style="padding:8px 14px 4px;">'
        '<span style="font-size:0.62rem;font-weight:700;padding:3px 10px;'
        'background:rgba(255,255,255,0.05);border:1px solid ' + branch_color + '44;'
        'border-radius:6px;color:' + branch_color + ';letter-spacing:0.4px;">'
        + st.session_state.branch + '</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── Nav ────────────────────────────────────────────────────────────────
    for icon, label in NAV_ITEMS:
        is_active = st.session_state.nav_page == label
        css = "nav-btn-active" if is_active else "nav-btn"
        st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
        if st.button(f"{icon}  {label}", key="nav_" + label, use_container_width=True):
            st.session_state.nav_page = label
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Logout (pinned bottom) ─────────────────────────────────────────────
    st.markdown("""
    <div style="position:fixed;bottom:20px;width:184px;
                padding-top:12px;border-top:1px solid rgba(255,255,255,0.06);">
    """, unsafe_allow_html=True)
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("🚪  Logout", key="sidebar_logout", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# NON-DASHBOARD PLACEHOLDER PAGES
# ═════════════════════════════════════════════════════════════════════════════
page = st.session_state.nav_page

if page != "My Dashboard":
    PAGE_META = {
        "My Schedule":    ("📅","My Schedule",    "Your weekly timetable will render here."),
        "Academics":      ("📚","Academics",       "Grades, CGPA, and exam records appear here."),
        "Study Material": ("📝","Study Material",  "Uploaded notes and resources appear here."),
        "PYQs":           ("📂","PYQs",            "Previous year question papers appear here."),
        "Fee Portal":     ("💰","Fee Portal",      "Fee dues, payments, and receipts appear here."),
        "Mess Menu":      ("🍱","Mess Menu",       "Weekly mess menu from the hostel appears here."),
    }
    icon, title, desc = PAGE_META.get(page, ("📄", page, "Content coming soon."))

    st.markdown(
        '<div style="display:flex;align-items:center;gap:10px;'
        'padding:16px 0 12px;border-bottom:1px solid rgba(255,255,255,0.06);'
        'margin-bottom:28px;">'
        '<span style="font-size:1.3rem;">' + icon + '</span>'
        '<span style="font-family:\'Syne Mono\',monospace;font-size:1.0rem;'
        'color:#E2E8F0;">' + title.upper() + '</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="background:linear-gradient(160deg,#0A1220,#050A13);'
        'border:1px dashed rgba(59,130,246,0.18);border-radius:16px;'
        'padding:64px 40px;text-align:center;">'
        '<div style="font-size:2.8rem;margin-bottom:14px;opacity:0.30;">' + icon + '</div>'
        '<div style="font-family:\'Syne Mono\',monospace;font-size:0.92rem;'
        'color:#E2E8F0;margin-bottom:8px;">' + title.upper() + '</div>'
        '<div style="font-size:0.78rem;color:rgba(148,163,184,0.48);'
        'max-width:300px;margin:0 auto;line-height:1.65;">' + desc + '</div>'
        '<div style="margin-top:14px;font-size:0.62rem;color:rgba(59,130,246,0.40);">'
        '[ FUNCTIONALITY WIRED IN NEXT ITERATION ]</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.stop()


# ═════════════════════════════════════════════════════════════════════════════
# MAIN DASHBOARD
# ═════════════════════════════════════════════════════════════════════════════

# ── TOP HEADER BAR ────────────────────────────────────────────────────────────
h_left, h_mid, h_right = st.columns([2, 5, 2])

with h_left:
    st.markdown(
        '<div style="display:flex;align-items:center;gap:9px;padding:14px 0 10px;">'
        '<div style="width:34px;height:34px;border-radius:8px;'
        'background:linear-gradient(135deg,#2563EB,#4F46E5);'
        'display:flex;align-items:center;justify-content:center;'
        'font-size:0.95rem;font-weight:700;color:white;'
        'box-shadow:0 3px 12px rgba(37,99,235,0.28);">M</div>'
        '<div>'
        '<div style="font-family:\'Syne Mono\',monospace;font-size:0.80rem;'
        'color:#E2E8F0;letter-spacing:0.1px;">MNIT Jaipur</div>'
        '<div style="font-size:0.55rem;color:rgba(148,163,184,0.40);">[ MNIT LOGO ]</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

with h_mid:
    now_str = datetime.datetime.now().strftime("%a, %d %b %Y  •  %H:%M")
    st.markdown(
        '<div style="padding:14px 0 10px;text-align:center;">'
        '<span style="font-family:\'Syne Mono\',monospace;font-size:0.80rem;'
        'color:#60A5FA;letter-spacing:0.8px;">MY DASHBOARD</span>'
        '<br><span style="font-size:0.60rem;color:rgba(148,163,184,0.40);">'
        + now_str + '</span>'
        '</div>',
        unsafe_allow_html=True,
    )

with h_right:
    init = initials(st.session_state.student_name)
    st.markdown(
        '<div style="display:flex;align-items:center;justify-content:flex-end;'
        'gap:10px;padding:14px 0 10px;">'
        '<div title="Notifications" style="width:32px;height:32px;border-radius:8px;'
        'background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.09);'
        'display:flex;align-items:center;justify-content:center;font-size:0.95rem;'
        'cursor:pointer;position:relative;">'
        '&#128276;'
        '<span style="position:absolute;top:-3px;right:-3px;width:8px;height:8px;'
        'border-radius:50%;background:#EF4444;border:1.5px solid #050A13;"></span>'
        '</div>'
        '<div title="Profile" style="width:32px;height:32px;border-radius:8px;'
        'background:linear-gradient(135deg,#2563EB,#4F46E5);'
        'display:flex;align-items:center;justify-content:center;'
        'font-size:0.72rem;font-weight:700;color:white;'
        'font-family:\'Syne Mono\',monospace;'
        'box-shadow:0 2px 8px rgba(37,99,235,0.24);cursor:pointer;">'
        + init + '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div style="height:1px;background:linear-gradient(90deg,'
    'transparent,rgba(59,130,246,0.38),rgba(34,211,238,0.20),transparent);'
    'margin-bottom:18px;"></div>',
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# ROW 1 — PROFILE CARD  +  ATTENDANCE METER
# ══════════════════════════════════════════════════════════════════════════════
col_profile, col_att = st.columns([1, 1.85], gap="large")

# ─────────────────────────────────────────────────────────────────────
# PROFILE CARD
# ─────────────────────────────────────────────────────────────────────
with col_profile:
    st.markdown(
        '<div style="background:linear-gradient(160deg,#0A1220,#060E1C);'
        'border:1px solid rgba(59,130,246,0.22);border-radius:16px;'
        'padding:20px 20px 16px;">'
        '<div style="font-family:\'Syne Mono\',monospace;font-size:0.58rem;'
        'color:rgba(148,163,184,0.45);text-transform:uppercase;'
        'letter-spacing:1.4px;margin-bottom:14px;">// STUDENT PROFILE</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.editing_profile:
        # ── EDIT MODE ────────────────────────────────────────────────────
        new_name = st.text_input("Full Name", value=st.session_state.student_name,
                                  key="ep_name")
        new_cid  = st.text_input("College ID", value=st.session_state.college_id,
                                  key="ep_cid")
        new_sem  = st.selectbox("Semester", SEMESTERS,
                                 index=SEMESTERS.index(st.session_state.semester)
                                       if st.session_state.semester in SEMESTERS else 0,
                                 key="ep_sem")
        new_br   = st.selectbox("Branch", BRANCHES,
                                 index=BRANCHES.index(st.session_state.branch)
                                       if st.session_state.branch in BRANCHES else 0,
                                 key="ep_branch")

        # ── PDF SCHEDULE UPLOADER ─────────────────────────────────────────
        st.markdown(
            '<div style="margin-top:10px;margin-bottom:4px;'
            'font-size:0.60rem;color:rgba(148,163,184,0.50);'
            'text-transform:uppercase;letter-spacing:0.8px;font-weight:600;">'
            'Upload Weekly Schedule PDF</div>',
            unsafe_allow_html=True,
        )
        uploaded_pdf = st.file_uploader(
            label="",
            type=["pdf"],
            key="pdf_uploader",
            label_visibility="collapsed",
        )
        if uploaded_pdf is not None:
            with st.spinner("Analysing schedule PDF…"):
                extracted = process_schedule_pdf(uploaded_pdf, new_br)
            st.session_state.full_schedule  = extracted
            st.session_state.schedule_loaded = True
            st.session_state.pdf_filename    = uploaded_pdf.name
            st.success("Schedule extracted from: " + uploaded_pdf.name)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        sv1, sv2 = st.columns(2)
        with sv1:
            if st.button("💾 Save Profile", key="save_profile_btn", use_container_width=True):
                branch_changed = new_br != st.session_state.branch

                st.session_state.student_name = new_name
                st.session_state.college_id   = new_cid
                st.session_state.semester      = new_sem
                st.session_state.branch        = new_br

                if branch_changed:
                    # Rebuild attendance with new subject list
                    new_subjs = get_subjects_for_branch(new_br)
                    old_att   = st.session_state.attendance
                    new_att   = {}
                    for s in new_subjs:
                        # Preserve existing counts if subject carried over
                        new_att[s] = old_att.get(s, {"present": 0, "total": 0})
                    st.session_state.attendance = new_att

                st.session_state.editing_profile = False
                st.rerun()
        with sv2:
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("Cancel", key="cancel_profile_btn", use_container_width=True):
                st.session_state.editing_profile = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        # ── DISPLAY MODE ─────────────────────────────────────────────────
        init_str    = initials(st.session_state.student_name)
        b_color     = {"CSE":"#3B82F6","AI & ML":"#8B5CF6","ECE":"#06B6D4",
                       "Civil":"#F59E0B","Metallurgy":"#10B981"}.get(
                       st.session_state.branch, "#6366F1")

        st.markdown(
            '<div style="display:flex;align-items:center;gap:14px;margin-bottom:14px;">'
            '<div style="width:50px;height:50px;border-radius:13px;flex-shrink:0;'
            'background:linear-gradient(135deg,#2563EB,#4F46E5);'
            'display:flex;align-items:center;justify-content:center;'
            'font-family:\'Syne Mono\',monospace;font-size:1.05rem;color:white;'
            'box-shadow:0 4px 16px rgba(37,99,235,0.30);">'
            + init_str + '</div>'
            '<div style="min-width:0;flex:1;">'
            '<div style="font-weight:700;font-size:0.98rem;color:#E2E8F0;'
            'font-family:\'Outfit\',sans-serif;margin-bottom:3px;'
            'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'
            + st.session_state.student_name + '</div>'
            '<div style="font-family:\'Syne Mono\',monospace;font-size:0.66rem;'
            'color:rgba(148,163,184,0.55);margin-bottom:6px;">'
            + st.session_state.college_id + '</div>'
            '<div style="display:flex;gap:6px;flex-wrap:wrap;">'
            '<span style="font-size:0.62rem;padding:2px 9px;border-radius:5px;'
            'background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.10);'
            'color:rgba(186,230,253,0.70);">' + st.session_state.semester + '</span>'
            '<span style="font-size:0.62rem;padding:2px 9px;border-radius:5px;'
            'background:rgba(255,255,255,0.05);border:1px solid ' + b_color + '44;'
            'color:' + b_color + ';font-weight:700;">' + st.session_state.branch + '</span>'
            '</div></div></div>',
            unsafe_allow_html=True,
        )

        # Quick stat row
        att_all  = st.session_state.attendance
        ov_pct   = overall_pct(att_all)
        n_subj   = len(att_all)
        low_cnt  = sum(1 for r in att_all.values() if att_pct(r) < 75 and r["total"] > 0)

        st.markdown(
            '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;'
            'gap:8px;margin-bottom:14px;">' +
            ''.join(
                '<div style="background:rgba(255,255,255,0.03);'
                'border:1px solid rgba(255,255,255,0.07);'
                'border-radius:9px;padding:9px 10px;text-align:center;">'
                '<div style="font-family:\'Syne Mono\',monospace;font-size:0.95rem;'
                'font-weight:700;color:' + vc + ';margin-bottom:2px;">' + str(vv) + '</div>'
                '<div style="font-size:0.58rem;color:rgba(148,163,184,0.45);'
                'text-transform:uppercase;letter-spacing:0.6px;">' + lb + '</div>'
                '</div>'
                for vv, vc, lb in [
                    (str(ov_pct) + "%", "#10B981" if ov_pct >= 75 else "#F59E0B", "Overall"),
                    (n_subj,            "#60A5FA",  "Subjects"),
                    (low_cnt,           "#EF4444" if low_cnt else "#10B981", "Low Att."),
                ]
            ) +
            '</div>',
            unsafe_allow_html=True,
        )

        # PDF status
        if st.session_state.schedule_loaded:
            st.markdown(
                '<div style="background:rgba(16,185,129,0.07);'
                'border:1px solid rgba(16,185,129,0.20);border-radius:8px;'
                'padding:7px 12px;margin-bottom:10px;font-size:0.72rem;'
                'color:#34D399;display:flex;align-items:center;gap:6px;">'
                '<span>&#128196;</span>'
                '<span>' + st.session_state.pdf_filename + ' loaded</span>'
                '</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="edit-btn">', unsafe_allow_html=True)
        if st.button("✏  Edit Profile  +  Upload Schedule", key="edit_profile_main",
                     use_container_width=True):
            st.session_state.editing_profile = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# ATTENDANCE METER
# ─────────────────────────────────────────────────────────────────────
with col_att:
    att_all  = st.session_state.attendance
    ov       = overall_pct(att_all)
    s_lbl, s_tc, s_bg = status_info(ov)
    ov_c     = subj_color(ov)

    st.markdown(
        '<div style="background:linear-gradient(160deg,#0A1220,#060E1C);'
        'border:1px solid rgba(255,255,255,0.07);border-radius:16px;'
        'padding:20px 20px 16px;">'
        '<div style="display:flex;align-items:center;justify-content:space-between;'
        'margin-bottom:14px;">'
        '<span style="font-family:\'Syne Mono\',monospace;font-size:0.58rem;'
        'color:rgba(148,163,184,0.45);text-transform:uppercase;letter-spacing:1.4px;">'
        '// ATTENDANCE METER</span>'
        '<span style="font-size:0.66rem;font-weight:700;padding:3px 11px;'
        'border-radius:999px;background:' + s_bg + ';color:' + s_tc + ';'
        'border:1px solid ' + s_tc + '44;">' + s_lbl + '</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Overall arc display
    st.markdown(
        '<div style="display:flex;align-items:center;gap:16px;margin-bottom:12px;">'
        '<div style="font-family:\'Syne Mono\',monospace;font-size:2.4rem;'
        'color:' + ov_c + ';letter-spacing:-2px;line-height:1;">'
        + str(ov) + '<span style="font-size:1.1rem;">%</span></div>'
        '<div>'
        '<div style="font-size:0.70rem;color:rgba(148,163,184,0.50);">Overall Attendance</div>'
        '<div style="font-size:0.62rem;color:rgba(100,116,139,0.42);margin-top:2px;">'
        'Min required: 75%  ·  ' + str(len(att_all)) + ' subjects (' + st.session_state.branch + ')'
        '</div></div></div>',
        unsafe_allow_html=True,
    )
    st.progress(min(ov / 100, 1.0))
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── Subject rows (scrollable region) ─────────────────────────────────
    subjects = list(att_all.keys())
    # Split into common vs branch
    branch_only = BRANCH_SUBJECTS.get(st.session_state.branch, [])
    is_branch   = {s: (s in branch_only) for s in subjects}

    # Show common subjects in one expander, branch in another
    def render_subject_rows(subj_list: list[str], prefix: str):
        for i, subj in enumerate(subj_list):
            if subj not in att_all:
                continue
            rec  = att_all[subj]
            spct = att_pct(rec)
            sc   = subj_color(spct)
            key_p = prefix + "_pres_" + str(i)
            key_a = prefix + "_abs_"  + str(i)

            st.markdown(
                '<div style="background:rgba(255,255,255,0.02);'
                'border:1px solid rgba(255,255,255,0.06);'
                'border-radius:10px;padding:9px 12px;margin-bottom:7px;">',
                unsafe_allow_html=True,
            )
            c1, c2, c3, c4 = st.columns([4, 1.6, 1.2, 1.2])
            with c1:
                # Subject name + progress bar
                st.markdown(
                    '<div style="font-size:0.80rem;font-weight:600;color:#E2E8F0;'
                    'margin-bottom:3px;white-space:nowrap;overflow:hidden;'
                    'text-overflow:ellipsis;">' + subj + '</div>'
                    '<div style="font-family:\'Syne Mono\',monospace;font-size:0.66rem;'
                    'color:rgba(148,163,184,0.48);">'
                    + str(rec["present"]) + ' / ' + str(rec["total"]) + ' classes</div>',
                    unsafe_allow_html=True,
                )
                st.progress(min(spct / 100, 1.0))
            with c2:
                st.markdown(
                    '<div style="text-align:right;font-family:\'Syne Mono\',monospace;'
                    'font-weight:700;font-size:1.05rem;color:' + sc + ';padding-top:4px;">'
                    + str(spct) + '%</div>',
                    unsafe_allow_html=True,
                )
            with c3:
                st.markdown('<div class="present-btn">', unsafe_allow_html=True)
                if st.button("✓ P", key=key_p, use_container_width=True):
                    st.session_state.attendance[subj]["present"] += 1
                    st.session_state.attendance[subj]["total"]   += 1
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with c4:
                st.markdown('<div class="absent-btn">', unsafe_allow_html=True)
                if st.button("✗ A", key=key_a, use_container_width=True):
                    st.session_state.attendance[subj]["total"] += 1
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    # Common subjects
    with st.expander("📘  Common Subjects  (" + str(len(COMMON_SUBJECTS)) + ")", expanded=True):
        render_subject_rows(COMMON_SUBJECTS, "cmn")

    # Branch subjects
    if branch_only:
        with st.expander("🔬  " + st.session_state.branch + " Subjects  (" +
                         str(len(branch_only)) + ")", expanded=True):
            render_subject_rows(branch_only, "brnch")

    st.markdown("</div>", unsafe_allow_html=True)


st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ROW 2 — TODAY'S DIGITAL PLANNER  (from PDF schedule or manual)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div style="background:linear-gradient(160deg,#0A1220,#060E1C);'
    'border:1px solid rgba(255,255,255,0.07);border-radius:16px;'
    'padding:20px 20px 16px;margin-bottom:16px;">'
    '<div style="display:flex;align-items:center;justify-content:space-between;'
    'margin-bottom:14px;">'
    '<span style="font-family:\'Syne Mono\',monospace;font-size:0.58rem;'
    'color:rgba(148,163,184,0.45);text-transform:uppercase;letter-spacing:1.4px;">'
    '// TODAY\'S PLANNER</span>',
    unsafe_allow_html=True,
)

today_name = datetime.datetime.now().strftime("%A")
st.markdown(
    '<span style="font-size:0.66rem;color:rgba(96,165,250,0.70);'
    'font-family:\'Syne Mono\',monospace;">' + today_name.upper() + '</span>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Countdown banner ─────────────────────────────────────────────────────────
if st.session_state.schedule_loaded:
    today_slots = get_today_schedule(st.session_state.full_schedule)
    next_cls    = get_next_class(today_slots)

    if next_cls:
        mins = next_cls["minutes_away"]
        hrs  = mins // 60
        rem  = mins % 60
        countdown_str = (f"{hrs}h {rem}m" if hrs else f"{rem} min") + " away"
        urgency_color = "#EF4444" if mins < 15 else "#F59E0B" if mins < 45 else "#22D3EE"

        st.markdown(
            '<div style="background:linear-gradient(90deg,'
            'rgba(34,211,238,0.06),rgba(37,99,235,0.06));'
            'border:1px solid rgba(34,211,238,0.18);border-radius:12px;'
            'padding:12px 16px;margin-bottom:14px;'
            'display:flex;align-items:center;justify-content:space-between;">'
            '<div>'
            '<div style="font-size:0.62rem;color:rgba(148,163,184,0.50);'
            'text-transform:uppercase;letter-spacing:0.8px;margin-bottom:3px;">'
            'Next Class</div>'
            '<div style="font-weight:700;font-size:0.90rem;color:#E2E8F0;">'
            + next_cls["subject"] + '  <span style="font-size:0.72rem;'
            'color:rgba(148,163,184,0.55);">in ' + next_cls["room"] + '</span></div>'
            '</div>'
            '<div style="font-family:\'Syne Mono\',monospace;font-size:1.0rem;'
            'font-weight:700;color:' + urgency_color + ';text-align:right;">'
            + countdown_str +
            '<div style="font-size:0.62rem;color:rgba(148,163,184,0.45);'
            'font-weight:400;text-align:right;margin-top:1px;">'
            + next_cls["time"] + '</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="background:rgba(16,185,129,0.05);'
            'border:1px solid rgba(16,185,129,0.16);border-radius:10px;'
            'padding:10px 14px;margin-bottom:12px;font-size:0.78rem;'
            'color:rgba(52,211,153,0.70);">'
            '✅  No more classes scheduled for today.</div>',
            unsafe_allow_html=True,
        )

    # Schedule table
    pl1, pl2 = st.columns([1, 2])
    with pl1:
        st.markdown(
            '<div style="font-size:0.62rem;color:rgba(148,163,184,0.45);'
            'text-transform:uppercase;letter-spacing:0.8px;font-weight:600;'
            'margin-bottom:8px;">Time</div>',
            unsafe_allow_html=True,
        )
        for slot in today_slots:
            now_h = datetime.datetime.now().hour * 60 + datetime.datetime.now().minute
            sh, sm = map(int, slot["time"].split(":"))
            slot_m = sh * 60 + sm
            is_past = slot_m < now_h
            st.markdown(
                '<div style="font-family:\'Syne Mono\',monospace;font-size:0.72rem;'
                'color:' + ('rgba(148,163,184,0.35)' if is_past else '#60A5FA') + ';'
                'padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.04);'
                'text-decoration:' + ('line-through' if is_past else 'none') + ';">'
                + slot["time"] + '</div>',
                unsafe_allow_html=True,
            )
    with pl2:
        st.markdown(
            '<div style="font-size:0.62rem;color:rgba(148,163,184,0.45);'
            'text-transform:uppercase;letter-spacing:0.8px;font-weight:600;'
            'margin-bottom:8px;">Subject  /  Room  /  Type</div>',
            unsafe_allow_html=True,
        )
        for slot in today_slots:
            now_h = datetime.datetime.now().hour * 60 + datetime.datetime.now().minute
            sh, sm = map(int, slot["time"].split(":"))
            is_past = (sh * 60 + sm) < now_h
            type_color = {"Lab": "#F59E0B", "Tutorial": "#8B5CF6",
                          "Lecture": "#22D3EE"}.get(slot["type"], "#60A5FA")
            st.markdown(
                '<div style="padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);">'
                '<span style="font-size:0.80rem;font-weight:600;'
                'color:' + ('rgba(148,163,184,0.38)' if is_past else '#E2E8F0') + ';">'
                + slot["subject"] + '</span>'
                '  <span style="font-size:0.66rem;color:rgba(148,163,184,0.45);">'
                + slot["room"] + '</span>'
                '  <span style="font-size:0.60rem;padding:1px 7px;border-radius:4px;'
                'background:' + type_color + '18;color:' + type_color + ';font-weight:600;">'
                + slot["type"] + '</span>'
                '</div>',
                unsafe_allow_html=True,
            )

else:
    # ── No PDF yet — manual planner ───────────────────────────────────────
    st.markdown(
        '<div style="background:rgba(59,130,246,0.05);'
        'border:1px dashed rgba(59,130,246,0.22);border-radius:10px;'
        'padding:10px 14px;margin-bottom:14px;font-size:0.76rem;'
        'color:rgba(148,163,184,0.55);display:flex;align-items:center;gap:8px;">'
        '<span>&#128196;</span>'
        '<span>Upload your Weekly Schedule PDF in <b>Edit Profile</b> to auto-populate today\'s timetable.</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Manual planner rows
    MANUAL_SLOTS = ["08:00", "09:30", "11:00", "12:00", "14:00", "15:30"]
    for slot_time in MANUAL_SLOTS:
        override = st.session_state.planner_overrides.get(slot_time, "")
        p1, p2, p3, p4 = st.columns([1.2, 4.5, 0.8, 2])
        with p1:
            st.markdown(
                '<div style="font-family:\'Syne Mono\',monospace;font-size:0.70rem;'
                'color:#60A5FA;padding-top:10px;white-space:nowrap;">'
                + slot_time + '</div>',
                unsafe_allow_html=True,
            )
        with p2:
            note_val = st.text_input(
                label="", value=override,
                placeholder="Add task or note…",
                key="man_plan_" + slot_time,
                label_visibility="collapsed",
            )
        with p3:
            st.markdown('<div class="save-btn">', unsafe_allow_html=True)
            if st.button("💾", key="save_man_" + slot_time, use_container_width=True):
                st.session_state.planner_overrides[slot_time] = note_val
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with p4:
            saved = st.session_state.planner_overrides.get(slot_time, "")
            if saved:
                st.markdown(
                    '<div style="font-size:0.70rem;color:#34D399;'
                    'background:rgba(16,185,129,0.07);border:1px solid rgba(16,185,129,0.16);'
                    'border-radius:7px;padding:5px 10px;margin-top:2px;'
                    'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'
                    '✓ ' + saved + '</div>',
                    unsafe_allow_html=True,
                )

st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ROW 3 — QUICK LINKS  +  PERSONAL NOTES
# ══════════════════════════════════════════════════════════════════════════════
ql_col, notes_col = st.columns([1, 1.3], gap="large")

with ql_col:
    st.markdown(
        '<div style="background:linear-gradient(160deg,#0A1220,#060E1C);'
        'border:1px solid rgba(255,255,255,0.07);border-radius:16px;'
        'padding:20px 20px 16px;height:100%;">'
        '<div style="font-family:\'Syne Mono\',monospace;font-size:0.58rem;'
        'color:rgba(148,163,184,0.45);text-transform:uppercase;'
        'letter-spacing:1.4px;margin-bottom:14px;">// QUICK LINKS</div>',
        unsafe_allow_html=True,
    )
    QUICK_LINKS = [
        ("📤", "Upload Syllabus",  "Syllabus file uploader will be enabled here."),
        ("🔗", "Add PYQ Link",     "PYQ link manager will open here."),
        ("🔍", "Library Search",   "Library catalogue search will open here."),
    ]
    st.markdown('<div class="ql-btn">', unsafe_allow_html=True)
    for icon, label, fb in QUICK_LINKS:
        if st.button(icon + "  " + label, key="ql_" + label, use_container_width=True):
            st.session_state.ql_feedback = fb
            st.rerun()
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.ql_feedback:
        st.markdown(
            '<div style="background:rgba(59,130,246,0.07);'
            'border:1px solid rgba(59,130,246,0.20);border-radius:9px;'
            'padding:8px 12px;margin-top:8px;font-size:0.72rem;'
            'color:rgba(186,230,253,0.65);line-height:1.5;">'
            + st.session_state.ql_feedback + '</div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

with notes_col:
    st.markdown(
        '<div style="background:linear-gradient(160deg,#0A1220,#060E1C);'
        'border:1px solid rgba(255,255,255,0.07);border-radius:16px;'
        'padding:20px 20px 16px;height:100%;">'
        '<div style="font-family:\'Syne Mono\',monospace;font-size:0.58rem;'
        'color:rgba(148,163,184,0.45);text-transform:uppercase;'
        'letter-spacing:1.4px;margin-bottom:14px;">// PERSONAL NOTES</div>',
        unsafe_allow_html=True,
    )
    notes_val = st.text_area(
        label="", value=st.session_state.notes_text,
        height=130, placeholder="• Add a note…",
        key="notes_area", label_visibility="collapsed",
    )
    n1, n2 = st.columns(2)
    with n1:
        st.markdown('<div class="save-btn">', unsafe_allow_html=True)
        if st.button("💾  Save", key="save_notes_btn", use_container_width=True):
            st.session_state.notes_text = notes_val
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with n2:
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("🗑  Clear", key="clr_notes_btn", use_container_width=True):
            st.session_state.notes_text = ""
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.notes_text.strip():
        lines = st.session_state.notes_text.strip().split("\n")
        preview = "".join(
            '<div style="font-size:0.74rem;color:rgba(148,163,184,0.62);'
            'padding:3px 0;border-bottom:1px solid rgba(255,255,255,0.04);'
            'line-height:1.55;">'
            + (ln if ln.strip().startswith("•") else "• " + ln) + '</div>'
            for ln in lines if ln.strip()
        )
        st.markdown(
            '<div style="margin-top:10px;background:rgba(255,255,255,0.018);'
            'border:1px solid rgba(255,255,255,0.06);border-radius:9px;'
            'padding:9px 12px;max-height:90px;overflow-y:auto;">'
            + preview + '</div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FLOATING AI BUTTON + CHATBOT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

_, _, ai_col = st.columns([3, 2, 1])
with ai_col:
    st.markdown('<div class="floating-ai-btn">', unsafe_allow_html=True)
    if st.button("🤖 AskMNIT AI", key="float_ai_toggle", use_container_width=True):
        st.session_state.show_ai    = not st.session_state.show_ai
        st.session_state.ai_messages = []
        st.session_state.ai_pending  = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.show_ai:
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div style="background:linear-gradient(160deg,#0A1220,#050E1A);'
        'border:1px solid rgba(16,185,129,0.28);border-radius:20px;'
        'padding:22px 22px 10px;box-shadow:0 14px 52px rgba(16,185,129,0.12);">'

        '<div style="display:flex;align-items:center;justify-content:space-between;'
        'margin-bottom:14px;">'
        '<div style="display:flex;align-items:center;gap:10px;">'
        '<div style="width:30px;height:30px;border-radius:8px;'
        'background:linear-gradient(135deg,#059669,#10B981);'
        'display:flex;align-items:center;justify-content:center;font-size:0.88rem;'
        'box-shadow:0 3px 12px rgba(16,185,129,0.30);">&#129302;</div>'
        '<div>'
        '<div style="font-family:\'Syne Mono\',monospace;font-size:0.84rem;'
        'color:#E2E8F0;">AskMNIT AI</div>'
        '<div style="font-size:0.56rem;color:#10B981;font-weight:600;">&#9679; Active</div>'
        '</div></div>'
        '<div style="font-size:0.62rem;color:rgba(148,163,184,0.40);">'
        'Session-local  ·  LLaMA 3.3 70B (demo)</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    first_name = st.session_state.student_name.split()[0]

    if not st.session_state.ai_messages:
        st.markdown(
            '<div style="text-align:center;padding:30px 16px 22px;opacity:0.55;">'
            '<div style="font-size:1.9rem;margin-bottom:10px;">&#129302;</div>'
            '<div style="font-family:\'Syne Mono\',monospace;font-size:0.84rem;'
            'color:#E2E8F0;margin-bottom:6px;">Ready, ' + first_name + '.</div>'
            '<div style="font-size:0.74rem;color:rgba(226,232,240,0.45);'
            'max-width:320px;margin:0 auto;line-height:1.65;">'
            'Attendance analysis, PYQ links, schedule queries, exam strategy — ask anything.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        for msg in st.session_state.ai_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # ── Context-aware demo AI responses ──────────────────────────────────
    if st.session_state.ai_pending and st.session_state.ai_messages:
        last   = st.session_state.ai_messages[-1]["content"]
        lower  = last.lower()
        att    = st.session_state.attendance
        branch = st.session_state.branch

        with st.chat_message("assistant"):
            if "attendance" in lower or "present" in lower or "absent" in lower or "%" in lower:
                ov_now  = overall_pct(att)
                low_sub = [(s, att_pct(r)) for s, r in att.items()
                           if att_pct(r) < 75 and r["total"] > 0]
                resp = (
                    "**Attendance Report — " + st.session_state.student_name + ":**\n\n"
                    "Overall: **" + str(ov_now) + "%**\n\n"
                )
                if low_sub:
                    resp += "⚠️ **Below 75% threshold:**\n"
                    for s, p in low_sub:
                        tot = att[s]["total"]
                        need = max(0, int((0.75 * tot - att[s]["present"]) / 0.25) + 1)
                        resp += f"- **{s}**: {p}%  →  need {need} more present\n"
                else:
                    resp += "✅ All subjects above the 75% minimum — keep it steady!"

            elif "schedule" in lower or "class" in lower or "timetable" in lower or "today" in lower:
                if st.session_state.schedule_loaded:
                    today_s = get_today_schedule(st.session_state.full_schedule)
                    nxt = get_next_class(today_s)
                    resp = "**Today's Schedule (" + today_name + "):**\n\n"
                    for slot in today_s:
                        resp += f"- **{slot['time']}** — {slot['subject']} in {slot['room']} ({slot['type']})\n"
                    if nxt:
                        resp += f"\n⏰ Next class: **{nxt['subject']}** in {nxt['minutes_away']} minutes."
                    else:
                        resp += "\n✅ No more classes today."
                else:
                    resp = ("Upload your Weekly Schedule PDF in **Edit Profile** "
                            "to get your personalised timetable and next-class countdown here.")

            elif "branch" in lower or "subject" in lower or "syllabus" in lower:
                subjs = get_subjects_for_branch(branch)
                resp = (
                    "**Your subjects for " + branch + " — " + st.session_state.semester + ":**\n\n"
                    "**Common:**\n" + "\n".join(f"- {s}" for s in COMMON_SUBJECTS) + "\n\n"
                    "**" + branch + " specific:**\n" +
                    "\n".join(f"- {s}" for s in BRANCH_SUBJECTS.get(branch, [])) +
                    "\n\nTotal: **" + str(len(subjs)) + " subjects**"
                )

            elif "pyq" in lower or "previous" in lower or "question paper" in lower:
                resp = ("You can access Previous Year Papers from the **📂 PYQs** section in the sidebar. "
                        "You can also add custom PYQ links using '🔗 Add PYQ Link' in Quick Links.")

            elif "fee" in lower or "pay" in lower or "due" in lower:
                resp = ("Fee details and payment options are in the **💰 Fee Portal** section. "
                        "Head to the sidebar to access your fee records.")

            elif "schedule" in lower and not st.session_state.schedule_loaded:
                resp = ("Your schedule isn't loaded yet. Click **Edit Profile** on the dashboard, "
                        "then upload your Weekly Schedule PDF. The planner will auto-update.")

            elif "cgpa" in lower or "grade" in lower or "result" in lower:
                resp = ("Academic records including CGPA and grades are in the **📚 Academics** section. "
                        "I'll surface them directly here once you wire the ERP integration.")

            else:
                resp = (
                    "I'm AskMNIT — your campus AI. Here's what I can help you with:\n\n"
                    "- **Attendance** — analyse shortfall and calculate classes needed\n"
                    "- **Schedule** — today's timetable and next-class countdown\n"
                    "- **Subjects** — branch-specific syllabus for " + branch + "\n"
                    "- **PYQs** — links and search for previous year papers\n"
                    "- **Fees** — due dates and payment status\n"
                    "- **Exams** — preparation strategy and scheduling\n\n"
                    "What would you like to dig into?"
                )

            st.markdown(resp)
            st.session_state.ai_messages.append({"role": "assistant", "content": resp})
        st.session_state.ai_pending = False
        st.rerun()

    if prompt := st.chat_input("Ask about attendance, schedule, subjects, fees…",
                                key="ai_chat_input"):
        st.session_state.ai_messages.append({"role": "user", "content": prompt})
        st.session_state.ai_pending = True
        st.rerun()

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
    if st.button("✕  Close AI Panel", key="close_ai_btn", use_container_width=True):
        st.session_state.show_ai     = False
        st.session_state.ai_messages = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-top:36px;
            padding:12px 0;border-top:1px solid rgba(255,255,255,0.05);">
    <span style="font-family:'Syne Mono',monospace;font-size:0.56rem;
                 color:rgba(148,163,184,0.28);letter-spacing:1.2px;">
        ASKMNT  ·  STUDENT PORTAL  ·  SESSION-STATE ONLY  ·  MNIT JAIPUR
    </span>
</div>
""", unsafe_allow_html=True)
