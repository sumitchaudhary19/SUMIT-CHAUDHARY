# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  AskMNIT — Premium AI Assistant + Student Dashboard                         ║
# ║  v7.0 — New Premium Chatbot Design                                          ║
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
    # Chat state
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
    "show_history_panel":  False,
    "show_settings_panel": False,
    "sb_open":             True,
    "erp_panel":           False,
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
        att_summary += "BELOW 75%:\n"
        for s, p in low:
            r = att[s]
            need = max(0, int((0.75 * r["total"] - r["present"]) / 0.25) + 1)
            att_summary += f"  - {s}: {p}% — needs {need} more\n"
    if good:
        att_summary += "Above 75%: " + ", ".join(f"{s}:{p}%" for s,p in good[:4]) + "\n"
    sched_summary = "Schedule not uploaded yet."
    if st.session_state.schedule_loaded:
        today_slots = get_today_slots(st.session_state.full_schedule)
        nxt = get_next_class(today_slots)
        dn  = datetime.datetime.now().strftime("%A")
        if today_slots:
            sched_summary = f"Today ({dn}): " + ", ".join(f"{fmt_time(sl['time_start'])} {sl['subject']}" for sl in today_slots)
            if nxt: sched_summary += f"\nNext: {nxt['subject']} in {nxt['minutes_away']} min"
        else:
            sched_summary = f"No classes today ({dn})."
    return f"Student: {nm} | Branch: {br} | Semester: {sem}\nAttendance: {att_summary}\nSchedule: {sched_summary}\nResponse style: {st.session_state.response_style}"

def _detect_mood(text):
    t = text.lower()
    if any(w in t for w in ["stressed","tension","worried","fail","rona","confused"]): return "STRESSED — warm first"
    if any(w in t for w in ["happy","khush","cleared","yay","hogaya"]): return "EXCITED — vibe first"
    if any(w in t for w in ["angry","gussa","bakwas","frustrat"]): return "FRUSTRATED — validate first"
    if any(w in t for w in ["thak","tired","neend","exhausted"]): return "TIRED — gentle"
    return "NEUTRAL — friendly"

def generate_ai_response(last: str) -> str:
    import requests
    nm = st.session_state.student_name.split()[0]
    br = st.session_state.branch
    system_prompt = f"""You are AskMNIT — {nm}'s brilliant senior at MNIT Jaipur.
Mood hint: {_detect_mood(last)}
{_build_student_context()}

Rules: Call them "{nm}" or "yaar/bhai". Be natural, Hinglish ok. Never say "I'm an AI".
Keep it conversational and punchy."""

    history = st.session_state.chat_messages[:-1]
    api_msgs = [{"role":m["role"],"content":m["content"]} for m in history[-14:]]
    api_msgs.append({"role":"user","content":last})

    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY","") or st.session_state.get("groq_api_key","")
    if not GROQ_API_KEY:
        return f"Yaar, Groq API key set nahi hai 😅\n\n`.streamlit/secrets.toml` mein `GROQ_API_KEY = 'gsk_...'` add kar!"
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile","messages":[{"role":"system","content":system_prompt},*api_msgs],
                  "max_tokens":900,"temperature":0.82,"top_p":0.90,"stream":False},
            timeout=30,
        )
        data = resp.json()
        if resp.status_code == 200:
            return data["choices"][0]["message"]["content"].strip()
        err = data.get("error",{}).get("message","Unknown error")
        return f"Groq API error 😬\n`{err}`"
    except requests.Timeout:
        return "Connection slow hai ⏳ — ek minute ruk ke try kar!"
    except Exception as e:
        return f"Kuch gadbad hai 😅 ({str(e)[:80]})"

def dispatch_message(text: str):
    text = text.strip()
    if not text: return
    st.session_state.chat_messages.append({"role":"user","content":text})
    with st.spinner(""):
        reply = generate_ai_response(text)
    st.session_state.chat_messages.append({"role":"assistant","content":reply})

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS — Dashboard only styles
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500&family=Outfit:wght@300;400;500;600;700&display=swap');

