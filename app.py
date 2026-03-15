# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  AskMNIT — Premium AI Chat + Student Dashboard (Fully Functional)            ║
# ║                                                                              ║
# ║  ARCHITECTURE DECISION:                                                      ║
# ║  All interactivity uses NATIVE Streamlit widgets — buttons, popovers,        ║
# ║  chat_input, file_uploader, toggles. Premium CSS is injected via             ║
# ║  st.markdown() to style everything to look like a top-tier LLM UI.          ║
# ║                                                                              ║
# ║  The iframe approach was abandoned because sandboxed iframes cannot          ║
# ║  trigger st.session_state changes reliably without full page reloads.        ║
# ║                                                                              ║
# ║  CHAT FEATURES:                                                              ║
# ║  • ➕ New Chat   — clears messages, resets to hero state                     ║
# ║  • ⏱ History    — st.popover with mock previous sessions                    ║
# ║  • ⚙ Settings   — st.popover with live toggles (voice, strict mode)         ║
# ║  • 🔙 Dashboard  — routes back to main dashboard                             ║
# ║  • Suggestion pills — on_click callbacks, immediate message + AI response    ║
# ║  • 📎 Attach     — st.popover with file_uploader                            ║
# ║  • 🎤 Voice      — toggles recording state, shows toast                     ║
# ║  • Send / Enter  — appends message, clears input, triggers AI response       ║
# ║  • Shift effect  — hero centered (0 msgs) → bottom input (>0 msgs)          ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import streamlit as st
import datetime
import random
import base64

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  ← must be first Streamlit call
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
    "Mathematics I/II","Physics","Chemistry","Computer Programming",
    "Basic Electrical","Basic Electronics","Basic Mechanical",
    "Engineering Drawing","Environmental Science",
    "Technical Communication","Basic Economics",
]
BRANCH_SUBJECTS: dict[str,list[str]] = {
    "CSE":        ["Discrete Mathematics","Problem Solving using C"],
    "AI & ML":    ["Mathematics for AI","Data Structures and Algorithms"],
    "ECE":        ["Signals and Systems","Electronic Devices and Circuits"],
    "Civil":      ["Mechanics of Solid","Engineering Geology"],
    "Metallurgy": ["Engineering Materials","Mineral Processing"],
}
BRANCHES  = ["CSE","AI & ML","ECE","Civil","Metallurgy"]
SEMESTERS = [f"Semester {i}" for i in range(1,9)]
DAYS      = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
TYPE_COLORS = {"Lecture":"#22D3EE","Lab":"#F59E0B","Tutorial":"#A78BFA"}

MOCK_HISTORY = [
    ("Today",       "Attendance analysis request"),
    ("Yesterday",   "Mineral Processing PYQs"),
    ("Yesterday",   "Exam prep strategy — CSE"),
    ("2 days ago",  "Fee due date query"),
    ("3 days ago",  "Welding Technology schedule"),
    ("Last week",   "Subject list for Semester 6"),
]

# ─────────────────────────────────────────────────────────────────────────────
# SCHEDULE HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def process_schedule_pdf(file, branch:str) -> dict:
    pool = COMMON_SUBJECTS[:4] + BRANCH_SUBJECTS.get(branch,[])
    random.seed(42)
    TIME_PAIRS = [
        ("08:00","09:00"),("09:30","10:30"),("11:00","12:00"),
        ("12:00","13:00"),("14:00","15:00"),("15:30","16:30"),
    ]
    sched:dict[str,list[dict]] = {}
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

def get_today_slots(fs:dict) -> list[dict]:
    return fs.get(datetime.datetime.now().strftime("%A"),[])

