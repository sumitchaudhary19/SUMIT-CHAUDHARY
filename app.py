# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  AskMNIT — v7.0 PREMIUM CHAT REDESIGN                                       ║
# ║  New: Premium dark chatbot UI, left sidebar, centered input, animations      ║
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
    with st.spinner(""):
        reply = generate_ai_response(text)
    st.session_state.chat_messages.append({"role":"assistant","content":reply})

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS — Dashboard styles (unchanged)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,700;9..144,900&family=DM+Mono:wght@400;500&family=Outfit:wght@300;400;500;600;700&display=swap');

*,html,body{box-sizing:border-box;margin:0;padding:0;}
html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"]{font-family:'Outfit',sans-serif!important;}
header[data-testid="stHeader"],footer,#MainMenu,[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important;}
[data-testid="stMainBlockContainer"]{padding:0!important;max-width:100%!important;}

/* Dashboard sidebar */
[data-testid="stSidebar"]{background:#0B1120!important;border-right:1px solid rgba(59,130,246,0.16)!important;min-width:260px!important;max-width:260px!important;}
[data-testid="stSidebar"]>div{padding:0!important;}
.sb-section-header{font-family:'DM Mono',monospace;font-size:0.60rem;font-weight:700;color:rgba(148,163,184,0.50);text-transform:uppercase;letter-spacing:1.4px;padding:14px 16px 6px;border-top:1px solid rgba(255,255,255,0.05);margin-top:4px;}
[data-testid="stSidebar"] .stButton>button{background:rgba(239,68,68,0.10)!important;border:1px solid rgba(239,68,68,0.28)!important;color:#FCA5A5!important;border-radius:8px!important;font-size:0.80rem!important;font-weight:600!important;padding:7px 14px!important;box-shadow:none!important;}
[data-testid="stSidebar"] .stButton>button:hover{background:rgba(239,68,68,0.20)!important;transform:none!important;}

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
.logout-btn .stButton>button{background:rgba(239,68,68,.09)!important;border:1px solid rgba(239,68,68,.20)!important;color:#FCA5A5!important;box-shadow:none!important;font-size:0.80rem!important;}
.open-chat-btn .stButton>button{background:linear-gradient(135deg,#059669,#10B981)!important;border-radius:12px!important;font-weight:700!important;font-size:0.88rem!important;padding:11px 22px!important;box-shadow:0 5px 24px rgba(16,185,129,.36)!important;font-family:'DM Mono',monospace!important;}
.settings-menu-btn .stButton>button{background:rgba(255,255,255,0.06)!important;border:1px solid rgba(255,255,255,0.12)!important;color:rgba(226,232,240,0.75)!important;box-shadow:none!important;font-size:0.82rem!important;font-weight:600!important;padding:8px 16px!important;border-radius:10px!important;}
.nav-btn .stButton>button{background:transparent!important;color:rgba(148,163,184,.65)!important;border:none!important;box-shadow:none!important;text-align:left!important;justify-content:flex-start!important;padding:10px 14px!important;font-size:0.83rem!important;font-weight:500!important;border-radius:8px!important;}
.nav-btn .stButton>button:hover{background:rgba(59,130,246,.10)!important;color:#BAE6FD!important;transform:none!important;}
.nav-btn-active .stButton>button{background:rgba(59,130,246,.14)!important;color:#60A5FA!important;border-left:2px solid #3B82F6!important;font-weight:700!important;box-shadow:none!important;}

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


# ═════════════════════════════════════════════════════════════════════════════
# VIEW ROUTER
# ═════════════════════════════════════════════════════════════════════════════
view = st.session_state.view

###############################################################################
# ██████████████████████  NEW PREMIUM CHAT VIEW  ██████████████████████████████
###############################################################################
if view == "chat":

    # ── Kill Streamlit sidebar & default layout completely ─────────────────
    st.markdown("""
    <style>
    [data-testid="stSidebar"]{display:none!important;}
    [data-testid="stSidebarCollapseButton"]{display:none!important;}
    [data-testid="collapsedControl"]{display:none!important;}
    section[data-testid="stMain"]{margin-left:0!important;padding-left:0!important;}
    [data-testid="stMainBlockContainer"]{padding:0!important;max-width:100%!important;}
    html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"]{
        background:#08080F!important;overflow:hidden!important;height:100vh!important;
    }
    /* Hide all streamlit default spacing */
    .block-container{padding:0!important;max-width:100%!important;}
    </style>
    """, unsafe_allow_html=True)

    has_messages = bool(st.session_state.chat_messages)

    # ── Handle voice submit ────────────────────────────────────────────────
    if st.session_state._voice_submit:
        st.session_state._voice_submit = False
        msg = st.session_state.voice_transcript or "[Voice message]"
        st.session_state.voice_transcript = ""
        dispatch_message(f"🎤 {msg}")
        st.rerun()

    # ──────────────────────────────────────────────────────────────────────
    # FULL CUSTOM HTML CHAT UI
    # ──────────────────────────────────────────────────────────────────────
    nm   = st.session_state.student_name
    br   = st.session_state.branch
    msgs = st.session_state.chat_messages
    sessions = st.session_state.chat_sessions

    # Build chat messages HTML
    chat_html = ""
    for msg in msgs:
        role = msg["role"]
        content = msg["content"].replace("<","&lt;").replace(">","&gt;").replace("\n","<br>")
        if role == "user":
            chat_html += f'''
            <div class="msg-row user-row">
                <div class="msg-bubble user-bubble">{content}</div>
                <div class="msg-avatar user-avatar">{initials(nm)}</div>
            </div>'''
        else:
            chat_html += f'''
            <div class="msg-row ai-row">
                <div class="msg-avatar ai-avatar">A</div>
                <div class="msg-bubble ai-bubble">{content}</div>
            </div>'''

    # Build history sidebar items
    history_html = ""
    if sessions:
        for i, sess in enumerate(reversed(sessions)):
            label = sess.get("label","Chat")[:32]
            history_html += f'<div class="hist-item" onclick="loadSession({len(sessions)-1-i})"><span class="hist-dot"></span>{label}...</div>'
    else:
        history_html = '<div class="hist-empty">No saved chats yet</div>'

    # Suggestion pills
    branch = st.session_state.branch
    PILLS = [
        f"📊 Analyse my attendance",
        f"📅 Next class today?",
        f"📚 PYQs for {branch}",
        f"💸 Fee status check",
        f"📖 Subjects this sem",
        f"🎯 Exam tips for me",
    ]
    pills_html = "".join(f'<button class="pill-btn" onclick="sendPill(this)">{p}</button>' for p in PILLS)

    # ERP login form
    erp_section = '''
    <div class="erp-section">
      <div class="erp-title">🔐 ERP Login</div>
      <input class="erp-input" id="erpUser" placeholder="College ID / Username" />
      <input class="erp-input" type="password" id="erpPass" placeholder="Password" />
      <button class="erp-btn" onclick="erpLogin()">Login to ERP Portal →</button>
      <div class="erp-note">Opens official MNIT ERP in new tab</div>
    </div>'''

    # Pre-build JS variable strings (avoids f-string / repr brace conflicts)
    import json
    _attached_js   = json.dumps(st.session_state.attached_file_name)
    _sessions_list = [{"label": s["label"], "count": len(s["messages"])} for s in sessions[:20]]
    _sessions_js   = json.dumps(_sessions_list)
    _initials_js   = json.dumps(initials(nm))
    _branch_js     = json.dumps(branch)
    _has_msgs_js   = "true" if has_messages else "false"

    # Assemble the full HTML
    CHAT_HTML = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&family=Nunito:wght@400;500;600;700&display=swap');

:root {{
  --bg:       #08080F;
  --bg2:      #0D0D1A;
  --bg3:      #12121F;
  --sidebar:  #0A0A16;
  --border:   rgba(120,80,255,0.18);
  --border2:  rgba(255,255,255,0.07);
  --purple:   #7C3AED;
  --purple2:  #A78BFA;
  --cyan:     #22D3EE;
  --pink:     #EC4899;
  --text:     #F1F0FF;
  --text2:    rgba(200,195,240,0.65);
  --text3:    rgba(150,140,200,0.42);
  --glow:     rgba(124,58,237,0.35);
  --sidebar-w: 256px;
}}

*{{box-sizing:border-box;margin:0;padding:0;}}
html,body{{
  height:100vh;overflow:hidden;
  font-family:'Nunito',sans-serif;
  background:var(--bg);
  color:var(--text);
}}

/* ─── ANIMATED BACKGROUND ─── */
.bg-canvas{{
  position:fixed;inset:0;z-index:0;pointer-events:none;
  background: radial-gradient(ellipse 80% 60% at 60% -10%, rgba(124,58,237,0.18) 0%, transparent 60%),
              radial-gradient(ellipse 50% 40% at 100% 80%, rgba(34,211,238,0.09) 0%, transparent 55%),
              radial-gradient(ellipse 40% 50% at -10% 50%, rgba(236,72,153,0.07) 0%, transparent 60%),
              var(--bg);
}}
.bg-orb{{
  position:absolute;border-radius:50%;filter:blur(80px);animation:orbFloat 12s ease-in-out infinite;
}}
.bg-orb1{{width:400px;height:400px;top:-100px;right:10%;background:rgba(124,58,237,0.12);animation-delay:0s;}}
.bg-orb2{{width:300px;height:300px;bottom:10%;left:5%;background:rgba(34,211,238,0.08);animation-delay:4s;}}
.bg-orb3{{width:250px;height:250px;top:40%;right:-5%;background:rgba(236,72,153,0.07);animation-delay:8s;}}
@keyframes orbFloat{{
  0%,100%{{transform:translate(0,0) scale(1);}}
  33%{{transform:translate(20px,-30px) scale(1.05);}}
  66%{{transform:translate(-15px,20px) scale(0.96);}}
}}

/* ─── GRID TEXTURE ─── */
.bg-grid{{
  position:fixed;inset:0;z-index:0;pointer-events:none;
  background-image: linear-gradient(rgba(120,80,255,0.04) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(120,80,255,0.04) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: radial-gradient(ellipse 90% 90% at 50% 50%, black 30%, transparent 100%);
}}

/* ─── LAYOUT ─── */
.chat-root{{
  position:fixed;inset:0;z-index:10;
  display:flex;
}}

/* ─── SIDEBAR ─── */
.sidebar{{
  width:var(--sidebar-w);
  min-width:var(--sidebar-w);
  height:100vh;
  background:var(--sidebar);
  border-right:1px solid var(--border);
  display:flex;flex-direction:column;
  overflow:hidden;
  position:relative;
  z-index:20;
  backdrop-filter:blur(20px);
}}
.sidebar::before{{
  content:'';
  position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,var(--purple),transparent);
}}
.sb-logo{{
  padding:20px 18px 16px;
  border-bottom:1px solid var(--border2);
}}
.sb-logo-mark{{
  display:flex;align-items:center;gap:10px;
}}
.sb-logo-icon{{
  width:34px;height:34px;border-radius:10px;
  background:linear-gradient(135deg,var(--purple),#4F46E5);
  display:flex;align-items:center;justify-content:center;
  font-family:'JetBrains Mono',monospace;font-size:0.88rem;font-weight:700;color:#fff;
  box-shadow:0 0 20px var(--glow),0 4px 12px rgba(0,0,0,0.4);
}}
.sb-logo-text{{
  font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:800;color:var(--text);letter-spacing:-0.3px;
}}
.sb-logo-sub{{font-size:0.55rem;color:var(--text3);font-family:'JetBrains Mono',monospace;letter-spacing:0.8px;margin-top:1px;}}
.sb-new-chat{{
  margin:14px 14px 8px;
  background:linear-gradient(135deg,rgba(124,58,237,0.25),rgba(79,70,229,0.18));
  border:1px solid rgba(124,58,237,0.40);
  border-radius:10px;padding:10px 14px;
  display:flex;align-items:center;gap:9px;
  cursor:pointer;
  font-size:0.84rem;font-weight:600;color:var(--purple2);
  transition:all 0.18s;
}}
.sb-new-chat:hover{{background:rgba(124,58,237,0.32);border-color:rgba(124,58,237,0.60);transform:translateY(-1px);box-shadow:0 4px 16px rgba(124,58,237,0.20);}}
.sb-new-icon{{font-size:1rem;}}
.sb-section{{
  font-family:'JetBrains Mono',monospace;
  font-size:0.52rem;font-weight:500;color:var(--text3);
  text-transform:uppercase;letter-spacing:1.6px;
  padding:14px 16px 7px;
}}
.sb-nav-item{{
  display:flex;align-items:center;gap:10px;
  padding:9px 16px;margin:2px 8px;
  border-radius:9px;cursor:pointer;
  font-size:0.83rem;font-weight:500;color:var(--text2);
  transition:all 0.15s;
  position:relative;
}}
.sb-nav-item:hover{{background:rgba(124,58,237,0.12);color:var(--purple2);}}
.sb-nav-item.active{{background:rgba(124,58,237,0.18);color:var(--purple2);border-left:2px solid var(--purple);}}
.sb-nav-icon{{font-size:0.92rem;width:18px;text-align:center;}}
.sb-history{{flex:1;overflow-y:auto;padding:0 0 10px;}}
.sb-history::-webkit-scrollbar{{width:3px;}}
.sb-history::-webkit-scrollbar-thumb{{background:rgba(124,58,237,0.20);border-radius:3px;}}
.hist-item{{
  display:flex;align-items:center;gap:9px;
  padding:8px 16px;cursor:pointer;
  font-size:0.78rem;color:var(--text3);
  border-bottom:1px solid rgba(255,255,255,0.025);
  transition:all 0.14s;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
}}
.hist-item:hover{{background:rgba(124,58,237,0.08);color:var(--purple2);}}
.hist-dot{{width:5px;height:5px;border-radius:50%;background:rgba(124,58,237,0.50);flex-shrink:0;}}
.hist-empty{{padding:18px 16px;font-size:0.74rem;color:var(--text3);text-align:center;font-style:italic;}}
.sb-bottom{{
  border-top:1px solid var(--border2);padding:14px;
}}
.sb-back-btn{{
  display:flex;align-items:center;gap:8px;
  padding:9px 12px;border-radius:9px;cursor:pointer;
  font-size:0.81rem;font-weight:600;color:rgba(34,211,238,0.75);
  background:rgba(34,211,238,0.07);border:1px solid rgba(34,211,238,0.18);
  transition:all 0.16s;
}}
.sb-back-btn:hover{{background:rgba(34,211,238,0.13);color:var(--cyan);border-color:rgba(34,211,238,0.35);}}

/* ERP Section */
.erp-section{{padding:12px;margin:8px 10px;background:rgba(236,72,153,0.06);border:1px solid rgba(236,72,153,0.18);border-radius:12px;}}
.erp-title{{font-family:'JetBrains Mono',monospace;font-size:0.62rem;font-weight:500;color:rgba(236,72,153,0.80);text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;}}
.erp-input{{
  width:100%;margin-bottom:7px;padding:8px 10px;
  background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.10);
  border-radius:8px;color:var(--text);font-size:0.76rem;font-family:'Nunito',sans-serif;
  outline:none;transition:border-color 0.18s;
}}
.erp-input:focus{{border-color:rgba(236,72,153,0.45);}}
.erp-input::placeholder{{color:rgba(150,140,200,0.35);}}
.erp-btn{{
  width:100%;padding:8px;
  background:linear-gradient(135deg,rgba(236,72,153,0.28),rgba(190,24,93,0.20));
  border:1px solid rgba(236,72,153,0.35);border-radius:8px;
  color:rgba(236,72,153,0.90);font-size:0.76rem;font-weight:700;
  cursor:pointer;transition:all 0.16s;
}}
.erp-btn:hover{{background:rgba(236,72,153,0.35);box-shadow:0 3px 12px rgba(236,72,153,0.20);}}
.erp-note{{font-size:0.58rem;color:var(--text3);text-align:center;margin-top:6px;}}

/* ─── MAIN AREA ─── */
.main-area{{
  flex:1;display:flex;flex-direction:column;
  height:100vh;overflow:hidden;position:relative;
}}

/* ─── TOPBAR ─── */
.topbar{{
  height:52px;flex-shrink:0;
  display:flex;align-items:center;justify-content:space-between;
  padding:0 24px;
  background:rgba(8,8,15,0.90);
  border-bottom:1px solid var(--border2);
  backdrop-filter:blur(20px);
  z-index:30;
}}
.topbar-model{{
  display:flex;align-items:center;gap:8px;
  background:rgba(255,255,255,0.04);border:1px solid var(--border2);
  border-radius:20px;padding:5px 14px;
  font-family:'JetBrains Mono',monospace;font-size:0.70rem;color:var(--text2);
  cursor:pointer;transition:all 0.15s;
}}
.topbar-model:hover{{border-color:rgba(124,58,237,0.35);color:var(--purple2);}}
.model-dot{{width:6px;height:6px;border-radius:50%;background:#10B981;box-shadow:0 0 6px #10B981;}}
.topbar-actions{{display:flex;align-items:center;gap:8px;}}
.topbar-btn{{
  padding:6px 14px;border-radius:20px;cursor:pointer;
  font-size:0.72rem;font-weight:600;
  background:rgba(255,255,255,0.04);border:1px solid var(--border2);
  color:var(--text2);transition:all 0.15s;
  font-family:'Nunito',sans-serif;
}}
.topbar-btn:hover{{background:rgba(124,58,237,0.15);border-color:rgba(124,58,237,0.35);color:var(--purple2);}}
.topbar-btn.active{{background:rgba(124,58,237,0.20);border-color:rgba(124,58,237,0.45);color:var(--purple2);}}

/* ─── CHAT AREA ─── */
.chat-area{{
  flex:1;overflow-y:auto;
  padding:20px 0 20px;
  scroll-behavior:smooth;
}}
.chat-area::-webkit-scrollbar{{width:4px;}}
.chat-area::-webkit-scrollbar-thumb{{background:rgba(124,58,237,0.20);border-radius:4px;}}

/* ─── HERO (empty state) ─── */
.hero-wrap{{
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  min-height:calc(100vh - 220px);padding:20px;
  animation:heroIn 0.55s cubic-bezier(0.22,0.61,0.36,1) both;
}}
@keyframes heroIn{{
  from{{opacity:0;transform:translateY(28px);}}
  to{{opacity:1;transform:translateY(0);}}
}}
.hero-orb{{
  width:88px;height:88px;border-radius:24px;
  background:linear-gradient(135deg,#1E1B4B 0%,#4C1D95 40%,#7C3AED 70%,#22D3EE 100%);
  display:flex;align-items:center;justify-content:center;
  font-size:2.2rem;margin-bottom:26px;
  box-shadow:
    0 0 0 1px rgba(124,58,237,0.30),
    0 0 40px rgba(124,58,237,0.35),
    0 20px 60px rgba(0,0,0,0.50),
    inset 0 1px 0 rgba(255,255,255,0.10);
  animation:orbPulse 3s ease-in-out infinite;
  position:relative;
}}
@keyframes orbPulse{{
  0%,100%{{box-shadow:0 0 0 1px rgba(124,58,237,0.30),0 0 40px rgba(124,58,237,0.35),0 20px 60px rgba(0,0,0,0.50),inset 0 1px 0 rgba(255,255,255,0.10);}}
  50%{{box-shadow:0 0 0 1px rgba(124,58,237,0.50),0 0 60px rgba(124,58,237,0.55),0 20px 60px rgba(0,0,0,0.50),inset 0 1px 0 rgba(255,255,255,0.10);}}
}}
.hero-title{{
  font-family:'Syne',sans-serif;
  font-size:2.6rem;font-weight:800;
  letter-spacing:-2px;line-height:1.05;
  text-align:center;margin-bottom:12px;
  background:linear-gradient(135deg,#F1F0FF 0%,var(--purple2) 50%,var(--cyan) 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}}
.hero-sub{{
  font-size:0.88rem;color:var(--text3);text-align:center;
  line-height:1.75;margin-bottom:36px;
  max-width:460px;
}}

/* ─── SUGGESTION PILLS ─── */
.pills-wrap{{
  display:flex;flex-wrap:wrap;gap:8px;justify-content:center;
  max-width:660px;margin:0 auto;
  animation:heroIn 0.65s 0.12s cubic-bezier(0.22,0.61,0.36,1) both;
}}
.pill-btn{{
  padding:9px 18px;border-radius:999px;cursor:pointer;
  font-size:0.79rem;font-weight:600;font-family:'Nunito',sans-serif;
  background:rgba(255,255,255,0.04);
  border:1px solid rgba(255,255,255,0.10);
  color:rgba(200,195,240,0.72);
  transition:all 0.18s;
  white-space:nowrap;
}}
.pill-btn:hover{{
  background:rgba(124,58,237,0.18);
  border-color:rgba(124,58,237,0.40);
  color:var(--purple2);
  transform:translateY(-2px);
  box-shadow:0 6px 20px rgba(124,58,237,0.20);
}}

/* ─── MESSAGE BUBBLES ─── */
.msg-row{{
  display:flex;align-items:flex-end;gap:10px;
  padding:6px 28px;max-width:860px;margin:0 auto;width:100%;
  animation:msgIn 0.28s cubic-bezier(0.22,0.61,0.36,1) both;
}}
@keyframes msgIn{{from{{opacity:0;transform:translateY(10px);}}to{{opacity:1;transform:translateY(0);}}}}
.user-row{{flex-direction:row-reverse;}}
.msg-avatar{{
  width:32px;height:32px;border-radius:50%;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;
  font-size:0.72rem;font-weight:800;
  font-family:'JetBrains Mono',monospace;
}}
.user-avatar{{
  background:linear-gradient(135deg,var(--purple),#4F46E5);
  color:#fff;box-shadow:0 3px 12px rgba(124,58,237,0.35);
}}
.ai-avatar{{
  background:linear-gradient(135deg,#0F172A,#1E1B4B);
  color:var(--purple2);border:1px solid rgba(124,58,237,0.30);
  font-size:0.78rem;font-weight:700;
}}
.msg-bubble{{
  max-width:72%;padding:13px 17px;border-radius:16px;
  font-size:0.88rem;line-height:1.65;
}}
.user-bubble{{
  background:linear-gradient(135deg,rgba(124,58,237,0.30),rgba(79,70,229,0.22));
  border:1px solid rgba(124,58,237,0.35);
  border-bottom-right-radius:4px;
  color:var(--text);
  box-shadow:0 4px 20px rgba(124,58,237,0.18);
}}
.ai-bubble{{
  background:rgba(255,255,255,0.032);
  border:1px solid rgba(255,255,255,0.07);
  border-bottom-left-radius:4px;
  color:rgba(220,215,255,0.88);
}}

/* ─── INPUT ZONE ─── */
.input-zone{{
  flex-shrink:0;
  padding:14px 24px 18px;
  background:rgba(8,8,15,0.92);
  border-top:1px solid var(--border2);
  backdrop-filter:blur(24px);
}}
.input-zone.hero-mode{{
  background:transparent;
  border-top:none;
  padding:0 24px 20px;
  max-width:680px;
  margin:0 auto;
  width:100%;
}}

/* The bar itself */
.search-bar{{
  display:flex;align-items:flex-end;gap:0;
  background:rgba(13,13,26,0.92);
  border:1.5px solid rgba(124,58,237,0.28);
  border-radius:18px;padding:10px 10px 10px 16px;
  min-height:60px;
  box-shadow:0 4px 32px rgba(0,0,0,0.40), 0 0 0 0px rgba(124,58,237,0);
  transition:border-color 0.22s, box-shadow 0.22s;
  animation:barGlow 4s ease-in-out infinite;
  position:relative;
}}
@keyframes barGlow{{
  0%,100%{{box-shadow:0 4px 32px rgba(0,0,0,0.40),0 0 0 0 rgba(124,58,237,0.0);}}
  50%{{box-shadow:0 4px 32px rgba(0,0,0,0.40),0 0 28px rgba(124,58,237,0.12);}}
}}
.search-bar:focus-within{{
  border-color:rgba(124,58,237,0.65)!important;
  box-shadow:0 0 0 3px rgba(124,58,237,0.14), 0 6px 40px rgba(124,58,237,0.20)!important;
  animation:none;
}}
.bar-spark{{
  color:rgba(167,139,250,0.50);font-size:1rem;
  margin-right:8px;flex-shrink:0;align-self:center;
  animation:sparkPulse 2.5s ease-in-out infinite;
}}
@keyframes sparkPulse{{
  0%,100%{{opacity:0.50;transform:scale(1);}}
  50%{{opacity:0.80;transform:scale(1.12);}}
}}
.bar-input{{
  flex:1;background:transparent;border:none;outline:none;
  color:var(--text);font-family:'Nunito',sans-serif;font-size:0.95rem;
  caret-color:var(--purple2);
  resize:none;overflow:hidden;min-height:36px;max-height:160px;
  line-height:1.5;padding:4px 0;
  align-self:center;
}}
.bar-input::placeholder{{color:rgba(150,140,200,0.35);}}
.bar-actions{{
  display:flex;align-items:center;gap:6px;flex-shrink:0;align-self:flex-end;
  padding-bottom:2px;
}}
.bar-icon-btn{{
  width:36px;height:36px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  cursor:pointer;font-size:0.95rem;
  background:rgba(255,255,255,0.04);
  border:1px solid rgba(255,255,255,0.09);
  color:rgba(150,140,200,0.55);
  transition:all 0.16s;
  flex-shrink:0;
}}
.bar-icon-btn:hover{{background:rgba(124,58,237,0.18);border-color:rgba(124,58,237,0.40);color:var(--purple2);}}
.bar-icon-btn.active{{background:rgba(239,68,68,0.18);border-color:rgba(239,68,68,0.45);color:#FCA5A5;animation:micPulse 1.1s ease-in-out infinite;}}
@keyframes micPulse{{0%,100%{{box-shadow:0 0 0 0 rgba(239,68,68,0.40);}}50%{{box-shadow:0 0 0 7px rgba(239,68,68,0.0);}}}}
.send-btn{{
  width:38px;height:38px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  cursor:pointer;font-size:1.05rem;
  background:linear-gradient(135deg,var(--purple),#4F46E5);
  border:none;color:#fff;
  box-shadow:0 3px 14px rgba(124,58,237,0.40);
  transition:all 0.15s;
  flex-shrink:0;
}}
.send-btn:hover{{transform:scale(1.08);box-shadow:0 5px 20px rgba(124,58,237,0.55);}}

/* Attach chip */
.attach-chip{{
  display:inline-flex;align-items:center;gap:5px;
  background:rgba(124,58,237,0.15);border:1px solid rgba(124,58,237,0.35);
  border-radius:20px;padding:3px 10px 3px 8px;
  font-size:0.72rem;color:var(--purple2);font-weight:600;
  max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
  margin-bottom:8px;
}}
.chip-x{{cursor:pointer;color:rgba(150,140,200,0.45);margin-left:4px;padding:0 2px;}}
.chip-x:hover{{color:var(--purple2);}}

/* File input hidden */
#realFileInput{{display:none;}}

/* Input bar hint */
.bar-hint{{
  text-align:center;font-size:0.58rem;
  color:rgba(100,90,160,0.38);
  font-family:'JetBrains Mono',monospace;
  letter-spacing:0.5px;margin-top:8px;
}}

/* Recording banner */
.recording-banner{{
  display:flex;align-items:center;gap:7px;
  max-width:600px;margin:8px auto 0;
  padding:7px 16px;
  background:rgba(239,68,68,0.09);border:1px solid rgba(239,68,68,0.22);border-radius:9px;
  font-size:0.78rem;color:#FCA5A5;
}}
.rec-dot{{width:7px;height:7px;border-radius:50%;background:#EF4444;animation:blinkDot 1s ease infinite;flex-shrink:0;}}
@keyframes blinkDot{{0%,100%{{opacity:1;}}50%{{opacity:0.2;}}}}

/* Typing indicator */
.typing-row{{display:flex;align-items:flex-end;gap:10px;padding:6px 28px;max-width:860px;margin:0 auto;width:100%;}}
.typing-bubble{{padding:12px 16px;border-radius:16px;border-bottom-left-radius:4px;background:rgba(255,255,255,0.032);border:1px solid rgba(255,255,255,0.07);}}
.typing-dots{{display:flex;align-items:center;gap:4px;}}
.typing-dot{{width:6px;height:6px;border-radius:50%;background:rgba(124,58,237,0.60);animation:typeDot 1.2s ease-in-out infinite;}}
.typing-dot:nth-child(2){{animation-delay:0.20s;}}
.typing-dot:nth-child(3){{animation-delay:0.40s;}}
@keyframes typeDot{{0%,60%,100%{{transform:translateY(0);opacity:0.5;}}30%{{transform:translateY(-6px);opacity:1;}}}}

/* Scrollbar */
::-webkit-scrollbar{{width:4px;}}
::-webkit-scrollbar-thumb{{background:rgba(124,58,237,0.20);border-radius:4px;}}
</style>
</head>
<body>

<!-- Background -->
<div class="bg-canvas">
  <div class="bg-orb bg-orb1"></div>
  <div class="bg-orb bg-orb2"></div>
  <div class="bg-orb bg-orb3"></div>
</div>
<div class="bg-grid"></div>

<!-- Hidden file input -->
<input type="file" id="realFileInput" accept=".pdf,.txt,.png,.jpg,.jpeg,.docx,.csv" onchange="handleFileSelect(this)">

<div class="chat-root">

  <!-- ═══ SIDEBAR ═══ -->
  <aside class="sidebar">
    <div class="sb-logo">
      <div class="sb-logo-mark">
        <div class="sb-logo-icon">A</div>
        <div>
          <div class="sb-logo-text">AskMNIT</div>
          <div class="sb-logo-sub">AI ASSISTANT · MNIT JAIPUR</div>
        </div>
      </div>
    </div>

    <!-- New Chat -->
    <div class="sb-new-chat" onclick="newChat()">
      <span class="sb-new-icon">✦</span>
      <span>New Chat</span>
    </div>

    <!-- Nav Items -->
    <div class="sb-section">Navigation</div>
    <div class="sb-nav-item active" onclick="setNav(this)"><span class="sb-nav-icon">💬</span> Chat</div>
    <div class="sb-nav-item" onclick="openHistoryPanel()"><span class="sb-nav-icon">🕐</span> Chat History</div>

    <!-- History section -->
    <div class="sb-section">Recent</div>
    <div class="sb-history" id="historyList">
      {history_html}
    </div>

    <!-- ERP Login -->
    {erp_section}

    <!-- Back button -->
    <div class="sb-bottom">
      <div class="sb-back-btn" onclick="backToDashboard()">
        <span>←</span><span>Back to Dashboard</span>
      </div>
    </div>
  </aside>

  <!-- ═══ MAIN ═══ -->
  <div class="main-area">

    <!-- Topbar -->
    <div class="topbar">
      <div class="topbar-model">
        <span class="model-dot"></span>
        <span>AskMNIT AI &nbsp;·&nbsp; LLaMA 3.3 70B</span>
        <span style="opacity:0.5">▾</span>
      </div>
      <div class="topbar-actions">
        <div class="topbar-btn" onclick="toggleSettings(this)">⚙ Settings</div>
        <div class="topbar-btn" id="themeToggle" onclick="toggleTheme(this)">☀ Light</div>
      </div>
    </div>

    <!-- Chat scroll area -->
    <div class="chat-area" id="chatArea">
      {'<div id="heroSection">' if not has_messages else ''}
      {'<div class="hero-wrap"><div class="hero-orb">🎓</div><div class="hero-title">Hey ' + nm.split()[0] + ', ready?</div><div class="hero-sub">Your AI senior at MNIT Jaipur — attendance, schedule, PYQs, exam strategy, everything.</div><div class="pills-wrap" id="pillsWrap">' + pills_html + '</div></div>' if not has_messages else ''}
      {'</div>' if not has_messages else ''}

      <div id="msgContainer">
        {chat_html}
      </div>
    </div>

    <!-- Input zone -->
    <div class="input-zone {'hero-mode' if not has_messages else ''}" id="inputZone">
      <div id="attachChipArea"></div>

      <div class="search-bar" id="searchBar">
        <span class="bar-spark">✦</span>
        <textarea
          class="bar-input"
          id="barInput"
          rows="1"
          placeholder="Ask AskMNIT anything..."
          onkeydown="handleKey(event)"
          oninput="autoResize(this)"
        ></textarea>
        <div class="bar-actions">
          <div class="bar-icon-btn" id="attachBtn" title="Attach file" onclick="triggerFileInput()">📎</div>
          <div class="bar-icon-btn" id="micBtn" title="Voice input" onclick="toggleMic()">🎤</div>
          <div class="send-btn" onclick="sendMessage()" title="Send">↑</div>
        </div>
      </div>

      <div id="recordingBanner" style="display:none;" class="recording-banner">
        <div class="rec-dot"></div>
        <span>Listening... click mic again to stop</span>
      </div>

      <div class="bar-hint">AskMNIT can make mistakes · Verify with official ERP or faculty</div>
    </div>

  </div>
</div>

<script>
// ─── State ───
var isRecording = false;
var mediaRecorder = null;
var audioChunks = [];
var attachedFileName = {_attached_js};
var chatSessions = {_sessions_js};

// ─── Init ───
function init() {{
  updateAttachChip();
  scrollBottom();
  rotatePlaceholders();
  if ({str(has_messages).lower()}) {{
    var iz = document.getElementById('inputZone');
    if(iz) iz.classList.remove('hero-mode');
  }}
}}

// ─── Scroll ───
function scrollBottom() {{
  var ca = document.getElementById('chatArea');
  if(ca) setTimeout(function(){{ ca.scrollTop = ca.scrollHeight; }}, 60);
}}

// ─── Auto resize textarea ───
function autoResize(el) {{
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 160) + 'px';
}}

// ─── Send message ───
function sendMessage() {{
  var inp = document.getElementById('barInput');
  var text = (inp.value || '').trim();
  if (!text && !attachedFileName) return;

  var full = text;
  if (attachedFileName && !text) full = '[File attached: ' + attachedFileName + ']';
  else if (attachedFileName && text) full = text + ' [File: ' + attachedFileName + ']';

  // Append user bubble immediately
  appendMsg('user', full);
  inp.value = ''; inp.style.height = 'auto';
  attachedFileName = '';
  updateAttachChip();

  // Hide hero
  var hero = document.getElementById('heroSection');
  if(hero) {{ hero.style.display = 'none'; }}
  var iz = document.getElementById('inputZone');
  if(iz) iz.classList.remove('hero-mode');

  // Show typing indicator
  showTyping();
  scrollBottom();

  // Submit to Streamlit via query params
  var url = new URL(window.parent.location.href);
  url.searchParams.set('_chat_msg', encodeURIComponent(full));
  url.searchParams.set('_chat_ts', Date.now());
  window.parent.history.replaceState(null,'',url.toString());
  setTimeout(function(){{ window.parent.location.href = url.toString(); }}, 80);
}}

function handleKey(e) {{
  if (e.key === 'Enter' && !e.shiftKey) {{
    e.preventDefault();
    sendMessage();
  }}
}}

// ─── Append message ───
function appendMsg(role, text) {{
  var mc = document.getElementById('msgContainer');
  var row = document.createElement('div');
  row.className = 'msg-row ' + (role==='user' ? 'user-row' : 'ai-row');
  var avTxt = role==='user' ? {_initials_js} : 'A';
  var avClass = role==='user' ? 'user-avatar' : 'ai-avatar';
  var bubClass = role==='user' ? 'user-bubble' : 'ai-bubble';
  var safeText = text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\\n/g,'<br>');
  if(role==='user') {{
    row.innerHTML = '<div class="msg-bubble '+bubClass+'">'+safeText+'</div><div class="msg-avatar '+avClass+'">'+avTxt+'</div>';
  }} else {{
    row.innerHTML = '<div class="msg-avatar '+avClass+'">'+avTxt+'</div><div class="msg-bubble '+bubClass+'">'+safeText+'</div>';
  }}
  mc.appendChild(row);
  scrollBottom();
}}

// ─── Typing indicator ───
function showTyping() {{
  var mc = document.getElementById('msgContainer');
  var row = document.createElement('div');
  row.id = 'typingRow';
  row.className = 'typing-row';
  row.innerHTML = '<div class="msg-avatar ai-avatar">A</div><div class="typing-bubble"><div class="typing-dots"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div></div>';
  mc.appendChild(row);
  scrollBottom();
}}
function hideTyping() {{
  var t = document.getElementById('typingRow');
  if(t) t.remove();
}}

// ─── Pill click ───
function sendPill(btn) {{
  var text = btn.innerText;
  document.getElementById('barInput').value = text;
  sendMessage();
}}

// ─── Mic toggle ───
function toggleMic() {{
  if (!isRecording) {{
    startRecording();
  }} else {{
    stopRecording();
  }}
}}

function startRecording() {{
  navigator.mediaDevices.getUserMedia({{audio:true}}).then(function(stream) {{
    audioChunks = [];
    try {{ mediaRecorder = new MediaRecorder(stream, {{mimeType:'audio/webm'}}); }}
    catch(e) {{ mediaRecorder = new MediaRecorder(stream); }}
    mediaRecorder.ondataavailable = function(e) {{ if(e.data && e.data.size>0) audioChunks.push(e.data); }};
    mediaRecorder.onstop = function() {{
      stream.getTracks().forEach(function(t){{t.stop();}});
      // Simulate voice transcript
      var inp = document.getElementById('barInput');
      inp.value = '[Voice message recorded]';
      autoResize(inp);
    }};
    mediaRecorder.start(200);
    isRecording = true;
    var btn = document.getElementById('micBtn');
    btn.classList.add('active');
    btn.innerText = '⏹';
    document.getElementById('recordingBanner').style.display = 'flex';
  }}).catch(function(err) {{
    alert('Microphone access denied: ' + err.message);
  }});
}}

function stopRecording() {{
  if(mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop();
  isRecording = false;
  var btn = document.getElementById('micBtn');
  btn.classList.remove('active');
  btn.innerText = '🎤';
  document.getElementById('recordingBanner').style.display = 'none';
}}

// ─── File attach ───
function triggerFileInput() {{
  document.getElementById('realFileInput').click();
}}
function handleFileSelect(input) {{
  if(!input.files || !input.files[0]) return;
  attachedFileName = input.files[0].name;
  updateAttachChip();
  // Also persist to Streamlit via query param
  var url = new URL(window.parent.location.href);
  url.searchParams.set('_attach_file', encodeURIComponent(attachedFileName));
  window.parent.history.replaceState(null,'',url.toString());
}}
function updateAttachChip() {{
  var area = document.getElementById('attachChipArea');
  if(!area) return;
  if(attachedFileName) {{
    var short = attachedFileName.length > 22 ? attachedFileName.substring(0,19)+'...' : attachedFileName;
    area.innerHTML = '<div class="attach-chip">📎 '+short+'<span class="chip-x" onclick="clearAttach()">✕</span></div>';
  }} else {{
    area.innerHTML = '';
  }}
}}
function clearAttach() {{
  attachedFileName = '';
  updateAttachChip();
  document.getElementById('realFileInput').value = '';
}}

// ─── New chat ───
function newChat() {{
  var url = new URL(window.parent.location.href);
  url.searchParams.set('_new_chat', Date.now());
  window.parent.location.href = url.toString();
}}

// ─── Load session ───
function loadSession(idx) {{
  var url = new URL(window.parent.location.href);
  url.searchParams.set('_load_session', idx);
  window.parent.location.href = url.toString();
}}

// ─── Back to dashboard ───
function backToDashboard() {{
  var url = new URL(window.parent.location.href);
  url.searchParams.set('_back_dash', '1');
  window.parent.location.href = url.toString();
}}

// ─── Open history panel (scrolls to history) ───
function openHistoryPanel() {{
  var hl = document.getElementById('historyList');
  if(hl) hl.scrollIntoView({{behavior:'smooth'}});
}}

// ─── ERP login ───
function erpLogin() {{
  window.open('https://erp.mnit.ac.in/', '_blank');
}}

// ─── Nav active ───
function setNav(el) {{
  document.querySelectorAll('.sb-nav-item').forEach(function(i){{i.classList.remove('active');}});
  el.classList.add('active');
}}

// ─── Toggle theme ───
function toggleTheme(btn) {{
  var root = document.documentElement;
  if(btn.innerText.includes('Light')) {{
    root.style.setProperty('--bg','#F0F4FF');
    root.style.setProperty('--bg2','#E8EDFF');
    root.style.setProperty('--bg3','#DDE4FF');
    root.style.setProperty('--sidebar','#EBF0FF');
    root.style.setProperty('--text','#1E2A3A');
    root.style.setProperty('--text2','rgba(40,50,100,0.65)');
    root.style.setProperty('--text3','rgba(80,90,160,0.45)');
    document.querySelector('.bg-canvas').style.background = 'var(--bg)';
    btn.innerText = '🌙 Dark';
  }} else {{
    root.style.setProperty('--bg','#08080F');
    root.style.setProperty('--bg2','#0D0D1A');
    root.style.setProperty('--bg3','#12121F');
    root.style.setProperty('--sidebar','#0A0A16');
    root.style.setProperty('--text','#F1F0FF');
    root.style.setProperty('--text2','rgba(200,195,240,0.65)');
    root.style.setProperty('--text3','rgba(150,140,200,0.42)');
    btn.innerText = '☀ Light';
  }}
}}

// ─── Toggle settings ───
function toggleSettings(btn) {{
  btn.classList.toggle('active');
}}

// ─── Rotating placeholder ───
var placeholders = [
  "Ask AskMNIT anything...",
  "Check my attendance %...",
  "What's my next class?",
  "Give me PYQs for " + {_branch_js} + "...",
  "Exam strategy for this sem?",
  "Is my attendance safe?",
  "Explain " + {_branch_js} + " topics...",
];
var pidx = 0;
function rotatePlaceholders() {{
  var inp = document.getElementById('barInput');
  if(!inp || document.activeElement === inp) {{
    setTimeout(rotatePlaceholders, 2800);
    return;
  }}
  pidx = (pidx+1) % placeholders.length;
  inp.style.transition = 'opacity 0.30s';
  inp.style.opacity = '0';
  setTimeout(function() {{
    inp.setAttribute('placeholder', placeholders[pidx]);
    inp.style.opacity = '1';
  }}, 300);
  setTimeout(rotatePlaceholders, 2800);
}}

init();
scrollBottom();
</script>
</body>
</html>
"""

    # Render the HTML chatbot
    components.html(CHAT_HTML, height=700, scrolling=False)

    # ── Handle query param actions from the HTML ────────────────────────
    qp = st.query_params

    # Back to dashboard
    if qp.get("_back_dash"):
        try: del st.query_params["_back_dash"]
        except: pass
        st.session_state.view = "dashboard"
        st.rerun()

    # New chat
    if qp.get("_new_chat"):
        try: del st.query_params["_new_chat"]
        except: pass
        if st.session_state.chat_messages:
            fu = next((m["content"][:38] for m in st.session_state.chat_messages if m["role"]=="user"), "Session")
            st.session_state.chat_sessions.append({"label": fu, "messages": list(st.session_state.chat_messages)})
        st.session_state.chat_messages = []
        st.session_state.attached_file_name = ""
        st.rerun()

    # Load session
    if qp.get("_load_session"):
        try:
            idx = int(qp.get("_load_session"))
            del st.query_params["_load_session"]
            st.session_state.chat_messages = list(st.session_state.chat_sessions[idx]["messages"])
            st.rerun()
        except: pass

    # File attach
    if qp.get("_attach_file"):
        fname = qp.get("_attach_file","")
        try: del st.query_params["_attach_file"]
        except: pass
        if fname:
            st.session_state.attached_file_name = fname
            st.rerun()

    # Chat message
    chat_msg = qp.get("_chat_msg","")
    if chat_msg:
        try: del st.query_params["_chat_msg"]
        except: pass
        try: del st.query_params["_chat_ts"]
        except: pass
        dispatch_message(chat_msg)
        st.rerun()

    st.stop()


###############################################################################
# DASHBOARD VIEW  (completely unchanged from original)
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
# MY DASHBOARD  (completely unchanged from original)
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
    ql_fb = st.session_state.get("ql_feedback","")
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

st.markdown('<div style="text-align:center;margin-top:28px;padding:10px 0;border-top:1px solid rgba(255,255,255,0.05);"><span style="font-family:\'DM Mono\',monospace;font-size:0.52rem;color:rgba(148,163,184,0.24);letter-spacing:1.2px;">ASKMNT &nbsp;·&nbsp; MNIT JAIPUR &nbsp;·&nbsp; v7.0 PREMIUM</span></div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
