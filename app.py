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

    import json as _json

    # ── Kill Streamlit sidebar & inject premium chat CSS ──────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&family=Nunito:wght@400;500;600;700&display=swap');

    [data-testid="stSidebar"]{display:none!important;}
    [data-testid="stSidebarCollapseButton"]{display:none!important;}
    [data-testid="collapsedControl"]{display:none!important;}
    section[data-testid="stMain"]{margin-left:0!important;padding-left:0!important;}
    html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"]{
        background:#08080F!important;
        font-family:'Nunito',sans-serif!important;
    }
    .block-container{padding:0 0 0 0!important;max-width:100%!important;}

    /* ── Animated BG ── */
    [data-testid="stAppViewContainer"]::before{
        content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
        background:
            radial-gradient(ellipse 80% 60% at 70% -10%, rgba(124,58,237,0.18) 0%, transparent 60%),
            radial-gradient(ellipse 50% 40% at 100% 80%, rgba(34,211,238,0.09) 0%, transparent 55%),
            radial-gradient(ellipse 40% 50% at -10% 50%, rgba(236,72,153,0.07) 0%, transparent 60%);
    }
    [data-testid="stAppViewContainer"]::after{
        content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
        background-image:
            linear-gradient(rgba(120,80,255,0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(120,80,255,0.04) 1px, transparent 1px);
        background-size:48px 48px;
        mask-image:radial-gradient(ellipse 90% 90% at 50% 50%, black 30%, transparent 100%);
    }

    /* ── Custom sidebar panel (left fixed) ── */
    .chat-sidebar{
        position:fixed;top:0;left:0;bottom:0;width:258px;
        background:#0A0A16;
        border-right:1px solid rgba(120,80,255,0.18);
        z-index:999;display:flex;flex-direction:column;
        overflow:hidden;
    }
    .chat-sidebar::before{
        content:'';position:absolute;top:0;left:0;right:0;height:1px;
        background:linear-gradient(90deg,transparent,#7C3AED,transparent);
    }
    .sb-logo{padding:18px 16px 14px;border-bottom:1px solid rgba(255,255,255,0.06);}
    .sb-logo-row{display:flex;align-items:center;gap:10px;}
    .sb-logo-icon{
        width:34px;height:34px;border-radius:10px;
        background:linear-gradient(135deg,#7C3AED,#4F46E5);
        display:flex;align-items:center;justify-content:center;
        font-family:'JetBrains Mono',monospace;font-size:0.88rem;font-weight:700;color:#fff;
        box-shadow:0 0 20px rgba(124,58,237,0.35),0 4px 12px rgba(0,0,0,0.4);
        flex-shrink:0;
    }
    .sb-logo-text{font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:800;color:#F1F0FF;letter-spacing:-0.3px;}
    .sb-logo-sub{font-size:0.52rem;color:rgba(150,140,200,0.42);font-family:'JetBrains Mono',monospace;letter-spacing:0.8px;margin-top:1px;}
    .sb-section{
        font-family:'JetBrains Mono',monospace;font-size:0.50rem;font-weight:500;
        color:rgba(150,140,200,0.40);text-transform:uppercase;letter-spacing:1.6px;
        padding:12px 16px 6px;
    }
    .sb-nav-item{
        display:flex;align-items:center;gap:10px;
        padding:9px 14px;margin:2px 8px;border-radius:9px;cursor:pointer;
        font-size:0.82rem;font-weight:500;color:rgba(200,195,240,0.65);
        transition:all 0.15s;
    }
    .sb-nav-item:hover{background:rgba(124,58,237,0.12);color:#A78BFA;}
    .sb-nav-active{background:rgba(124,58,237,0.18)!important;color:#A78BFA!important;border-left:2px solid #7C3AED;}
    .sb-nav-icon{font-size:0.90rem;width:18px;text-align:center;}
    .sb-history-scroll{flex:1;overflow-y:auto;padding-bottom:8px;}
    .sb-history-scroll::-webkit-scrollbar{width:3px;}
    .sb-history-scroll::-webkit-scrollbar-thumb{background:rgba(124,58,237,0.20);border-radius:3px;}
    .hist-item{
        display:flex;align-items:center;gap:8px;padding:8px 16px;
        font-size:0.76rem;color:rgba(150,140,200,0.42);
        border-bottom:1px solid rgba(255,255,255,0.025);
        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
    }
    .hist-dot{width:5px;height:5px;border-radius:50%;background:rgba(124,58,237,0.50);flex-shrink:0;}
    .hist-empty{padding:16px;font-size:0.72rem;color:rgba(150,140,200,0.35);text-align:center;font-style:italic;}
    .erp-box{
        margin:10px 10px 0;padding:12px;
        background:rgba(236,72,153,0.06);border:1px solid rgba(236,72,153,0.18);border-radius:12px;
    }
    .erp-title{font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:rgba(236,72,153,0.80);text-transform:uppercase;letter-spacing:1px;margin-bottom:9px;}
    .erp-inp{
        width:100%;margin-bottom:6px;padding:7px 9px;
        background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.09);
        border-radius:7px;color:#F1F0FF;font-size:0.74rem;outline:none;
        font-family:'Nunito',sans-serif;box-sizing:border-box;
    }
    .erp-inp::placeholder{color:rgba(150,140,200,0.30);}
    .erp-btn{
        width:100%;padding:7px;border:1px solid rgba(236,72,153,0.35);border-radius:7px;
        background:rgba(236,72,153,0.18);color:rgba(236,72,153,0.90);
        font-size:0.74rem;font-weight:700;cursor:pointer;box-sizing:border-box;
        font-family:'Nunito',sans-serif;
    }
    .erp-note{font-size:0.56rem;color:rgba(150,140,200,0.35);text-align:center;margin-top:5px;}
    .sb-back{
        margin:10px;padding:9px 12px;border-radius:9px;cursor:pointer;
        display:flex;align-items:center;gap:8px;
        font-size:0.80rem;font-weight:600;color:rgba(34,211,238,0.75);
        background:rgba(34,211,238,0.07);border:1px solid rgba(34,211,238,0.18);
        transition:all 0.16s;
    }
    .sb-back:hover{background:rgba(34,211,238,0.13);border-color:rgba(34,211,238,0.35);}

    /* ── Main chat area (offset for sidebar) ── */
    .chat-main-wrap{
        margin-left:258px;
        display:flex;flex-direction:column;
        min-height:100vh;
        position:relative;z-index:1;
    }

    /* ── Top navbar ── */
    .chat-navbar{
        position:fixed;top:0;left:258px;right:0;height:52px;z-index:998;
        background:rgba(8,8,15,0.94);backdrop-filter:blur(20px);
        border-bottom:1px solid rgba(255,255,255,0.06);
        display:flex;align-items:center;justify-content:space-between;
        padding:0 24px;
    }
    .nb-model{
        display:flex;align-items:center;gap:7px;
        background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
        border-radius:20px;padding:5px 13px;
        font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:rgba(200,195,240,0.65);
    }
    .nb-model-dot{width:6px;height:6px;border-radius:50%;background:#10B981;box-shadow:0 0 6px #10B981;}
    .nb-actions{display:flex;gap:8px;align-items:center;}
    .nb-btn{
        padding:5px 13px;border-radius:20px;cursor:pointer;
        font-size:0.71rem;font-weight:600;font-family:'Nunito',sans-serif;
        background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
        color:rgba(200,195,240,0.65);transition:all 0.15s;
    }
    .nb-btn:hover{background:rgba(124,58,237,0.15);border-color:rgba(124,58,237,0.35);color:#A78BFA;}

    /* ── Hero state ── */
    .hero-section{
        display:flex;flex-direction:column;align-items:center;
        justify-content:center;padding:40px 24px 20px;
        min-height:calc(100vh - 200px);
        animation:heroIn 0.50s cubic-bezier(0.22,0.61,0.36,1) both;
    }
    @keyframes heroIn{from{opacity:0;transform:translateY(22px);}to{opacity:1;transform:translateY(0);}}
    .hero-orb{
        width:82px;height:82px;border-radius:22px;
        background:linear-gradient(135deg,#1E1B4B 0%,#4C1D95 40%,#7C3AED 70%,#22D3EE 100%);
        display:flex;align-items:center;justify-content:center;font-size:2rem;
        margin-bottom:22px;
        box-shadow:0 0 0 1px rgba(124,58,237,0.30),0 0 40px rgba(124,58,237,0.30),0 16px 50px rgba(0,0,0,0.50);
        animation:orbPulse 3s ease-in-out infinite;
    }
    @keyframes orbPulse{
        0%,100%{box-shadow:0 0 0 1px rgba(124,58,237,0.30),0 0 40px rgba(124,58,237,0.30),0 16px 50px rgba(0,0,0,0.50);}
        50%{box-shadow:0 0 0 1px rgba(124,58,237,0.50),0 0 60px rgba(124,58,237,0.50),0 16px 50px rgba(0,0,0,0.50);}
    }
    .hero-title{
        font-family:'Syne',sans-serif;font-size:2.4rem;font-weight:800;
        letter-spacing:-1.5px;line-height:1.1;text-align:center;margin-bottom:10px;
        background:linear-gradient(135deg,#F1F0FF 0%,#A78BFA 50%,#22D3EE 100%);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
    }
    .hero-sub{
        font-size:0.85rem;color:rgba(150,140,200,0.50);text-align:center;
        line-height:1.75;margin-bottom:30px;max-width:440px;
    }

    /* ── Pills ── */
    .pills-row{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;max-width:640px;margin-bottom:0;}
    .pill-st-btn > button{
        background:rgba(255,255,255,0.04)!important;
        border:1px solid rgba(255,255,255,0.10)!important;
        border-radius:999px!important;
        color:rgba(200,195,240,0.72)!important;
        font-size:0.78rem!important;font-weight:600!important;
        padding:8px 18px!important;box-shadow:none!important;
        font-family:'Nunito',sans-serif!important;
    }
    .pill-st-btn > button:hover{
        background:rgba(124,58,237,0.18)!important;
        border-color:rgba(124,58,237,0.40)!important;
        color:#A78BFA!important;transform:translateY(-2px)!important;
        box-shadow:0 6px 20px rgba(124,58,237,0.20)!important;
    }

    /* ── Chat messages ── */
    .stChatMessage{margin-top:0!important;margin-bottom:0!important;padding:4px 0!important;}
    [data-testid="stChatMessage"]{
        background:transparent!important;
        border:none!important;border-radius:0!important;
        padding:4px 0!important;
        max-width:820px;margin:0 auto;width:100%;
    }
    /* User bubble */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stMarkdownContainer"]{
        background:linear-gradient(135deg,rgba(124,58,237,0.28),rgba(79,70,229,0.20))!important;
        border:1px solid rgba(124,58,237,0.32)!important;
        border-radius:16px 16px 4px 16px!important;
        padding:12px 16px!important;
        box-shadow:0 4px 20px rgba(124,58,237,0.15)!important;
        color:#F1F0FF!important;
        font-family:'Nunito',sans-serif!important;
        font-size:0.90rem!important;
    }
    /* AI bubble */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stMarkdownContainer"]{
        background:rgba(255,255,255,0.030)!important;
        border:1px solid rgba(255,255,255,0.07)!important;
        border-radius:16px 16px 16px 4px!important;
        padding:12px 16px!important;
        color:rgba(220,215,255,0.88)!important;
        font-family:'Nunito',sans-serif!important;
        font-size:0.90rem!important;
    }
    [data-testid="chatAvatarIcon-assistant"]{
        background:linear-gradient(135deg,#0F172A,#1E1B4B)!important;
        border:1px solid rgba(124,58,237,0.30)!important;
        color:#A78BFA!important;
        font-family:'JetBrains Mono',monospace!important;
        font-size:0.75rem!important;font-weight:700!important;
    }
    [data-testid="chatAvatarIcon-user"]{
        background:linear-gradient(135deg,#7C3AED,#4F46E5)!important;
        box-shadow:0 3px 10px rgba(124,58,237,0.35)!important;
    }

    /* ── st.chat_input custom styling ── */
    [data-testid="stChatInput"]{
        background:#0D0D1A!important;
        border:1.5px solid rgba(124,58,237,0.30)!important;
        border-radius:16px!important;
        padding:4px 8px!important;
        box-shadow:0 4px 32px rgba(0,0,0,0.40)!important;
        font-family:'Nunito',sans-serif!important;
    }
    [data-testid="stChatInput"]:focus-within{
        border-color:rgba(124,58,237,0.65)!important;
        box-shadow:0 0 0 3px rgba(124,58,237,0.14),0 6px 40px rgba(124,58,237,0.18)!important;
    }
    [data-testid="stChatInput"] textarea{
        color:#F1F0FF!important;background:transparent!important;
        font-family:'Nunito',sans-serif!important;font-size:0.94rem!important;
        caret-color:#A78BFA!important;
    }
    [data-testid="stChatInput"] textarea::placeholder{color:rgba(150,140,200,0.38)!important;}
    [data-testid="stChatInputSubmitButton"]{
        background:linear-gradient(135deg,#7C3AED,#4F46E5)!important;
        border-radius:50%!important;color:#fff!important;
        box-shadow:0 3px 14px rgba(124,58,237,0.40)!important;
    }

    /* ── Bottom bar wrapper ── */
    .chat-bottom-bar{
        position:fixed;bottom:0;left:258px;right:0;z-index:990;
        background:rgba(8,8,15,0.95);backdrop-filter:blur(24px);
        border-top:1px solid rgba(255,255,255,0.06);
        padding:10px 24px 14px;
    }
    .bottom-bar-inner{max-width:800px;margin:0 auto;}
    .bottom-hint{
        text-align:center;font-size:0.57rem;
        color:rgba(100,90,160,0.35);
        font-family:'JetBrains Mono',monospace;letter-spacing:0.4px;margin-top:6px;
    }

    /* Override Streamlit's own bottom chat input positioning */
    [data-testid="stBottom"]{
        left:258px!important;
        background:rgba(8,8,15,0.95)!important;
        border-top:1px solid rgba(255,255,255,0.06)!important;
        backdrop-filter:blur(24px)!important;
        padding:10px 24px 14px!important;
    }
    [data-testid="stBottom"] > div{max-width:800px;margin:0 auto!important;}

    /* Spacers */
    .chat-top-spacer{height:64px;}
    .chat-bot-spacer{height:100px;}
    .chat-messages-wrap{
        max-width:820px;margin:0 auto;
        padding:0 16px;width:100%;
    }
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
    # STREAMLIT-NATIVE CHAT (reliable messaging) + PREMIUM HTML CHROME
    # ──────────────────────────────────────────────────────────────────────
    nm       = st.session_state.student_name
    br       = st.session_state.branch
    sessions = st.session_state.chat_sessions

    # ── Build history HTML for sidebar ─────────────────────────────────
    history_items_html = ""
    if sessions:
        for i, sess in enumerate(reversed(sessions)):
            lbl = sess.get("label","Chat")[:34]
            history_items_html += f'<div class="hist-item"><span class="hist-dot"></span>{lbl}...</div>'
    else:
        history_items_html = '<div class="hist-empty">No saved chats yet</div>'

    # ── SIDEBAR (fixed left panel via HTML) ───────────────────────────────
    st.markdown(f'''
    <div class="chat-sidebar">
      <div class="sb-logo">
        <div class="sb-logo-row">
          <div class="sb-logo-icon">A</div>
          <div>
            <div class="sb-logo-text">AskMNIT</div>
            <div class="sb-logo-sub">AI ASSISTANT · MNIT JAIPUR</div>
          </div>
        </div>
      </div>
      <div class="sb-section">Navigation</div>
      <div class="sb-nav-item sb-nav-active"><span class="sb-nav-icon">💬</span> Chat</div>
      <div class="sb-section">Recent Chats</div>
      <div class="sb-history-scroll">{history_items_html}</div>
      <div class="erp-box">
        <div class="erp-title">🔐 ERP Login</div>
        <input class="erp-inp" id="erpUser" placeholder="College ID" />
        <input class="erp-inp" type="password" id="erpPass" placeholder="Password" />
        <button class="erp-btn" onclick="window.open('https://erp.mnit.ac.in/','_blank')">Login to ERP Portal →</button>
        <div class="erp-note">Opens official MNIT ERP in new tab</div>
      </div>
      <div class="sb-back" id="backDashBtn">← Back to Dashboard</div>
    </div>
    <script>
    document.getElementById('backDashBtn').onclick = function() {{
      var url = new URL(window.parent.location.href);
      url.searchParams.set('_back_dash', '1');
      window.parent.location.href = url.toString();
    }};
    </script>
    ''', unsafe_allow_html=True)

    # ── TOPBAR ────────────────────────────────────────────────────────────
    st.markdown(f'''
    <div class="chat-navbar">
      <div class="nb-model">
        <span class="nb-model-dot"></span>
        AskMNIT AI &nbsp;·&nbsp; LLaMA 3.3 70B
      </div>
      <div class="nb-actions">
        <div class="nb-btn" onclick="
          var url=new URL(window.parent.location.href);
          url.searchParams.set('_new_chat', Date.now());
          window.parent.location.href=url.toString();">
          + New Chat
        </div>
      </div>
    </div>
    <div class="chat-top-spacer"></div>
    ''', unsafe_allow_html=True)

    # ── HERO (empty state) ─────────────────────────────────────────────────
    if not has_messages:
        st.markdown(f'''
        <div class="hero-section">
          <div class="hero-orb">🎓</div>
          <div class="hero-title">Hey {nm.split()[0]}, ready?</div>
          <div class="hero-sub">Your AI senior at MNIT Jaipur — attendance, schedule, PYQs, exam strategy, everything.</div>
        </div>
        ''', unsafe_allow_html=True)

        # Suggestion pills — 2 rows via Streamlit columns
        branch = st.session_state.branch
        PILLS = [
            f"📊 Analyse my attendance",
            f"📅 Next class today?",
            f"📚 PYQs for {branch}",
            f"💸 Fee status check",
            f"📖 Subjects this sem",
            f"🎯 Exam tips for me",
        ]
        st.markdown('<div class="chat-messages-wrap"><div class="pills-row">', unsafe_allow_html=True)
        cols = st.columns(len(PILLS))
        for i, (pill, col) in enumerate(zip(PILLS, cols)):
            with col:
                st.markdown('<div class="pill-st-btn">', unsafe_allow_html=True)
                if st.button(pill, key=f"pill_{i}", use_container_width=True):
                    dispatch_message(pill)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)
        st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)

    # ── CHAT MESSAGES (Streamlit native — always works) ────────────────────
    else:
        st.markdown('<div class="chat-messages-wrap">', unsafe_allow_html=True)
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chat-bot-spacer"></div>', unsafe_allow_html=True)

    # ── CHAT INPUT — Streamlit native (100% reliable) ─────────────────────
    user_input = st.chat_input(
        "Ask AskMNIT anything...",
        key="main_chat_input"
    )
    if user_input:
        dispatch_message(user_input.strip())
        st.rerun()

    # ── Handle back-to-dashboard via query param ───────────────────────────
    if st.query_params.get("_back_dash"):
        try: del st.query_params["_back_dash"]
        except: pass
        st.session_state.view = "dashboard"
        st.rerun()

    if st.query_params.get("_new_chat"):
        try: del st.query_params["_new_chat"]
        except: pass
        if st.session_state.chat_messages:
            fu = next((m["content"][:38] for m in st.session_state.chat_messages if m["role"]=="user"), "Session")
            st.session_state.chat_sessions.append({"label": fu, "messages": list(st.session_state.chat_messages)})
        st.session_state.chat_messages = []
        st.session_state.attached_file_name = ""
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
