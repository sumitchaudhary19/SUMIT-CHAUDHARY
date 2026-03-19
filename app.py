# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  AskMNIT — Premium AI Chatbot + Student Dashboard                           ║
# ║  v4.1 — Sticky Navbar, Centered Input Bar                                   ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import streamlit as st
import streamlit.components.v1 as components
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

SIDEBAR_HISTORY = [
    ("Today",       "Attendance analysis request"),
    ("Today",       "Mineral Processing PYQs"),
    ("Yesterday",   "Welding Lab dates"),
    ("Yesterday",   "Exam prep strategy"),
    ("2 days ago",  "Fee payment receipt"),
    ("2 days ago",  "Subject list Sem 6"),
    ("Last week",   "Schedule for Monday"),
    ("Last week",   "CSE branch subjects"),
]

# ─────────────────────────────────────────────────────────────────────────────
# SCHEDULE / GENERAL HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def process_schedule_pdf(file, branch: str) -> dict:
    pool = COMMON_SUBJECTS[:4] + BRANCH_SUBJECTS.get(branch, [])
    random.seed(42)
    TIME_PAIRS = [
        ("08:00","09:00"),("09:30","10:30"),("11:00","12:00"),
        ("12:00","13:00"),("14:00","15:00"),("15:30","16:30"),
    ]
    sched: dict[str, list[dict]] = {}
    for day in DAYS[:6]:
        chosen = sorted(random.sample(range(len(TIME_PAIRS)), k=random.randint(2,4)))
        sched[day] = [
            {"time_start":TIME_PAIRS[ci][0],"time_end":TIME_PAIRS[ci][1],
             "subject":random.choice(pool),
             "room":random.choice(["LT-1","LT-2","Lab-A","Lab-B","CR-3","CR-5"]),
             "type":random.choice(["Lecture","Lecture","Lab","Tutorial"])}
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

def subjects_for_branch(b):   return COMMON_SUBJECTS + BRANCH_SUBJECTS.get(b, [])
def blank_att(s):             return {x: {"present":0,"total":0} for x in s}
def att_pct(r):               return round(r["present"]/r["total"]*100,1) if r["total"] else 0.0
def overall_pct(a):
    tp = sum(r["present"] for r in a.values())
    tt = sum(r["total"] for r in a.values())
    return round(tp/tt*100,1) if tt else 0.0
def status_badge(p):
    if p>=75: return "Safe","#10B981","rgba(16,185,129,0.12)"
    if p>=65: return "Low","#F59E0B","rgba(245,158,11,0.12)"
    return "Critical","#EF4444","rgba(239,68,68,0.12)"
def att_color(p):    return "#10B981" if p>=75 else "#F59E0B" if p>=65 else "#EF4444"
def initials(n):     return "".join(w[0].upper() for w in n.split()[:2]) if n else "??"
def branch_hex(b):   return {"CSE":"#3B82F6","AI & ML":"#8B5CF6","ECE":"#06B6D4","Civil":"#F59E0B","Metallurgy":"#10B981"}.get(b,"#6366F1")
def img_to_b64(f):
    d=f.read(); m=f.type or "image/png"
    return f"data:{m};base64,{base64.b64encode(d).decode()}"
def fmt_time(t: str) -> str:
    try:
        h,m=map(int,t.split(":"))
        return f"{h%12 or 12:02d}:{m:02d} {'AM' if h<12 else 'PM'}"
    except: return t
def _safe_key(s: str) -> str:
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
        {"text":"Mid-sem revision starts Monday","pinned":False},
        {"text":"Submit fee by 17 Mar","pinned":False},
        {"text":"Collect hall ticket from ERP","pinned":False},
    ],
    "ql_feedback":       "",
    "chat_messages":     [],
    "chat_sessions":     [],
    "voice_output":      False,
    "strict_mode":       False,
    "is_recording":      False,
    "planner_overrides": {},
    "show_uploader":     False,
    "chat_theme":        "dark",
    "response_style":    "Concise",
    "attached_file_name":"",
    "voice_transcript":  "",
    "_voice_submit":     False,
    "show_settings_panel": False,
    "show_history_panel":  False,
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
    style = st.session_state.response_style

    def fmt(resp):
        if style == "Bullet Points":
            lines = resp.split("\n")
            return "\n".join(f"• {l}" if l.strip() and not l.startswith(("•","#","*","-","1","2","3","4","5")) else l for l in lines)
        if style == "Detailed":
            return resp + "\n\n---\n*Need more detail? Just ask a follow-up!*"
        return resp

    if any(w in lower for w in ["attendance","present","absent","%"]):
        ov  = overall_pct(att)
        low = [(s,att_pct(r)) for s,r in att.items() if att_pct(r)<75 and r["total"]>0]
        resp = f"**Attendance — {st.session_state.student_name}**\n\nOverall: **{ov}%**\n\n"
        if low:
            resp += "**Below 75%:**\n"
            for s,p in low:
                need = max(0,int((0.75*att[s]["total"]-att[s]["present"])/0.25)+1)
                resp += f"- **{s}**: {p}% — need **{need}** more\n"
        else:
            resp += "All subjects above 75%. Stay consistent!"
        return fmt(resp)

    if any(w in lower for w in ["schedule","class","next","today","timetable"]):
        if st.session_state.schedule_loaded:
            slots = get_today_slots(st.session_state.full_schedule)
            nxt   = get_next_class(slots)
            dn    = datetime.datetime.now().strftime("%A")
            resp  = f"**Today's Classes ({dn})**\n\n"
            for s in slots:
                resp += f"- **{fmt_time(s['time_start'])}–{fmt_time(s['time_end'])}** — {s['subject']} in {s['room']} _({s['type']})_\n"
            if nxt:
                resp += f"\nNext: {nxt['subject']} in **{nxt['minutes_away']} min**"
            else:
                resp += "\nNo more classes today."
            return fmt(resp)
        return "No schedule loaded. Go to **Upload Schedule** on the dashboard."

    if any(w in lower for w in ["pyq","previous year","question paper","past paper"]):
        return fmt(f"**PYQ Resources for {br}**\n\nAccess via PYQs in the dashboard.\n\nBranch subjects: {', '.join(BRANCH_SUBJECTS.get(br,[]))}")

    if any(w in lower for w in ["fee","pay","due","payment"]):
        return fmt("Fee details are in the **Fee Portal** section on the dashboard.")

    if any(w in lower for w in ["subject","syllabus","branch","course"]):
        common   = "\n".join(f"- {s}" for s in COMMON_SUBJECTS)
        branch_s = "\n".join(f"- {s}" for s in BRANCH_SUBJECTS.get(br,[]))
        return fmt(f"**Subjects — {br} · {st.session_state.semester}**\n\n**Common:**\n{common}\n\n**{br} specific:**\n{branch_s}")

    if any(w in lower for w in ["exam","tip","strategy","prepare","study"]):
        first_bs = BRANCH_SUBJECTS.get(br,["your core subject"])[0]
        return fmt(f"**Exam Prep — {br}**\n\n1. **Triage by attendance** — below-75% subjects first.\n2. **PYQ pattern** — last 5 years covers ~70%.\n3. **Block schedule** — 2-hour deep-work slots.\n4. **Group study** — 3-person group for {first_bs}.\n5. **ERP deadlines** — check submissions weekly.")

    if any(w in lower for w in ["hi","hello","hey","hii"]):
        fn = st.session_state.student_name.split()[0]
        return fmt(f"Hey {fn}! 👋 I'm AskMNIT. I can help with:\n\n- Attendance analysis\n- Today's schedule\n- Previous year papers\n- Fee status\n- Exam strategy\n\nYou're on **{br} · {st.session_state.semester}**. What can I help with?")

    if "voice" in lower or "recorded" in lower or "[voice" in lower:
        fn = st.session_state.student_name.split()[0]
        return fmt(f"🎤 Voice message received, {fn}! I heard your question. For best results, try asking about attendance, schedule, PYQs, fees, or exam strategy.")

    if "attached" in lower or "file" in lower:
        return fmt("File received! Tell me what you'd like to do with this file.")

    fn = st.session_state.student_name.split()[0]
    return fmt(f"I'm AskMNIT — built for **{fn}** · **{br}**.\n\n| Topic | Try asking... |\n|---|---|\n| Attendance | _Analyse my attendance_ |\n| Schedule | _What's next today?_ |\n| PYQs | _Find PYQs for my branch_ |\n| Fees | _Check fee due date_ |\n| Exams | _Give me an exam strategy_ |")

def dispatch_message(text: str):
    text = text.strip()
    if not text: return
    st.session_state.chat_messages.append({"role":"user","content":text})
    st.session_state.chat_messages.append({"role":"assistant","content":generate_ai_response(text)})


# ═════════════════════════════════════════════════════════════════════════════
# THEME-AWARE CSS VARIABLES
# ═════════════════════════════════════════════════════════════════════════════
def get_theme_css() -> str:
    is_light = st.session_state.chat_theme == "light"
    if is_light:
        return """
:root {
  --bg:      #F0F4FF;
  --surf:    #FFFFFF;
  --surf2:   #E8EEFF;
  --bar-bg:  #FFFFFF;
  --border:  rgba(0,0,0,0.10);
  --border2: rgba(0,0,0,0.18);
  --text:    #1E2A3A;
  --muted:   rgba(60,80,110,0.60);
  --accent:  #2563EB;
}
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"] {
  background: #F0F4FF !important;
  color: #1E2A3A !important;
}
.gemini-bar [data-testid="stForm"] {
  background: #FFFFFF !important;
  border-color: rgba(37,99,235,0.22) !important;
  box-shadow: 0 4px 24px rgba(37,99,235,0.10) !important;
}
.gemini-bar [data-testid="stTextInput"] input {
  color: #1E2A3A !important;
  caret-color: #2563EB !important;
}
.gemini-bar [data-testid="stTextInput"] input::placeholder {
  color: rgba(60,80,110,0.45) !important;
}
.gemini-bar-anchored {
  background: rgba(240,244,255,0.97) !important;
  border-top-color: rgba(37,99,235,0.15) !important;
}
[data-testid="stChatMessage"] {
  background: rgba(255,255,255,0.85) !important;
  border-color: rgba(0,0,0,0.08) !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
  background: rgba(37,99,235,0.07) !important;
  border-color: rgba(37,99,235,0.15) !important;
}
[data-testid="stSidebar"] {
  background: #FFFFFF !important;
  border-right: 1px solid rgba(37,99,235,0.14) !important;
}
"""
    else:
        return """
:root {
  --bg:      #070B14;
  --surf:    #0B1120;
  --surf2:   #0E1726;
  --bar-bg:  #1A1E2E;
  --border:  rgba(255,255,255,0.08);
  --border2: rgba(255,255,255,0.14);
  --text:    #E2E8F0;
  --muted:   rgba(148,163,184,0.55);
  --accent:  #3B82F6;
}
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"] {
  background: #070B14 !important;
  color: #E2E8F0 !important;
}
"""

# ═════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS  ← PATCH 1: sticky navbar CSS added here
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,700;9..144,900&family=DM+Mono:wght@400;500&family=Outfit:wght@300;400;500;600;700&display=swap');

