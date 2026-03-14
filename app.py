# AskMNIT — Student Dashboard + Premium AI Chat
# Single file, session-state driven, no external database.
# NEW: Pinned Notes, Top-Right Settings Menu (st.popover), Circular Profile Pic,
#      Styled Schedule Cards, base64 profile image, persistent schedule template.
# RULE: Zero HTML comments inside st.markdown() — they render as visible text.

import streamlit as st
import datetime
import random
import base64
import io

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AskMNIT",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# SUBJECT DATABASE
# ─────────────────────────────────────────────────────────────────────────────
COMMON_SUBJECTS = [
    "Mathematics I/II", "Physics", "Chemistry", "Computer Programming",
    "Basic Electrical", "Basic Electronics", "Basic Mechanical",
    "Engineering Drawing", "Environmental Science",
    "Technical Communication", "Basic Economics",
]
BRANCH_SUBJECTS: dict[str, list[str]] = {
    "CSE":        ["Discrete Mathematics", "Problem Solving using C"],
    "AI & ML":    ["Mathematics for AI", "Data Structures and Algorithms"],
    "ECE":        ["Signals and Systems", "Electronic Devices and Circuits"],
    "Civil":      ["Mechanics of Solid", "Engineering Geology"],
    "Metallurgy": ["Engineering Materials", "Mineral Processing"],
}
BRANCHES  = ["CSE", "AI & ML", "ECE", "Civil", "Metallurgy"]
SEMESTERS = [f"Semester {i}" for i in range(1, 9)]
DAYS      = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

TYPE_COLORS = {
    "Lecture":  "#22D3EE",
    "Lab":      "#F59E0B",
    "Tutorial": "#A78BFA",
}

# ─────────────────────────────────────────────────────────────────────────────
# PDF SCHEDULE PLACEHOLDER
# Replace internals with pdfplumber in production.
# ─────────────────────────────────────────────────────────────────────────────
def process_schedule_pdf(file, branch: str) -> dict:
    pool = COMMON_SUBJECTS[:4] + BRANCH_SUBJECTS.get(branch, [])
    random.seed(42)
    TIME_PAIRS = [
        ("08:00","09:00"), ("09:30","10:30"), ("11:00","12:00"),
        ("12:00","13:00"), ("14:00","15:00"), ("15:30","16:30"),
    ]
    sched: dict[str, list[dict]] = {}
    for day in DAYS[:6]:
        chosen = sorted(random.sample(range(len(TIME_PAIRS)), k=random.randint(2, 4)))
        sched[day] = [
            {
                "time_start": TIME_PAIRS[ci][0],
                "time_end":   TIME_PAIRS[ci][1],
                "subject":    random.choice(pool),
                "room":       random.choice(["LT-1","LT-2","Lab-A","Lab-B","CR-3","CR-5"]),
                "type":       random.choice(["Lecture","Lecture","Lab","Tutorial"]),
            }
            for ci in chosen
        ]
    return sched

def get_today_slots(full_sched: dict) -> list[dict]:
    return full_sched.get(datetime.datetime.now().strftime("%A"), [])

