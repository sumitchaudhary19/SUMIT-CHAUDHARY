# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  AskMNIT — v6.0 CLEAN                                                       ║
# ║  Fixes: No sidebar in chat, centered input bar, working navbar buttons       ║
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

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def process_schedule_pdf(file, branch):
    pool = COMMON_SUBJECTS[:4] + BRANCH_SUBJECTS.get(branch, [])
    random.seed(42)
    TIME_PAIRS = [
        ("08:00","09:00"),("09:30","10:30"),("11:00","12:00"),
        ("12:00","13:00"),("14:00","15:00"),("15:30","16:30"),
    ]
    sched = {}
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

def get_today_slots(fs):
    return fs.get(datetime.datetime.now().strftime("%A"), [])

def get_next_class(slots):
    now = datetime.datetime.now()
    for slot in slots:
        h, m = map(int, slot["time_start"].split(":"))
        dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if dt > now:
            return {**slot, "minutes_away": int((dt - now).total_seconds() // 60)}
    return None

def subjects_for_branch(b): return COMMON_SUBJECTS + BRANCH_SUBJECTS.get(b, [])
def blank_att(s):           return {x: {"present":0,"total":0} for x in s}
def att_pct(r):             return round(r["present"]/r["total"]*100,1) if r["total"] else 0.0
def overall_pct(a):
    tp = sum(r["present"] for r in a.values())
    tt = sum(r["total"]   for r in a.values())
    return round(tp/tt*100,1) if tt else 0.0
def status_badge(p):
    if p>=75: return "Safe","#10B981","rgba(16,185,129,0.12)"
    if p>=65: return "Low","#F59E0B","rgba(245,158,11,0.12)"
    return "Critical","#EF4444","rgba(239,68,68,0.12)"
def att_color(p):   return "#10B981" if p>=75 else "#F59E0B" if p>=65 else "#EF4444"
def initials(n):    return "".join(w[0].upper() for w in n.split()[:2]) if n else "??"
def branch_hex(b):  return {"CSE":"#3B82F6","AI & ML":"#8B5CF6","ECE":"#06B6D4","Civil":"#F59E0B","Metallurgy":"#10B981"}.get(b,"#6366F1")
def img_to_b64(f):
    d=f.read(); m=f.type or "image/png"
    return f"data:{m};base64,{base64.b64encode(d).decode()}"
def fmt_time(t):
    try:
        h,m=map(int,t.split(":")); return f"{h%12 or 12:02d}:{m:02d} {'AM' if h<12 else 'PM'}"
    except: return t
def _safe_key(s): return "".join(c if c.isalnum() else "_" for c in s)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
_def_branch = "CSE"
_DEFAULTS = {
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
def _build_student_context() -> str:
    att  = st.session_state.attendance
    br   = st.session_state.branch
    nm   = st.session_state.student_name
    sem  = st.session_state.semester
    ov   = overall_pct(att)
    low  = [(s, att_pct(r)) for s, r in att.items() if att_pct(r) < 75 and r["total"] > 0]
    good = [(s, att_pct(r)) for s, r in att.items() if att_pct(r) >= 75 and r["total"] > 0]
    att_summary = f"Overall attendance: {ov}%\n"
    if low:
        att_summary += "BELOW 75% (critical):\n"
        for s, p in low:
            r = att[s]
            need = max(0, int((0.75 * r["total"] - r["present"]) / 0.25) + 1)
            att_summary += f"  - {s}: {p}% ({r['present']}/{r['total']}) — needs {need} more classes\n"
    if good:
        att_summary += "Above 75%:\n"
        for s, p in good[:5]:
            att_summary += f"  - {s}: {p}%\n"
    sched_summary = "Schedule not uploaded yet."
    if st.session_state.schedule_loaded:
        today_slots = get_today_slots(st.session_state.full_schedule)
        nxt = get_next_class(today_slots)
        dn  = datetime.datetime.now().strftime("%A")
        if today_slots:
            sched_summary = f"Today ({dn}):\n"
            for sl in today_slots:
                sched_summary += f"  {fmt_time(sl['time_start'])}–{fmt_time(sl['time_end'])}: {sl['subject']} @ {sl['room']} ({sl['type']})\n"
            sched_summary += f"Next class: {nxt['subject']} in {nxt['minutes_away']} min\n" if nxt else "No more classes today.\n"
        else:
            sched_summary = f"No classes today ({dn})."
    return f"""
Student: {nm} | Branch: {br} | Semester: {sem} | ID: {st.session_state.college_id}
Subjects: {", ".join(subjects_for_branch(br))}
Attendance: {att_summary}
Schedule: {sched_summary}
Response style pref: {st.session_state.response_style}
"""

def _detect_mood(text):
    t = text.lower()
    if any(w in t for w in ["stressed","tension","worried","dar","bhot pressure","exam tension","fail","nahi hua","rona","roo","samajh nahi","confused"]):
        return "STRESSED/ANXIOUS — be warm and reassuring first, solutions after"
    if any(w in t for w in ["happy","khush","amazing","got","cleared","hogaya","yay","😄","🎉","🥳","woah","lets go"]):
        return "EXCITED/HAPPY — match their energy, celebrate with them"
    if any(w in t for w in ["bored","kya karu","nothing","bakwaas","boring","time pass"]):
        return "BORED — be playful and engaging"
    if any(w in t for w in ["angry","gussa","bakwas","worst","hate","ugh","aarrgh","irritating","frustrat"]):
        return "FRUSTRATED — validate their feelings immediately before solving"
    if any(w in t for w in ["thak","tired","neend","so raha","sleep","exhausted"]):
        return "TIRED — be gentle, keep it short and supportive"
    return "NEUTRAL/CASUAL — be friendly and natural"

def generate_ai_response(last: str) -> str:
    import requests
    nm          = st.session_state.student_name.split()[0]
    br          = st.session_state.branch
    student_ctx = _build_student_context()
    mood_hint   = _detect_mood(last)
    system_prompt = f"""You are AskMNIT — not a bot, but {nm}'s most brilliant and chill senior at MNIT Jaipur.

DETECTED STUDENT MOOD: {mood_hint}
→ Adjust tone accordingly from the first word.

YOUR PERSONALITY:
- Warm like a best friend, sharp like a topper
- Naturally mix Hindi + English (Hinglish) if student uses it
- Funny when appropriate — NEVER sound like a corporate chatbot
- Short punchy sentences > long paragraphs
- When stressed → acknowledge feeling first, THEN help
- When excited → vibe with them first

STUDENT DATA:
{student_ctx}

HARD RULES:
1. Call them "{nm}" or "yaar/bhai" — never "user" or "student"
2. Attendance math must be EXACT using data above
3. Schedule info must come EXACTLY from data above
4. If unsure → say "yaar iske baare mein sure nahi, ERP check kar"
5. NEVER say "I'm an AI" — you're AskMNIT, {nm}'s senior
6. Keep it conversational and natural"""

    history = st.session_state.chat_messages[:-1]
    api_messages = []
    for msg in history[-16:]:
        api_messages.append({"role": msg["role"], "content": msg["content"]})
    api_messages.append({"role": "user", "content": last})

    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "") or st.session_state.get("groq_api_key", "")
    if not GROQ_API_KEY:
        return (f"Yaar, Groq API key set nahi hai abhi 😅\n\n"
                f"`.streamlit/secrets.toml` mein `GROQ_API_KEY = 'gsk_...'` add kar, phir restart kar!")
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role":"system","content":system_prompt}, *api_messages],
                "max_tokens": 900, "temperature": 0.82, "top_p": 0.90, "stream": False,
            },
            timeout=30,
        )
        data = resp.json()
        if resp.status_code == 200:
            return data["choices"][0]["message"]["content"].strip()
        else:
            err = data.get("error", {}).get("message", "Unknown Groq error")
            return f"Arrey yaar, Groq API ne chakkar de diya 😬\n`{err}`\n\nThodi der baad try kar!"
    except requests.Timeout:
        return "Yaar connection slow lag raha hai ⏳ — ek minute ruk ke dobara try kar!"
    except Exception as e:
        return f"Kuch toh gadbad hai yaar 😅 ({str(e)[:80]})\n\nInternet/API key check kar!"