*,html,body{box-sizing:border-box;margin:0;padding:0;}
html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"]{font-family:'Outfit',sans-serif!important;background:#070B14!important;color:#E2E8F0!important;}
header[data-testid="stHeader"],footer,#MainMenu,[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important;}
[data-testid="stMainBlockContainer"]{padding:0!important;max-width:100%!important;}
[data-testid="stSidebar"]{background:#0B1120!important;border-right:1px solid rgba(59,130,246,0.16)!important;min-width:260px!important;max-width:260px!important;}
[data-testid="stSidebar"]>div{padding:0!important;}
.sb-section-header{font-family:'JetBrains Mono',monospace;font-size:0.60rem;font-weight:700;color:rgba(148,163,184,0.50);text-transform:uppercase;letter-spacing:1.4px;padding:14px 16px 6px;border-top:1px solid rgba(255,255,255,0.05);margin-top:4px;}
.sb-history-item{display:flex;align-items:center;gap:8px;padding:7px 16px;cursor:pointer;font-size:0.80rem;color:rgba(148,163,184,0.70);border-bottom:1px solid rgba(255,255,255,0.03);}
.sb-history-item:hover{background:rgba(59,130,246,0.09);color:#BAE6FD;}
.sb-history-dot{width:5px;height:5px;border-radius:50%;background:#3B82F6;flex-shrink:0;}
[data-testid="stSidebar"] .stButton>button{background:rgba(239,68,68,0.10)!important;border:1px solid rgba(239,68,68,0.28)!important;color:#FCA5A5!important;border-radius:8px!important;font-size:0.80rem!important;font-weight:600!important;padding:7px 14px!important;box-shadow:none!important;}
[data-testid="stSidebar"] .stButton>button:hover{background:rgba(239,68,68,0.20)!important;transform:none!important;}
.stButton>button{background:linear-gradient(135deg,#2563EB,#4F46E5)!important;color:#fff!important;border:none!important;border-radius:9px!important;font-family:'Outfit',sans-serif!important;font-weight:600!important;font-size:0.82rem!important;padding:9px 16px!important;box-shadow:0 3px 14px rgba(37,99,235,0.20)!important;transition:all 0.16s ease!important;}
.stButton>button:hover{opacity:.88!important;transform:translateY(-1px)!important;}
.ghost-btn .stButton>button{background:rgba(255,255,255,.05)!important;border:1px solid rgba(255,255,255,0.14)!important;color:rgba(226,232,240,.55)!important;box-shadow:none!important;}
.present-btn .stButton>button{background:linear-gradient(135deg,#065F46,#10B981)!important;box-shadow:0 2px 10px rgba(16,185,129,.18)!important;padding:6px 11px!important;font-size:0.75rem!important;border-radius:7px!important;}
.absent-btn .stButton>button{background:linear-gradient(135deg,#7F1D1D,#EF4444)!important;box-shadow:0 2px 10px rgba(239,68,68,.16)!important;padding:6px 11px!important;font-size:0.75rem!important;border-radius:7px!important;}
.save-btn .stButton>button{background:linear-gradient(135deg,#92400E,#F59E0B)!important;padding:7px 13px!important;font-size:0.77rem!important;}
.pin-btn .stButton>button{background:rgba(245,158,11,0.10)!important;border:1px solid rgba(245,158,11,0.28)!important;color:#FCD34D!important;box-shadow:none!important;font-size:0.70rem!important;padding:4px 10px!important;border-radius:7px!important;}
.del-btn .stButton>button{background:rgba(239,68,68,0.07)!important;border:1px solid rgba(239,68,68,0.18)!important;color:rgba(252,165,165,0.70)!important;box-shadow:none!important;font-size:0.68rem!important;padding:3px 8px!important;border-radius:6px!important;}
.ql-btn .stButton>button{background:rgba(255,255,255,.03)!important;border:1px solid rgba(255,255,255,0.14)!important;color:rgba(186,230,253,.65)!important;box-shadow:none!important;text-align:left!important;justify-content:flex-start!important;font-size:0.80rem!important;padding:9px 14px!important;border-radius:9px!important;}
.logout-btn .stButton>button{background:rgba(239,68,68,.09)!important;border:1px solid rgba(239,68,68,.20)!important;color:#FCA5A5!important;box-shadow:none!important;font-size:0.80rem!important;}
.open-chat-btn .stButton>button{background:linear-gradient(135deg,#7C3AED,#A855F7)!important;border-radius:12px!important;font-weight:700!important;font-size:0.88rem!important;padding:11px 22px!important;box-shadow:0 5px 24px rgba(124,58,237,.40)!important;font-family:'Syne',sans-serif!important;}
.settings-menu-btn .stButton>button{background:rgba(255,255,255,0.06)!important;border:1px solid rgba(255,255,255,0.12)!important;color:rgba(226,232,240,0.75)!important;box-shadow:none!important;font-size:0.82rem!important;font-weight:600!important;padding:8px 16px!important;border-radius:10px!important;}
.nav-btn .stButton>button{background:transparent!important;color:rgba(148,163,184,.65)!important;border:none!important;box-shadow:none!important;text-align:left!important;justify-content:flex-start!important;padding:10px 14px!important;font-size:0.83rem!important;font-weight:500!important;border-radius:8px!important;}
.nav-btn .stButton>button:hover{background:rgba(59,130,246,.10)!important;color:#BAE6FD!important;transform:none!important;}
.nav-btn-active .stButton>button{background:rgba(59,130,246,.14)!important;color:#60A5FA!important;border-left:2px solid #3B82F6!important;font-weight:700!important;box-shadow:none!important;}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{background:rgba(255,255,255,0.04)!important;border:1px solid rgba(255,255,255,0.14)!important;border-radius:10px!important;color:#E2E8F0!important;font-family:'Outfit',sans-serif!important;font-size:0.87rem!important;}
[data-testid="stTextInput"] input:focus{border-color:rgba(59,130,246,0.55)!important;box-shadow:0 0 0 2.5px rgba(59,130,246,0.13)!important;}
[data-testid="stTextInput"] label,[data-testid="stTextArea"] label{color:rgba(148,163,184,0.55)!important;font-size:0.70rem!important;font-weight:600!important;text-transform:uppercase!important;letter-spacing:0.6px!important;}
[data-testid="stSelectbox"]>div>div{background:rgba(255,255,255,0.04)!important;border:1px solid rgba(255,255,255,0.14)!important;border-radius:10px!important;color:#E2E8F0!important;}
[data-testid="stFileUploader"]{background:rgba(59,130,246,0.04)!important;border:1px dashed rgba(59,130,246,0.26)!important;border-radius:12px!important;}
[data-testid="stToggle"] label{color:#E2E8F0!important;font-size:0.86rem!important;}
[data-testid="stExpander"]{background:rgba(255,255,255,.018)!important;border:1px solid rgba(255,255,255,0.08)!important;border-radius:12px!important;}
[data-testid="stProgress"]>div>div{border-radius:99px!important;background:linear-gradient(90deg,#7C3AED,#A855F7)!important;}
[data-testid="stProgress"]>div{background:rgba(255,255,255,.07)!important;border-radius:99px!important;height:5px!important;}
h1,h2,h3,h4{font-family:'Syne',sans-serif!important;font-weight:700!important;}
[data-testid="stMarkdown"] p,[data-testid="stMarkdown"] li{color:rgba(226,232,240,.72)!important;font-family:'Outfit',sans-serif!important;}
hr{border-color:rgba(255,255,255,0.08)!important;}
::-webkit-scrollbar{width:4px;height:4px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:rgba(124,58,237,.30);border-radius:4px;}
[data-testid="column"]{padding:0 4px!important;}
</style>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# VIEW ROUTER
# ═════════════════════════════════════════════════════════════════════════════
view = st.session_state.view

###############################################################################
# ████████████████████████  CHAT VIEW — NEW PREMIUM DESIGN  ██████████████████
###############################################################################
if view == "chat":

    # Hide Streamlit sidebar completely
    st.markdown("""
    <style>
    [data-testid="stSidebar"]{display:none!important;}
    [data-testid="stSidebarCollapseButton"]{display:none!important;}
    [data-testid="collapsedControl"]{display:none!important;}
    section[data-testid="stMain"]{margin-left:0!important;padding-left:0!important;}
    html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"]{
      background:#0D0618!important;
    }
    </style>
    """, unsafe_allow_html=True)

    has_messages = len(st.session_state.chat_messages) > 0

    # ── Handle voice done ────────────────────────────────────────────────
    for rkey in ["hero","anchored"]:
        vdone = st.query_params.get(f"vr_{rkey}","")
        if vdone == "DONE" and not st.session_state.get("_voice_submit"):
            st.session_state._voice_submit = True
            st.session_state.is_recording  = False
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

    # ── Handle file picker ───────────────────────────────────────────────
    for rkey in ["hero","anchored"]:
        fpname = st.query_params.get(f"fp_{rkey}","")
        if fpname and fpname != st.session_state.attached_file_name:
            st.session_state.attached_file_name = fpname
            st.toast(f"📎 {fpname}", icon="✅")
            try: del st.query_params[f"fp_{rkey}"]
            except: pass
            st.rerun()

    # ── Sidebar open/close ───────────────────────────────────────────────
    if "sb_open" not in st.session_state:
        st.session_state.sb_open = True
    if "erp_panel" not in st.session_state:
        st.session_state.erp_panel = False

    # ════════════════════════════════════════════════════════════════════
    # INJECT THE ENTIRE PREMIUM CHATBOT UI via components.html
    # ════════════════════════════════════════════════════════════════════
    _msgs_json = []
    for m in st.session_state.chat_messages[-60:]:
        _msgs_json.append({"role": m["role"], "content": m["content"]})

    import json as _json
    _msgs_str = _json.dumps(_msgs_json)
    _sb_open_str = "true" if st.session_state.sb_open else "false"
    _has_msgs = "true" if has_messages else "false"
    _student  = st.session_state.student_name.split()[0]
    _branch   = st.session_state.branch

    components.html(f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500&family=Outfit:wght@300;400;500;600;700&display=swap');

*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{
  font-family:'Outfit',sans-serif;
  background:#0D0618;
  color:#E8DCFF;
  height:100vh;
  width:100%;
  overflow:hidden;
}}

/* ══ ANIMATED BACKGROUND ══════════════════════════════════════════════ */
.bg-canvas{{
  position:fixed;inset:0;z-index:0;
  background:
    radial-gradient(ellipse 80% 60% at 20% 20%, rgba(124,58,237,0.18) 0%, transparent 60%),
    radial-gradient(ellipse 60% 50% at 80% 80%, rgba(168,85,247,0.12) 0%, transparent 60%),
    radial-gradient(ellipse 40% 40% at 50% 50%, rgba(76,29,149,0.08) 0%, transparent 70%),
    #0D0618;
}}
.bg-orb{{
  position:fixed;border-radius:50%;filter:blur(80px);
  animation:orbFloat 8s ease-in-out infinite;pointer-events:none;z-index:0;
}}
.bg-orb-1{{
  width:400px;height:400px;
  background:radial-gradient(circle,rgba(124,58,237,0.22),transparent 70%);
  top:-100px;left:-100px;animation-delay:0s;
}}
.bg-orb-2{{
  width:350px;height:350px;
  background:radial-gradient(circle,rgba(168,85,247,0.18),transparent 70%);
  bottom:-80px;right:-80px;animation-delay:-3s;
}}
.bg-orb-3{{
  width:250px;height:250px;
  background:radial-gradient(circle,rgba(139,92,246,0.12),transparent 70%);
  top:40%;left:60%;animation-delay:-5s;
}}
@keyframes orbFloat{{
  0%,100%{{transform:translate(0,0) scale(1);}}
  33%{{transform:translate(30px,-30px) scale(1.05);}}
  66%{{transform:translate(-20px,20px) scale(0.95);}}
}}

/* Grid overlay */
.bg-grid{{
  position:fixed;inset:0;z-index:0;pointer-events:none;
  background-image:
    linear-gradient(rgba(124,58,237,0.04) 1px,transparent 1px),
    linear-gradient(90deg,rgba(124,58,237,0.04) 1px,transparent 1px);
  background-size:60px 60px;
  mask-image:radial-gradient(ellipse at center,black 30%,transparent 80%);
}}

/* ══ LAYOUT ═══════════════════════════════════════════════════════════ */
.app-shell{{
  position:fixed;inset:0;
  display:flex;z-index:1;
}}

/* ══ LEFT SIDEBAR ══════════════════════════════════════════════════════ */
.sidebar{
  width:240px;
  min-width:240px;
  flex-shrink:0;
  background:rgba(15,7,36,0.92);
  border-right:1px solid rgba(124,58,237,0.22);
  display:flex;
  flex-direction:column;
  transition:width 0.28s cubic-bezier(0.22,0.61,0.36,1),
             min-width 0.28s cubic-bezier(0.22,0.61,0.36,1),
             opacity 0.22s ease;
  z-index:50;
  overflow:hidden;
  position:relative;
  box-shadow:4px 0 32px rgba(60,10,120,0.20);
}
.sidebar.collapsed{
  width:0;
  min-width:0;
  opacity:0;
  pointer-events:none;
  border-right:none;
}
.sb-header{{
  padding:20px 16px 14px;
  border-bottom:1px solid rgba(124,58,237,0.14);
  display:flex;align-items:center;gap:10px;
}}
.sb-logo-icon{{
  width:32px;height:32px;border-radius:9px;
  background:linear-gradient(135deg,#7C3AED,#A855F7);
  display:flex;align-items:center;justify-content:center;
  font-size:0.88rem;font-weight:800;color:#fff;
  box-shadow:0 4px 14px rgba(124,58,237,0.45);
  font-family:'Syne',sans-serif;flex-shrink:0;
}}
.sb-logo-name{{font-family:'Syne',sans-serif;font-size:0.92rem;font-weight:700;color:#E8DCFF;}}
.sb-logo-sub{{font-size:0.52rem;color:rgba(168,140,255,0.45);margin-top:1px;}}

.sb-section{{padding:10px 10px 4px;}}
.sb-section-label{{
  font-family:'JetBrains Mono',monospace;
  font-size:0.52rem;color:rgba(168,140,255,0.38);
  text-transform:uppercase;letter-spacing:1.8px;
  padding:0 6px 6px;
}}

.sb-item{{
  display:flex;align-items:center;gap:10px;
  padding:9px 12px;border-radius:10px;
  cursor:pointer;user-select:none;
  font-size:0.82rem;font-weight:500;
  color:rgba(210,190,255,0.65);
  transition:all 0.14s ease;
  border:1px solid transparent;
  margin-bottom:2px;
}}
.sb-item:hover{{
  background:rgba(124,58,237,0.14);
  border-color:rgba(168,85,247,0.22);
  color:#DDD0FF;
}}
.sb-item.active{{
  background:rgba(124,58,237,0.20);
  border-color:rgba(168,85,247,0.35);
  color:#EDE0FF;
}}
.sb-item.new-chat{{
  background:rgba(124,58,237,0.22);
  border-color:rgba(168,85,247,0.40);
  color:#E8DCFF;font-weight:600;
  margin:10px 0 4px;
}}
.sb-item.new-chat:hover{{
  background:rgba(124,58,237,0.32);
  box-shadow:0 4px 16px rgba(124,58,237,0.25);
}}
.sb-icon{{font-size:0.92rem;width:20px;text-align:center;flex-shrink:0;}}

.sb-chat-history{{
  flex:1;overflow-y:auto;padding:0 10px;
}}
.sb-chat-history::-webkit-scrollbar{{width:3px;}}
.sb-chat-history::-webkit-scrollbar-thumb{{background:rgba(124,58,237,0.25);border-radius:3px;}}
.sb-hist-item{{
  display:flex;align-items:center;gap:7px;
  padding:7px 10px;border-radius:8px;
  cursor:pointer;font-size:0.74rem;
  color:rgba(180,160,220,0.55);
  transition:all 0.12s;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
}}
.sb-hist-item:hover{{background:rgba(124,58,237,0.10);color:rgba(210,190,255,0.80);}}
.sb-hist-dot{{width:4px;height:4px;border-radius:50%;background:rgba(168,85,247,0.40);flex-shrink:0;}}

.sb-footer{{
  padding:12px 10px;
  border-top:1px solid rgba(124,58,237,0.12);
}}

/* ══ MAIN CONTENT ══════════════════════════════════════════════════════ */
.main-content{{
  flex:1;
  display:flex;
  flex-direction:column;
  overflow:hidden;
  position:relative;
  transition:all 0.30s ease;
}}

/* ══ TOP BAR ══════════════════════════════════════════════════════════ */
.topbar{
  height:52px;
  background:rgba(13,6,24,0.90);
  border-bottom:1px solid rgba(124,58,237,0.16);
  display:flex;align-items:center;
  padding:0 16px;
  gap:10px;
  flex-shrink:0;
  z-index:40;
  position:sticky;top:0;
}
.topbar-toggle{{
  width:34px;height:34px;border-radius:9px;
  background:rgba(124,58,237,0.15);
  border:1px solid rgba(168,85,247,0.28);
  cursor:pointer;
  display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:4.5px;
  transition:all 0.16s ease;flex-shrink:0;
}}
.topbar-toggle:hover{{background:rgba(124,58,237,0.28);border-color:rgba(168,85,247,0.50);}}
.tb-bar{{display:block;width:14px;height:1.5px;background:rgba(220,200,255,0.82);border-radius:2px;transition:all 0.22s ease;}}
.topbar-title{{
  font-family:'Syne',sans-serif;font-size:0.90rem;font-weight:600;
  color:rgba(220,200,255,0.80);flex:1;
}}
.topbar-badge{{
  font-family:'JetBrains Mono',monospace;
  font-size:0.60rem;padding:3px 8px;border-radius:6px;
  background:rgba(124,58,237,0.20);border:1px solid rgba(168,85,247,0.28);
  color:rgba(180,150,255,0.80);
}}

/* ══ CHAT AREA ════════════════════════════════════════════════════════ */
.chat-area{{
  flex:1;
  overflow-y:auto;
  padding:20px 0 20px;
  display:flex;
  flex-direction:column;
}}
.chat-area::-webkit-scrollbar{{width:4px;}}
.chat-area::-webkit-scrollbar-thumb{{background:rgba(124,58,237,0.25);border-radius:4px;}}

/* ── Hero center (before 1st message) ── */
.hero-center{{
  flex:1;
  display:flex;flex-direction:column;
  align-items:center;justify-content:center;
  padding:20px 24px;
  text-align:center;
  animation:fadeUp 0.50s ease both;
}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(20px);}}to{{opacity:1;transform:translateY(0);}}}}

.hero-orb{{
  width:80px;height:80px;border-radius:50%;
  background:conic-gradient(from 0deg,#7C3AED,#A855F7,#C084FC,#7C3AED);
  display:flex;align-items:center;justify-content:center;
  margin-bottom:20px;
  animation:orbSpin 8s linear infinite, orb3d 4s ease-in-out infinite;
  box-shadow:0 0 0 1px rgba(168,85,247,0.30), 0 16px 60px rgba(124,58,237,0.50);
  position:relative;
}}
.hero-orb::before{{
  content:'';position:absolute;inset:3px;border-radius:50%;
  background:radial-gradient(circle at 35% 35%,rgba(255,255,255,0.25),transparent 60%),
    conic-gradient(from 120deg,#4C1D95,#7C3AED,#A855F7,#4C1D95);
}}
.hero-orb-emoji{{position:relative;z-index:1;font-size:1.8rem;}}
@keyframes orbSpin{{from{{filter:hue-rotate(0deg);}}to{{filter:hue-rotate(360deg);}}}}
@keyframes orb3d{{
  0%,100%{{transform:scale(1) rotateY(0deg);box-shadow:0 0 0 1px rgba(168,85,247,0.30),0 16px 60px rgba(124,58,237,0.50);}}
  50%{{transform:scale(1.05) rotateY(10deg);box-shadow:0 0 0 2px rgba(168,85,247,0.45),0 24px 80px rgba(124,58,237,0.65);}}
}}

.hero-title{{
  font-family:'Syne',sans-serif;font-size:2.2rem;font-weight:800;
  background:linear-gradient(135deg,#EDE0FF 0%,#C084FC 50%,#A855F7 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  letter-spacing:-1px;margin-bottom:8px;
}}
.hero-sub{{
  font-size:0.84rem;color:rgba(180,160,220,0.55);
  line-height:1.65;max-width:380px;
}}

/* Suggestion chips */
.sugg-row{{
  display:flex;flex-wrap:wrap;gap:8px;
  justify-content:center;margin-top:20px;
  max-width:580px;
}}
.sugg-chip{{
  display:inline-flex;align-items:center;gap:6px;
  padding:8px 14px;border-radius:22px;
  background:rgba(124,58,237,0.10);
  border:1px solid rgba(168,85,247,0.22);
  color:rgba(200,180,255,0.75);
  font-size:0.76rem;font-weight:500;
  cursor:pointer;user-select:none;
  transition:all 0.16s ease;
  white-space:nowrap;
}}
.sugg-chip:hover{{
  background:rgba(124,58,237,0.22);
  border-color:rgba(168,85,247,0.45);
  color:#E0CCFF;
  transform:translateY(-2px);
  box-shadow:0 6px 20px rgba(124,58,237,0.25);
}}
.sugg-chip-icon{{font-size:0.82rem;}}

/* ── Messages ── */
.msgs-container{{
  display:flex;flex-direction:column;gap:16px;
  padding:0 20px;max-width:780px;width:100%;margin:0 auto;
}}
.msg-bubble{{
  display:flex;gap:10px;
  animation:msgIn 0.22s ease both;
}}
@keyframes msgIn{{from{{opacity:0;transform:translateY(8px);}}to{{opacity:1;transform:translateY(0);}}}}
.msg-bubble.user{{flex-direction:row-reverse;}}
.msg-avatar{{
  width:32px;height:32px;border-radius:9px;
  display:flex;align-items:center;justify-content:center;
  font-size:0.82rem;font-weight:700;flex-shrink:0;
  box-shadow:0 2px 10px rgba(0,0,0,0.25);
}}
.msg-avatar.ai{{background:linear-gradient(135deg,#7C3AED,#A855F7);color:#fff;}}
.msg-avatar.user{{background:rgba(255,255,255,0.10);color:rgba(220,200,255,0.80);border:1px solid rgba(255,255,255,0.12);}}
.msg-text{{
  max-width:72%;
  padding:11px 15px;
  border-radius:14px;
  font-size:0.86rem;line-height:1.65;
}}
.msg-text.ai{{
  background:rgba(30,12,60,0.70);
  border:1px solid rgba(124,58,237,0.22);
  color:rgba(220,200,255,0.90);
  border-radius:4px 14px 14px 14px;
}}
.msg-text.user{{
  background:rgba(124,58,237,0.22);
  border:1px solid rgba(168,85,247,0.35);
  color:#EDE0FF;
  border-radius:14px 4px 14px 14px;
}}
.msg-text pre{{
  background:rgba(0,0,0,0.35);border-radius:8px;padding:10px 12px;
  font-family:'JetBrains Mono',monospace;font-size:0.78rem;
  overflow-x:auto;margin:8px 0;
  border:1px solid rgba(124,58,237,0.20);
}}

/* Typing indicator */
.typing-indicator{{
  display:flex;align-items:center;gap:5px;padding:10px 14px;
}}
.typing-dot{{
  width:7px;height:7px;border-radius:50%;
  background:rgba(168,85,247,0.70);
  animation:typingBounce 1.2s ease-in-out infinite;
}}
.typing-dot:nth-child(2){{animation-delay:0.16s;}}
.typing-dot:nth-child(3){{animation-delay:0.32s;}}
@keyframes typingBounce{{0%,80%,100%{{transform:scale(0.7);opacity:0.4;}}40%{{transform:scale(1.1);opacity:1;}}}}

/* ══ INPUT AREA ════════════════════════════════════════════════════════ */
.input-area{{
  flex-shrink:0;
  padding:12px 20px 16px;
  background:rgba(13,6,24,0.60);
  backdrop-filter:blur(20px);
  border-top:1px solid rgba(124,58,237,0.12);
}}
.input-area.hero-mode{{
  background:transparent;
  border-top:none;
  padding:0 20px 20px;
}}
.input-shell{{
  max-width:680px;margin:0 auto;
  background:rgba(22,10,50,0.88);
  border:1.5px solid rgba(124,58,237,0.35);
  border-radius:20px;
  box-shadow:
    0 8px 40px rgba(124,58,237,0.22),
    0 2px 0 rgba(168,85,247,0.12) inset,
    0 -1px 0 rgba(30,5,60,0.60) inset;
  transition:all 0.20s ease;
  overflow:hidden;
}}
.input-shell:focus-within{{
  border-color:rgba(168,85,247,0.65);
  box-shadow:
    0 0 0 3px rgba(124,58,237,0.18),
    0 10px 50px rgba(124,58,237,0.35),
    0 2px 0 rgba(200,140,255,0.18) inset;
}}

/* Shine animation */
@keyframes inputShine{{
  0%{{background-position:200% center;}}
  100%{{background-position:-200% center;}}
}}
.input-shell::before{{
  content:'';display:block;
  height:1px;
  background:linear-gradient(90deg,transparent,rgba(168,85,247,0.50),rgba(200,160,255,0.30),transparent);
  background-size:200% 100%;
  animation:inputShine 4s linear infinite;
}}

.input-row{{
  display:flex;align-items:center;gap:0;
  padding:4px 6px 4px 12px;
  min-height:56px;
}}
.input-field{{
  flex:1;background:transparent;border:none;outline:none;
  color:#EDE0FF;font-family:'Outfit',sans-serif;font-size:0.94rem;
  caret-color:#C084FC;
  padding:8px 0;
}}
.input-field::placeholder{{color:rgba(168,140,200,0.45);}}
.input-actions{{display:flex;align-items:center;gap:5px;flex-shrink:0;}}

.ib-btn{{
  width:36px;height:36px;border-radius:10px;
  background:transparent;border:none;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  color:rgba(180,150,220,0.55);font-size:1.0rem;
  transition:all 0.14s ease;
}}
.ib-btn:hover{{background:rgba(124,58,237,0.18);color:rgba(200,170,255,0.90);}}
.ib-btn.active{{background:rgba(239,68,68,0.18);color:#FCA5A5;animation:micPulse 1.1s infinite;}}
@keyframes micPulse{{0%,100%{{box-shadow:0 0 0 0 rgba(239,68,68,0.40);}}50%{{box-shadow:0 0 0 6px rgba(239,68,68,0.00);}}}}

.send-btn{{
  width:38px;height:38px;border-radius:12px;
  background:linear-gradient(135deg,#7C3AED,#A855F7);
  border:none;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  color:#fff;font-size:1.1rem;
  box-shadow:0 4px 16px rgba(124,58,237,0.45);
  transition:all 0.14s ease;
  margin-left:3px;
}}
.send-btn:hover{{
  box-shadow:0 6px 24px rgba(124,58,237,0.60);
  transform:scale(1.06);
}}
.send-btn:active{{transform:scale(0.94);}}

/* File chip */
.file-chip-strip{{display:flex;align-items:center;gap:6px;padding:6px 12px 0;}}
.file-chip{{
  display:inline-flex;align-items:center;gap:5px;
  background:rgba(124,58,237,0.14);
  border:1px solid rgba(168,85,247,0.30);
  border-radius:16px;padding:3px 10px 3px 8px;
  font-size:0.70rem;color:rgba(200,180,255,0.85);font-weight:600;
}}
.file-chip-rm{{background:none;border:none;color:rgba(168,140,200,0.55);cursor:pointer;font-size:0.75rem;margin-left:3px;}}

/* Input hint */
.input-hint{{
  text-align:center;padding:6px 0 0;
  font-size:0.58rem;color:rgba(120,90,160,0.42);
  font-family:'JetBrains Mono',monospace;
}}

/* ══ MISC ═════════════════════════════════════════════════════════════ */
.overlay{
  display:none;
}
.overlay.show{
  display:none;
}

/* Scrollbar placeholder for chat messages container */
.msgs-wrap{{flex:1;overflow-y:auto;}}
.msgs-wrap::-webkit-scrollbar{{width:4px;}}
.msgs-wrap::-webkit-scrollbar-thumb{{background:rgba(124,58,237,0.25);border-radius:4px;}}

.listening-pill{{
  display:inline-flex;align-items:center;gap:7px;
  background:rgba(239,68,68,0.10);border:1px solid rgba(239,68,68,0.28);
  border-radius:20px;padding:5px 12px;margin:6px auto;
  font-size:0.75rem;color:#FCA5A5;
}}
.listen-dot{{width:6px;height:6px;border-radius:50%;background:#EF4444;animation:blinkDot 1s infinite;}}
@keyframes blinkDot{{0%,100%{{opacity:1;}}50%{{opacity:0.2;}}}}

</style>
</head>
<body>

<div class="bg-canvas"></div>
<div class="bg-grid"></div>
<div class="bg-orb bg-orb-1"></div>
<div class="bg-orb bg-orb-2"></div>
<div class="bg-orb bg-orb-3"></div>

<div class="overlay" id="overlay" onclick="closeSidebar()"></div>

<div class="app-shell">

  <!-- ═══ LEFT SIDEBAR ═══════════════════════════════════════════════ -->
  <div class="sidebar {'collapsed' if not st.session_state.sb_open else ''}" id="sidebar">

    <div class="sb-header">
      <div class="sb-logo-icon">A</div>
      <div>
        <div class="sb-logo-name">AskMNIT</div>
        <div class="sb-logo-sub">MNIT Jaipur · AI</div>
      </div>
    </div>

    <div class="sb-section">
      <div class="sb-item new-chat" onclick="sendAction('new_chat')">
        <span class="sb-icon">✦</span> New Chat
      </div>
    </div>

    <div class="sb-section">
      <div class="sb-section-label">Navigation</div>
      <div class="sb-item" onclick="sendAction('erp')">
        <span class="sb-icon">🔐</span> ERP Login
      </div>
      <div class="sb-item {'active' if st.session_state.show_history_panel else ''}" onclick="sendAction('history')">
        <span class="sb-icon">🕐</span> Chat History
      </div>
      <div class="sb-item" onclick="sendAction('dashboard')">
        <span class="sb-icon">⊞</span> Dashboard
      </div>
    </div>

    <div class="sb-section" style="flex:1;display:flex;flex-direction:column;overflow:hidden;">
      <div class="sb-section-label">Recent Chats</div>
      <div class="sb-chat-history" id="chatHistoryList">
        {"".join(f'<div class="sb-hist-item"><span class="sb-hist-dot"></span>{s.get("label","Chat")[:35]}...</div>' for s in list(reversed(st.session_state.chat_sessions[-8:]))) if st.session_state.chat_sessions else '<div style="padding:8px 10px;font-size:0.72rem;color:rgba(140,110,180,0.40);">No chats yet...</div>'}
      </div>
    </div>

    <div class="sb-footer">
      <div class="sb-item" onclick="sendAction('settings')">
        <span class="sb-icon">⚙</span> Settings
      </div>
      <div style="margin-top:10px;padding:8px 6px;border-top:1px solid rgba(124,58,237,0.12);">
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.60rem;color:rgba(140,110,180,0.40);">
          {_student} · {_branch}
        </div>
      </div>
    </div>
  </div>

  <!-- ═══ MAIN CONTENT ════════════════════════════════════════════════ -->
  <div class="main-content" id="mainContent">

    <!-- Top Bar -->
    <div class="topbar">
      <button class="topbar-toggle" id="sbToggle" onclick="toggleSidebar()" title="Toggle menu">
        <span class="tb-bar" id="tb1"></span>
        <span class="tb-bar" id="tb2"></span>
        <span class="tb-bar" id="tb3"></span>
      </button>
      <div class="topbar-title">AskMNIT AI</div>
      <span class="topbar-badge">MNIT Jaipur</span>
    </div>

    <!-- Chat / Hero Area -->
    <div class="chat-area" id="chatArea">

      {"<!-- HERO -->" if not has_messages else ""}
      <div id="heroSection" style="display:{'flex' if not has_messages else 'none'};flex:1;flex-direction:column;align-items:center;justify-content:center;">
        <div class="hero-center">
          <div class="hero-orb">
            <span class="hero-orb-emoji">🎓</span>
          </div>
          <div class="hero-title">Ask me anything</div>
          <div class="hero-sub">Your AI-powered MNIT senior — attendance, schedule, PYQs, exam strategy &amp; more.</div>

          <div class="sugg-row" id="suggRow">
            <div class="sugg-chip" onclick="useChip(this)"><span class="sugg-chip-icon">📊</span>My attendance status</div>
            <div class="sugg-chip" onclick="useChip(this)"><span class="sugg-chip-icon">📅</span>Next class today</div>
            <div class="sugg-chip" onclick="useChip(this)"><span class="sugg-chip-icon">📚</span>PYQs for my branch</div>
            <div class="sugg-chip" onclick="useChip(this)"><span class="sugg-chip-icon">💰</span>Fee due date</div>
            <div class="sugg-chip" onclick="useChip(this)"><span class="sugg-chip-icon">🎯</span>Exam prep strategy</div>
            <div class="sugg-chip" onclick="useChip(this)"><span class="sugg-chip-icon">📋</span>Subjects this semester</div>
          </div>
        </div>
      </div>

      <!-- Messages wrapper -->
      <div class="msgs-wrap" id="msgsWrap" style="display:{'flex' if has_messages else 'none'};flex-direction:column;">
        <div class="msgs-container" id="msgsContainer">
          <!-- Messages injected by JS -->
        </div>
      </div>

    </div>

    <!-- Input Area -->
    <div class="input-area {'hero-mode' if not has_messages else ''}" id="inputArea">
      <div id="fileChipStrip" class="file-chip-strip" style="display:none;"></div>
      <div class="input-shell">
        <div style="display:none;" id="shineBar"></div>
        <div class="input-row">
          <input
            class="input-field"
            id="mainInput"
            type="text"
            placeholder="Ask AskMNIT anything..."
            autocomplete="off"
            onkeydown="handleKey(event)"
            oninput="onInput()"
          />
          <div class="input-actions">
            <button class="ib-btn" id="attachBtn" onclick="toggleAttach()" title="Attach file">📎</button>
            <button class="ib-btn" id="micBtn" onclick="toggleMic()" title="Voice input">🎤</button>
            <button class="send-btn" onclick="sendMessage()" title="Send">↑</button>
          </div>
        </div>
      </div>
      <div class="input-hint">AskMNIT AI · MNIT Jaipur · Verify important info with ERP</div>
    </div>

  </div><!-- end main-content -->
</div><!-- end app-shell -->

<!-- Hidden file input -->
<input type="file" id="fileInput" style="display:none;" accept=".pdf,.txt,.png,.jpg,.jpeg,.docx,.csv" onchange="onFileSelect(this)">

<script>
// ══ STATE ═══════════════════════════════════════════════════════════════════
var sbOpen = {_sb_open_str};
var hasMessages = {_has_msgs};
var isRecording = false;
var attachedFile = "";
var mediaRecorder = null;
var audioChunks = [];
var isTyping = false;

var MESSAGES = {_msgs_str};

// ══ INIT ═════════════════════════════════════════════════════════════════════
(function init() {{
  renderMessages();
  updateSidebarState(sbOpen);
  rotatePlaceholder();
  setInterval(rotatePlaceholder, 3000);

  // Rotate orb hue
  var orb = document.querySelector('.hero-orb');
  if(orb) {{
    var hue=0;
    setInterval(function(){{ hue=(hue+0.5)%360; orb.style.filter='hue-rotate('+hue+'deg)'; }}, 50);
  }}
}})();

// ══ PLACEHOLDER ROTATION ════════════════════════════════════════════════════
var hints = [
  "Ask AskMNIT anything...",
  "What's my attendance %?",
  "When is my next class?",
  "Find PYQs for my branch...",
  "What's the fee deadline?",
  "Give me exam tips...",
  "Subjects this semester?",
];
var hintIdx = 0;
function rotatePlaceholder() {{
  var inp = document.getElementById('mainInput');
  if(!inp || document.activeElement === inp) return;
  hintIdx = (hintIdx+1) % hints.length;
  inp.style.opacity='0.3';
  setTimeout(function(){{
    inp.placeholder = hints[hintIdx];
    inp.style.transition='opacity 0.4s';
    inp.style.opacity='1';
  }}, 200);
}}

// ══ SIDEBAR ══════════════════════════════════════════════════════════════════
function toggleSidebar() {{
  sbOpen = !sbOpen;
  updateSidebarState(sbOpen);
}}
function closeSidebar() {{
  sbOpen = false;
  updateSidebarState(false);
}}
function updateSidebarState(open) {{
  var sb = document.getElementById('sidebar');
  var t1=document.getElementById('tb1'), t2=document.getElementById('tb2'), t3=document.getElementById('tb3');
  if(sb) {{ if(open) sb.classList.remove('collapsed'); else sb.classList.add('collapsed'); }}
  if(t1&&t2&&t3) {{
    if(open) {{
      t1.style.transform='rotate(45deg) translate(4.5px,4.5px)';
      t2.style.opacity='0'; t2.style.transform='scaleX(0)';
      t3.style.transform='rotate(-45deg) translate(4.5px,-4.5px)';
    }} else {{
      t1.style.transform=''; t2.style.opacity='1'; t2.style.transform=''; t3.style.transform='';
    }}
  }}
}}
  var sb = document.getElementById('sidebar');
  var t1=document.getElementById('tb1'), t2=document.getElementById('tb2'), t3=document.getElementById('tb3');
  if(sb) {{ if(open) sb.classList.remove('collapsed'); else sb.classList.add('collapsed'); }}
  if(t1&&t2&&t3) {{
    if(open) {{
      t1.style.transform='rotate(45deg) translate(4.5px,4.5px)';
      t2.style.opacity='0'; t2.style.transform='scaleX(0)';
      t3.style.transform='rotate(-45deg) translate(4.5px,-4.5px)';
    }} else {{
      t1.style.transform=''; t2.style.opacity='1'; t2.style.transform=''; t3.style.transform='';
    }}
  }}
}}

document.addEventListener('keydown', function(e){{ if(e.key==='Escape') closeSidebar(); }});

// ══ ACTIONS → PARENT STREAMLIT ════════════════════════════════════════════
function sendAction(action) {{
  closeSidebar();
  var url = new URL(window.parent.location.href);
  url.searchParams.set('_act', action);
  window.parent.location.href = url.toString();
}}

// ══ MESSAGES ═════════════════════════════════════════════════════════════════
function renderMessages() {{
  if(!MESSAGES || MESSAGES.length === 0) return;
  var container = document.getElementById('msgsContainer');
  var wrap = document.getElementById('msgsWrap');
  var hero = document.getElementById('heroSection');
  var inputArea = document.getElementById('inputArea');

  if(container) container.innerHTML = '';
  if(wrap) wrap.style.display = 'flex';
  if(hero) hero.style.display = 'none';
  if(inputArea) {{ inputArea.classList.remove('hero-mode'); }}

  MESSAGES.forEach(function(msg) {{
    appendMessage(msg.role, msg.content, false);
  }});
  scrollToBottom();
}}

function appendMessage(role, content, animate) {{
  var container = document.getElementById('msgsContainer');
  if(!container) return;
  var div = document.createElement('div');
  div.className = 'msg-bubble ' + role;
  if(animate) div.style.animationDelay = '0s';

  var formattedContent = content
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/```([\s\S]*?)```/g, '<pre>$1</pre>')
    .replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>')
    .replace(/\*(.*?)\*/g,'<em>$1</em>')
    .replace(/\n/g,'<br>');

  div.innerHTML =
    '<div class="msg-avatar ' + role + '">' + (role==='ai'?'A':'U') + '</div>' +
    '<div class="msg-text ' + role + '">' + formattedContent + '</div>';

  container.appendChild(div);
}}

function scrollToBottom() {{
  var wrap = document.getElementById('msgsWrap');
  if(wrap) setTimeout(function(){{ wrap.scrollTop = wrap.scrollHeight; }}, 50);
}}

// ══ SEND MESSAGE ════════════════════════════════════════════════════════════
function handleKey(e) {{
  if(e.key === 'Enter' && !e.shiftKey) {{ e.preventDefault(); sendMessage(); }}
}}
function onInput() {{
  var val = document.getElementById('mainInput').value.trim();
}}

function sendMessage() {{
  var inp = document.getElementById('mainInput');
  var txt = inp ? inp.value.trim() : '';
  if(!txt && !attachedFile) return;

  var fullMsg = txt;
  if(attachedFile && !txt) fullMsg = '[File: ' + attachedFile + ']';
  else if(attachedFile) fullMsg = txt + ' [File: ' + attachedFile + ']';

  // Show in UI immediately
  var wrap = document.getElementById('msgsWrap');
  var hero = document.getElementById('heroSection');
  var inputArea = document.getElementById('inputArea');
  if(wrap) wrap.style.display='flex';
  if(hero) hero.style.display='none';
  if(inputArea) inputArea.classList.remove('hero-mode');

  appendMessage('user', fullMsg, true);

  // Typing indicator
  var container = document.getElementById('msgsContainer');
  var typingDiv = document.createElement('div');
  typingDiv.className='msg-bubble ai'; typingDiv.id='typingIndicator';
  typingDiv.innerHTML=
    '<div class="msg-avatar ai">A</div>'+
    '<div class="msg-text ai"><div class="typing-indicator">'+
    '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>'+
    '</div></div>';
  if(container) container.appendChild(typingDiv);
  scrollToBottom();

  if(inp) inp.value='';
  clearAttach();

  // Post to parent Streamlit
  var url = new URL(window.parent.location.href);
  url.searchParams.set('_msg', encodeURIComponent(fullMsg));
  window.parent.location.href = url.toString();
}}

// ══ SUGGESTION CHIPS ════════════════════════════════════════════════════════
function useChip(el) {{
  var txt = el.textContent.trim().replace(/^[^\w]+/,'');
  var inp = document.getElementById('mainInput');
  if(inp) {{ inp.value = txt; inp.focus(); sendMessage(); }}
}}

// ══ FILE ATTACH ═════════════════════════════════════════════════════════════
function toggleAttach() {{
  document.getElementById('fileInput').click();
}}
function onFileSelect(input) {{
  if(!input.files||!input.files[0]) return;
  attachedFile = input.files[0].name;
  var strip = document.getElementById('fileChipStrip');
  if(strip) {{
    strip.style.display='flex';
    strip.innerHTML='<div class="file-chip">📎 '+attachedFile+
      '<button class="file-chip-rm" onclick="clearAttach()">✕</button></div>';
  }}
}}
function clearAttach() {{
  attachedFile='';
  var strip=document.getElementById('fileChipStrip');
  if(strip) {{strip.style.display='none';strip.innerHTML='';}}
  var fi=document.getElementById('fileInput'); if(fi) fi.value='';
}}

// ══ VOICE ═══════════════════════════════════════════════════════════════════
function toggleMic() {{
  if(isRecording) stopRecording(); else startRecording();
}}
function startRecording() {{
  navigator.mediaDevices.getUserMedia({{audio:true}}).then(function(stream) {{
    audioChunks=[];
    try{{mediaRecorder=new MediaRecorder(stream,{{mimeType:'audio/webm'}});}}
    catch(e){{mediaRecorder=new MediaRecorder(stream);}}
    mediaRecorder.ondataavailable=function(e){{if(e.data&&e.data.size>0)audioChunks.push(e.data);}};
    mediaRecorder.onstop=function(){{
      isRecording=false;
      var btn=document.getElementById('micBtn');
      if(btn){{btn.classList.remove('active');btn.textContent='🎤';}}
      // Signal to Streamlit
      var url=new URL(window.parent.location.href);
      url.searchParams.set('_mic_done','1');
      window.parent.location.href=url.toString();
      stream.getTracks().forEach(function(t){{t.stop();}});
    }};
    mediaRecorder.start(200);
    isRecording=true;
    var btn=document.getElementById('micBtn');
    if(btn){{btn.classList.add('active');btn.textContent='⏹';}}
  }}).catch(function(){{alert('Microphone access denied!');}} );
}}
function stopRecording() {{
  if(mediaRecorder&&mediaRecorder.state!=='inactive') mediaRecorder.stop();
}}

// Sidebar starts open by default - already handled in updateSidebarState call above
</script>
</body>
</html>
""", height=750, scrolling=False)

    # ── Handle actions from the chatbot component ────────────────────────
    _act = st.query_params.get("_act","")
    if _act:
        try: del st.query_params["_act"]
        except: pass
        if _act == "new_chat":
            if st.session_state.chat_messages:
                fu = next((m["content"][:38] for m in st.session_state.chat_messages if m["role"]=="user"),"Session")
                st.session_state.chat_sessions.append({"label":fu+"...","messages":list(st.session_state.chat_messages)})
            st.session_state.chat_messages=[]
            st.session_state.attached_file_name=""
            st.session_state.sb_open=False
            st.rerun()
        elif _act == "dashboard":
            st.session_state.view="dashboard"; st.rerun()
        elif _act == "history":
            st.session_state.show_history_panel = not st.session_state.show_history_panel
            st.rerun()
        elif _act == "settings":
            st.session_state.show_settings_panel = not st.session_state.show_settings_panel
            st.rerun()
        elif _act == "erp":
            st.session_state.erp_panel = not st.session_state.erp_panel
            st.rerun()

    # Handle message from chatbot
    _msg_raw = st.query_params.get("_msg","")
    if _msg_raw:
        try: del st.query_params["_msg"]
        except: pass
        _msg_text = _msg_raw  # already decoded by Streamlit
        if _msg_text:
            dispatch_message(_msg_text)
            st.rerun()

    # Handle mic done
    _mic_done = st.query_params.get("_mic_done","")
    if _mic_done:
        try: del st.query_params["_mic_done"]
        except: pass
        dispatch_message("🎤 [Voice message — please transcribe]")
        st.rerun()

    # ── Panels below the chatbot (if open) ───────────────────────────────
    if st.session_state.show_history_panel:
        all_sessions = st.session_state.chat_sessions
        with st.expander("🕐 Chat History", expanded=True):
            if not all_sessions:
                st.markdown('<p style="color:rgba(148,163,184,0.40);font-size:0.82rem;text-align:center;padding:20px 0;">No saved chats yet.</p>', unsafe_allow_html=True)
            else:
                _pinned   = [(i,s) for i,s in enumerate(all_sessions) if s.get("pinned")]
                _unpinned = [(i,s) for i,s in enumerate(all_sessions) if not s.get("pinned")]
                for _grp_label, _grp in [("📌 Pinned", _pinned), ("Recent", _unpinned)]:
                    if not _grp: continue
                    st.markdown(f'<div style="font-size:0.60rem;color:rgba(148,163,184,0.40);text-transform:uppercase;letter-spacing:1px;padding:4px 0 6px;">{_grp_label}</div>', unsafe_allow_html=True)
                    for _i, _sess in reversed(_grp):
                        _c1,_c2,_c3,_c4 = st.columns([5,0.9,0.9,0.9])
                        with _c1:
                            st.markdown(f'<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:9px 14px;font-size:0.82rem;color:rgba(226,232,240,0.80);">{"📌 " if _sess.get("pinned") else ""}{_sess.get("label","Chat")[:50]}</div>', unsafe_allow_html=True)
                        with _c2:
                            if st.button("↩",key=f"_load_{_i}"):
                                st.session_state.chat_messages=list(_sess["messages"])
                                st.session_state.show_history_panel=False; st.rerun()
                        with _c3:
                            if st.button("📌" if not _sess.get("pinned") else "📍",key=f"_pin_{_i}"):
                                st.session_state.chat_sessions[_i]["pinned"]=not _sess.get("pinned"); st.rerun()
                        with _c4:
                            if st.button("🗑",key=f"_del_{_i}"):
                                st.session_state.chat_sessions.pop(_i); st.rerun()
                if st.button("🗑 Clear All",key="_clear_hist"):
                    st.session_state.chat_sessions=[]
                    st.toast("History cleared!"); st.rerun()

    if st.session_state.show_settings_panel:
        with st.expander("⚙ Settings", expanded=True):
            _t1,_t2=st.columns(2)
            with _t1:
                if st.button("🌙 Dark Theme",key="_tdark",use_container_width=True):
                    st.session_state.chat_theme="dark"; st.rerun()
            with _t2:
                if st.button("☀️ Light Theme",key="_tlight",use_container_width=True):
                    st.session_state.chat_theme="light"; st.rerun()
            _ns=st.selectbox("Response Style",["Concise","Detailed","Bullet Points"],
                index=["Concise","Detailed","Bullet Points"].index(st.session_state.response_style),key="_rstyle")
            if _ns!=st.session_state.response_style:
                st.session_state.response_style=_ns; st.rerun()
            st.session_state.voice_output=st.toggle("🔊 Voice Output",value=st.session_state.voice_output,key="_voice_t")
            st.session_state.strict_mode=st.toggle("🎓 Strict Mode",value=st.session_state.strict_mode,key="_strict_t")
            if st.button("✕ Close",key="_cls_sets",use_container_width=True):
                st.session_state.show_settings_panel=False; st.rerun()

    if st.session_state.erp_panel:
        with st.expander("🔐 ERP Portal", expanded=True):
            st.markdown('<div style="font-size:0.82rem;color:rgba(168,140,255,0.70);margin-bottom:10px;">MNIT Jaipur ERP Login</div>', unsafe_allow_html=True)
            erp_id=st.text_input("ERP ID / Enrollment No.",key="_erp_id")
            erp_pw=st.text_input("Password",type="password",key="_erp_pw")
            if st.button("Login to ERP",key="_erp_login",use_container_width=True):
                st.toast("ERP integration coming soon! Visit erp.mnit.ac.in",icon="🔗")
            st.markdown('<div style="font-size:0.70rem;color:rgba(148,163,184,0.40);margin-top:6px;">Or visit: <a href="https://erp.mnit.ac.in" target="_blank" style="color:rgba(168,85,247,0.70);">erp.mnit.ac.in</a></div>', unsafe_allow_html=True)
            if st.button("Close",key="_erp_close"):
                st.session_state.erp_panel=False; st.rerun()

    st.stop()


###############################################################################
# ████████████████████  DASHBOARD VIEW  ██████████████████████████████████████
###############################################################################
NAV_LABELS = ["My Dashboard","My Schedule","Academics","Study Material","PYQs","Fee Portal","Mess Menu"]
with st.sidebar:
    st.markdown(
        '<div style="padding:18px 14px 14px;border-bottom:1px solid rgba(59,130,246,0.14);">'
        '<div style="display:flex;align-items:center;gap:9px;">'
        '<div style="width:30px;height:30px;border-radius:7px;background:linear-gradient(135deg,#7C3AED,#A855F7);'
        'display:flex;align-items:center;justify-content:center;font-size:0.9rem;font-weight:800;color:white;'
        'box-shadow:0 3px 12px rgba(124,58,237,0.35);font-family:Syne,sans-serif;">A</div>'
        '<div><div style="font-family:Syne,sans-serif;font-size:0.85rem;color:#E2E8F0;font-weight:700;">AskMNIT</div>'
        '<div style="font-size:0.56rem;color:rgba(148,163,184,.40);margin-top:1px;">Student Portal</div>'
        '</div></div></div>', unsafe_allow_html=True)
    bh = branch_hex(st.session_state.branch)
    st.markdown(f'<div style="padding:8px 12px 4px;"><span style="font-size:0.60rem;font-weight:700;padding:2px 9px;background:rgba(124,58,237,0.10);border:1px solid {bh}44;border-radius:5px;color:{bh};">{st.session_state.branch}</span></div>', unsafe_allow_html=True)
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
        "My Schedule":    ("My Schedule","Weekly timetable renders here."),
        "Academics":      ("Academics","Grades and CGPA records render here."),
        "Study Material": ("Study Material","Uploaded notes render here."),
        "PYQs":           ("PYQs","Previous year papers render here."),
        "Fee Portal":     ("Fee Portal","Fee dues and receipts render here."),
        "Mess Menu":      ("Mess Menu","Weekly hostel menu renders here."),
    }
    title, desc = PMETA.get(dash_page, (dash_page, "Coming soon."))
    st.markdown(f'<div style="padding:24px;"><div style="font-family:Syne,sans-serif;font-size:0.95rem;color:#E2E8F0;border-bottom:1px solid rgba(255,255,255,0.06);padding-bottom:14px;margin-bottom:24px;">{title.upper()}</div><div style="background:linear-gradient(160deg,#0B1120,#060A12);border:1px dashed rgba(124,58,237,0.18);border-radius:16px;padding:60px 40px;text-align:center;"><div style="font-family:Syne,sans-serif;font-size:0.88rem;color:#E2E8F0;margin-bottom:8px;">{title.upper()}</div><div style="font-size:0.76rem;color:rgba(148,163,184,.44);max-width:280px;margin:0 auto;line-height:1.65;">{desc}</div></div></div>', unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# MY DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div style='padding:0 22px 80px;'>", unsafe_allow_html=True)

h_logo, h_mid, h_right = st.columns([2,4,3])
with h_logo:
    st.markdown('<div style="display:flex;align-items:center;gap:8px;padding:13px 0 9px;"><div style="width:30px;height:30px;border-radius:7px;background:linear-gradient(135deg,#7C3AED,#A855F7);display:flex;align-items:center;justify-content:center;font-size:0.85rem;font-weight:800;color:white;font-family:Syne,sans-serif;">M</div><div><div style="font-family:Syne,sans-serif;font-size:0.76rem;color:#E2E8F0;">MNIT Jaipur</div><div style="font-size:0.52rem;color:rgba(148,163,184,.36);">[ MNIT LOGO ]</div></div></div>', unsafe_allow_html=True)
with h_mid:
    now_str = datetime.datetime.now().strftime("%a, %d %b %Y  ·  %H:%M")
    st.markdown(f'<div style="padding:13px 0 9px;text-align:center;"><span style="font-family:Syne,sans-serif;font-size:0.76rem;color:#A855F7;letter-spacing:0.8px;font-weight:700;">MY DASHBOARD</span><br><span style="font-size:0.57rem;color:rgba(148,163,184,.38);">{now_str}</span></div>', unsafe_allow_html=True)
with h_right:
    nm,br,sem = st.session_state.student_name,st.session_state.branch,st.session_state.semester
    bh = branch_hex(br); pp = st.session_state.profile_pic_b64
    av_html = (f'<img src="{pp}" style="width:36px;height:36px;border-radius:50%;object-fit:cover;border:2px solid {bh}55;">' if pp
               else f'<div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,{bh},{bh}88);display:flex;align-items:center;justify-content:center;font-size:0.85rem;font-weight:700;color:#fff;border:2px solid {bh}55;">{initials(nm)}</div>')
    st.markdown(f'<div style="display:flex;align-items:center;justify-content:flex-end;gap:9px;padding:10px 0 6px;">{av_html}<div><div style="font-weight:700;font-size:0.83rem;color:#E2E8F0;font-family:Syne,sans-serif;">{nm}</div><div style="font-size:0.58rem;color:{bh};font-weight:600;">{br} · {sem}</div></div></div>', unsafe_allow_html=True)

st.markdown('<div style="height:1px;background:linear-gradient(90deg,transparent,rgba(124,58,237,0.30),rgba(168,85,247,0.14),transparent);margin-bottom:20px;"></div>', unsafe_allow_html=True)

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
            new_name = st.text_input("Full Name", value=st.session_state.student_name, key="inp_name")
            new_id   = st.text_input("College ID", value=st.session_state.college_id, key="inp_id")
            new_sem  = st.selectbox("Semester", SEMESTERS, index=SEMESTERS.index(st.session_state.semester), key="sel_sem")
            new_br   = st.selectbox("Branch", BRANCHES, index=BRANCHES.index(st.session_state.branch), key="sel_br")
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
            st.toast(f"Schedule loaded!", icon="✅"); st.session_state.settings_mode=None; st.rerun()
        if st.session_state.schedule_loaded:
            st.markdown(f'<div style="font-size:0.75rem;color:#10B981;margin-top:6px;">Active: {st.session_state.pdf_filename}</div>', unsafe_allow_html=True)

# KPI Row
ov = overall_pct(st.session_state.attendance)
stat_badge_txt,stat_col,_ = status_badge(ov)
kpi1,kpi2,kpi3,kpi4 = st.columns(4)
for col,ico,val,lbl,c in [
    (kpi1,"📊",f"{ov}%","Overall Attendance",stat_col),
    (kpi2,"📚",str(len(subjects_for_branch(st.session_state.branch))),"Enrolled Subjects","#A855F7"),
    (kpi3,"📅",str(len(get_today_slots(st.session_state.full_schedule)) if st.session_state.schedule_loaded else 0),"Classes Today","#22D3EE"),
    (kpi4,"📝",str(len(st.session_state.notes_list)),"Active Notes","#C084FC"),
]:
    with col:
        st.markdown(f'<div style="background:linear-gradient(160deg,#0D0618,#110824);border:1px solid rgba(124,58,237,0.14);border-radius:14px;padding:16px 18px 14px;margin-bottom:14px;"><div style="font-size:1.4rem;margin-bottom:6px;">{ico}</div><div style="font-size:1.7rem;font-weight:800;color:{c};font-family:Syne,sans-serif;line-height:1.1;">{val}</div><div style="font-size:0.68rem;color:rgba(148,163,184,.46);margin-top:4px;">{lbl}</div></div>', unsafe_allow_html=True)

# Attendance Tracker
st.markdown('<div style="background:linear-gradient(160deg,#0D0618,#110824);border:1px solid rgba(124,58,237,0.12);border-radius:16px;padding:18px 18px 14px;margin-bottom:14px;"><div style="font-family:\'JetBrains Mono\',monospace;font-size:0.56rem;color:rgba(168,85,247,.40);text-transform:uppercase;letter-spacing:1.4px;margin-bottom:14px;">// ATTENDANCE TRACKER</div>', unsafe_allow_html=True)

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
            st.markdown(f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.85rem;font-weight:700;color:{c};padding-top:8px;">{pct}%</div><div style="font-size:0.60rem;color:rgba(148,163,184,.40);">{r["present"]}/{r["total"]}</div>', unsafe_allow_html=True)
        with sc3:
            st.markdown('<div class="present-btn">', unsafe_allow_html=True)
            if st.button("P",key=f"pp_{kb}",use_container_width=True): att[subj]["present"]+=1; att[subj]["total"]+=1; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with sc4:
            st.markdown('<div class="absent-btn">', unsafe_allow_html=True)
            if st.button("A",key=f"pa_{kb}",use_container_width=True): att[subj]["total"]+=1; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with sc5:
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("-P",key=f"rp_{kb}",use_container_width=True):
                if r["present"]>0 and r["total"]>0: att[subj]["present"]-=1; att[subj]["total"]-=1; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with sc6:
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("-A",key=f"ra_{kb}",use_container_width=True):
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
st.markdown(f'<div style="background:linear-gradient(160deg,#0D0618,#110824);border:1px solid rgba(124,58,237,0.12);border-radius:16px;padding:18px 18px 14px;margin-bottom:14px;"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;"><span style="font-family:\'JetBrains Mono\',monospace;font-size:0.56rem;color:rgba(168,85,247,.40);text-transform:uppercase;letter-spacing:1.4px;">// TODAY\'S SCHEDULE</span><span style="font-family:\'JetBrains Mono\',monospace;font-size:0.62rem;color:rgba(168,85,247,.65);">{today_name.upper()}</span></div>', unsafe_allow_html=True)
if st.session_state.schedule_loaded:
    today_slots=get_today_slots(st.session_state.full_schedule); nxt=get_next_class(today_slots)
    if nxt:
        mins=nxt["minutes_away"]; hrs=mins//60; rem=mins%60
        cd_str=(f"{hrs}h {rem}m" if hrs else f"{rem} min")+" away"
        urg_c="#EF4444" if mins<15 else "#F59E0B" if mins<45 else "#A855F7"
        st.markdown(f'<div style="background:linear-gradient(90deg,rgba(168,85,247,.06),rgba(124,58,237,.04));border:1px solid rgba(168,85,247,.20);border-radius:10px;padding:10px 16px;margin-bottom:14px;display:flex;align-items:center;justify-content:space-between;"><div><div style="font-size:0.57rem;color:rgba(168,140,255,.46);text-transform:uppercase;letter-spacing:0.8px;margin-bottom:2px;">Next Class</div><div style="font-weight:700;font-size:0.86rem;color:#E2E8F0;font-family:Syne,sans-serif;">{nxt["subject"]} <span style="font-size:0.67rem;color:rgba(148,163,184,.46);">{nxt["room"]}</span></div></div><div style="font-family:\'JetBrains Mono\',monospace;font-size:0.96rem;font-weight:600;color:{urg_c};text-align:right;">{cd_str}</div></div>', unsafe_allow_html=True)
    if today_slots:
        rows=[today_slots[i:i+3] for i in range(0,len(today_slots),3)]
        for row in rows:
            cols=st.columns(len(row))
            for ci,(col,slot) in enumerate(zip(cols,row)):
                sh,sm=map(int,slot["time_start"].split(":")); is_past=(sh*60+sm)<now_hm
                tc=TYPE_COLORS.get(slot["type"],"#A855F7")
                is_next=(nxt is not None and slot["time_start"]==nxt["time_start"] and slot["subject"]==nxt["subject"])
                bc=tc if not is_past else "rgba(255,255,255,0.06)"
                with col:
                    st.markdown(f'<div style="background:{"rgba(168,85,247,0.05)" if is_next else "rgba(255,255,255,0.02)"};border:1px solid {bc};border-left:3px solid {bc};border-radius:12px;padding:13px 14px;margin-bottom:8px;"><div style="font-family:\'JetBrains Mono\',monospace;font-size:0.78rem;color:{"#E2E8F0" if not is_past else "rgba(148,163,184,0.32)"};margin-bottom:6px;">{fmt_time(slot["time_start"])}</div><div style="font-size:0.82rem;font-weight:700;color:{"#F1F5F9" if not is_past else "rgba(148,163,184,0.28)"};margin-bottom:4px;font-family:Syne,sans-serif;">{slot["subject"]}</div><span style="font-size:0.58rem;padding:1px 7px;border-radius:4px;background:{tc}1A;color:{tc};font-weight:600;">{slot["type"]}</span>{"  <span style=\"font-size:0.58rem;color:#A855F7;font-weight:700;\">NEXT</span>" if is_next else ""}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="text-align:center;padding:24px;color:rgba(148,163,184,.40);">No classes for {today_name}.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div style="background:rgba(124,58,237,.04);border:1px dashed rgba(124,58,237,.20);border-radius:9px;padding:9px 13px;margin-bottom:12px;font-size:0.73rem;color:rgba(148,163,184,.48);">Use <b>Upload Schedule</b> to activate the planner.</div>', unsafe_allow_html=True)
    if "planner_overrides" not in st.session_state: st.session_state.planner_overrides={}
    for st_start,st_end in [("08:00","09:00"),("09:30","10:30"),("11:00","12:00"),("12:00","13:00"),("14:00","15:00"),("15:30","16:30")]:
        override=st.session_state.planner_overrides.get(st_start,"")
        mp1,mp2,mp3,mp4=st.columns([1.6,4,0.8,2.2])
        with mp1: st.markdown(f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.68rem;color:#A855F7;padding-top:10px;">{fmt_time(st_start)}</div>', unsafe_allow_html=True)
        with mp2: note_v=st.text_input("",value=override,placeholder="Task...",key="mp_"+st_start,label_visibility="collapsed")
        with mp3:
            st.markdown('<div class="save-btn">', unsafe_allow_html=True)
            if st.button("Save",key="sv_mp_"+st_start,use_container_width=True): st.session_state.planner_overrides[st_start]=note_v; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with mp4:
            saved=st.session_state.planner_overrides.get(st_start,"")
            if saved: st.markdown(f'<div style="font-size:0.67rem;color:#34D399;background:rgba(16,185,129,.07);border:1px solid rgba(16,185,129,.14);border-radius:7px;padding:4px 9px;margin-top:2px;">{saved}</div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# Notes & Quick Links
ql_col,notes_col=st.columns([1,1.5],gap="large")
with ql_col:
    st.markdown('<div style="background:linear-gradient(160deg,#0D0618,#110824);border:1px solid rgba(124,58,237,0.12);border-radius:16px;padding:18px 18px 14px;height:100%;"><div style="font-family:\'JetBrains Mono\',monospace;font-size:0.56rem;color:rgba(168,85,247,.40);text-transform:uppercase;letter-spacing:1.4px;margin-bottom:12px;">// QUICK LINKS</div>', unsafe_allow_html=True)
    QL=[("Upload Syllabus","Syllabus uploader will be enabled here."),("Add PYQ Link","PYQ link manager will open here."),("Library Search","Library search will open here.")]
    st.markdown('<div class="ql-btn">', unsafe_allow_html=True)
    for lbl,fb in QL:
        if st.button(lbl,key="ql_"+lbl,use_container_width=True): st.session_state.ql_feedback=fb; st.rerun()
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if st.session_state.ql_feedback: st.markdown(f'<div style="background:rgba(124,58,237,.06);border:1px solid rgba(168,85,247,.18);border-radius:8px;padding:7px 11px;margin-top:7px;font-size:0.70rem;color:rgba(200,170,255,.58);">{st.session_state.ql_feedback}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with notes_col:
    st.markdown('<div style="background:linear-gradient(160deg,#0D0618,#110824);border:1px solid rgba(124,58,237,0.12);border-radius:16px;padding:18px 18px 14px;"><div style="font-family:\'JetBrains Mono\',monospace;font-size:0.56rem;color:rgba(168,85,247,.40);text-transform:uppercase;letter-spacing:1.4px;margin-bottom:12px;">// PERSONAL NOTES</div>', unsafe_allow_html=True)
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
            with nr1: st.markdown(f'<div style="background:rgba(124,58,237,0.04);border:1px solid rgba(124,58,237,0.12);border-radius:9px;padding:9px 12px;margin-bottom:4px;font-size:0.80rem;color:rgba(226,232,240,0.75);">{note["text"]}</div>', unsafe_allow_html=True)
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

st.markdown('<div style="text-align:center;margin-top:28px;padding:10px 0;border-top:1px solid rgba(124,58,237,0.08);"><span style="font-family:\'JetBrains Mono\',monospace;font-size:0.52rem;color:rgba(168,85,247,0.24);">ASKMNT &nbsp;·&nbsp; MNIT JAIPUR &nbsp;·&nbsp; v7.0</span></div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
