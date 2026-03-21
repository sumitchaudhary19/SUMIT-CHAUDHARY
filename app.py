# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  AskMNIT — v2.0 PREMIUM CHATBOT  (Dashboard untouched)                      ║
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
    # ── CHATBOT STATE ──
    "chat_messages":     [],
    "chat_sessions":     [],
    "chat_input_text":   "",
    "attached_file_name": "",
    "is_recording":      False,
    "voice_transcript":  "",
    "_voice_submit":     False,
    "show_uploader":     False,
    "response_style":    "Concise",
    "voice_output":      False,
    "strict_mode":       False,
    "show_history_panel": False,
    "show_settings_panel": False,
    "sb_open":           False,
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
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&family=Outfit:wght@300;400;500;600;700&display=swap');

*,html,body{box-sizing:border-box;margin:0;padding:0;}
html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"]{font-family:'Inter',sans-serif!important;}
header[data-testid="stHeader"],footer,#MainMenu,[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important;}
[data-testid="stMainBlockContainer"]{padding:0!important;max-width:100%!important;}

/* Dashboard sidebar */
[data-testid="stSidebar"]{background:#0B1120!important;border-right:1px solid rgba(59,130,246,0.16)!important;min-width:260px!important;max-width:260px!important;}
[data-testid="stSidebar"]>div{padding:0!important;}
.sb-section-header{font-family:'DM Mono',monospace;font-size:0.60rem;font-weight:700;color:rgba(148,163,184,0.50);text-transform:uppercase;letter-spacing:1.4px;padding:14px 16px 6px;border-top:1px solid rgba(255,255,255,0.05);margin-top:4px;}
[data-testid="stSidebar"] .stButton>button{background:rgba(239,68,68,0.10)!important;border:1px solid rgba(239,68,68,0.28)!important;color:#FCA5A5!important;border-radius:8px!important;font-size:0.80rem!important;font-weight:600!important;padding:7px 14px!important;box-shadow:none!important;}
[data-testid="stSidebar"] .stButton>button:hover{background:rgba(239,68,68,0.20)!important;transform:none!important;}

/* ── Global buttons ── */
.stButton>button{background:linear-gradient(135deg,#2563EB,#4F46E5)!important;color:#fff!important;border:none!important;border-radius:9px!important;font-family:'Inter',sans-serif!important;font-weight:600!important;font-size:0.82rem!important;padding:9px 16px!important;box-shadow:0 3px 14px rgba(37,99,235,0.20)!important;transition:all 0.16s ease!important;}
.stButton>button:hover{opacity:.88!important;transform:translateY(-1px)!important;}
.ghost-btn .stButton>button{background:rgba(255,255,255,.05)!important;border:1px solid rgba(255,255,255,0.14)!important;color:rgba(226,232,240,.55)!important;box-shadow:none!important;}
.present-btn .stButton>button{background:linear-gradient(135deg,#065F46,#10B981)!important;box-shadow:0 2px 10px rgba(16,185,129,.18)!important;padding:6px 11px!important;font-size:0.75rem!important;border-radius:7px!important;}
.absent-btn .stButton>button{background:linear-gradient(135deg,#7F1D1D,#EF4444)!important;box-shadow:0 2px 10px rgba(239,68,68,.16)!important;padding:6px 11px!important;font-size:0.75rem!important;border-radius:7px!important;}
.save-btn .stButton>button{background:linear-gradient(135deg,#92400E,#F59E0B)!important;box-shadow:0 2px 10px rgba(245,158,11,.18)!important;padding:7px 13px!important;font-size:0.77rem!important;}
.pin-btn .stButton>button{background:rgba(245,158,11,0.10)!important;border:1px solid rgba(245,158,11,0.28)!important;color:#FCD34D!important;box-shadow:none!important;font-size:0.70rem!important;padding:4px 10px!important;border-radius:7px!important;}
.del-btn .stButton>button{background:rgba(239,68,68,0.07)!important;border:1px solid rgba(239,68,68,0.18)!important;color:rgba(252,165,165,0.70)!important;box-shadow:none!important;font-size:0.68rem!important;padding:3px 8px!important;border-radius:6px!important;}
.ql-btn .stButton>button{background:rgba(255,255,255,.03)!important;border:1px solid rgba(255,255,255,0.14)!important;color:rgba(186,230,253,.65)!important;box-shadow:none!important;text-align:left!important;justify-content:flex-start!important;font-size:0.80rem!important;padding:9px 14px!important;border-radius:9px!important;}
.logout-btn .stButton>button{background:rgba(239,68,68,.09)!important;border:1px solid rgba(239,68,68,.20)!important;color:#FCA5A5!important;box-shadow:none!important;font-size:0.80rem!important;}
.open-chat-btn .stButton>button{background:linear-gradient(135deg,#059669,#10B981)!important;border-radius:12px!important;font-weight:700!important;font-size:0.88rem!important;padding:11px 22px!important;box-shadow:0 5px 24px rgba(16,185,129,.36)!important;}
.settings-menu-btn .stButton>button{background:rgba(255,255,255,0.06)!important;border:1px solid rgba(255,255,255,0.12)!important;color:rgba(226,232,240,0.75)!important;box-shadow:none!important;font-size:0.82rem!important;font-weight:600!important;padding:8px 16px!important;border-radius:10px!important;}
.nav-btn .stButton>button{background:transparent!important;color:rgba(148,163,184,.65)!important;border:none!important;box-shadow:none!important;text-align:left!important;justify-content:flex-start!important;padding:10px 14px!important;font-size:0.83rem!important;font-weight:500!important;border-radius:8px!important;}
.nav-btn .stButton>button:hover{background:rgba(59,130,246,.10)!important;color:#BAE6FD!important;transform:none!important;}
.nav-btn-active .stButton>button{background:rgba(59,130,246,.14)!important;color:#60A5FA!important;border-left:2px solid #3B82F6!important;font-weight:700!important;box-shadow:none!important;}

/* ── Inputs ── */
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{background:rgba(255,255,255,0.04)!important;border:1px solid rgba(255,255,255,0.14)!important;border-radius:10px!important;color:#E2E8F0!important;font-family:'Inter',sans-serif!important;font-size:0.87rem!important;}
[data-testid="stTextInput"] input:focus,[data-testid="stTextArea"] textarea:focus{border-color:rgba(59,130,246,0.55)!important;box-shadow:0 0 0 2.5px rgba(59,130,246,0.13)!important;}
[data-testid="stTextInput"] label,[data-testid="stTextArea"] label{color:rgba(148,163,184,0.55)!important;font-size:0.70rem!important;font-weight:600!important;text-transform:uppercase!important;letter-spacing:0.6px!important;}
[data-testid="stSelectbox"]>div>div{background:rgba(255,255,255,0.04)!important;border:1px solid rgba(255,255,255,0.14)!important;border-radius:10px!important;color:#E2E8F0!important;}
[data-testid="stFileUploader"]{background:rgba(59,130,246,0.04)!important;border:1px dashed rgba(59,130,246,0.26)!important;border-radius:12px!important;}
[data-testid="stToggle"] label{color:#E2E8F0!important;font-size:0.86rem!important;}
[data-testid="stExpander"]{background:rgba(255,255,255,.018)!important;border:1px solid rgba(255,255,255,0.08)!important;border-radius:12px!important;}
[data-testid="stProgress"]>div>div{border-radius:99px!important;background:linear-gradient(90deg,#2563EB,#22D3EE)!important;}
[data-testid="stProgress"]>div{background:rgba(255,255,255,.07)!important;border-radius:99px!important;height:5px!important;}
h1,h2,h3,h4{font-family:'DM Mono',monospace!important;font-weight:500!important;}
[data-testid="stMarkdown"] p,[data-testid="stMarkdown"] li{color:rgba(226,232,240,.72)!important;}
hr{border-color:rgba(255,255,255,0.08)!important;}
::-webkit-scrollbar{width:4px;height:4px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:rgba(100,60,200,.30);border-radius:4px;}
[data-testid="column"]{padding:0 4px!important;}
html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"]{background:#0a0a12!important;color:#E2E8F0!important;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# VIEW ROUTER
# ─────────────────────────────────────────────────────────────────────────────
view = st.session_state.view

###############################################################################
# ██████╗ ██╗  ██╗ █████╗ ████████╗██████╗  ██████╗ ████████╗
# ██╔════╝██║  ██║██╔══██╗╚══██╔══╝██╔══██╗██╔═══██╗╚══██╔══╝
# ██║     ███████║███████║   ██║   ██████╔╝██║   ██║   ██║
# ██║     ██╔══██║██╔══██║   ██║   ██╔══██╗██║   ██║   ██║
# ╚██████╗██║  ██║██║  ██║   ██║   ██████╔╝╚██████╔╝   ██║
#  ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═════╝  ╚═════╝    ╚═╝
###############################################################################
if view == "chat":

    # Hide Streamlit sidebar
    st.markdown("""
    <style>
    [data-testid="stSidebar"]{display:none!important;}
    [data-testid="stSidebarCollapseButton"]{display:none!important;}
    [data-testid="collapsedControl"]{display:none!important;}
    section[data-testid="stMain"]{margin-left:0!important;padding-left:0!important;}
    </style>
    """, unsafe_allow_html=True)

    has_messages = bool(st.session_state.chat_messages)

    # ── Voice done handler ────────────────────────────────────────────────
    if st.session_state._voice_submit:
        st.session_state._voice_submit = False
        msg = st.session_state.voice_transcript or "[Voice message]"
        st.session_state.voice_transcript = ""
        dispatch_message(f"🎤 {msg}")
        st.toast("Voice message sent!", icon="🎤")
        st.rerun()

    # ═════════════════════════════════════════════════════════════════════
    # PREMIUM CHATBOT FULL UI — injected as one big HTML/CSS/JS block
    # ═════════════════════════════════════════════════════════════════════

    # Build messages HTML
    msgs_html = ""
    for msg in st.session_state.chat_messages:
        role = msg["role"]
        content = msg["content"].replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\n","<br>")
        if role == "user":
            msgs_html += f"""
            <div class="msg-row user">
              <div class="msg-bubble user-bubble">{content}</div>
              <div class="msg-avatar user-av">U</div>
            </div>"""
        else:
            msgs_html += f"""
            <div class="msg-row ai">
              <div class="msg-avatar ai-av">✦</div>
              <div class="msg-bubble ai-bubble">{content}</div>
            </div>"""

    # Build history items
    hist_html = ""
    for i, sess in enumerate(reversed(st.session_state.chat_sessions[-8:])):
        label = sess.get("label","Chat")[:36]
        hist_html += f'<div class="hist-item" onclick="loadSession({len(st.session_state.chat_sessions)-1-i})"><span class="hist-dot"></span>{label}</div>'
    if not hist_html:
        hist_html = '<div style="padding:18px 12px;font-size:0.76rem;color:rgba(180,180,220,0.35);text-align:center;">No saved chats yet</div>'

    # Suggestion pills
    br = st.session_state.branch
    pills = [
        f"📊 My attendance %",
        f"📅 Next class today?",
        f"📚 PYQs for {br}",
        f"💰 Fee status",
        f"📖 Subjects this sem",
        f"🎯 Exam tips",
    ]
    pills_html = "".join(f'<button class="pill-btn" onclick="sendPill(`{p}`)">{p}</button>' for p in pills)

    # Attached file chip
    chip_html = ""
    if st.session_state.attached_file_name:
        fn = st.session_state.attached_file_name[:22]
        chip_html = f'<div class="file-chip"><span>📎</span>{fn}<button onclick="clearFile()">✕</button></div>'

    nm = st.session_state.student_name.split()[0]

    components.html(f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
/* ═══════════════════════════════════════════════════════
   RESET & BASE
═══════════════════════════════════════════════════════ */
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{
  width:100%;height:100%;
  font-family:'Inter',system-ui,sans-serif;
  background:transparent;
  overflow:hidden;
  color:#e8e8f0;
}}

/* ═══════════════════════════════════════════════════════
   ANIMATED BACKGROUND
═══════════════════════════════════════════════════════ */
#bg{{
  position:fixed;inset:0;z-index:0;
  background:radial-gradient(ellipse 80% 60% at 50% -10%, rgba(120,40,200,0.38) 0%, transparent 70%),
             radial-gradient(ellipse 60% 50% at 85% 80%, rgba(30,60,180,0.28) 0%, transparent 60%),
             radial-gradient(ellipse 50% 40% at 10% 90%, rgba(60,20,140,0.22) 0%, transparent 55%),
             #09070f;
}}
/* floating orbs */
.orb{{
  position:absolute;border-radius:50%;filter:blur(80px);
  animation:orbFloat linear infinite;
  pointer-events:none;
}}
.orb1{{width:320px;height:320px;background:rgba(100,30,200,0.18);top:-80px;left:10%;animation-duration:18s;}}
.orb2{{width:240px;height:240px;background:rgba(40,80,220,0.14);bottom:10%;right:5%;animation-duration:24s;animation-delay:-8s;}}
.orb3{{width:180px;height:180px;background:rgba(160,40,255,0.12);top:40%;left:-60px;animation-duration:20s;animation-delay:-5s;}}
@keyframes orbFloat{{
  0%{{transform:translateY(0) scale(1);}}
  33%{{transform:translateY(-30px) scale(1.05);}}
  66%{{transform:translateY(20px) scale(0.96);}}
  100%{{transform:translateY(0) scale(1);}}
}}
/* grid overlay */
#bg::after{{
  content:'';position:absolute;inset:0;
  background-image:linear-gradient(rgba(140,80,255,0.04) 1px, transparent 1px),
                   linear-gradient(90deg, rgba(140,80,255,0.04) 1px, transparent 1px);
  background-size:48px 48px;
  pointer-events:none;
}}

/* ═══════════════════════════════════════════════════════
   LAYOUT SHELL
═══════════════════════════════════════════════════════ */
#shell{{
  position:fixed;inset:0;z-index:1;
  display:flex;flex-direction:column;
  overflow:hidden;
}}

/* ═══════════════════════════════════════════════════════
   TOP BAR
═══════════════════════════════════════════════════════ */
#topbar{{
  height:52px;
  display:flex;align-items:center;
  padding:0 20px;gap:12px;
  background:rgba(14,10,28,0.82);
  backdrop-filter:blur(24px);
  border-bottom:1px solid rgba(140,80,255,0.14);
  flex-shrink:0;
  position:relative;z-index:100;
}}
.tb-logo{{
  display:flex;align-items:center;gap:9px;
  font-size:0.92rem;font-weight:700;color:#e8e8f8;
  letter-spacing:-0.3px;
}}
.tb-logo-icon{{
  width:30px;height:30px;border-radius:9px;
  background:linear-gradient(135deg,#7c3aed,#4f46e5);
  display:flex;align-items:center;justify-content:center;
  font-size:1rem;box-shadow:0 4px 16px rgba(120,60,220,0.45);
}}
.tb-badge{{
  font-size:0.52rem;padding:2px 7px;border-radius:4px;
  background:rgba(140,80,255,0.15);
  border:1px solid rgba(140,80,255,0.28);
  color:rgba(200,170,255,0.80);font-weight:600;
  letter-spacing:0.6px;
}}
.tb-spacer{{flex:1;}}
.tb-menu-btn{{
  width:34px;height:34px;border-radius:8px;
  background:rgba(140,80,255,0.12);
  border:1px solid rgba(140,80,255,0.24);
  cursor:pointer;display:flex;
  flex-direction:column;align-items:center;justify-content:center;gap:4px;
  transition:all 0.18s;
  flex-shrink:0;
}}
.tb-menu-btn:hover{{background:rgba(160,100,255,0.22);border-color:rgba(180,120,255,0.40);}}
.tb-hbar{{width:14px;height:2px;background:rgba(210,180,255,0.80);border-radius:2px;transition:all 0.22s;}}
.tb-menu-btn.open .tb-hbar:nth-child(1){{transform:rotate(45deg) translate(4.5px,4.5px);}}
.tb-menu-btn.open .tb-hbar:nth-child(2){{opacity:0;transform:scaleX(0);}}
.tb-menu-btn.open .tb-hbar:nth-child(3){{transform:rotate(-45deg) translate(4.5px,-4.5px);}}

/* ═══════════════════════════════════════════════════════
   LEFT SIDEBAR
═══════════════════════════════════════════════════════ */
#sidebar{{
  position:fixed;top:52px;left:0;
  width:220px;height:calc(100vh - 52px);
  background:rgba(10,6,22,0.97);
  backdrop-filter:blur(28px);
  border-right:1px solid rgba(140,80,255,0.16);
  box-shadow:6px 0 40px rgba(60,10,130,0.30);
  transform:translateX(-100%);
  transition:transform 0.28s cubic-bezier(0.22,0.61,0.36,1);
  z-index:90;
  display:flex;flex-direction:column;
  padding:20px 10px 16px;
  gap:3px;
  overflow-y:auto;
}}
#sidebar.open{{transform:translateX(0);}}
.sb-head{{
  font-size:0.50rem;color:rgba(180,140,255,0.35);
  text-transform:uppercase;letter-spacing:1.8px;
  padding:0 8px 10px;
  border-bottom:1px solid rgba(140,80,255,0.12);
  margin-bottom:8px;
  font-family:'DM Mono',monospace;
}}
.sb-item{{
  display:flex;align-items:center;gap:10px;
  padding:10px 12px;border-radius:10px;
  font-size:0.80rem;font-weight:500;
  color:rgba(200,180,240,0.70);
  cursor:pointer;user-select:none;
  border:1px solid transparent;
  transition:all 0.15s;
  margin-bottom:2px;
}}
.sb-item:hover{{
  background:rgba(140,80,255,0.14);
  border-color:rgba(180,120,255,0.22);
  color:#d4aaff;
}}
.sb-item.active{{
  background:rgba(140,80,255,0.20);
  border-color:rgba(180,120,255,0.35);
  color:#e0ccff;
}}
.sb-item-icon{{font-size:0.90rem;width:20px;text-align:center;}}
.sb-divider{{height:1px;background:rgba(140,80,255,0.10);margin:8px 4px;}}
.sb-section-label{{
  font-size:0.48rem;color:rgba(180,140,255,0.28);
  text-transform:uppercase;letter-spacing:1.5px;
  padding:6px 12px 4px;
  font-family:'DM Mono',monospace;
}}
/* History inside sidebar */
.hist-item{{
  display:flex;align-items:center;gap:8px;
  padding:7px 12px;border-radius:8px;
  font-size:0.73rem;color:rgba(180,160,220,0.58);
  cursor:pointer;
  transition:all 0.14s;
  overflow:hidden;white-space:nowrap;text-overflow:ellipsis;
  border:1px solid transparent;
}}
.hist-item:hover{{background:rgba(100,60,200,0.12);border-color:rgba(140,80,255,0.18);color:rgba(210,190,255,0.75);}}
.hist-dot{{width:5px;height:5px;border-radius:50%;background:rgba(140,80,255,0.50);flex-shrink:0;}}

/* ═══════════════════════════════════════════════════════
   OVERLAY
═══════════════════════════════════════════════════════ */
#overlay{{
  position:fixed;inset:0;z-index:80;
  background:rgba(0,0,0,0);pointer-events:none;
  transition:background 0.28s;
}}
#overlay.open{{background:rgba(0,0,0,0.45);pointer-events:auto;}}

/* ═══════════════════════════════════════════════════════
   MAIN CONTENT AREA
═══════════════════════════════════════════════════════ */
#main{{
  flex:1;display:flex;flex-direction:column;
  overflow:hidden;position:relative;z-index:2;
}}

/* ─── HERO (no messages) ─── */
#hero{{
  flex:1;display:flex;flex-direction:column;
  align-items:center;justify-content:center;
  padding:20px 24px 180px;
  animation:fadeUp 0.5s ease both;
}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(20px);}}to{{opacity:1;transform:translateY(0);}}}}
.hero-orb{{
  width:72px;height:72px;border-radius:50%;margin-bottom:20px;
  background:radial-gradient(circle at 35% 35%, #c084fc, #7c3aed 55%, #4f46e5);
  box-shadow:0 0 0 1px rgba(180,120,255,0.25),0 16px 60px rgba(120,60,220,0.50),0 0 80px rgba(100,40,200,0.25);
  display:flex;align-items:center;justify-content:center;
  font-size:1.8rem;
  animation:orb3dPulse 4s ease-in-out infinite;
}}
@keyframes orb3dPulse{{
  0%,100%{{box-shadow:0 0 0 1px rgba(180,120,255,0.25),0 16px 60px rgba(120,60,220,0.50),0 0 80px rgba(100,40,200,0.20);}}
  50%{{box-shadow:0 0 0 2px rgba(200,140,255,0.35),0 20px 80px rgba(140,80,240,0.65),0 0 100px rgba(120,60,220,0.32);}}
}}
.hero-title{{
  font-size:2.2rem;font-weight:700;
  background:linear-gradient(135deg,#e8d8ff 30%,#a78bfa 70%,#818cf8);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  letter-spacing:-1px;margin-bottom:8px;text-align:center;
}}
.hero-sub{{
  font-size:0.82rem;color:rgba(180,160,220,0.48);
  margin-bottom:32px;text-align:center;letter-spacing:0.2px;
  line-height:1.6;
}}
/* pills */
.pills-wrap{{
  display:flex;flex-wrap:wrap;gap:8px;
  justify-content:center;margin-bottom:36px;
  max-width:640px;
}}
.pill-btn{{
  padding:8px 16px;border-radius:999px;
  background:rgba(140,80,255,0.08);
  border:1px solid rgba(140,80,255,0.22);
  color:rgba(200,175,255,0.72);
  font-size:0.77rem;font-weight:500;
  cursor:pointer;
  transition:all 0.16s;font-family:'Inter',sans-serif;
}}
.pill-btn:hover{{
  background:rgba(140,80,255,0.20);
  border-color:rgba(180,120,255,0.42);
  color:#d4aaff;transform:translateY(-2px);
}}

/* ─── MESSAGES ─── */
#messages{{
  flex:1;overflow-y:auto;
  padding:20px 0 200px;
  scroll-behavior:smooth;
}}
#messages::-webkit-scrollbar{{width:4px;}}
#messages::-webkit-scrollbar-thumb{{background:rgba(140,80,255,0.25);border-radius:4px;}}
.msg-row{{
  display:flex;align-items:flex-end;gap:10px;
  padding:6px 20px;
  animation:msgIn 0.28s ease both;
}}
@keyframes msgIn{{from{{opacity:0;transform:translateY(10px);}}to{{opacity:1;transform:translateY(0);}}}}
.msg-row.user{{flex-direction:row-reverse;}}
.msg-avatar{{
  width:32px;height:32px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-size:0.80rem;font-weight:700;flex-shrink:0;
}}
.user-av{{
  background:linear-gradient(135deg,#4f46e5,#7c3aed);
  color:white;box-shadow:0 3px 12px rgba(100,60,220,0.35);
  font-size:0.72rem;
}}
.ai-av{{
  background:linear-gradient(135deg,#7c3aed,#a855f7);
  color:white;box-shadow:0 3px 12px rgba(140,80,220,0.35);
  font-size:0.68rem;font-weight:800;
}}
.msg-bubble{{
  max-width:62%;padding:12px 16px;
  border-radius:18px;font-size:0.84rem;line-height:1.65;
}}
.user-bubble{{
  background:linear-gradient(135deg,rgba(79,70,229,0.55),rgba(124,58,237,0.45));
  border:1px solid rgba(140,80,255,0.30);
  color:#ede8ff;border-bottom-right-radius:5px;
}}
.ai-bubble{{
  background:rgba(255,255,255,0.04);
  border:1px solid rgba(255,255,255,0.08);
  color:rgba(230,225,255,0.88);border-bottom-left-radius:5px;
}}

/* ─── TYPING indicator ─── */
.typing-row{{display:flex;align-items:flex-end;gap:10px;padding:6px 20px;}}
.typing-bubble{{
  padding:12px 18px;
  background:rgba(255,255,255,0.04);
  border:1px solid rgba(255,255,255,0.08);
  border-radius:18px;border-bottom-left-radius:5px;
  display:flex;gap:5px;align-items:center;
}}
.t-dot{{
  width:7px;height:7px;border-radius:50%;
  background:rgba(180,140,255,0.60);
  animation:typingPulse 1.4s ease-in-out infinite;
}}
.t-dot:nth-child(2){{animation-delay:0.2s;}}
.t-dot:nth-child(3){{animation-delay:0.4s;}}
@keyframes typingPulse{{0%,80%,100%{{transform:scale(0.7);opacity:0.4;}}40%{{transform:scale(1);opacity:1;}}}}

/* ═══════════════════════════════════════════════════════
   INPUT BAR — BOTTOM (always centered)
═══════════════════════════════════════════════════════ */
#input-zone{{
  position:fixed;bottom:0;left:0;right:0;
  z-index:50;
  padding:12px max(16px,calc((100% - 720px)/2)) 18px;
  background:linear-gradient(to top, rgba(9,7,15,0.98) 0%, rgba(9,7,15,0.90) 70%, transparent 100%);
  backdrop-filter:blur(12px);
}}
/* file chip */
.file-chip{{
  display:inline-flex;align-items:center;gap:6px;
  padding:4px 12px 4px 10px;margin-bottom:8px;
  background:rgba(140,80,255,0.14);
  border:1px solid rgba(140,80,255,0.32);
  border-radius:999px;font-size:0.72rem;color:#c4aaff;
  font-weight:600;
}}
.file-chip button{{background:none;border:none;cursor:pointer;color:rgba(180,150,255,0.55);margin-left:2px;font-size:0.75rem;}}
/* Bar card */
.bar-card{{
  background:rgba(22,14,42,0.92);
  border:1px solid rgba(140,80,255,0.22);
  border-radius:20px;
  box-shadow:0 -4px 40px rgba(80,30,160,0.30), 0 0 0 0 rgba(140,80,255,0);
  overflow:hidden;
  animation:barGlow 5s ease-in-out infinite;
  transition:border-color 0.22s, box-shadow 0.22s;
}}
.bar-card:focus-within{{
  border-color:rgba(160,100,255,0.55) !important;
  box-shadow:0 0 0 3px rgba(140,80,255,0.14),0 -4px 40px rgba(100,40,200,0.45) !important;
  animation:none !important;
}}
@keyframes barGlow{{
  0%,100%{{box-shadow:0 -4px 40px rgba(80,30,160,0.28), 0 0 0 0 rgba(140,80,255,0);}}
  50%{{box-shadow:0 -4px 48px rgba(100,40,200,0.40), 0 0 18px rgba(140,80,255,0.10);}}
}}
/* Input row */
.bar-inner{{display:flex;align-items:center;padding:10px 10px 10px 14px;gap:6px;}}
#chat-input{{
  flex:1;background:transparent;border:none;outline:none;
  color:#e8e0ff;font-family:'Inter',sans-serif;
  font-size:0.93rem;line-height:1.5;
  resize:none;max-height:120px;min-height:24px;height:auto;
  caret-color:#a78bfa;
  padding:0 4px;
}}
#chat-input::placeholder{{color:rgba(180,155,240,0.35);font-size:0.90rem;}}
/* bottom row of bar */
.bar-bottom{{
  display:flex;align-items:center;
  padding:0 12px 11px 14px;gap:8px;
}}
.bar-bottom-left{{display:flex;gap:6px;flex:1;}}
/* icon buttons */
.icon-btn{{
  width:34px;height:34px;border-radius:10px;
  background:rgba(140,80,255,0.10);
  border:1px solid rgba(140,80,255,0.20);
  cursor:pointer;display:flex;align-items:center;justify-content:center;
  color:rgba(190,160,255,0.65);font-size:1rem;
  transition:all 0.16s;user-select:none;
  flex-shrink:0;
}}
.icon-btn:hover{{background:rgba(160,100,255,0.22);border-color:rgba(180,120,255,0.38);color:#d4aaff;}}
.icon-btn.active{{background:rgba(239,68,68,0.18);border-color:rgba(239,68,68,0.40);color:#fca5a5;animation:micPulse 1.1s ease-in-out infinite;}}
@keyframes micPulse{{0%,100%{{box-shadow:0 0 0 0 rgba(239,68,68,0.40);}}50%{{box-shadow:0 0 0 6px rgba(239,68,68,0);}}}}
/* send button */
.send-btn{{
  width:38px;height:38px;border-radius:50%;
  background:linear-gradient(135deg,#7c3aed,#4f46e5);
  border:none;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  color:white;font-size:1.1rem;font-weight:700;
  box-shadow:0 4px 18px rgba(120,60,220,0.50);
  transition:all 0.16s;flex-shrink:0;
}}
.send-btn:hover{{transform:scale(1.08);box-shadow:0 6px 24px rgba(140,80,240,0.65);}}
.send-btn:active{{transform:scale(0.96);}}
/* label tags */
.bar-tag{{
  font-size:0.62rem;color:rgba(180,150,255,0.40);
  padding:3px 9px;border-radius:5px;
  background:rgba(140,80,255,0.06);
  border:1px solid rgba(140,80,255,0.12);
  user-select:none;
}}

/* ═══════════════════════════════════════════════════════
   PLACEHOLDER SHIMMER
═══════════════════════════════════════════════════════ */
@keyframes phShimmer{{0%,100%{{opacity:0.35;}}50%{{opacity:0.65;}}}}
#chat-input:placeholder-shown{{animation:phShimmer 3s ease-in-out infinite;}}

/* ═══════════════════════════════════════════════════════
   VOICE INDICATOR
═══════════════════════════════════════════════════════ */
#voice-bar{{
  display:none;
  align-items:center;gap:8px;
  margin-bottom:8px;padding:8px 14px;
  background:rgba(239,68,68,0.08);
  border:1px solid rgba(239,68,68,0.22);
  border-radius:10px;font-size:0.78rem;color:#fca5a5;
}}
#voice-bar.show{{display:flex;}}
.v-dot{{width:7px;height:7px;border-radius:50%;background:#ef4444;animation:blinkDot 1.1s ease infinite;}}
@keyframes blinkDot{{0%,100%{{opacity:1;}}50%{{opacity:0.2;}}}}

</style>
</head>
<body>

<!-- Animated BG -->
<div id="bg">
  <div class="orb orb1"></div>
  <div class="orb orb2"></div>
  <div class="orb orb3"></div>
</div>

<!-- Overlay -->
<div id="overlay" onclick="closeSb()"></div>

<!-- LEFT SIDEBAR -->
<div id="sidebar">
  <div class="sb-head">AskMNIT Menu</div>

  <div class="sb-item active" onclick="goAction('new_chat')">
    <span class="sb-item-icon">✦</span> New Chat
  </div>

  <div class="sb-item" onclick="toggleHistory()">
    <span class="sb-item-icon">🕐</span> Chat History
  </div>

  <div class="sb-divider"></div>
  <div class="sb-section-label">Navigation</div>

  <div class="sb-item" onclick="goAction('dashboard')">
    <span class="sb-item-icon">⊞</span> Back to Dashboard
  </div>

  <div class="sb-item" onclick="openERP()">
    <span class="sb-item-icon">🔗</span> ERP Login
  </div>

  <div class="sb-divider"></div>
  <div class="sb-section-label">Chat History</div>
  <div id="hist-list">{hist_html}</div>
</div>

<!-- MAIN SHELL -->
<div id="shell">

  <!-- TOP BAR -->
  <div id="topbar">
    <button class="tb-menu-btn" id="menu-btn" onclick="toggleSb()">
      <span class="tb-hbar"></span>
      <span class="tb-hbar"></span>
      <span class="tb-hbar"></span>
    </button>
    <div class="tb-logo">
      <div class="tb-logo-icon">✦</div>
      AskMNIT
    </div>
    <div class="tb-badge">AI</div>
    <div class="tb-spacer"></div>
    <div class="tb-badge" style="background:rgba(16,185,129,0.12);border-color:rgba(16,185,129,0.28);color:rgba(100,220,160,0.80);">● LIVE</div>
  </div>

  <!-- MAIN CONTENT -->
  <div id="main">

    <!-- HERO (shown when no messages) -->
    <div id="hero" style="display:{'none' if has_messages else 'flex'};">
      <div class="hero-orb">✦</div>
      <div class="hero-title">AskMNIT AI</div>
      <div class="hero-sub">
        Hey {nm}! Your smart MNIT senior — always here 🎓<br>
        Attendance · PYQs · Schedule · Exam prep
      </div>
      <div class="pills-wrap" id="pills">
        {pills_html}
      </div>
    </div>

    <!-- MESSAGES (shown when has messages) -->
    <div id="messages" style="display:{'flex' if has_messages else 'none'};flex-direction:column;">
      {msgs_html}
      <div id="msg-bottom"></div>
    </div>

  </div><!-- /main -->

  <!-- INPUT ZONE (always at bottom) -->
  <div id="input-zone">
    <div id="voice-bar">
      <div class="v-dot"></div>
      <span>Listening... click mic to stop</span>
    </div>
    {chip_html}
    <div class="bar-card" id="bar-card">
      <div class="bar-inner">
        <textarea id="chat-input" rows="1"
          placeholder="Ask AskMNIT anything..."
          onkeydown="handleKey(event)"
          oninput="autoResize(this)"></textarea>
      </div>
      <div class="bar-bottom">
        <div class="bar-bottom-left">
          <button class="icon-btn" title="Attach file" onclick="triggerFile()">📎</button>
          <button class="icon-btn" id="mic-btn" title="Voice input" onclick="toggleMic()">🎤</button>
          <span class="bar-tag">MNIT AI</span>
        </div>
        <button class="send-btn" onclick="sendMsg()" title="Send">↑</button>
      </div>
    </div>
    <div style="text-align:center;margin-top:6px;">
      <span style="font-size:0.52rem;color:rgba(140,100,200,0.28);letter-spacing:0.8px;">AskMNIT AI may make mistakes · Verify with official ERP</span>
    </div>
  </div>

</div><!-- /shell -->

<!-- hidden file input -->
<input type="file" id="file-input"
  accept=".pdf,.txt,.png,.jpg,.jpeg,.docx,.csv"
  style="position:absolute;width:1px;height:1px;opacity:0;"
  onchange="handleFile(this)">

<!-- hidden voice recorder -->
<div id="recorder-holder" style="display:none;"></div>

<script>
// ── Sidebar ──────────────────────────────────────────────────────
var sbOpen = false;
function toggleSb(){{ sbOpen ? closeSb() : openSb(); }}
function openSb(){{
  sbOpen=true;
  document.getElementById('sidebar').classList.add('open');
  document.getElementById('overlay').classList.add('open');
  document.getElementById('menu-btn').classList.add('open');
}}
function closeSb(){{
  sbOpen=false;
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('overlay').classList.remove('open');
  document.getElementById('menu-btn').classList.remove('open');
}}
function toggleHistory(){{
  document.getElementById('hist-list').style.display =
    document.getElementById('hist-list').style.display === 'none' ? 'block' : 'none';
}}
document.addEventListener('keydown',function(e){{ if(e.key==='Escape') closeSb(); }});

// ── SEND TO STREAMLIT — query param method (proven working) ──────
function sendToStreamlit(payload) {{
  try {{
    var data = JSON.parse(payload);
    var url = new URL(window.parent.location.href);
    url.searchParams.set('_am_type', data.type || '');
    url.searchParams.set('_am_val', encodeURIComponent(data.value || ''));
    window.parent.location.href = url.toString();
  }} catch(e) {{
    // fallback: try setting just the hash
    try {{
      window.parent.location.hash = encodeURIComponent(payload);
    }} catch(e2) {{}}
  }}
}}

// ── Actions (sidebar) ────────────────────────────────────────────
function goAction(action){{
  closeSb();
  sendToStreamlit(JSON.stringify({{type:'action', value:action}}));
}}
function openERP(){{
  window.open('https://erp.mnit.ac.in','_blank');
}}
function loadSession(idx){{
  closeSb();
  sendToStreamlit(JSON.stringify({{type:'load_session', value:idx}}));
}}

// ── File attach ───────────────────────────────────────────────────
function triggerFile(){{
  document.getElementById('file-input').click();
}}
function handleFile(input){{
  if(!input.files||!input.files[0]) return;
  var fname = input.files[0].name;
  sendToStreamlit(JSON.stringify({{type:'file', value:fname}}));
}}
function clearFile(){{
  sendToStreamlit(JSON.stringify({{type:'clear_file', value:''}}));
}}

// ── Textarea auto-resize ──────────────────────────────────────────
function autoResize(el){{
  el.style.height='auto';
  el.style.height=Math.min(el.scrollHeight,120)+'px';
}}

// ── Send message ─────────────────────────────────────────────────
function sendMsg(){{
  var inp = document.getElementById('chat-input');
  var txt = inp.value.trim();
  if(!txt) return;
  inp.value=''; inp.style.height='auto';
  sendToStreamlit(JSON.stringify({{type:'send', value:txt}}));
}}
function sendPill(txt){{
  sendToStreamlit(JSON.stringify({{type:'send', value:txt}}));
}}
function handleKey(e){{
  if(e.key==='Enter' && !e.shiftKey){{ e.preventDefault(); sendMsg(); }}
}}

// ── Voice ─────────────────────────────────────────────────────────
var mediaRecorder=null, audioChunks=[], isRecording=false;
function toggleMic(){{
  isRecording ? stopMic() : startMic();
}}
function startMic(){{
  navigator.mediaDevices.getUserMedia({{audio:true}}).then(function(stream){{
    audioChunks=[];
    try{{mediaRecorder=new MediaRecorder(stream,{{mimeType:'audio/webm'}});}}
    catch(e){{mediaRecorder=new MediaRecorder(stream);}}
    mediaRecorder.ondataavailable=function(e){{if(e.data&&e.data.size>0) audioChunks.push(e.data);}};
    mediaRecorder.onstop=function(){{
      isRecording=false;
      document.getElementById('mic-btn').classList.remove('active');
      document.getElementById('voice-bar').classList.remove('show');
      stream.getTracks().forEach(function(t){{t.stop();}});
      sendToStreamlit(JSON.stringify({{type:'voice_done', value:'[Voice message recorded]'}}));
    }};
    mediaRecorder.start(200); isRecording=true;
    document.getElementById('mic-btn').classList.add('active');
    document.getElementById('voice-bar').classList.add('show');
  }}).catch(function(){{
    alert('Microphone permission denied!');
  }});
}}
function stopMic(){{
  if(mediaRecorder&&mediaRecorder.state!=='inactive') mediaRecorder.stop();
}}

// ── Rotating placeholder ──────────────────────────────────────────
var _ph = [
  "Ask AskMNIT anything...",
  "What's my attendance today?",
  "When is my next class?",
  "Give me PYQs for {br}...",
  "How many classes can I miss?",
  "Exam preparation tips...",
  "Check my fee status...",
];
var _phi=0;
setInterval(function(){{
  var el=document.getElementById('chat-input');
  if(!el||document.activeElement===el) return;
  _phi=(_phi+1)%_ph.length;
  el.style.opacity='0';
  setTimeout(function(){{el.placeholder=_ph[_phi];el.style.opacity='1';}},200);
}},3000);

// ── Scroll to bottom ──────────────────────────────────────────────
var mb = document.getElementById('msg-bottom');
if(mb) setTimeout(function(){{mb.scrollIntoView({{behavior:'smooth'}});}},100);

// ── Streamlit component ready signal ─────────────────────────────
window.parent.postMessage({{isStreamlitMessage:true, type:"streamlit:componentReady", apiVersion:1}}, "*");
</script>
</body>
</html>
""", height=700 if has_messages else 680, scrolling=False)

    # ── Handle query params from iframe JS ───────────────────────────────
    import urllib.parse as _up
    _am_type = st.query_params.get("_am_type", "")
    _am_val  = _up.unquote(st.query_params.get("_am_val", ""))

    if _am_type:
        # Clear params immediately
        try:
            del st.query_params["_am_type"]
            del st.query_params["_am_val"]
        except: pass

        if _am_type == "send" and _am_val.strip():
            dispatch_message(_am_val.strip())
            st.session_state.attached_file_name = ""
            st.rerun()

        elif _am_type == "action":
            if _am_val == "new_chat":
                if st.session_state.chat_messages:
                    fu = next((m["content"][:40] for m in st.session_state.chat_messages if m["role"]=="user"), "Session")
                    st.session_state.chat_sessions.append({"label": fu, "messages": list(st.session_state.chat_messages)})
                st.session_state.chat_messages = []
                st.session_state.attached_file_name = ""
                st.rerun()
            elif _am_val == "dashboard":
                st.session_state.view = "dashboard"; st.rerun()

        elif _am_type == "file" and _am_val:
            st.session_state.attached_file_name = _am_val
            st.toast(f"📎 {_am_val} attached!", icon="✅"); st.rerun()

        elif _am_type == "clear_file":
            st.session_state.attached_file_name = ""; st.rerun()

        elif _am_type == "voice_done":
            dispatch_message("🎤 " + _am_val); st.rerun()

    st.stop()


###############################################################################
# DASHBOARD VIEW  (100% UNCHANGED)
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
# MY DASHBOARD  (100% UNCHANGED)
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

st.markdown('<div style="text-align:center;margin-top:28px;padding:10px 0;border-top:1px solid rgba(255,255,255,0.05);"><span style="font-family:\'DM Mono\',monospace;font-size:0.52rem;color:rgba(148,163,184,0.24);letter-spacing:1.2px;">ASKMNT &nbsp;·&nbsp; MNIT JAIPUR &nbsp;·&nbsp; v2.0 PREMIUM</span></div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