def dispatch_message(text: str):
    text = text.strip()
    if not text: return
    st.session_state.chat_messages.append({"role":"user","content":text})
    with st.spinner("AskMNIT soch raha hai... 🤔"):
        reply = generate_ai_response(text)
    st.session_state.chat_messages.append({"role":"assistant","content":reply})

# ─────────────────────────────────────────────────────────────────────────────
# THEME CSS
# ─────────────────────────────────────────────────────────────────────────────
def get_theme_css() -> str:
    if st.session_state.chat_theme == "light":
        return """
html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"]{background:#F0F4FF!important;color:#1E2A3A!important;}
.gemini-bar [data-testid="stForm"]{background:#FFFFFF!important;border-color:rgba(37,99,235,0.22)!important;}
.gemini-bar [data-testid="stTextInput"] input{color:#1E2A3A!important;caret-color:#2563EB!important;}
.gemini-bar [data-testid="stTextInput"] input::placeholder{color:rgba(60,80,110,0.45)!important;}
.gemini-bar-anchored{background:rgba(240,244,255,0.97)!important;border-top-color:rgba(37,99,235,0.15)!important;}
[data-testid="stChatMessage"]{background:rgba(255,255,255,0.85)!important;border-color:rgba(0,0,0,0.08)!important;}
"""
    return """
html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"]{background:#070B14!important;color:#E2E8F0!important;}
"""

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,700;9..144,900&family=DM+Mono:wght@400;500&family=Outfit:wght@300;400;500;600;700&display=swap');

*,html,body{box-sizing:border-box;margin:0;padding:0;}
html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"]{font-family:'Outfit',sans-serif!important;}
header[data-testid="stHeader"],footer,#MainMenu,[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important;}
[data-testid="stMainBlockContainer"]{padding:0!important;max-width:100%!important;}

/* ── HIDE SIDEBAR COMPLETELY IN CHAT VIEW ── */
[data-chat-view="true"] [data-testid="stSidebar"],
[data-chat-view="true"] [data-testid="stSidebarCollapseButton"],
[data-chat-view="true"] [data-testid="collapsedControl"]{display:none!important;}

