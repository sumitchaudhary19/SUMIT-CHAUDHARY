# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  AskMNIT — v7.0 PREMIUM  (Dashboard untouched · New Chatbot UI)            ║
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
    "response_style":    "Concise",
    "attached_file_name":"",
    "voice_transcript":  "",
    "_voice_submit":     False,
    "show_history_panel":  False,
    "show_settings_panel": False,
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
    with st.spinner(""):
        reply = generate_ai_response(text)
    st.session_state.chat_messages.append({"role":"assistant","content":reply})

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS — DASHBOARD (UNCHANGED STYLES)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,700;9..144,900&family=DM+Mono:wght@400;500&family=Outfit:wght@300;400;500;600;700&display=swap');

*,html,body{box-sizing:border-box;margin:0;padding:0;}
html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"]{font-family:'Outfit',sans-serif!important;background:#070B14!important;color:#E2E8F0!important;}
header[data-testid="stHeader"],footer,#MainMenu,[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important;}
[data-testid="stMainBlockContainer"]{padding:0!important;max-width:100%!important;}

/* Dashboard sidebar */
[data-testid="stSidebar"]{background:#0B1120!important;border-right:1px solid rgba(59,130,246,0.16)!important;min-width:260px!important;max-width:260px!important;}
[data-testid="stSidebar"]>div{padding:0!important;}
.nav-btn .stButton>button{background:transparent!important;color:rgba(148,163,184,.65)!important;border:none!important;box-shadow:none!important;text-align:left!important;justify-content:flex-start!important;padding:10px 14px!important;font-size:0.83rem!important;font-weight:500!important;border-radius:8px!important;}
.nav-btn .stButton>button:hover{background:rgba(59,130,246,.10)!important;color:#BAE6FD!important;transform:none!important;}
.nav-btn-active .stButton>button{background:rgba(59,130,246,.14)!important;color:#60A5FA!important;border-left:2px solid #3B82F6!important;font-weight:700!important;box-shadow:none!important;}
.logout-btn .stButton>button{background:rgba(239,68,68,.09)!important;border:1px solid rgba(239,68,68,.20)!important;color:#FCA5A5!important;box-shadow:none!important;font-size:0.80rem!important;}

/* Global buttons */
.stButton>button{background:linear-gradient(135deg,#2563EB,#4F46E5)!important;color:#fff!important;border:none!important;border-radius:9px!important;font-family:'Outfit',sans-serif!important;font-weight:600!important;font-size:0.82rem!important;padding:9px 16px!important;box-shadow:0 3px 14px rgba(37,99,235,0.20)!important;transition:all 0.16s ease!important;}
.stButton>button:hover{opacity:.88!important;transform:translateY(-1px)!important;}
.ghost-btn .stButton>button{background:rgba(255,255,255,.05)!important;border:1px solid rgba(255,255,255,0.14)!important;color:rgba(226,232,240,.55)!important;box-shadow:none!important;}
.ghost-btn .stButton>button:hover{background:rgba(59,130,246,.10)!important;color:#E2E8F0!important;}
.present-btn .stButton>button{background:linear-gradient(135deg,#065F46,#10B981)!important;box-shadow:0 2px 10px rgba(16,185,129,.18)!important;padding:6px 11px!important;font-size:0.75rem!important;border-radius:7px!important;}
.absent-btn .stButton>button{background:linear-gradient(135deg,#7F1D1D,#EF4444)!important;box-shadow:0 2px 10px rgba(239,68,68,.16)!important;padding:6px 11px!important;font-size:0.75rem!important;border-radius:7px!important;}
.save-btn .stButton>button{background:linear-gradient(135deg,#92400E,#F59E0B)!important;box-shadow:0 2px 10px rgba(245,158,11,.18)!important;padding:7px 13px!important;font-size:0.77rem!important;}
.pin-btn .stButton>button{background:rgba(245,158,11,0.10)!important;border:1px solid rgba(245,158,11,0.28)!important;color:#FCD34D!important;box-shadow:none!important;font-size:0.70rem!important;padding:4px 10px!important;border-radius:7px!important;}
.del-btn .stButton>button{background:rgba(239,68,68,0.07)!important;border:1px solid rgba(239,68,68,0.18)!important;color:rgba(252,165,165,0.70)!important;box-shadow:none!important;font-size:0.68rem!important;padding:3px 8px!important;border-radius:6px!important;}
.ql-btn .stButton>button{background:rgba(255,255,255,.03)!important;border:1px solid rgba(255,255,255,0.14)!important;color:rgba(186,230,253,.65)!important;box-shadow:none!important;text-align:left!important;justify-content:flex-start!important;font-size:0.80rem!important;padding:9px 14px!important;border-radius:9px!important;}
.open-chat-btn .stButton>button{background:linear-gradient(135deg,#059669,#10B981)!important;border-radius:12px!important;font-weight:700!important;font-size:0.88rem!important;padding:11px 22px!important;box-shadow:0 5px 24px rgba(16,185,129,.36)!important;font-family:'DM Mono',monospace!important;}
.settings-menu-btn .stButton>button{background:rgba(255,255,255,0.06)!important;border:1px solid rgba(255,255,255,0.12)!important;color:rgba(226,232,240,0.75)!important;box-shadow:none!important;font-size:0.82rem!important;font-weight:600!important;padding:8px 16px!important;border-radius:10px!important;}

/* Inputs */
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
@keyframes fadeUp{from{opacity:0;transform:translateY(18px);}to{opacity:1;transform:translateY(0);}}
@keyframes slideUp{from{opacity:0;transform:translateY(24px);}to{opacity:1;transform:translateY(0);}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# VIEW ROUTER
# ─────────────────────────────────────────────────────────────────────────────
view = st.session_state.view

###############################################################################
# ██████████████████████  CHAT VIEW  ████████████████████████████████████████
###############################################################################
if view == "chat":

    # Hide sidebar entirely in chat
    st.markdown("""
    <style>
    [data-testid="stSidebar"]{display:none!important;}
    [data-testid="stSidebarCollapseButton"]{display:none!important;}
    [data-testid="collapsedControl"]{display:none!important;}
    section[data-testid="stMain"]{margin-left:0!important;padding-left:0!important;}
    [data-testid="stMainBlockContainer"]{padding:0!important;}
    </style>
    """, unsafe_allow_html=True)

    # ── PREMIUM CHAT CSS ──────────────────────────────────────────────────
    st.markdown("""
    <style>
    /* ═══ CHAT ROOT ═══════════════════════════════════════════════════════ */
    html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"]{
      background: #05070F !important;
      overflow-x: hidden !important;
    }

    /* ═══ ANIMATED MESH BACKGROUND ════════════════════════════════════════ */
    .chat-bg {
      position: fixed; inset: 0; z-index: 0; overflow: hidden; pointer-events: none;
    }
    .chat-bg::before {
      content: '';
      position: absolute; inset: 0;
      background:
        radial-gradient(ellipse 80% 60% at 20% 10%, rgba(79,46,220,0.22) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 80% 5%, rgba(6,182,212,0.14) 0%, transparent 55%),
        radial-gradient(ellipse 50% 40% at 50% 90%, rgba(124,58,237,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 40% 30% at 10% 80%, rgba(16,185,129,0.08) 0%, transparent 50%);
      animation: meshMove 18s ease-in-out infinite alternate;
    }
    .chat-bg::after {
      content: '';
      position: absolute; inset: 0;
      background-image:
        repeating-linear-gradient(0deg, transparent, transparent 60px, rgba(255,255,255,0.012) 60px, rgba(255,255,255,0.012) 61px),
        repeating-linear-gradient(90deg, transparent, transparent 60px, rgba(255,255,255,0.012) 60px, rgba(255,255,255,0.012) 61px);
    }
    @keyframes meshMove {
      0%   { opacity: 1; transform: scale(1) translate(0,0); }
      50%  { opacity: 0.8; transform: scale(1.08) translate(2%, 1%); }
      100% { opacity: 1; transform: scale(1.04) translate(-1%, 2%); }
    }

    /* ═══ FLOATING ORBS ════════════════════════════════════════════════════ */
    .orb {
      position: fixed; border-radius: 50%; filter: blur(80px);
      pointer-events: none; z-index: 0; animation: orbFloat 20s ease-in-out infinite;
    }
    .orb-1 { width:400px;height:400px; top:-100px; left:-120px; background:rgba(79,46,220,0.18); animation-delay:0s; }
    .orb-2 { width:300px;height:300px; top:20%; right:-80px; background:rgba(6,182,212,0.14); animation-delay:-7s; }
    .orb-3 { width:250px;height:250px; bottom:-60px; left:30%; background:rgba(124,58,237,0.16); animation-delay:-14s; }
    @keyframes orbFloat {
      0%,100% { transform: translate(0,0) scale(1); }
      33%  { transform: translate(30px,-20px) scale(1.05); }
      66%  { transform: translate(-20px,30px) scale(0.96); }
    }

    /* ═══ LEFT SIDEBAR ═════════════════════════════════════════════════════ */
    .chat-sidebar {
      position: fixed; top: 0; left: 0; bottom: 0; width: 268px; z-index: 1000;
      background: rgba(8,12,24,0.92);
      backdrop-filter: blur(28px) saturate(180%);
      -webkit-backdrop-filter: blur(28px) saturate(180%);
      border-right: 1px solid rgba(255,255,255,0.07);
      display: flex; flex-direction: column;
      padding: 0;
      box-shadow: 4px 0 40px rgba(0,0,0,0.5);
    }
    .sidebar-header {
      padding: 20px 20px 16px;
      border-bottom: 1px solid rgba(255,255,255,0.06);
      display: flex; align-items: center; gap: 11px;
    }
    .sidebar-logo-icon {
      width: 36px; height: 36px; border-radius: 10px;
      background: linear-gradient(135deg, #4F2EDC, #06B6D4);
      display: flex; align-items: center; justify-content: center;
      font-size: 1rem; font-weight: 800; color: #fff;
      box-shadow: 0 4px 16px rgba(79,46,220,0.40);
      flex-shrink: 0;
    }
    .sidebar-brand { font-family: 'DM Mono', monospace; font-size: 0.92rem; color: #E2E8F0; font-weight: 500; }
    .sidebar-tagline { font-size: 0.56rem; color: rgba(148,163,184,0.38); margin-top: 1px; }

    .sidebar-section { padding: 14px 14px 6px; }
    .sidebar-section-label {
      font-family: 'DM Mono', monospace; font-size: 0.52rem;
      color: rgba(148,163,184,0.32); text-transform: uppercase;
      letter-spacing: 1.6px; margin-bottom: 8px; padding-left: 6px;
    }

    .sidebar-btn {
      display: flex; align-items: center; gap: 10px;
      padding: 10px 14px; border-radius: 10px; cursor: pointer;
      font-size: 0.83rem; color: rgba(148,163,184,0.68);
      transition: all 0.18s ease; margin-bottom: 3px;
      border: 1px solid transparent;
      text-decoration: none; background: transparent;
      width: 100%;
    }
    .sidebar-btn:hover {
      background: rgba(79,46,220,0.10);
      color: #C4B5FD; border-color: rgba(124,58,237,0.22);
    }
    .sidebar-btn.active {
      background: rgba(79,46,220,0.16);
      color: #A78BFA; border-color: rgba(124,58,237,0.32);
      font-weight: 600;
    }
    .sidebar-btn-icon { font-size: 1rem; width: 20px; text-align: center; flex-shrink: 0; }

    .sidebar-divider { height:1px; background: rgba(255,255,255,0.05); margin: 8px 14px; }

    .sidebar-history-item {
      display: flex; align-items: center; gap: 8px;
      padding: 8px 14px; border-radius: 8px; cursor: pointer;
      font-size: 0.75rem; color: rgba(148,163,184,0.52);
      transition: all 0.15s; margin-bottom: 2px;
    }
    .sidebar-history-item:hover { background: rgba(255,255,255,0.04); color: rgba(226,232,240,0.72); }
    .sidebar-history-dot { width:5px;height:5px;border-radius:50%;background:rgba(124,58,237,0.6);flex-shrink:0; }
    .sidebar-history-text { overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1; }

    .sidebar-footer {
      margin-top: auto;
      padding: 14px;
      border-top: 1px solid rgba(255,255,255,0.05);
    }
    .sidebar-user {
      display: flex; align-items: center; gap: 10px;
      padding: 10px 12px; border-radius: 10px;
      background: rgba(255,255,255,0.04);
      border: 1px solid rgba(255,255,255,0.07);
    }
    .sidebar-user-avatar {
      width: 32px; height: 32px; border-radius: 8px;
      background: linear-gradient(135deg,#4F2EDC,#06B6D4);
      display: flex; align-items:center; justify-content:center;
      font-size: 0.75rem; font-weight: 700; color:#fff; flex-shrink:0;
    }
    .sidebar-user-name { font-size:0.78rem;color:#E2E8F0;font-weight:600; }
    .sidebar-user-branch { font-size:0.60rem;color:rgba(148,163,184,0.44); }

    /* ═══ MAIN CHAT AREA ════════════════════════════════════════════════════ */
    .chat-main {
      margin-left: 268px;
      min-height: 100vh;
      display: flex; flex-direction: column;
      position: relative; z-index: 1;
    }

    /* ═══ TOP NAV BAR ═══════════════════════════════════════════════════════ */
    .chat-topnav {
      position: fixed; top: 0; left: 268px; right: 0; z-index: 900;
      height: 56px; background: rgba(5,7,15,0.90);
      backdrop-filter: blur(20px) saturate(180%);
      -webkit-backdrop-filter: blur(20px) saturate(180%);
      border-bottom: 1px solid rgba(255,255,255,0.06);
      display: flex; align-items: center; justify-content: space-between;
      padding: 0 24px;
    }
    .topnav-left { display:flex;align-items:center;gap:12px; }
    .topnav-model-badge {
      display:inline-flex;align-items:center;gap:6px;
      padding:4px 12px;border-radius:999px;
      background:rgba(79,46,220,0.14);
      border:1px solid rgba(124,58,237,0.28);
      font-family:'DM Mono',monospace;font-size:0.62rem;
      color:#C4B5FD;font-weight:500;
    }
    .topnav-dot { width:6px;height:6px;border-radius:50%;background:#10B981;animation:topnavPulse 2s ease infinite; }
    @keyframes topnavPulse{0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(16,185,129,0.4);}50%{opacity:0.7;box-shadow:0 0 0 4px rgba(16,185,129,0);}}
    .topnav-right { display:flex;align-items:center;gap:8px; }
    .topnav-pill-btn {
      padding:5px 14px;border-radius:999px;font-size:0.72rem;font-weight:500;
      border:1px solid rgba(255,255,255,0.10);
      background:rgba(255,255,255,0.05);
      color:rgba(226,232,240,0.70);cursor:pointer;
      transition:all 0.15s;font-family:'Outfit',sans-serif;
    }
    .topnav-pill-btn:hover{background:rgba(79,46,220,0.16);border-color:rgba(124,58,237,0.35);color:#C4B5FD;}
    .topnav-icon-btn {
      width:32px;height:32px;border-radius:8px;display:flex;align-items:center;justify-content:center;
      background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.09);
      font-size:0.88rem;cursor:pointer;transition:all 0.15s;
    }
    .topnav-icon-btn:hover{background:rgba(79,46,220,0.16);border-color:rgba(124,58,237,0.30);}

    /* ═══ HERO SECTION (no messages) ════════════════════════════════════════ */
    .hero-wrap {
      display:flex;flex-direction:column;align-items:center;
      justify-content:center;min-height:100vh;
      padding:80px 24px 200px;
      animation:fadeUp 0.5s cubic-bezier(0.22,0.61,0.36,1) both;
    }
    .hero-orb-icon {
      width: 88px; height: 88px; border-radius: 26px;
      background: linear-gradient(135deg,#1E1060 0%,#4F2EDC 40%,#06B6D4 80%,#10B981 100%);
      display:flex;align-items:center;justify-content:center;font-size:2.5rem;
      box-shadow:0 0 0 1px rgba(124,58,237,0.30), 0 20px 60px rgba(79,46,220,0.40);
      margin-bottom:28px;
      animation: heroOrb 6s ease-in-out infinite;
    }
    @keyframes heroOrb {
      0%,100%{box-shadow:0 0 0 1px rgba(124,58,237,0.30),0 20px 60px rgba(79,46,220,0.40);}
      50%{box-shadow:0 0 0 1px rgba(6,182,212,0.40),0 20px 80px rgba(6,182,212,0.30),0 0 60px rgba(79,46,220,0.20);}
    }
    .hero-title {
      font-family:'Fraunces',serif;font-size:3.4rem;font-weight:900;
      color:#F1F5F9;letter-spacing:-2.5px;line-height:1.05;text-align:center;
      margin-bottom:12px;
    }
    .hero-title span{
      background:linear-gradient(90deg,#A78BFA,#38BDF8,#34D399);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
    }
    .hero-sub {
      font-size:0.88rem;color:rgba(148,163,184,0.50);text-align:center;
      line-height:1.80;margin-bottom:40px;max-width:420px;
    }

    /* ═══ SUGGESTION BUBBLES ════════════════════════════════════════════════ */
    .sug-wrap { display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-bottom:40px;max-width:680px; }
    .sug-bubble {
      padding:9px 18px;border-radius:999px;
      background:rgba(255,255,255,0.04);
      border:1px solid rgba(255,255,255,0.09);
      color:rgba(186,230,253,0.72);font-size:0.80rem;cursor:pointer;
      transition:all 0.20s ease;font-family:'Outfit',sans-serif;
      backdrop-filter:blur(8px);
    }
    .sug-bubble:hover{
      background:rgba(79,46,220,0.16);
      border-color:rgba(124,58,237,0.40);
      color:#C4B5FD;transform:translateY(-2px);
      box-shadow:0 8px 24px rgba(79,46,220,0.18);
    }

    /* ═══ INPUT BAR ═════════════════════════════════════════════════════════ */
    .input-bar-wrap {
      width:100%;max-width:720px;margin:0 auto;
    }
    /* Fixed anchored bar */
    .input-bar-fixed {
      position:fixed;bottom:0;left:268px;right:0;z-index:800;
      padding:16px 32px 20px;
      background:linear-gradient(to top, rgba(5,7,15,1) 60%, transparent);
    }
    .input-bar-inner {
      max-width:720px;margin:0 auto;
      background:rgba(14,18,35,0.92);
      border:1px solid rgba(255,255,255,0.11);
      border-radius:20px;
      padding:6px 6px 6px 18px;
      display:flex;align-items:center;gap:0;
      box-shadow:0 8px 48px rgba(0,0,0,0.60),0 0 0 1px rgba(79,46,220,0.12);
      backdrop-filter:blur(20px);
      transition:border-color 0.22s,box-shadow 0.22s;
    }
    .input-bar-inner:focus-within{
      border-color:rgba(124,58,237,0.50)!important;
      box-shadow:0 0 0 3px rgba(79,46,220,0.14),0 8px 48px rgba(0,0,0,0.60)!important;
    }
    /* Streamlit input inside bar */
    .chat-input-field [data-testid="stTextInput"] label{display:none!important;}
    .chat-input-field [data-testid="stTextInput"]>div{
      background:transparent!important;border:none!important;
      box-shadow:none!important;padding:0!important;
    }
    .chat-input-field [data-testid="stTextInput"] input{
      background:transparent!important;border:none!important;outline:none!important;
      box-shadow:none!important;color:#E2E8F0!important;
      font-family:'Outfit',sans-serif!important;font-size:0.97rem!important;
      caret-color:#A78BFA!important;padding:10px 4px!important;height:44px!important;
      border-radius:0!important;width:100%!important;
    }
    .chat-input-field [data-testid="stTextInput"] input:focus{border:none!important;box-shadow:none!important;}
    .chat-input-field [data-testid="stTextInput"] input::placeholder{
      color:rgba(148,163,184,0.35)!important;
    }
    /* Bar action buttons */
    .bar-attach-btn .stButton>button{
      background:transparent!important;border:none!important;border-radius:10px!important;
      color:rgba(148,163,184,0.50)!important;font-size:1.10rem!important;
      width:38px!important;height:38px!important;min-width:38px!important;
      padding:0!important;box-shadow:none!important;
    }
    .bar-attach-btn .stButton>button:hover{background:rgba(255,255,255,0.07)!important;color:#A78BFA!important;transform:none!important;}
    .bar-mic-btn .stButton>button{
      background:rgba(255,255,255,0.05)!important;border:1px solid rgba(255,255,255,0.09)!important;
      border-radius:50%!important;color:rgba(148,163,184,0.60)!important;font-size:1rem!important;
      width:36px!important;height:36px!important;min-width:36px!important;
      padding:0!important;box-shadow:none!important;
    }
    .bar-mic-btn .stButton>button:hover{background:rgba(79,46,220,0.18)!important;border-color:rgba(124,58,237,0.40)!important;color:#C4B5FD!important;transform:none!important;}
    .bar-mic-active .stButton>button{
      background:rgba(239,68,68,0.18)!important;border:1px solid rgba(239,68,68,0.45)!important;
      border-radius:50%!important;color:#FCA5A5!important;font-size:1rem!important;
      width:36px!important;height:36px!important;min-width:36px!important;
      padding:0!important;animation:micPulse 1.1s ease-in-out infinite!important;
    }
    @keyframes micPulse{0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,0.40);}50%{box-shadow:0 0 0 7px rgba(239,68,68,0.00);}}
    .bar-send-btn [data-testid="stFormSubmitButton"]>button{
      background:linear-gradient(135deg,#4F2EDC,#06B6D4)!important;border:none!important;
      border-radius:12px!important;color:#fff!important;font-size:1.15rem!important;font-weight:700!important;
      width:40px!important;height:40px!important;min-width:40px!important;
      padding:0!important;line-height:1!important;
      box-shadow:0 4px 16px rgba(79,46,220,0.45)!important;
      transition:opacity 0.16s,transform 0.14s!important;
    }
    .bar-send-btn [data-testid="stFormSubmitButton"]>button:hover{opacity:0.88!important;transform:scale(1.06)!important;}
    /* File chip */
    .file-chip{
      display:inline-flex;align-items:center;gap:5px;
      background:rgba(79,46,220,0.15);border:1px solid rgba(124,58,237,0.35);
      border-radius:20px;padding:3px 10px 3px 8px;font-size:0.72rem;
      color:#C4B5FD;font-weight:600;max-width:180px;overflow:hidden;
      text-overflow:ellipsis;white-space:nowrap;margin-right:6px;flex-shrink:0;
    }

    /* ═══ CHAT MESSAGES ═════════════════════════════════════════════════════ */
    .chat-messages-area {
      padding:72px 32px 160px;
      max-width:760px;margin:0 auto;width:100%;
    }
    [data-testid="stChatMessage"]{
      background:rgba(255,255,255,0.03)!important;
      border:1px solid rgba(255,255,255,0.07)!important;
      border-radius:16px!important;font-family:'Outfit',sans-serif!important;
      margin-bottom:10px!important;
      animation:msgFadeIn 0.3s ease both!important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]){
      background:rgba(79,46,220,0.07)!important;
      border-color:rgba(124,58,237,0.18)!important;
    }
    @keyframes msgFadeIn{from{opacity:0;transform:translateY(10px);}to{opacity:1;transform:translateY(0);}}

    /* ═══ RECORDING BANNER ══════════════════════════════════════════════════ */
    .rec-banner{
      display:flex;align-items:center;gap:8px;padding:8px 16px;
      background:rgba(239,68,68,0.09);border:1px solid rgba(239,68,68,0.22);
      border-radius:10px;font-size:0.78rem;color:#FCA5A5;
      margin-bottom:8px;max-width:720px;margin-left:auto;margin-right:auto;
    }
    .rec-dot{width:7px;height:7px;border-radius:50%;background:#EF4444;animation:blinkDot 1.1s ease infinite;flex-shrink:0;}
    @keyframes blinkDot{0%,100%{opacity:1;}50%{opacity:0.25;}}

    /* ═══ DISCLAIMER ════════════════════════════════════════════════════════ */
    .chat-disclaimer{
      text-align:center;font-family:'DM Mono',monospace;
      font-size:0.55rem;color:rgba(100,116,139,0.35);
      margin-top:6px;
    }

    /* ═══ HISTORY PANEL INSIDE SIDEBAR ══════════════════════════════════════ */
    .history-panel-inner{
      max-height:calc(100vh - 340px);overflow-y:auto;padding:0 4px;
    }
    .history-panel-inner::-webkit-scrollbar{width:3px;}
    .history-panel-inner::-webkit-scrollbar-thumb{background:rgba(124,58,237,0.25);border-radius:3px;}

    /* Stagger animation for suggestion bubbles */
    .sug-bubble:nth-child(1){animation:bubblePop 0.4s 0.05s both;}
    .sug-bubble:nth-child(2){animation:bubblePop 0.4s 0.12s both;}
    .sug-bubble:nth-child(3){animation:bubblePop 0.4s 0.19s both;}
    .sug-bubble:nth-child(4){animation:bubblePop 0.4s 0.26s both;}
    .sug-bubble:nth-child(5){animation:bubblePop 0.4s 0.33s both;}
    .sug-bubble:nth-child(6){animation:bubblePop 0.4s 0.40s both;}
    @keyframes bubblePop{from{opacity:0;transform:scale(0.88) translateY(6px);}to{opacity:1;transform:scale(1) translateY(0);}}
    </style>
    """, unsafe_allow_html=True)

    # ── BACKGROUND & ORBS ─────────────────────────────────────────────────
    st.markdown("""
    <div class="chat-bg"></div>
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
    """, unsafe_allow_html=True)

    # ── Handle voice/file state ───────────────────────────────────────────
    if st.session_state._voice_submit:
        st.session_state._voice_submit = False
        msg = st.session_state.voice_transcript or "[Voice message]"
        st.session_state.voice_transcript = ""
        dispatch_message(f"🎤 {msg}")
        st.toast("Voice message sent!", icon="🎤")
        st.rerun()

    # ── LEFT SIDEBAR HTML ─────────────────────────────────────────────────
    nm    = st.session_state.student_name
    br    = st.session_state.branch
    bh    = branch_hex(br)
    av_i  = initials(nm)
    sessions = st.session_state.chat_sessions

    history_html = ""
    if sessions:
        for sess in reversed(sessions[-8:]):
            lbl = sess.get("label","Chat")[:36]
            history_html += f'<div class="sidebar-history-item"><div class="sidebar-history-dot"></div><div class="sidebar-history-text">{lbl}</div></div>'
    else:
        history_html = '<div style="font-size:0.70rem;color:rgba(148,163,184,0.28);padding:8px 14px;">No saved chats yet.</div>'

    st.markdown(f"""
    <div class="chat-sidebar">
      <div class="sidebar-header">
        <div class="sidebar-logo-icon">A</div>
        <div>
          <div class="sidebar-brand">AskMNIT</div>
          <div class="sidebar-tagline">Your MNIT AI Senior</div>
        </div>
      </div>

      <div class="sidebar-section">
        <div class="sidebar-section-label">Navigation</div>
      </div>
    """, unsafe_allow_html=True)

    # Real sidebar nav buttons (Streamlit buttons positioned inside sidebar via CSS)
    st.markdown('<div style="padding:0 14px;">', unsafe_allow_html=True)

    col_nav = st.columns(1)
    with col_nav[0]:
        # ERP Login
        st.markdown("""
        <div class="sidebar-btn">
          <span class="sidebar-btn-icon">🎓</span> ERP Login
        </div>
        """, unsafe_allow_html=True)

    # History section
    st.markdown(f"""
      <div class="sidebar-divider"></div>
      <div class="sidebar-section">
        <div class="sidebar-section-label">Chat History</div>
        <div class="history-panel-inner">
          {history_html}
        </div>
      </div>
      <div class="sidebar-footer">
        <div class="sidebar-user">
          <div class="sidebar-user-avatar" style="background:linear-gradient(135deg,{bh},{bh}99);">{av_i}</div>
          <div>
            <div class="sidebar-user-name">{nm}</div>
            <div class="sidebar-user-branch">{br}</div>
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Actual functional sidebar buttons (use Streamlit, overlay on sidebar) ──
    # We handle sidebar buttons separately with real Streamlit buttons
    st.markdown("""
    <style>
    .sidebar-real-btns {
      position:fixed;top:76px;left:0;width:268px;z-index:1001;
      padding:0 14px;
    }
    .sidebar-real-btns .stButton>button{
      background:transparent!important;
      border:1px solid transparent!important;
      color:rgba(148,163,184,0.68)!important;
      box-shadow:none!important;
      text-align:left!important;
      justify-content:flex-start!important;
      padding:10px 14px!important;
      font-size:0.83rem!important;
      font-weight:500!important;
      border-radius:10px!important;
      width:100%!important;
    }
    .sidebar-real-btns .stButton>button:hover{
      background:rgba(79,46,220,0.10)!important;
      color:#C4B5FD!important;
      border-color:rgba(124,58,237,0.22)!important;
      transform:none!important;
    }
    .sidebar-real-btns [data-testid="stHorizontalBlock"]{gap:0!important;}
    .sidebar-real-btns [data-testid="column"]{padding:0!important;}
    </style>
    <div class="sidebar-real-btns">
    """, unsafe_allow_html=True)

    sb1, = st.columns([1])
    with sb1:
        if st.button("🎓  ERP Login", key="_sb_erp"):
            st.toast("ERP Login se MNIT portal khulega! 🎓", icon="🎓")
        if st.button("🕐  Chat History", key="_sb_history"):
            st.session_state.show_history_panel = not st.session_state.show_history_panel
            st.rerun()
        if st.button("+ New Chat", key="_sb_new"):
            if st.session_state.chat_messages:
                fu = next((m["content"][:42] for m in st.session_state.chat_messages if m["role"]=="user"), "Session")
                st.session_state.chat_sessions.append({"label": fu, "messages": list(st.session_state.chat_messages)})
            st.session_state.chat_messages = []
            st.session_state.attached_file_name = ""
            st.rerun()
        if st.button("🏠  Back to Dashboard", key="_sb_dash"):
            st.session_state.view = "dashboard"; st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ── TOP NAV BAR ───────────────────────────────────────────────────────
    st.markdown("""
    <div class="chat-topnav">
      <div class="topnav-left">
        <div class="topnav-model-badge">
          <div class="topnav-dot"></div>
          AskMNIT · LLaMA 3.3 70B
        </div>
      </div>
      <div class="topnav-right">
        <div class="topnav-icon-btn" title="Export">⬆</div>
        <div class="topnav-icon-btn" title="Settings">⚙</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── TOP NAV SETTINGS BUTTON (Streamlit) ───────────────────────────────
    st.markdown("""
    <style>
    .topnav-real-btns {
      position:fixed;top:0;right:0;height:56px;z-index:901;
      display:flex;align-items:center;gap:6px;padding-right:20px;
    }
    .topnav-real-btns .stButton>button{
      border-radius:999px!important;padding:5px 14px!important;
      font-size:0.72rem!important;font-weight:500!important;height:30px!important;
      border:1px solid rgba(255,255,255,0.10)!important;
      background:rgba(255,255,255,0.05)!important;
      color:rgba(226,232,240,0.70)!important;box-shadow:none!important;
      white-space:nowrap!important;
    }
    .topnav-real-btns .stButton>button:hover{
      background:rgba(79,46,220,0.16)!important;border-color:rgba(124,58,237,0.35)!important;
      color:#C4B5FD!important;transform:none!important;
    }
    .topnav-real-btns [data-testid="stHorizontalBlock"]{gap:6px!important;flex-wrap:nowrap!important;}
    .topnav-real-btns [data-testid="column"]{padding:0!important;flex:0 0 auto!important;width:auto!important;min-width:unset!important;}
    </style>
    <div class="topnav-real-btns">
    """, unsafe_allow_html=True)

    tn1, tn2 = st.columns([1,1])
    with tn1:
        if st.button("⚙ Settings", key="_tn_settings"):
            st.session_state.show_settings_panel = not st.session_state.show_settings_panel
            st.rerun()
    with tn2:
        if st.button("⬆ Export", key="_tn_export"):
            st.toast("Export feature coming soon!", icon="⬆")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── SETTINGS PANEL ────────────────────────────────────────────────────
    if st.session_state.show_settings_panel:
        st.markdown('<div style="margin-left:268px;padding:72px 32px 0;max-width:760px;margin-right:auto;">', unsafe_allow_html=True)
        with st.expander("⚙ Chat Settings", expanded=True):
            _s1, _s2 = st.columns(2)
            with _s1:
                new_style = st.selectbox("Response Style", ["Concise","Detailed","Bullet Points"],
                    index=["Concise","Detailed","Bullet Points"].index(st.session_state.response_style),
                    key="_sets_style2")
                if new_style != st.session_state.response_style:
                    st.session_state.response_style = new_style
            with _s2:
                st.session_state.voice_output = st.toggle("🔊 Voice Output", value=st.session_state.voice_output)
                st.session_state.strict_mode  = st.toggle("🎓 Strict Mode",  value=st.session_state.strict_mode)
            cc1, cc2 = st.columns([3,1])
            with cc1: st.markdown('<div style="font-size:0.84rem;color:rgba(226,232,240,0.75);padding-top:6px;">🗑 Clear all chat messages</div>', unsafe_allow_html=True)
            with cc2:
                if st.button("Clear", key="_sets_clear2"):
                    st.session_state.chat_messages = []
                    st.toast("Cleared!", icon="🗑"); st.rerun()
            if st.button("✕ Close", key="_sets_close2", use_container_width=True):
                st.session_state.show_settings_panel = False; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── HISTORY PANEL ─────────────────────────────────────────────────────
    if st.session_state.show_history_panel:
        st.markdown('<div style="margin-left:268px;padding:72px 32px 0;max-width:760px;margin-right:auto;">', unsafe_allow_html=True)
        with st.expander("🕐 Chat History", expanded=True):
            all_sess = st.session_state.chat_sessions
            if not all_sess:
                st.markdown('<div style="text-align:center;padding:20px;color:rgba(148,163,184,0.40);font-size:0.82rem;">No saved chats yet!</div>', unsafe_allow_html=True)
            else:
                for _i, _sess in enumerate(reversed(all_sess)):
                    _lbl = _sess.get("label","Chat")[:50]
                    _c1,_c2,_c3 = st.columns([5,1,1])
                    with _c1: st.markdown(f'<div style="padding:8px 12px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:9px;font-size:0.80rem;color:rgba(226,232,240,0.75);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{_lbl}</div>', unsafe_allow_html=True)
                    with _c2:
                        if st.button("↩", key=f"_hload_{_i}"):
                            st.session_state.chat_messages = list(_sess["messages"])
                            st.session_state.show_history_panel = False; st.rerun()
                    with _c3:
                        if st.button("🗑", key=f"_hdel_{_i}"):
                            real_i = len(all_sess) - 1 - _i
                            st.session_state.chat_sessions.pop(real_i); st.rerun()
                if st.button("Clear All", key="_hclearall"):
                    st.session_state.chat_sessions = []; st.rerun()
            if st.button("✕ Close History", key="_hclose", use_container_width=True):
                st.session_state.show_history_panel = False; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── FILE UPLOADER ─────────────────────────────────────────────────────
    if st.session_state.show_uploader:
        st.markdown('<div style="margin-left:268px;padding:72px 32px 0;max-width:760px;margin-right:auto;">', unsafe_allow_html=True)
        up_a, up_b = st.columns([6,1])
        with up_a:
            uploaded = st.file_uploader("Attach a file", type=["pdf","txt","png","jpg","jpeg","docx","csv"], key="chat_file_up")
        with up_b:
            st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
            if st.button("✕ Close", key="_up_close"):
                st.session_state.show_uploader = False; st.rerun()
        if uploaded:
            st.session_state.attached_file_name = uploaded.name
            st.session_state.show_uploader = False
            st.toast(f"📎 {uploaded.name} attached!", icon="✅"); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    has_messages = len(st.session_state.chat_messages) > 0

    # ══════════════════════════════════════════════════════════════════════
    # HERO STATE — No messages yet
    # ══════════════════════════════════════════════════════════════════════
    if not has_messages:
        st.markdown('<div class="chat-main">', unsafe_allow_html=True)
        st.markdown('<div class="hero-wrap">', unsafe_allow_html=True)

        st.markdown("""
        <div class="hero-orb-icon">🤖</div>
        <div class="hero-title">Ask <span>MNIT</span></div>
        <div class="hero-sub">
          Tera apna AI senior — attendance, schedule, PYQs,<br>
          aur baaki sab — ek jagah pe. Ready hai kya? 🚀
        </div>
        """, unsafe_allow_html=True)

        # Suggestion bubbles
        br = st.session_state.branch
        SUGGESTIONS = [
            "📊 Meri attendance analyse kar",
            "📅 Aaj ka schedule kya hai?",
            f"📚 {br} ke PYQs chahiye",
            "💸 Fee status check karo",
            "🎯 Exam strategy bana do",
            f"📖 {br} ke subjects batao",
        ]

        sug_html = '<div class="sug-wrap">'
        for s in SUGGESTIONS:
            sug_html += f'<div class="sug-bubble" onclick="">{s}</div>'
        sug_html += '</div>'
        st.markdown(sug_html, unsafe_allow_html=True)

        # Real suggestion buttons (hidden, triggered via columns)
        _, sug_mid, _ = st.columns([1, 6, 1])
        with sug_mid:
            row1 = st.columns(3)
            row2 = st.columns(3)
            sug_styles = """
            <style>
            .sug-real-row .stButton>button{
              background:rgba(255,255,255,0.04)!important;
              border:1px solid rgba(255,255,255,0.09)!important;
              border-radius:999px!important;
              color:rgba(186,230,253,0.72)!important;
              font-size:0.80rem!important;font-weight:500!important;
              padding:9px 14px!important;box-shadow:none!important;
              width:100%!important;
            }
            .sug-real-row .stButton>button:hover{
              background:rgba(79,46,220,0.16)!important;
              border-color:rgba(124,58,237,0.40)!important;
              color:#C4B5FD!important;transform:translateY(-2px)!important;
            }
            </style>
            <div class="sug-real-row">
            """
            st.markdown(sug_styles, unsafe_allow_html=True)
            for i, (pill, col) in enumerate(zip(SUGGESTIONS[:3], row1)):
                with col:
                    if st.button(pill, key=f"sug_r1_{i}", use_container_width=True):
                        dispatch_message(pill); st.rerun()
            for i, (pill, col) in enumerate(zip(SUGGESTIONS[3:], row2)):
                with col:
                    if st.button(pill, key=f"sug_r2_{i}", use_container_width=True):
                        dispatch_message(pill); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)  # hero-wrap

        # ── HERO INPUT BAR (centered) ─────────────────────────────────────
        st.markdown('<div class="input-bar-fixed">', unsafe_allow_html=True)

        if st.session_state.is_recording:
            st.markdown('<div class="rec-banner"><div class="rec-dot"></div><span>Listening… Press ⏹ to stop</span></div>', unsafe_allow_html=True)

        # File chip row
        if st.session_state.attached_file_name:
            st.markdown(f'<div style="max-width:720px;margin:0 auto 6px;display:flex;align-items:center;"><span class="file-chip">📎 {st.session_state.attached_file_name}</span></div>', unsafe_allow_html=True)

        st.markdown('<div class="input-bar-wrap">', unsafe_allow_html=True)
        st.markdown('<div class="input-bar-inner">', unsafe_allow_html=True)

        mic_class = "bar-mic-active" if st.session_state.is_recording else "bar-mic-btn"
        mic_icon  = "⏹" if st.session_state.is_recording else "🎤"

        col_attach, col_input, col_mic, col_send = st.columns([0.5, 10, 0.55, 0.55])

        with col_attach:
            st.markdown('<div class="bar-attach-btn">', unsafe_allow_html=True)
            if st.button("📎", key="h_attach", help="Attach file"):
                st.session_state.show_uploader = True; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with col_input:
            with st.form(key="hero_form", clear_on_submit=True):
                fc, fs = st.columns([12, 0.8])
                with fc:
                    st.markdown('<div class="chat-input-field">', unsafe_allow_html=True)
                    user_text = st.text_input("__h__", placeholder="Kuch bhi puch yaar...", key="h_text", label_visibility="collapsed")
                    st.markdown('</div>', unsafe_allow_html=True)
                with fs:
                    st.markdown('<div class="bar-send-btn">', unsafe_allow_html=True)
                    send_hero = st.form_submit_button("↑")
                    st.markdown('</div>', unsafe_allow_html=True)

        with col_mic:
            st.markdown(f'<div class="{mic_class}">', unsafe_allow_html=True)
            mic_hero = st.button(mic_icon, key="h_mic", help="Voice input")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_send:
            pass  # send is inside form

        st.markdown('</div></div>', unsafe_allow_html=True)  # input-bar-inner + wrap
        st.markdown('<div class="chat-disclaimer">AskMNIT AI mistakes kar sakta hai · Always verify with ERP or faculty</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)  # input-bar-fixed

        st.markdown('</div>', unsafe_allow_html=True)  # chat-main

        # Handle hero actions
        if send_hero:
            txt = (user_text or "").strip()
            if txt or st.session_state.attached_file_name:
                full = txt
                if st.session_state.attached_file_name and not txt:
                    full = f"[File attached: {st.session_state.attached_file_name}]"
                elif st.session_state.attached_file_name:
                    full = f"{txt} [File: {st.session_state.attached_file_name}]"
                dispatch_message(full)
                st.session_state.attached_file_name = ""; st.rerun()

        if mic_hero:
            if st.session_state.is_recording:
                st.session_state.is_recording = False
                st.session_state._voice_submit = True
                st.session_state.voice_transcript = "[Voice message recorded]"
                st.toast("⏹ Processing voice...", icon="⏳")
            else:
                st.session_state.is_recording = True
                st.toast("🎤 Recording started!", icon="🎤")
            st.rerun()

    # ══════════════════════════════════════════════════════════════════════
    # ACTIVE CHAT STATE — messages exist
    # ══════════════════════════════════════════════════════════════════════
    else:
        st.markdown('<div class="chat-main">', unsafe_allow_html=True)
        st.markdown('<div class="chat-messages-area">', unsafe_allow_html=True)
        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        st.markdown('</div>', unsafe_allow_html=True)  # messages-area
        st.markdown('</div>', unsafe_allow_html=True)  # chat-main

        # ── ANCHORED INPUT BAR ────────────────────────────────────────────
        st.markdown('<div class="input-bar-fixed">', unsafe_allow_html=True)

        if st.session_state.is_recording:
            st.markdown('<div class="rec-banner"><div class="rec-dot"></div><span>Listening… Press ⏹ to stop</span></div>', unsafe_allow_html=True)

        if st.session_state.attached_file_name:
            st.markdown(f'<div style="max-width:720px;margin:0 auto 6px;display:flex;align-items:center;"><span class="file-chip">📎 {st.session_state.attached_file_name}</span></div>', unsafe_allow_html=True)

        st.markdown('<div class="input-bar-wrap">', unsafe_allow_html=True)
        st.markdown('<div class="input-bar-inner">', unsafe_allow_html=True)

        mic_class2 = "bar-mic-active" if st.session_state.is_recording else "bar-mic-btn"
        mic_icon2  = "⏹" if st.session_state.is_recording else "🎤"

        ac_a, ac_i, ac_m, _ = st.columns([0.5, 10, 0.55, 0.55])

        with ac_a:
            st.markdown('<div class="bar-attach-btn">', unsafe_allow_html=True)
            if st.button("📎", key="a_attach", help="Attach file"):
                st.session_state.show_uploader = True; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with ac_i:
            with st.form(key="anchored_form", clear_on_submit=True):
                fc2, fs2 = st.columns([12, 0.8])
                with fc2:
                    st.markdown('<div class="chat-input-field">', unsafe_allow_html=True)
                    user_text_a = st.text_input("__a__", placeholder="Kuch bhi puch yaar...", key="a_text", label_visibility="collapsed")
                    st.markdown('</div>', unsafe_allow_html=True)
                with fs2:
                    st.markdown('<div class="bar-send-btn">', unsafe_allow_html=True)
                    send_a = st.form_submit_button("↑")
                    st.markdown('</div>', unsafe_allow_html=True)

        with ac_m:
            st.markdown(f'<div class="{mic_class2}">', unsafe_allow_html=True)
            mic_a = st.button(mic_icon2, key="a_mic", help="Voice input")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="chat-disclaimer">AskMNIT AI mistakes kar sakta hai · Always verify with ERP or faculty</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)  # input-bar-fixed

        if send_a:
            txt = (user_text_a or "").strip()
            if txt or st.session_state.attached_file_name:
                full = txt
                if st.session_state.attached_file_name and not txt:
                    full = f"[File attached: {st.session_state.attached_file_name}]"
                elif st.session_state.attached_file_name:
                    full = f"{txt} [File: {st.session_state.attached_file_name}]"
                dispatch_message(full)
                st.session_state.attached_file_name = ""; st.rerun()

        if mic_a:
            if st.session_state.is_recording:
                st.session_state.is_recording = False
                st.session_state._voice_submit = True
                st.session_state.voice_transcript = "[Voice message recorded]"
                st.toast("⏹ Processing voice...", icon="⏳")
            else:
                st.session_state.is_recording = True
                st.toast("🎤 Recording started!", icon="🎤")
            st.rerun()

    st.stop()


###############################################################################
# ██████████████████████  DASHBOARD VIEW  ███████████████████████████████████
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

st.markdown('<div style="text-align:center;margin-top:28px;padding:10px 0;border-top:1px solid rgba(255,255,255,0.05);"><span style="font-family:\'DM Mono\',monospace;font-size:0.52rem;color:rgba(148,163,184,0.24);letter-spacing:1.2px;">ASKMINT &nbsp;·&nbsp; MNIT JAIPUR &nbsp;·&nbsp; v7.0 PREMIUM</span></div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
