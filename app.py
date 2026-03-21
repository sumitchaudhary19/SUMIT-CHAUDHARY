# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  AskMNIT — v7.0 PREMIUM CHATBOT REDESIGN                                    ║
# ║  New chatbot UI: sidebar, premium bg, modern search bar, suggestions         ║
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
    "response_style":    "Concise",
    "attached_file_name":"",
    "voice_transcript":  "",
    "_voice_submit":     False,
    "chat_sidebar_open": True,
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
html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"]{font-family:'Outfit',sans-serif!important;background:#070B14!important;color:#E2E8F0!important;}
header[data-testid="stHeader"],footer,#MainMenu,[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important;}
[data-testid="stMainBlockContainer"]{padding:0!important;max-width:100%!important;}

/* Dashboard sidebar */
[data-testid="stSidebar"]{background:#0B1120!important;border-right:1px solid rgba(59,130,246,0.16)!important;min-width:260px!important;max-width:260px!important;}
[data-testid="stSidebar"]>div{padding:0!important;}
.sb-section-header{font-family:'DM Mono',monospace;font-size:0.60rem;font-weight:700;color:rgba(148,163,184,0.50);text-transform:uppercase;letter-spacing:1.4px;padding:14px 16px 6px;border-top:1px solid rgba(255,255,255,0.05);margin-top:4px;}
[data-testid="stSidebar"] .stButton>button{background:rgba(239,68,68,0.10)!important;border:1px solid rgba(239,68,68,0.28)!important;color:#FCA5A5!important;border-radius:8px!important;font-size:0.80rem!important;font-weight:600!important;padding:7px 14px!important;box-shadow:none!important;}
[data-testid="stSidebar"] .stButton>button:hover{background:rgba(239,68,68,0.20)!important;transform:none!important;}

/* ── Global buttons ── */
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
@keyframes fadeUp{from{opacity:0;transform:translateY(18px);}to{opacity:1;transform:translateY(0);}}
@keyframes slideUp{from{opacity:0;transform:translateY(24px);}to{opacity:1;transform:translateY(0);}}
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# VIEW ROUTER
# ═════════════════════════════════════════════════════════════════════════════
view = st.session_state.view

###############################################################################
# ███████████████████████  CHAT VIEW — PREMIUM REDESIGN  ██████████████████████
###############################################################################
if view == "chat":

    # Hide all Streamlit chrome & sidebar
    st.markdown("""
    <style>
    [data-testid="stSidebar"]{display:none!important;}
    [data-testid="stSidebarCollapseButton"]{display:none!important;}
    [data-testid="collapsedControl"]{display:none!important;}
    section[data-testid="stMain"]{margin-left:0!important;padding-left:0!important;}
    [data-testid="stMainBlockContainer"]{padding:0!important;}
    /* Hide spinner text */
    [data-testid="stStatusWidget"]{display:none!important;}
    </style>
    """, unsafe_allow_html=True)

    # ── Voice done handler ────────────────────────────────────────────────
    for rkey in ["chat_bar"]:
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
        st.rerun()

    has_messages = len(st.session_state.chat_messages) > 0

    # ─────────────────────────────────────────────────────────────────────
    # FULL PAGE PREMIUM CHAT HTML SHELL
    # ─────────────────────────────────────────────────────────────────────
    nm = st.session_state.student_name
    br = st.session_state.branch
    bh = branch_hex(br)

    # Build session history HTML for sidebar
    sessions_html = ""
    if st.session_state.chat_sessions:
        for i, sess in enumerate(reversed(st.session_state.chat_sessions[-12:])):
            lbl = sess.get("label", "Chat")[:32]
            sessions_html += f'<div class="hist-item" data-idx="{i}"><span class="hist-icon">💬</span><span class="hist-label">{lbl}...</span></div>'
    else:
        sessions_html = '<div class="hist-empty">No saved chats yet</div>'

    # Build messages HTML
    msgs_html = ""
    for msg in st.session_state.chat_messages:
        role = msg["role"]
        content = msg["content"].replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        if role == "user":
            msgs_html += f'''
            <div class="msg-row msg-user">
              <div class="msg-bubble msg-bubble-user">{content}</div>
              <div class="msg-avatar msg-avatar-user">{initials(nm)}</div>
            </div>'''
        else:
            msgs_html += f'''
            <div class="msg-row msg-ai">
              <div class="msg-avatar msg-avatar-ai">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M12 2L13.5 8.5L20 10L13.5 11.5L12 18L10.5 11.5L4 10L10.5 8.5L12 2Z" fill="url(#star-grad)"/><defs><linearGradient id="star-grad" x1="4" y1="2" x2="20" y2="18"><stop stop-color="#818CF8"/><stop offset="1" stop-color="#22D3EE"/></linearGradient></defs></svg>
              </div>
              <div class="msg-bubble msg-bubble-ai">{content}</div>
            </div>'''

    chip_html = ""
    if st.session_state.attached_file_name:
        fname = st.session_state.attached_file_name
        short = fname if len(fname) <= 20 else fname[:17] + "..."
        chip_html = f'<div class="attach-chip">📎 {short} <span class="chip-close" onclick="clearAttach()">✕</span></div>'

    recording_class = "recording" if st.session_state.is_recording else ""

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@400;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── RESET & ROOT ── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

/* ── CHAT APP WRAPPER ── */
#askmnt-chat-app {{
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  display: flex;
  font-family: 'Space Grotesk', sans-serif;
  overflow: hidden;
  background: #050810;
  z-index: 9999;
}}

