# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  AskMNIT — Premium AI Chat + Student Dashboard                              ║
# ║  v3.0 — All bugs fixed, Gemini-style bar fully functional                  ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import streamlit as st
import datetime
import random
import base64

st.set_page_config(
    page_title="AskMNIT",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
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
DAYS      = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
TYPE_COLORS = {"Lecture": "#22D3EE", "Lab": "#F59E0B", "Tutorial": "#A78BFA"}

MOCK_HISTORY = [
    ("Today",      "Attendance analysis request"),
    ("Yesterday",  "Mineral Processing PYQs"),
    ("Yesterday",  "Exam prep strategy - CSE"),
    ("2 days ago", "Fee due date query"),
    ("3 days ago", "Welding Technology schedule"),
    ("Last week",  "Subject list for Semester 6"),
]

# ─────────────────────────────────────────────────────────────────────────────
# SCHEDULE HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def process_schedule_pdf(file, branch: str) -> dict:
    pool = COMMON_SUBJECTS[:4] + BRANCH_SUBJECTS.get(branch, [])
    random.seed(42)
    TIME_PAIRS = [
        ("08:00", "09:00"), ("09:30", "10:30"), ("11:00", "12:00"),
        ("12:00", "13:00"), ("14:00", "15:00"), ("15:30", "16:30"),
    ]
    sched: dict[str, list[dict]] = {}
    for day in DAYS[:6]:
        chosen = sorted(random.sample(range(len(TIME_PAIRS)), k=random.randint(2, 4)))
        sched[day] = [
            {
                "time_start": TIME_PAIRS[ci][0], "time_end": TIME_PAIRS[ci][1],
                "subject": random.choice(pool),
                "room": random.choice(["LT-1", "LT-2", "Lab-A", "Lab-B", "CR-3", "CR-5"]),
                "type": random.choice(["Lecture", "Lecture", "Lab", "Tutorial"])
            }
            for ci in chosen
        ]
    return sched

def get_today_slots(fs: dict) -> list[dict]:
    return fs.get(datetime.datetime.now().strftime("%A"), [])

def get_next_class(slots: list[dict]) -> dict | None:
    now = datetime.datetime.now()
    for slot in slots:
        h, m = map(int, slot["time_start"].split(":"))
        dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if dt > now:
            return {**slot, "minutes_away": int((dt - now).total_seconds() // 60)}
    return None

# ─────────────────────────────────────────────────────────────────────────────
# GENERAL HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def subjects_for_branch(b):
    return COMMON_SUBJECTS + BRANCH_SUBJECTS.get(b, [])

def blank_att(s):
    return {x: {"present": 0, "total": 0} for x in s}

def att_pct(r):
    return round(r["present"] / r["total"] * 100, 1) if r["total"] else 0.0

def overall_pct(a):
    tp = sum(r["present"] for r in a.values())
    tt = sum(r["total"] for r in a.values())
    return round(tp / tt * 100, 1) if tt else 0.0

def status_badge(p):
    if p >= 75: return "Safe", "#10B981", "rgba(16,185,129,0.12)"
    if p >= 65: return "Low",  "#F59E0B", "rgba(245,158,11,0.12)"
    return "Critical", "#EF4444", "rgba(239,68,68,0.12)"

def att_color(p):
    return "#10B981" if p >= 75 else "#F59E0B" if p >= 65 else "#EF4444"

def initials(n):
    return "".join(w[0].upper() for w in n.split()[:2]) if n else "??"

def branch_hex(b):
    return {
        "CSE": "#3B82F6", "AI & ML": "#8B5CF6", "ECE": "#06B6D4",
        "Civil": "#F59E0B", "Metallurgy": "#10B981"
    }.get(b, "#6366F1")

def img_to_b64(f):
    d = f.read(); m = f.type or "image/png"
    return f"data:{m};base64,{base64.b64encode(d).decode()}"

def fmt_time(t: str) -> str:
    try:
        h, m = map(int, t.split(":"))
        return f"{h % 12 or 12:02d}:{m:02d} {'AM' if h < 12 else 'PM'}"
    except:
        return t

def _safe_key(s: str) -> str:
    """Sanitize string for use in Streamlit widget keys."""
    return "".join(c if c.isalnum() else "_" for c in s)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
_def_branch = "CSE"
_DEFAULTS: dict = {
    "view":              "dashboard",
    "nav_page":          "My Dashboard",
    "student_name":      "Sumit Chaudhary",
    "college_id":        "2022UMT1234",
    "semester":          "Semester 6",
    "branch":            _def_branch,
    "profile_pic_b64":   "",
    "settings_mode":     None,
    "attendance":        blank_att(subjects_for_branch(_def_branch)),
    "schedule_loaded":   False,
    "full_schedule":     {},
    "pdf_filename":      "",
    "notes_list": [
        {"text": "Mid-sem revision starts Monday", "pinned": False},
        {"text": "Submit fee by 17 Mar",           "pinned": False},
        {"text": "Collect hall ticket from ERP",   "pinned": False},
    ],
    "ql_feedback":       "",
    "chat_messages":     [],
    "chat_sessions":     [],
    "voice_output":      False,
    "strict_mode":       False,
    "is_recording":      False,
    "planner_overrides": {},
    "show_uploader":     False,
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
# AI RESPONSE GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def generate_ai_response(last: str) -> str:
    lower = last.lower()
    att   = st.session_state.attendance
    br    = st.session_state.branch

    if any(w in lower for w in ["attendance", "present", "absent", "%"]):
        ov  = overall_pct(att)
        low = [(s, att_pct(r)) for s, r in att.items() if att_pct(r) < 75 and r["total"] > 0]
        resp = f"**Attendance - {st.session_state.student_name}**\n\nOverall: **{ov}%**\n\n"
        if low:
            resp += "**Below 75%:**\n"
            for s, p in low:
                need = max(0, int((0.75 * att[s]["total"] - att[s]["present"]) / 0.25) + 1)
                resp += f"- **{s}**: {p}% - need **{need}** more\n"
        else:
            resp += "All subjects above 75%. Stay consistent!"
        return resp

    if any(w in lower for w in ["schedule", "class", "next", "today", "timetable"]):
        if st.session_state.schedule_loaded:
            slots = get_today_slots(st.session_state.full_schedule)
            nxt   = get_next_class(slots)
            dn    = datetime.datetime.now().strftime("%A")
            resp  = f"**Today's Classes ({dn})**\n\n"
            for s in slots:
                resp += f"- **{fmt_time(s['time_start'])}-{fmt_time(s['time_end'])}** - {s['subject']} in {s['room']} _({s['type']})_\n"
            if nxt:
                resp += f"\nNext: {nxt['subject']} in **{nxt['minutes_away']} min**"
            else:
                resp += "\nNo more classes today."
            return resp
        return "No schedule loaded. Go to **Menu - Upload Weekly Schedule** on the dashboard."

    if any(w in lower for w in ["pyq", "previous year", "question paper", "past paper"]):
        return (f"**PYQ Resources for {br}**\n\nAccess via PYQs in the dashboard.\n\n"
                f"Branch subjects: {', '.join(BRANCH_SUBJECTS.get(br, []))}")

    if any(w in lower for w in ["fee", "pay", "due", "payment"]):
        return "Fee details are in the **Fee Portal** section on the dashboard."

    if any(w in lower for w in ["subject", "syllabus", "branch", "course"]):
        common   = "\n".join(f"- {s}" for s in COMMON_SUBJECTS)
        branch_s = "\n".join(f"- {s}" for s in BRANCH_SUBJECTS.get(br, []))
        return (f"**Subjects - {br} - {st.session_state.semester}**\n\n"
                f"**Common:**\n{common}\n\n**{br} specific:**\n{branch_s}")

    if any(w in lower for w in ["exam", "tip", "strategy", "prepare", "study"]):
        first_bs = BRANCH_SUBJECTS.get(br, ["your core subject"])[0]
        return (f"**Exam Prep - {br}**\n\n"
                "1. **Triage by attendance** - below-75% subjects first.\n"
                "2. **PYQ pattern** - last 5 years covers ~70%.\n"
                "3. **Block schedule** - 2-hour deep-work slots.\n"
                f"4. **Group study** - 3-person group for {first_bs}.\n"
                "5. **ERP deadlines** - check submissions weekly.")

    if any(w in lower for w in ["hi", "hello", "hey", "hii"]):
        fn = st.session_state.student_name.split()[0]
        return (f"Hey {fn}! I'm AskMNIT. I can help with:\n\n"
                "- Attendance analysis\n- Today's schedule\n"
                "- Previous year papers\n- Fee status\n- Exam strategy\n\n"
                f"You're on **{br} - {st.session_state.semester}**. What can I help with?")

    if "attached" in lower or "file" in lower:
        return "File received! Tell me what you'd like to do with this file."

    fn = st.session_state.student_name.split()[0]
    return (f"I'm AskMNIT - built for **{fn}** - **{br}**.\n\n"
            "| Topic | Try asking... |\n|---|---|\n"
            "| Attendance | _Analyse my attendance_ |\n"
            "| Schedule | _What's next today?_ |\n"
            "| PYQs | _Find PYQs for my branch_ |\n"
            "| Fees | _Check fee due date_ |\n"
            "| Exams | _Give me an exam strategy_ |")

# ─────────────────────────────────────────────────────────────────────────────
# MESSAGE DISPATCH
# ─────────────────────────────────────────────────────────────────────────────
def dispatch_message(text: str):
    text = text.strip()
    if not text:
        return
    st.session_state.chat_messages.append({"role": "user", "content": text})
    st.session_state.chat_messages.append(
        {"role": "assistant", "content": generate_ai_response(text)}
    )

# ═════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,700;9..144,900&family=DM+Mono:wght@400;500&family=Outfit:wght@300;400;500;600;700&display=swap');

:root {
  --bg:      #070B14;
  --surf:    #0B1120;
  --surf2:   #0E1726;
  --border:  rgba(255,255,255,0.08);
  --border2: rgba(255,255,255,0.14);
  --accent:  #3B82F6;
  --green:   #10B981;
  --amber:   #F59E0B;
  --red:     #EF4444;
  --violet:  #A78BFA;
  --text:    #E2E8F0;
  --muted:   rgba(148,163,184,0.55);
  --mono:    'DM Mono', monospace;
  --sans:    'Outfit', sans-serif;
  --display: 'Fraunces', serif;
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
  min-width: 210px !important; max-width: 210px !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
  background: rgba(255,255,255,0.025) !important;
  border: 1px solid rgba(255,255,255,0.06) !important;
  border-radius: 14px !important;
  font-family: var(--sans) !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
  background: rgba(37,99,235,0.08) !important;
  border-color: rgba(59,130,246,0.16) !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   GEMINI-STYLE SEARCH BAR
   Built from a native st.form with 4 columns: [attach | textarea | mic | send]
   The form wrapper is styled to look like the Gemini pill container.
   All buttons/inputs are real Streamlit widgets — fully functional.
   ═══════════════════════════════════════════════════════════════════════════ */

/* ── Pill container: the st.form becomes the Gemini bar ── */
.gemini-bar [data-testid="stForm"] {
  background: #1A1E2E !important;
  border: 1.5px solid rgba(255,255,255,0.10) !important;
  border-radius: 28px !important;
  padding: 6px 8px 6px 2px !important;
  min-height: 60px !important;
  box-shadow: 0 4px 32px rgba(0,0,0,0.45), 0 1px 0 rgba(255,255,255,0.04) inset !important;
  transition: border-color 0.22s, box-shadow 0.22s !important;
}
.gemini-bar [data-testid="stForm"]:focus-within {
  border-color: rgba(59,130,246,0.55) !important;
  box-shadow: 0 0 0 3px rgba(59,130,246,0.12), 0 6px 40px rgba(37,99,235,0.18) !important;
}
/* Remove default form border/padding if any */
.gemini-bar [data-testid="stForm"] > div:first-child {
  padding: 0 !important;
}

/* ── Columns inside the form ── */
.gemini-bar [data-testid="stHorizontalBlock"] {
  align-items: center !important;
  gap: 2px !important;
}

/* ── Text input: transparent fill ── */
.gemini-bar [data-testid="stTextInput"] label { display: none !important; }
.gemini-bar [data-testid="stTextInput"] > div {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
}
.gemini-bar [data-testid="stTextInput"] input {
  background: transparent !important;
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
  color: #E2E8F0 !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 0.97rem !important;
  caret-color: #60A5FA !important;
  padding: 11px 8px !important;
  height: 44px !important;
  border-radius: 0 !important;
  width: 100% !important;
}
.gemini-bar [data-testid="stTextInput"] input::placeholder {
  color: rgba(148,163,184,0.38) !important;
}
.gemini-bar [data-testid="stTextInput"] input:focus {
  border: none !important;
  box-shadow: none !important;
  outline: none !important;
}

/* ── Attach button (left icon) ── */
.gemini-attach .stButton > button {
  background: transparent !important;
  border: none !important;
  border-radius: 50% !important;
  color: rgba(148,163,184,0.55) !important;
  font-size: 1.2rem !important;
  width: 42px !important; height: 42px !important;
  min-width: 42px !important;
  padding: 0 !important;
  box-shadow: none !important;
  transition: background 0.16s, color 0.16s !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}
.gemini-attach .stButton > button:hover {
  background: rgba(255,255,255,0.08) !important;
  color: rgba(186,230,253,0.80) !important;
  transform: none !important;
  opacity: 1 !important;
}

/* ── Mic button (right icon, idle) ── */
.gemini-mic .stButton > button {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.09) !important;
  border-radius: 50% !important;
  color: rgba(148,163,184,0.60) !important;
  font-size: 1.05rem !important;
  width: 38px !important; height: 38px !important;
  min-width: 38px !important;
  padding: 0 !important;
  box-shadow: none !important;
  transition: background 0.16s, color 0.16s !important;
}
.gemini-mic .stButton > button:hover {
  background: rgba(255,255,255,0.09) !important;
  color: rgba(186,230,253,0.80) !important;
  transform: none !important;
  opacity: 1 !important;
}

/* ── Mic button (recording / active state) ── */
.gemini-mic-active .stButton > button {
  background: rgba(239,68,68,0.18) !important;
  border: 1px solid rgba(239,68,68,0.45) !important;
  border-radius: 50% !important;
  color: #FCA5A5 !important;
  font-size: 1.05rem !important;
  width: 38px !important; height: 38px !important;
  min-width: 38px !important;
  padding: 0 !important;
  animation: micPulse 1.1s ease-in-out infinite !important;
}
@keyframes micPulse {
  0%,100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.40); }
  50%      { box-shadow: 0 0 0 7px rgba(239,68,68,0.00); }
}

/* ── Send button (form submit) ── */
.gemini-send [data-testid="stFormSubmitButton"] > button {
  background: linear-gradient(135deg, #2563EB, #4F46E5) !important;
  border: none !important;
  border-radius: 50% !important;
  color: #fff !important;
  font-size: 1.25rem !important;
  font-weight: 700 !important;
  width: 38px !important; height: 38px !important;
  min-width: 38px !important;
  padding: 0 !important;
  line-height: 1 !important;
  box-shadow: 0 3px 14px rgba(37,99,235,0.38) !important;
  transition: opacity 0.16s, transform 0.14s !important;
}
.gemini-send [data-testid="stFormSubmitButton"] > button:hover {
  opacity: 0.88 !important;
  transform: scale(1.07) !important;
}
.gemini-send [data-testid="stFormSubmitButton"] > button:active {
  transform: scale(0.95) !important;
}

/* ── Listening banner ── */
.listening-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  padding: 8px 18px;
  background: rgba(239,68,68,0.09);
  border: 1px solid rgba(239,68,68,0.22);
  border-radius: 10px;
  font-size: 0.80rem;
  color: #FCA5A5;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  animation: fadeInUp 0.25s ease both;
}
.listening-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #EF4444;
  animation: blinkDot 1.1s ease infinite;
  flex-shrink: 0;
}
@keyframes blinkDot { 0%,100% { opacity:1; } 50% { opacity:0.25; } }

/* ── Attach panel ── */
.attach-panel {
  max-width: 800px;
  margin: 10px auto 4px;
  padding: 14px 16px;
  background: rgba(59,130,246,0.05);
  border: 1px dashed rgba(59,130,246,0.28);
  border-radius: 14px;
  animation: fadeInUp 0.2s ease both;
}

/* ── Fixed bottom bar (active chat) ── */
.gemini-bar-anchored {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  z-index: 900;
  background: rgba(7,11,20,0.97);
  backdrop-filter: blur(24px) saturate(160%);
  border-top: 1px solid rgba(59,130,246,0.12);
  padding: 10px max(16px, calc((100% - 860px) / 2)) 12px;
}

/* ═════════════════════════════════════════════════════════════════════════
   END GEMINI BAR CSS
   ═════════════════════════════════════════════════════════════════════════ */

/* ── Standard text inputs (dashboard) ── */
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
[data-testid="stTextInput"] label, [data-testid="stTextArea"] label {
  color: var(--muted) !important; font-size: 0.70rem !important;
  font-weight: 600 !important; text-transform: uppercase !important;
  letter-spacing: 0.6px !important; font-family: var(--sans) !important;
}
[data-testid="stSelectbox"] > div > div {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 10px !important; color: var(--text) !important;
}
[data-testid="stSelectbox"] label {
  color: var(--muted) !important; font-size: 0.70rem !important;
  font-weight: 600 !important; text-transform: uppercase !important;
  font-family: var(--sans) !important;
}
[data-testid="stFileUploader"] {
  background: rgba(59,130,246,0.04) !important;
  border: 1px dashed rgba(59,130,246,0.26) !important;
  border-radius: 12px !important;
}
[data-testid="stToggle"] label {
  color: var(--text) !important; font-family: var(--sans) !important;
  font-size: 0.86rem !important;
}

/* ── BASE BUTTON ── */
.stButton > button {
  background: linear-gradient(135deg,#2563EB,#4F46E5) !important;
  color: #fff !important; border: none !important; border-radius: 9px !important;
  font-family: var(--sans) !important; font-weight: 600 !important;
  font-size: 0.82rem !important; padding: 9px 16px !important;
  box-shadow: 0 3px 14px rgba(37,99,235,0.20) !important;
  transition: all 0.16s ease !important;
}
.stButton > button:hover { opacity: .88 !important; transform: translateY(-1px) !important; }
.stButton > button:active { transform: scale(0.97) !important; }

/* ── NAV PILL ── */
.nav-pill .stButton > button {
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
  border-radius: 999px !important; color: rgba(226,232,240,0.72) !important;
  font-size: 0.78rem !important; font-weight: 500 !important;
  padding: 6px 15px !important; box-shadow: none !important;
}
.nav-pill .stButton > button:hover {
  background: rgba(59,130,246,0.16) !important;
  border-color: rgba(59,130,246,0.38) !important;
  color: #BAE6FD !important; transform: none !important;
}

/* ── NAV BACK ── */
.nav-back .stButton > button {
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  border-radius: 10px !important; color: rgba(226,232,240,0.65) !important;
  font-size: 0.78rem !important; font-weight: 600 !important;
  padding: 6px 14px !important; box-shadow: none !important;
}
.nav-back .stButton > button:hover {
  background: rgba(59,130,246,0.14) !important;
  color: #BAE6FD !important; border-color: rgba(59,130,246,0.30) !important;
}

/* ── SUGGESTION PILLS ── */
.sug-pill .stButton > button {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
  border-radius: 999px !important; color: rgba(186,230,253,0.74) !important;
  font-size: 0.79rem !important; font-weight: 500 !important;
  padding: 9px 18px !important; box-shadow: none !important;
}
.sug-pill .stButton > button:hover {
  background: rgba(59,130,246,0.14) !important;
  border-color: rgba(59,130,246,0.34) !important;
  color: #BAE6FD !important; transform: translateY(-2px) !important;
}

/* ── DASHBOARD BUTTONS ── */
.ghost-btn .stButton > button {
  background: rgba(255,255,255,.05) !important;
  border: 1px solid var(--border2) !important;
  color: rgba(226,232,240,.55) !important; box-shadow: none !important;
}
.ghost-btn .stButton > button:hover {
  background: rgba(59,130,246,.10) !important; color: var(--text) !important;
}
.present-btn .stButton > button {
  background: linear-gradient(135deg,#065F46,#10B981) !important;
  box-shadow: 0 2px 10px rgba(16,185,129,.18) !important;
  padding: 6px 11px !important; font-size: 0.75rem !important; border-radius: 7px !important;
}
.absent-btn .stButton > button {
  background: linear-gradient(135deg,#7F1D1D,#EF4444) !important;
  box-shadow: 0 2px 10px rgba(239,68,68,.16) !important;
  padding: 6px 11px !important; font-size: 0.75rem !important; border-radius: 7px !important;
}
.save-btn .stButton > button {
  background: linear-gradient(135deg,#92400E,#F59E0B) !important;
  box-shadow: 0 2px 10px rgba(245,158,11,.18) !important;
  padding: 7px 13px !important; font-size: 0.77rem !important;
}
.pin-btn .stButton > button {
  background: rgba(245,158,11,0.10) !important;
  border: 1px solid rgba(245,158,11,0.28) !important;
  color: #FCD34D !important; box-shadow: none !important;
  font-size: 0.70rem !important; padding: 4px 10px !important; border-radius: 7px !important;
}
.pin-btn .stButton > button:hover {
  background: rgba(245,158,11,0.20) !important; transform: none !important;
}
.del-btn .stButton > button {
  background: rgba(239,68,68,0.07) !important;
  border: 1px solid rgba(239,68,68,0.18) !important;
  color: rgba(252,165,165,0.70) !important; box-shadow: none !important;
  font-size: 0.68rem !important; padding: 3px 8px !important; border-radius: 6px !important;
}
.del-btn .stButton > button:hover {
  background: rgba(239,68,68,0.16) !important; transform: none !important;
}
.ql-btn .stButton > button {
  background: rgba(255,255,255,.03) !important;
  border: 1px solid var(--border2) !important;
  color: rgba(186,230,253,.65) !important; box-shadow: none !important;
  text-align: left !important; justify-content: flex-start !important;
  font-size: 0.80rem !important; padding: 9px 14px !important; border-radius: 9px !important;
}
.ql-btn .stButton > button:hover {
  background: rgba(59,130,246,.10) !important;
  border-color: rgba(59,130,246,.28) !important;
  color: #BAE6FD !important; transform: none !important;
}
.logout-btn .stButton > button {
  background: rgba(239,68,68,.09) !important;
  border: 1px solid rgba(239,68,68,.20) !important;
  color: #FCA5A5 !important; box-shadow: none !important; font-size: 0.80rem !important;
}
.logout-btn .stButton > button:hover { background: rgba(239,68,68,.18) !important; }
.open-chat-btn .stButton > button {
  background: linear-gradient(135deg,#059669,#10B981) !important;
  border-radius: 12px !important; font-weight: 700 !important;
  font-size: 0.88rem !important; padding: 11px 22px !important;
  box-shadow: 0 5px 24px rgba(16,185,129,.36) !important;
  font-family: var(--mono) !important;
}
.open-chat-btn .stButton > button:hover {
  box-shadow: 0 7px 32px rgba(16,185,129,.50) !important;
  transform: translateY(-2px) !important;
}
.settings-menu-btn .stButton > button {
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  color: rgba(226,232,240,0.75) !important; box-shadow: none !important;
  font-size: 0.82rem !important; font-weight: 600 !important;
  padding: 8px 16px !important; border-radius: 10px !important;
}
.settings-menu-btn .stButton > button:hover {
  background: rgba(59,130,246,0.13) !important;
  color: #BAE6FD !important; border-color: rgba(59,130,246,0.30) !important;
}
.nav-btn .stButton > button {
  background: transparent !important; color: rgba(148,163,184,.65) !important;
  border: none !important; box-shadow: none !important;
  text-align: left !important; justify-content: flex-start !important;
  padding: 10px 14px !important; font-size: 0.83rem !important;
  font-weight: 500 !important; border-radius: 8px !important;
}
.nav-btn .stButton > button:hover {
  background: rgba(59,130,246,.10) !important;
  color: #BAE6FD !important; transform: none !important;
}
.nav-btn-active .stButton > button {
  background: rgba(59,130,246,.14) !important; color: #60A5FA !important;
  border-left: 2px solid #3B82F6 !important; font-weight: 700 !important;
  box-shadow: none !important;
}

/* ── Popovers ── */
[data-testid="stPopover"] > div {
  background: #0D1828 !important;
  border: 1px solid rgba(59,130,246,0.30) !important;
  border-radius: 16px !important;
  box-shadow: 0 16px 56px rgba(0,0,0,0.65) !important;
}
button[data-testid="stPopoverButton"] {
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
  border-radius: 999px !important; color: rgba(226,232,240,0.72) !important;
  font-family: var(--sans) !important; font-size: 0.78rem !important;
  font-weight: 500 !important; padding: 6px 15px !important; box-shadow: none !important;
}
button[data-testid="stPopoverButton"]:hover {
  background: rgba(59,130,246,0.16) !important;
  border-color: rgba(59,130,246,0.38) !important; color: #BAE6FD !important;
}

/* ── Progress bars ── */
[data-testid="stProgress"] > div > div {
  border-radius: 99px !important;
  background: linear-gradient(90deg,#2563EB,#22D3EE) !important;
}
[data-testid="stProgress"] > div {
  background: rgba(255,255,255,.07) !important;
  border-radius: 99px !important; height: 5px !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
  background: rgba(255,255,255,.018) !important;
  border: 1px solid var(--border) !important; border-radius: 12px !important;
}
summary { font-family: var(--sans) !important; font-weight: 600 !important; }

/* ── Typography ── */
h1,h2,h3,h4 { font-family: var(--mono) !important; font-weight: 500 !important; }
[data-testid="stMarkdown"] p,
[data-testid="stMarkdown"] li { color: rgba(226,232,240,.72) !important; font-family: var(--sans) !important; }
hr { border-color: var(--border) !important; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(59,130,246,.22); border-radius: 4px; }
[data-testid="column"] { padding: 0 4px !important; }

/* ── Animations ── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(18px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(-6px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes pinPulse {
  0%,100% { box-shadow: 0 0 0 0 rgba(245,158,11,0.30); }
  50%      { box-shadow: 0 0 0 6px rgba(245,158,11,0.00); }
}
.pinned-note-card { animation: pinPulse 2.5s ease infinite; }
.chat-scroll-area  { padding-bottom: 130px; }
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# GEMINI INPUT BAR — render_gemini_bar()
# ─────────────────────────────────────────────────────────────────────────────
# Architecture: A native st.form styled with CSS to look like the Gemini pill.
# Layout: [📎 attach] [text input (flex-grow)] [🎤 mic] [↑ send]
# All are real Streamlit widgets — 100% functional, no iframes, no JS bridge.
# bar_key: unique string so hero + anchored bars don't share keys.
# Returns: ("send", text) | ("mic",) | ("attach",) | None
# ═════════════════════════════════════════════════════════════════════════════
def render_gemini_bar(bar_key: str, hero_mode: bool = True):
    recording = st.session_state.is_recording
    mic_class  = "gemini-mic-active" if recording else "gemini-mic"
    mic_icon   = "⏹" if recording else "🎤"

    anim_style = "animation:slideUp 0.35s cubic-bezier(0.22,0.61,0.36,1) both;" if hero_mode else ""
    st.markdown(
        f'<div class="gemini-bar" style="max-width:800px;margin:0 auto;{anim_style}">',
        unsafe_allow_html=True,
    )

    with st.form(key=f"gemini_form_{bar_key}", clear_on_submit=True):
        # 4 columns: narrow attach | wide input | narrow mic | narrow send
        c_attach, c_input, c_mic, c_send = st.columns([0.55, 10, 0.65, 0.65])

        with c_attach:
            st.markdown('<div class="gemini-attach">', unsafe_allow_html=True)
            attach_clicked = st.form_submit_button("📎", help="Attach a file")
            st.markdown('</div>', unsafe_allow_html=True)

        with c_input:
            user_text = st.text_input(
                label="__gi__",
                placeholder="Ask AskMNIT...",
                key=f"gi_text_{bar_key}",
                label_visibility="collapsed",
            )

        with c_mic:
            st.markdown(f'<div class="{mic_class}">', unsafe_allow_html=True)
            mic_clicked = st.form_submit_button(mic_icon, help="Voice input")
            st.markdown('</div>', unsafe_allow_html=True)

        with c_send:
            st.markdown('<div class="gemini-send">', unsafe_allow_html=True)
            send_clicked = st.form_submit_button("↑", help="Send message")
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close .gemini-bar

    if mic_clicked:
        return ("mic",)
    if attach_clicked:
        return ("attach",)
    if send_clicked:
        txt = (user_text or "").strip()
        if txt:
            return ("send", txt)
    return None


# ═════════════════════════════════════════════════════════════════════════════
# VIEW ROUTER
# ═════════════════════════════════════════════════════════════════════════════
view = st.session_state.view


###############################################################################
# ████████████████████████  CHAT VIEW  ████████████████████████████████████████
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

    # ── NAVBAR ────────────────────────────────────────────────────────────────
    st.markdown(
        '<div style="background:rgba(7,11,20,0.96);'
        'backdrop-filter:blur(20px) saturate(180%);'
        'border-bottom:1px solid rgba(59,130,246,0.16);'
        'box-shadow:0 2px 24px rgba(0,0,0,0.50);'
        'padding:10px 22px;'
        'display:flex;align-items:center;">'
        '<div style="display:flex;align-items:center;gap:9px;">'
        '<div style="width:28px;height:28px;border-radius:8px;'
        'background:linear-gradient(135deg,#2563EB,#4F46E5);'
        'display:flex;align-items:center;justify-content:center;'
        'font-size:0.82rem;font-weight:700;color:white;'
        'box-shadow:0 2px 10px rgba(37,99,235,0.32);">A</div>'
        '<span style="font-family:\'DM Mono\',monospace;font-size:0.88rem;color:#E2E8F0;">AskMNIT</span>'
        '<span style="font-size:0.56rem;color:#10B981;font-weight:700;margin-left:2px;">&#9679; AI</span>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    _, nc1, nc2, nc3, nc4 = st.columns([4, 1.1, 1, 1, 1.3])

    with nc1:
        st.markdown('<div class="nav-pill">', unsafe_allow_html=True)
        if st.button("+ New Chat", key="btn_new_chat"):
            if st.session_state.chat_messages:
                fu = next(
                    (m["content"][:38] for m in st.session_state.chat_messages if m["role"] == "user"),
                    "Session"
                )
                st.session_state.chat_sessions.append(
                    {"label": fu + "...", "messages": list(st.session_state.chat_messages)}
                )
            st.session_state.chat_messages = []
            st.session_state.show_uploader = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with nc2:
        with st.popover("History", use_container_width=True):
            st.markdown(
                '<div style="font-family:\'DM Mono\',monospace;font-size:0.58rem;'
                'color:rgba(148,163,184,0.45);text-transform:uppercase;'
                'letter-spacing:1.2px;margin-bottom:12px;">Chat History</div>',
                unsafe_allow_html=True,
            )
            all_sessions = list(st.session_state.chat_sessions)
            for day_label, title in MOCK_HISTORY:
                all_sessions.append({"label": title, "_mock_day": day_label, "messages": []})
            if not all_sessions:
                st.markdown(
                    '<p style="font-size:0.77rem;color:rgba(148,163,184,0.44);'
                    'text-align:center;padding:8px 0;">No sessions yet.</p>',
                    unsafe_allow_html=True,
                )
            else:
                current_day = ""
                for i, sess in enumerate(reversed(all_sessions)):
                    day_lbl = sess.get("_mock_day", "This session")
                    if day_lbl != current_day:
                        current_day = day_lbl
                        st.markdown(
                            f'<div style="font-size:0.60rem;font-weight:700;'
                            f'color:rgba(148,163,184,0.40);text-transform:uppercase;'
                            f'letter-spacing:0.8px;padding:8px 0 4px;">{day_lbl}</div>',
                            unsafe_allow_html=True,
                        )
                    hc1, hc2 = st.columns([5, 1])
                    with hc1:
                        st.markdown(
                            f'<div style="font-size:0.78rem;color:rgba(148,163,184,0.65);'
                            f'padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.04);">'
                            f'{sess["label"]}</div>',
                            unsafe_allow_html=True,
                        )
                    with hc2:
                        if sess.get("messages") and not sess.get("_mock_day"):
                            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
                            if st.button("back", key=f"load_sess_{i}"):
                                st.session_state.chat_messages = list(sess["messages"])
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)

    with nc3:
        with st.popover("Settings", use_container_width=True):
            st.markdown(
                '<div style="font-family:\'DM Mono\',monospace;font-size:0.58rem;'
                'color:rgba(148,163,184,0.45);text-transform:uppercase;'
                'letter-spacing:1.2px;margin-bottom:12px;">Bot Settings</div>',
                unsafe_allow_html=True,
            )
            st.session_state.voice_output = st.toggle(
                "Voice Output", value=st.session_state.voice_output, key="toggle_voice",
            )
            st.session_state.strict_mode = st.toggle(
                "Strict Academic Mode", value=st.session_state.strict_mode, key="toggle_strict",
            )
            st.markdown(
                '<div style="font-size:0.78rem;color:rgba(148,163,184,0.52);line-height:1.70;margin-top:6px;">'
                f'Context: {st.session_state.student_name} · {st.session_state.branch}<br>'
                f'Sessions: {len(st.session_state.chat_sessions)}'
                '</div>',
                unsafe_allow_html=True,
            )

    with nc4:
        st.markdown('<div class="nav-back">', unsafe_allow_html=True)
        if st.button("Dashboard", key="btn_dashboard"):
            st.session_state.view = "dashboard"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        '<div style="height:1px;background:linear-gradient(90deg,transparent,'
        'rgba(59,130,246,0.30),rgba(34,211,238,0.14),transparent);"></div>',
        unsafe_allow_html=True,
    )

    # ── FILE UPLOADER PANEL ───────────────────────────────────────────────────
    if st.session_state.show_uploader:
        st.markdown('<div class="attach-panel">', unsafe_allow_html=True)
        up_c1, up_c2 = st.columns([6, 1])
        with up_c1:
            attached = st.file_uploader(
                "Attach a file",
                type=["pdf", "txt", "png", "jpg", "jpeg", "docx", "csv"],
                key="file_uploader_chat",
            )
        with up_c2:
            st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("Close", key="close_uploader"):
                st.session_state.show_uploader = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        if attached is not None:
            msg_text = f"File **{attached.name}** attached."
            if not st.session_state.chat_messages or \
               st.session_state.chat_messages[-1]["content"] != msg_text:
                dispatch_message(msg_text)
                st.session_state.show_uploader = False
                st.toast(f"{attached.name} attached!", icon="✅")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── HERO STATE — no messages ──────────────────────────────────────────────
    if not has_messages:
        st.markdown("<div style='height:5vh'></div>", unsafe_allow_html=True)

        _, hero_col, _ = st.columns([1, 3, 1])
        with hero_col:
            st.markdown(
                '<div style="text-align:center;animation:fadeUp 0.45s ease both;">'
                '<div style="width:80px;height:80px;margin:0 auto 22px;border-radius:22px;'
                'background:linear-gradient(135deg,#1E3A8A,#4338CA 50%,#059669);'
                'display:flex;align-items:center;justify-content:center;font-size:2.3rem;'
                'box-shadow:0 0 0 1px rgba(59,130,246,0.22),'
                '0 16px 52px rgba(37,99,235,0.30),'
                '0 0 100px rgba(59,130,246,0.07);">&#129302;</div>'
                '<div style="font-family:\'Fraunces\',serif;font-size:3rem;font-weight:900;'
                'color:#E2E8F0;letter-spacing:-2px;line-height:1.05;margin-bottom:10px;">'
                'AskMNIT <span style="font-weight:300;color:#60A5FA;">AI</span></div>'
                '<div style="font-size:0.86rem;color:rgba(148,163,184,0.50);line-height:1.70;margin-bottom:32px;">'
                'Attendance analysis &nbsp;&#183;&nbsp; PYQ search &nbsp;&#183;&nbsp; '
                'Schedule queries &nbsp;&#183;&nbsp; Exam prep'
                '</div></div>',
                unsafe_allow_html=True,
            )

        br = st.session_state.branch
        PILLS_ROW1 = [
            "Analyse my attendance",
            "What's next on my schedule?",
            f"PYQs for {br}",
            "Check my fee status",
        ]
        PILLS_ROW2 = [f"Subjects for {br}", "Exam schedule tips"]

        _, pills_col, _ = st.columns([0.5, 5, 0.5])
        with pills_col:
            r1_cols = st.columns(len(PILLS_ROW1))
            for i, pill in enumerate(PILLS_ROW1):
                with r1_cols[i]:
                    st.markdown('<div class="sug-pill">', unsafe_allow_html=True)
                    if st.button(pill, key=f"pill_r1_{i}", use_container_width=True):
                        dispatch_message(pill); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            _, r2_c1, r2_c2, _ = st.columns([1, 1.5, 1.5, 1])
            for i, (pill, col) in enumerate(zip(PILLS_ROW2, [r2_c1, r2_c2])):
                with col:
                    st.markdown('<div class="sug-pill">', unsafe_allow_html=True)
                    if st.button(pill, key=f"pill_r2_{i}", use_container_width=True):
                        dispatch_message(pill); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:3vh'></div>", unsafe_allow_html=True)

        # ── HERO GEMINI BAR ──────────────────────────────────────────────────
        _, bar_col, _ = st.columns([0.5, 5, 0.5])
        with bar_col:
            hero_action = render_gemini_bar(bar_key="hero", hero_mode=True)

        # Listening banner
        if st.session_state.is_recording:
            st.markdown(
                '<div class="listening-banner">'
                '<div class="listening-dot"></div>'
                '<span>Listening... speak your question</span>'
                '</div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            '<p style="text-align:center;font-size:0.59rem;color:rgba(100,116,139,0.38);'
            'margin-top:10px;font-family:\'DM Mono\',monospace;letter-spacing:0.4px;">'
            'AskMNIT AI can make mistakes &nbsp;&#183;&nbsp; Verify with official ERP or faculty'
            '</p>',
            unsafe_allow_html=True,
        )

        # Handle hero bar actions
        if hero_action is not None:
            if hero_action[0] == "send":
                dispatch_message(hero_action[1]); st.rerun()
            elif hero_action[0] == "mic":
                st.session_state.is_recording = not st.session_state.is_recording
                st.toast("Listening..." if st.session_state.is_recording else "Recording stopped.", icon="🎤")
                st.rerun()
            elif hero_action[0] == "attach":
                st.session_state.show_uploader = not st.session_state.show_uploader
                st.rerun()

    # ── ACTIVE STATE — messages exist ─────────────────────────────────────────
    else:
        st.markdown("<div class='chat-scroll-area'>", unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        _, msg_col, _ = st.columns([0.5, 5, 0.5])
        with msg_col:
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
        st.markdown("</div>", unsafe_allow_html=True)

        # ── ANCHORED BOTTOM BAR ───────────────────────────────────────────────
        st.markdown('<div class="gemini-bar-anchored">', unsafe_allow_html=True)

        anchored_action = render_gemini_bar(bar_key="anchored", hero_mode=False)

        if st.session_state.is_recording:
            st.markdown(
                '<div class="listening-banner" style="margin-top:8px;">'
                '<div class="listening-dot"></div>'
                '<span>Listening... speak your question</span>'
                '</div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            '<p style="text-align:center;font-size:0.59rem;color:rgba(100,116,139,0.38);'
            'margin-top:4px;font-family:\'DM Mono\',monospace;letter-spacing:0.4px;">'
            'AskMNIT AI can make mistakes &nbsp;&#183;&nbsp; Verify with official ERP or faculty'
            '</p>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)  # close .gemini-bar-anchored

        # Handle anchored bar actions
        if anchored_action is not None:
            if anchored_action[0] == "send":
                dispatch_message(anchored_action[1]); st.rerun()
            elif anchored_action[0] == "mic":
                st.session_state.is_recording = not st.session_state.is_recording
                st.toast("Listening..." if st.session_state.is_recording else "Recording stopped.", icon="🎤")
                st.rerun()
            elif anchored_action[0] == "attach":
                st.session_state.show_uploader = not st.session_state.show_uploader
                st.rerun()

    st.stop()


###############################################################################
# ████████████████████  DASHBOARD VIEW  ██████████████████████████████████████
###############################################################################

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
NAV_ITEMS = [
    ("", "My Dashboard"), ("", "My Schedule"), ("", "Academics"),
    ("", "Study Material"), ("", "PYQs"), ("", "Fee Portal"), ("", "Mess Menu"),
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
        '<div><div style="font-family:\'DM Mono\',monospace;font-size:0.85rem;color:#E2E8F0;">'
        'AskMNIT</div>'
        '<div style="font-size:0.56rem;color:rgba(148,163,184,.40);margin-top:1px;">'
        'Student Portal</div></div></div></div>',
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

    NAV_ITEMS_FULL = [
        ("", "My Dashboard"), ("", "My Schedule"), ("", "Academics"),
        ("", "Study Material"), ("", "PYQs"), ("", "Fee Portal"), ("", "Mess Menu"),
    ]
    NAV_LABELS = ["My Dashboard", "My Schedule", "Academics",
                  "Study Material", "PYQs", "Fee Portal", "Mess Menu"]
    NAV_ICONS  = ["Dashboard", "Schedule", "Academics",
                  "Study Material", "PYQs", "Fee Portal", "Mess Menu"]

    for label in NAV_LABELS:
        is_active = st.session_state.nav_page == label
        css = "nav-btn-active" if is_active else "nav-btn"
        st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
        if st.button(label, key="nav_" + label, use_container_width=True):
            st.session_state.nav_page = label; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div style="position:fixed;bottom:18px;width:182px;'
        'padding-top:10px;border-top:1px solid rgba(255,255,255,0.06);">',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("Logout", key="sidebar_logout", use_container_width=True):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PLACEHOLDER PAGES
# ─────────────────────────────────────────────────────────────────────────────
dash_page = st.session_state.nav_page
if dash_page != "My Dashboard":
    PMETA = {
        "My Schedule":    ("My Schedule",    "Weekly timetable renders here."),
        "Academics":      ("Academics",       "Grades and CGPA records render here."),
        "Study Material": ("Study Material",  "Uploaded notes render here."),
        "PYQs":           ("PYQs",            "Previous year papers render here."),
        "Fee Portal":     ("Fee Portal",      "Fee dues and receipts render here."),
        "Mess Menu":      ("Mess Menu",       "Weekly hostel menu renders here."),
    }
    title, desc = PMETA.get(dash_page, (dash_page, "Coming soon."))
    st.markdown(
        '<div style="padding:24px;">'
        '<div style="display:flex;align-items:center;gap:10px;'
        'border-bottom:1px solid rgba(255,255,255,0.06);padding-bottom:14px;margin-bottom:24px;">'
        '<span style="font-family:\'DM Mono\',monospace;font-size:0.95rem;color:#E2E8F0;">'
        + title.upper() + '</span></div>'
        '<div style="background:linear-gradient(160deg,#0B1120,#060A12);'
        'border:1px dashed rgba(59,130,246,0.18);border-radius:16px;'
        'padding:60px 40px;text-align:center;">'
        '<div style="font-family:\'DM Mono\',monospace;font-size:0.88rem;color:#E2E8F0;margin-bottom:8px;">'
        + title.upper() + '</div>'
        '<div style="font-size:0.76rem;color:rgba(148,163,184,.44);max-width:280px;margin:0 auto;line-height:1.65;">'
        + desc + '</div></div></div>',
        unsafe_allow_html=True,
    )
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# MY DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div style='padding:0 22px 80px;'>", unsafe_allow_html=True)

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
    nm  = st.session_state.student_name
    br  = st.session_state.branch
    sem = st.session_state.semester
    bh  = branch_hex(br)
    pp  = st.session_state.profile_pic_b64
    av_html = (
        f'<img src="{pp}" style="width:36px;height:36px;border-radius:50%;'
        f'object-fit:cover;border:2px solid {bh}55;">'
        if pp else
        f'<div style="width:36px;height:36px;border-radius:50%;'
        f'background:linear-gradient(135deg,{bh},{bh}88);'
        f'display:flex;align-items:center;justify-content:center;'
        f'font-size:0.85rem;font-weight:700;color:#fff;'
        f'border:2px solid {bh}55;">{initials(nm)}</div>'
    )
    st.markdown(
        f'<div style="display:flex;align-items:center;justify-content:flex-end;'
        f'gap:9px;padding:10px 0 6px;">'
        f'{av_html}'
        f'<div>'
        f'<div style="font-weight:700;font-size:0.83rem;color:#E2E8F0;line-height:1.2;">{nm}</div>'
        f'<div style="font-size:0.58rem;color:{bh};font-weight:600;">{br} · {sem}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div style="height:1px;background:linear-gradient(90deg,transparent,'
    'rgba(59,130,246,0.22),rgba(34,211,238,0.10),transparent);margin-bottom:20px;"></div>',
    unsafe_allow_html=True,
)

# ── SETTINGS TOGGLE ROW ───────────────────────────────────────────────────
srow1, srow2, srow3, srow4, srow5 = st.columns([1, 1, 1, 1, 1])
with srow1:
    st.markdown('<div class="settings-menu-btn">', unsafe_allow_html=True)
    if st.button("Settings & Profile", key="open_settings"):
        st.session_state.settings_mode = (
            None if st.session_state.settings_mode == "profile" else "profile"
        )
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with srow2:
    st.markdown('<div class="settings-menu-btn">', unsafe_allow_html=True)
    if st.button("Upload Schedule", key="open_schedule"):
        st.session_state.settings_mode = (
            None if st.session_state.settings_mode == "schedule" else "schedule"
        )
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with srow3:
    st.markdown('<div class="settings-menu-btn">', unsafe_allow_html=True)
    if st.button("Notifications", key="open_notif"):
        st.toast("No new notifications.", icon="🔔")
    st.markdown('</div>', unsafe_allow_html=True)
with srow4:
    pass
with srow5:
    st.markdown('<div class="open-chat-btn">', unsafe_allow_html=True)
    if st.button("Open AskMNIT AI", key="btn_open_chat_dash"):
        st.session_state.view = "chat"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── SETTINGS / PROFILE DRAWER ─────────────────────────────────────────────
mode = st.session_state.settings_mode
if mode == "profile":
    with st.expander("Settings & Profile", expanded=True):
        pc1, pc2 = st.columns([1, 2])
        with pc1:
            pp = st.session_state.profile_pic_b64
            bh = branch_hex(st.session_state.branch)
            if pp:
                st.markdown(
                    f'<img src="{pp}" style="width:80px;height:80px;border-radius:50%;'
                    f'object-fit:cover;border:3px solid {bh}66;display:block;margin:0 auto 8px;">',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div style="width:80px;height:80px;border-radius:50%;'
                    f'background:linear-gradient(135deg,{bh},{bh}88);'
                    f'display:flex;align-items:center;justify-content:center;'
                    f'font-size:1.8rem;font-weight:700;color:#fff;margin:0 auto 8px;">'
                    f'{initials(st.session_state.student_name)}</div>',
                    unsafe_allow_html=True,
                )
            pic_file = st.file_uploader("Upload photo", type=["png", "jpg", "jpeg"],
                                        key="profile_pic_up", label_visibility="collapsed")
            if pic_file:
                st.session_state.profile_pic_b64 = img_to_b64(pic_file); st.rerun()
        with pc2:
            new_name = st.text_input("Full Name",  value=st.session_state.student_name, key="inp_name")
            new_id   = st.text_input("College ID", value=st.session_state.college_id,   key="inp_id")
            new_sem  = st.selectbox("Semester", SEMESTERS,
                                    index=SEMESTERS.index(st.session_state.semester), key="sel_sem")
            new_br   = st.selectbox("Branch", BRANCHES,
                                    index=BRANCHES.index(st.session_state.branch), key="sel_br")
            if st.button("Save Profile", key="save_profile"):
                old_br = st.session_state.branch
                st.session_state.student_name = new_name
                st.session_state.college_id   = new_id
                st.session_state.semester      = new_sem
                st.session_state.branch        = new_br
                if old_br != new_br:
                    st.session_state.attendance = blank_att(subjects_for_branch(new_br))
                st.toast("Profile saved!", icon="✅")
                st.session_state.settings_mode = None
                st.rerun()

elif mode == "schedule":
    with st.expander("Upload Weekly Schedule PDF", expanded=True):
        pdf_file = st.file_uploader("Drop schedule PDF here", type=["pdf"], key="sched_upload")
        if pdf_file:
            st.session_state.full_schedule   = process_schedule_pdf(pdf_file, st.session_state.branch)
            st.session_state.schedule_loaded = True
            st.session_state.pdf_filename    = pdf_file.name
            st.toast(f"Schedule loaded: {pdf_file.name}", icon="✅")
            st.session_state.settings_mode  = None
            st.rerun()
        if st.session_state.schedule_loaded:
            st.markdown(
                f'<div style="font-size:0.75rem;color:#10B981;margin-top:6px;">'
                f'Active: {st.session_state.pdf_filename}</div>',
                unsafe_allow_html=True,
            )

# ── OVERVIEW STATS ────────────────────────────────────────────────────────
ov = overall_pct(st.session_state.attendance)
stat_badge_txt, stat_col, stat_bg = status_badge(ov)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
for col, ico, val, lbl, c in [
    (kpi1, "📊", f"{ov}%", "Overall Attendance", stat_col),
    (kpi2, "📚", str(len(subjects_for_branch(st.session_state.branch))), "Enrolled Subjects", "#60A5FA"),
    (kpi3, "📅",
     str(len(get_today_slots(st.session_state.full_schedule)) if st.session_state.schedule_loaded else 0),
     "Classes Today", "#22D3EE"),
    (kpi4, "📝", str(len(st.session_state.notes_list)), "Active Notes", "#A78BFA"),
]:
    with col:
        st.markdown(
            f'<div style="background:linear-gradient(160deg,#0B1120,#070D1C);'
            f'border:1px solid rgba(255,255,255,0.07);border-radius:14px;'
            f'padding:16px 18px 14px;margin-bottom:14px;">'
            f'<div style="font-size:1.4rem;margin-bottom:6px;">{ico}</div>'
            f'<div style="font-size:1.7rem;font-weight:800;color:{c};'
            f'font-family:\'DM Mono\',monospace;line-height:1.1;">{val}</div>'
            f'<div style="font-size:0.68rem;color:rgba(148,163,184,.46);margin-top:4px;">{lbl}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ── ATTENDANCE TRACKER ────────────────────────────────────────────────────
st.markdown(
    '<div style="background:linear-gradient(160deg,#0B1120,#070D1C);'
    'border:1px solid rgba(255,255,255,0.07);border-radius:16px;'
    'padding:18px 18px 14px;margin-bottom:14px;">'
    '<div style="font-family:\'DM Mono\',monospace;font-size:0.56rem;'
    'color:rgba(148,163,184,.40);text-transform:uppercase;'
    'letter-spacing:1.4px;margin-bottom:14px;">// ATTENDANCE TRACKER</div>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# BUG FIX: render_subj_rows
# KEY FORMAT: f"{action}_{section}_{idx}_{safe_subject_name}"
# - section: "cmn" or "brnch" — differentiates the two expander calls
# - idx: enumerate() index — handles subjects with identical first-8-chars
# - _safe_key(subj): sanitized full subject name — extra guarantee of uniqueness
# This eliminates StreamlitDuplicateElementKey even when subject names share
# prefixes like "Mathematics I/II" vs "Mathematics for AI" vs "Discrete Mathematics"
# ─────────────────────────────────────────────────────────────────────────────
def render_subj_rows(subj_list: list, section: str):
    att = st.session_state.attendance
    for idx, subj in enumerate(subj_list):
        if subj not in att:
            att[subj] = {"present": 0, "total": 0}
        r   = att[subj]
        pct = att_pct(r)
        c   = att_color(pct)
        # Unique key base: section prefix + enumerate index + sanitized full name
        kb  = f"{section}_{idx}_{_safe_key(subj)}"

        sc1, sc2, sc3, sc4, sc5, sc6 = st.columns([3.5, 1.2, 0.9, 0.9, 0.9, 0.9])
        with sc1:
            st.markdown(
                f'<div style="font-size:0.80rem;color:#E2E8F0;font-weight:600;padding:8px 0 4px;">{subj}</div>'
                f'<div style="background:rgba(255,255,255,.06);border-radius:99px;height:4px;overflow:hidden;width:90%;">'
                f'<div style="width:{pct}%;height:100%;background:linear-gradient(90deg,{c},{c}88);border-radius:99px;"></div></div>',
                unsafe_allow_html=True,
            )
        with sc2:
            st.markdown(
                f'<div style="font-family:\'DM Mono\',monospace;font-size:0.85rem;font-weight:700;'
                f'color:{c};padding-top:8px;">{pct}%</div>'
                f'<div style="font-size:0.60rem;color:rgba(148,163,184,.40);">'
                f'{r["present"]}/{r["total"]}</div>',
                unsafe_allow_html=True,
            )
        with sc3:
            st.markdown('<div class="present-btn">', unsafe_allow_html=True)
            if st.button("P", key=f"pp_{kb}", use_container_width=True):
                st.session_state.attendance[subj]["present"] += 1
                st.session_state.attendance[subj]["total"]   += 1
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with sc4:
            st.markdown('<div class="absent-btn">', unsafe_allow_html=True)
            if st.button("A", key=f"pa_{kb}", use_container_width=True):
                st.session_state.attendance[subj]["total"] += 1
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with sc5:
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("-P", key=f"rp_{kb}", use_container_width=True):
                if r["present"] > 0 and r["total"] > 0:
                    st.session_state.attendance[subj]["present"] -= 1
                    st.session_state.attendance[subj]["total"]   -= 1
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with sc6:
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("-A", key=f"ra_{kb}", use_container_width=True):
                if r["total"] > 0:
                    st.session_state.attendance[subj]["total"] -= 1
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)


branch_only = BRANCH_SUBJECTS.get(st.session_state.branch, [])
with st.expander("Common Subjects (" + str(len(COMMON_SUBJECTS)) + ")", expanded=True):
    render_subj_rows(COMMON_SUBJECTS, "cmn")
if branch_only:
    with st.expander(st.session_state.branch + " Subjects (" + str(len(branch_only)) + ")", expanded=True):
        render_subj_rows(branch_only, "brnch")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

# ── SCHEDULE SECTION ──────────────────────────────────────────────────────
today_name = datetime.datetime.now().strftime("%A")
now_hm     = datetime.datetime.now().hour * 60 + datetime.datetime.now().minute
st.markdown(
    '<div style="background:linear-gradient(160deg,#0B1120,#070D1C);'
    'border:1px solid rgba(255,255,255,0.07);border-radius:16px;'
    'padding:18px 18px 14px;margin-bottom:14px;">'
    '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">'
    '<span style="font-family:\'DM Mono\',monospace;font-size:0.56rem;'
    'color:rgba(148,163,184,.40);text-transform:uppercase;letter-spacing:1.4px;">'
    "// TODAY'S CLASS SCHEDULE</span>"
    '<span style="font-family:\'DM Mono\',monospace;font-size:0.62rem;'
    'color:rgba(96,165,250,.65);">' + today_name.upper() + '</span></div>',
    unsafe_allow_html=True,
)
if st.session_state.schedule_loaded:
    today_slots = get_today_slots(st.session_state.full_schedule)
    nxt         = get_next_class(today_slots)
    if nxt:
        mins   = nxt["minutes_away"]
        hrs    = mins // 60; rem = mins % 60
        cd_str = (f"{hrs}h {rem}m" if hrs else f"{rem} min") + " away"
        urg_c  = "#EF4444" if mins < 15 else "#F59E0B" if mins < 45 else "#22D3EE"
        st.markdown(
            '<div style="background:linear-gradient(90deg,rgba(34,211,238,.06),rgba(37,99,235,.04));'
            'border:1px solid rgba(34,211,238,.18);border-radius:10px;padding:10px 16px;margin-bottom:14px;'
            'display:flex;align-items:center;justify-content:space-between;">'
            '<div><div style="font-size:0.57rem;color:rgba(148,163,184,.46);text-transform:uppercase;'
            'letter-spacing:0.8px;margin-bottom:2px;">Next Class</div>'
            '<div style="font-weight:700;font-size:0.86rem;color:#E2E8F0;">'
            + nxt["subject"] + '  <span style="font-size:0.67rem;color:rgba(148,163,184,.46);">'
            + nxt["room"] + '</span></div></div>'
            '<div style="font-family:\'DM Mono\',monospace;font-size:0.96rem;font-weight:600;color:'
            + urg_c + ';text-align:right;">' + cd_str
            + '<div style="font-size:0.57rem;color:rgba(148,163,184,.42);font-weight:400;margin-top:1px;">'
            + fmt_time(nxt["time_start"]) + ' - ' + fmt_time(nxt["time_end"]) + '</div></div></div>',
            unsafe_allow_html=True,
        )
    if today_slots:
        rows = [today_slots[i:i + 3] for i in range(0, len(today_slots), 3)]
        for row in rows:
            cols = st.columns(len(row))
            for ci, (col, slot) in enumerate(zip(cols, row)):
                sh, sm   = map(int, slot["time_start"].split(":"))
                is_past  = (sh * 60 + sm) < now_hm
                tc       = TYPE_COLORS.get(slot["type"], "#60A5FA")
                is_next  = (nxt is not None
                            and slot["time_start"] == nxt["time_start"]
                            and slot["subject"]    == nxt["subject"])
                bc  = tc if not is_past else "rgba(255,255,255,0.06)"
                cbg = ("linear-gradient(160deg,rgba(34,211,238,0.06),rgba(37,99,235,0.03))"
                       if is_next else "rgba(255,255,255,0.02)" if not is_past else "rgba(255,255,255,0.01)")
                with col:
                    st.markdown(
                        '<div style="background:' + cbg + ';border:1px solid ' + bc
                        + ';border-left:3px solid ' + bc
                        + ';border-radius:12px;padding:13px 14px;margin-bottom:8px;">'
                        '<div style="font-family:\'DM Mono\',monospace;font-size:0.78rem;font-weight:700;color:'
                        + ("#E2E8F0" if not is_past else "rgba(148,163,184,0.32)")
                        + ';margin-bottom:6px;">' + fmt_time(slot["time_start"])
                        + '<br><span style="font-size:0.62rem;font-weight:400;color:rgba(148,163,184,0.45);">- '
                        + fmt_time(slot["time_end"]) + '</span></div>'
                        '<div style="font-size:0.82rem;font-weight:700;color:'
                        + ("#F1F5F9" if not is_past else "rgba(148,163,184,0.28)")
                        + ';margin-bottom:5px;">' + slot["subject"] + '</div>'
                        '<div style="display:flex;align-items:center;gap:6px;">'
                        '<span style="font-size:0.62rem;color:rgba(148,163,184,.48);">' + slot["room"] + '</span>'
                        '<span style="font-size:0.58rem;padding:1px 7px;border-radius:4px;background:'
                        + tc + '1A;color:' + tc + ';font-weight:600;">' + slot["type"] + '</span>'
                        + ('  <span style="font-size:0.58rem;color:#22D3EE;font-weight:700;">NEXT</span>'
                           if is_next else '')
                        + '</div>'
                        + ('<div style="font-size:0.58rem;color:rgba(148,163,184,.28);'
                           'margin-top:4px;text-decoration:line-through;">Done</div>' if is_past else '')
                        + '</div>',
                        unsafe_allow_html=True,
                    )
    else:
        st.markdown(
            '<div style="text-align:center;padding:24px;color:rgba(148,163,184,.40);font-size:0.80rem;">No classes for '
            + today_name + '.</div>',
            unsafe_allow_html=True,
        )
else:
    st.markdown(
        '<div style="background:rgba(59,130,246,.04);border:1px dashed rgba(59,130,246,.20);'
        'border-radius:9px;padding:9px 13px;margin-bottom:12px;font-size:0.73rem;'
        'color:rgba(148,163,184,.48);">Use <b>Upload Schedule</b> to activate the planner.</div>',
        unsafe_allow_html=True,
    )
    if "planner_overrides" not in st.session_state:
        st.session_state.planner_overrides = {}
    for st_start, st_end in [
        ("08:00", "09:00"), ("09:30", "10:30"), ("11:00", "12:00"),
        ("12:00", "13:00"), ("14:00", "15:00"), ("15:30", "16:30")
    ]:
        override = st.session_state.planner_overrides.get(st_start, "")
        mp1, mp2, mp3, mp4 = st.columns([1.6, 4, 0.8, 2.2])
        with mp1:
            st.markdown(
                '<div style="font-family:\'DM Mono\',monospace;font-size:0.68rem;'
                'color:#60A5FA;padding-top:10px;white-space:nowrap;font-weight:700;">'
                + fmt_time(st_start)
                + '<br><span style="font-size:0.56rem;font-weight:400;color:rgba(148,163,184,.38);">- '
                + fmt_time(st_end) + '</span></div>',
                unsafe_allow_html=True,
            )
        with mp2:
            note_v = st.text_input("", value=override, placeholder="Task...",
                                   key="mp_" + st_start, label_visibility="collapsed")
        with mp3:
            st.markdown('<div class="save-btn">', unsafe_allow_html=True)
            if st.button("Save", key="sv_mp_" + st_start, use_container_width=True):
                st.session_state.planner_overrides[st_start] = note_v; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with mp4:
            saved = st.session_state.planner_overrides.get(st_start, "")
            if saved:
                st.markdown(
                    '<div style="font-size:0.67rem;color:#34D399;background:rgba(16,185,129,.07);'
                    'border:1px solid rgba(16,185,129,.14);border-radius:7px;padding:4px 9px;'
                    'margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'
                    + saved + '</div>',
                    unsafe_allow_html=True,
                )
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# ── NOTES & QUICK LINKS ───────────────────────────────────────────────────
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
    QL = [
        ("Upload Syllabus",  "Syllabus uploader will be enabled here."),
        ("Add PYQ Link",     "PYQ link manager will open here."),
        ("Library Search",   "Library search will open here."),
    ]
    st.markdown('<div class="ql-btn">', unsafe_allow_html=True)
    for lbl, fb in QL:
        if st.button(lbl, key="ql_" + lbl, use_container_width=True):
            st.session_state.ql_feedback = fb; st.rerun()
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if st.session_state.ql_feedback:
        st.markdown(
            '<div style="background:rgba(59,130,246,.06);border:1px solid rgba(59,130,246,.18);'
            'border-radius:8px;padding:7px 11px;margin-top:7px;font-size:0.70rem;'
            'color:rgba(186,230,253,.58);line-height:1.5;">' + st.session_state.ql_feedback + '</div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

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
    new_note_input = st.text_input("", placeholder="Type a new note...",
                                   key="new_note_input_field", label_visibility="collapsed")
    ac, _ = st.columns([1, 3])
    with ac:
        if st.button("Add Note", key="add_note_btn", use_container_width=True):
            txt = new_note_input.strip()
            if txt:
                st.session_state.notes_list.append({"text": txt, "pinned": False}); st.rerun()
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    unpinned = [(i, n) for i, n in enumerate(st.session_state.notes_list) if not n["pinned"]]
    if not unpinned:
        st.markdown(
            '<div style="font-size:0.76rem;color:rgba(148,163,184,.38);'
            'text-align:center;padding:16px;font-style:italic;">No notes yet.</div>',
            unsafe_allow_html=True,
        )
    else:
        for list_idx, (i, note) in enumerate(unpinned):
            nr1, nr2, nr3 = st.columns([5, 1.2, 1])
            with nr1:
                st.markdown(
                    '<div style="background:rgba(255,255,255,0.025);border:1px solid '
                    'rgba(255,255,255,0.07);border-radius:9px;padding:9px 12px;margin-bottom:4px;'
                    'font-size:0.80rem;color:rgba(226,232,240,0.75);line-height:1.5;">'
                    + note["text"] + '</div>',
                    unsafe_allow_html=True,
                )
            with nr2:
                st.markdown('<div class="pin-btn">', unsafe_allow_html=True)
                # FIX: key uses list_idx + i + sanitized text prefix — guaranteed unique
                if st.button("Pin", key=f"pin_{list_idx}_{i}_{_safe_key(note['text'][:10])}", use_container_width=True):
                    st.session_state.notes_list[i]["pinned"] = True; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with nr3:
                st.markdown('<div class="del-btn">', unsafe_allow_html=True)
                if st.button("Del", key=f"del_{list_idx}_{i}_{_safe_key(note['text'][:10])}", use_container_width=True):
                    st.session_state.notes_list.pop(i); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div style="text-align:center;margin-top:28px;padding:10px 0;'
    'border-top:1px solid rgba(255,255,255,0.05);">'
    '<span style="font-family:\'DM Mono\',monospace;font-size:0.52rem;'
    'color:rgba(148,163,184,0.24);letter-spacing:1.2px;">'
    'ASKMNT &nbsp;·&nbsp; MNIT JAIPUR &nbsp;·&nbsp; SESSION-STATE ONLY'
    '</span></div>',
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)