/* Dashboard sidebar */
[data-testid="stSidebar"]{background:#0B1120!important;border-right:1px solid rgba(59,130,246,0.16)!important;min-width:260px!important;max-width:260px!important;}
[data-testid="stSidebar"]>div{padding:0!important;}
.sb-section-header{font-family:'DM Mono',monospace;font-size:0.60rem;font-weight:700;color:rgba(148,163,184,0.50);text-transform:uppercase;letter-spacing:1.4px;padding:14px 16px 6px;border-top:1px solid rgba(255,255,255,0.05);margin-top:4px;}
.sb-history-item{display:flex;align-items:center;gap:8px;padding:7px 16px;cursor:pointer;font-size:0.80rem;color:rgba(148,163,184,0.70);border-bottom:1px solid rgba(255,255,255,0.03);}
.sb-history-item:hover{background:rgba(59,130,246,0.09);color:#BAE6FD;}
.sb-history-dot{width:5px;height:5px;border-radius:50%;background:#3B82F6;flex-shrink:0;}
[data-testid="stSidebar"] .stButton>button{background:rgba(239,68,68,0.10)!important;border:1px solid rgba(239,68,68,0.28)!important;color:#FCA5A5!important;border-radius:8px!important;font-size:0.80rem!important;font-weight:600!important;padding:7px 14px!important;box-shadow:none!important;}
[data-testid="stSidebar"] .stButton>button:hover{background:rgba(239,68,68,0.20)!important;transform:none!important;}
.sb-theme-dark-btn .stButton>button{background:rgba(15,23,42,0.80)!important;border:1.5px solid rgba(59,130,246,0.35)!important;color:#60A5FA!important;border-radius:8px!important;font-size:0.80rem!important;padding:7px 12px!important;box-shadow:none!important;}
.sb-theme-light-btn .stButton>button{background:rgba(240,244,255,0.15)!important;border:1.5px solid rgba(148,163,184,0.25)!important;color:rgba(226,232,240,0.75)!important;border-radius:8px!important;font-size:0.80rem!important;padding:7px 12px!important;box-shadow:none!important;}

/* ── CHAT FIXED NAVBAR ── */
.chat-topbar{
  position:fixed;top:0;left:0;right:0;z-index:9999;
  height:52px;
  background:rgba(7,11,20,0.97);
  backdrop-filter:blur(24px) saturate(200%);
  -webkit-backdrop-filter:blur(24px) saturate(200%);
  border-bottom:1px solid rgba(59,130,246,0.18);
  box-shadow:0 2px 20px rgba(0,0,0,0.60);
  display:flex;align-items:center;justify-content:space-between;
  padding:0 24px;
}
.chat-topbar-logo{display:flex;align-items:center;gap:9px;}
.chat-topbar-logo-icon{width:28px;height:28px;border-radius:8px;background:linear-gradient(135deg,#2563EB,#4F46E5);display:flex;align-items:center;justify-content:center;font-size:0.82rem;font-weight:700;color:#fff;box-shadow:0 3px 10px rgba(37,99,235,0.30);}
.chat-topbar-spacer{height:60px;width:100%;}
.chat-topbar-divider{height:1px;background:linear-gradient(90deg,transparent,rgba(59,130,246,0.28),rgba(34,211,238,0.12),transparent);margin-bottom:6px;}

/* Navbar real Streamlit buttons — vertical stack, upper LEFT corner */
.nb-real{
  position:fixed!important;
  top:60px!important;   /* below the topbar */
  left:12px!important;
  z-index:10000!important;
  display:flex!important;
  flex-direction:column!important;
  align-items:flex-start!important;
  gap:5px!important;
  background:transparent!important;
  pointer-events:auto!important;
}
.nb-real .stButton>button{
  border-radius:10px!important;
  padding:5px 14px!important;
  font-size:0.74rem!important;font-weight:500!important;
  height:30px!important;min-height:30px!important;line-height:1!important;
  border:1px solid rgba(255,255,255,0.10)!important;
  background:rgba(10,12,28,0.82)!important;
  color:rgba(200,212,240,0.78)!important;
  box-shadow:none!important;
  transition:all 0.14s!important;
  white-space:nowrap!important;
  width:auto!important;
  min-width:110px!important;
  backdrop-filter:blur(8px)!important;
}
.nb-real .stButton>button:hover{
  background:rgba(59,130,246,0.16)!important;
  border-color:rgba(59,130,246,0.38)!important;
  color:#BAE6FD!important;transform:none!important;
}
.nb-new .stButton>button{
  background:rgba(59,130,246,0.14)!important;
  border-color:rgba(59,130,246,0.32)!important;
  color:#93C5FD!important;
}
.nb-on .stButton>button{
  background:rgba(59,130,246,0.22)!important;
  border-color:rgba(59,130,246,0.50)!important;
  color:#BAE6FD!important;
}
/* Each column in the vertical stack = auto-width, no stretch */
.nb-real [data-testid="stVerticalBlock"]{gap:5px!important;}
.nb-real [data-testid="column"]{padding:0!important;width:auto!important;flex:0 0 auto!important;min-width:unset!important;}
.nb-real [data-testid="stHorizontalBlock"]{flex-direction:column!important;gap:5px!important;align-items:flex-start!important;}

/* ── Chat messages ── */
[data-testid="stChatMessage"]{background:rgba(255,255,255,0.025)!important;border:1px solid rgba(255,255,255,0.06)!important;border-radius:14px!important;font-family:'Outfit',sans-serif!important;}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]){background:rgba(37,99,235,0.08)!important;border-color:rgba(59,130,246,0.16)!important;}

/* ── GEMINI BAR — Purple 3D Premium ── */
@keyframes bar3dShine {
  0%   { background-position: 200% center; }
  100% { background-position: -200% center; }
}
@keyframes barIdleGlow {
  0%,100% {
    box-shadow:
      0 8px 32px rgba(80,20,140,0.55),
      0 2px 0 rgba(180,100,255,0.18) inset,
      0 -1px 0 rgba(30,5,60,0.70) inset;
  }
  50% {
    box-shadow:
      0 8px 48px rgba(120,40,200,0.70),
      0 0 0 1.5px rgba(160,80,255,0.30),
      0 0 40px rgba(140,60,220,0.22),
      0 2px 0 rgba(200,120,255,0.22) inset,
      0 -1px 0 rgba(30,5,60,0.70) inset;
  }
}
.gemini-bar [data-testid="stForm"]{
  /* Deep purple base — screenshot 2 color */
  background: linear-gradient(135deg, #2D1B69 0%, #1E0E4A 40%, #3B1380 100%) !important;
  border: 1.5px solid rgba(160,80,255,0.35) !important;
  border-radius: 28px !important;
  padding: 6px 8px 6px 2px !important;
  min-height: 60px !important;
  /* 3D top-highlight + bottom shadow */
  box-shadow:
    0 8px 32px rgba(80,20,140,0.55),
    0 2px 0 rgba(180,100,255,0.18) inset,
    0 -1px 0 rgba(30,5,60,0.70) inset !important;
  animation: barIdleGlow 4s ease-in-out infinite !important;
  position: relative !important;
  overflow: hidden !important;
}
/* Shine streak pseudo-element via a child overlay div */
.gemini-bar [data-testid="stForm"]::before {
  content: '' !important;
  position: absolute !important;
  top: 0 !important; left: -100% !important;
  width: 60% !important; height: 100% !important;
  background: linear-gradient(105deg, transparent 20%, rgba(220,180,255,0.10) 50%, transparent 80%) !important;
  animation: bar3dShine 5s linear infinite !important;
  pointer-events: none !important;
  border-radius: 28px !important;
}
.gemini-bar [data-testid="stForm"]:focus-within {
  animation: none !important;
  background: linear-gradient(135deg, #3D2580 0%, #2A1260 40%, #4E1FA0 100%) !important;
  border-color: rgba(180,100,255,0.65) !important;
  box-shadow:
    0 0 0 3px rgba(140,60,220,0.22),
    0 8px 48px rgba(120,40,200,0.60),
    0 2px 0 rgba(200,140,255,0.25) inset,
    0 -1px 0 rgba(30,5,60,0.70) inset !important;
}
.gemini-bar [data-testid="stForm"]>div:first-child{padding:0!important;}
.gemini-bar [data-testid="stHorizontalBlock"]{align-items:center!important;gap:2px!important;}
.gemini-bar [data-testid="stTextInput"] label{display:none!important;}
.gemini-bar [data-testid="stTextInput"]>div{background:transparent!important;border:none!important;box-shadow:none!important;padding:0!important;}
/* Text input area — bright purple (screenshot 3 color) */
.gemini-bar [data-testid="stTextInput"] input{
  background: rgba(140,50,220,0.22) !important;
  border: none !important;
  border-radius: 18px !important;
  outline: none !important;
  box-shadow:
    inset 0 2px 8px rgba(50,10,100,0.40),
    inset 0 -1px 0 rgba(200,150,255,0.12) !important;
  color: #EDE0FF !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 0.97rem !important;
  caret-color: #D4AAFF !important;
  padding: 11px 12px !important;
  height: 44px !important;
  width: 100% !important;
  transition: background 0.2s, box-shadow 0.2s !important;
}
.gemini-bar [data-testid="stTextInput"] input:focus {
  background: rgba(160,70,240,0.28) !important;
  box-shadow:
    inset 0 2px 10px rgba(60,10,120,0.50),
    inset 0 -1px 0 rgba(210,160,255,0.16),
    0 0 0 1.5px rgba(180,110,255,0.30) !important;
  outline: none !important;
  border: none !important;
}
/* Animated placeholder shimmer */
@keyframes placeholderShimmer {
  0%,100% { opacity: 0.45; }
  50%      { opacity: 0.75; }
}
.gemini-bar [data-testid="stTextInput"] input::placeholder {
  color: rgba(210,170,255,0.55) !important;
  animation: placeholderShimmer 3s ease-in-out infinite !important;
}
.gemini-bar>.stHorizontalBlock,.gemini-bar>[data-testid="stHorizontalBlock"]{align-items:stretch!important;gap:0!important;}
.gemini-attach .stButton>button{background:transparent!important;border:none!important;border-radius:50%!important;color:rgba(148,163,184,0.55)!important;font-size:1.2rem!important;width:42px!important;height:42px!important;min-width:42px!important;padding:0!important;box-shadow:none!important;}
.gemini-attach .stButton>button:hover{background:rgba(255,255,255,0.08)!important;color:rgba(186,230,253,0.80)!important;transform:none!important;opacity:1!important;}
.gemini-mic .stButton>button{background:rgba(255,255,255,0.05)!important;border:1px solid rgba(255,255,255,0.09)!important;border-radius:50%!important;color:rgba(148,163,184,0.60)!important;font-size:1.05rem!important;width:38px!important;height:38px!important;min-width:38px!important;padding:0!important;box-shadow:none!important;}
.gemini-mic-active .stButton>button{background:rgba(239,68,68,0.18)!important;border:1px solid rgba(239,68,68,0.45)!important;border-radius:50%!important;color:#FCA5A5!important;font-size:1.05rem!important;width:38px!important;height:38px!important;min-width:38px!important;padding:0!important;animation:micPulse 1.1s ease-in-out infinite!important;}
@keyframes micPulse{0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,0.40);}50%{box-shadow:0 0 0 7px rgba(239,68,68,0.00);}}
.gemini-send [data-testid="stFormSubmitButton"]>button{background:linear-gradient(135deg,#2563EB,#4F46E5)!important;border:none!important;border-radius:50%!important;color:#fff!important;font-size:1.25rem!important;font-weight:700!important;width:38px!important;height:38px!important;min-width:38px!important;padding:0!important;line-height:1!important;box-shadow:0 3px 14px rgba(37,99,235,0.38)!important;transition:opacity 0.16s,transform 0.14s!important;}
.gemini-send [data-testid="stFormSubmitButton"]>button:hover{opacity:0.88!important;transform:scale(1.07)!important;}
.file-chip{display:inline-flex;align-items:center;gap:5px;background:rgba(59,130,246,0.15);border:1px solid rgba(59,130,246,0.35);border-radius:20px;padding:3px 10px 3px 8px;font-size:0.72rem;color:#BAE6FD;font-weight:600;max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-left:4px;flex-shrink:0;}
.gemini-bar-anchored{position:fixed;bottom:0;left:0;right:0;z-index:900;background:rgba(20,8,50,0.97);backdrop-filter:blur(24px) saturate(160%);border-top:1px solid rgba(140,60,220,0.22);padding:10px max(16px,calc((100% - 680px)/2)) 12px;}
.listening-banner{display:flex;align-items:center;gap:8px;margin:10px auto 0;padding:8px 18px;background:rgba(239,68,68,0.09);border:1px solid rgba(239,68,68,0.22);border-radius:10px;font-size:0.80rem;color:#FCA5A5;max-width:800px;}
.listening-dot{width:7px;height:7px;border-radius:50%;background:#EF4444;animation:blinkDot 1.1s ease infinite;flex-shrink:0;}
@keyframes blinkDot{0%,100%{opacity:1;}50%{opacity:0.25;}}
.attach-panel{max-width:800px;margin:10px auto 4px;padding:14px 16px;background:rgba(59,130,246,0.05);border:1px dashed rgba(59,130,246,0.28);border-radius:14px;}

/* ── Global buttons ── */
.stButton>button{background:linear-gradient(135deg,#2563EB,#4F46E5)!important;color:#fff!important;border:none!important;border-radius:9px!important;font-family:'Outfit',sans-serif!important;font-weight:600!important;font-size:0.82rem!important;padding:9px 16px!important;box-shadow:0 3px 14px rgba(37,99,235,0.20)!important;transition:all 0.16s ease!important;}
.stButton>button:hover{opacity:.88!important;transform:translateY(-1px)!important;}
.sug-pill .stButton>button{background:rgba(255,255,255,0.04)!important;border:1px solid rgba(255,255,255,0.10)!important;border-radius:999px!important;color:rgba(186,230,253,0.74)!important;font-size:0.79rem!important;font-weight:500!important;padding:9px 18px!important;box-shadow:none!important;}
.sug-pill .stButton>button:hover{background:rgba(59,130,246,0.14)!important;border-color:rgba(59,130,246,0.34)!important;color:#BAE6FD!important;transform:translateY(-2px)!important;}
.ghost-btn .stButton>button{background:rgba(255,255,255,.05)!important;border:1px solid rgba(255,255,255,0.14)!important;color:rgba(226,232,240,.55)!important;box-shadow:none!important;}
.ghost-btn .stButton>button:hover{background:rgba(59,130,246,.10)!important;color:#E2E8F0!important;}
.present-btn .stButton>button{background:linear-gradient(135deg,#065F46,#10B981)!important;box-shadow:0 2px 10px rgba(16,185,129,.18)!important;padding:6px 11px!important;font-size:0.75rem!important;border-radius:7px!important;}
.absent-btn .stButton>button{background:linear-gradient(135deg,#7F1D1D,#EF4444)!important;box-shadow:0 2px 10px rgba(239,68,68,.16)!important;padding:6px 11px!important;font-size:0.75rem!important;border-radius:7px!important;}
.save-btn .stButton>button{background:linear-gradient(135deg,#92400E,#F59E0B)!important;box-shadow:0 2px 10px rgba(245,158,11,.18)!important;padding:7px 13px!important;font-size:0.77rem!important;}
.pin-btn .stButton>button{background:rgba(245,158,11,0.10)!important;border:1px solid rgba(245,158,11,0.28)!important;color:#FCD34D!important;box-shadow:none!important;font-size:0.70rem!important;padding:4px 10px!important;border-radius:7px!important;}
.del-btn .stButton>button{background:rgba(239,68,68,0.07)!important;border:1px solid rgba(239,68,68,0.18)!important;color:rgba(252,165,165,0.70)!important;box-shadow:none!important;font-size:0.68rem!important;padding:3px 8px!important;border-radius:6px!important;}
.ql-btn .stButton>button{background:rgba(255,255,255,.03)!important;border:1px solid rgba(255,255,255,0.14)!important;color:rgba(186,230,253,.65)!important;box-shadow:none!important;text-align:left!important;justify-content:flex-start!important;font-size:0.80rem!important;padding:9px 14px!important;border-radius:9px!important;}
.logout-btn .stButton>button{background:rgba(239,68,68,.09)!important;border:1px solid rgba(239,68,68,.20)!important;color:#FCA5A5!important;box-shadow:none!important;font-size:0.80rem!important;}
.open-chat-btn .stButton>button{background:linear-gradient(135deg,#059669,#10B981)!important;border-radius:12px!important;font-weight:700!important;font-size:0.88rem!important;padding:11px 22px!important;box-shadow:0 5px 24px rgba(16,185,129,.36)!important;font-family:'DM Mono',monospace!important;}
.settings-menu-btn .stButton>button{background:rgba(255,255,255,0.06)!important;border:1px solid rgba(255,255,255,0.12)!important;color:rgba(226,232,240,0.75)!important;box-shadow:none!important;font-size:0.82rem!important;font-weight:600!important;padding:8px 16px!important;border-radius:10px!important;}
.nav-btn .stButton>button{background:transparent!important;color:rgba(148,163,184,.65)!important;border:none!important;box-shadow:none!important;text-align:left!important;justify-content:flex-start!important;padding:10px 14px!important;font-size:0.83rem!important;font-weight:500!important;border-radius:8px!important;}
.nav-btn .stButton>button:hover{background:rgba(59,130,246,.10)!important;color:#BAE6FD!important;transform:none!important;}
.nav-btn-active .stButton>button{background:rgba(59,130,246,.14)!important;color:#60A5FA!important;border-left:2px solid #3B82F6!important;font-weight:700!important;box-shadow:none!important;}

/* ── Inputs ── */
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{background:rgba(255,255,255,0.04)!important;border:1px solid rgba(255,255,255,0.14)!important;border-radius:10px!important;color:#E2E8F0!important;font-family:'Outfit',sans-serif!important;font-size:0.87rem!important;}
[data-testid="stTextInput"] input:focus,[data-testid="stTextArea"] textarea:focus{border-color:rgba(59,130,246,0.55)!important;box-shadow:0 0 0 2.5px rgba(59,130,246,0.13)!important;}
[data-testid="stTextInput"] label,[data-testid="stTextArea"] label{color:rgba(148,163,184,0.55)!important;font-size:0.70rem!important;font-weight:600!important;text-transform:uppercase!important;letter-spacing:0.6px!important;}
[data-testid="stSelectbox"]>div>div{background:rgba(255,255,255,0.04)!important;border:1px solid rgba(255,255,255,0.14)!important;border-radius:10px!important;color:#E2E8F0!important;}
[data-testid="stSelectbox"] label{color:rgba(148,163,184,0.55)!important;font-size:0.70rem!important;font-weight:600!important;text-transform:uppercase!important;}
[data-testid="stFileUploader"]{background:rgba(59,130,246,0.04)!important;border:1px dashed rgba(59,130,246,0.26)!important;border-radius:12px!important;}
[data-testid="stToggle"] label{color:#E2E8F0!important;font-size:0.86rem!important;}
[data-testid="stExpander"]{background:rgba(255,255,255,.018)!important;border:1px solid rgba(255,255,255,0.08)!important;border-radius:12px!important;}
[data-testid="stProgress"]>div>div{border-radius:99px!important;background:linear-gradient(90deg,#2563EB,#22D3EE)!important;}
[data-testid="stProgress"]>div{background:rgba(255,255,255,.07)!important;border-radius:99px!important;height:5px!important;}
h1,h2,h3,h4{font-family:'DM Mono',monospace!important;font-weight:500!important;}
[data-testid="stMarkdown"] p,[data-testid="stMarkdown"] li{color:rgba(226,232,240,.72)!important;font-family:'Outfit',sans-serif!important;}
hr{border-color:rgba(255,255,255,0.08)!important;}
::-webkit-scrollbar{width:4px;height:4px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:rgba(59,130,246,.22);border-radius:4px;}
[data-testid="column"]{padding:0 4px!important;}

/* ── Animations ── */
@keyframes fadeUp{from{opacity:0;transform:translateY(18px);}to{opacity:1;transform:translateY(0);}}
@keyframes slideUp{from{opacity:0;transform:translateY(24px);}to{opacity:1;transform:translateY(0);}}
@keyframes fadeInUp{from{opacity:0;transform:translateY(-6px);}to{opacity:1;transform:translateY(0);}}
.chat-scroll-area{padding-bottom:140px;}
</style>
""", unsafe_allow_html=True)

st.markdown(f"<style>{get_theme_css()}</style>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FILE PICKER
# ─────────────────────────────────────────────────────────────────────────────
def render_native_file_picker(picker_id: str):
    qp = st.query_params
    fname = qp.get(f"fp_{picker_id}", "")
    components.html(f"""
<div id="picker-{picker_id}" style="display:none;">
  <input type="file" id="fileinput-{picker_id}"
    accept=".pdf,.txt,.png,.jpg,.jpeg,.docx,.csv,.mp4,.zip"
    style="position:absolute;width:1px;height:1px;opacity:0;pointer-events:none;"
    onchange="handleFileChange_{picker_id}(this)">
</div>
<script>
window.triggerFilePicker_{picker_id} = function() {{ document.getElementById('fileinput-{picker_id}').click(); }};
function handleFileChange_{picker_id}(input) {{
  if (!input.files || !input.files[0]) return;
  var fname = input.files[0].name;
  var url = new URL(window.parent.location.href);
  url.searchParams.set('fp_{picker_id}', fname);
  window.parent.history.replaceState(null,'',url.toString());
  setTimeout(function(){{ window.parent.location.href = url.toString(); }}, 100);
}}
</script>
""", height=0, scrolling=False)
    return fname


# ─────────────────────────────────────────────────────────────────────────────
# VOICE RECORDER
# ─────────────────────────────────────────────────────────────────────────────
def render_voice_recorder(recorder_id: str):
    qp = st.query_params
    voice_done = qp.get(f"vr_{recorder_id}", "")
    components.html(f"""
<div id="recorder-{recorder_id}" style="display:none;"></div>
<script>
(function(){{
  var mediaRecorder=null,audioChunks=[],isRecording=false;
  window.addEventListener('message',function(evt){{
    var d=evt.data; if(!d||!d.type) return;
    if(d.type==='startRecording_{recorder_id}') startRec();
    else if(d.type==='stopRecording_{recorder_id}') stopRec();
  }});
  function startRec(){{
    if(isRecording) return;
    navigator.mediaDevices.getUserMedia({{audio:true}}).then(function(stream){{
      audioChunks=[];
      try{{mediaRecorder=new MediaRecorder(stream,{{mimeType:'audio/webm'}});}}
      catch(e){{mediaRecorder=new MediaRecorder(stream);}}
      mediaRecorder.ondataavailable=function(e){{if(e.data&&e.data.size>0) audioChunks.push(e.data);}};
      mediaRecorder.onstop=function(){{
        var blob=new Blob(audioChunks,{{type:'audio/webm'}});
        var reader=new FileReader();
        reader.onloadend=function(){{
          var url=new URL(window.parent.location.href);
          url.searchParams.set('vr_{recorder_id}','DONE');
          url.searchParams.set('vr_{recorder_id}_ts',Date.now().toString());
          window.parent.history.replaceState(null,'',url.toString());
          setTimeout(function(){{window.parent.location.href=url.toString();}},80);
        }};
        reader.readAsDataURL(blob);
        stream.getTracks().forEach(function(t){{t.stop();}});
        isRecording=false;
      }};
      mediaRecorder.start(200); isRecording=true;
    }}).catch(function(err){{window.parent.postMessage({{type:'micError_{recorder_id}',error:err.message}},'*');}});
  }}
  function stopRec(){{
    if(mediaRecorder&&mediaRecorder.state!=='inactive') mediaRecorder.stop();
    isRecording=false;
  }}
  window.startRecording_{recorder_id}=startRec;
  window.stopRecording_{recorder_id}=stopRec;
}})();
</script>
""", height=0, scrolling=False)
    return voice_done if voice_done == "DONE" else None


# ─────────────────────────────────────────────────────────────────────────────
# GEMINI INPUT BAR  (Enter = Send only, 📎 and 🎤 outside form)
# ─────────────────────────────────────────────────────────────────────────────
def render_gemini_bar(bar_key: str, hero_mode: bool = True):
    recording  = st.session_state.is_recording
    mic_class  = "gemini-mic-active" if recording else "gemini-mic"
    mic_icon   = "⏹" if recording else "🎤"
    anim_style = "animation:slideUp 0.35s cubic-bezier(0.22,0.61,0.36,1) both;" if hero_mode else ""

    chip_html = ""
    if st.session_state.attached_file_name:
        fname = st.session_state.attached_file_name
        short = fname if len(fname) <= 18 else fname[:15] + "..."
        chip_html = (f'<div class="file-chip" title="{fname}"><span>📎</span>{short}'
                     f'<button onclick="clearChip_{bar_key}()" style="background:none;border:none;color:rgba(148,163,184,0.5);cursor:pointer;font-size:0.75rem;margin-left:4px;padding:0 4px;">✕</button></div>')

    st.markdown(f'<div class="gemini-bar" style="max-width:580px;width:100%;margin:0 auto;{anim_style}">', unsafe_allow_html=True)
    if chip_html:
        st.markdown(f'<div style="display:flex;align-items:center;padding:0 16px 6px;">{chip_html}</div>', unsafe_allow_html=True)

    # attach (outside form) | [form: input + send] | mic (outside form)
    oc = st.columns([0.55, 10, 0.65])
    with oc[0]:
        st.markdown('<div class="gemini-attach">', unsafe_allow_html=True)
        attach_clicked = st.button("📎", key=f"attach_{bar_key}", help="Attach file")
        st.markdown('</div>', unsafe_allow_html=True)
    with oc[1]:
        with st.form(key=f"gemini_form_{bar_key}", clear_on_submit=True):
            fi, fs = st.columns([12, 0.75])
            with fi:
                placeholder = "Ask AskMNIT..." if not st.session_state.attached_file_name else "Add a message about the file..."
                user_text = st.text_input("__gi__", placeholder=placeholder, key=f"gi_text_{bar_key}", label_visibility="collapsed")
            with fs:
                st.markdown('<div class="gemini-send">', unsafe_allow_html=True)
                send_clicked = st.form_submit_button("↑", help="Send")
                st.markdown('</div>', unsafe_allow_html=True)
    with oc[2]:
        st.markdown(f'<div class="{mic_class}">', unsafe_allow_html=True)
        mic_clicked = st.button(mic_icon, key=f"mic_{bar_key}", help="Voice input")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""<script>
    function clearChip_{bar_key}() {{
      var url=new URL(window.location.href);
      url.searchParams.delete('fp_{bar_key}');
      window.location.href=url.toString();
    }}
    </script>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if mic_clicked:    return ("mic", "stop" if recording else "start")
    if attach_clicked: return ("attach",)
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
# VIEW ROUTER
# ═════════════════════════════════════════════════════════════════════════════
view = st.session_state.view

###############################################################################
# CHAT VIEW
###############################################################################
if view == "chat":

    # ── HIDE SIDEBAR + suppress all sidebar-related layout space ─────────
    st.markdown("""
    <style>
    [data-testid="stSidebar"]{display:none!important;}
    [data-testid="stSidebarCollapseButton"]{display:none!important;}
    [data-testid="collapsedControl"]{display:none!important;}
    section[data-testid="stMain"]{margin-left:0!important;padding-left:0!important;}
    </style>
    """, unsafe_allow_html=True)

    has_messages = len(st.session_state.chat_messages) > 0

    # ── Voice done ────────────────────────────────────────────────────────
    for rkey in ["hero", "anchored"]:
        vdone = st.query_params.get(f"vr_{rkey}", "")
        if vdone == "DONE" and not st.session_state.get("_voice_submit"):
            st.session_state._voice_submit    = True
            st.session_state.is_recording     = False
            st.session_state.voice_transcript = "[Voice message recorded]"
            try: del st.query_params[f"vr_{rkey}"]
            except: pass

    if st.session_state._voice_submit:
        st.session_state._voice_submit = False
        msg = st.session_state.voice_transcript or "[Voice message]"
        st.session_state.voice_transcript = ""
        dispatch_message(f"🎤 {msg}")
        st.toast("Voice message sent!", icon="🎤")
        st.rerun()

    # ── File picker result ────────────────────────────────────────────────
    for rkey in ["hero", "anchored"]:
        fpname = st.query_params.get(f"fp_{rkey}", "")
        if fpname and fpname != st.session_state.attached_file_name:
            st.session_state.attached_file_name = fpname
            st.toast(f"📎 {fpname} selected!", icon="✅")
            try: del st.query_params[f"fp_{rkey}"]
            except: pass
            st.rerun()

    # ── FIXED NAVBAR: logo HTML + real Streamlit buttons (position:fixed) ─
    st.markdown("""
    <div class="chat-topbar">
      <div class="chat-topbar-logo">
        <div class="chat-topbar-logo-icon">A</div>
        <span style="font-family:'DM Mono',monospace;font-size:0.88rem;color:#E2E8F0;font-weight:500;">AskMNIT</span>
        <span style="font-size:0.50rem;color:#10B981;font-weight:700;margin-left:3px;">&#9679; AI</span>
      </div>
    </div>
    <div class="chat-topbar-spacer"></div>
    <div class="chat-topbar-divider"></div>
    """, unsafe_allow_html=True)

    # Vertical left-side nav — 4 buttons stacked, each in own row
    st.markdown('<div class="nb-real">', unsafe_allow_html=True)

    _hcls = "nb-on" if st.session_state.get("show_history_panel") else ""
    st.markdown(f'<div class="{_hcls}">', unsafe_allow_html=True)
    if st.button("🕐 History", key="_btn_history"):
        st.session_state.show_history_panel = not st.session_state.get("show_history_panel", False)
        st.session_state.show_settings_panel = False; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="nb-new">', unsafe_allow_html=True)
    if st.button("+ New Chat", key="_btn_new_chat"):
        if st.session_state.chat_messages:
            fu = next((m["content"][:38] for m in st.session_state.chat_messages if m["role"]=="user"), "Session")
            st.session_state.chat_sessions.append({"label": fu+"...", "messages": list(st.session_state.chat_messages)})
        st.session_state.chat_messages = []
        st.session_state.show_uploader = False
        st.session_state.attached_file_name = ""
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    _scls = "nb-on" if st.session_state.get("show_settings_panel") else ""
    st.markdown(f'<div class="{_scls}">', unsafe_allow_html=True)
    if st.button("⚙ Settings", key="_btn_settings"):
        st.session_state.show_settings_panel = not st.session_state.get("show_settings_panel", False)
        st.session_state.show_history_panel = False; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Dashboard", key="_btn_dashboard"):
        st.session_state.view = "dashboard"; st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Rotating animated placeholder injection ───────────────────────────
    st.markdown("""
    <style>
    @keyframes fadeInUp2 {
      from { opacity:0; transform:translateY(3px); }
      to   { opacity:1; transform:translateY(0); }
    }
    </style>
    <script>
    (function() {
      var hints = [
        "Ask AskMNIT anything...",
        "Check my attendance %...",
        "What's my next class?",
        "Find PYQs for my branch...",
        "Give me an exam strategy...",
        "Is my fee paid?",
        "Subjects this semester?",
      ];
      var idx = 0;
      function rotatePlaceholder() {
        var inputs = window.parent.document.querySelectorAll('.gemini-bar input[type="text"]');
        inputs.forEach(function(inp) {
          if (document.activeElement === inp) return;
          inp.setAttribute('placeholder', hints[idx]);
          inp.style.transition = 'opacity 0.35s';
          inp.style.opacity = '0';
          setTimeout(function(){ inp.style.opacity = '1'; }, 50);
        });
        idx = (idx + 1) % hints.length;
      }
      setInterval(rotatePlaceholder, 2800);
    })();
    </script>
    """, unsafe_allow_html=True)

    # ── HISTORY PANEL ─────────────────────────────────────────────────────
    if st.session_state.get("show_history_panel"):
        all_sessions = st.session_state.chat_sessions
        st.markdown('<div style="max-width:600px;margin:0 auto 12px;">', unsafe_allow_html=True)
        with st.expander("🕐 Chat History", expanded=True):
            if not all_sessions:
                st.markdown('<div style="text-align:center;padding:28px 0;font-size:0.82rem;color:rgba(148,163,184,0.40);">No saved chats yet. Start a conversation!</div>', unsafe_allow_html=True)
            else:
                _pinned   = [(i,s) for i,s in enumerate(all_sessions) if s.get("pinned")]
                _unpinned = [(i,s) for i,s in enumerate(all_sessions) if not s.get("pinned")]
                for _grp_label, _grp in [("📌 Pinned", _pinned), ("Recent", _unpinned)]:
                    if not _grp: continue
                    st.markdown(f'<div style="font-size:0.60rem;color:rgba(148,163,184,0.40);text-transform:uppercase;letter-spacing:1px;padding:4px 0 6px;">{_grp_label}</div>', unsafe_allow_html=True)
                    for _i, _sess in reversed(_grp):
                        _label     = _sess.get("label","Chat")[:50]
                        _is_pinned = _sess.get("pinned", False)
                        _c1, _c2, _c3, _c4 = st.columns([5, 0.9, 0.9, 0.9])
                        with _c1:
                            st.markdown(
                                f'<div style="background:rgba(255,255,255,0.03);border:1px solid '
                                f'{"rgba(245,158,11,0.25)" if _is_pinned else "rgba(255,255,255,0.07)"};'
                                f'border-radius:10px;padding:10px 14px;font-size:0.82rem;'
                                f'color:rgba(226,232,240,0.80);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'
                                f'{"📌 " if _is_pinned else ""}{_label}</div>', unsafe_allow_html=True)
                        with _c2:
                            if st.button("↩", key=f"_load_{_i}", help="Load chat"):
                                st.session_state.chat_messages = list(_sess["messages"])
                                st.session_state.show_history_panel = False; st.rerun()
                        with _c3:
                            if st.button("📌" if not _is_pinned else "📍", key=f"_pin_{_i}", help="Pin/Unpin"):
                                st.session_state.chat_sessions[_i]["pinned"] = not _is_pinned; st.rerun()
                        with _c4:
                            if st.button("🗑", key=f"_del_{_i}", help="Delete"):
                                st.session_state.chat_sessions.pop(_i); st.rerun()
                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                if st.button("🗑 Clear All History", key="_clear_hist"):
                    st.session_state.chat_sessions = []
                    st.toast("History cleared!", icon="🗑"); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── SETTINGS PANEL ────────────────────────────────────────────────────
    if st.session_state.get("show_settings_panel"):
        st.markdown('<div style="max-width:540px;margin:0 auto 12px;">', unsafe_allow_html=True)
        with st.expander("⚙ Chatbot Settings", expanded=True):
            st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:0.58rem;color:rgba(148,163,184,0.40);text-transform:uppercase;letter-spacing:1.2px;margin-bottom:14px;">Customize AskMNIT</div>', unsafe_allow_html=True)

            # Theme
            _ts1, _ts2 = st.columns([2, 3])
            with _ts1:
                st.markdown('<div style="font-size:0.84rem;color:rgba(226,232,240,0.80);font-weight:500;padding-top:6px;">🎨 Interface Theme</div><div style="font-size:0.68rem;color:rgba(148,163,184,0.42);margin-top:2px;">Dark or light mode</div>', unsafe_allow_html=True)
            with _ts2:
                _t1, _t2 = st.columns(2)
                with _t1:
                    if st.button("🌙 Dark", key="_theme_dark", use_container_width=True):
                        st.session_state.chat_theme = "dark"; st.rerun()
                with _t2:
                    if st.button("☀️ Light", key="_theme_light", use_container_width=True):
                        st.session_state.chat_theme = "light"; st.rerun()
            st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:10px 0;'>", unsafe_allow_html=True)

            # Response style
            _rs1, _rs2 = st.columns([2, 3])
            with _rs1:
                st.markdown('<div style="font-size:0.84rem;color:rgba(226,232,240,0.80);font-weight:500;padding-top:6px;">💬 Response Style</div><div style="font-size:0.68rem;color:rgba(148,163,184,0.42);margin-top:2px;">How AI replies</div>', unsafe_allow_html=True)
            with _rs2:
                _new_style = st.selectbox("", ["Concise","Detailed","Bullet Points"],
                    index=["Concise","Detailed","Bullet Points"].index(st.session_state.get("response_style","Concise")),
                    key="_sets_style", label_visibility="collapsed")
                if _new_style != st.session_state.response_style:
                    st.session_state.response_style = _new_style; st.rerun()
            st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:10px 0;'>", unsafe_allow_html=True)

            # Toggles
            _tog1, _tog2 = st.columns(2)
            with _tog1:
                st.session_state.voice_output = st.toggle("🔊 Voice Output", value=st.session_state.voice_output, key="_sets_voice")
            with _tog2:
                st.session_state.strict_mode  = st.toggle("🎓 Strict Mode",  value=st.session_state.strict_mode,  key="_sets_strict")
            st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:10px 0;'>", unsafe_allow_html=True)

            # Clear chats
            _cl1, _cl2 = st.columns([3,1])
            with _cl1:
                st.markdown('<div style="font-size:0.84rem;color:rgba(226,232,240,0.80);font-weight:500;padding-top:6px;">🗑 Clear All Chats</div>', unsafe_allow_html=True)
            with _cl2:
                if st.button("Clear", key="_sets_clear"):
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
            attached_file = st.file_uploader("Attach a file", type=["pdf","txt","png","jpg","jpeg","docx","csv"], key="file_uploader_chat")
        with up_c2:
            st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("Close", key="close_uploader"):
                st.session_state.show_uploader = False; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        if attached_file is not None:
            st.session_state.attached_file_name = attached_file.name
            st.session_state.show_uploader = False
            st.toast(f"📎 {attached_file.name} selected!", icon="✅"); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────
    # HERO STATE (no messages yet)
    # ─────────────────────────────────────────────────────────────────────
    if not has_messages:
        st.markdown("<div style='height:4vh'></div>", unsafe_allow_html=True)

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

        # Pills — centered with equal margins, no sidebar offset
        _, pc, _ = st.columns([0.8, 8.4, 0.8])
        with pc:
            r1 = st.columns(4)
            for i, pill in enumerate(PILLS_ROW1):
                with r1[i]:
                    st.markdown('<div class="sug-pill">', unsafe_allow_html=True)
                    if st.button(pill, key=f"pill_r1_{i}", use_container_width=True):
                        dispatch_message(pill); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            _, r2c1, r2c2, _ = st.columns([1.5, 2, 2, 1.5])
            for i, (pill, col) in enumerate(zip(PILLS_ROW2, [r2c1, r2c2])):
                with col:
                    st.markdown('<div class="sug-pill">', unsafe_allow_html=True)
                    if st.button(pill, key=f"pill_r2_{i}", use_container_width=True):
                        dispatch_message(pill); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:3vh'></div>", unsafe_allow_html=True)

        # Input bar — narrower, premium centered
        _, bc, _ = st.columns([1.5, 7, 1.5])
        with bc:
            hero_action = render_gemini_bar(bar_key="hero", hero_mode=True)

        render_voice_recorder("hero")
        render_native_file_picker("hero")

        if st.session_state.is_recording:
            st.markdown('<div class="listening-banner"><div class="listening-dot"></div><span>Listening... press ⏹ to stop</span></div>', unsafe_allow_html=True)

        st.markdown('<p style="text-align:center;font-size:0.59rem;color:rgba(100,116,139,0.38);margin-top:10px;font-family:\'DM Mono\',monospace;">AskMNIT AI can make mistakes &nbsp;·&nbsp; Verify with official ERP or faculty</p>', unsafe_allow_html=True)

        if hero_action:
            act = hero_action[0]
            if act == "send":
                dispatch_message(hero_action[1])
                st.session_state.attached_file_name = ""; st.rerun()
            elif act == "mic":
                if hero_action[1] == "start":
                    st.session_state.is_recording = True
                    st.toast("🎤 Recording started!", icon="🎤")
                else:
                    st.session_state.is_recording = False
                    st.toast("⏹ Processing voice...", icon="⏳")
                st.rerun()
            elif act == "attach":
                st.session_state.show_uploader = True; st.rerun()

    # ─────────────────────────────────────────────────────────────────────
    # ACTIVE CHAT STATE
    # ─────────────────────────────────────────────────────────────────────
    else:
        st.markdown("<div class='chat-scroll-area'>", unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        _, mc, _ = st.columns([0.5, 9, 0.5])
        with mc:
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="gemini-bar-anchored">', unsafe_allow_html=True)
        anchored_action = render_gemini_bar(bar_key="anchored", hero_mode=False)
        render_voice_recorder("anchored")
        render_native_file_picker("anchored")
        if st.session_state.is_recording:
            st.markdown('<div class="listening-banner" style="margin-top:8px;"><div class="listening-dot"></div><span>Listening... press ⏹ to stop</span></div>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center;font-size:0.59rem;color:rgba(100,116,139,0.38);margin-top:4px;font-family:\'DM Mono\',monospace;">AskMNIT AI can make mistakes &nbsp;·&nbsp; Verify with official ERP or faculty</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if anchored_action:
            act = anchored_action[0]
            if act == "send":
                dispatch_message(anchored_action[1])
                st.session_state.attached_file_name = ""; st.rerun()
            elif act == "mic":
                if anchored_action[1] == "start":
                    st.session_state.is_recording = True
                    st.toast("🎤 Recording started!", icon="🎤")
                else:
                    st.session_state.is_recording = False
                    st.toast("⏹ Processing voice...", icon="⏳")
                st.rerun()
            elif act == "attach":
                st.session_state.show_uploader = True; st.rerun()

    st.stop()


###############################################################################
# DASHBOARD VIEW
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
        '</div></div></div>', unsafe_allow_html=True)
    bh = branch_hex(st.session_state.branch)
    st.markdown(f'<div style="padding:8px 12px 4px;"><span style="font-size:0.60rem;font-weight:700;padding:2px 9px;background:rgba(255,255,255,0.05);border:1px solid {bh}44;border-radius:5px;color:{bh};letter-spacing:0.4px;">{st.session_state.branch}</span></div>', unsafe_allow_html=True)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    for label in NAV_LABELS:
        css = "nav-btn-active" if st.session_state.nav_page == label else "nav-btn"
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
    st.markdown(f'<div style="padding:24px;"><div style="font-family:\'DM Mono\',monospace;font-size:0.95rem;color:#E2E8F0;border-bottom:1px solid rgba(255,255,255,0.06);padding-bottom:14px;margin-bottom:24px;">{title.upper()}</div><div style="background:linear-gradient(160deg,#0B1120,#060A12);border:1px dashed rgba(59,130,246,0.18);border-radius:16px;padding:60px 40px;text-align:center;"><div style="font-family:\'DM Mono\',monospace;font-size:0.88rem;color:#E2E8F0;margin-bottom:8px;">{title.upper()}</div><div style="font-size:0.76rem;color:rgba(148,163,184,.44);max-width:280px;margin:0 auto;line-height:1.65;">{desc}</div></div></div>', unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# MY DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div style='padding:0 22px 80px;'>", unsafe_allow_html=True)

h_logo, h_mid, h_right = st.columns([2,4,3])
with h_logo:
    st.markdown('<div style="display:flex;align-items:center;gap:8px;padding:13px 0 9px;"><div style="width:30px;height:30px;border-radius:7px;background:linear-gradient(135deg,#2563EB,#4F46E5);display:flex;align-items:center;justify-content:center;font-size:0.85rem;font-weight:700;color:white;">M</div><div><div style="font-family:\'DM Mono\',monospace;font-size:0.76rem;color:#E2E8F0;">MNIT Jaipur</div><div style="font-size:0.52rem;color:rgba(148,163,184,.36);">[ MNIT LOGO ]</div></div></div>', unsafe_allow_html=True)
with h_mid:
    now_str = datetime.datetime.now().strftime("%a, %d %b %Y  ·  %H:%M")
    st.markdown(f'<div style="padding:13px 0 9px;text-align:center;"><span style="font-family:\'DM Mono\',monospace;font-size:0.76rem;color:#60A5FA;letter-spacing:0.8px;">MY DASHBOARD</span><br><span style="font-size:0.57rem;color:rgba(148,163,184,.38);">{now_str}</span></div>', unsafe_allow_html=True)
with h_right:
    nm,br,sem = st.session_state.student_name,st.session_state.branch,st.session_state.semester
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

def render_subj_rows(subj_list, section):
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
st.markdown(f'<div style="background:linear-gradient(160deg,#0B1120,#070D1C);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:18px 18px 14px;margin-bottom:14px;"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;"><span style="font-family:\'DM Mono\',monospace;font-size:0.56rem;color:rgba(148,163,184,.40);text-transform:uppercase;letter-spacing:1.4px;">// TODAY\'S CLASS SCHEDULE</span><span style="font-family:\'DM Mono\',monospace;font-size:0.62rem;color:rgba(96,165,250,.65);">{today_name.upper()}</span></div>', unsafe_allow_html=True)
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

st.markdown('<div style="text-align:center;margin-top:28px;padding:10px 0;border-top:1px solid rgba(255,255,255,0.05);"><span style="font-family:\'DM Mono\',monospace;font-size:0.52rem;color:rgba(148,163,184,0.24);letter-spacing:1.2px;">ASKMNT &nbsp;·&nbsp; MNIT JAIPUR &nbsp;·&nbsp; v6.0 CLEAN</span></div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