/* ══════════ ANIMATED BACKGROUND ══════════ */
.chat-bg {{
  position: fixed;
  inset: 0;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;
}}
.chat-bg::before {{
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 80% 60% at 20% 10%, rgba(99,102,241,0.18) 0%, transparent 60%),
              radial-gradient(ellipse 60% 50% at 80% 80%, rgba(34,211,238,0.12) 0%, transparent 55%),
              radial-gradient(ellipse 50% 40% at 50% 50%, rgba(139,92,246,0.06) 0%, transparent 70%);
  animation: bgPulse 8s ease-in-out infinite alternate;
}}
@keyframes bgPulse {{
  0% {{ opacity: 0.7; transform: scale(1); }}
  100% {{ opacity: 1; transform: scale(1.04); }}
}}
.orb {{
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  animation: orbFloat linear infinite;
  opacity: 0;
}}
.orb-1 {{
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(99,102,241,0.22) 0%, transparent 70%);
  top: -150px; left: -100px;
  animation-duration: 25s; animation-delay: 0s;
  animation-name: orbFloat1;
}}
.orb-2 {{
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(34,211,238,0.16) 0%, transparent 70%);
  bottom: -100px; right: -80px;
  animation-duration: 20s; animation-delay: -8s;
  animation-name: orbFloat2;
}}
.orb-3 {{
  width: 300px; height: 300px;
  background: radial-gradient(circle, rgba(167,139,250,0.14) 0%, transparent 70%);
  top: 50%; left: 60%;
  animation-duration: 30s; animation-delay: -15s;
  animation-name: orbFloat3;
}}
@keyframes orbFloat1 {{
  0%,100% {{ opacity: 0.6; transform: translate(0,0); }}
  33% {{ opacity: 1; transform: translate(60px, 40px); }}
  66% {{ opacity: 0.7; transform: translate(-30px, 80px); }}
}}
@keyframes orbFloat2 {{
  0%,100% {{ opacity: 0.5; transform: translate(0,0); }}
  50% {{ opacity: 0.9; transform: translate(-50px, -60px); }}
}}
@keyframes orbFloat3 {{
  0%,100% {{ opacity: 0.4; transform: translate(0,0) rotate(0deg); }}
  50% {{ opacity: 0.7; transform: translate(-80px, 40px) rotate(180deg); }}
}}

/* Grid overlay */
.chat-bg-grid {{
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(99,102,241,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(99,102,241,0.04) 1px, transparent 1px);
  background-size: 60px 60px;
  mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black 30%, transparent 100%);
}}

/* ══════════ LEFT SIDEBAR ══════════ */
.chat-sidebar {{
  position: relative;
  z-index: 10;
  width: 260px;
  min-width: 260px;
  height: 100vh;
  background: rgba(8, 12, 28, 0.92);
  border-right: 1px solid rgba(99,102,241,0.18);
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(24px);
  transition: transform 0.3s cubic-bezier(0.22,0.61,0.36,1);
  overflow: hidden;
}}

/* Sidebar brand */
.sb-brand {{
  padding: 20px 18px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  display: flex;
  align-items: center;
  gap: 11px;
}}
.sb-brand-icon {{
  width: 36px; height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #4F46E5, #818CF8);
  display: flex; align-items: center; justify-content: center;
  font-family: 'Syne', sans-serif;
  font-size: 0.95rem; font-weight: 800;
  color: #fff;
  box-shadow: 0 4px 16px rgba(79,70,229,0.40);
  flex-shrink: 0;
}}
.sb-brand-text {{ display: flex; flex-direction: column; }}
.sb-brand-name {{
  font-family: 'Syne', sans-serif;
  font-size: 0.92rem; font-weight: 700;
  color: #E2E8F0; letter-spacing: -0.3px;
}}
.sb-brand-sub {{
  font-size: 0.58rem;
  color: rgba(148,163,184,0.45);
  letter-spacing: 0.8px;
  text-transform: uppercase;
  margin-top: 1px;
}}

/* Sidebar sections */
.sb-section {{
  padding: 14px 12px 8px;
}}
.sb-section-title {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.56rem; font-weight: 500;
  color: rgba(148,163,184,0.35);
  text-transform: uppercase; letter-spacing: 1.6px;
  padding: 0 6px 8px;
}}