*, html, body { box-sizing: border-box; margin: 0; padding: 0; }
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"] {
  font-family: 'Outfit', sans-serif !important;
}
header[data-testid="stHeader"], footer, #MainMenu,
[data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
[data-testid="stMainBlockContainer"] { padding: 0 !important; max-width: 100% !important; }

/* ── Sidebar (both views) ── */
[data-testid="stSidebar"] {
  background: #0B1120 !important;
  border-right: 1px solid rgba(59,130,246,0.16) !important;
  min-width: 260px !important; max-width: 260px !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }

.sb-section-header {
  font-family: 'DM Mono', monospace;
  font-size: 0.60rem;
  font-weight: 700;
  color: rgba(148,163,184,0.50);
  text-transform: uppercase;
  letter-spacing: 1.4px;
  padding: 14px 16px 6px;
  border-top: 1px solid rgba(255,255,255,0.05);
  margin-top: 4px;
}
.sb-history-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 16px;
  cursor: pointer;
  border-radius: 0;
  transition: background 0.14s;
  font-size: 0.80rem;
  color: rgba(148,163,184,0.70);
  border-bottom: 1px solid rgba(255,255,255,0.03);
}
.sb-history-item:hover { background: rgba(59,130,246,0.09); color: #BAE6FD; }
.sb-history-dot { width:5px; height:5px; border-radius:50%; background:#3B82F6; flex-shrink:0; }

[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  border-radius: 8px !important;
  color: #E2E8F0 !important;
  font-size: 0.83rem !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] label {
  color: rgba(148,163,184,0.65) !important;
  font-size: 0.70rem !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
}
[data-testid="stSidebar"] .stButton > button {
  background: rgba(239,68,68,0.10) !important;
  border: 1px solid rgba(239,68,68,0.28) !important;
  color: #FCA5A5 !important;
  border-radius: 8px !important;
  font-size: 0.80rem !important;
  font-weight: 600 !important;
  padding: 7px 14px !important;
  box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(239,68,68,0.20) !important; transform: none !important;
}
.sb-theme-dark-btn .stButton > button {
  background: rgba(15,23,42,0.80) !important;
  border: 1.5px solid rgba(59,130,246,0.35) !important;
  color: #60A5FA !important;
  border-radius: 8px !important;
  font-size: 0.80rem !important;
  padding: 7px 12px !important;
  box-shadow: none !important;
}
.sb-theme-dark-btn .stButton > button:hover {
  border-color: rgba(59,130,246,0.65) !important; transform: none !important;
}
.sb-theme-light-btn .stButton > button {
  background: rgba(240,244,255,0.15) !important;
  border: 1.5px solid rgba(148,163,184,0.25) !important;
  color: rgba(226,232,240,0.75) !important;
  border-radius: 8px !important;
  font-size: 0.80rem !important;
  padding: 7px 12px !important;
  box-shadow: none !important;
}
.sb-theme-light-btn .stButton > button:hover {
  background: rgba(240,244,255,0.25) !important; transform: none !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
  background: rgba(255,255,255,0.025) !important;
  border: 1px solid rgba(255,255,255,0.06) !important;
  border-radius: 14px !important;
  font-family: 'Outfit', sans-serif !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
  background: rgba(37,99,235,0.08) !important;
  border-color: rgba(59,130,246,0.16) !important;
}

/* ══════════════════════════════════════════════════════════════════════════
   GEMINI BAR
   ══════════════════════════════════════════════════════════════════════════ */
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
.gemini-bar [data-testid="stForm"] > div:first-child { padding: 0 !important; }
.gemini-bar [data-testid="stHorizontalBlock"] { align-items: center !important; gap: 2px !important; }

/* The outer columns wrapper (attach + form + mic) must align vertically */
.gemini-bar > div[data-testid="stHorizontalBlock"] {
  align-items: stretch !important;
  gap: 0 !important;
}
/* Make attach and mic buttons sit flush with the form pill */
.gemini-bar .gemini-attach,
.gemini-bar .gemini-mic,
.gemini-bar .gemini-mic-active {
  display: flex; align-items: center; height: 100%;
}

.gemini-bar [data-testid="stTextInput"] label { display: none !important; }
.gemini-bar [data-testid="stTextInput"] > div {
  background: transparent !important; border: none !important;
  box-shadow: none !important; padding: 0 !important;
}
.gemini-bar [data-testid="stTextInput"] input {
  background: transparent !important; border: none !important;
  outline: none !important; box-shadow: none !important;
  color: #E2E8F0 !important; font-family: 'Outfit', sans-serif !important;
  font-size: 0.97rem !important; caret-color: #60A5FA !important;
  padding: 11px 8px !important; height: 44px !important;
  border-radius: 0 !important; width: 100% !important;
}
.gemini-bar [data-testid="stTextInput"] input::placeholder { color: rgba(148,163,184,0.38) !important; }
.gemini-bar [data-testid="stTextInput"] input:focus { border: none !important; box-shadow: none !important; outline: none !important; }

.gemini-attach .stButton > button {
  background: transparent !important; border: none !important;
  border-radius: 50% !important; color: rgba(148,163,184,0.55) !important;
  font-size: 1.2rem !important; width: 42px !important; height: 42px !important;
  min-width: 42px !important; padding: 0 !important; box-shadow: none !important;
  transition: background 0.16s, color 0.16s !important;
}
.gemini-attach .stButton > button:hover {
  background: rgba(255,255,255,0.08) !important;
  color: rgba(186,230,253,0.80) !important; transform: none !important; opacity: 1 !important;
}

.gemini-mic .stButton > button {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.09) !important;
  border-radius: 50% !important; color: rgba(148,163,184,0.60) !important;
  font-size: 1.05rem !important; width: 38px !important; height: 38px !important;
  min-width: 38px !important; padding: 0 !important; box-shadow: none !important;
}
.gemini-mic .stButton > button:hover {
  background: rgba(255,255,255,0.09) !important;
  color: rgba(186,230,253,0.80) !important; transform: none !important; opacity: 1 !important;
}

.gemini-mic-active .stButton > button {
  background: rgba(239,68,68,0.18) !important;
  border: 1px solid rgba(239,68,68,0.45) !important;
  border-radius: 50% !important; color: #FCA5A5 !important;
  font-size: 1.05rem !important; width: 38px !important; height: 38px !important;
  min-width: 38px !important; padding: 0 !important;
  animation: micPulse 1.1s ease-in-out infinite !important;
}
@keyframes micPulse {
  0%,100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.40); }
  50%      { box-shadow: 0 0 0 7px rgba(239,68,68,0.00); }
}