def get_next_class(slots:list[dict]) -> dict|None:
    now = datetime.datetime.now()
    for slot in slots:
        h,m = map(int,slot["time_start"].split(":"))
        dt = now.replace(hour=h,minute=m,second=0,microsecond=0)
        if dt > now:
            return {**slot,"minutes_away":int((dt-now).total_seconds()//60)}
    return None

# ─────────────────────────────────────────────────────────────────────────────
# GENERAL HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def subjects_for_branch(b): return COMMON_SUBJECTS + BRANCH_SUBJECTS.get(b,[])
def blank_att(s): return {x:{"present":0,"total":0} for x in s}
def att_pct(r): return round(r["present"]/r["total"]*100,1) if r["total"] else 0.0
def overall_pct(a):
    tp=sum(r["present"] for r in a.values()); tt=sum(r["total"] for r in a.values())
    return round(tp/tt*100,1) if tt else 0.0
def status_badge(p):
    if p>=75: return "Safe ✅","#10B981","rgba(16,185,129,0.12)"
    if p>=65: return "Low ⚠️","#F59E0B","rgba(245,158,11,0.12)"
    return "Critical 🔴","#EF4444","rgba(239,68,68,0.12)"
def att_color(p): return "#10B981" if p>=75 else "#F59E0B" if p>=65 else "#EF4444"
def initials(n): return "".join(w[0].upper() for w in n.split()[:2]) if n else "??"
def branch_hex(b): return {
    "CSE":"#3B82F6","AI & ML":"#8B5CF6","ECE":"#06B6D4",
    "Civil":"#F59E0B","Metallurgy":"#10B981"
}.get(b,"#6366F1")
def img_to_b64(f):
    d=f.read(); m=f.type or "image/png"
    return f"data:{m};base64,{base64.b64encode(d).decode()}"
def fmt_time(t:str) -> str:
    try:
        h,m=map(int,t.split(":"))
        return f"{h%12 or 12:02d}:{m:02d} {'AM' if h<12 else 'PM'}"
    except: return t

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE — initialise once
# ─────────────────────────────────────────────────────────────────────────────
_def_branch = "CSE"
_DEFAULTS:dict = {
    # Routing
    "view":            "dashboard",
    "nav_page":        "My Dashboard",
    # Profile
    "student_name":    "Sumit Chaudhary",
    "college_id":      "2022UMT1234",
    "semester":        "Semester 6",
    "branch":          _def_branch,
    "profile_pic_b64": "",
    "settings_mode":   None,
    # Attendance
    "attendance":      blank_att(subjects_for_branch(_def_branch)),
    # Schedule
    "schedule_loaded": False,
    "full_schedule":   {},
    "pdf_filename":    "",
    # Notes
    "notes_list": [
        {"text":"Mid-sem revision starts Monday","pinned":False},
        {"text":"Submit fee by 17 Mar",          "pinned":False},
        {"text":"Collect hall ticket from ERP",  "pinned":False},
    ],
    "ql_feedback":       "",
    # Chat state
    "chat_messages":     [],   # list of {"role":"user"|"assistant","content":str}
    "chat_sessions":     [],   # saved sessions
    # Chat settings toggles
    "voice_output":      False,
    "strict_mode":       False,
    "is_recording":      False,
    # Planner
    "planner_overrides": {},
    # Input pending text (for pill callbacks)
    "_pending_message":  "",
}
for k,v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
# AI RESPONSE GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def generate_ai_response(last:str) -> str:
    lower = last.lower()
    att   = st.session_state.attendance
    br    = st.session_state.branch

    if any(w in lower for w in ["attendance","present","absent","%"]):
        ov = overall_pct(att)
        low = [(s,att_pct(r)) for s,r in att.items() if att_pct(r)<75 and r["total"]>0]
        resp = f"**Attendance — {st.session_state.student_name}**\n\nOverall: **{ov}%**\n\n"
        if low:
            resp += "⚠️ **Below 75%:**\n"
            for s,p in low:
                need = max(0,int((0.75*att[s]["total"]-att[s]["present"])/0.25)+1)
                resp += f"- **{s}**: {p}% → need **{need}** more\n"
        else:
            resp += "✅ All subjects above 75%. Stay consistent!"
        return resp

    if any(w in lower for w in ["schedule","class","next","today","timetable"]):
        if st.session_state.schedule_loaded:
            slots = get_today_slots(st.session_state.full_schedule)
            nxt   = get_next_class(slots)
            dn    = datetime.datetime.now().strftime("%A")
            resp  = f"**Today's Classes ({dn})**\n\n"
            for s in slots:
                resp += f"- **{fmt_time(s['time_start'])}–{fmt_time(s['time_end'])}** — {s['subject']} in {s['room']} _({s['type']})_\n"
            if nxt:
                resp += f"\n⏰ **Next:** {nxt['subject']} in **{nxt['minutes_away']} min**"
            else:
                resp += "\n✅ No more classes today."
            return resp
        return "No schedule loaded. Go to **⚙️ Menu → Upload Weekly Schedule** on the dashboard."

    if any(w in lower for w in ["pyq","previous year","question paper","past paper"]):
        return (f"**PYQ Resources for {br}**\n\nAccess via **📂 PYQs** in the dashboard.\n\n"
                f"Branch subjects: {', '.join(BRANCH_SUBJECTS.get(br,[]))}")

    if any(w in lower for w in ["fee","pay","due","payment"]):
        return "Fee details are in the **💰 Fee Portal** section on the dashboard sidebar."

    if any(w in lower for w in ["subject","syllabus","branch","course"]):
        common   = "\n".join(f"- {s}" for s in COMMON_SUBJECTS)
        branch_s = "\n".join(f"- {s}" for s in BRANCH_SUBJECTS.get(br,[]))
        return (f"**Subjects — {br} · {st.session_state.semester}**\n\n"
                f"**Common:**\n{common}\n\n**{br} specific:**\n{branch_s}")

    if any(w in lower for w in ["exam","tip","strategy","prepare","study"]):
        first_bs = BRANCH_SUBJECTS.get(br,["your core subject"])[0]
        return (f"**Exam Prep — {br}**\n\n"
                "1. **Triage by attendance** — below-75% subjects first.\n"
                "2. **PYQ pattern** — last 5 years covers ~70%.\n"
                "3. **Block schedule** — 2-hour deep-work slots.\n"
                f"4. **Group study** — 3-person group for {first_bs}.\n"
                "5. **ERP deadlines** — check submissions weekly.")

    if any(w in lower for w in ["hi","hello","hey","hii"]):
        fn = st.session_state.student_name.split()[0]
        return (f"Hey {fn}! 👋 I'm AskMNIT. I can help with:\n\n"
                "- 📊 Attendance analysis\n"
                "- 📅 Today's schedule\n"
                "- 📂 Previous year papers\n"
                "- 💰 Fee status\n"
                "- 🎯 Exam strategy\n\n"
                f"You're on **{br} · {st.session_state.semester}**. What can I help with?")

    if "attached" in lower or "file" in lower:
        return ("File received! I can help you analyse documents, assignments, or syllabi.\n\n"
                "For now, tell me what you'd like to do with this file.")

    fn = st.session_state.student_name.split()[0]
    return (f"I'm AskMNIT — built for **{fn}** · **{br}**.\n\n"
            "| Topic | Try asking… |\n|---|---|\n"
            "| 📊 Attendance | _Analyse my attendance_ |\n"
            "| 📅 Schedule | _What's next today?_ |\n"
            "| 📂 PYQs | _Find PYQs for my branch_ |\n"
            "| 💰 Fees | _Check fee due date_ |\n"
            "| 🎯 Exams | _Give me an exam strategy_ |")


# ─────────────────────────────────────────────────────────────────────────────
# MESSAGE DISPATCH — shared by all entry points (pills, send, file, etc.)
# ─────────────────────────────────────────────────────────────────────────────
def dispatch_message(text:str):
    """Add user message + AI response to chat, then rerun."""
    text = text.strip()
    if not text:
        return
    st.session_state.chat_messages.append({"role":"user","content":text})
    resp = generate_ai_response(text)
    st.session_state.chat_messages.append({"role":"assistant","content":resp})


# ─────────────────────────────────────────────────────────────────────────────
# PILL CALLBACKS — each pill sends its own message
# ─────────────────────────────────────────────────────────────────────────────
def _pill_cb(text:str):
    dispatch_message(text)

# ═════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS — Premium dark theme applied to all views
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,700;9..144,900&family=DM+Mono:wght@400;500&family=Outfit:wght@300;400;500;600;700&display=swap');

:root {
  --bg:      #070B14;
  --surf:    #0B1120;
  --surf2:   #0E1726;
  --surf3:   #131E30;
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

/* ── Chat message area ── */
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

/* ── Chat input at bottom ── */
[data-testid="stChatInput"] > div {
  background: #111827 !important;
  border: 1px solid rgba(59,130,246,0.28) !important;
  border-radius: 36px !important;
  box-shadow: 0 2px 20px rgba(0,0,0,0.35) !important;
  transition: border-color 0.20s, box-shadow 0.20s !important;
}
[data-testid="stChatInput"] > div:focus-within {
  border-color: rgba(59,130,246,0.58) !important;
  box-shadow: 0 0 0 3px rgba(59,130,246,0.11), 0 4px 24px rgba(37,99,235,0.16) !important;
}
[data-testid="stChatInput"] textarea {
  background: transparent !important;
  color: #E2E8F0 !important;
  font-family: var(--sans) !important;
  font-size: 0.94rem !important;
  caret-color: #3B82F6 !important;
}
[data-testid="stChatInput"] textarea::placeholder {
  color: rgba(148,163,184,0.36) !important;
}
[data-testid="stChatInputSubmitButton"] button,
[data-testid="stChatInput"] button[data-testid="stChatInputSubmitButton"] {
  background: linear-gradient(135deg,#2563EB,#4F46E5) !important;
  border-radius: 10px !important;
  border: none !important;
  box-shadow: 0 3px 14px rgba(37,99,235,0.36) !important;
}

/* ── Text inputs / textareas / selects ── */
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
  border: 1px dashed rgba(59,130,246,0.26) !important; border-radius: 12px !important;
}

/* ── Toggle ── */
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

/* ── NAV PILL buttons ── */
.nav-pill .stButton > button {
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
  border-radius: 999px !important;
  color: rgba(226,232,240,0.72) !important;
  font-size: 0.78rem !important; font-weight: 500 !important;
  padding: 6px 15px !important; box-shadow: none !important;
}
.nav-pill .stButton > button:hover {
  background: rgba(59,130,246,0.16) !important;
  border-color: rgba(59,130,246,0.38) !important;
  color: #BAE6FD !important; transform: none !important;
}

/* ── NAV BACK button (dashboard) ── */
.nav-back .stButton > button {
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  border-radius: 10px !important;
  color: rgba(226,232,240,0.65) !important;
  font-size: 0.78rem !important; font-weight: 600 !important;
  padding: 6px 14px !important; box-shadow: none !important;
}
.nav-back .stButton > button:hover {
  background: rgba(59,130,246,0.14) !important;
  color: #BAE6FD !important; border-color: rgba(59,130,246,0.30) !important;
}

/* ── SUGGESTION CHIP buttons ── */
.sug-pill .stButton > button {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
  border-radius: 999px !important;
  color: rgba(186,230,253,0.74) !important;
  font-size: 0.79rem !important; font-weight: 500 !important;
  padding: 9px 18px !important; box-shadow: none !important;
}
.sug-pill .stButton > button:hover {
  background: rgba(59,130,246,0.14) !important;
  border-color: rgba(59,130,246,0.34) !important;
  color: #BAE6FD !important; transform: translateY(-2px) !important;
}

/* ── ICON BUTTONS (paperclip, mic) ── */
.icon-btn .stButton > button {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: 10px !important;
  color: rgba(148,163,184,0.60) !important;
  font-size: 1.0rem !important;
  padding: 6px 10px !important; box-shadow: none !important;
  width: 38px !important; height: 38px !important;
  display: flex !important; align-items: center !important; justify-content: center !important;
}
.icon-btn .stButton > button:hover {
  background: rgba(255,255,255,0.08) !important;
  color: rgba(148,163,184,0.90) !important; transform: none !important;
}
/* recording state for mic */
.icon-btn-recording .stButton > button {
  background: rgba(239,68,68,0.15) !important;
  border-color: rgba(239,68,68,0.40) !important;
  color: #FCA5A5 !important;
  animation: micPulse 1s ease infinite !important;
}
@keyframes micPulse {
  0%,100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.40); }
  50%      { box-shadow: 0 0 0 6px rgba(239,68,68,0.00); }
}

/* ── Dashboard sidebar buttons ── */
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

/* ── Various dashboard buttons ── */
.ghost-btn .stButton > button {
  background: rgba(255,255,255,.05) !important; border: 1px solid var(--border2) !important;
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
.edit-btn .stButton > button {
  background: rgba(255,255,255,.05) !important; border: 1px solid var(--border2) !important;
  color: rgba(148,163,184,.65) !important; box-shadow: none !important;
  font-size: 0.72rem !important; padding: 4px 10px !important;
}
.edit-btn .stButton > button:hover { color: #BAE6FD !important; background: rgba(59,130,246,.10) !important; }
.pin-btn .stButton > button {
  background: rgba(245,158,11,0.10) !important; border: 1px solid rgba(245,158,11,0.28) !important;
  color: #FCD34D !important; box-shadow: none !important;
  font-size: 0.70rem !important; padding: 4px 10px !important; border-radius: 7px !important;
}
.pin-btn .stButton > button:hover { background: rgba(245,158,11,0.20) !important; transform: none !important; }
.unpin-btn .stButton > button {
  background: rgba(239,68,68,0.09) !important; border: 1px solid rgba(239,68,68,0.24) !important;
  color: #FCA5A5 !important; box-shadow: none !important;
  font-size: 0.70rem !important; padding: 4px 10px !important; border-radius: 7px !important;
}
.unpin-btn .stButton > button:hover { background: rgba(239,68,68,0.18) !important; transform: none !important; }
.del-btn .stButton > button {
  background: rgba(239,68,68,0.07) !important; border: 1px solid rgba(239,68,68,0.18) !important;
  color: rgba(252,165,165,0.70) !important; box-shadow: none !important;
  font-size: 0.68rem !important; padding: 3px 8px !important; border-radius: 6px !important;
}
.del-btn .stButton > button:hover { background: rgba(239,68,68,0.16) !important; transform: none !important; }
.ql-btn .stButton > button {
  background: rgba(255,255,255,.03) !important; border: 1px solid var(--border2) !important;
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
  box-shadow: 0 5px 24px rgba(16,185,129,.36) !important; font-family: var(--mono) !important;
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
  background: rgba(59,130,246,0.13) !important; color: #BAE6FD !important; border-color: rgba(59,130,246,0.30) !important;
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
  border-radius: 999px !important;
  color: rgba(226,232,240,0.72) !important;
  font-family: var(--sans) !important; font-size: 0.78rem !important;
  font-weight: 500 !important; padding: 6px 15px !important;
  box-shadow: none !important; cursor: pointer !important;
  transition: background 0.14s, border-color 0.14s, color 0.14s !important;
}
button[data-testid="stPopoverButton"]:hover {
  background: rgba(59,130,246,0.16) !important;
  border-color: rgba(59,130,246,0.38) !important;
  color: #BAE6FD !important;
}
/* Paperclip icon popover button */
.attach-popover button[data-testid="stPopoverButton"] {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: 10px !important;
  color: rgba(148,163,184,0.60) !important;
  font-size: 1.05rem !important; font-weight: 400 !important;
  padding: 6px 10px !important;
  width: 38px !important; min-width: 38px !important; height: 38px !important;
}
.attach-popover button[data-testid="stPopoverButton"]:hover {
  background: rgba(255,255,255,0.08) !important; color: rgba(148,163,184,0.90) !important;
}

/* ── Progress bars ── */
[data-testid="stProgress"] > div > div {
  border-radius: 99px !important; background: linear-gradient(90deg,#2563EB,#22D3EE) !important;
}
[data-testid="stProgress"] > div {
  background: rgba(255,255,255,.07) !important; border-radius: 99px !important; height: 5px !important;
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
@keyframes pinPulse {
  0%,100% { box-shadow: 0 0 0 0 rgba(245,158,11,0.30); }
  50%      { box-shadow: 0 0 0 6px rgba(245,158,11,0.00); }
}
.pinned-note-card { animation: pinPulse 2.5s ease infinite; }
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# VIEW ROUTER
# ═════════════════════════════════════════════════════════════════════════════
view = st.session_state.view


###############################################################################
# ██████████████████████  CHAT VIEW  █████████████████████████████████████████
###############################################################################
if view == "chat":

    # Hide sidebar completely in chat view
    st.markdown("""
    <style>
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stMainBlockContainer"] {
        padding: 0 !important; max-width: 100% !important;
    }
    /* Add top padding for the fixed-style navbar we build with columns */
    .chat-page-wrapper { padding: 0 max(16px, calc((100% - 880px)/2)); }
    </style>
    """, unsafe_allow_html=True)

    has_messages = len(st.session_state.chat_messages) > 0

    # ── NAVBAR ────────────────────────────────────────────────────────────────
    st.markdown(
        '<div style="'
        'background:rgba(7,11,20,0.96);'
        'backdrop-filter:blur(20px) saturate(180%);'
        'border-bottom:1px solid rgba(59,130,246,0.16);'
        'box-shadow:0 2px 24px rgba(0,0,0,0.50);'
        'padding:10px 22px;'
        'display:flex;align-items:center;justify-content:space-between;'
        'position:sticky;top:0;z-index:1000;'
        '">'
        '<div style="display:flex;align-items:center;gap:9px;">'
        '<div style="width:28px;height:28px;border-radius:8px;'
        'background:linear-gradient(135deg,#2563EB,#4F46E5);'
        'display:flex;align-items:center;justify-content:center;'
        'font-size:0.82rem;font-weight:700;color:white;'
        'box-shadow:0 2px 10px rgba(37,99,235,0.32);">A</div>'
        '<span style="font-family:\'DM Mono\',monospace;font-size:0.88rem;'
        'color:#E2E8F0;">AskMNIT</span>'
        '<span style="font-size:0.56rem;color:#10B981;font-weight:700;'
        'margin-left:2px;">&#9679; AI</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Nav action row — full-width columns aligned right
    _, nc1, nc2, nc3, nc4 = st.columns([4, 1.1, 1, 1, 1.3])

    with nc1:
        st.markdown('<div class="nav-pill">', unsafe_allow_html=True)
        if st.button("➕ New Chat", key="btn_new_chat"):
            if st.session_state.chat_messages:
                fu = next(
                    (m["content"][:38] for m in st.session_state.chat_messages if m["role"]=="user"),
                    "Session"
                )
                st.session_state.chat_sessions.append(
                    {"label": fu+"…", "messages": list(st.session_state.chat_messages)}
                )
            st.session_state.chat_messages = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with nc2:
        with st.popover("⏱ History", use_container_width=True):
            st.markdown(
                '<div style="font-family:\'DM Mono\',monospace;font-size:0.58rem;'
                'color:rgba(148,163,184,0.45);text-transform:uppercase;'
                'letter-spacing:1.2px;margin-bottom:12px;">Chat History</div>',
                unsafe_allow_html=True,
            )
            # Live sessions from this session
            all_sessions = list(st.session_state.chat_sessions)
            # Add mock history items
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
                    idx = len(all_sessions) - 1 - i
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
                            if st.button("↩", key=f"load_sess_{i}"):
                                st.session_state.chat_messages = list(sess["messages"])
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)

    with nc3:
        with st.popover("⚙ Settings", use_container_width=True):
            st.markdown(
                '<div style="font-family:\'DM Mono\',monospace;font-size:0.58rem;'
                'color:rgba(148,163,184,0.45);text-transform:uppercase;'
                'letter-spacing:1.2px;margin-bottom:12px;">Bot Settings</div>',
                unsafe_allow_html=True,
            )
            st.session_state.voice_output = st.toggle(
                "🔊 Enable Voice Output",
                value=st.session_state.voice_output,
                key="toggle_voice",
            )
            st.session_state.strict_mode = st.toggle(
                "🎓 Strict Academic Mode",
                value=st.session_state.strict_mode,
                key="toggle_strict",
            )
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            st.markdown(
                '<div style="font-size:0.78rem;color:rgba(148,163,184,0.52);'
                'line-height:1.70;">'
                f'Model: LLaMA 3.3 70B (via Groq)<br>'
                f'Context: {st.session_state.student_name} · {st.session_state.branch}<br>'
                f'Sessions saved: {len(st.session_state.chat_sessions)}'
                '</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div style="font-size:0.60rem;color:rgba(100,116,139,0.36);margin-top:8px;">'
                'Add GROQ_API_KEY to .streamlit/secrets.toml for live AI.'
                '</div>',
                unsafe_allow_html=True,
            )

    with nc4:
        st.markdown('<div class="nav-back">', unsafe_allow_html=True)
        if st.button("🔙 Dashboard", key="btn_dashboard"):
            st.session_state.view = "dashboard"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        '<div style="height:1px;background:linear-gradient(90deg,'
        'transparent,rgba(59,130,246,0.30),rgba(34,211,238,0.14),transparent);">'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── HERO STATE (no messages) ──────────────────────────────────────────────
    if not has_messages:
        st.markdown("<div style='height:6vh'></div>", unsafe_allow_html=True)

        # Centered hero
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
                '<div style="font-size:0.86rem;color:rgba(148,163,184,0.50);line-height:1.70;'
                'margin-bottom:32px;">'
                'Attendance analysis &nbsp;&#183;&nbsp; PYQ search &nbsp;&#183;&nbsp; '
                'Schedule queries &nbsp;&#183;&nbsp; Exam prep'
                '</div></div>',
                unsafe_allow_html=True,
            )

        # Suggestion pill rows
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        br = st.session_state.branch
        PILLS_ROW1 = [
            f"📊 Analyse my attendance",
            f"📅 What's next on my schedule?",
            f"📂 PYQs for {br}",
            "💰 Check my fee status",
        ]
        PILLS_ROW2 = [
            f"📚 Subjects for {br}",
            "⏰ Exam schedule tips",
        ]

        _, pills_col, _ = st.columns([0.5, 5, 0.5])
        with pills_col:
            # Row 1
            r1_cols = st.columns(len(PILLS_ROW1))
            for i, pill in enumerate(PILLS_ROW1):
                with r1_cols[i]:
                    st.markdown('<div class="sug-pill">', unsafe_allow_html=True)
                    if st.button(pill, key=f"pill_r1_{i}", use_container_width=True):
                        dispatch_message(pill)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            # Row 2 — centered
            _, r2_c1, r2_c2, _ = st.columns([1, 1.5, 1.5, 1])
            for i, (pill, col) in enumerate(zip(PILLS_ROW2, [r2_c1, r2_c2])):
                with col:
                    st.markdown('<div class="sug-pill">', unsafe_allow_html=True)
                    if st.button(pill, key=f"pill_r2_{i}", use_container_width=True):
                        dispatch_message(pill)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:5vh'></div>", unsafe_allow_html=True)

    # ── ACTIVE STATE (messages exist) ────────────────────────────────────────
    else:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        _, msg_col, _ = st.columns([0.5, 5, 0.5])
        with msg_col:
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

    # ── INPUT ROW (always at bottom) ─────────────────────────────────────────
    st.markdown(
        '<div style="'
        'background:rgba(7,11,20,0.94);'
        'backdrop-filter:blur(20px) saturate(160%);'
        'border-top:1px solid rgba(59,130,246,0.12);'
        'padding:10px max(16px,calc((100% - 860px)/2)) 12px;'
        '">'
        '</div>',
        unsafe_allow_html=True,
    )

    # Three-column input bar: [📎] [chat_input] [🎤]
    attach_col, input_col, mic_col = st.columns([0.45, 8, 0.45])

    with attach_col:
        st.markdown('<div style="padding-top:6px;"><div class="attach-popover">', unsafe_allow_html=True)
        with st.popover("📎", use_container_width=False):
            st.markdown(
                '<div style="font-family:\'DM Mono\',monospace;font-size:0.58rem;'
                'color:rgba(148,163,184,0.45);text-transform:uppercase;'
                'letter-spacing:1.2px;margin-bottom:10px;">Attach a file</div>',
                unsafe_allow_html=True,
            )
            attached = st.file_uploader(
                "",
                type=["pdf","txt","png","jpg","jpeg","docx","csv"],
                key="file_uploader_chat",
                label_visibility="collapsed",
            )
            if attached is not None:
                msg_text = f"📎 File **{attached.name}** attached successfully."
                if not st.session_state.chat_messages or \
                   st.session_state.chat_messages[-1]["content"] != msg_text:
                    dispatch_message(msg_text)
                    st.toast(f"📎 {attached.name} attached!", icon="✅")
                    st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)

    with input_col:
        # st.chat_input handles Enter to submit natively
        prompt = st.chat_input(
            placeholder="Ask anything — attendance, schedule, PYQs, fees, exams…",
            key="main_chat_input",
        )
        if prompt:
            dispatch_message(prompt)
            st.rerun()

    with mic_col:
        recording = st.session_state.is_recording
        mic_css = "icon-btn-recording" if recording else "icon-btn"
        st.markdown(f'<div style="padding-top:6px;"><div class="{mic_css}">', unsafe_allow_html=True)
        mic_label = "🔴" if recording else "🎤"
        if st.button(mic_label, key="btn_mic"):
            st.session_state.is_recording = not st.session_state.is_recording
            if st.session_state.is_recording:
                st.toast("🎤 Listening… (speak your question)", icon="🎤")
            else:
                st.toast("Recording stopped.", icon="⏹")
            st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)

    # Disclaimer text
    st.markdown(
        '<p style="text-align:center;font-size:0.59rem;'
        'color:rgba(100,116,139,0.38);margin-top:4px;'
        'font-family:\'DM Mono\',monospace;letter-spacing:0.4px;">'
        'AskMNIT AI can make mistakes &nbsp;&#183;&nbsp; '
        'Verify critical info with official ERP or faculty'
        '</p>',
        unsafe_allow_html=True,
    )

    st.stop()


###############################################################################
# ████████████████████  DASHBOARD VIEW  ██████████████████████████████████████
###############################################################################

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
NAV_ITEMS = [
    ("⬡","My Dashboard"),("📅","My Schedule"),("📚","Academics"),
    ("📝","Study Material"),("📂","PYQs"),("💰","Fee Portal"),("🍱","Mess Menu"),
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
        'Student Portal</div>'
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
        if st.button(f"{icon}  {label}", key="nav_"+label, use_container_width=True):
            st.session_state.nav_page = label; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(
        '<div style="position:fixed;bottom:18px;width:182px;'
        'padding-top:10px;border-top:1px solid rgba(255,255,255,0.06);">',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("🚪  Logout", key="sidebar_logout", use_container_width=True):
        for k in list(st.session_state.keys()): del st.session_state[k]
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
    icon,title,desc = PMETA.get(dash_page,("📄",dash_page,"Coming soon."))
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
# MY DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div style='padding:0 22px 80px;'>", unsafe_allow_html=True)

h_logo, h_mid, h_right = st.columns([2,4,3])
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
    init_str = initials(st.session_state.student_name)
    pic_b64  = st.session_state.profile_pic_b64
    notif = ('<div style="width:30px;height:30px;border-radius:7px;'
             'background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);'
             'display:flex;align-items:center;justify-content:center;font-size:0.86rem;'
             'position:relative;cursor:pointer;">&#128276;'
             '<span style="position:absolute;top:-2px;right:-2px;width:7px;height:7px;'
             'border-radius:50%;background:#EF4444;border:1.5px solid #060A12;"></span></div>')
    if pic_b64:
        av = ('<div style="width:32px;height:32px;border-radius:50%;overflow:hidden;'
              'border:2px solid #3B82F6;box-shadow:0 0 0 2px rgba(59,130,246,0.25);flex-shrink:0;">'
              '<img src="' + pic_b64 + '" style="width:100%;height:100%;object-fit:cover;" /></div>')
    else:
        av = ('<div style="width:32px;height:32px;border-radius:50%;'
              'background:linear-gradient(135deg,#2563EB,#4F46E5);'
              'display:flex;align-items:center;justify-content:center;'
              'font-size:0.66rem;font-weight:700;color:white;'
              'font-family:\'DM Mono\',monospace;'
              'border:2px solid rgba(59,130,246,0.40);flex-shrink:0;">'
              + init_str + '</div>')
    nc, ac, mc = st.columns([1,1,2])
    with nc: st.markdown('<div style="padding:13px 0 9px;display:flex;justify-content:flex-end;">' + notif + '</div>', unsafe_allow_html=True)
    with ac: st.markdown('<div style="padding:13px 0 9px;display:flex;justify-content:center;">' + av + '</div>', unsafe_allow_html=True)
    with mc:
        st.markdown("<div style='padding:9px 0 0;'>", unsafe_allow_html=True)
        with st.popover("⚙️ Menu", use_container_width=True):
            st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:0.58rem;color:rgba(148,163,184,.45);text-transform:uppercase;letter-spacing:1.2px;margin-bottom:10px;">Quick Actions</div>', unsafe_allow_html=True)
            st.markdown('<div class="settings-menu-btn">', unsafe_allow_html=True)
            if st.button("👤  Update Profile", key="menu_profile", use_container_width=True):
                st.session_state.settings_mode = "profile"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            st.markdown('<div class="settings-menu-btn">', unsafe_allow_html=True)
            if st.button("📅  Upload Weekly Schedule", key="menu_schedule", use_container_width=True):
                st.session_state.settings_mode = "schedule"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            st.markdown('<a href="https://mniterp.org/mniterp/" target="_blank" rel="noopener noreferrer" style="text-decoration:none;"><div style="background:linear-gradient(135deg,#065F46,#10B981);color:white;font-family:\'Outfit\',sans-serif;font-weight:700;font-size:0.82rem;padding:9px 16px;border-radius:9px;text-align:center;cursor:pointer;">🔗  ERP — Login</div></a>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div style="height:1px;background:linear-gradient(90deg,transparent,rgba(59,130,246,0.36),rgba(34,211,238,0.18),transparent);margin-bottom:14px;"></div>', unsafe_allow_html=True)

# Settings panels
if st.session_state.settings_mode == "profile":
    with st.expander("👤  Update Profile", expanded=True):
        p1,p2 = st.columns(2)
        with p1:
            new_name = st.text_input("Full Name",  value=st.session_state.student_name, key="ep_name")
            new_cid  = st.text_input("College ID", value=st.session_state.college_id,   key="ep_cid")
        with p2:
            new_sem = st.selectbox("Semester", SEMESTERS, index=SEMESTERS.index(st.session_state.semester) if st.session_state.semester in SEMESTERS else 0, key="ep_sem")
            new_br  = st.selectbox("Branch",   BRANCHES,  index=BRANCHES.index(st.session_state.branch)   if st.session_state.branch   in BRANCHES  else 0, key="ep_branch")
        st.markdown('<div style="font-size:0.60rem;color:rgba(148,163,184,.44);text-transform:uppercase;letter-spacing:0.7px;font-weight:600;margin-top:8px;margin-bottom:4px;">Profile Picture</div>', unsafe_allow_html=True)
        pic_file = st.file_uploader("", type=["png","jpg","jpeg","webp"], key="pic_uploader", label_visibility="collapsed")
        if pic_file: st.session_state.profile_pic_b64 = img_to_b64(pic_file)
        if st.session_state.profile_pic_b64:
            st.markdown('<div style="margin:8px 0;"><div style="width:64px;height:64px;border-radius:50%;overflow:hidden;border:2px solid #3B82F6;"><img src="' + st.session_state.profile_pic_b64 + '" style="width:100%;height:100%;object-fit:cover;" /></div></div>', unsafe_allow_html=True)
        sv1,sv2,_ = st.columns([1,1,3])
        with sv1:
            if st.button("💾 Save Profile", key="save_profile_btn", use_container_width=True):
                bc = new_br != st.session_state.branch
                st.session_state.student_name = new_name; st.session_state.college_id = new_cid
                st.session_state.semester = new_sem; st.session_state.branch = new_br
                if bc:
                    old = st.session_state.attendance
                    st.session_state.attendance = {s:old.get(s,{"present":0,"total":0}) for s in subjects_for_branch(new_br)}
                st.session_state.settings_mode = None; st.rerun()
        with sv2:
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("Cancel", key="cancel_profile_btn", use_container_width=True):
                st.session_state.settings_mode = None; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.settings_mode == "schedule":
    with st.expander("📅  Upload Weekly Schedule", expanded=True):
        if st.session_state.schedule_loaded:
            st.markdown('<div style="background:rgba(16,185,129,.07);border:1px solid rgba(16,185,129,.20);border-radius:9px;padding:8px 12px;margin-bottom:10px;font-size:0.74rem;color:#34D399;">&#128196; Loaded: <b>' + st.session_state.pdf_filename + '</b></div>', unsafe_allow_html=True)
        uploaded_pdf = st.file_uploader("", type=["pdf"], key="pdf_up", label_visibility="collapsed")
        if uploaded_pdf is not None:
            with st.spinner("Analysing…"):
                st.session_state.full_schedule = process_schedule_pdf(uploaded_pdf, st.session_state.branch)
            st.session_state.schedule_loaded = True; st.session_state.pdf_filename = uploaded_pdf.name
            st.success("Loaded: " + uploaded_pdf.name)
        sc1,sc2,_ = st.columns([1,1,3])
        with sc1:
            if st.button("Done", key="done_sched_btn", use_container_width=True):
                st.session_state.settings_mode = None; st.rerun()
        with sc2:
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("Cancel", key="cancel_sched_btn", use_container_width=True):
                st.session_state.settings_mode = None; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# Pinned notes
pinned_notes = [n for n in st.session_state.notes_list if n["pinned"]]
for pi,pnote in enumerate(pinned_notes):
    note_text = pnote["text"]
    note_idx  = next((i for i,n in enumerate(st.session_state.notes_list) if n["text"]==note_text and n["pinned"]),None)
    pcol1,pcol2 = st.columns([8,1])
    with pcol1:
        st.markdown('<div class="pinned-note-card" style="background:linear-gradient(135deg,rgba(245,158,11,0.10),rgba(245,158,11,0.04));border:1px solid rgba(245,158,11,0.40);border-left:4px solid #F59E0B;border-radius:12px;padding:13px 16px;margin-bottom:8px;display:flex;align-items:center;gap:10px;"><span style="font-size:1.1rem;">&#128204;</span><div style="flex:1;"><div style="font-size:0.60rem;font-weight:700;color:#FCD34D;text-transform:uppercase;letter-spacing:1px;margin-bottom:2px;">Pinned Note</div><div style="font-size:0.88rem;font-weight:600;color:#FDE68A;line-height:1.5;">' + note_text + '</div></div></div>', unsafe_allow_html=True)
    with pcol2:
        st.markdown("<div style='padding-top:4px;'>", unsafe_allow_html=True)
        st.markdown('<div class="unpin-btn">', unsafe_allow_html=True)
        if st.button("✕ Unpin", key="unpin_"+str(pi), use_container_width=True):
            if note_idx is not None: st.session_state.notes_list[note_idx]["pinned"] = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ROW 1 — Profile + Attendance
c_profile,c_att = st.columns([1,1.9], gap="large")

with c_profile:
    att_all    = st.session_state.attendance
    ov_pct_val = overall_pct(att_all)
    ov_c       = att_color(ov_pct_val)
    n_subj     = len(att_all)
    low_cnt    = sum(1 for r in att_all.values() if att_pct(r)<75 and r["total"]>0)
    bh_val     = branch_hex(st.session_state.branch)
    pic_b64    = st.session_state.profile_pic_b64
    init_str   = initials(st.session_state.student_name)

    st.markdown('<div style="background:linear-gradient(160deg,#0B1120,#070D1C);border:1px solid rgba(59,130,246,0.22);border-radius:16px;padding:18px 18px 14px;"><div style="font-family:\'DM Mono\',monospace;font-size:0.56rem;color:rgba(148,163,184,.40);text-transform:uppercase;letter-spacing:1.4px;margin-bottom:12px;">// STUDENT PROFILE</div>', unsafe_allow_html=True)
    if pic_b64:
        ab = '<div style="width:52px;height:52px;border-radius:50%;overflow:hidden;border:2px solid #3B82F6;box-shadow:0 4px 14px rgba(37,99,235,0.28);flex-shrink:0;"><img src="' + pic_b64 + '" style="width:100%;height:100%;object-fit:cover;" /></div>'
    else:
        ab = '<div style="width:52px;height:52px;border-radius:50%;flex-shrink:0;background:linear-gradient(135deg,#2563EB,#4F46E5);display:flex;align-items:center;justify-content:center;font-family:\'DM Mono\',monospace;font-size:1.0rem;color:white;border:2px solid rgba(59,130,246,0.40);box-shadow:0 4px 14px rgba(37,99,235,0.28);">' + init_str + '</div>'
    st.markdown(
        '<div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">' + ab +
        '<div style="min-width:0;flex:1;">'
        '<div style="font-weight:700;font-size:0.94rem;color:#E2E8F0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-family:\'Outfit\',sans-serif;margin-bottom:2px;">' + st.session_state.student_name + '</div>'
        '<div style="font-family:\'DM Mono\',monospace;font-size:0.61rem;color:rgba(148,163,184,.50);">' + st.session_state.college_id + '</div>'
        '<div style="display:flex;gap:5px;flex-wrap:wrap;margin-top:6px;">'
        '<span style="font-size:0.59rem;padding:2px 8px;border-radius:4px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.09);color:rgba(186,230,253,.62);">' + st.session_state.semester + '</span>'
        '<span style="font-size:0.59rem;padding:2px 8px;border-radius:4px;background:rgba(255,255,255,.05);border:1px solid ' + bh_val + '44;color:' + bh_val + ';font-weight:700;">' + st.session_state.branch + '</span>'
        '</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-bottom:12px;">' +
        ''.join(
            '<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:8px;padding:8px 9px;text-align:center;">'
            '<div style="font-family:\'DM Mono\',monospace;font-size:0.88rem;font-weight:600;color:' + vc + ';margin-bottom:1px;">' + str(vv) + '</div>'
            '<div style="font-size:0.55rem;color:rgba(148,163,184,.40);text-transform:uppercase;letter-spacing:0.5px;">' + lb + '</div>'
            '</div>'
            for vv,vc,lb in [
                (str(ov_pct_val)+"%", ov_c,   "Overall"),
                (n_subj,              "#60A5FA","Subjects"),
                (low_cnt, "#EF4444" if low_cnt else "#10B981", "Low Att"),
            ]
        ) + '</div>',
        unsafe_allow_html=True,
    )
    if st.session_state.schedule_loaded:
        st.markdown('<div style="background:rgba(16,185,129,.07);border:1px solid rgba(16,185,129,.18);border-radius:7px;padding:5px 10px;margin-bottom:8px;font-size:0.66rem;color:#34D399;display:flex;gap:5px;align-items:center;">&#128196; ' + st.session_state.pdf_filename + '</div>', unsafe_allow_html=True)
    st.markdown('<div class="open-chat-btn">', unsafe_allow_html=True)
    if st.button("🤖  AskMNIT AI", key="open_chat_from_dash", use_container_width=True):
        st.session_state.view = "chat"; st.session_state.chat_messages = []; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c_att:
    att_all = st.session_state.attendance; ov = overall_pct(att_all)
    s_lbl,s_tc,s_bg = status_badge(ov); ov_c = att_color(ov)
    st.markdown('<div style="background:linear-gradient(160deg,#0B1120,#070D1C);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:18px 18px 14px;"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;"><span style="font-family:\'DM Mono\',monospace;font-size:0.56rem;color:rgba(148,163,184,.40);text-transform:uppercase;letter-spacing:1.4px;">// ATTENDANCE METER</span><span style="font-size:0.63rem;font-weight:700;padding:3px 10px;border-radius:999px;background:' + s_bg + ';color:' + s_tc + ';border:1px solid ' + s_tc + '44;">' + s_lbl + '</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="display:flex;align-items:center;gap:14px;margin-bottom:10px;"><div style="font-family:\'DM Mono\',monospace;font-size:2.3rem;color:' + ov_c + ';letter-spacing:-2px;line-height:1;">' + str(ov) + '<span style="font-size:1.0rem;">%</span></div><div><div style="font-size:0.67rem;color:rgba(148,163,184,.48);">Overall Attendance</div><div style="font-size:0.59rem;color:rgba(100,116,139,.40);margin-top:2px;">Min 75%  ·  ' + str(len(att_all)) + ' subjects  ·  ' + st.session_state.branch + '</div></div></div>', unsafe_allow_html=True)
    st.progress(min(ov/100,1.0))
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    def render_subj_rows(subj_list, prefix):
        for i,subj in enumerate(subj_list):
            if subj not in att_all: continue
            rec=att_all[subj]; spct=att_pct(rec); sc=att_color(spct)
            kp=prefix+"_p_"+str(i); ka=prefix+"_a_"+str(i)
            st.markdown('<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.055);border-radius:10px;padding:8px 10px;margin-bottom:6px;">', unsafe_allow_html=True)
            r1,r2,r3,r4=st.columns([4,1.5,1.1,1.1])
            with r1:
                st.markdown('<div style="font-size:0.76rem;font-weight:600;color:#E2E8F0;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">' + subj + '</div><div style="font-family:\'DM Mono\',monospace;font-size:0.61rem;color:rgba(148,163,184,.44);">' + str(rec["present"]) + '/' + str(rec["total"]) + '</div>', unsafe_allow_html=True)
                st.progress(min(spct/100,1.0))
            with r2: st.markdown('<div style="text-align:right;font-family:\'DM Mono\',monospace;font-weight:600;font-size:1.0rem;color:' + sc + ';padding-top:4px;">' + str(spct) + '%</div>', unsafe_allow_html=True)
            with r3:
                st.markdown('<div class="present-btn">', unsafe_allow_html=True)
                if st.button("✓ P", key=kp, use_container_width=True):
                    st.session_state.attendance[subj]["present"]+=1; st.session_state.attendance[subj]["total"]+=1; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with r4:
                st.markdown('<div class="absent-btn">', unsafe_allow_html=True)
                if st.button("✗ A", key=ka, use_container_width=True):
                    st.session_state.attendance[subj]["total"]+=1; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    branch_only = BRANCH_SUBJECTS.get(st.session_state.branch,[])
    with st.expander("📘  Common Subjects  ("+str(len(COMMON_SUBJECTS))+")", expanded=True):
        render_subj_rows(COMMON_SUBJECTS,"cmn")
    if branch_only:
        with st.expander("🔬  "+st.session_state.branch+" Subjects  ("+str(len(branch_only))+")", expanded=True):
            render_subj_rows(branch_only,"brnch")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

# Schedule section
today_name = datetime.datetime.now().strftime("%A"); now_hm = datetime.datetime.now().hour*60+datetime.datetime.now().minute
st.markdown('<div style="background:linear-gradient(160deg,#0B1120,#070D1C);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:18px 18px 14px;margin-bottom:14px;"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;"><span style="font-family:\'DM Mono\',monospace;font-size:0.56rem;color:rgba(148,163,184,.40);text-transform:uppercase;letter-spacing:1.4px;">// TODAY\'S CLASS SCHEDULE</span><span style="font-family:\'DM Mono\',monospace;font-size:0.62rem;color:rgba(96,165,250,.65);">' + today_name.upper() + '</span></div>', unsafe_allow_html=True)
if st.session_state.schedule_loaded:
    today_slots = get_today_slots(st.session_state.full_schedule); nxt = get_next_class(today_slots)
    if nxt:
        mins=nxt["minutes_away"]; hrs=mins//60; rem=mins%60; cd_str=(f"{hrs}h {rem}m" if hrs else f"{rem} min")+" away"
        urg_c="#EF4444" if mins<15 else "#F59E0B" if mins<45 else "#22D3EE"
        st.markdown('<div style="background:linear-gradient(90deg,rgba(34,211,238,.06),rgba(37,99,235,.04));border:1px solid rgba(34,211,238,.18);border-radius:10px;padding:10px 16px;margin-bottom:14px;display:flex;align-items:center;justify-content:space-between;"><div><div style="font-size:0.57rem;color:rgba(148,163,184,.46);text-transform:uppercase;letter-spacing:0.8px;margin-bottom:2px;">Next Class</div><div style="font-weight:700;font-size:0.86rem;color:#E2E8F0;">' + nxt["subject"] + '  <span style="font-size:0.67rem;color:rgba(148,163,184,.46);">' + nxt["room"] + '</span></div></div><div style="font-family:\'DM Mono\',monospace;font-size:0.96rem;font-weight:600;color:' + urg_c + ';text-align:right;">' + cd_str + '<div style="font-size:0.57rem;color:rgba(148,163,184,.42);font-weight:400;margin-top:1px;">' + fmt_time(nxt["time_start"]) + ' – ' + fmt_time(nxt["time_end"]) + '</div></div></div>', unsafe_allow_html=True)
    if today_slots:
        rows=[today_slots[i:i+3] for i in range(0,len(today_slots),3)]
        for row in rows:
            cols=st.columns(len(row))
            for ci,(col,slot) in enumerate(zip(cols,row)):
                sh,sm=map(int,slot["time_start"].split(":")); is_past=(sh*60+sm)<now_hm
                tc=TYPE_COLORS.get(slot["type"],"#60A5FA")
                is_next=(nxt is not None and slot["time_start"]==nxt["time_start"] and slot["subject"]==nxt["subject"])
                bc=tc if not is_past else "rgba(255,255,255,0.06)"; cbg="linear-gradient(160deg,rgba(34,211,238,0.06),rgba(37,99,235,0.03))" if is_next else "rgba(255,255,255,0.02)" if not is_past else "rgba(255,255,255,0.01)"
                with col:
                    st.markdown('<div style="background:' + cbg + ';border:1px solid ' + bc + ';border-left:3px solid ' + bc + ';border-radius:12px;padding:13px 14px;margin-bottom:8px;position:relative;overflow:hidden;"><div style="position:absolute;top:10px;right:10px;width:7px;height:7px;border-radius:50%;background:' + tc + ';opacity:' + ("1" if not is_past else "0.35") + ';' + ("box-shadow:0 0 6px "+tc+";" if is_next else "") + '"></div><div style="font-family:\'DM Mono\',monospace;font-size:0.78rem;font-weight:700;color:' + ("#E2E8F0" if not is_past else "rgba(148,163,184,0.32)") + ';margin-bottom:6px;line-height:1.2;">' + fmt_time(slot["time_start"]) + '<br><span style="font-size:0.62rem;font-weight:400;color:rgba(148,163,184,0.45);">– ' + fmt_time(slot["time_end"]) + '</span></div><div style="font-size:0.82rem;font-weight:700;color:' + ("#F1F5F9" if not is_past else "rgba(148,163,184,0.28)") + ';margin-bottom:5px;line-height:1.3;">' + slot["subject"] + '</div><div style="display:flex;align-items:center;gap:6px;"><span style="font-size:0.62rem;color:rgba(148,163,184,.48);">' + slot["room"] + '</span><span style="font-size:0.58rem;padding:1px 7px;border-radius:4px;background:' + tc + '1A;color:' + tc + ';font-weight:600;">' + slot["type"] + '</span>' + ('  <span style="font-size:0.58rem;color:#22D3EE;font-weight:700;">&#9679; NEXT</span>' if is_next else '') + '</div>' + ('<div style="font-size:0.58rem;color:rgba(148,163,184,.28);margin-top:4px;text-decoration:line-through;">Done</div>' if is_past else '') + '</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align:center;padding:24px;color:rgba(148,163,184,.40);font-size:0.80rem;">No classes for ' + today_name + '.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div style="background:rgba(59,130,246,.04);border:1px dashed rgba(59,130,246,.20);border-radius:9px;padding:9px 13px;margin-bottom:12px;font-size:0.73rem;color:rgba(148,163,184,.48);">&#128196;  Use <b>&#9881;&#65039; Menu &#8594; Upload Weekly Schedule</b> to activate the planner.</div>', unsafe_allow_html=True)
    if "planner_overrides" not in st.session_state: st.session_state.planner_overrides = {}
    for st_start,st_end in [("08:00","09:00"),("09:30","10:30"),("11:00","12:00"),("12:00","13:00"),("14:00","15:00"),("15:30","16:30")]:
        override=st.session_state.planner_overrides.get(st_start,"")
        mp1,mp2,mp3,mp4=st.columns([1.6,4,0.8,2.2])
        with mp1: st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:0.68rem;color:#60A5FA;padding-top:10px;white-space:nowrap;font-weight:700;">' + fmt_time(st_start) + '<br><span style="font-size:0.56rem;font-weight:400;color:rgba(148,163,184,.38);">– ' + fmt_time(st_end) + '</span></div>', unsafe_allow_html=True)
        with mp2: note_v=st.text_input("",value=override,placeholder="Task…",key="mp_"+st_start,label_visibility="collapsed")
        with mp3:
            st.markdown('<div class="save-btn">', unsafe_allow_html=True)
            if st.button("💾",key="sv_mp_"+st_start,use_container_width=True): st.session_state.planner_overrides[st_start]=note_v; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with mp4:
            saved=st.session_state.planner_overrides.get(st_start,"")
            if saved: st.markdown('<div style="font-size:0.67rem;color:#34D399;background:rgba(16,185,129,.07);border:1px solid rgba(16,185,129,.14);border-radius:7px;padding:4px 9px;margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">&#10003; ' + saved + '</div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# Notes & Quick Links
ql_col,notes_col=st.columns([1,1.5],gap="large")
with ql_col:
    st.markdown('<div style="background:linear-gradient(160deg,#0B1120,#070D1C);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:18px 18px 14px;height:100%;"><div style="font-family:\'DM Mono\',monospace;font-size:0.56rem;color:rgba(148,163,184,.40);text-transform:uppercase;letter-spacing:1.4px;margin-bottom:12px;">// QUICK LINKS</div>', unsafe_allow_html=True)
    QL=[("📤","Upload Syllabus","Syllabus uploader will be enabled here."),("🔗","Add PYQ Link","PYQ link manager will open here."),("🔍","Library Search","Library search will open here.")]
    st.markdown('<div class="ql-btn">', unsafe_allow_html=True)
    for ico,lbl,fb in QL:
        if st.button(ico+"  "+lbl,key="ql_"+lbl,use_container_width=True): st.session_state.ql_feedback=fb; st.rerun()
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if st.session_state.ql_feedback: st.markdown('<div style="background:rgba(59,130,246,.06);border:1px solid rgba(59,130,246,.18);border-radius:8px;padding:7px 11px;margin-top:7px;font-size:0.70rem;color:rgba(186,230,253,.58);line-height:1.5;">' + st.session_state.ql_feedback + '</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with notes_col:
    st.markdown('<div style="background:linear-gradient(160deg,#0B1120,#070D1C);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:18px 18px 14px;"><div style="font-family:\'DM Mono\',monospace;font-size:0.56rem;color:rgba(148,163,184,.40);text-transform:uppercase;letter-spacing:1.4px;margin-bottom:12px;">// PERSONAL NOTES</div>', unsafe_allow_html=True)
    new_note_input=st.text_input("",placeholder="Type a new note…",key="new_note_input_field",label_visibility="collapsed")
    ac,_=st.columns([1,3])
    with ac:
        if st.button("➕ Add Note",key="add_note_btn",use_container_width=True):
            txt=new_note_input.strip()
            if txt: st.session_state.notes_list.append({"text":txt,"pinned":False}); st.rerun()
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    unpinned=[(i,n) for i,n in enumerate(st.session_state.notes_list) if not n["pinned"]]
    if not unpinned:
        st.markdown('<div style="font-size:0.76rem;color:rgba(148,163,184,.38);text-align:center;padding:16px;font-style:italic;">No notes yet.</div>', unsafe_allow_html=True)
    else:
        for i,note in unpinned:
            nr1,nr2,nr3=st.columns([5,1.2,1])
            with nr1: st.markdown('<div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.07);border-radius:9px;padding:9px 12px;margin-bottom:4px;font-size:0.80rem;color:rgba(226,232,240,0.75);line-height:1.5;">' + note["text"] + '</div>', unsafe_allow_html=True)
            with nr2:
                st.markdown('<div class="pin-btn">', unsafe_allow_html=True)
                if st.button("📌 Pin",key="pin_note_"+str(i),use_container_width=True): st.session_state.notes_list[i]["pinned"]=True; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with nr3:
                st.markdown('<div class="del-btn">', unsafe_allow_html=True)
                if st.button("🗑",key="del_note_"+str(i),use_container_width=True): st.session_state.notes_list.pop(i); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div style="text-align:center;margin-top:28px;padding:10px 0;border-top:1px solid rgba(255,255,255,0.05);"><span style="font-family:\'DM Mono\',monospace;font-size:0.52rem;color:rgba(148,163,184,0.24);letter-spacing:1.2px;">ASKMNT &nbsp;·&nbsp; MNIT JAIPUR &nbsp;·&nbsp; SESSION-STATE ONLY</span></div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