/* Sidebar action buttons */
.sb-action-btn {{
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
  margin-bottom: 3px;
  transition: all 0.18s ease;
  border: 1px solid transparent;
  text-decoration: none;
}}
.sb-action-btn:hover {{
  background: rgba(99,102,241,0.10);
  border-color: rgba(99,102,241,0.22);
}}
.sb-action-icon {{
  width: 28px; height: 28px;
  border-radius: 7px;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.85rem;
  flex-shrink: 0;
}}
.sb-action-label {{
  font-size: 0.82rem; font-weight: 500;
  color: rgba(226,232,240,0.75);
}}
.sb-action-btn.new-chat {{ background: rgba(99,102,241,0.08); border-color: rgba(99,102,241,0.20); }}
.sb-action-btn.new-chat:hover {{ background: rgba(99,102,241,0.18); }}
.sb-action-btn.new-chat .sb-action-icon {{ background: rgba(99,102,241,0.20); color: #818CF8; }}
.sb-action-btn.new-chat .sb-action-label {{ color: #A5B4FC; font-weight: 600; }}
.sb-action-btn.erp .sb-action-icon {{ background: rgba(34,211,238,0.12); color: #22D3EE; }}
.sb-action-btn.dashboard-btn .sb-action-icon {{ background: rgba(16,185,129,0.12); color: #10B981; }}

/* History list */
.hist-scroll {{
  flex: 1;
  overflow-y: auto;
  padding: 0 12px 12px;
}}
.hist-scroll::-webkit-scrollbar {{ width: 3px; }}
.hist-scroll::-webkit-scrollbar-thumb {{ background: rgba(99,102,241,0.25); border-radius: 3px; }}
.hist-item {{
  display: flex; align-items: center; gap: 9px;
  padding: 9px 10px;
  border-radius: 9px;
  margin-bottom: 2px;
  cursor: pointer;
  transition: background 0.15s;
  border: 1px solid transparent;
}}
.hist-item:hover {{
  background: rgba(255,255,255,0.04);
  border-color: rgba(255,255,255,0.07);
}}
.hist-icon {{ font-size: 0.78rem; opacity: 0.5; flex-shrink: 0; }}
.hist-label {{
  font-size: 0.76rem; color: rgba(148,163,184,0.60);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}}
.hist-empty {{
  font-size: 0.72rem; color: rgba(148,163,184,0.28);
  text-align: center; padding: 24px 0;
  font-style: italic;
}}

/* Sidebar footer */
.sb-footer {{
  padding: 12px 14px;
  border-top: 1px solid rgba(255,255,255,0.05);
}}
.sb-user-chip {{
  display: flex; align-items: center; gap: 10px;
  padding: 8px 10px;
  border-radius: 10px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07);
}}
.sb-user-av {{
  width: 28px; height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, {bh}, {bh}88);
  display: flex; align-items: center; justify-content: center;
  font-size: 0.68rem; font-weight: 700; color: #fff;
  flex-shrink: 0;
}}
.sb-user-name {{
  font-size: 0.76rem; font-weight: 600; color: rgba(226,232,240,0.80);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}}
.sb-user-branch {{
  font-size: 0.58rem; color: {bh}; font-weight: 600;
}}

/* ══════════ MAIN CHAT AREA ══════════ */
.chat-main {{
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 5;
  overflow: hidden;
}}

/* ── Top bar ── */
.chat-topbar {{
  height: 54px;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  background: rgba(5,8,16,0.60);
  backdrop-filter: blur(20px);
  flex-shrink: 0;
}}
.topbar-left {{
  display: flex; align-items: center; gap: 10px;
}}
.topbar-model-badge {{
  display: flex; align-items: center; gap: 6px;
  padding: 5px 12px;
  background: rgba(99,102,241,0.10);
  border: 1px solid rgba(99,102,241,0.22);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.18s;
}}
.topbar-model-badge:hover {{ background: rgba(99,102,241,0.18); }}
.topbar-model-dot {{
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #818CF8;
  animation: blink 2s ease infinite;
}}
@keyframes blink {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.3; }} }}
.topbar-model-name {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem; color: #A5B4FC; font-weight: 500;
}}
.topbar-right {{
  display: flex; align-items: center; gap: 8px;
}}
.topbar-pill {{
  padding: 5px 14px;
  border-radius: 20px;
  font-size: 0.72rem; font-weight: 500;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(255,255,255,0.05);
  color: rgba(226,232,240,0.65);
  cursor: pointer;
  transition: all 0.18s;
  white-space: nowrap;
}}
.topbar-pill:hover {{
  background: rgba(99,102,241,0.15);
  border-color: rgba(99,102,241,0.35);
  color: #BAE6FD;
}}

/* ── Messages area ── */
.chat-messages {{
  flex: 1;
  overflow-y: auto;
  padding: 24px 0;
  scroll-behavior: smooth;
}}
.chat-messages::-webkit-scrollbar {{ width: 4px; }}
.chat-messages::-webkit-scrollbar-thumb {{ background: rgba(99,102,241,0.20); border-radius: 4px; }}

.msgs-inner {{
  max-width: 760px;
  margin: 0 auto;
  padding: 0 24px;
}}

/* Message rows */
.msg-row {{
  display: flex;
  align-items: flex-end;
  gap: 10px;
  margin-bottom: 16px;
  animation: msgIn 0.3s cubic-bezier(0.22,0.61,0.36,1) both;
}}
@keyframes msgIn {{
  from {{ opacity: 0; transform: translateY(12px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}
.msg-row.msg-user {{ flex-direction: row-reverse; }}

/* Avatars */
.msg-avatar {{
  width: 30px; height: 30px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; font-size: 0.70rem; font-weight: 700;
}}
.msg-avatar-user {{
  background: linear-gradient(135deg, {bh}, {bh}88);
  color: #fff;
  border: 1.5px solid {bh}55;
}}
.msg-avatar-ai {{
  background: linear-gradient(135deg, #1e1b4b, #312e81);
  border: 1.5px solid rgba(99,102,241,0.35);
}}

/* Bubbles */
.msg-bubble {{
  max-width: 68%;
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 0.88rem;
  line-height: 1.65;
  word-wrap: break-word;
}}
.msg-bubble-user {{
  background: linear-gradient(135deg, #3730a3, #4338ca);
  color: #e0e7ff;
  border-radius: 18px 18px 4px 18px;
  border: 1px solid rgba(99,102,241,0.40);
  box-shadow: 0 4px 20px rgba(67,56,202,0.30);
}}
.msg-bubble-ai {{
  background: rgba(255,255,255,0.04);
  color: rgba(226,232,240,0.90);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 18px 18px 18px 4px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.20);
}}

/* ══════════ HERO (empty state) ══════════ */
.chat-hero {{
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0 24px 40px;
}}
.hero-orb {{
  width: 90px; height: 90px;
  border-radius: 50%;
  margin-bottom: 28px;
  position: relative;
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4338ca 70%, #6366f1 100%);
  box-shadow:
    0 0 0 1px rgba(99,102,241,0.30),
    0 0 40px rgba(99,102,241,0.35),
    0 0 80px rgba(99,102,241,0.15);
  display: flex; align-items: center; justify-content: center;
  animation: heroOrbPulse 3s ease-in-out infinite;
}}
@keyframes heroOrbPulse {{
  0%,100% {{ box-shadow: 0 0 0 1px rgba(99,102,241,0.30), 0 0 40px rgba(99,102,241,0.35), 0 0 80px rgba(99,102,241,0.15); transform: scale(1); }}
  50% {{ box-shadow: 0 0 0 2px rgba(99,102,241,0.50), 0 0 60px rgba(99,102,241,0.50), 0 0 120px rgba(99,102,241,0.20); transform: scale(1.04); }}
}}
.hero-orb-inner {{
  font-size: 2.4rem;
  filter: drop-shadow(0 2px 8px rgba(129,140,248,0.6));
}}
.hero-title {{
  font-family: 'Syne', sans-serif;
  font-size: 2.8rem; font-weight: 800;
  color: #F1F5F9;
  letter-spacing: -1.5px;
  text-align: center;
  line-height: 1.1;
  margin-bottom: 10px;
}}
.hero-title span {{
  background: linear-gradient(90deg, #818CF8, #22D3EE);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}}
.hero-subtitle {{
  font-size: 0.86rem;
  color: rgba(148,163,184,0.55);
  text-align: center;
  line-height: 1.7;
  margin-bottom: 40px;
  max-width: 400px;
}}

/* Suggestion pills */
.suggestions {{
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  max-width: 600px;
  margin-bottom: 44px;
}}
.sug-pill {{
  padding: 9px 18px;
  border-radius: 999px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.10);
  color: rgba(186,230,253,0.72);
  font-size: 0.80rem; font-weight: 500;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.22,0.61,0.36,1);
  white-space: nowrap;
  user-select: none;
  display: flex; align-items: center; gap: 6px;
}}
.sug-pill:hover {{
  background: rgba(99,102,241,0.14);
  border-color: rgba(99,102,241,0.36);
  color: #BAE6FD;
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(99,102,241,0.18);
}}

/* ══════════ INPUT BAR ══════════ */
.chat-input-zone {{
  flex-shrink: 0;
  padding: 12px 24px 18px;
  background: rgba(5,8,16,0.70);
  backdrop-filter: blur(24px);
  border-top: 1px solid rgba(255,255,255,0.05);
}}
.chat-input-zone.hero-mode {{
  background: transparent;
  border-top: none;
  padding: 0 24px 8px;
}}
.chat-input-inner {{
  max-width: 720px;
  margin: 0 auto;
}}
.attach-chip-row {{
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 8px; padding: 0 4px;
}}
.attach-chip {{
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 12px 4px 10px;
  background: rgba(99,102,241,0.14);
  border: 1px solid rgba(99,102,241,0.32);
  border-radius: 20px;
  font-size: 0.73rem; color: #A5B4FC; font-weight: 600;
  max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}}
.chip-close {{
  cursor: pointer; opacity: 0.6; margin-left: 2px; font-size: 0.7rem;
}}
.chip-close:hover {{ opacity: 1; }}

/* The input bar box */
.input-bar {{
  display: flex; align-items: center;
  background: rgba(14, 17, 35, 0.85);
  border: 1.5px solid rgba(99,102,241,0.22);
  border-radius: 20px;
  padding: 6px 8px 6px 16px;
  gap: 8px;
  transition: border-color 0.22s, box-shadow 0.22s;
  box-shadow: 0 4px 32px rgba(0,0,0,0.40), 0 0 0 1px rgba(99,102,241,0.08);
  animation: barIdle 5s ease-in-out infinite;
}}
@keyframes barIdle {{
  0%,100% {{ box-shadow: 0 4px 32px rgba(0,0,0,0.40), 0 0 0 1px rgba(99,102,241,0.08); }}
  50%      {{ box-shadow: 0 4px 32px rgba(0,0,0,0.40), 0 0 0 1px rgba(99,102,241,0.16), 0 0 28px rgba(99,102,241,0.10); }}
}}
.input-bar:focus-within {{
  border-color: rgba(99,102,241,0.55);
  box-shadow: 0 0 0 3px rgba(99,102,241,0.12), 0 8px 40px rgba(67,56,202,0.20);
  animation: none;
}}
.input-bar input {{
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #E2E8F0;
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.93rem;
  padding: 10px 4px;
  min-height: 44px;
  caret-color: #818CF8;
}}
.input-bar input::placeholder {{
  color: rgba(148,163,184,0.35);
  animation: phShimmer 3.5s ease-in-out infinite;
}}
@keyframes phShimmer {{
  0%,100% {{ opacity: 0.35; }}
  50% {{ opacity: 0.65; }}
}}

/* Input action buttons */
.input-btn {{
  width: 36px; height: 36px;
  border-radius: 50%;
  border: none; outline: none;
  background: transparent;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.18s;
  font-size: 1.0rem;
  color: rgba(148,163,184,0.55);
  flex-shrink: 0;
}}
.input-btn:hover {{
  background: rgba(255,255,255,0.08);
  color: rgba(186,230,253,0.85);
}}
.input-btn.mic-btn {{
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.09);
}}
.input-btn.mic-btn.recording {{
  background: rgba(239,68,68,0.18);
  border-color: rgba(239,68,68,0.45);
  color: #FCA5A5;
  animation: micPulse 1.1s ease-in-out infinite;
}}
@keyframes micPulse {{
  0%,100% {{ box-shadow: 0 0 0 0 rgba(239,68,68,0.40); }}
  50% {{ box-shadow: 0 0 0 7px rgba(239,68,68,0.00); }}
}}
.send-btn {{
  width: 38px; height: 38px;
  border-radius: 50%;
  border: none; outline: none;
  background: linear-gradient(135deg, #4338CA, #6366F1);
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  color: #fff;
  font-size: 1.15rem;
  font-weight: 700;
  transition: all 0.18s;
  box-shadow: 0 3px 14px rgba(67,56,202,0.40);
  flex-shrink: 0;
}}
.send-btn:hover {{
  opacity: 0.88;
  transform: scale(1.08);
}}
.input-divider {{
  width: 1px; height: 22px;
  background: rgba(255,255,255,0.08);
  flex-shrink: 0;
}}
.input-disclaimer {{
  text-align: center;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.55rem;
  color: rgba(100,116,139,0.32);
  margin-top: 8px;
  letter-spacing: 0.5px;
}}

/* Listening banner */
.listening-banner {{
  display: flex; align-items: center; gap: 8px;
  padding: 8px 16px;
  margin-bottom: 8px;
  background: rgba(239,68,68,0.08);
  border: 1px solid rgba(239,68,68,0.20);
  border-radius: 10px;
  font-size: 0.78rem; color: #FCA5A5;
}}
.listening-dot {{
  width: 7px; height: 7px; border-radius: 50%;
  background: #EF4444;
  animation: blinkDot 1s ease infinite;
}}
@keyframes blinkDot {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.2; }} }}

/* Thinking indicator */
.thinking {{
  display: flex; align-items: center; gap: 10px;
  padding: 12px 16px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 18px 18px 18px 4px;
  max-width: 120px;
  margin-bottom: 16px;
}}
.thinking-dot {{
  width: 7px; height: 7px; border-radius: 50%;
  background: #818CF8;
  animation: thinkBounce 1.4s ease-in-out infinite;
}}
.thinking-dot:nth-child(2) {{ animation-delay: 0.2s; }}
.thinking-dot:nth-child(3) {{ animation-delay: 0.4s; }}
@keyframes thinkBounce {{
  0%,80%,100% {{ transform: translateY(0); opacity: 0.4; }}
  40% {{ transform: translateY(-6px); opacity: 1; }}
}}

/* File uploader overlay */
.file-overlay {{
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(5,8,16,0.80);
  display: flex; align-items: center; justify-content: center;
  backdrop-filter: blur(8px);
}}
.file-overlay-box {{
  background: rgba(14,17,35,0.95);
  border: 1.5px solid rgba(99,102,241,0.32);
  border-radius: 20px;
  padding: 32px 36px;
  width: 380px;
  text-align: center;
}}
.file-overlay-title {{
  font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700;
  color: #E2E8F0; margin-bottom: 6px;
}}
.file-overlay-sub {{
  font-size: 0.76rem; color: rgba(148,163,184,0.50);
  margin-bottom: 20px;
}}

/* Scrollbar */
.chat-messages::-webkit-scrollbar {{ width: 4px; }}
.chat-messages::-webkit-scrollbar-track {{ background: transparent; }}
.chat-messages::-webkit-scrollbar-thumb {{ background: rgba(99,102,241,0.20); border-radius: 4px; }}

/* Animations */
.chat-hero {{ animation: fadeUp 0.5s cubic-bezier(0.22,0.61,0.36,1) both; }}
@keyframes fadeUp {{ from {{ opacity:0; transform:translateY(20px); }} to {{ opacity:1; transform:translateY(0); }} }}
</style>

<div id="askmnt-chat-app">
  <!-- ANIMATED BG -->
  <div class="chat-bg">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
    <div class="chat-bg-grid"></div>
  </div>

  <!-- LEFT SIDEBAR -->
  <div class="chat-sidebar" id="chatSidebar">
    <div class="sb-brand">
      <div class="sb-brand-icon">A</div>
      <div class="sb-brand-text">
        <div class="sb-brand-name">AskMNIT</div>
        <div class="sb-brand-sub">AI Assistant</div>
      </div>
    </div>

    <div class="sb-section">
      <div class="sb-section-title">Actions</div>
      <div class="sb-action-btn new-chat" onclick="handleSbAction('new_chat')">
        <div class="sb-action-icon">✦</div>
        <span class="sb-action-label">New Chat</span>
      </div>
      <div class="sb-action-btn erp" onclick="handleSbAction('erp')">
        <div class="sb-action-icon">🎓</div>
        <span class="sb-action-label">ERP Login</span>
      </div>
      <div class="sb-action-btn dashboard-btn" onclick="handleSbAction('dashboard')">
        <div class="sb-action-icon">⬡</div>
        <span class="sb-action-label">Back to Dashboard</span>
      </div>
    </div>

    <div class="sb-section" style="flex:1;display:flex;flex-direction:column;min-height:0;">
      <div class="sb-section-title">Chat History</div>
      <div class="hist-scroll">
        {sessions_html}
      </div>
    </div>

    <div class="sb-footer">
      <div class="sb-user-chip">
        <div class="sb-user-av">{initials(nm)}</div>
        <div>
          <div class="sb-user-name">{nm}</div>
          <div class="sb-user-branch">{br}</div>
        </div>
      </div>
    </div>
  </div>

  <!-- MAIN CHAT AREA -->
  <div class="chat-main">
    <!-- TOP BAR -->
    <div class="chat-topbar">
      <div class="topbar-left">
        <div class="topbar-model-badge">
          <div class="topbar-model-dot"></div>
          <span class="topbar-model-name">AskMNIT · Llama 3.3 70B</span>
        </div>
      </div>
      <div class="topbar-right">
        <div class="topbar-pill" onclick="handleTopbarAction('settings')">⚙ Settings</div>
        <div class="topbar-pill" onclick="handleTopbarAction('export')">↑ Export</div>
      </div>
    </div>

    <!-- MESSAGES OR HERO -->
    {'<!-- HERO STATE -->' if not has_messages else ''}
    <div id="chatBody" class="{'chat-hero' if not has_messages else 'chat-messages'}">
""", unsafe_allow_html=True)

    if not has_messages:
        # Hero state — rendered in HTML
        st.markdown(f"""
      <div class="hero-orb">
        <div class="hero-orb-inner">🤖</div>
      </div>
      <div class="hero-title">Ready to <span>Ask</span> Anything?</div>
      <div class="hero-subtitle">
        Your AI senior at MNIT Jaipur — attendance, schedule, PYQs, exam tips, sab kuch!
      </div>
      <div class="suggestions" id="sugPills">
        <div class="sug-pill" onclick="sendSuggestion('Meri attendance check karo')">📊 Attendance check karo</div>
        <div class="sug-pill" onclick="sendSuggestion('What is my next class today?')">📅 Next class kaunsi hai?</div>
        <div class="sug-pill" onclick="sendSuggestion('PYQs for {br} branch')">📄 PYQs dhundo</div>
        <div class="sug-pill" onclick="sendSuggestion('Exam preparation tips do')">🎯 Exam tips chahiye</div>
        <div class="sug-pill" onclick="sendSuggestion('Subjects for this semester?')">📚 Subjects list karo</div>
        <div class="sug-pill" onclick="sendSuggestion('Fee status check karo')">💳 Fee status</div>
      </div>
    </div>

    <!-- INPUT ZONE (hero mode) -->
    <div class="chat-input-zone hero-mode" id="inputZone">
      <div class="chat-input-inner">
        {'<div class="attach-chip-row">' + chip_html + '</div>' if chip_html else ''}
        {'<div class="listening-banner"><div class="listening-dot"></div><span>Listening... mic icon dabao stop karne ke liye</span></div>' if st.session_state.is_recording else ''}
        <div class="input-bar" id="mainInputBar">
          <button class="input-btn" title="Attach file" onclick="triggerAttach()">＋</button>
          <div class="input-divider"></div>
          <input type="text" id="chatInput" placeholder="Ask AskMNIT anything..." autocomplete="off" onkeydown="handleInputKey(event)"/>
          <button class="input-btn mic-btn {'recording' if st.session_state.is_recording else ''}" id="micBtn" title="Voice input" onclick="toggleMic()">{'⏹' if st.session_state.is_recording else '🎤'}</button>
          <button class="send-btn" title="Send" onclick="sendMessage()">↑</button>
        </div>
        <div class="input-disclaimer">AskMNIT AI · MNIT Jaipur · Verify important info with ERP</div>
      </div>
    </div>
""", unsafe_allow_html=True)

    else:
        # Active chat — messages + anchored bar
        st.markdown(f"""
      <div class="msgs-inner" id="msgsInner">
        {msgs_html}
        <div id="msgAnchor"></div>
      </div>
    </div>

    <!-- INPUT ZONE (anchored) -->
    <div class="chat-input-zone" id="inputZone">
      <div class="chat-input-inner">
        {'<div class="attach-chip-row">' + chip_html + '</div>' if chip_html else ''}
        {'<div class="listening-banner"><div class="listening-dot"></div><span>Listening... mic icon dabao stop karne ke liye</span></div>' if st.session_state.is_recording else ''}
        <div class="input-bar" id="mainInputBar">
          <button class="input-btn" title="Attach file" onclick="triggerAttach()">＋</button>
          <div class="input-divider"></div>
          <input type="text" id="chatInput" placeholder="Message AskMNIT..." autocomplete="off" onkeydown="handleInputKey(event)"/>
          <button class="input-btn mic-btn {'recording' if st.session_state.is_recording else ''}" id="micBtn" title="Voice input" onclick="toggleMic()">{'⏹' if st.session_state.is_recording else '🎤'}</button>
          <button class="send-btn" title="Send" onclick="sendMessage()">↑</button>
        </div>
        <div class="input-disclaimer">AskMNIT AI · MNIT Jaipur · Verify important info with ERP</div>
      </div>
    </div>
""", unsafe_allow_html=True)

    # JavaScript + end of HTML
    st.markdown("""
  </div><!-- end chat-main -->
</div><!-- end askmnt-chat-app -->

<script>
// ── Scroll to bottom ──
(function() {
  var anchor = document.getElementById('msgAnchor');
  if (anchor) anchor.scrollIntoView({ behavior: 'smooth' });
  var msgs = document.querySelector('.chat-messages');
  if (msgs) msgs.scrollTop = msgs.scrollHeight;
})();

// ── Sidebar actions via query params ──
function handleSbAction(action) {
  var url = new URL(window.parent.location.href);
  url.searchParams.set('sb_action', action);
  url.searchParams.set('sb_ts', Date.now());
  window.parent.location.href = url.toString();
}
function handleTopbarAction(action) {
  var url = new URL(window.parent.location.href);
  url.searchParams.set('tb_action', action);
  url.searchParams.set('tb_ts', Date.now());
  window.parent.location.href = url.toString();
}

// ── Send message via query param ──
function sendMessage() {
  var inp = document.getElementById('chatInput');
  var txt = inp ? inp.value.trim() : '';
  if (!txt) return;
  var url = new URL(window.parent.location.href);
  url.searchParams.set('chat_msg', txt);
  url.searchParams.set('chat_ts', Date.now());
  window.parent.location.href = url.toString();
}
function handleInputKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
}
function sendSuggestion(txt) {
  var url = new URL(window.parent.location.href);
  url.searchParams.set('chat_msg', txt);
  url.searchParams.set('chat_ts', Date.now());
  window.parent.location.href = url.toString();
}

// ── Attach file ──
function triggerAttach() {
  var inp = document.createElement('input');
  inp.type = 'file';
  inp.accept = '.pdf,.txt,.png,.jpg,.jpeg,.docx,.csv';
  inp.onchange = function() {
    if (!inp.files || !inp.files[0]) return;
    var url = new URL(window.parent.location.href);
    url.searchParams.set('attach_file', inp.files[0].name);
    url.searchParams.set('attach_ts', Date.now());
    window.parent.location.href = url.toString();
  };
  inp.click();
}
function clearAttach() {
  var url = new URL(window.parent.location.href);
  url.searchParams.delete('attach_file');
  window.parent.location.href = url.toString();
}

// ── Mic toggle ──
function toggleMic() {
  var url = new URL(window.parent.location.href);
  url.searchParams.set('mic_toggle', Date.now());
  window.parent.location.href = url.toString();
}

// ── Rotating placeholder ──
var hints = [
  "Ask AskMNIT anything...",
  "Attendance kitni hai meri?",
  "Next class kaunsi hai?",
  "Exam tips chahiye...",
  "PYQs dhundne hain...",
  "Fee status kya hai?",
  "Subjects list karo...",
];
var pidx = 0;
setInterval(function() {
  var inp = document.getElementById('chatInput');
  if (inp && document.activeElement !== inp) {
    inp.placeholder = hints[pidx++ % hints.length];
  }
}, 3000);

// ── Focus input on load ──
setTimeout(function() {
  var inp = document.getElementById('chatInput');
  if (inp) inp.focus();
}, 200);
</script>
""", unsafe_allow_html=True)

    # ── Handle query param actions from HTML JS ────────────────────────────
    qp = st.query_params

    # New message
    chat_msg = qp.get("chat_msg", "")
    chat_ts  = qp.get("chat_ts", "")
    if chat_msg and chat_ts != st.session_state.get("_last_chat_ts", ""):
        st.session_state["_last_chat_ts"] = chat_ts
        try: del st.query_params["chat_msg"]
        except: pass
        try: del st.query_params["chat_ts"]
        except: pass
        full_msg = chat_msg
        if st.session_state.attached_file_name:
            full_msg += f" [File: {st.session_state.attached_file_name}]"
            st.session_state.attached_file_name = ""
        dispatch_message(full_msg)
        st.rerun()

    # Sidebar actions
    sb_action = qp.get("sb_action", "")
    sb_ts     = qp.get("sb_ts", "")
    if sb_action and sb_ts != st.session_state.get("_last_sb_ts", ""):
        st.session_state["_last_sb_ts"] = sb_ts
        try: del st.query_params["sb_action"]
        except: pass
        try: del st.query_params["sb_ts"]
        except: pass
        if sb_action == "new_chat":
            if st.session_state.chat_messages:
                fu = next((m["content"][:38] for m in st.session_state.chat_messages if m["role"]=="user"), "Session")
                st.session_state.chat_sessions.append({"label": fu+"...", "messages": list(st.session_state.chat_messages)})
            st.session_state.chat_messages = []
            st.session_state.attached_file_name = ""
            st.rerun()
        elif sb_action == "dashboard":
            st.session_state.view = "dashboard"; st.rerun()
        elif sb_action == "erp":
            st.toast("ERP: https://erp.mnit.ac.in — browser mein open hoga!", icon="🎓")

    # Attach file
    attach_file = qp.get("attach_file", "")
    attach_ts   = qp.get("attach_ts", "")
    if attach_file and attach_ts != st.session_state.get("_last_attach_ts", ""):
        st.session_state["_last_attach_ts"] = attach_ts
        st.session_state.attached_file_name = attach_file
        try: del st.query_params["attach_file"]
        except: pass
        st.toast(f"📎 {attach_file} selected!", icon="✅")
        st.rerun()

    # Mic toggle
    mic_toggle = qp.get("mic_toggle", "")
    if mic_toggle and mic_toggle != st.session_state.get("_last_mic_ts", ""):
        st.session_state["_last_mic_ts"] = mic_toggle
        try: del st.query_params["mic_toggle"]
        except: pass
        if st.session_state.is_recording:
            st.session_state.is_recording = False
            st.session_state._voice_submit = True
            st.session_state.voice_transcript = "[Voice message recorded — feature requires browser mic API]"
            st.toast("⏹ Voice stopped!", icon="✅")
        else:
            st.session_state.is_recording = True
            st.toast("🎤 Recording started! Mic button dabao stop karne ke liye.", icon="🎤")
        st.rerun()

    st.stop()


###############################################################################
# DASHBOARD VIEW  (completely unchanged)
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
# MY DASHBOARD  (completely unchanged)
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

st.markdown('<div style="text-align:center;margin-top:28px;padding:10px 0;border-top:1px solid rgba(255,255,255,0.05);"><span style="font-family:\'DM Mono\',monospace;font-size:0.52rem;color:rgba(148,163,184,0.24);letter-spacing:1.2px;">ASKMNT &nbsp;·&nbsp; MNIT JAIPUR &nbsp;·&nbsp; v7.0 PREMIUM</span></div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