.gemini-send [data-testid="stFormSubmitButton"] > button {
  background: linear-gradient(135deg, #2563EB, #4F46E5) !important;
  border: none !important; border-radius: 50% !important;
  color: #fff !important; font-size: 1.25rem !important; font-weight: 700 !important;
  width: 38px !important; height: 38px !important; min-width: 38px !important;
  padding: 0 !important; line-height: 1 !important;
  box-shadow: 0 3px 14px rgba(37,99,235,0.38) !important;
  transition: opacity 0.16s, transform 0.14s !important;
}
.gemini-send [data-testid="stFormSubmitButton"] > button:hover { opacity: 0.88 !important; transform: scale(1.07) !important; }
.gemini-send [data-testid="stFormSubmitButton"] > button:active { transform: scale(0.95) !important; }

.file-chip {
  display: inline-flex; align-items: center; gap: 5px;
  background: rgba(59,130,246,0.15);
  border: 1px solid rgba(59,130,246,0.35);
  border-radius: 20px; padding: 3px 10px 3px 8px;
  font-size: 0.72rem; color: #BAE6FD; font-weight: 600;
  max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  animation: chipIn 0.2s ease both;
  margin-left: 4px; flex-shrink: 0;
}
.file-chip-icon { font-size: 0.85rem; flex-shrink: 0; }
@keyframes chipIn {
  from { opacity:0; transform:scale(0.85); }
  to   { opacity:1; transform:scale(1); }
}

.listening-banner {
  display: flex; align-items: center; gap: 8px;
  margin: 10px auto 0; padding: 8px 18px;
  background: rgba(239,68,68,0.09); border: 1px solid rgba(239,68,68,0.22);
  border-radius: 10px; font-size: 0.80rem; color: #FCA5A5;
  max-width: 800px; animation: fadeInUp 0.25s ease both;
}
.listening-dot {
  width: 7px; height: 7px; border-radius: 50%; background: #EF4444;
  animation: blinkDot 1.1s ease infinite; flex-shrink: 0;
}
@keyframes blinkDot { 0%,100% { opacity:1; } 50% { opacity:0.25; } }

.attach-panel {
  max-width: 800px; margin: 10px auto 4px; padding: 14px 16px;
  background: rgba(59,130,246,0.05); border: 1px dashed rgba(59,130,246,0.28);
  border-radius: 14px; animation: fadeInUp 0.2s ease both;
}

.gemini-bar-anchored {
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 900;
  background: rgba(7,11,20,0.97);
  backdrop-filter: blur(24px) saturate(160%);
  border-top: 1px solid rgba(59,130,246,0.12);
  padding: 10px max(16px, calc((100% - 860px) / 2)) 12px;
}

/* ── Global buttons ── */
.stButton > button {
  background: linear-gradient(135deg,#2563EB,#4F46E5) !important;
  color: #fff !important; border: none !important; border-radius: 9px !important;
  font-family: 'Outfit', sans-serif !important; font-weight: 600 !important;
  font-size: 0.82rem !important; padding: 9px 16px !important;
  box-shadow: 0 3px 14px rgba(37,99,235,0.20) !important;
  transition: all 0.16s ease !important;
}
.stButton > button:hover { opacity: .88 !important; transform: translateY(-1px) !important; }
.stButton > button:active { transform: scale(0.97) !important; }
.nav-pill .stButton > button {
  background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(255,255,255,0.10) !important;
  border-radius: 999px !important; color: rgba(226,232,240,0.72) !important;
  font-size: 0.78rem !important; font-weight: 500 !important;
  padding: 6px 15px !important; box-shadow: none !important;
}
.nav-pill .stButton > button:hover {
  background: rgba(59,130,246,0.16) !important; border-color: rgba(59,130,246,0.38) !important;
  color: #BAE6FD !important; transform: none !important;
}
.nav-back .stButton > button {
  background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(255,255,255,0.12) !important;
  border-radius: 10px !important; color: rgba(226,232,240,0.65) !important;
  font-size: 0.78rem !important; font-weight: 600 !important;
  padding: 6px 14px !important; box-shadow: none !important;
}
.nav-back .stButton > button:hover {
  background: rgba(59,130,246,0.14) !important; color: #BAE6FD !important;
  border-color: rgba(59,130,246,0.30) !important;
}
.sug-pill .stButton > button {
  background: rgba(255,255,255,0.04) !important; border: 1px solid rgba(255,255,255,0.10) !important;
  border-radius: 999px !important; color: rgba(186,230,253,0.74) !important;
  font-size: 0.79rem !important; font-weight: 500 !important;
  padding: 9px 18px !important; box-shadow: none !important;
}
.sug-pill .stButton > button:hover {
  background: rgba(59,130,246,0.14) !important; border-color: rgba(59,130,246,0.34) !important;
  color: #BAE6FD !important; transform: translateY(-2px) !important;
}
.ghost-btn .stButton > button {
  background: rgba(255,255,255,.05) !important; border: 1px solid rgba(255,255,255,0.14) !important;
  color: rgba(226,232,240,.55) !important; box-shadow: none !important;
}
.ghost-btn .stButton > button:hover { background: rgba(59,130,246,.10) !important; color: #E2E8F0 !important; }
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
  background: rgba(245,158,11,0.10) !important; border: 1px solid rgba(245,158,11,0.28) !important;
  color: #FCD34D !important; box-shadow: none !important;
  font-size: 0.70rem !important; padding: 4px 10px !important; border-radius: 7px !important;
}
.pin-btn .stButton > button:hover { background: rgba(245,158,11,0.20) !important; transform: none !important; }
.del-btn .stButton > button {
  background: rgba(239,68,68,0.07) !important; border: 1px solid rgba(239,68,68,0.18) !important;
  color: rgba(252,165,165,0.70) !important; box-shadow: none !important;
  font-size: 0.68rem !important; padding: 3px 8px !important; border-radius: 6px !important;
}
.del-btn .stButton > button:hover { background: rgba(239,68,68,0.16) !important; transform: none !important; }
.ql-btn .stButton > button {
  background: rgba(255,255,255,.03) !important; border: 1px solid rgba(255,255,255,0.14) !important;
  color: rgba(186,230,253,.65) !important; box-shadow: none !important;
  text-align: left !important; justify-content: flex-start !important;
  font-size: 0.80rem !important; padding: 9px 14px !important; border-radius: 9px !important;
}
.ql-btn .stButton > button:hover {
  background: rgba(59,130,246,.10) !important; border-color: rgba(59,130,246,.28) !important;
  color: #BAE6FD !important; transform: none !important;
}
.logout-btn .stButton > button {
  background: rgba(239,68,68,.09) !important; border: 1px solid rgba(239,68,68,.20) !important;
  color: #FCA5A5 !important; box-shadow: none !important; font-size: 0.80rem !important;
}
.logout-btn .stButton > button:hover { background: rgba(239,68,68,.18) !important; }
.open-chat-btn .stButton > button {
  background: linear-gradient(135deg,#059669,#10B981) !important;
  border-radius: 12px !important; font-weight: 700 !important;
  font-size: 0.88rem !important; padding: 11px 22px !important;
  box-shadow: 0 5px 24px rgba(16,185,129,.36) !important; font-family: 'DM Mono',monospace !important;
}
.open-chat-btn .stButton > button:hover {
  box-shadow: 0 7px 32px rgba(16,185,129,.50) !important; transform: translateY(-2px) !important;
}
.settings-menu-btn .stButton > button {
  background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(255,255,255,0.12) !important;
  color: rgba(226,232,240,0.75) !important; box-shadow: none !important;
  font-size: 0.82rem !important; font-weight: 600 !important;
  padding: 8px 16px !important; border-radius: 10px !important;
}
.settings-menu-btn .stButton > button:hover {
  background: rgba(59,130,246,0.13) !important; color: #BAE6FD !important;
  border-color: rgba(59,130,246,0.30) !important;
}
.nav-btn .stButton > button {
  background: transparent !important; color: rgba(148,163,184,.65) !important;
  border: none !important; box-shadow: none !important;
  text-align: left !important; justify-content: flex-start !important;
  padding: 10px 14px !important; font-size: 0.83rem !important;
  font-weight: 500 !important; border-radius: 8px !important;
}
.nav-btn .stButton > button:hover { background: rgba(59,130,246,.10) !important; color: #BAE6FD !important; transform: none !important; }
.nav-btn-active .stButton > button {
  background: rgba(59,130,246,.14) !important; color: #60A5FA !important;
  border-left: 2px solid #3B82F6 !important; font-weight: 700 !important; box-shadow: none !important;
}

/* ── Text inputs ── */
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
  background: rgba(255,255,255,0.04) !important; border: 1px solid rgba(255,255,255,0.14) !important;
  border-radius: 10px !important; color: #E2E8F0 !important;
  font-family: 'Outfit', sans-serif !important; font-size: 0.87rem !important;
}
[data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
  border-color: rgba(59,130,246,0.55) !important;
  box-shadow: 0 0 0 2.5px rgba(59,130,246,0.13) !important;
}
[data-testid="stTextInput"] label, [data-testid="stTextArea"] label {
  color: rgba(148,163,184,0.55) !important; font-size: 0.70rem !important;
  font-weight: 600 !important; text-transform: uppercase !important;
  letter-spacing: 0.6px !important;
}
[data-testid="stSelectbox"] > div > div {
  background: rgba(255,255,255,0.04) !important; border: 1px solid rgba(255,255,255,0.14) !important;
  border-radius: 10px !important; color: #E2E8F0 !important;
}
[data-testid="stSelectbox"] label {
  color: rgba(148,163,184,0.55) !important; font-size: 0.70rem !important;
  font-weight: 600 !important; text-transform: uppercase !important;
}
[data-testid="stFileUploader"] {
  background: rgba(59,130,246,0.04) !important;
  border: 1px dashed rgba(59,130,246,0.26) !important; border-radius: 12px !important;
}
[data-testid="stToggle"] label { color: #E2E8F0 !important; font-size: 0.86rem !important; }

/* ── Popovers ── */
[data-testid="stPopover"] > div {
  background: #0D1828 !important; border: 1px solid rgba(59,130,246,0.30) !important;
  border-radius: 16px !important; box-shadow: 0 16px 56px rgba(0,0,0,0.65) !important;
}
button[data-testid="stPopoverButton"] {
  background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(255,255,255,0.10) !important;
  border-radius: 999px !important; color: rgba(226,232,240,0.72) !important;
  font-size: 0.78rem !important; font-weight: 500 !important;
  padding: 6px 15px !important; box-shadow: none !important;
}
button[data-testid="stPopoverButton"]:hover {
  background: rgba(59,130,246,0.16) !important;
  border-color: rgba(59,130,246,0.38) !important; color: #BAE6FD !important;
}

/* ── Progress / Expanders / Misc ── */
[data-testid="stProgress"] > div > div { border-radius: 99px !important; background: linear-gradient(90deg,#2563EB,#22D3EE) !important; }
[data-testid="stProgress"] > div { background: rgba(255,255,255,.07) !important; border-radius: 99px !important; height: 5px !important; }
[data-testid="stExpander"] { background: rgba(255,255,255,.018) !important; border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 12px !important; }
summary { font-family: 'Outfit',sans-serif !important; font-weight: 600 !important; }
h1,h2,h3,h4 { font-family: 'DM Mono', monospace !important; font-weight: 500 !important; }
[data-testid="stMarkdown"] p, [data-testid="stMarkdown"] li { color: rgba(226,232,240,.72) !important; font-family: 'Outfit',sans-serif !important; }
hr { border-color: rgba(255,255,255,0.08) !important; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(59,130,246,.22); border-radius: 4px; }
[data-testid="column"] { padding: 0 4px !important; }

/* ══════════════════════════════════════════════════════════════════
   PATCH 1 — Chat view sticky/fixed top navbar
   ══════════════════════════════════════════════════════════════════ */
.chat-navbar-wrap {
  position: fixed;
  top: 0 !important; left: 0 !important; right: 0 !important;
  z-index: 9999;
  background: rgba(7,11,20,0.97);
  backdrop-filter: blur(24px) saturate(200%);
  -webkit-backdrop-filter: blur(24px) saturate(200%);
  border-bottom: 1px solid rgba(59,130,246,0.18);
  box-shadow: 0 4px 28px rgba(0,0,0,0.55);
}
.chat-navbar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 9px 24px;
}
.chat-navbar-logo {
  display: flex; align-items: center; gap: 9px;
}
.chat-navbar-logo-icon {
  width: 28px; height: 28px; border-radius: 8px;
  background: linear-gradient(135deg,#2563EB,#4F46E5);
  display: flex; align-items: center; justify-content: center;
  font-size: 0.82rem; font-weight: 700; color: white;
  box-shadow: 0 3px 12px rgba(37,99,235,0.28);
}
/* Spacer pushes content below the fixed navbar */
.chat-navbar-spacer { height: 58px; width: 100%; }

/* ── Animations ── */
@keyframes fadeUp { from { opacity:0; transform:translateY(18px); } to { opacity:1; transform:translateY(0); } }
@keyframes slideUp { from { opacity:0; transform:translateY(24px); } to { opacity:1; transform:translateY(0); } }
@keyframes fadeInUp { from { opacity:0; transform:translateY(-6px); } to { opacity:1; transform:translateY(0); } }
@keyframes pinPulse { 0%,100% { box-shadow:0 0 0 0 rgba(245,158,11,.30); } 50% { box-shadow:0 0 0 6px rgba(245,158,11,.00); } }
.pinned-note-card { animation: pinPulse 2.5s ease infinite; }
.chat-scroll-area { padding-bottom: 140px; }
</style>
""", unsafe_allow_html=True)

# Inject theme CSS dynamically
st.markdown(f"<style>{get_theme_css()}</style>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# FEATURE 2: NATIVE FILE PICKER COMPONENT
# ═════════════════════════════════════════════════════════════════════════════
def render_native_file_picker(picker_id: str):
    qp = st.query_params
    fname = qp.get(f"fp_{picker_id}", "")

    picker_html = f"""
<div id="picker-{picker_id}" style="display:none;">
  <input type="file" id="fileinput-{picker_id}"
    accept=".pdf,.txt,.png,.jpg,.jpeg,.docx,.csv,.mp4,.zip"
    style="position:absolute;width:1px;height:1px;opacity:0;pointer-events:none;"
    onchange="handleFileChange_{picker_id}(this)">
</div>
<script>
window.triggerFilePicker_{picker_id} = function() {{
  document.getElementById('fileinput-{picker_id}').click();
}};
function handleFileChange_{picker_id}(input) {{
  if (!input.files || !input.files[0]) return;
  var fname = input.files[0].name;
  var url = new URL(window.parent.location.href);
  url.searchParams.set('fp_{picker_id}', fname);
  window.parent.history.replaceState(null, '', url.toString());
  window.parent.postMessage({{type:'streamlit:forceRerun', filename: fname}}, '*');
  setTimeout(function() {{ window.parent.location.href = url.toString(); }}, 100);
}}
window.addEventListener('message', function(e) {{
  if (e.data && e.data.type === 'triggerPicker_{picker_id}') {{
    document.getElementById('fileinput-{picker_id}').click();
  }}
}});
</script>
"""
    components.html(picker_html, height=0, scrolling=False)
    return fname


# ═════════════════════════════════════════════════════════════════════════════
# FEATURE 3: VOICE RECORDER COMPONENT
# ═════════════════════════════════════════════════════════════════════════════
def render_voice_recorder(recorder_id: str) -> str | None:
    qp = st.query_params
    voice_done = qp.get(f"vr_{recorder_id}", "")

    recorder_html = f"""
<div id="recorder-{recorder_id}" style="display:none;"></div>
<script>
(function() {{
  var mediaRecorder = null;
  var audioChunks = [];
  var isRecording = false;
  window.addEventListener('message', function(evt) {{
    var d = evt.data;
    if (!d || !d.type) return;
    if (d.type === 'startRecording_{recorder_id}') {{ startRec(); }}
    else if (d.type === 'stopRecording_{recorder_id}') {{ stopRec(); }}
  }});
  function startRec() {{
    if (isRecording) return;
    navigator.mediaDevices.getUserMedia({{ audio: true }}).then(function(stream) {{
      audioChunks = [];
      var options = {{ mimeType: 'audio/webm' }};
      try {{ mediaRecorder = new MediaRecorder(stream, options); }}
      catch(e) {{ mediaRecorder = new MediaRecorder(stream); }}
      mediaRecorder.ondataavailable = function(e) {{
        if (e.data && e.data.size > 0) audioChunks.push(e.data);
      }};
      mediaRecorder.onstop = function() {{
        var blob = new Blob(audioChunks, {{ type: 'audio/webm' }});
        var reader = new FileReader();
        reader.onloadend = function() {{
          var url = new URL(window.parent.location.href);
          url.searchParams.set('vr_{recorder_id}', 'DONE');
          url.searchParams.set('vr_{recorder_id}_ts', Date.now().toString());
          window.parent.history.replaceState(null, '', url.toString());
          setTimeout(function() {{ window.parent.location.href = url.toString(); }}, 80);
        }};
        reader.readAsDataURL(blob);
        stream.getTracks().forEach(function(t) {{ t.stop(); }});
        isRecording = false;
      }};
      mediaRecorder.start(200);
      isRecording = true;
      window.parent.postMessage({{ type: 'recordingStarted_{recorder_id}' }}, '*');
    }}).catch(function(err) {{
      window.parent.postMessage({{ type: 'micError_{recorder_id}', error: err.message }}, '*');
    }});
  }}
  function stopRec() {{
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {{ mediaRecorder.stop(); }}
    isRecording = false;
  }}
  window.startRecording_{recorder_id} = startRec;
  window.stopRecording_{recorder_id}  = stopRec;
}})();
</script>
"""
    components.html(recorder_html, height=0, scrolling=False)
    return voice_done if voice_done == "DONE" else None


# ═════════════════════════════════════════════════════════════════════════════
# GEMINI INPUT BAR
# ═════════════════════════════════════════════════════════════════════════════
def render_gemini_bar(bar_key: str, hero_mode: bool = True):
    """
    BUG FIX v2: 📎 and 🎤 are now st.button (OUTSIDE the form).
    Only ↑ (send) is a form_submit_button inside the form.
    This means Enter key ONLY triggers Send — never Attach or Mic.
    Layout: [📎] [___text input + ↑ send___] [🎤]
    📎 and 🎤 are overlaid left/right using CSS absolute positioning.
    """
    recording  = st.session_state.is_recording
    mic_class  = "gemini-mic-active" if recording else "gemini-mic"
    mic_icon   = "⏹" if recording else "🎤"
    anim_style = "animation:slideUp 0.35s cubic-bezier(0.22,0.61,0.36,1) both;" if hero_mode else ""

    # File chip above bar
    chip_html = ""
    if st.session_state.attached_file_name:
        fname = st.session_state.attached_file_name
        short = fname if len(fname) <= 18 else fname[:15] + "..."
        chip_html = (
            f'<div class="file-chip" title="{fname}">'
            f'<span class="file-chip-icon">📎</span>{short}'
            f'<button onclick="clearChip_{bar_key}()" style="background:none;border:none;'
            f'color:rgba(148,163,184,0.5);cursor:pointer;font-size:0.75rem;'
            f'margin-left:4px;padding:0 4px;" title="Remove file">✕</button>'
            f'</div>'
        )

    # Outer wrapper
    st.markdown(
        f'<div class="gemini-bar" style="max-width:780px;width:100%;margin:0 auto;{anim_style}">',
        unsafe_allow_html=True,
    )

    if chip_html:
        st.markdown(
            f'<div style="display:flex;align-items:center;padding:0 16px 6px;">{chip_html}</div>',
            unsafe_allow_html=True,
        )

    # ── Row: [attach_btn] [FORM: text + send] [mic_btn] ──────────────────
    # attach and mic are st.button (outside form) → Enter never triggers them
    outer_cols = st.columns([0.55, 10, 0.65])

    with outer_cols[0]:
        st.markdown('<div class="gemini-attach">', unsafe_allow_html=True)
        attach_clicked = st.button("📎", key=f"attach_{bar_key}", help="Attach file")
        st.markdown('</div>', unsafe_allow_html=True)

    with outer_cols[1]:
        # Form contains ONLY text input + send button
        # Enter key in text_input submits this form → triggers send_clicked
        with st.form(key=f"gemini_form_{bar_key}", clear_on_submit=True):
            f_input_col, f_send_col = st.columns([12, 0.75])
            with f_input_col:
                placeholder = (
                    "Ask AskMNIT..."
                    if not st.session_state.attached_file_name
                    else "Add a message about the file..."
                )
                user_text = st.text_input(
                    label="__gi__",
                    placeholder=placeholder,
                    key=f"gi_text_{bar_key}",
                    label_visibility="collapsed",
                )
            with f_send_col:
                st.markdown('<div class="gemini-send">', unsafe_allow_html=True)
                send_clicked = st.form_submit_button("↑", help="Send")
                st.markdown('</div>', unsafe_allow_html=True)

    with outer_cols[2]:
        st.markdown(f'<div class="{mic_class}">', unsafe_allow_html=True)
        mic_clicked = st.button(mic_icon, key=f"mic_{bar_key}", help="Voice input")
        st.markdown('</div>', unsafe_allow_html=True)

    # JS utility
    st.markdown(f"""
    <script>
    function clearChip_{bar_key}() {{
      var url = new URL(window.location.href);
      url.searchParams.delete('fp_{bar_key}');
      window.location.href = url.toString();
    }}
    </script>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close .gemini-bar

    # ── Return action ─────────────────────────────────────────────────────
    if mic_clicked:
        return ("mic", "stop" if recording else "start")
    if attach_clicked:
        return ("attach",)
    if send_clicked:
        txt = (user_text or "").strip()
        if txt or st.session_state.attached_file_name:
            full = txt
            if st.session_state.attached_file_name and not txt:
                full = f"[File attached: {st.session_state.attached_file_name}]"
            elif st.session_state.attached_file_name:
                full = f"{txt} [File: {st.session_state.attached_file_name}]"
            return ("send", full)
    return None


# ═════════════════════════════════════════════════════════════════════════════
# SHARED SIDEBAR
# ═════════════════════════════════════════════════════════════════════════════
def render_chat_sidebar():
    with st.sidebar:
        st.markdown(
            '<div style="padding:18px 16px 14px;border-bottom:1px solid rgba(59,130,246,0.14);">'
            '<div style="display:flex;align-items:center;gap:9px;">'
            '<div style="width:32px;height:32px;border-radius:9px;'
            'background:linear-gradient(135deg,#2563EB,#4F46E5);'
            'display:flex;align-items:center;justify-content:center;'
            'font-size:0.95rem;font-weight:700;color:white;'
            'box-shadow:0 3px 12px rgba(37,99,235,0.30);">A</div>'
            '<div>'
            '<div style="font-family:\'DM Mono\',monospace;font-size:0.87rem;color:#E2E8F0;font-weight:500;">AskMNIT AI</div>'
            '<div style="font-size:0.57rem;color:rgba(148,163,184,.40);margin-top:1px;">Smart Campus Assistant</div>'
            '</div></div></div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sb-section-header">⏱️ Chat History</div>', unsafe_allow_html=True)

        if st.session_state.chat_sessions:
            st.markdown(
                '<div style="font-size:0.60rem;color:rgba(59,130,246,0.60);'
                'padding:4px 16px 2px;text-transform:uppercase;letter-spacing:0.6px;">This session</div>',
                unsafe_allow_html=True,
            )
            for i, sess in enumerate(reversed(st.session_state.chat_sessions[-3:])):
                label = sess["label"][:28] + ("..." if len(sess["label"]) > 28 else "")
                col_h, col_b = st.columns([5, 1])
                with col_h:
                    st.markdown(
                        f'<div class="sb-history-item"><div class="sb-history-dot"></div>{label}</div>',
                        unsafe_allow_html=True,
                    )
                with col_b:
                    st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
                    if st.button("↩", key=f"sb_load_{i}"):
                        st.session_state.chat_messages = list(sess["messages"]); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        current_day = ""
        for day_lbl, title in SIDEBAR_HISTORY:
            if day_lbl != current_day:
                current_day = day_lbl
                st.markdown(
                    f'<div style="font-size:0.60rem;color:rgba(148,163,184,0.38);'
                    f'padding:6px 16px 2px;text-transform:uppercase;letter-spacing:0.6px;">{day_lbl}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown(
                f'<div class="sb-history-item"><div class="sb-history-dot" style="background:rgba(148,163,184,0.30);"></div>{title}</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="sb-section-header">⚙️ Chatbot Settings</div>', unsafe_allow_html=True)
        st.markdown('<div style="padding:8px 16px 4px;">', unsafe_allow_html=True)

        new_style = st.selectbox(
            "Response Style",
            ["Concise", "Detailed", "Bullet Points"],
            index=["Concise","Detailed","Bullet Points"].index(st.session_state.response_style),
            key="sb_response_style",
        )
        if new_style != st.session_state.response_style:
            st.session_state.response_style = new_style
            st.rerun()

        st.session_state.strict_mode = st.toggle(
            "Strict Academic Mode", value=st.session_state.strict_mode, key="sb_strict",
        )
        st.session_state.voice_output = st.toggle(
            "Voice Output", value=st.session_state.voice_output, key="sb_voice_out",
        )

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("🗑 Clear All Chats", key="sb_clear_chats"):
            st.session_state.chat_messages  = []
            st.session_state.chat_sessions  = []
            st.session_state.show_uploader  = False
            st.session_state.attached_file_name = ""
            st.toast("All chats cleared.", icon="🗑")
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sb-section-header">🌗 Theme</div>', unsafe_allow_html=True)
        st.markdown('<div style="padding:8px 16px 14px;display:flex;gap:8px;">', unsafe_allow_html=True)

        t1, t2 = st.columns(2)
        with t1:
            active_dark = st.session_state.chat_theme == "dark"
            btn_label_d = "🟢 Dark" if active_dark else "Dark"
            st.markdown('<div class="sb-theme-dark-btn">', unsafe_allow_html=True)
            if st.button(btn_label_d, key="sb_theme_dark", use_container_width=True):
                st.session_state.chat_theme = "dark"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with t2:
            active_light = st.session_state.chat_theme == "light"
            btn_label_l = "⚪ Light" if not active_light else "🟡 Light"
            st.markdown('<div class="sb-theme-light-btn">', unsafe_allow_html=True)
            if st.button(btn_label_l, key="sb_theme_light", use_container_width=True):
                st.session_state.chat_theme = "light"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(
            '<div style="padding:10px 16px;border-top:1px solid rgba(255,255,255,0.05);margin-top:auto;">'
            f'<div style="font-size:0.60rem;color:rgba(148,163,184,0.30);font-family:\'DM Mono\',monospace;">'
            f'{st.session_state.student_name} · {st.session_state.branch}'
            '</div></div>',
            unsafe_allow_html=True,
        )


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
    [data-testid="stSidebar"] { display: flex !important; }
    [data-testid="stSidebarCollapseButton"] { display: flex !important; }
    [data-testid="collapsedControl"] { display: flex !important; }
    [data-testid="stMainBlockContainer"] { padding: 0 !important; max-width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

    render_chat_sidebar()

    has_messages = len(st.session_state.chat_messages) > 0

    for rkey in ["hero", "anchored"]:
        qp = st.query_params
        vdone = qp.get(f"vr_{rkey}", "")
        if vdone == "DONE" and not st.session_state.get("_voice_submit"):
            st.session_state._voice_submit    = True
            st.session_state.is_recording     = False
            st.session_state.voice_transcript = "[Voice message recorded]"
            try:
                del st.query_params[f"vr_{rkey}"]
                st.query_params.pop(f"vr_{rkey}_ts", None)
            except Exception:
                pass

    if st.session_state._voice_submit:
        st.session_state._voice_submit = False
        msg = st.session_state.voice_transcript or "[Voice message]"
        st.session_state.voice_transcript = ""
        dispatch_message(f"🎤 {msg}")
        st.toast("Voice message sent!", icon="🎤")
        st.rerun()

    for rkey in ["hero", "anchored"]:
        qp = st.query_params
        fpname = qp.get(f"fp_{rkey}", "")
        if fpname and fpname != st.session_state.attached_file_name:
            st.session_state.attached_file_name = fpname
            st.toast(f"📎 {fpname} selected!", icon="✅")
            try: del st.query_params[f"fp_{rkey}"]
            except Exception: pass
            st.rerun()

    # ── Navbar button actions via session_state flags (NOT query params) ──────
    # Buttons set ss flags directly → rerun → flags read here → action taken
    # This avoids the URL-replace bug where ?nav_action= clears session state
    if st.session_state.get("_nav_new_chat"):
        st.session_state._nav_new_chat = False
        if st.session_state.chat_messages:
            fu = next((m["content"][:38] for m in st.session_state.chat_messages if m["role"]=="user"), "Session")
            st.session_state.chat_sessions.append({"label": fu+"...", "messages": list(st.session_state.chat_messages)})
        st.session_state.chat_messages = []
        st.session_state.show_uploader = False
        st.session_state.attached_file_name = ""
        st.rerun()

    if st.session_state.get("_nav_dashboard"):
        st.session_state._nav_dashboard = False
        st.session_state.view = "dashboard"
        st.rerun()

    # ── FIXED NAVBAR — pure Streamlit buttons inside columns ─────────────
    # Rendered BEFORE content so spacer pushes content down
    st.markdown("""
    <style>
    /* Fixed navbar strip */
    div[data-testid="stVerticalBlock"] > div:first-child > div[data-testid="stHorizontalBlock"].navbar-row {
      position: fixed !important; top:0 !important; left:0 !important; right:0 !important;
    }
    .askmnt-navbar {
      position: fixed;
      top: 0; left: 0; right: 0; z-index: 99999;
      height: 52px;
      background: rgba(7,11,20,0.98);
      backdrop-filter: blur(24px) saturate(200%);
      -webkit-backdrop-filter: blur(24px) saturate(200%);
      border-bottom: 1px solid rgba(59,130,246,0.18);
      box-shadow: 0 2px 24px rgba(0,0,0,0.65);
      display: flex; align-items: center;
      justify-content: space-between;
      padding: 0 20px;
    }
    .askmnt-nb-left { display:flex; align-items:center; gap:8px; }
    .askmnt-nb-logo-icon {
      width:28px; height:28px; border-radius:8px;
      background:linear-gradient(135deg,#2563EB,#4F46E5);
      display:flex; align-items:center; justify-content:center;
      font-size:0.82rem; font-weight:700; color:#fff;
      box-shadow:0 3px 10px rgba(37,99,235,0.35); flex-shrink:0;
    }
    .askmnt-nb-logo-name {
      font-family:'DM Mono',monospace; font-size:0.87rem;
      color:#E2E8F0; font-weight:500;
    }
    .askmnt-nb-logo-dot { font-size:0.50rem; color:#10B981; font-weight:700; margin-left:2px; }
    .askmnt-nb-right { display:flex; align-items:center; gap:7px; }
    /* Pill button base */
    .nb-pill {
      display:inline-flex; align-items:center; justify-content:center;
      padding:5px 14px; border-radius:999px; cursor:pointer;
      font-family:'Outfit',sans-serif; font-size:0.77rem; font-weight:500;
      border:1px solid rgba(255,255,255,0.10);
      background:rgba(255,255,255,0.06);
      color:rgba(226,232,240,0.80);
      transition:all 0.15s ease; white-space:nowrap; text-decoration:none;
      user-select:none;
    }
    .nb-pill:hover { background:rgba(59,130,246,0.18); border-color:rgba(59,130,246,0.40); color:#BAE6FD; }
    .nb-pill-blue { background:rgba(59,130,246,0.13); border-color:rgba(59,130,246,0.32); color:#93C5FD; }
    .nb-pill-blue:hover { background:rgba(59,130,246,0.26); border-color:rgba(59,130,246,0.58); color:#BAE6FD; }
    .askmnt-navbar-spacer { height:60px; width:100%; }
    .askmnt-navbar-divider {
      height:1px;
      background:linear-gradient(90deg,transparent,rgba(59,130,246,0.28),rgba(34,211,238,0.12),transparent);
      margin-bottom:4px;
    }

    /* ── Chat History Modal ── */
    .ch-overlay {
      position:fixed; inset:0; z-index:99998;
      background:rgba(0,0,0,0.55);
      backdrop-filter:blur(6px);
      display:flex; align-items:flex-start; justify-content:center;
      padding-top:64px;
      animation:fadeIn 0.18s ease;
    }
    .ch-panel {
      width:min(520px,92vw);
      max-height:72vh;
      background:#0B1120;
      border:1px solid rgba(59,130,246,0.22);
      border-radius:18px;
      box-shadow:0 24px 80px rgba(0,0,0,0.70);
      overflow:hidden;
      display:flex; flex-direction:column;
      animation:slideDown 0.22s cubic-bezier(0.22,0.61,0.36,1);
    }
    .ch-header {
      display:flex; align-items:center; justify-content:space-between;
      padding:16px 20px 12px;
      border-bottom:1px solid rgba(255,255,255,0.06);
      flex-shrink:0;
    }
    .ch-title {
      font-family:'DM Mono',monospace; font-size:0.72rem;
      color:rgba(148,163,184,0.55); text-transform:uppercase; letter-spacing:1.2px;
    }
    .ch-close {
      width:26px; height:26px; border-radius:50%;
      background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.10);
      color:rgba(148,163,184,0.60); font-size:0.82rem; cursor:pointer;
      display:flex; align-items:center; justify-content:center;
      transition:all 0.14s;
    }
    .ch-close:hover { background:rgba(239,68,68,0.15); border-color:rgba(239,68,68,0.35); color:#FCA5A5; }
    .ch-list { overflow-y:auto; padding:12px 14px; flex:1; }
    .ch-list::-webkit-scrollbar { width:3px; }
    .ch-list::-webkit-scrollbar-thumb { background:rgba(59,130,246,0.25); border-radius:3px; }
    .ch-capsule {
      display:flex; align-items:center; justify-content:space-between;
      background:rgba(255,255,255,0.030);
      border:1px solid rgba(255,255,255,0.07);
      border-radius:12px; padding:11px 14px; margin-bottom:8px;
      transition:all 0.14s; cursor:pointer;
    }
    .ch-capsule:hover { background:rgba(59,130,246,0.08); border-color:rgba(59,130,246,0.22); }
    .ch-capsule-pinned {
      border-color:rgba(245,158,11,0.28);
      background:rgba(245,158,11,0.05);
    }
    .ch-capsule-label {
      font-size:0.82rem; color:rgba(226,232,240,0.80);
      font-family:'Outfit',sans-serif; font-weight:500;
      flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
      margin-right:10px;
    }
    .ch-capsule-actions { display:flex; align-items:center; gap:5px; flex-shrink:0; }
    .ch-action-btn {
      font-size:0.68rem; padding:3px 9px; border-radius:6px; cursor:pointer;
      font-family:'Outfit',sans-serif; font-weight:600; border:1px solid;
      transition:all 0.14s; background:transparent;
    }
    .ch-pin-btn { color:#FCD34D; border-color:rgba(245,158,11,0.28); }
    .ch-pin-btn:hover { background:rgba(245,158,11,0.14); }
    .ch-del-btn { color:rgba(252,165,165,0.70); border-color:rgba(239,68,68,0.20); }
    .ch-del-btn:hover { background:rgba(239,68,68,0.14); color:#FCA5A5; }
    .ch-empty {
      text-align:center; padding:36px 20px;
      font-size:0.80rem; color:rgba(148,163,184,0.40);
      font-family:'Outfit',sans-serif;
    }
    @keyframes slideDown { from { opacity:0; transform:translateY(-14px); } to { opacity:1; transform:translateY(0); } }
    @keyframes fadeIn { from { opacity:0; } to { opacity:1; } }

    /* ── Settings Modal ── */
    .st-modal-overlay {
      position:fixed; inset:0; z-index:99998;
      background:rgba(0,0,0,0.55);
      backdrop-filter:blur(6px);
      display:flex; align-items:flex-start; justify-content:center;
      padding-top:64px;
      animation:fadeIn 0.18s ease;
    }
    .st-modal-panel {
      width:min(480px,92vw);
      background:#0B1120;
      border:1px solid rgba(59,130,246,0.22);
      border-radius:18px;
      box-shadow:0 24px 80px rgba(0,0,0,0.70);
      overflow:hidden;
      animation:slideDown 0.22s cubic-bezier(0.22,0.61,0.36,1);
    }
    .st-modal-header {
      display:flex; align-items:center; justify-content:space-between;
      padding:16px 20px 14px;
      border-bottom:1px solid rgba(255,255,255,0.06);
    }
    .st-modal-title {
      font-family:'DM Mono',monospace; font-size:0.72rem;
      color:rgba(148,163,184,0.55); text-transform:uppercase; letter-spacing:1.2px;
    }
    .st-modal-body { padding:18px 20px 22px; }
    .st-setting-row {
      display:flex; align-items:center; justify-content:space-between;
      padding:12px 0; border-bottom:1px solid rgba(255,255,255,0.05);
    }
    .st-setting-row:last-child { border-bottom:none; }
    .st-setting-label {
      font-family:'Outfit',sans-serif; font-size:0.86rem;
      color:rgba(226,232,240,0.80); font-weight:500;
    }
    .st-setting-desc {
      font-size:0.68rem; color:rgba(148,163,184,0.45); margin-top:2px;
    }
    .theme-toggle-group { display:flex; gap:6px; }
    .theme-btn {
      padding:5px 14px; border-radius:8px; cursor:pointer;
      font-family:'Outfit',sans-serif; font-size:0.75rem; font-weight:600;
      border:1px solid rgba(255,255,255,0.10);
      background:rgba(255,255,255,0.05); color:rgba(226,232,240,0.60);
      transition:all 0.14s;
    }
    .theme-btn-active-dark {
      background:rgba(15,23,42,0.90); border-color:rgba(59,130,246,0.45);
      color:#60A5FA;
    }
    .theme-btn-active-light {
      background:rgba(240,244,255,0.15); border-color:rgba(148,163,184,0.40);
      color:#E2E8F0;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Render the fixed navbar HTML (logo only - buttons rendered by Streamlit below) ──
    st.markdown("""
    <div class="askmnt-navbar">
      <div class="askmnt-nb-left">
        <div class="askmnt-nb-logo-icon">A</div>
        <span class="askmnt-nb-logo-name">AskMNIT</span>
        <span class="askmnt-nb-logo-dot">&#9679; AI</span>
      </div>
    </div>
    <div class="askmnt-navbar-spacer"></div>
    <div class="askmnt-navbar-divider"></div>
    """, unsafe_allow_html=True)





    # ── Actual st.buttons for navbar — hidden via CSS, triggered via JS ────
    # These REAL Streamlit buttons are visually hidden (CSS above hides them).
    # The HTML navbar's onclick calls triggerNbBtn() which clicks the real button.
    # This is the ONLY reliable way to communicate HTML→Streamlit.
    _nb_container = st.container()
    with _nb_container:
        st.markdown("""
        <style>
        /* Hide the real st.button navbar row from normal flow */
        div[data-nb-buttons="true"] {
          position: fixed !important;
          top: 8px !important; right: 14px !important;
          z-index: 100000 !important;
          display: flex !important; gap: 6px !important;
          align-items: center !important;
          pointer-events: auto !important;
        }
        div[data-nb-buttons="true"] .stButton > button {
          border-radius: 999px !important;
          padding: 5px 13px !important;
          font-size: 0.76rem !important; font-weight: 500 !important;
          height: 34px !important; min-height: 34px !important;
          border: 1px solid rgba(255,255,255,0.11) !important;
          background: rgba(255,255,255,0.06) !important;
          color: rgba(226,232,240,0.80) !important;
          box-shadow: none !important; line-height: 1 !important;
        }
        div[data-nb-buttons="true"] .stButton > button:hover {
          background: rgba(59,130,246,0.18) !important;
          border-color: rgba(59,130,246,0.42) !important;
          color: #BAE6FD !important; transform: none !important;
        }
        div[data-nb-buttons="true"] .nb-new .stButton > button {
          background: rgba(59,130,246,0.13) !important;
          border-color: rgba(59,130,246,0.32) !important;
          color: #93C5FD !important;
        }
        div[data-nb-buttons="true"] .nb-active .stButton > button {
          background: rgba(59,130,246,0.22) !important;
          border-color: rgba(59,130,246,0.50) !important;
          color: #BAE6FD !important;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<div data-nb-buttons="true">', unsafe_allow_html=True)
        _c1, _c2, _c3, _c4 = st.columns([1,1,1,1])
        with _c1:
            _hcls = "nb-active" if st.session_state.get("show_history_panel") else ""
            st.markdown(f'<div class="{_hcls}" id="nb-history-wrap">', unsafe_allow_html=True)
            if st.button("🕐 History", key="_btn_history"):
                st.session_state.show_history_panel = not st.session_state.get("show_history_panel", False)
                st.session_state.show_settings_panel = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with _c2:
            st.markdown('<div class="nb-new" id="nb-newchat-wrap">', unsafe_allow_html=True)
            if st.button("+ New Chat", key="_btn_new_chat"):
                if st.session_state.chat_messages:
                    fu = next((m["content"][:38] for m in st.session_state.chat_messages if m["role"]=="user"), "Session")
                    st.session_state.chat_sessions.append({"label": fu+"...", "messages": list(st.session_state.chat_messages)})
                st.session_state.chat_messages = []
                st.session_state.show_uploader = False
                st.session_state.attached_file_name = ""
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with _c3:
            _scls = "nb-active" if st.session_state.get("show_settings_panel") else ""
            st.markdown(f'<div class="{_scls}" id="nb-settings-wrap">', unsafe_allow_html=True)
            if st.button("⚙ Settings", key="_btn_settings"):
                st.session_state.show_settings_panel = not st.session_state.get("show_settings_panel", False)
                st.session_state.show_history_panel = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with _c4:
            st.markdown('<div id="nb-dashboard-wrap">', unsafe_allow_html=True)
            if st.button("Dashboard", key="_btn_dashboard"):
                st.session_state.view = "dashboard"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)  # close data-nb-buttons


    # ── CHAT HISTORY PANEL ────────────────────────────────────────────────
    if st.session_state.get("show_history_panel", False):
        all_sessions = st.session_state.chat_sessions
        st.markdown('<div style="max-width:560px;margin:0 auto 14px;">', unsafe_allow_html=True)
        with st.expander("🕐 Chat History", expanded=True):
            if not all_sessions:
                st.markdown('<div style="text-align:center;padding:28px 0;font-size:0.82rem;color:rgba(148,163,184,0.40);">No saved chats yet. Start a conversation!</div>', unsafe_allow_html=True)
            else:
                # Pinned first
                _pinned   = [(i,s) for i,s in enumerate(all_sessions) if s.get("pinned")]
                _unpinned = [(i,s) for i,s in enumerate(all_sessions) if not s.get("pinned")]
                for _grp_label, _grp in [("📌 Pinned", _pinned), ("Recent", _unpinned)]:
                    if not _grp: continue
                    st.markdown(f'<div style="font-size:0.60rem;color:rgba(148,163,184,0.40);text-transform:uppercase;letter-spacing:1px;padding:4px 0 6px;">{_grp_label}</div>', unsafe_allow_html=True)
                    for _i, _sess in reversed(_grp):
                        _label = _sess.get("label","Chat")[:48]
                        _is_pinned = _sess.get("pinned", False)
                        _c1, _c2, _c3, _c4 = st.columns([5, 0.9, 0.9, 0.9])
                        with _c1:
                            st.markdown(
                                f'<div style="background:rgba(255,255,255,0.03);border:1px solid {"rgba(245,158,11,0.25)" if _is_pinned else "rgba(255,255,255,0.07)"};'
                                f'border-radius:10px;padding:10px 14px;font-size:0.82rem;color:rgba(226,232,240,0.80);'
                                f'font-family:\'Outfit\',sans-serif;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'
                                f'{"📌 " if _is_pinned else ""}{_label}</div>',
                                unsafe_allow_html=True
                            )
                        with _c2:
                            if st.button("↩", key=f"_load_sess_{_i}", help="Load chat"):
                                st.session_state.chat_messages = list(_sess["messages"])
                                st.session_state.show_history_panel = False
                                st.rerun()
                        with _c3:
                            _pin_lbl = "📌" if not _is_pinned else "📍"
                            if st.button(_pin_lbl, key=f"_pin_sess_{_i}", help="Pin/Unpin"):
                                st.session_state.chat_sessions[_i]["pinned"] = not _is_pinned
                                st.rerun()
                        with _c4:
                            if st.button("🗑", key=f"_del_sess_{_i}", help="Delete"):
                                st.session_state.chat_sessions.pop(_i)
                                st.rerun()
            # Clear all button
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            if all_sessions:
                if st.button("🗑 Clear All History", key="_clear_all_hist"):
                    st.session_state.chat_sessions = []
                    st.toast("History cleared!", icon="🗑")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── SETTINGS PANEL ────────────────────────────────────────────────────
    if st.session_state.get("show_settings_panel", False):
        st.markdown('<div style="max-width:520px;margin:0 auto 14px;">', unsafe_allow_html=True)
        with st.expander("⚙ Chatbot Settings", expanded=True):
            st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:0.58rem;color:rgba(148,163,184,0.40);text-transform:uppercase;letter-spacing:1.2px;margin-bottom:14px;">Customize AskMNIT</div>', unsafe_allow_html=True)

            # Theme
            _ts1, _ts2 = st.columns([2, 3])
            with _ts1:
                st.markdown('<div style="font-size:0.84rem;color:rgba(226,232,240,0.80);font-weight:500;padding-top:6px;">🎨 Interface Theme</div><div style="font-size:0.68rem;color:rgba(148,163,184,0.42);margin-top:2px;">Dark or light mode</div>', unsafe_allow_html=True)
            with _ts2:
                _t1, _t2 = st.columns(2)
                with _t1:
                    _d_active = st.session_state.get("chat_theme","dark") == "dark"
                    st.markdown(f'<div class="{"nb-btn-active" if _d_active else ""}">', unsafe_allow_html=True)
                    if st.button("🌙 Dark", key="_theme_dark", use_container_width=True):
                        st.session_state.chat_theme = "dark"; st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with _t2:
                    _l_active = st.session_state.get("chat_theme","dark") == "light"
                    st.markdown(f'<div class="{"nb-btn-active" if _l_active else ""}">', unsafe_allow_html=True)
                    if st.button("☀️ Light", key="_theme_light", use_container_width=True):
                        st.session_state.chat_theme = "light"; st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:10px 0;'>", unsafe_allow_html=True)

            # Response style
            _rs1, _rs2 = st.columns([2, 3])
            with _rs1:
                st.markdown('<div style="font-size:0.84rem;color:rgba(226,232,240,0.80);font-weight:500;padding-top:6px;">💬 Response Style</div><div style="font-size:0.68rem;color:rgba(148,163,184,0.42);margin-top:2px;">How AI replies</div>', unsafe_allow_html=True)
            with _rs2:
                _new_style = st.selectbox("", ["Concise","Detailed","Bullet Points"],
                    index=["Concise","Detailed","Bullet Points"].index(st.session_state.get("response_style","Concise")),
                    key="_sets_response_style", label_visibility="collapsed")
                if _new_style != st.session_state.response_style:
                    st.session_state.response_style = _new_style; st.rerun()

            st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:10px 0;'>", unsafe_allow_html=True)

            # Toggles
            _tog1, _tog2 = st.columns(2)
            with _tog1:
                st.session_state.voice_output = st.toggle("🔊 Voice Output", value=st.session_state.voice_output, key="_sets_voice")
            with _tog2:
                st.session_state.strict_mode = st.toggle("🎓 Strict Academic Mode", value=st.session_state.strict_mode, key="_sets_strict")

            st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:10px 0;'>", unsafe_allow_html=True)

            # Clear chats
            _cl1, _cl2 = st.columns([3, 1])
            with _cl1:
                st.markdown('<div style="font-size:0.84rem;color:rgba(226,232,240,0.80);font-weight:500;padding-top:6px;">🗑 Clear All Chats</div><div style="font-size:0.68rem;color:rgba(148,163,184,0.42);margin-top:2px;">Remove current session messages</div>', unsafe_allow_html=True)
            with _cl2:
                if st.button("Clear", key="_sets_clear_chats"):
                    st.session_state.chat_messages = []
                    st.session_state.chat_sessions = []
                    st.session_state.attached_file_name = ""
                    st.toast("Chats cleared!", icon="🗑"); st.rerun()

            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            if st.button("✕ Close Settings", key="_sets_close", use_container_width=True):
                st.session_state.show_settings_panel = False; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── FILE UPLOADER PANEL ───────────────────────────────────────────────
    if st.session_state.show_uploader:
        st.markdown('<div class="attach-panel">', unsafe_allow_html=True)
        up_c1, up_c2 = st.columns([6, 1])
        with up_c1:
            attached_file = st.file_uploader(
                "Attach a file",
                type=["pdf","txt","png","jpg","jpeg","docx","csv"],
                key="file_uploader_chat",
            )
        with up_c2:
            st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("Close", key="close_uploader"):
                st.session_state.show_uploader = False; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        if attached_file is not None:
            st.session_state.attached_file_name = attached_file.name
            st.session_state.show_uploader = False
            st.toast(f"📎 {attached_file.name} selected!", icon="✅")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── HERO STATE ────────────────────────────────────────────────────────
    if not has_messages:
        st.markdown("<div style='height:5vh'></div>", unsafe_allow_html=True)

        _, hero_col, _ = st.columns([1, 3, 1])
        with hero_col:
            st.markdown(
                '<div style="text-align:center;animation:fadeUp 0.45s ease both;">'
                '<div style="width:80px;height:80px;margin:0 auto 22px;border-radius:22px;'
                'background:linear-gradient(135deg,#1E3A8A,#4338CA 50%,#059669);'
                'display:flex;align-items:center;justify-content:center;font-size:2.3rem;'
                'box-shadow:0 0 0 1px rgba(59,130,246,0.22),0 16px 52px rgba(37,99,235,0.30);">&#129302;</div>'
                '<div style="font-family:\'Fraunces\',serif;font-size:3rem;font-weight:900;'
                'color:#E2E8F0;letter-spacing:-2px;line-height:1.05;margin-bottom:10px;">'
                'AskMNIT <span style="font-weight:300;color:#60A5FA;">AI</span></div>'
                '<div style="font-size:0.86rem;color:rgba(148,163,184,0.50);line-height:1.70;margin-bottom:32px;">'
                'Attendance analysis &nbsp;&#183;&nbsp; PYQ search &nbsp;&#183;&nbsp; Schedule queries &nbsp;&#183;&nbsp; Exam prep'
                '</div></div>',
                unsafe_allow_html=True,
            )

        br = st.session_state.branch
        PILLS_ROW1 = ["Analyse my attendance", "What's next on my schedule?", f"PYQs for {br}", "Check my fee status"]
        PILLS_ROW2 = [f"Subjects for {br}", "Exam schedule tips"]

        # PATCH 3: pills centered via padding
        st.markdown('<div style="padding:0 6vw;">', unsafe_allow_html=True)
        pills_col = st.container()
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

        st.markdown('</div>', unsafe_allow_html=True)  # close pills padding div

        st.markdown("<div style='height:3vh'></div>", unsafe_allow_html=True)

        # Input bar — CSS centered, no columns needed
        st.markdown('<div style="padding:0 6vw;">', unsafe_allow_html=True)
        hero_action = render_gemini_bar(bar_key="hero", hero_mode=True)
        st.markdown('</div>', unsafe_allow_html=True)

        render_voice_recorder("hero")
        render_native_file_picker("hero")

        if st.session_state.is_recording:
            st.markdown('<div class="listening-banner"><div class="listening-dot"></div><span>Listening... speak now, then press ⏹ to stop</span></div>', unsafe_allow_html=True)

        st.markdown('<p style="text-align:center;font-size:0.59rem;color:rgba(100,116,139,0.38);margin-top:10px;font-family:\'DM Mono\',monospace;">AskMNIT AI can make mistakes &nbsp;·&nbsp; Verify with official ERP or faculty</p>', unsafe_allow_html=True)

        if hero_action is not None:
            act = hero_action[0]
            if act == "send":
                dispatch_message(hero_action[1])
                st.session_state.attached_file_name = ""
                st.rerun()
            elif act == "mic":
                direction = hero_action[1]
                if direction == "start":
                    st.session_state.is_recording = True
                    st.markdown("""<script>
                    (function poll(){ var f = document.querySelector('iframe');
                    if(f && f.contentWindow){ f.contentWindow.postMessage({type:'startRecording_hero'},'*'); }
                    else { setTimeout(poll,200); }
                    })(); </script>""", unsafe_allow_html=True)
                    st.toast("🎤 Recording started — speak now!", icon="🎤")
                else:
                    st.session_state.is_recording = False
                    st.markdown("""<script>
                    (function poll(){ var frames = document.querySelectorAll('iframe');
                    frames.forEach(function(f){ if(f.contentWindow) f.contentWindow.postMessage({type:'stopRecording_hero'},'*'); });
                    })(); </script>""", unsafe_allow_html=True)
                    st.toast("⏹ Processing voice...", icon="⏳")
                st.rerun()
            elif act == "attach":
                st.markdown("""<script>
                setTimeout(function(){
                  var frames = document.querySelectorAll('iframe');
                  frames.forEach(function(f){ if(f.contentWindow) f.contentWindow.postMessage({type:'triggerPicker_hero'},'*'); });
                }, 100);
                </script>""", unsafe_allow_html=True)
                st.session_state.show_uploader = True
                st.rerun()

    # ── ACTIVE STATE ──────────────────────────────────────────────────────
    else:
        st.markdown("<div class='chat-scroll-area'>", unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        _, msg_col, _ = st.columns([0.5, 5, 0.5])
        with msg_col:
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="gemini-bar-anchored">', unsafe_allow_html=True)
        anchored_action = render_gemini_bar(bar_key="anchored", hero_mode=False)

        render_voice_recorder("anchored")
        render_native_file_picker("anchored")

        if st.session_state.is_recording:
            st.markdown('<div class="listening-banner" style="margin-top:8px;"><div class="listening-dot"></div><span>Listening... press ⏹ to stop and send</span></div>', unsafe_allow_html=True)

        st.markdown('<p style="text-align:center;font-size:0.59rem;color:rgba(100,116,139,0.38);margin-top:4px;font-family:\'DM Mono\',monospace;">AskMNIT AI can make mistakes &nbsp;·&nbsp; Verify with official ERP or faculty</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if anchored_action is not None:
            act = anchored_action[0]
            if act == "send":
                dispatch_message(anchored_action[1])
                st.session_state.attached_file_name = ""
                st.rerun()
            elif act == "mic":
                direction = anchored_action[1]
                if direction == "start":
                    st.session_state.is_recording = True
                    st.markdown("""<script>
                    setTimeout(function(){
                      var frames = document.querySelectorAll('iframe');
                      frames.forEach(function(f){ if(f.contentWindow) f.contentWindow.postMessage({type:'startRecording_anchored'},'*'); });
                    }, 150);
                    </script>""", unsafe_allow_html=True)
                    st.toast("🎤 Recording started — speak now!", icon="🎤")
                else:
                    st.session_state.is_recording = False
                    st.markdown("""<script>
                    setTimeout(function(){
                      var frames = document.querySelectorAll('iframe');
                      frames.forEach(function(f){ if(f.contentWindow) f.contentWindow.postMessage({type:'stopRecording_anchored'},'*'); });
                    }, 50);
                    </script>""", unsafe_allow_html=True)
                    st.toast("⏹ Processing voice...", icon="⏳")
                st.rerun()
            elif act == "attach":
                st.markdown("""<script>
                setTimeout(function(){
                  var frames = document.querySelectorAll('iframe');
                  frames.forEach(function(f){ if(f.contentWindow) f.contentWindow.postMessage({type:'triggerPicker_anchored'},'*'); });
                }, 100);
                </script>""", unsafe_allow_html=True)
                st.session_state.show_uploader = True
                st.rerun()

    st.stop()


###############################################################################
# ████████████████████  DASHBOARD VIEW  ██████████████████████████████████████
###############################################################################

NAV_LABELS = ["My Dashboard","My Schedule","Academics","Study Material","PYQs","Fee Portal","Mess Menu"]
with st.sidebar:
    st.markdown(
        '<div style="padding:18px 14px 14px;border-bottom:1px solid rgba(59,130,246,0.14);">'
        '<div style="display:flex;align-items:center;gap:9px;">'
        '<div style="width:30px;height:30px;border-radius:7px;background:linear-gradient(135deg,#2563EB,#4F46E5);'
        'display:flex;align-items:center;justify-content:center;font-size:0.9rem;font-weight:700;color:white;'
        'box-shadow:0 3px 12px rgba(37,99,235,0.28);">A</div>'
        '<div><div style="font-family:\'DM Mono\',monospace;font-size:0.85rem;color:#E2E8F0;">AskMNIT</div>'
        '<div style="font-size:0.56rem;color:rgba(148,163,184,.40);margin-top:1px;">Student Portal</div>'
        '</div></div></div>',
        unsafe_allow_html=True,
    )
    bh = branch_hex(st.session_state.branch)
    st.markdown(
        f'<div style="padding:8px 12px 4px;">'
        f'<span style="font-size:0.60rem;font-weight:700;padding:2px 9px;background:rgba(255,255,255,0.05);'
        f'border:1px solid {bh}44;border-radius:5px;color:{bh};letter-spacing:0.4px;">'
        f'{st.session_state.branch}</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    for label in NAV_LABELS:
        is_active = st.session_state.nav_page == label
        css = "nav-btn-active" if is_active else "nav-btn"
        st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
        if st.button(label, key="nav_"+label, use_container_width=True):
            st.session_state.nav_page = label; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div style="position:fixed;bottom:18px;width:182px;padding-top:10px;border-top:1px solid rgba(255,255,255,0.06);">', unsafe_allow_html=True)
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("Logout", key="sidebar_logout", use_container_width=True):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

dash_page = st.session_state.nav_page
if dash_page != "My Dashboard":
    PMETA = {
        "My Schedule":    ("My Schedule",   "Weekly timetable renders here."),
        "Academics":      ("Academics",      "Grades and CGPA records render here."),
        "Study Material": ("Study Material", "Uploaded notes render here."),
        "PYQs":           ("PYQs",           "Previous year papers render here."),
        "Fee Portal":     ("Fee Portal",     "Fee dues and receipts render here."),
        "Mess Menu":      ("Mess Menu",      "Weekly hostel menu renders here."),
    }
    title, desc = PMETA.get(dash_page, (dash_page, "Coming soon."))
    st.markdown(
        f'<div style="padding:24px;">'
        f'<div style="font-family:\'DM Mono\',monospace;font-size:0.95rem;color:#E2E8F0;'
        f'border-bottom:1px solid rgba(255,255,255,0.06);padding-bottom:14px;margin-bottom:24px;">{title.upper()}</div>'
        f'<div style="background:linear-gradient(160deg,#0B1120,#060A12);border:1px dashed rgba(59,130,246,0.18);'
        f'border-radius:16px;padding:60px 40px;text-align:center;">'
        f'<div style="font-family:\'DM Mono\',monospace;font-size:0.88rem;color:#E2E8F0;margin-bottom:8px;">{title.upper()}</div>'
        f'<div style="font-size:0.76rem;color:rgba(148,163,184,.44);max-width:280px;margin:0 auto;line-height:1.65;">{desc}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# MY DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div style='padding:0 22px 80px;'>", unsafe_allow_html=True)

h_logo, h_mid, h_right = st.columns([2,4,3])
with h_logo:
    st.markdown(
        '<div style="display:flex;align-items:center;gap:8px;padding:13px 0 9px;">'
        '<div style="width:30px;height:30px;border-radius:7px;background:linear-gradient(135deg,#2563EB,#4F46E5);'
        'display:flex;align-items:center;justify-content:center;font-size:0.85rem;font-weight:700;color:white;">M</div>'
        '<div><div style="font-family:\'DM Mono\',monospace;font-size:0.76rem;color:#E2E8F0;">MNIT Jaipur</div>'
        '<div style="font-size:0.52rem;color:rgba(148,163,184,.36);">[ MNIT LOGO ]</div></div></div>',
        unsafe_allow_html=True,
    )
with h_mid:
    now_str = datetime.datetime.now().strftime("%a, %d %b %Y  ·  %H:%M")
    st.markdown(
        '<div style="padding:13px 0 9px;text-align:center;">'
        '<span style="font-family:\'DM Mono\',monospace;font-size:0.76rem;color:#60A5FA;letter-spacing:0.8px;">MY DASHBOARD</span>'
        f'<br><span style="font-size:0.57rem;color:rgba(148,163,184,.38);">{now_str}</span></div>',
        unsafe_allow_html=True,
    )
with h_right:
    nm, br, sem = st.session_state.student_name, st.session_state.branch, st.session_state.semester
    bh = branch_hex(br); pp = st.session_state.profile_pic_b64
    av_html = (f'<img src="{pp}" style="width:36px;height:36px;border-radius:50%;object-fit:cover;border:2px solid {bh}55;">' if pp
               else f'<div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,{bh},{bh}88);display:flex;align-items:center;justify-content:center;font-size:0.85rem;font-weight:700;color:#fff;border:2px solid {bh}55;">{initials(nm)}</div>')
    st.markdown(f'<div style="display:flex;align-items:center;justify-content:flex-end;gap:9px;padding:10px 0 6px;">{av_html}<div><div style="font-weight:700;font-size:0.83rem;color:#E2E8F0;line-height:1.2;">{nm}</div><div style="font-size:0.58rem;color:{bh};font-weight:600;">{br} · {sem}</div></div></div>', unsafe_allow_html=True)

st.markdown('<div style="height:1px;background:linear-gradient(90deg,transparent,rgba(59,130,246,0.22),rgba(34,211,238,0.10),transparent);margin-bottom:20px;"></div>', unsafe_allow_html=True)

srow1,srow2,srow3,_,srow5 = st.columns([1,1,1,1,1])
with srow1:
    st.markdown('<div class="settings-menu-btn">', unsafe_allow_html=True)
    if st.button("Settings & Profile", key="open_settings"):
        st.session_state.settings_mode = None if st.session_state.settings_mode=="profile" else "profile"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with srow2:
    st.markdown('<div class="settings-menu-btn">', unsafe_allow_html=True)
    if st.button("Upload Schedule", key="open_schedule"):
        st.session_state.settings_mode = None if st.session_state.settings_mode=="schedule" else "schedule"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with srow3:
    st.markdown('<div class="settings-menu-btn">', unsafe_allow_html=True)
    if st.button("Notifications", key="open_notif"):
        st.toast("No new notifications.", icon="🔔")
    st.markdown('</div>', unsafe_allow_html=True)
with srow5:
    st.markdown('<div class="open-chat-btn">', unsafe_allow_html=True)
    if st.button("Open AskMNIT AI", key="btn_open_chat_dash"):
        st.session_state.view = "chat"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

mode = st.session_state.settings_mode
if mode == "profile":
    with st.expander("Settings & Profile", expanded=True):
        pc1,pc2 = st.columns([1,2])
        with pc1:
            pp = st.session_state.profile_pic_b64; bh = branch_hex(st.session_state.branch)
            if pp:
                st.markdown(f'<img src="{pp}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;border:3px solid {bh}66;display:block;margin:0 auto 8px;">', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,{bh},{bh}88);display:flex;align-items:center;justify-content:center;font-size:1.8rem;font-weight:700;color:#fff;margin:0 auto 8px;">{initials(st.session_state.student_name)}</div>', unsafe_allow_html=True)
            pic_file = st.file_uploader("Upload photo", type=["png","jpg","jpeg"], key="profile_pic_up", label_visibility="collapsed")
            if pic_file: st.session_state.profile_pic_b64 = img_to_b64(pic_file); st.rerun()
        with pc2:
            new_name = st.text_input("Full Name",  value=st.session_state.student_name, key="inp_name")
            new_id   = st.text_input("College ID", value=st.session_state.college_id,   key="inp_id")
            new_sem  = st.selectbox("Semester", SEMESTERS, index=SEMESTERS.index(st.session_state.semester), key="sel_sem")
            new_br   = st.selectbox("Branch",   BRANCHES,  index=BRANCHES.index(st.session_state.branch),   key="sel_br")
            if st.button("Save Profile", key="save_profile"):
                old_br = st.session_state.branch
                st.session_state.student_name=new_name; st.session_state.college_id=new_id
                st.session_state.semester=new_sem; st.session_state.branch=new_br
                if old_br!=new_br: st.session_state.attendance=blank_att(subjects_for_branch(new_br))
                st.toast("Profile saved!", icon="✅"); st.session_state.settings_mode=None; st.rerun()

elif mode == "schedule":
    with st.expander("Upload Weekly Schedule PDF", expanded=True):
        pdf_file = st.file_uploader("Drop schedule PDF here", type=["pdf"], key="sched_upload")
        if pdf_file:
            st.session_state.full_schedule=process_schedule_pdf(pdf_file,st.session_state.branch)
            st.session_state.schedule_loaded=True; st.session_state.pdf_filename=pdf_file.name
            st.toast(f"Schedule loaded: {pdf_file.name}", icon="✅"); st.session_state.settings_mode=None; st.rerun()
        if st.session_state.schedule_loaded:
            st.markdown(f'<div style="font-size:0.75rem;color:#10B981;margin-top:6px;">Active: {st.session_state.pdf_filename}</div>', unsafe_allow_html=True)

# KPI Row
ov = overall_pct(st.session_state.attendance)
stat_badge_txt,stat_col,_ = status_badge(ov)
kpi1,kpi2,kpi3,kpi4 = st.columns(4)
for col,ico,val,lbl,c in [
    (kpi1,"📊",f"{ov}%","Overall Attendance",stat_col),
    (kpi2,"📚",str(len(subjects_for_branch(st.session_state.branch))),"Enrolled Subjects","#60A5FA"),
    (kpi3,"📅",str(len(get_today_slots(st.session_state.full_schedule)) if st.session_state.schedule_loaded else 0),"Classes Today","#22D3EE"),
    (kpi4,"📝",str(len(st.session_state.notes_list)),"Active Notes","#A78BFA"),
]:
    with col:
        st.markdown(f'<div style="background:linear-gradient(160deg,#0B1120,#070D1C);border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:16px 18px 14px;margin-bottom:14px;"><div style="font-size:1.4rem;margin-bottom:6px;">{ico}</div><div style="font-size:1.7rem;font-weight:800;color:{c};font-family:\'DM Mono\',monospace;line-height:1.1;">{val}</div><div style="font-size:0.68rem;color:rgba(148,163,184,.46);margin-top:4px;">{lbl}</div></div>', unsafe_allow_html=True)

# Attendance Tracker
st.markdown('<div style="background:linear-gradient(160deg,#0B1120,#070D1C);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:18px 18px 14px;margin-bottom:14px;"><div style="font-family:\'DM Mono\',monospace;font-size:0.56rem;color:rgba(148,163,184,.40);text-transform:uppercase;letter-spacing:1.4px;margin-bottom:14px;">// ATTENDANCE TRACKER</div>', unsafe_allow_html=True)

def render_subj_rows(subj_list: list, section: str):
    att = st.session_state.attendance
    for idx, subj in enumerate(subj_list):
        if subj not in att: att[subj]={"present":0,"total":0}
        r=att[subj]; pct=att_pct(r); c=att_color(pct)
        kb = f"{section}_{idx}_{_safe_key(subj)}"
        sc1,sc2,sc3,sc4,sc5,sc6 = st.columns([3.5,1.2,0.9,0.9,0.9,0.9])
        with sc1:
            st.markdown(f'<div style="font-size:0.80rem;color:#E2E8F0;font-weight:600;padding:8px 0 4px;">{subj}</div><div style="background:rgba(255,255,255,.06);border-radius:99px;height:4px;overflow:hidden;width:90%;"><div style="width:{pct}%;height:100%;background:linear-gradient(90deg,{c},{c}88);border-radius:99px;"></div></div>', unsafe_allow_html=True)
        with sc2:
            st.markdown(f'<div style="font-family:\'DM Mono\',monospace;font-size:0.85rem;font-weight:700;color:{c};padding-top:8px;">{pct}%</div><div style="font-size:0.60rem;color:rgba(148,163,184,.40);">{r["present"]}/{r["total"]}</div>', unsafe_allow_html=True)
        with sc3:
            st.markdown('<div class="present-btn">', unsafe_allow_html=True)
            if st.button("P", key=f"pp_{kb}", use_container_width=True):
                att[subj]["present"]+=1; att[subj]["total"]+=1; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with sc4:
            st.markdown('<div class="absent-btn">', unsafe_allow_html=True)
            if st.button("A", key=f"pa_{kb}", use_container_width=True):
                att[subj]["total"]+=1; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with sc5:
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("-P", key=f"rp_{kb}", use_container_width=True):
                if r["present"]>0 and r["total"]>0: att[subj]["present"]-=1; att[subj]["total"]-=1; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with sc6:
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("-A", key=f"ra_{kb}", use_container_width=True):
                if r["total"]>0: att[subj]["total"]-=1; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

branch_only = BRANCH_SUBJECTS.get(st.session_state.branch,[])
with st.expander("Common Subjects ("+str(len(COMMON_SUBJECTS))+")", expanded=True):
    render_subj_rows(COMMON_SUBJECTS,"cmn")
if branch_only:
    with st.expander(st.session_state.branch+" Subjects ("+str(len(branch_only))+")", expanded=True):
        render_subj_rows(branch_only,"brnch")
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

# Schedule Section
today_name = datetime.datetime.now().strftime("%A")
now_hm = datetime.datetime.now().hour*60+datetime.datetime.now().minute
st.markdown(
    '<div style="background:linear-gradient(160deg,#0B1120,#070D1C);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:18px 18px 14px;margin-bottom:14px;">'
    '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">'
    '<span style="font-family:\'DM Mono\',monospace;font-size:0.56rem;color:rgba(148,163,184,.40);text-transform:uppercase;letter-spacing:1.4px;">// TODAY\'S CLASS SCHEDULE</span>'
    f'<span style="font-family:\'DM Mono\',monospace;font-size:0.62rem;color:rgba(96,165,250,.65);">{today_name.upper()}</span></div>',
    unsafe_allow_html=True,
)
if st.session_state.schedule_loaded:
    today_slots=get_today_slots(st.session_state.full_schedule); nxt=get_next_class(today_slots)
    if nxt:
        mins=nxt["minutes_away"]; hrs=mins//60; rem=mins%60
        cd_str=(f"{hrs}h {rem}m" if hrs else f"{rem} min")+" away"
        urg_c="#EF4444" if mins<15 else "#F59E0B" if mins<45 else "#22D3EE"
        st.markdown(f'<div style="background:linear-gradient(90deg,rgba(34,211,238,.06),rgba(37,99,235,.04));border:1px solid rgba(34,211,238,.18);border-radius:10px;padding:10px 16px;margin-bottom:14px;display:flex;align-items:center;justify-content:space-between;"><div><div style="font-size:0.57rem;color:rgba(148,163,184,.46);text-transform:uppercase;letter-spacing:0.8px;margin-bottom:2px;">Next Class</div><div style="font-weight:700;font-size:0.86rem;color:#E2E8F0;">{nxt["subject"]}  <span style="font-size:0.67rem;color:rgba(148,163,184,.46);">{nxt["room"]}</span></div></div><div style="font-family:\'DM Mono\',monospace;font-size:0.96rem;font-weight:600;color:{urg_c};text-align:right;">{cd_str}<div style="font-size:0.57rem;color:rgba(148,163,184,.42);font-weight:400;margin-top:1px;">{fmt_time(nxt["time_start"])} – {fmt_time(nxt["time_end"])}</div></div></div>', unsafe_allow_html=True)
    if today_slots:
        rows=[today_slots[i:i+3] for i in range(0,len(today_slots),3)]
        for row in rows:
            cols=st.columns(len(row))
            for ci,(col,slot) in enumerate(zip(cols,row)):
                sh,sm=map(int,slot["time_start"].split(":")); is_past=(sh*60+sm)<now_hm
                tc=TYPE_COLORS.get(slot["type"],"#60A5FA")
                is_next=(nxt is not None and slot["time_start"]==nxt["time_start"] and slot["subject"]==nxt["subject"])
                bc=tc if not is_past else "rgba(255,255,255,0.06)"
                cbg="linear-gradient(160deg,rgba(34,211,238,0.06),rgba(37,99,235,0.03))" if is_next else "rgba(255,255,255,0.02)" if not is_past else "rgba(255,255,255,0.01)"
                with col:
                    st.markdown(f'<div style="background:{cbg};border:1px solid {bc};border-left:3px solid {bc};border-radius:12px;padding:13px 14px;margin-bottom:8px;"><div style="font-family:\'DM Mono\',monospace;font-size:0.78rem;font-weight:700;color:{"#E2E8F0" if not is_past else "rgba(148,163,184,0.32)"};margin-bottom:6px;">{fmt_time(slot["time_start"])}<br><span style="font-size:0.62rem;font-weight:400;color:rgba(148,163,184,0.45);">– {fmt_time(slot["time_end"])}</span></div><div style="font-size:0.82rem;font-weight:700;color:{"#F1F5F9" if not is_past else "rgba(148,163,184,0.28)"};margin-bottom:5px;">{slot["subject"]}</div><div style="display:flex;align-items:center;gap:6px;"><span style="font-size:0.62rem;color:rgba(148,163,184,.48);">{slot["room"]}</span><span style="font-size:0.58rem;padding:1px 7px;border-radius:4px;background:{tc}1A;color:{tc};font-weight:600;">{slot["type"]}</span>{"  <span style=\"font-size:0.58rem;color:#22D3EE;font-weight:700;\">NEXT</span>" if is_next else ""}</div>{"<div style=\"font-size:0.58rem;color:rgba(148,163,184,.28);margin-top:4px;text-decoration:line-through;\">Done</div>" if is_past else ""}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="text-align:center;padding:24px;color:rgba(148,163,184,.40);font-size:0.80rem;">No classes for {today_name}.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div style="background:rgba(59,130,246,.04);border:1px dashed rgba(59,130,246,.20);border-radius:9px;padding:9px 13px;margin-bottom:12px;font-size:0.73rem;color:rgba(148,163,184,.48);">Use <b>Upload Schedule</b> to activate the planner.</div>', unsafe_allow_html=True)
    if "planner_overrides" not in st.session_state: st.session_state.planner_overrides={}
    for st_start,st_end in [("08:00","09:00"),("09:30","10:30"),("11:00","12:00"),("12:00","13:00"),("14:00","15:00"),("15:30","16:30")]:
        override=st.session_state.planner_overrides.get(st_start,"")
        mp1,mp2,mp3,mp4=st.columns([1.6,4,0.8,2.2])
        with mp1: st.markdown(f'<div style="font-family:\'DM Mono\',monospace;font-size:0.68rem;color:#60A5FA;padding-top:10px;white-space:nowrap;font-weight:700;">{fmt_time(st_start)}<br><span style="font-size:0.56rem;font-weight:400;color:rgba(148,163,184,.38);">– {fmt_time(st_end)}</span></div>', unsafe_allow_html=True)
        with mp2: note_v=st.text_input("",value=override,placeholder="Task...",key="mp_"+st_start,label_visibility="collapsed")
        with mp3:
            st.markdown('<div class="save-btn">', unsafe_allow_html=True)
            if st.button("Save",key="sv_mp_"+st_start,use_container_width=True): st.session_state.planner_overrides[st_start]=note_v; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with mp4:
            saved=st.session_state.planner_overrides.get(st_start,"")
            if saved: st.markdown(f'<div style="font-size:0.67rem;color:#34D399;background:rgba(16,185,129,.07);border:1px solid rgba(16,185,129,.14);border-radius:7px;padding:4px 9px;margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{saved}</div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# Notes & Quick Links
ql_col,notes_col=st.columns([1,1.5],gap="large")
with ql_col:
    st.markdown('<div style="background:linear-gradient(160deg,#0B1120,#070D1C);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:18px 18px 14px;height:100%;"><div style="font-family:\'DM Mono\',monospace;font-size:0.56rem;color:rgba(148,163,184,.40);text-transform:uppercase;letter-spacing:1.4px;margin-bottom:12px;">// QUICK LINKS</div>', unsafe_allow_html=True)
    QL=[("Upload Syllabus","Syllabus uploader will be enabled here."),("Add PYQ Link","PYQ link manager will open here."),("Library Search","Library search will open here.")]
    st.markdown('<div class="ql-btn">', unsafe_allow_html=True)
    for lbl,fb in QL:
        if st.button(lbl,key="ql_"+lbl,use_container_width=True): st.session_state.ql_feedback=fb; st.rerun()
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if st.session_state.ql_feedback: st.markdown(f'<div style="background:rgba(59,130,246,.06);border:1px solid rgba(59,130,246,.18);border-radius:8px;padding:7px 11px;margin-top:7px;font-size:0.70rem;color:rgba(186,230,253,.58);line-height:1.5;">{st.session_state.ql_feedback}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with notes_col:
    st.markdown('<div style="background:linear-gradient(160deg,#0B1120,#070D1C);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:18px 18px 14px;"><div style="font-family:\'DM Mono\',monospace;font-size:0.56rem;color:rgba(148,163,184,.40);text-transform:uppercase;letter-spacing:1.4px;margin-bottom:12px;">// PERSONAL NOTES</div>', unsafe_allow_html=True)
    new_note_input=st.text_input("",placeholder="Type a new note...",key="new_note_input_field",label_visibility="collapsed")
    ac,_=st.columns([1,3])
    with ac:
        if st.button("Add Note",key="add_note_btn",use_container_width=True):
            txt=new_note_input.strip()
            if txt: st.session_state.notes_list.append({"text":txt,"pinned":False}); st.rerun()
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    unpinned=[(i,n) for i,n in enumerate(st.session_state.notes_list) if not n["pinned"]]
    if not unpinned:
        st.markdown('<div style="font-size:0.76rem;color:rgba(148,163,184,.38);text-align:center;padding:16px;font-style:italic;">No notes yet.</div>', unsafe_allow_html=True)
    else:
        for list_idx,(i,note) in enumerate(unpinned):
            nr1,nr2,nr3=st.columns([5,1.2,1])
            with nr1: st.markdown(f'<div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.07);border-radius:9px;padding:9px 12px;margin-bottom:4px;font-size:0.80rem;color:rgba(226,232,240,0.75);line-height:1.5;">{note["text"]}</div>', unsafe_allow_html=True)
            with nr2:
                st.markdown('<div class="pin-btn">', unsafe_allow_html=True)
                if st.button("Pin",key=f"pin_{list_idx}_{i}_{_safe_key(note['text'][:10])}",use_container_width=True):
                    st.session_state.notes_list[i]["pinned"]=True; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with nr3:
                st.markdown('<div class="del-btn">', unsafe_allow_html=True)
                if st.button("Del",key=f"del_{list_idx}_{i}_{_safe_key(note['text'][:10])}",use_container_width=True):
                    st.session_state.notes_list.pop(i); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div style="text-align:center;margin-top:28px;padding:10px 0;border-top:1px solid rgba(255,255,255,0.05);"><span style="font-family:\'DM Mono\',monospace;font-size:0.52rem;color:rgba(148,163,184,0.24);letter-spacing:1.2px;">ASKMNT &nbsp;·&nbsp; MNIT JAIPUR &nbsp;·&nbsp; SESSION-STATE ONLY</span></div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