def get_next_class(slots: list[dict]) -> dict | None:
    now = datetime.datetime.now()
    for slot in slots:
        h, m = map(int, slot["time_start"].split(":"))
        dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if dt > now:
            return {**slot, "minutes_away": int((dt - now).total_seconds() // 60)}
    return None

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def subjects_for_branch(b: str) -> list[str]:
    return COMMON_SUBJECTS + BRANCH_SUBJECTS.get(b, [])

def blank_att(subjects: list[str]) -> dict:
    return {s: {"present": 0, "total": 0} for s in subjects}

def att_pct(rec: dict) -> float:
    return round(rec["present"] / rec["total"] * 100, 1) if rec["total"] else 0.0

def overall_pct(att: dict) -> float:
    tp = sum(r["present"] for r in att.values())
    tt = sum(r["total"]   for r in att.values())
    return round(tp / tt * 100, 1) if tt else 0.0

def status_badge(pct: float) -> tuple[str, str, str]:
    if pct >= 75: return "Safe ✅",      "#10B981", "rgba(16,185,129,0.12)"
    if pct >= 65: return "Low ⚠️",      "#F59E0B", "rgba(245,158,11,0.12)"
    return              "Critical 🔴",  "#EF4444", "rgba(239,68,68,0.12)"

def att_color(pct: float) -> str:
    return "#10B981" if pct >= 75 else "#F59E0B" if pct >= 65 else "#EF4444"

def initials(name: str) -> str:
    return "".join(w[0].upper() for w in name.split()[:2]) if name else "??"

def branch_hex(b: str) -> str:
    return {"CSE":"#3B82F6","AI & ML":"#8B5CF6","ECE":"#06B6D4",
            "Civil":"#F59E0B","Metallurgy":"#10B981"}.get(b, "#6366F1")

def img_to_b64(uploaded_file) -> str:
    """Convert Streamlit uploaded file to base64 data URI."""
    data = uploaded_file.read()
    mime = uploaded_file.type or "image/png"
    b64  = base64.b64encode(data).decode()
    return f"data:{mime};base64,{b64}"

def fmt_time(t: str) -> str:
    """Convert 24h 'HH:MM' to '09:30 AM' style."""
    try:
        h, m  = map(int, t.split(":"))
        suffix = "AM" if h < 12 else "PM"
        h12    = h % 12 or 12
        return f"{h12:02d}:{m:02d} {suffix}"
    except Exception:
        return t

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE — initialise all keys once
# ─────────────────────────────────────────────────────────────────────────────
_def_branch = "CSE"
_DEFAULTS: dict = {
    # Routing
    "view":                 "dashboard",
    "nav_page":             "My Dashboard",
    # Profile
    "student_name":         "Sumit Chaudhary",
    "college_id":           "2022UMT1234",
    "semester":             "Semester 6",
    "branch":               _def_branch,
    "profile_pic_b64":      "",          # base64 data URI or ""
    # Settings menu state
    "settings_mode":        None,        # None | "profile" | "schedule"
    # Attendance
    "attendance":           blank_att(subjects_for_branch(_def_branch)),
    # Schedule (persistent template — reused every week)
    "schedule_loaded":      False,
    "full_schedule":        {},
    "pdf_filename":         "",
    # Notes
    "notes_list":           [            # list of {"text": str, "pinned": bool}
        {"text": "Mid-sem revision starts Monday",   "pinned": False},
        {"text": "Submit fee by 17 Mar",             "pinned": False},
        {"text": "Collect hall ticket from ERP",     "pinned": False},
    ],
    "new_note_draft":       "",
    # Quick links feedback
    "ql_feedback":          "",
    # Chat
    "chat_messages":        [],
    "chat_pending":         False,
    "chat_sessions":        [],
    "show_chat_history":    False,
    "show_chat_settings":   False,
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,700;9..144,900&family=DM+Mono:wght@400;500&family=Outfit:wght@300;400;500;600;700&display=swap');

:root {
    --bg:       #060A12;
    --surf:     #0B1120;
    --surf2:    #101929;
    --surf3:    #141F32;
    --border:   rgba(255,255,255,0.07);
    --border2:  rgba(255,255,255,0.13);
    --accent:   #3B82F6;
    --indigo:   #6366F1;
    --cyan:     #22D3EE;
    --green:    #10B981;
    --amber:    #F59E0B;
    --red:      #EF4444;
    --violet:   #A78BFA;
    --text:     #E2E8F0;
    --muted:    rgba(148,163,184,0.55);
    --mono:     'DM Mono', monospace;
    --sans:     'Outfit', sans-serif;
    --display:  'Fraunces', serif;
}

*, html, body { box-sizing: border-box; margin: 0; padding: 0; }
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"] {
    font-family: var(--sans) !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}

header[data-testid="stHeader"], footer, #MainMenu,
[data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
[data-testid="stMainBlockContainer"] { padding: 0 !important; max-width: 100% !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surf) !important;
    border-right: 1px solid rgba(59,130,246,0.16) !important;
    min-width: 210px !important;
    max-width: 210px !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }

/* ── Inputs / selects ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
    font-size: 0.87rem !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(59,130,246,0.55) !important;
    box-shadow: 0 0 0 2.5px rgba(59,130,246,0.13) !important;
}
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label {
    color: var(--muted) !important;
    font-size: 0.70rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.6px !important;
    font-family: var(--sans) !important;
}
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}
[data-testid="stSelectbox"] label {
    color: var(--muted) !important;
    font-size: 0.70rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    font-family: var(--sans) !important;
}
[data-testid="stFileUploader"] {
    background: rgba(59,130,246,0.04) !important;
    border: 1px dashed rgba(59,130,246,0.26) !important;
    border-radius: 12px !important;
}

/* ── Base button ── */
.stButton > button {
    background: linear-gradient(135deg,#2563EB,#4F46E5) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 9px !important;
    font-family: var(--sans) !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 9px 16px !important;
    box-shadow: 0 3px 14px rgba(37,99,235,0.20) !important;
    transition: all 0.16s ease !important;
}
.stButton > button:hover { opacity: .88 !important; transform: translateY(-1px) !important; }
.stButton > button:active { transform: scale(0.97) !important; }

/* nav */
.nav-btn .stButton > button {
    background: transparent !important; color: rgba(148,163,184,.65) !important;
    border: none !important; box-shadow: none !important;
    text-align: left !important; justify-content: flex-start !important;
    padding: 10px 14px !important; font-size: 0.83rem !important;
    font-weight: 500 !important; border-radius: 8px !important;
}
.nav-btn .stButton > button:hover {
    background: rgba(59,130,246,.10) !important; color: #BAE6FD !important; transform: none !important;
}
.nav-btn-active .stButton > button {
    background: rgba(59,130,246,.14) !important; color: #60A5FA !important;
    border-left: 2px solid #3B82F6 !important; font-weight: 700 !important; box-shadow: none !important;
}

/* ghost */
.ghost-btn .stButton > button {
    background: rgba(255,255,255,.05) !important;
    border: 1px solid var(--border2) !important;
    color: rgba(226,232,240,.55) !important; box-shadow: none !important;
}
.ghost-btn .stButton > button:hover { background: rgba(59,130,246,.10) !important; color: var(--text) !important; }

/* present */
.present-btn .stButton > button {
    background: linear-gradient(135deg,#065F46,#10B981) !important;
    box-shadow: 0 2px 10px rgba(16,185,129,.18) !important;
    padding: 6px 11px !important; font-size: 0.75rem !important; border-radius: 7px !important;
}
/* absent */
.absent-btn .stButton > button {
    background: linear-gradient(135deg,#7F1D1D,#EF4444) !important;
    box-shadow: 0 2px 10px rgba(239,68,68,.16) !important;
    padding: 6px 11px !important; font-size: 0.75rem !important; border-radius: 7px !important;
}
/* save amber */
.save-btn .stButton > button {
    background: linear-gradient(135deg,#92400E,#F59E0B) !important;
    box-shadow: 0 2px 10px rgba(245,158,11,.18) !important;
    padding: 7px 13px !important; font-size: 0.77rem !important;
}
/* edit subtle */
.edit-btn .stButton > button {
    background: rgba(255,255,255,.05) !important;
    border: 1px solid var(--border2) !important;
    color: rgba(148,163,184,.65) !important;
    box-shadow: none !important; font-size: 0.72rem !important; padding: 4px 10px !important;
}
.edit-btn .stButton > button:hover { color: #BAE6FD !important; background: rgba(59,130,246,.10) !important; }

/* pin note */
.pin-btn .stButton > button {
    background: rgba(245,158,11,0.10) !important;
    border: 1px solid rgba(245,158,11,0.28) !important;
    color: #FCD34D !important; box-shadow: none !important;
    font-size: 0.70rem !important; padding: 4px 10px !important; border-radius: 7px !important;
}
.pin-btn .stButton > button:hover {
    background: rgba(245,158,11,0.20) !important; transform: none !important;
}
/* unpin note */
.unpin-btn .stButton > button {
    background: rgba(239,68,68,0.09) !important;
    border: 1px solid rgba(239,68,68,0.24) !important;
    color: #FCA5A5 !important; box-shadow: none !important;
    font-size: 0.70rem !important; padding: 4px 10px !important; border-radius: 7px !important;
}
.unpin-btn .stButton > button:hover {
    background: rgba(239,68,68,0.18) !important; transform: none !important;
}
/* delete note */
.del-btn .stButton > button {
    background: rgba(239,68,68,0.07) !important;
    border: 1px solid rgba(239,68,68,0.18) !important;
    color: rgba(252,165,165,0.70) !important;
    box-shadow: none !important; font-size: 0.68rem !important; padding: 3px 8px !important;
    border-radius: 6px !important;
}
.del-btn .stButton > button:hover { background: rgba(239,68,68,0.16) !important; transform: none !important; }

/* quick links */
.ql-btn .stButton > button {
    background: rgba(255,255,255,.03) !important;
    border: 1px solid var(--border2) !important;
    color: rgba(186,230,253,.65) !important; box-shadow: none !important;
    text-align: left !important; justify-content: flex-start !important;
    font-size: 0.80rem !important; padding: 9px 14px !important; border-radius: 9px !important;
}
.ql-btn .stButton > button:hover {
    background: rgba(59,130,246,.10) !important; border-color: rgba(59,130,246,.28) !important;
    color: #BAE6FD !important; transform: none !important;
}

/* logout */
.logout-btn .stButton > button {
    background: rgba(239,68,68,.09) !important;
    border: 1px solid rgba(239,68,68,.20) !important;
    color: #FCA5A5 !important; box-shadow: none !important; font-size: 0.80rem !important;
}
.logout-btn .stButton > button:hover { background: rgba(239,68,68,.18) !important; }

/* open chat CTA */
.open-chat-btn .stButton > button {
    background: linear-gradient(135deg,#059669,#10B981) !important;
    border-radius: 12px !important; font-weight: 700 !important;
    font-size: 0.88rem !important; padding: 11px 22px !important;
    box-shadow: 0 5px 24px rgba(16,185,129,.36) !important;
    font-family: var(--mono) !important;
}
.open-chat-btn .stButton > button:hover {
    box-shadow: 0 7px 32px rgba(16,185,129,.50) !important; transform: translateY(-2px) !important;
}

/* settings menu button */
.settings-menu-btn .stButton > button {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: rgba(226,232,240,0.75) !important;
    box-shadow: none !important; font-size: 0.82rem !important;
    font-weight: 600 !important; padding: 8px 16px !important; border-radius: 10px !important;
}
.settings-menu-btn .stButton > button:hover {
    background: rgba(59,130,246,0.13) !important; color: #BAE6FD !important;
    border-color: rgba(59,130,246,0.30) !important;
}

/* ERP link button */
.erp-btn .stButton > button {
    background: linear-gradient(135deg,#065F46,#10B981) !important;
    font-size: 0.82rem !important; font-weight: 700 !important;
    padding: 9px 18px !important; border-radius: 9px !important;
    box-shadow: 0 3px 12px rgba(16,185,129,0.22) !important;
}

/* chat pills */
.chat-pill .stButton > button {
    background: rgba(255,255,255,.05) !important;
    border: 1px solid rgba(255,255,255,.10) !important;
    border-radius: 999px !important; color: rgba(226,232,240,.62) !important;
    box-shadow: none !important; font-size: 0.78rem !important;
    font-weight: 500 !important; padding: 7px 16px !important;
}
.chat-pill .stButton > button:hover {
    background: rgba(59,130,246,.13) !important; border-color: rgba(59,130,246,.32) !important;
    color: #BAE6FD !important; transform: none !important;
}

/* back btn */
.back-btn .stButton > button {
    background: rgba(255,255,255,.06) !important;
    border: 1px solid rgba(255,255,255,.11) !important;
    border-radius: 10px !important; color: rgba(226,232,240,.62) !important;
    box-shadow: none !important; font-size: 0.80rem !important;
    font-weight: 600 !important; padding: 8px 18px !important;
}
.back-btn .stButton > button:hover {
    background: rgba(59,130,246,.13) !important; color: #BAE6FD !important;
    border-color: rgba(59,130,246,.28) !important;
}

/* suggestion chips */
.sug-btn .stButton > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 999px !important; color: rgba(186,230,253,0.70) !important;
    font-size: 0.76rem !important; font-weight: 500 !important;
    padding: 8px 16px !important; box-shadow: none !important;
}
.sug-btn .stButton > button:hover {
    background: rgba(59,130,246,0.13) !important; border-color: rgba(59,130,246,0.32) !important;
    color: #BAE6FD !important; transform: translateY(-1px) !important;
}

/* ── Progress ── */
[data-testid="stProgress"] > div > div {
    border-radius: 99px !important; background: linear-gradient(90deg,#2563EB,#22D3EE) !important;
}
[data-testid="stProgress"] > div {
    background: rgba(255,255,255,.07) !important; border-radius: 99px !important; height: 5px !important;
}

/* ── Chat ── */
[data-testid="stChatInput"] > div {
    background: rgba(11,17,32,.98) !important;
    border: 1px solid rgba(59,130,246,.30) !important; border-radius: 16px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important; color: var(--text) !important;
    font-family: var(--sans) !important; font-size: 0.92rem !important;
}
[data-testid="stChatInput"] button[data-testid="stChatInputSubmitButton"] {
    background: linear-gradient(135deg,#2563EB,#4F46E5) !important; border-radius: 9px !important;
}
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,.025) !important;
    border: 1px solid var(--border) !important; border-radius: 14px !important;
    font-family: var(--sans) !important;
}

/* ── Popover ── */
[data-testid="stPopover"] > div {
    background: #0F1928 !important;
    border: 1px solid rgba(59,130,246,0.28) !important;
    border-radius: 14px !important;
    box-shadow: 0 12px 40px rgba(0,0,0,0.60) !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,.018) !important;
    border: 1px solid var(--border) !important; border-radius: 12px !important;
}
summary { font-family: var(--sans) !important; font-weight: 600 !important; }

/* ── Typography misc ── */
h1,h2,h3,h4 { font-family: var(--mono) !important; font-weight: 500 !important; }
[data-testid="stMarkdown"] p,
[data-testid="stMarkdown"] li { color: rgba(226,232,240,.72) !important; font-family: var(--sans) !important; }
hr { border-color: var(--border) !important; }

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(59,130,246,.22); border-radius: 4px; }
[data-testid="column"] { padding: 0 5px !important; }

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
.hero-anim { animation: fadeUp 0.50s ease both; }

@keyframes msgIn {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}
[data-testid="stChatMessage"] { animation: msgIn 0.20s ease both !important; }

/* Pinned note banner pulse */
@keyframes pinPulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(245,158,11,0.30); }
    50%       { box-shadow: 0 0 0 6px rgba(245,158,11,0.00); }
}
.pinned-note-card { animation: pinPulse 2.5s ease infinite; }
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# VIEW ROUTER
# ═════════════════════════════════════════════════════════════════════════════
view = st.session_state.view


###############################################################################
#  CHAT VIEW  (no sidebar)
###############################################################################
if view == "chat":
    st.markdown("""
    <style>
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stMainBlockContainer"] { padding: 0 !important; max-width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

    has_messages = len(st.session_state.chat_messages) > 0

    # Top bar
    st.markdown(
        '<div style="background:rgba(6,10,18,0.97);'
        'border-bottom:1px solid rgba(59,130,246,0.14);'
        'padding:11px 24px;display:flex;align-items:center;gap:10px;">'
        '<div style="width:26px;height:26px;border-radius:7px;'
        'background:linear-gradient(135deg,#2563EB,#4F46E5);'
        'display:flex;align-items:center;justify-content:center;'
        'font-size:0.82rem;font-weight:700;color:white;">A</div>'
        '<span style="font-family:\'DM Mono\',monospace;font-size:0.86rem;color:#E2E8F0;">AskMNIT</span>'
        '<span style="font-size:0.58rem;color:#10B981;font-weight:600;">&#9679; AI</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Action pills
    _, pill_area = st.columns([2.5, 2])
    with pill_area:
        p1, p2, p3, p4 = st.columns([1.2, 1, 1, 1.5])
        with p1:
            st.markdown('<div class="chat-pill">', unsafe_allow_html=True)
            if st.button("➕ New Chat", key="chat_new", use_container_width=True):
                if st.session_state.chat_messages:
                    first_user = next(
                        (m["content"][:38] for m in st.session_state.chat_messages if m["role"] == "user"),
                        "Session"
                    )
                    st.session_state.chat_sessions.append(
                        {"label": first_user + "…", "messages": list(st.session_state.chat_messages)}
                    )
                st.session_state.chat_messages = []
                st.session_state.chat_pending  = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with p2:
            st.markdown('<div class="chat-pill">', unsafe_allow_html=True)
            if st.button("⏱ History", key="chat_hist", use_container_width=True):
                st.session_state.show_chat_history  = not st.session_state.show_chat_history
                st.session_state.show_chat_settings = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with p3:
            st.markdown('<div class="chat-pill">', unsafe_allow_html=True)
            if st.button("⚙ Settings", key="chat_sett", use_container_width=True):
                st.session_state.show_chat_settings = not st.session_state.show_chat_settings
                st.session_state.show_chat_history  = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with p4:
            st.markdown('<div class="back-btn">', unsafe_allow_html=True)
            if st.button("🔙 Dashboard", key="back_to_dash", use_container_width=True):
                st.session_state.view               = "dashboard"
                st.session_state.show_chat_history  = False
                st.session_state.show_chat_settings = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # Dropdown panels
    if st.session_state.show_chat_history:
        _, panel, _ = st.columns([1, 3, 1])
        with panel:
            sessions = st.session_state.chat_sessions
            if not sessions:
                st.info("No saved sessions yet. Click ➕ New Chat to save the current one.")
            else:
                st.markdown(
                    '<div style="background:#101929;border:1px solid rgba(255,255,255,0.12);'
                    'border-radius:14px;padding:16px 18px;margin-bottom:8px;">'
                    '<div style="font-family:\'DM Mono\',monospace;font-size:0.58rem;'
                    'color:rgba(148,163,184,.45);text-transform:uppercase;'
                    'letter-spacing:1.2px;margin-bottom:12px;">Chat History</div>',
                    unsafe_allow_html=True,
                )
                for i, sess in enumerate(reversed(sessions)):
                    idx = len(sessions) - 1 - i
                    hc1, hc2 = st.columns([5, 1])
                    with hc1:
                        st.markdown(
                            '<div style="font-size:0.77rem;color:rgba(148,163,184,.62);'
                            'padding:5px 0;border-bottom:1px solid rgba(255,255,255,.04);">'
                            + str(idx + 1) + '.  ' + sess["label"] + '</div>',
                            unsafe_allow_html=True,
                        )
                    with hc2:
                        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
                        if st.button("Load", key="load_" + str(idx)):
                            st.session_state.chat_messages = list(sess["messages"])
                            st.session_state.show_chat_history = False
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.show_chat_settings:
        _, panel, _ = st.columns([1, 3, 1])
        with panel:
            st.markdown(
                '<div style="background:#101929;border:1px solid rgba(255,255,255,0.12);'
                'border-radius:14px;padding:16px 18px;margin-bottom:8px;">'
                '<div style="font-family:\'DM Mono\',monospace;font-size:0.58rem;'
                'color:rgba(148,163,184,.45);text-transform:uppercase;'
                'letter-spacing:1.2px;margin-bottom:10px;">Bot Settings</div>'
                '<div style="font-size:0.80rem;color:rgba(148,163,184,.56);line-height:1.75;">'
                'Model: LLaMA 3.3 70B (via Groq)<br>'
                'Context: ' + st.session_state.student_name + ' &nbsp;·&nbsp; ' + st.session_state.branch + '<br>'
                'Language: English &nbsp;·&nbsp; Response: Concise'
                '</div>'
                '<div style="font-size:0.60rem;color:rgba(100,116,139,.36);margin-top:8px;">'
                'Full settings available after GROQ_API_KEY is configured.'
                '</div></div>',
                unsafe_allow_html=True,
            )

    # SHIFT EFFECT
    if not has_messages:
        st.markdown("<div style='height:8vh'></div>", unsafe_allow_html=True)
        _, hero_col, _ = st.columns([1, 3, 1])
        with hero_col:
            st.markdown(
                '<div class="hero-anim" style="text-align:center;padding:0 0 24px;">'
                '<div style="width:72px;height:72px;margin:0 auto 20px;border-radius:20px;'
                'background:linear-gradient(135deg,#2563EB 0%,#4F46E5 50%,#059669 100%);'
                'display:flex;align-items:center;justify-content:center;font-size:2rem;'
                'box-shadow:0 0 0 1px rgba(59,130,246,0.28),0 12px 40px rgba(37,99,235,0.32),'
                '0 0 80px rgba(59,130,246,0.10);">&#129302;</div>'
                '<div style="font-family:\'Fraunces\',serif;font-size:2.6rem;font-weight:900;'
                'color:#E2E8F0;letter-spacing:-1.5px;line-height:1.08;margin-bottom:10px;">'
                'AskMNIT <span style="font-weight:300;color:#60A5FA;">AI</span></div>'
                '<div style="font-size:0.84rem;color:rgba(148,163,184,0.52);'
                'line-height:1.65;margin-bottom:28px;max-width:380px;'
                'margin-left:auto;margin-right:auto;">'
                'Your campus intelligence layer — attendance, PYQs, schedule, exam prep.'
                '</div></div>',
                unsafe_allow_html=True,
            )

        _, chips_col, _ = st.columns([0.3, 4, 0.3])
        with chips_col:
            SUGGESTIONS = [
                "📊 Analyse my attendance", "📅 What's next on my schedule?",
                "📂 Find PYQs for my branch", "💰 Check my fee status",
                "📚 Subjects for " + st.session_state.branch, "⏰ Exam schedule tips",
            ]
            chip_cols = st.columns(len(SUGGESTIONS))
            for i, sug in enumerate(SUGGESTIONS):
                with chip_cols[i]:
                    st.markdown('<div class="sug-btn">', unsafe_allow_html=True)
                    if st.button(sug, key="sug_" + str(i), use_container_width=True):
                        st.session_state.chat_messages.append({"role": "user", "content": sug})
                        st.session_state.chat_pending = True
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        _, input_col, _ = st.columns([1, 3.5, 1])
        with input_col:
            if prompt := st.chat_input("Ask anything about your academics…", key="chat_input_hero"):
                st.session_state.chat_messages.append({"role": "user", "content": prompt})
                st.session_state.chat_pending = True
                st.rerun()

    else:
        st.markdown("""
        <style>
        [data-testid="stChatInput"] {
            position: fixed !important; bottom: 16px !important; left: 50% !important;
            transform: translateX(-50%) !important;
            width: min(780px, calc(100vw - 80px)) !important; z-index: 1000 !important;
        }
        [data-testid="stVerticalBlock"] { padding-bottom: 110px !important; }
        </style>
        """, unsafe_allow_html=True)

        _, msg_col, _ = st.columns([0.5, 4, 0.5])
        with msg_col:
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        if st.session_state.chat_pending and st.session_state.chat_messages:
            last  = st.session_state.chat_messages[-1]["content"]
            lower = last.lower()
            att   = st.session_state.attendance
            br    = st.session_state.branch

            with msg_col:
                with st.chat_message("assistant"):
                    if any(w in lower for w in ["attendance","present","absent","%"]):
                        ov = overall_pct(att)
                        low_subs = [(s, att_pct(r)) for s, r in att.items() if att_pct(r) < 75 and r["total"] > 0]
                        resp = "**Attendance Overview — " + st.session_state.student_name + "**\n\nOverall: **" + str(ov) + "%**\n\n"
                        if low_subs:
                            resp += "⚠️ **Below 75%:**\n"
                            for s, p in low_subs:
                                need = max(0, int((0.75 * att[s]["total"] - att[s]["present"]) / 0.25) + 1)
                                resp += f"- **{s}**: {p}% → attend **{need}** more to recover\n"
                        else:
                            resp += "✅ All subjects above 75%. Keep it steady!"
                    elif any(w in lower for w in ["schedule","class","next","today"]):
                        if st.session_state.schedule_loaded:
                            today_slots = get_today_slots(st.session_state.full_schedule)
                            nxt = get_next_class(today_slots)
                            today_name = datetime.datetime.now().strftime("%A")
                            resp = "**Today's Classes (" + today_name + ")**\n\n"
                            for slot in today_slots:
                                resp += f"- **{fmt_time(slot['time_start'])}–{fmt_time(slot['time_end'])}** — {slot['subject']} in {slot['room']} _({slot['type']})_\n"
                            resp += ("\n⏰ **Next:** " + nxt["subject"] + " in **" + str(nxt["minutes_away"]) + " min**"
                                     if nxt else "\n✅ No more classes today.")
                        else:
                            resp = "No schedule loaded. Go to **⚙️ Menu → Upload Weekly Schedule** on the dashboard."
                    elif any(w in lower for w in ["pyq","previous year","question paper"]):
                        resp = ("**PYQ Resources for " + br + "**\n\n"
                                "Access via **📂 PYQs** in the sidebar.\n\n"
                                "Your branch subjects: " + ", ".join(BRANCH_SUBJECTS.get(br, [])))
                    elif any(w in lower for w in ["fee","pay","due"]):
                        resp = "Fee details are in the **💰 Fee Portal** section on the dashboard sidebar."
                    elif any(w in lower for w in ["subject","syllabus","branch"]):
                        resp = ("**Subjects — " + br + " · " + st.session_state.semester + "**\n\n"
                                "**Common:**\n" + "\n".join(f"- {s}" for s in COMMON_SUBJECTS) + "\n\n"
                                "**" + br + " specific:**\n" + "\n".join(f"- {s}" for s in BRANCH_SUBJECTS.get(br, [])))
                    elif any(w in lower for w in ["exam","tip","strategy","prepare"]):
                        first_branch_subj = BRANCH_SUBJECTS.get(br, ["your core subject"])[0]
                        resp = ("**Exam Prep Strategy for " + br + "**\n\n"
                                "1. **Triage by attendance** — below-75% subjects go first.\n"
                                "2. **PYQ analysis** — last 5 years covers ~70% of patterns.\n"
                                "3. **Block schedule** — 2-hour deep-work slots in the planner.\n"
                                "4. **Group study** — 3-person group for " + first_branch_subj + ".\n"
                                "5. **ERP deadlines** — check assignment submissions weekly.")
                    else:
                        first_name = st.session_state.student_name.split()[0]
                        resp = ("I'm AskMNIT — built for **" + first_name + "** · **" + br + "**.\n\n"
                                "| Topic | Try asking… |\n|---|---|\n"
                                "| 📊 Attendance | _Analyse my attendance_ |\n"
                                "| 📅 Schedule | _What's next today?_ |\n"
                                "| 📂 PYQs | _Find PYQs for my branch_ |\n"
                                "| 💰 Fees | _Check fee due date_ |\n"
                                "| 🎯 Exams | _Give me an exam prep strategy_ |")

                    st.markdown(resp)
                    st.session_state.chat_messages.append({"role": "assistant", "content": resp})
            st.session_state.chat_pending = False
            st.rerun()

        if prompt := st.chat_input("Ask about attendance, schedule, PYQs, fees, exams…", key="chat_input_active"):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            st.session_state.chat_pending = True
            st.rerun()

    st.stop()


###############################################################################
#  DASHBOARD VIEW
###############################################################################

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
NAV_ITEMS = [
    ("⬡","My Dashboard"), ("📅","My Schedule"), ("📚","Academics"),
    ("📝","Study Material"), ("📂","PYQs"), ("💰","Fee Portal"), ("🍱","Mess Menu"),
]

with st.sidebar:
    st.markdown(
        '<div style="padding:18px 14px 14px;border-bottom:1px solid rgba(59,130,246,0.14);">'
        '<div style="display:flex;align-items:center;gap:9px;">'
        '<div style="width:30px;height:30px;border-radius:7px;'
        'background:linear-gradient(135deg,#2563EB,#4F46E5);'
        'display:flex;align-items:center;justify-content:center;'
        'font-size:0.9rem;font-weight:700;color:white;'
        'box-shadow:0 3px 12px rgba(37,99,235,0.28);">A</div>'
        '<div>'
        '<div style="font-family:\'DM Mono\',monospace;font-size:0.85rem;color:#E2E8F0;">AskMNIT</div>'
        '<div style="font-size:0.56rem;color:rgba(148,163,184,.40);margin-top:1px;">Student Portal</div>'
        '</div></div></div>',
        unsafe_allow_html=True,
    )

    bh = branch_hex(st.session_state.branch)
    st.markdown(
        '<div style="padding:8px 12px 4px;">'
        '<span style="font-size:0.60rem;font-weight:700;padding:2px 9px;'
        'background:rgba(255,255,255,0.05);border:1px solid ' + bh + '44;'
        'border-radius:5px;color:' + bh + ';letter-spacing:0.4px;">'
        + st.session_state.branch + '</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    for icon, label in NAV_ITEMS:
        is_active = st.session_state.nav_page == label
        css = "nav-btn-active" if is_active else "nav-btn"
        st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
        if st.button(f"{icon}  {label}", key="nav_" + label, use_container_width=True):
            st.session_state.nav_page = label
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div style="position:fixed;bottom:18px;width:182px;'
        'padding-top:10px;border-top:1px solid rgba(255,255,255,0.06);">',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("🚪  Logout", key="sidebar_logout", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PLACEHOLDER PAGES
# ─────────────────────────────────────────────────────────────────────────────
dash_page = st.session_state.nav_page
if dash_page != "My Dashboard":
    PMETA = {
        "My Schedule":    ("📅","My Schedule",    "Weekly timetable renders here."),
        "Academics":      ("📚","Academics",       "Grades and CGPA records render here."),
        "Study Material": ("📝","Study Material",  "Uploaded notes render here."),
        "PYQs":           ("📂","PYQs",            "Previous year papers render here."),
        "Fee Portal":     ("💰","Fee Portal",      "Fee dues and receipts render here."),
        "Mess Menu":      ("🍱","Mess Menu",       "Weekly hostel menu renders here."),
    }
    icon, title, desc = PMETA.get(dash_page, ("📄", dash_page, "Coming soon."))
    st.markdown(
        '<div style="padding:24px;">'
        '<div style="display:flex;align-items:center;gap:10px;'
        'border-bottom:1px solid rgba(255,255,255,0.06);padding-bottom:14px;margin-bottom:24px;">'
        '<span style="font-size:1.2rem;">' + icon + '</span>'
        '<span style="font-family:\'DM Mono\',monospace;font-size:0.95rem;color:#E2E8F0;">'
        + title.upper() + '</span></div>'
        '<div style="background:linear-gradient(160deg,#0B1120,#060A12);'
        'border:1px dashed rgba(59,130,246,0.18);border-radius:16px;'
        'padding:60px 40px;text-align:center;">'
        '<div style="font-size:2.8rem;margin-bottom:14px;opacity:.26;">' + icon + '</div>'
        '<div style="font-family:\'DM Mono\',monospace;font-size:0.88rem;'
        'color:#E2E8F0;margin-bottom:8px;">' + title.upper() + '</div>'
        '<div style="font-size:0.76rem;color:rgba(148,163,184,.44);'
        'max-width:280px;margin:0 auto;line-height:1.65;">' + desc + '</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# MY DASHBOARD — content wrapper
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div style='padding:0 22px 80px;'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TOP HEADER BAR
# ══════════════════════════════════════════════════════════════════════════════
h_logo, h_mid, h_right = st.columns([2, 4, 3])

with h_logo:
    st.markdown(
        '<div style="display:flex;align-items:center;gap:8px;padding:13px 0 9px;">'
        '<div style="width:30px;height:30px;border-radius:7px;'
        'background:linear-gradient(135deg,#2563EB,#4F46E5);'
        'display:flex;align-items:center;justify-content:center;'
        'font-size:0.85rem;font-weight:700;color:white;">M</div>'
        '<div>'
        '<div style="font-family:\'DM Mono\',monospace;font-size:0.76rem;color:#E2E8F0;">MNIT Jaipur</div>'
        '<div style="font-size:0.52rem;color:rgba(148,163,184,.36);">[ MNIT LOGO ]</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

with h_mid:
    now_str = datetime.datetime.now().strftime("%a, %d %b %Y  ·  %H:%M")
    st.markdown(
        '<div style="padding:13px 0 9px;text-align:center;">'
        '<span style="font-family:\'DM Mono\',monospace;font-size:0.76rem;'
        'color:#60A5FA;letter-spacing:0.8px;">MY DASHBOARD</span>'
        '<br><span style="font-size:0.57rem;color:rgba(148,163,184,.38);">' + now_str + '</span>'
        '</div>',
        unsafe_allow_html=True,
    )

with h_right:
    # Notifications icon + Circular profile pic + Settings Popover
    init_str = initials(st.session_state.student_name)
    pic_b64  = st.session_state.profile_pic_b64

    notif_html = (
        '<div style="width:30px;height:30px;border-radius:7px;'
        'background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);'
        'display:flex;align-items:center;justify-content:center;font-size:0.86rem;'
        'position:relative;cursor:pointer;">&#128276;'
        '<span style="position:absolute;top:-2px;right:-2px;width:7px;height:7px;'
        'border-radius:50%;background:#EF4444;border:1.5px solid #060A12;"></span>'
        '</div>'
    )

    if pic_b64:
        avatar_html = (
            '<div style="width:32px;height:32px;border-radius:50%;overflow:hidden;'
            'border:2px solid #3B82F6;box-shadow:0 0 0 2px rgba(59,130,246,0.25);'
            'flex-shrink:0;">'
            '<img src="' + pic_b64 + '" style="width:100%;height:100%;object-fit:cover;" />'
            '</div>'
        )
    else:
        avatar_html = (
            '<div style="width:32px;height:32px;border-radius:50%;'
            'background:linear-gradient(135deg,#2563EB,#4F46E5);'
            'display:flex;align-items:center;justify-content:center;'
            'font-size:0.66rem;font-weight:700;color:white;'
            'font-family:\'DM Mono\',monospace;'
            'border:2px solid rgba(59,130,246,0.40);flex-shrink:0;">'
            + init_str + '</div>'
        )

    notif_col, avatar_col, menu_col = st.columns([1, 1, 2])

    with notif_col:
        st.markdown(
            '<div style="padding:13px 0 9px;display:flex;justify-content:flex-end;">'
            + notif_html + '</div>',
            unsafe_allow_html=True,
        )
    with avatar_col:
        st.markdown(
            '<div style="padding:13px 0 9px;display:flex;justify-content:center;">'
            + avatar_html + '</div>',
            unsafe_allow_html=True,
        )
    with menu_col:
        # ── TOP-RIGHT SETTINGS MENU via st.popover ────────────────────────
        st.markdown("<div style='padding:9px 0 0;'>", unsafe_allow_html=True)
        with st.popover("⚙️ Menu", use_container_width=True):
            st.markdown(
                '<div style="font-family:\'DM Mono\',monospace;font-size:0.58rem;'
                'color:rgba(148,163,184,.45);text-transform:uppercase;'
                'letter-spacing:1.2px;margin-bottom:10px;">Quick Actions</div>',
                unsafe_allow_html=True,
            )

            # 1. Update Profile
            st.markdown('<div class="settings-menu-btn">', unsafe_allow_html=True)
            if st.button("👤  Update Profile", key="menu_profile", use_container_width=True):
                st.session_state.settings_mode = "profile"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

            # 2. Upload Weekly Schedule
            st.markdown('<div class="settings-menu-btn">', unsafe_allow_html=True)
            if st.button("📅  Upload Weekly Schedule", key="menu_schedule", use_container_width=True):
                st.session_state.settings_mode = "schedule"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

            # 3. ERP Login — opens in new tab via HTML anchor
            st.markdown(
                '<a href="https://mniterp.org/mniterp/" target="_blank" '
                'rel="noopener noreferrer" style="text-decoration:none;">'
                '<div style="background:linear-gradient(135deg,#065F46,#10B981);'
                'color:white;font-family:\'Outfit\',sans-serif;font-weight:700;'
                'font-size:0.82rem;padding:9px 16px;border-radius:9px;'
                'text-align:center;cursor:pointer;'
                'box-shadow:0 3px 12px rgba(16,185,129,0.22);'
                'transition:opacity 0.15s;">'
                '🔗  ERP — Login'
                '</div></a>',
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div style="height:1px;background:linear-gradient(90deg,'
    'transparent,rgba(59,130,246,0.36),rgba(34,211,238,0.18),transparent);'
    'margin-bottom:14px;"></div>',
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# SETTINGS PANELS (shown below header when triggered from Menu)
# ──────────────────────────────────────────────────────────────────────────────
if st.session_state.settings_mode == "profile":
    with st.expander("👤  Update Profile", expanded=True):
        st.markdown(
            '<div style="font-family:\'DM Mono\',monospace;font-size:0.58rem;'
            'color:rgba(148,163,184,.40);text-transform:uppercase;'
            'letter-spacing:1.2px;margin-bottom:10px;">// EDIT PROFILE</div>',
            unsafe_allow_html=True,
        )
        p1, p2 = st.columns(2)
        with p1:
            new_name = st.text_input("Full Name",  value=st.session_state.student_name, key="ep_name")
            new_cid  = st.text_input("College ID", value=st.session_state.college_id,   key="ep_cid")
        with p2:
            new_sem = st.selectbox("Semester", SEMESTERS,
                                    index=SEMESTERS.index(st.session_state.semester)
                                          if st.session_state.semester in SEMESTERS else 0,
                                    key="ep_sem")
            new_br  = st.selectbox("Branch", BRANCHES,
                                    index=BRANCHES.index(st.session_state.branch)
                                          if st.session_state.branch in BRANCHES else 0,
                                    key="ep_branch")

        st.markdown(
            '<div style="font-size:0.60rem;color:rgba(148,163,184,.44);'
            'text-transform:uppercase;letter-spacing:0.7px;font-weight:600;'
            'margin-top:8px;margin-bottom:4px;">Profile Picture</div>',
            unsafe_allow_html=True,
        )
        pic_file = st.file_uploader(
            "", type=["png","jpg","jpeg","webp"], key="pic_uploader",
            label_visibility="collapsed"
        )
        if pic_file:
            st.session_state.profile_pic_b64 = img_to_b64(pic_file)

        # Preview circular
        if st.session_state.profile_pic_b64:
            st.markdown(
                '<div style="margin:8px 0;">'
                '<div style="font-size:0.60rem;color:rgba(148,163,184,.40);'
                'margin-bottom:4px;text-transform:uppercase;letter-spacing:0.7px;">Preview</div>'
                '<div style="width:64px;height:64px;border-radius:50%;overflow:hidden;'
                'border:2px solid #3B82F6;box-shadow:0 0 0 3px rgba(59,130,246,0.20);">'
                '<img src="' + st.session_state.profile_pic_b64 + '" '
                'style="width:100%;height:100%;object-fit:cover;" />'
                '</div></div>',
                unsafe_allow_html=True,
            )

        sv1, sv2, _ = st.columns([1, 1, 3])
        with sv1:
            if st.button("💾 Save Profile", key="save_profile_btn", use_container_width=True):
                branch_changed = new_br != st.session_state.branch
                st.session_state.student_name = new_name
                st.session_state.college_id   = new_cid
                st.session_state.semester      = new_sem
                st.session_state.branch        = new_br
                if branch_changed:
                    old_att = st.session_state.attendance
                    st.session_state.attendance = {
                        s: old_att.get(s, {"present": 0, "total": 0})
                        for s in subjects_for_branch(new_br)
                    }
                st.session_state.settings_mode = None
                st.rerun()
        with sv2:
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("Cancel", key="cancel_profile_btn", use_container_width=True):
                st.session_state.settings_mode = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.settings_mode == "schedule":
    with st.expander("📅  Upload Weekly Schedule", expanded=True):
        st.markdown(
            '<div style="font-family:\'DM Mono\',monospace;font-size:0.58rem;'
            'color:rgba(148,163,184,.40);text-transform:uppercase;'
            'letter-spacing:1.2px;margin-bottom:10px;">// WEEKLY SCHEDULE PDF</div>',
            unsafe_allow_html=True,
        )
        if st.session_state.schedule_loaded:
            st.markdown(
                '<div style="background:rgba(16,185,129,.07);'
                'border:1px solid rgba(16,185,129,.20);border-radius:9px;'
                'padding:8px 12px;margin-bottom:10px;font-size:0.74rem;color:#34D399;">'
                '&#128196; Currently loaded: <b>' + st.session_state.pdf_filename + '</b> — '
                'this template repeats every week until you upload a new one.'
                '</div>',
                unsafe_allow_html=True,
            )
        uploaded_pdf = st.file_uploader(
            "", type=["pdf"], key="pdf_up", label_visibility="collapsed"
        )
        if uploaded_pdf is not None:
            with st.spinner("Analysing schedule PDF…"):
                extracted = process_schedule_pdf(uploaded_pdf, st.session_state.branch)
            st.session_state.full_schedule   = extracted
            st.session_state.schedule_loaded = True
            st.session_state.pdf_filename    = uploaded_pdf.name
            st.success("Loaded: " + uploaded_pdf.name + " — schedule set as weekly template.")

        sc1, sc2, _ = st.columns([1, 1, 3])
        with sc1:
            if st.button("Done", key="done_schedule_btn", use_container_width=True):
                st.session_state.settings_mode = None
                st.rerun()
        with sc2:
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("Cancel", key="cancel_sched_btn", use_container_width=True):
                st.session_state.settings_mode = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PINNED NOTE BANNER — displayed at very top of dashboard content
# ══════════════════════════════════════════════════════════════════════════════
pinned_notes = [n for n in st.session_state.notes_list if n["pinned"]]

if pinned_notes:
    for pi, pnote in enumerate(pinned_notes):
        note_text = pnote["text"]
        note_idx  = next(
            (i for i, n in enumerate(st.session_state.notes_list) if n["text"] == note_text and n["pinned"]),
            None
        )
        pcol1, pcol2 = st.columns([8, 1])
        with pcol1:
            st.markdown(
                '<div class="pinned-note-card" style="'
                'background:linear-gradient(135deg,rgba(245,158,11,0.10),rgba(245,158,11,0.04));'
                'border:1px solid rgba(245,158,11,0.40);'
                'border-left:4px solid #F59E0B;'
                'border-radius:12px;padding:13px 16px;margin-bottom:8px;'
                'display:flex;align-items:center;gap:10px;">'
                '<span style="font-size:1.1rem;">📌</span>'
                '<div style="flex:1;">'
                '<div style="font-size:0.60rem;font-weight:700;color:#FCD34D;'
                'text-transform:uppercase;letter-spacing:1px;margin-bottom:2px;">Pinned Note</div>'
                '<div style="font-size:0.88rem;font-weight:600;color:#FDE68A;line-height:1.5;">'
                + note_text + '</div>'
                '</div></div>',
                unsafe_allow_html=True,
            )
        with pcol2:
            st.markdown("<div style='padding-top:4px;'>", unsafe_allow_html=True)
            st.markdown('<div class="unpin-btn">', unsafe_allow_html=True)
            if st.button("✕ Unpin", key="unpin_" + str(pi), use_container_width=True):
                if note_idx is not None:
                    st.session_state.notes_list[note_idx]["pinned"] = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ROW 1 — PROFILE CARD  +  ATTENDANCE METER
# ══════════════════════════════════════════════════════════════════════════════
c_profile, c_att = st.columns([1, 1.9], gap="large")

with c_profile:
    st.markdown(
        '<div style="background:linear-gradient(160deg,#0B1120,#070D1C);'
        'border:1px solid rgba(59,130,246,0.22);border-radius:16px;'
        'padding:18px 18px 14px;">'
        '<div style="font-family:\'DM Mono\',monospace;font-size:0.56rem;'
        'color:rgba(148,163,184,.40);text-transform:uppercase;'
        'letter-spacing:1.4px;margin-bottom:12px;">// STUDENT PROFILE</div>',
        unsafe_allow_html=True,
    )

    init_str   = initials(st.session_state.student_name)
    bh_val     = branch_hex(st.session_state.branch)
    att_all    = st.session_state.attendance
    ov_pct_val = overall_pct(att_all)
    ov_c       = att_color(ov_pct_val)
    n_subj     = len(att_all)
    low_cnt    = sum(1 for r in att_all.values() if att_pct(r) < 75 and r["total"] > 0)
    pic_b64    = st.session_state.profile_pic_b64

    if pic_b64:
        avatar_big = (
            '<div style="width:52px;height:52px;border-radius:50%;overflow:hidden;'
            'border:2px solid #3B82F6;box-shadow:0 4px 14px rgba(37,99,235,0.28);'
            'flex-shrink:0;">'
            '<img src="' + pic_b64 + '" style="width:100%;height:100%;object-fit:cover;" />'
            '</div>'
        )
    else:
        avatar_big = (
            '<div style="width:52px;height:52px;border-radius:50%;flex-shrink:0;'
            'background:linear-gradient(135deg,#2563EB,#4F46E5);'
            'display:flex;align-items:center;justify-content:center;'
            'font-family:\'DM Mono\',monospace;font-size:1.0rem;color:white;'
            'border:2px solid rgba(59,130,246,0.40);'
            'box-shadow:0 4px 14px rgba(37,99,235,0.28);">'
            + init_str + '</div>'
        )

    st.markdown(
        '<div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">'
        + avatar_big +
        '<div style="min-width:0;flex:1;">'
        '<div style="font-weight:700;font-size:0.94rem;color:#E2E8F0;'
        'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'
        'font-family:\'Outfit\',sans-serif;margin-bottom:2px;">'
        + st.session_state.student_name + '</div>'
        '<div style="font-family:\'DM Mono\',monospace;font-size:0.61rem;'
        'color:rgba(148,163,184,.50);">' + st.session_state.college_id + '</div>'
        '<div style="display:flex;gap:5px;flex-wrap:wrap;margin-top:6px;">'
        '<span style="font-size:0.59rem;padding:2px 8px;border-radius:4px;'
        'background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.09);'
        'color:rgba(186,230,253,.62);">' + st.session_state.semester + '</span>'
        '<span style="font-size:0.59rem;padding:2px 8px;border-radius:4px;'
        'background:rgba(255,255,255,.05);border:1px solid ' + bh_val + '44;'
        'color:' + bh_val + ';font-weight:700;">' + st.session_state.branch + '</span>'
        '</div></div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;'
        'gap:6px;margin-bottom:12px;">' +
        ''.join(
            '<div style="background:rgba(255,255,255,0.03);'
            'border:1px solid rgba(255,255,255,0.06);'
            'border-radius:8px;padding:8px 9px;text-align:center;">'
            '<div style="font-family:\'DM Mono\',monospace;font-size:0.88rem;'
            'font-weight:600;color:' + vc + ';margin-bottom:1px;">' + str(vv) + '</div>'
            '<div style="font-size:0.55rem;color:rgba(148,163,184,.40);'
            'text-transform:uppercase;letter-spacing:0.5px;">' + lb + '</div>'
            '</div>'
            for vv, vc, lb in [
                (str(ov_pct_val) + "%", ov_c, "Overall"),
                (n_subj, "#60A5FA", "Subjects"),
                (low_cnt, "#EF4444" if low_cnt else "#10B981", "Low Att"),
            ]
        ) + '</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.schedule_loaded:
        st.markdown(
            '<div style="background:rgba(16,185,129,.07);'
            'border:1px solid rgba(16,185,129,.18);border-radius:7px;'
            'padding:5px 10px;margin-bottom:8px;font-size:0.66rem;'
            'color:#34D399;display:flex;gap:5px;align-items:center;">'
            '&#128196; ' + st.session_state.pdf_filename + '</div>',
            unsafe_allow_html=True,
        )

    # Open AI Chat
    st.markdown('<div class="open-chat-btn">', unsafe_allow_html=True)
    if st.button("🤖  AskMNIT AI", key="open_chat_from_dash", use_container_width=True):
        st.session_state.view          = "chat"
        st.session_state.chat_messages = []
        st.session_state.chat_pending  = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ── ATTENDANCE METER ──────────────────────────────────────────────────────────
with c_att:
    att_all  = st.session_state.attendance
    ov       = overall_pct(att_all)
    s_lbl, s_tc, s_bg = status_badge(ov)
    ov_c     = att_color(ov)

    st.markdown(
        '<div style="background:linear-gradient(160deg,#0B1120,#070D1C);'
        'border:1px solid rgba(255,255,255,0.07);border-radius:16px;'
        'padding:18px 18px 14px;">'
        '<div style="display:flex;align-items:center;justify-content:space-between;'
        'margin-bottom:12px;">'
        '<span style="font-family:\'DM Mono\',monospace;font-size:0.56rem;'
        'color:rgba(148,163,184,.40);text-transform:uppercase;letter-spacing:1.4px;">'
        '// ATTENDANCE METER</span>'
        '<span style="font-size:0.63rem;font-weight:700;padding:3px 10px;'
        'border-radius:999px;background:' + s_bg + ';color:' + s_tc + ';'
        'border:1px solid ' + s_tc + '44;">' + s_lbl + '</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="display:flex;align-items:center;gap:14px;margin-bottom:10px;">'
        '<div style="font-family:\'DM Mono\',monospace;font-size:2.3rem;'
        'color:' + ov_c + ';letter-spacing:-2px;line-height:1;">'
        + str(ov) + '<span style="font-size:1.0rem;">%</span></div>'
        '<div>'
        '<div style="font-size:0.67rem;color:rgba(148,163,184,.48);">Overall Attendance</div>'
        '<div style="font-size:0.59rem;color:rgba(100,116,139,.40);margin-top:2px;">'
        'Min 75%  ·  ' + str(len(att_all)) + ' subjects  ·  ' + st.session_state.branch
        + '</div></div></div>',
        unsafe_allow_html=True,
    )
    st.progress(min(ov / 100, 1.0))
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    def render_subj_rows(subj_list: list[str], prefix: str):
        for i, subj in enumerate(subj_list):
            if subj not in att_all:
                continue
            rec  = att_all[subj]
            spct = att_pct(rec)
            sc   = att_color(spct)
            kp   = prefix + "_p_" + str(i)
            ka   = prefix + "_a_" + str(i)
            st.markdown(
                '<div style="background:rgba(255,255,255,0.02);'
                'border:1px solid rgba(255,255,255,0.055);'
                'border-radius:10px;padding:8px 10px;margin-bottom:6px;">',
                unsafe_allow_html=True,
            )
            r1, r2, r3, r4 = st.columns([4, 1.5, 1.1, 1.1])
            with r1:
                st.markdown(
                    '<div style="font-size:0.76rem;font-weight:600;color:#E2E8F0;'
                    'margin-bottom:2px;white-space:nowrap;overflow:hidden;'
                    'text-overflow:ellipsis;">' + subj + '</div>'
                    '<div style="font-family:\'DM Mono\',monospace;font-size:0.61rem;'
                    'color:rgba(148,163,184,.44);">'
                    + str(rec["present"]) + '/' + str(rec["total"]) + '</div>',
                    unsafe_allow_html=True,
                )
                st.progress(min(spct / 100, 1.0))
            with r2:
                st.markdown(
                    '<div style="text-align:right;font-family:\'DM Mono\',monospace;'
                    'font-weight:600;font-size:1.0rem;color:' + sc + ';padding-top:4px;">'
                    + str(spct) + '%</div>',
                    unsafe_allow_html=True,
                )
            with r3:
                st.markdown('<div class="present-btn">', unsafe_allow_html=True)
                if st.button("✓ P", key=kp, use_container_width=True):
                    st.session_state.attendance[subj]["present"] += 1
                    st.session_state.attendance[subj]["total"]   += 1
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with r4:
                st.markdown('<div class="absent-btn">', unsafe_allow_html=True)
                if st.button("✗ A", key=ka, use_container_width=True):
                    st.session_state.attendance[subj]["total"] += 1
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    branch_only = BRANCH_SUBJECTS.get(st.session_state.branch, [])
    with st.expander("📘  Common Subjects  (" + str(len(COMMON_SUBJECTS)) + ")", expanded=True):
        render_subj_rows(COMMON_SUBJECTS, "cmn")
    if branch_only:
        with st.expander("🔬  " + st.session_state.branch + " Subjects  ("
                         + str(len(branch_only)) + ")", expanded=True):
            render_subj_rows(branch_only, "brnch")

    st.markdown("</div>", unsafe_allow_html=True)


st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ROW 2 — TODAY'S CLASS SCHEDULE (modern card layout)
# ══════════════════════════════════════════════════════════════════════════════
today_name = datetime.datetime.now().strftime("%A")
now_hm     = datetime.datetime.now().hour * 60 + datetime.datetime.now().minute

st.markdown(
    '<div style="background:linear-gradient(160deg,#0B1120,#070D1C);'
    'border:1px solid rgba(255,255,255,0.07);border-radius:16px;'
    'padding:18px 18px 14px;margin-bottom:14px;">'
    '<div style="display:flex;align-items:center;justify-content:space-between;'
    'margin-bottom:14px;">'
    '<span style="font-family:\'DM Mono\',monospace;font-size:0.56rem;'
    'color:rgba(148,163,184,.40);text-transform:uppercase;letter-spacing:1.4px;">'
    "// TODAY'S CLASS SCHEDULE</span>"
    '<span style="font-family:\'DM Mono\',monospace;font-size:0.62rem;'
    'color:rgba(96,165,250,.65);">' + today_name.upper() + '</span>'
    '</div>',
    unsafe_allow_html=True,
)

if st.session_state.schedule_loaded:
    today_slots = get_today_slots(st.session_state.full_schedule)
    nxt = get_next_class(today_slots)

    # Next-class countdown banner
    if nxt:
        mins   = nxt["minutes_away"]
        hrs    = mins // 60
        rem    = mins % 60
        cd_str = (f"{hrs}h {rem}m" if hrs else f"{rem} min") + " away"
        urg_c  = "#EF4444" if mins < 15 else "#F59E0B" if mins < 45 else "#22D3EE"
        st.markdown(
            '<div style="background:linear-gradient(90deg,'
            'rgba(34,211,238,.06),rgba(37,99,235,.04));'
            'border:1px solid rgba(34,211,238,.18);border-radius:10px;'
            'padding:10px 16px;margin-bottom:14px;'
            'display:flex;align-items:center;justify-content:space-between;">'
            '<div>'
            '<div style="font-size:0.57rem;color:rgba(148,163,184,.46);'
            'text-transform:uppercase;letter-spacing:0.8px;margin-bottom:2px;">Next Class</div>'
            '<div style="font-weight:700;font-size:0.86rem;color:#E2E8F0;">'
            + nxt["subject"]
            + '  <span style="font-size:0.67rem;color:rgba(148,163,184,.46);">'
            + nxt["room"] + '</span></div>'
            '</div>'
            '<div style="font-family:\'DM Mono\',monospace;font-size:0.96rem;'
            'font-weight:600;color:' + urg_c + ';text-align:right;">'
            + cd_str
            + '<div style="font-size:0.57rem;color:rgba(148,163,184,.42);'
            'font-weight:400;margin-top:1px;">'
            + fmt_time(nxt["time_start"]) + ' – ' + fmt_time(nxt["time_end"])
            + '</div></div></div>',
            unsafe_allow_html=True,
        )

    # Modern class cards — 2-3 per row using columns
    if today_slots:
        max_cols = 3
        rows = [today_slots[i:i+max_cols] for i in range(0, len(today_slots), max_cols)]
        for row in rows:
            cols = st.columns(len(row))
            for ci, (col, slot) in enumerate(zip(cols, row)):
                sh, sm   = map(int, slot["time_start"].split(":"))
                is_past  = (sh * 60 + sm) < now_hm
                tc       = TYPE_COLORS.get(slot["type"], "#60A5FA")
                is_next  = (nxt is not None and slot["time_start"] == nxt["time_start"]
                            and slot["subject"] == nxt["subject"])

                # Card accent: neon left border, dimmed if past
                border_color = tc if not is_past else "rgba(255,255,255,0.06)"
                card_bg      = ("linear-gradient(160deg,rgba(34,211,238,0.06),"
                                "rgba(37,99,235,0.03))" if is_next
                                else "rgba(255,255,255,0.02)" if not is_past
                                else "rgba(255,255,255,0.01)")

                time_color   = "#E2E8F0" if not is_past else "rgba(148,163,184,0.32)"
                subj_color   = "#F1F5F9" if not is_past else "rgba(148,163,184,0.28)"
                badge_opacity = "1" if not is_past else "0.35"

                with col:
                    st.markdown(
                        '<div style="background:' + card_bg + ';'
                        'border:1px solid ' + border_color + ';'
                        'border-left:3px solid ' + border_color + ';'
                        'border-radius:12px;padding:13px 14px;margin-bottom:8px;'
                        'position:relative;overflow:hidden;">'

                        # Colored dot indicator
                        + '<div style="position:absolute;top:10px;right:10px;'
                        'width:7px;height:7px;border-radius:50%;'
                        'background:' + tc + ';opacity:' + badge_opacity + ';'
                        + ('box-shadow:0 0 6px ' + tc + ';' if is_next else '') + '"></div>'

                        # Time block — bold and clearly separated
                        + '<div style="font-family:\'DM Mono\',monospace;'
                        'font-size:0.78rem;font-weight:700;color:' + time_color + ';'
                        'margin-bottom:6px;line-height:1.2;">'
                        + fmt_time(slot["time_start"]) + '<br>'
                        '<span style="font-size:0.62rem;font-weight:400;'
                        'color:rgba(148,163,184,0.45);">– ' + fmt_time(slot["time_end"]) + '</span>'
                        '</div>'

                        # Subject name
                        + '<div style="font-size:0.82rem;font-weight:700;'
                        'color:' + subj_color + ';margin-bottom:5px;line-height:1.3;">'
                        + slot["subject"] + '</div>'

                        # Room + type badge
                        + '<div style="display:flex;align-items:center;gap:6px;">'
                        + '<span style="font-size:0.62rem;color:rgba(148,163,184,.48);">'
                        + slot["room"] + '</span>'
                        + '<span style="font-size:0.58rem;padding:1px 7px;border-radius:4px;'
                        'background:' + tc + '1A;color:' + tc + ';font-weight:600;'
                        'opacity:' + badge_opacity + ';">' + slot["type"] + '</span>'
                        + ('  <span style="font-size:0.58rem;color:#22D3EE;font-weight:700;">'
                           '● NEXT</span>' if is_next else '')
                        + '</div>'

                        + ('  <div style="font-size:0.58rem;color:rgba(148,163,184,.28);'
                           'margin-top:4px;text-decoration:line-through;">Done</div>'
                           if is_past else '')

                        + '</div>',
                        unsafe_allow_html=True,
                    )
    else:
        st.markdown(
            '<div style="text-align:center;padding:24px;'
            'color:rgba(148,163,184,.40);font-size:0.80rem;">'
            'No classes scheduled for ' + today_name + '.</div>',
            unsafe_allow_html=True,
        )

else:
    # Manual planner (no PDF loaded)
    st.markdown(
        '<div style="background:rgba(59,130,246,.04);'
        'border:1px dashed rgba(59,130,246,.20);border-radius:9px;'
        'padding:9px 13px;margin-bottom:12px;font-size:0.73rem;'
        'color:rgba(148,163,184,.48);display:flex;gap:7px;align-items:center;">'
        '&#128196;  Use <b>⚙️ Menu → Upload Weekly Schedule</b> to activate the auto-planner.'
        '</div>',
        unsafe_allow_html=True,
    )
    MANUAL_SLOTS = [("08:00","09:00"),("09:30","10:30"),("11:00","12:00"),
                    ("12:00","13:00"),("14:00","15:00"),("15:30","16:30")]
    for st_start, st_end in MANUAL_SLOTS:
        slot_key = st_start
        override = st.session_state.planner_overrides.get(slot_key, "") if hasattr(st.session_state, 'planner_overrides') else ""
        if not hasattr(st.session_state, 'planner_overrides'):
            st.session_state.planner_overrides = {}
        override = st.session_state.planner_overrides.get(slot_key, "")

        mp1, mp2, mp3, mp4 = st.columns([1.6, 4, 0.8, 2.2])
        with mp1:
            st.markdown(
                '<div style="font-family:\'DM Mono\',monospace;font-size:0.68rem;'
                'color:#60A5FA;padding-top:10px;white-space:nowrap;font-weight:700;">'
                + fmt_time(st_start) + '<br>'
                '<span style="font-size:0.56rem;font-weight:400;color:rgba(148,163,184,.38);">'
                '– ' + fmt_time(st_end) + '</span>'
                '</div>',
                unsafe_allow_html=True,
            )
        with mp2:
            note_v = st.text_input("", value=override, placeholder="Task or note…",
                                    key="mp_" + slot_key, label_visibility="collapsed")
        with mp3:
            st.markdown('<div class="save-btn">', unsafe_allow_html=True)
            if st.button("💾", key="sv_mp_" + slot_key, use_container_width=True):
                st.session_state.planner_overrides[slot_key] = note_v
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with mp4:
            saved = st.session_state.planner_overrides.get(slot_key, "")
            if saved:
                st.markdown(
                    '<div style="font-size:0.67rem;color:#34D399;'
                    'background:rgba(16,185,129,.07);border:1px solid rgba(16,185,129,.14);'
                    'border-radius:7px;padding:4px 9px;margin-top:2px;'
                    'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'
                    '✓ ' + saved + '</div>',
                    unsafe_allow_html=True,
                )

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ROW 3 — QUICK LINKS  +  PERSONAL NOTES (with pin feature)
# ══════════════════════════════════════════════════════════════════════════════
ql_col, notes_col = st.columns([1, 1.5], gap="large")

with ql_col:
    st.markdown(
        '<div style="background:linear-gradient(160deg,#0B1120,#070D1C);'
        'border:1px solid rgba(255,255,255,0.07);border-radius:16px;'
        'padding:18px 18px 14px;height:100%;">'
        '<div style="font-family:\'DM Mono\',monospace;font-size:0.56rem;'
        'color:rgba(148,163,184,.40);text-transform:uppercase;'
        'letter-spacing:1.4px;margin-bottom:12px;">// QUICK LINKS</div>',
        unsafe_allow_html=True,
    )
    QL = [("📤","Upload Syllabus","Syllabus uploader will be enabled here."),
          ("🔗","Add PYQ Link",   "PYQ link manager will open here."),
          ("🔍","Library Search", "Library search will open here.")]
    st.markdown('<div class="ql-btn">', unsafe_allow_html=True)
    for ico, lbl, fb in QL:
        if st.button(ico + "  " + lbl, key="ql_" + lbl, use_container_width=True):
            st.session_state.ql_feedback = fb
            st.rerun()
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if st.session_state.ql_feedback:
        st.markdown(
            '<div style="background:rgba(59,130,246,.06);'
            'border:1px solid rgba(59,130,246,.18);border-radius:8px;'
            'padding:7px 11px;margin-top:7px;font-size:0.70rem;'
            'color:rgba(186,230,253,.58);line-height:1.5;">'
            + st.session_state.ql_feedback + '</div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


# ── PERSONAL NOTES WITH PIN FEATURE ──────────────────────────────────────────
with notes_col:
    st.markdown(
        '<div style="background:linear-gradient(160deg,#0B1120,#070D1C);'
        'border:1px solid rgba(255,255,255,0.07);border-radius:16px;'
        'padding:18px 18px 14px;">'
        '<div style="font-family:\'DM Mono\',monospace;font-size:0.56rem;'
        'color:rgba(148,163,184,.40);text-transform:uppercase;'
        'letter-spacing:1.4px;margin-bottom:12px;">// PERSONAL NOTES</div>',
        unsafe_allow_html=True,
    )

    # Add new note
    new_note_input = st.text_input(
        "", placeholder="Type a new note and press Enter…",
        key="new_note_input_field", label_visibility="collapsed"
    )
    add_col, _ = st.columns([1, 3])
    with add_col:
        if st.button("➕ Add Note", key="add_note_btn", use_container_width=True):
            txt = new_note_input.strip()
            if txt:
                st.session_state.notes_list.append({"text": txt, "pinned": False})
                st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Render unpinned notes
    unpinned = [(i, n) for i, n in enumerate(st.session_state.notes_list) if not n["pinned"]]

    if not unpinned:
        st.markdown(
            '<div style="font-size:0.76rem;color:rgba(148,163,184,.38);'
            'text-align:center;padding:16px;font-style:italic;">'
            'No notes yet. Add one above.</div>',
            unsafe_allow_html=True,
        )
    else:
        for i, note in unpinned:
            note_text = note["text"]
            nr1, nr2, nr3 = st.columns([5, 1.2, 1])
            with nr1:
                st.markdown(
                    '<div style="background:rgba(255,255,255,0.025);'
                    'border:1px solid rgba(255,255,255,0.07);border-radius:9px;'
                    'padding:9px 12px;margin-bottom:4px;'
                    'font-size:0.80rem;color:rgba(226,232,240,0.75);line-height:1.5;">'
                    + note_text + '</div>',
                    unsafe_allow_html=True,
                )
            with nr2:
                st.markdown('<div class="pin-btn">', unsafe_allow_html=True)
                if st.button("📌 Pin", key="pin_note_" + str(i), use_container_width=True):
                    st.session_state.notes_list[i]["pinned"] = True
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with nr3:
                st.markdown('<div class="del-btn">', unsafe_allow_html=True)
                if st.button("🗑", key="del_note_" + str(i), use_container_width=True):
                    st.session_state.notes_list.pop(i)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# Footer
st.markdown("""
<div style="text-align:center;margin-top:28px;padding:10px 0;
            border-top:1px solid rgba(255,255,255,0.05);">
    <span style="font-family:'DM Mono',monospace;font-size:0.52rem;
                 color:rgba(148,163,184,0.24);letter-spacing:1.2px;">
        ASKMNT &nbsp;·&nbsp; MNIT JAIPUR &nbsp;·&nbsp; SESSION-STATE ONLY
    </span>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
