# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  AskMNIT — v8.0 FIXED PREMIUM                                               ║
# ║  Chat: components.html() full-page + query params for message handling      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import streamlit as st
import streamlit.components.v1 as components
import datetime, random, base64

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
    "Mathematics I/II","Physics","Chemistry","Computer Programming",
    "Basic Electrical","Basic Electronics","Basic Mechanical",
    "Engineering Drawing","Environmental Science",
    "Technical Communication","Basic Economics",
]
BRANCH_SUBJECTS = {
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

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def process_schedule_pdf(file, branch):
    pool = COMMON_SUBJECTS[:4] + BRANCH_SUBJECTS.get(branch, [])
    random.seed(42)
    TIME_PAIRS = [("08:00","09:00"),("09:30","10:30"),("11:00","12:00"),
                  ("12:00","13:00"),("14:00","15:00"),("15:30","16:30")]
    sched = {}
    for day in DAYS[:6]:
        chosen = sorted(random.sample(range(len(TIME_PAIRS)), k=random.randint(2,4)))
        sched[day] = [{"time_start":TIME_PAIRS[ci][0],"time_end":TIME_PAIRS[ci][1],
             "subject":random.choice(pool),"room":random.choice(["LT-1","LT-2","Lab-A","Lab-B","CR-3","CR-5"]),
             "type":random.choice(["Lecture","Lecture","Lab","Tutorial"])} for ci in chosen]
    return sched

def get_today_slots(fs):  return fs.get(datetime.datetime.now().strftime("%A"), [])
def get_next_class(slots):
    now = datetime.datetime.now()
    for slot in slots:
        h,m = map(int, slot["time_start"].split(":"))
        dt = now.replace(hour=h,minute=m,second=0,microsecond=0)
        if dt > now: return {**slot,"minutes_away":int((dt-now).total_seconds()//60)}
    return None

def subjects_for_branch(b): return COMMON_SUBJECTS + BRANCH_SUBJECTS.get(b,[])
def blank_att(s):  return {x:{"present":0,"total":0} for x in s}
def att_pct(r):    return round(r["present"]/r["total"]*100,1) if r["total"] else 0.0
def overall_pct(a):
    tp=sum(r["present"] for r in a.values()); tt=sum(r["total"] for r in a.values())
    return round(tp/tt*100,1) if tt else 0.0
def status_badge(p):
    if p>=75: return "Safe","#10B981","rgba(16,185,129,0.12)"
    if p>=65: return "Low","#F59E0B","rgba(245,158,11,0.12)"
    return "Critical","#EF4444","rgba(239,68,68,0.12)"
def att_color(p):  return "#10B981" if p>=75 else "#F59E0B" if p>=65 else "#EF4444"
def initials(n):   return "".join(w[0].upper() for w in n.split()[:2]) if n else "??"
def branch_hex(b): return {"CSE":"#3B82F6","AI & ML":"#8B5CF6","ECE":"#06B6D4","Civil":"#F59E0B","Metallurgy":"#10B981"}.get(b,"#6366F1")
def img_to_b64(f):
    d=f.read(); m=f.type or "image/png"; return f"data:{m};base64,{base64.b64encode(d).decode()}"
def fmt_time(t):
    try:
        h,m=map(int,t.split(":")); return f"{h%12 or 12:02d}:{m:02d} {'AM' if h<12 else 'PM'}"
    except: return t
def _safe_key(s): return "".join(c if c.isalnum() else "_" for c in s)
def esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
_def_branch = "CSE"
_DEFAULTS = {
    "view":"dashboard","nav_page":"My Dashboard",
    "student_name":"Sumit Chaudhary","college_id":"2022UMT1234",
    "semester":"Semester 6","branch":_def_branch,"profile_pic_b64":"",
    "settings_mode":None,"attendance":blank_att(subjects_for_branch(_def_branch)),
    "schedule_loaded":False,"full_schedule":{},"pdf_filename":"",
    "notes_list":[
        {"text":"Mid-sem revision starts Monday","pinned":False},
        {"text":"Submit fee by 17 Mar","pinned":False},
        {"text":"Collect hall ticket from ERP","pinned":False},
    ],
    "ql_feedback":"","chat_messages":[],"chat_sessions":[],
    "is_recording":False,"planner_overrides":{},
    "attached_file_name":"","response_style":"Concise",
    "_lct":"","_lsbt":"","_laft":"","_lmic":"",
}
for k,v in _DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
# AI RESPONSE GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def _build_student_context():
    att=st.session_state.attendance; br=st.session_state.branch
    nm=st.session_state.student_name; sem=st.session_state.semester; ov=overall_pct(att)
    low=[(s,att_pct(r)) for s,r in att.items() if att_pct(r)<75 and r["total"]>0]
    good=[(s,att_pct(r)) for s,r in att.items() if att_pct(r)>=75 and r["total"]>0]
    att_summary=f"Overall attendance: {ov}%\n"
    if low:
        att_summary+="BELOW 75%:\n"
        for s,p in low:
            r=att[s]; need=max(0,int((0.75*r["total"]-r["present"])/0.25)+1)
            att_summary+=f"  - {s}: {p}% ({r['present']}/{r['total']}) — needs {need} more\n"
    if good:
        att_summary+="Above 75%:\n"
        for s,p in good[:5]: att_summary+=f"  - {s}: {p}%\n"
    sched_summary="Schedule not uploaded yet."
    if st.session_state.schedule_loaded:
        today_slots=get_today_slots(st.session_state.full_schedule)
        nxt=get_next_class(today_slots); dn=datetime.datetime.now().strftime("%A")
        if today_slots:
            sched_summary=f"Today ({dn}):\n"
            for sl in today_slots:
                sched_summary+=f"  {fmt_time(sl['time_start'])}-{fmt_time(sl['time_end'])}: {sl['subject']} @ {sl['room']} ({sl['type']})\n"
            sched_summary+=f"Next: {nxt['subject']} in {nxt['minutes_away']} min\n" if nxt else "No more classes today.\n"
        else: sched_summary=f"No classes today ({dn})."
    return f"""Student: {nm} | Branch: {br} | Semester: {sem} | ID: {st.session_state.college_id}
Subjects: {", ".join(subjects_for_branch(br))}
Attendance: {att_summary}
Schedule: {sched_summary}
Response style: {st.session_state.response_style}"""

def _detect_mood(text):
    t=text.lower()
    if any(w in t for w in ["stressed","tension","worried","exam tension","fail","nahi hua","confused"]): return "STRESSED — warm and reassuring first"
    if any(w in t for w in ["happy","khush","amazing","cleared","hogaya","yay"]): return "EXCITED — match energy"
    if any(w in t for w in ["angry","gussa","bakwas","worst","frustrat"]): return "FRUSTRATED — validate first"
    if any(w in t for w in ["thak","tired","neend","exhausted"]): return "TIRED — gentle and short"
    return "NEUTRAL — friendly and natural"

def generate_ai_response(last: str) -> str:
    import requests
    nm=st.session_state.student_name.split()[0]
    system_prompt=f"""You are AskMNIT — {nm}'s brilliant senior at MNIT Jaipur.
Mood: {_detect_mood(last)}
Personality: warm, funny, mix Hinglish naturally, short punchy sentences.
Student data:
{_build_student_context()}
Rules:
1. Call them "{nm}" or "yaar/bhai"
2. Attendance math must be EXACT
3. If unsure say "yaar iske baare mein sure nahi, ERP check kar"
4. Never say "I'm an AI" — you're AskMNIT"""

    api_messages=[]
    for msg in st.session_state.chat_messages[:-1][-14:]:
        api_messages.append({"role":msg["role"],"content":msg["content"]})
    api_messages.append({"role":"user","content":last})

    GROQ_API_KEY=st.secrets.get("GROQ_API_KEY","") or st.session_state.get("groq_api_key","")
    if not GROQ_API_KEY:
        return "Yaar, Groq API key set nahi hai 😅\n\n`.streamlit/secrets.toml` mein `GROQ_API_KEY = 'gsk_...'` add kar, phir restart kar!"
    try:
        resp=requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile",
                  "messages":[{"role":"system","content":system_prompt},*api_messages],
                  "max_tokens":900,"temperature":0.82,"top_p":0.90},
            timeout=30)
        data=resp.json()
        if resp.status_code==200: return data["choices"][0]["message"]["content"].strip()
        return f"Groq error: {data.get('error',{}).get('message','unknown')}"
    except requests.Timeout: return "Yaar connection slow hai ⏳ — thodi der baad try kar!"
    except Exception as e:   return f"Kuch gadbad hai 😅 — {str(e)[:60]}"

def dispatch_message(text: str):
    text=text.strip()
    if not text: return
    st.session_state.chat_messages.append({"role":"user","content":text})
    with st.spinner("AskMNIT soch raha hai..."):
        reply=generate_ai_response(text)
    st.session_state.chat_messages.append({"role":"assistant","content":reply})

# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD CSS
# ─────────────────────────────────────────────────────────────────────────────
DASH_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,700;9..144,900&family=DM+Mono:wght@400;500&family=Outfit:wght@300;400;500;600;700&display=swap');
*,html,body{box-sizing:border-box;margin:0;padding:0;}
html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"]{font-family:'Outfit',sans-serif!important;background:#070B14!important;color:#E2E8F0!important;}
header[data-testid="stHeader"],footer,#MainMenu,[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important;}
[data-testid="stMainBlockContainer"]{padding:0!important;max-width:100%!important;}
[data-testid="stSidebar"]{background:#0B1120!important;border-right:1px solid rgba(59,130,246,0.16)!important;min-width:260px!important;max-width:260px!important;}
[data-testid="stSidebar"]>div{padding:0!important;}
.stButton>button{background:linear-gradient(135deg,#2563EB,#4F46E5)!important;color:#fff!important;border:none!important;border-radius:9px!important;font-family:'Outfit',sans-serif!important;font-weight:600!important;font-size:0.82rem!important;padding:9px 16px!important;box-shadow:0 3px 14px rgba(37,99,235,0.20)!important;transition:all 0.16s ease!important;}
.stButton>button:hover{opacity:.88!important;transform:translateY(-1px)!important;}
.ghost-btn .stButton>button{background:rgba(255,255,255,.05)!important;border:1px solid rgba(255,255,255,0.14)!important;color:rgba(226,232,240,.55)!important;box-shadow:none!important;}
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
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{background:rgba(255,255,255,0.04)!important;border:1px solid rgba(255,255,255,0.14)!important;border-radius:10px!important;color:#E2E8F0!important;font-family:'Outfit',sans-serif!important;font-size:0.87rem!important;}
[data-testid="stTextInput"] input:focus,[data-testid="stTextArea"] textarea:focus{border-color:rgba(59,130,246,0.55)!important;box-shadow:0 0 0 2.5px rgba(59,130,246,0.13)!important;}
[data-testid="stTextInput"] label,[data-testid="stTextArea"] label{color:rgba(148,163,184,0.55)!important;font-size:0.70rem!important;font-weight:600!important;text-transform:uppercase!important;letter-spacing:0.6px!important;}
[data-testid="stSelectbox"]>div>div{background:rgba(255,255,255,0.04)!important;border:1px solid rgba(255,255,255,0.14)!important;border-radius:10px!important;color:#E2E8F0!important;}
[data-testid="stSelectbox"] label{color:rgba(148,163,184,0.55)!important;font-size:0.70rem!important;font-weight:600!important;text-transform:uppercase!important;}
[data-testid="stFileUploader"]{background:rgba(59,130,246,0.04)!important;border:1px dashed rgba(59,130,246,0.26)!important;border-radius:12px!important;}
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
</style>"""

# ═════════════════════════════════════════════════════════════════════════════
# VIEW ROUTER
# ═════════════════════════════════════════════════════════════════════════════
view = st.session_state.view

###############################################################################
# ████████████████████  CHAT VIEW — v8 FIXED  █████████████████████████████████
###############################################################################
if view == "chat":

    # ── Hide Streamlit chrome ─────────────────────────────────────────────
    st.markdown("""<style>
    [data-testid="stSidebar"]{display:none!important;}
    [data-testid="stSidebarCollapseButton"]{display:none!important;}
    [data-testid="collapsedControl"]{display:none!important;}
    section[data-testid="stMain"]{margin-left:0!important;padding:0!important;}
    [data-testid="stMainBlockContainer"]{padding:0!important;max-width:100%!important;}
    .stSpinner > div{display:none!important;}
    iframe{border:none!important;}
    </style>""", unsafe_allow_html=True)

    # ── Process query param actions BEFORE rendering ──────────────────────
    qp = st.query_params

    def qpget(k): return qp.get(k, "")

    # Incoming chat message
    cm=qpget("_cm"); ct=qpget("_ct")
    if cm and ct and ct != st.session_state._lct:
        st.session_state._lct = ct
        try: del st.query_params["_cm"]
        except: pass
        try: del st.query_params["_ct"]
        except: pass
        full_msg = cm
        if st.session_state.attached_file_name:
            full_msg += f" [File: {st.session_state.attached_file_name}]"
            st.session_state.attached_file_name = ""
        dispatch_message(full_msg)
        st.rerun()

    # Sidebar/topbar action
    sb=qpget("_sb"); sbt=qpget("_sbt")
    if sb and sbt and sbt != st.session_state._lsbt:
        st.session_state._lsbt = sbt
        try: del st.query_params["_sb"]
        except: pass
        try: del st.query_params["_sbt"]
        except: pass
        if sb == "new_chat":
            if st.session_state.chat_messages:
                fu = next((m["content"][:38] for m in st.session_state.chat_messages if m["role"]=="user"),"Chat")
                st.session_state.chat_sessions.append({"label":fu+"...","messages":list(st.session_state.chat_messages)})
            st.session_state.chat_messages = []; st.session_state.attached_file_name = ""
            st.rerun()
        elif sb == "dashboard":
            st.session_state.view = "dashboard"; st.rerun()
        elif sb == "clear":
            st.session_state.chat_messages = []; st.session_state.attached_file_name = ""
            st.rerun()

    # Attach file
    af=qpget("_af"); aft=qpget("_at")
    if af and aft and aft != st.session_state._laft:
        st.session_state._laft = aft
        st.session_state.attached_file_name = af
        try: del st.query_params["_af"]
        except: pass
        st.toast(f"📎 {af} attached!", icon="✅"); st.rerun()

    # Mic toggle
    mic=qpget("_mic")
    if mic and mic != st.session_state._lmic:
        st.session_state._lmic = mic
        try: del st.query_params["_mic"]
        except: pass
        st.session_state.is_recording = not st.session_state.is_recording
        st.toast("🎤 Recording started! Again dabao to stop." if st.session_state.is_recording else "⏹ Stopped.", icon="🎤" if st.session_state.is_recording else "✅")
        st.rerun()

    # ── Build HTML parts ──────────────────────────────────────────────────
    nm    = st.session_state.student_name
    br    = st.session_state.branch
    bh    = branch_hex(br)
    inits = initials(nm)
    has_messages = len(st.session_state.chat_messages) > 0
    rec   = st.session_state.is_recording

    # Messages HTML
    msgs_html = ""
    for msg in st.session_state.chat_messages:
        content = esc(msg["content"]).replace("\n","<br>")
        if msg["role"] == "user":
            msgs_html += f'<div class="msg-row msg-user"><div class="msg-bubble user-bubble">{content}</div><div class="av av-user">{inits}</div></div>'
        else:
            msgs_html += f'<div class="msg-row msg-ai"><div class="av av-ai">&#10022;</div><div class="msg-bubble ai-bubble">{content}</div></div>'

    # History HTML
    hist_html = ""
    if st.session_state.chat_sessions:
        for sess in reversed(st.session_state.chat_sessions[-10:]):
            lbl = esc(sess.get("label","Chat")[:30])
            hist_html += f'<div class="hi">&#128172; {lbl}&hellip;</div>'
    else:
        hist_html = '<div class="he">No saved chats yet</div>'

    chip_html = ""
    if st.session_state.attached_file_name:
        chip_html = f'<div class="chip">&#128206; {esc(st.session_state.attached_file_name[:22])} <span onclick="clearChip()" style="cursor:pointer;opacity:.6;margin-left:3px;">&#10005;</span></div>'

    mic_class = "recording" if rec else ""
    mic_icon  = "&#9209;" if rec else "&#127908;"

    sug_html = ""
    if not has_messages:
        sug_items = [
            ("&#128202;","Attendance check karo"),
            ("&#128197;","Next class kaunsi hai?"),
            (f"&#128196;",f"PYQs for {esc(br)}"),
            ("&#127919;","Exam preparation tips"),
            ("&#128218;","Subjects list karo"),
            ("&#128179;","Fee status check karo"),
        ]
        for icon, label in sug_items:
            sug_html += f'<div class="sug" onclick="sendMsg(\'{label.replace(chr(39), chr(39))}\')">{icon} {label}</div>'

    CHAT_HTML = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Syne:wght@700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
html,body{{height:100%;overflow:hidden;background:#050810;color:#E2E8F0;font-family:'Space Grotesk',sans-serif;}}
#app{{display:flex;height:100vh;overflow:hidden;position:relative;}}

/* BG */
.bg{{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden;}}
.bg::before{{content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse 80% 60% at 15% 10%,rgba(99,102,241,.20) 0%,transparent 60%),
    radial-gradient(ellipse 55% 50% at 85% 85%,rgba(34,211,238,.13) 0%,transparent 55%),
    radial-gradient(ellipse 40% 40% at 50% 45%,rgba(139,92,246,.07) 0%,transparent 70%);
  animation:bgP 9s ease-in-out infinite alternate;}}
@keyframes bgP{{0%{{opacity:.7;transform:scale(1);}}100%{{opacity:1;transform:scale(1.03);}}}}
.orb{{position:absolute;border-radius:50%;filter:blur(90px);}}
.o1{{width:480px;height:480px;background:radial-gradient(circle,rgba(99,102,241,.22) 0%,transparent 70%);top:-150px;left:-80px;animation:o1a 24s ease-in-out infinite;}}
.o2{{width:380px;height:380px;background:radial-gradient(circle,rgba(34,211,238,.16) 0%,transparent 70%);bottom:-100px;right:-60px;animation:o2a 19s ease-in-out infinite;}}
.o3{{width:280px;height:280px;background:radial-gradient(circle,rgba(167,139,250,.13) 0%,transparent 70%);top:45%;left:55%;animation:o3a 28s ease-in-out infinite;}}
@keyframes o1a{{0%,100%{{transform:translate(0,0);opacity:.6;}}50%{{transform:translate(50px,60px);opacity:1;}}}}
@keyframes o2a{{0%,100%{{transform:translate(0,0);opacity:.5;}}50%{{transform:translate(-40px,-50px);opacity:.9;}}}}
@keyframes o3a{{0%,100%{{transform:translate(0,0);opacity:.4;}}50%{{transform:translate(-60px,30px);opacity:.7;}}}}
.grid{{position:absolute;inset:0;
  background-image:linear-gradient(rgba(99,102,241,.04) 1px,transparent 1px),
    linear-gradient(90deg,rgba(99,102,241,.04) 1px,transparent 1px);
  background-size:55px 55px;
  mask-image:radial-gradient(ellipse 80% 80% at 50% 50%,black 20%,transparent 100%);
  -webkit-mask-image:radial-gradient(ellipse 80% 80% at 50% 50%,black 20%,transparent 100%);}}

/* SIDEBAR */
.sb{{position:relative;z-index:10;width:248px;min-width:248px;height:100vh;
  display:flex;flex-direction:column;
  background:rgba(7,10,24,.95);border-right:1px solid rgba(99,102,241,.18);
  backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);}}
.sb-brand{{padding:17px 15px 13px;border-bottom:1px solid rgba(255,255,255,.06);
  display:flex;align-items:center;gap:10px;}}
.sb-logo{{width:33px;height:33px;border-radius:9px;
  background:linear-gradient(135deg,#4338CA,#818CF8);
  display:flex;align-items:center;justify-content:center;
  font-family:'Syne',sans-serif;font-size:.88rem;font-weight:800;color:#fff;
  box-shadow:0 4px 13px rgba(67,56,202,.40);flex-shrink:0;}}
.sb-name{{font-family:'Syne',sans-serif;font-size:.88rem;font-weight:800;color:#F1F5F9;letter-spacing:-.3px;}}
.sb-sub{{font-size:.53rem;color:rgba(148,163,184,.38);text-transform:uppercase;letter-spacing:1px;margin-top:1px;}}
.sb-sec{{padding:11px 11px 5px;}}
.sb-sec-t{{font-family:'JetBrains Mono',monospace;font-size:.53rem;font-weight:500;
  color:rgba(148,163,184,.33);text-transform:uppercase;letter-spacing:1.6px;padding:0 4px 7px;}}
.sb-btn{{display:flex;align-items:center;gap:9px;padding:9px 10px;border-radius:10px;
  cursor:pointer;margin-bottom:3px;transition:all .18s;border:1px solid transparent;}}
.sb-btn:hover{{background:rgba(99,102,241,.10);border-color:rgba(99,102,241,.22);}}
.sb-ico{{width:26px;height:26px;border-radius:6px;display:flex;align-items:center;
  justify-content:center;font-size:.80rem;flex-shrink:0;}}
.sb-lbl{{font-size:.79rem;font-weight:500;color:rgba(226,232,240,.70);}}
.new-c{{background:rgba(99,102,241,.07);border-color:rgba(99,102,241,.16)!important;}}
.new-c .sb-ico{{background:rgba(99,102,241,.20);color:#818CF8;}}
.new-c .sb-lbl{{color:#A5B4FC;font-weight:600;}}
.erp .sb-ico{{background:rgba(34,211,238,.12);color:#22D3EE;}}
.dash .sb-ico{{background:rgba(16,185,129,.12);color:#10B981;}}
.hist-wrap{{flex:1;overflow-y:auto;padding:0 11px 10px;}}
.hist-wrap::-webkit-scrollbar{{width:3px;}}
.hist-wrap::-webkit-scrollbar-thumb{{background:rgba(99,102,241,.22);border-radius:3px;}}
.hi{{display:flex;align-items:center;gap:7px;padding:8px 9px;border-radius:8px;
  margin-bottom:2px;cursor:pointer;font-size:.73rem;color:rgba(148,163,184,.56);
  transition:background .15s;border:1px solid transparent;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}}
.hi:hover{{background:rgba(255,255,255,.04);border-color:rgba(255,255,255,.07);}}
.he{{font-size:.70rem;color:rgba(148,163,184,.26);text-align:center;padding:20px 0;font-style:italic;}}
.sb-foot{{padding:11px 13px;border-top:1px solid rgba(255,255,255,.05);}}
.sb-user{{display:flex;align-items:center;gap:8px;padding:7px 9px;
  border-radius:9px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);}}
.sb-av{{width:27px;height:27px;border-radius:50%;
  background:linear-gradient(135deg,{bh},{bh}88);
  display:flex;align-items:center;justify-content:center;
  font-size:.65rem;font-weight:700;color:#fff;flex-shrink:0;}}
.sb-un{{font-size:.74rem;font-weight:600;color:rgba(226,232,240,.78);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.sb-ub{{font-size:.56rem;color:{bh};font-weight:600;}}

/* MAIN */
.main{{flex:1;display:flex;flex-direction:column;position:relative;z-index:5;overflow:hidden;min-width:0;}}

/* Topbar */
.tb{{height:50px;display:flex;align-items:center;justify-content:space-between;
  padding:0 20px;border-bottom:1px solid rgba(255,255,255,.05);
  background:rgba(5,8,16,.65);backdrop-filter:blur(20px);flex-shrink:0;}}
.tb-badge{{display:flex;align-items:center;gap:6px;padding:4px 12px;
  background:rgba(99,102,241,.10);border:1px solid rgba(99,102,241,.22);border-radius:20px;}}
.tb-dot{{width:6px;height:6px;border-radius:50%;background:#818CF8;animation:blink 2s ease infinite;}}
@keyframes blink{{0%,100%{{opacity:1;}}50%{{opacity:.25;}}}}
.tb-model{{font-family:'JetBrains Mono',monospace;font-size:.66rem;color:#A5B4FC;font-weight:500;}}
.tb-r{{display:flex;gap:7px;}}
.tb-pill{{padding:4px 12px;border-radius:20px;font-size:.70rem;font-weight:500;
  border:1px solid rgba(255,255,255,.09);background:rgba(255,255,255,.04);
  color:rgba(226,232,240,.58);cursor:pointer;transition:all .18s;}}
.tb-pill:hover{{background:rgba(99,102,241,.13);border-color:rgba(99,102,241,.30);color:#BAE6FD;}}

/* Messages */
.msgs{{flex:1;overflow-y:auto;padding:18px 0;}}
.msgs::-webkit-scrollbar{{width:4px;}}
.msgs::-webkit-scrollbar-thumb{{background:rgba(99,102,241,.17);border-radius:4px;}}
.mi{{max-width:720px;margin:0 auto;padding:0 20px;}}
.msg-row{{display:flex;align-items:flex-end;gap:9px;margin-bottom:13px;animation:mi .28s cubic-bezier(.22,.61,.36,1) both;}}
@keyframes mi{{from{{opacity:0;transform:translateY(9px);}}to{{opacity:1;transform:translateY(0);}}}}
.msg-user{{flex-direction:row-reverse;}}
.av{{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:.66rem;font-weight:700;}}
.av-user{{background:linear-gradient(135deg,{bh},{bh}88);color:#fff;border:1.5px solid {bh}55;}}
.av-ai{{background:linear-gradient(135deg,#1e1b4b,#312e81);border:1.5px solid rgba(99,102,241,.35);color:#818CF8;font-size:.88rem;}}
.msg-bubble{{max-width:70%;padding:10px 14px;border-radius:16px;font-size:.86rem;line-height:1.65;word-wrap:break-word;}}
.user-bubble{{background:linear-gradient(135deg,#3730a3,#4338ca);color:#e0e7ff;
  border-radius:16px 16px 4px 16px;border:1px solid rgba(99,102,241,.38);
  box-shadow:0 4px 16px rgba(67,56,202,.26);}}
.ai-bubble{{background:rgba(255,255,255,.04);color:rgba(226,232,240,.90);
  border:1px solid rgba(255,255,255,.08);border-radius:16px 16px 16px 4px;}}

/* HERO */
.hero{{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;
  padding:0 24px 24px;animation:fu .45s cubic-bezier(.22,.61,.36,1) both;}}
@keyframes fu{{from{{opacity:0;transform:translateY(16px);}}to{{opacity:1;transform:translateY(0);}}}}
.hero-orb{{width:84px;height:84px;border-radius:50%;margin-bottom:24px;
  background:linear-gradient(135deg,#1e1b4b 0%,#312e81 40%,#4338ca 70%,#6366f1 100%);
  display:flex;align-items:center;justify-content:center;font-size:2.2rem;
  box-shadow:0 0 0 1px rgba(99,102,241,.28),0 0 38px rgba(99,102,241,.34),0 0 76px rgba(99,102,241,.13);
  animation:op 3s ease-in-out infinite;}}
@keyframes op{{0%,100%{{box-shadow:0 0 0 1px rgba(99,102,241,.28),0 0 38px rgba(99,102,241,.34),0 0 76px rgba(99,102,241,.13);transform:scale(1);}}
  50%{{box-shadow:0 0 0 2px rgba(99,102,241,.48),0 0 56px rgba(99,102,241,.48),0 0 110px rgba(99,102,241,.18);transform:scale(1.04);}}}}
.hero-title{{font-family:'Syne',sans-serif;font-size:2.6rem;font-weight:800;
  color:#F1F5F9;letter-spacing:-1.5px;text-align:center;line-height:1.05;margin-bottom:8px;}}
.hero-title span{{background:linear-gradient(90deg,#818CF8,#22D3EE);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}}
.hero-sub{{font-size:.82rem;color:rgba(148,163,184,.50);text-align:center;line-height:1.7;
  margin-bottom:32px;max-width:360px;}}
.sugs{{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;max-width:560px;margin-bottom:34px;}}
.sug{{padding:8px 16px;border-radius:999px;background:rgba(255,255,255,.04);
  border:1px solid rgba(255,255,255,.09);color:rgba(186,230,253,.68);
  font-size:.78rem;font-weight:500;cursor:pointer;transition:all .2s cubic-bezier(.22,.61,.36,1);
  white-space:nowrap;user-select:none;}}
.sug:hover{{background:rgba(99,102,241,.13);border-color:rgba(99,102,241,.34);
  color:#BAE6FD;transform:translateY(-2px);box-shadow:0 4px 13px rgba(99,102,241,.16);}}

/* Input zone */
.iz{{flex-shrink:0;padding:9px 18px 14px;
  background:rgba(5,8,16,.72);backdrop-filter:blur(22px);
  border-top:1px solid rgba(255,255,255,.05);}}
.iz.hm{{background:transparent;border-top:none;padding:0 18px 5px;}}
.ii{{max-width:700px;margin:0 auto;}}
.chip{{display:inline-flex;align-items:center;gap:5px;padding:3px 11px 3px 8px;
  background:rgba(99,102,241,.13);border:1px solid rgba(99,102,241,.28);
  border-radius:18px;font-size:.70rem;color:#A5B4FC;font-weight:600;margin-bottom:7px;}}
.lb{{display:flex;align-items:center;gap:7px;padding:6px 13px;margin-bottom:7px;
  background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.16);
  border-radius:8px;font-size:.75rem;color:#FCA5A5;}}
.ld{{width:6px;height:6px;border-radius:50%;background:#EF4444;animation:lda 1s ease infinite;flex-shrink:0;}}
@keyframes lda{{0%,100%{{opacity:1;}}50%{{opacity:.2;}}}}
.ib{{display:flex;align-items:center;gap:6px;
  background:rgba(12,16,36,.90);border:1.5px solid rgba(99,102,241,.22);
  border-radius:17px;padding:5px 6px 5px 13px;
  transition:border-color .22s,box-shadow .22s;
  box-shadow:0 4px 26px rgba(0,0,0,.38),0 0 0 1px rgba(99,102,241,.08);
  animation:barI 5s ease-in-out infinite;}}
.ib:focus-within{{border-color:rgba(99,102,241,.55)!important;
  box-shadow:0 0 0 3px rgba(99,102,241,.12),0 8px 34px rgba(67,56,202,.18)!important;
  animation:none!important;}}
@keyframes barI{{0%,100%{{box-shadow:0 4px 26px rgba(0,0,0,.38),0 0 0 1px rgba(99,102,241,.08);}}
  50%{{box-shadow:0 4px 26px rgba(0,0,0,.38),0 0 0 1px rgba(99,102,241,.17),0 0 22px rgba(99,102,241,.10);}}}}
.ib input{{flex:1;background:transparent;border:none;outline:none;
  color:#E2E8F0;font-family:'Space Grotesk',sans-serif;font-size:.90rem;
  padding:10px 4px;min-height:42px;caret-color:#818CF8;}}
.ib input::placeholder{{color:rgba(148,163,184,.30);}}
.div{{width:1px;height:19px;background:rgba(255,255,255,.08);flex-shrink:0;}}
.ib-btn{{width:34px;height:34px;border-radius:50%;border:none;outline:none;
  background:transparent;cursor:pointer;display:flex;align-items:center;justify-content:center;
  transition:all .18s;font-size:.95rem;color:rgba(148,163,184,.50);flex-shrink:0;}}
.ib-btn:hover{{background:rgba(255,255,255,.08);color:rgba(186,230,253,.85);}}
.mic{{background:rgba(255,255,255,.04)!important;border:1px solid rgba(255,255,255,.08)!important;}}
.mic.recording{{background:rgba(239,68,68,.18)!important;border-color:rgba(239,68,68,.42)!important;
  color:#FCA5A5!important;animation:mpulse 1.1s ease-in-out infinite!important;}}
@keyframes mpulse{{0%,100%{{box-shadow:0 0 0 0 rgba(239,68,68,.38);}}50%{{box-shadow:0 0 0 7px rgba(239,68,68,.00);}}}}
.send{{width:37px;height:37px;border-radius:50%;border:none;outline:none;
  background:linear-gradient(135deg,#4338CA,#6366F1);cursor:pointer;
  display:flex;align-items:center;justify-content:center;color:#fff;
  font-size:1.1rem;font-weight:700;flex-shrink:0;
  box-shadow:0 3px 12px rgba(67,56,202,.38);transition:all .18s;}}
.send:hover{{opacity:.88;transform:scale(1.07);}}
.disc{{text-align:center;font-family:'JetBrains Mono',monospace;
  font-size:.52rem;color:rgba(100,116,139,.28);margin-top:6px;letter-spacing:.5px;}}
</style>
</head>
<body>
<div id="app">
  <div class="bg">
    <div class="orb o1"></div>
    <div class="orb o2"></div>
    <div class="orb o3"></div>
    <div class="grid"></div>
  </div>

  <!-- SIDEBAR -->
  <div class="sb">
    <div class="sb-brand">
      <div class="sb-logo">A</div>
      <div><div class="sb-name">AskMNIT</div><div class="sb-sub">AI Assistant &middot; MNIT Jaipur</div></div>
    </div>
    <div class="sb-sec">
      <div class="sb-sec-t">Actions</div>
      <div class="sb-btn new-c" onclick="sbAct('new_chat')"><div class="sb-ico">&#10022;</div><span class="sb-lbl">New Chat</span></div>
      <div class="sb-btn erp" onclick="window.open('https://erp.mnit.ac.in','_blank')"><div class="sb-ico">&#127891;</div><span class="sb-lbl">ERP Login</span></div>
      <div class="sb-btn dash" onclick="sbAct('dashboard')"><div class="sb-ico">&#x2B21;</div><span class="sb-lbl">Back to Dashboard</span></div>
    </div>
    <div class="sb-sec" style="flex:1;display:flex;flex-direction:column;min-height:0;">
      <div class="sb-sec-t">Chat History</div>
      <div class="hist-wrap">{hist_html}</div>
    </div>
    <div class="sb-foot">
      <div class="sb-user">
        <div class="sb-av">{inits}</div>
        <div style="min-width:0;"><div class="sb-un">{esc(nm)}</div><div class="sb-ub">{esc(br)}</div></div>
      </div>
    </div>
  </div>

  <!-- MAIN -->
  <div class="main">
    <div class="tb">
      <div class="tb-badge"><div class="tb-dot"></div><span class="tb-model">AskMNIT &middot; Llama 3.3 70B</span></div>
      <div class="tb-r">
        <div class="tb-pill" onclick="sbAct('clear')">&#128465; Clear</div>
        <div class="tb-pill" onclick="sbAct('dashboard')">&larr; Dashboard</div>
      </div>
    </div>

    <!-- HERO or MESSAGES -->
    {'<div class="hero">' if not has_messages else '<div class="msgs" id="msgsDiv">'}
    {'<div class="hero-orb">&#129302;</div><div class="hero-title">Ready to <span>Ask?</span></div><div class="hero-sub">Tera AI senior at MNIT &mdash; attendance, schedule, PYQs, sab kuch!</div><div class="sugs">' + sug_html + '</div>' if not has_messages else '<div class="mi" id="mi">' + msgs_html + '<div id="bot"></div></div>'}
    </div>

    <!-- INPUT -->
    <div class="iz {'hm' if not has_messages else ''}" id="iz">
      <div class="ii">
        {chip_html}
        {'<div class="lb"><div class="ld"></div><span>Recording... mic dabao stop karne ke liye</span></div>' if rec else ''}
        <div class="ib" id="ib">
          <button class="ib-btn" title="Attach" onclick="doAttach()">&#65291;</button>
          <div class="div"></div>
          <input type="text" id="inp" placeholder="Ask AskMNIT anything..." autocomplete="off" onkeydown="onKey(event)">
          <button class="ib-btn mic {mic_class}" id="mic" title="Voice" onclick="doMic()">{mic_icon}</button>
          <button class="send" title="Send" onclick="doSend()">&#8679;</button>
        </div>
        <div class="disc">AskMNIT AI &nbsp;&middot;&nbsp; MNIT Jaipur &nbsp;&middot;&nbsp; Important info ERP se verify karein</div>
      </div>
    </div>
  </div>
</div>

<script>
// Scroll to bottom on load
(function(){{
  var b=document.getElementById('bot');
  if(b) b.scrollIntoView({{behavior:'instant'}});
  var d=document.getElementById('msgsDiv');
  if(d) d.scrollTop=d.scrollHeight;
  var i=document.getElementById('inp');
  if(i) setTimeout(function(){{i.focus();}},120);
}})();

// Rotating placeholder
var hints=['Ask AskMNIT anything...','Attendance kitni hai?','Next class kaunsi hai?',
  'Exam tips chahiye...','PYQs dhundne hain...','Fee status?','Subjects list karo...'];
var pi=0;
setInterval(function(){{
  var i=document.getElementById('inp');
  if(i&&document.activeElement!==i){{i.placeholder=hints[pi++%hints.length];}}
}},3000);

// ── Send to Streamlit via component value API ──
function sendToStreamlit(data) {{
  // Method 1: Streamlit component API
  try {{
    window.parent.postMessage({{
      type: "streamlit:setComponentValue",
      value: data
    }}, "*");
  }} catch(e) {{}}
  // Method 2: Direct Streamlit component value setter
  try {{
    if (window.Streamlit) {{
      window.Streamlit.setComponentValue(data);
    }}
  }} catch(e) {{}}
}}

// Load Streamlit component API
(function() {{
  var script = document.createElement('script');
  script.src = 'https://unpkg.com/streamlit-component-lib/dist/StreamlitLib.bundle.js';
  document.head.appendChild(script);
}})();

function sbAct(a) {{
  sendToStreamlit({{type:'sb', action:a, ts:Date.now()}});
}}
function doSend() {{
  var i=document.getElementById('inp'), txt=i?i.value.trim():'';
  if (!txt) return;
  i.value='';
  // Show message optimistically in UI
  var mi=document.getElementById('mi');
  if(mi) {{
    var row=document.createElement('div');
    row.className='msg-row msg-user';
    row.innerHTML='<div class="msg-bubble user-bubble">'+txt.replace(/</g,'&lt;').replace(/>/g,'&gt;')+'</div><div class="av av-user">{inits}</div>';
    mi.insertBefore(row, document.getElementById('bot'));
    var bot=document.getElementById('bot');
    if(bot) bot.scrollIntoView({{behavior:'smooth'}});
  }}
  sendToStreamlit({{type:'msg', text:txt, ts:Date.now()}});
}}
function onKey(e) {{ if(e.key==='Enter'&&!e.shiftKey){{e.preventDefault();doSend();}} }}
function sendMsg(t) {{
  sendToStreamlit({{type:'msg', text:t, ts:Date.now()}});
}}
function doAttach() {{
  var f=document.createElement('input');f.type='file';
  f.accept='.pdf,.txt,.png,.jpg,.jpeg,.docx,.csv';
  f.onchange=function(){{
    if(f.files&&f.files[0]) sendToStreamlit({{type:'attach', name:f.files[0].name, ts:Date.now()}});
  }};
  f.click();
}}
function doMic() {{
  sendToStreamlit({{type:'mic', ts:Date.now()}});
}}
function clearChip() {{
  sendToStreamlit({{type:'clearchip', ts:Date.now()}});
}}
</script>
</body>
</html>"""

    # ─────────────────────────────────────────────────────────────────────
    # RENDER: beautiful HTML visual (sidebar, messages, orbs etc.)
    # Input is handled by st.chat_input BELOW — most reliable method
    # ─────────────────────────────────────────────────────────────────────

    # Hide Streamlit chat input default styling & position it over the iframe bar
    st.markdown("""<style>
    /* Make chat_input sit perfectly over the iframe input zone */
    [data-testid="stChatInput"]{
      position:fixed !important;
      bottom:16px !important;
      left:calc(252px + max(20px, calc((100vw - 252px - 700px)/2))) !important;
      width:min(700px, calc(100vw - 252px - 40px)) !important;
      z-index:99999 !important;
      background:rgba(12,16,36,0.97) !important;
      border:1.5px solid rgba(99,102,241,0.55) !important;
      border-radius:18px !important;
      box-shadow:0 0 0 3px rgba(99,102,241,0.14), 0 8px 34px rgba(67,56,202,0.22) !important;
      padding: 2px 6px 2px 16px !important;
    }
    [data-testid="stChatInput"] textarea {
      background:transparent !important;
      border:none !important;
      color:#E2E8F0 !important;
      font-family:'Space Grotesk',sans-serif !important;
      font-size:0.92rem !important;
      caret-color:#818CF8 !important;
    }
    [data-testid="stChatInput"] textarea::placeholder{color:rgba(148,163,184,0.35)!important;}
    [data-testid="stChatInputSubmitButton"] button{
      background:linear-gradient(135deg,#4338CA,#6366F1) !important;
      border-radius:50% !important;
      border:none !important;
      color:#fff !important;
      box-shadow:0 3px 12px rgba(67,56,202,.38) !important;
    }
    /* Sidebar action buttons — overlay on top of iframe sidebar */
    .stChatMessage{display:none!important;}
    </style>""", unsafe_allow_html=True)

    # Render the full visual HTML
    components.html(CHAT_HTML, height=720, scrolling=False)

    # ── REAL input via st.chat_input (works 100% in all Streamlit envs) ──
    user_input = st.chat_input("Ask AskMNIT anything...", key="_chat_input_main")
    if user_input and user_input.strip():
        full_msg = user_input.strip()
        if st.session_state.attached_file_name:
            full_msg += f" [File: {st.session_state.attached_file_name}]"
            st.session_state.attached_file_name = ""
        dispatch_message(full_msg)
        st.rerun()

    # ── Sidebar navigation buttons (hidden overlay, always functional) ────
    st.markdown("""<style>
    .sb-overlay{
      position:fixed; top:0; left:0; width:252px; height:100vh;
      z-index:99998; pointer-events:none;
    }
    .sb-overlay-btns{
      position:fixed; top:118px; left:8px; width:236px;
      z-index:99999; pointer-events:all;
      display:flex; flex-direction:column; gap:3px;
    }
    .sb-overlay-btns .stButton>button{
      background:transparent!important;
      border:1px solid transparent!important;
      color:transparent!important;
      width:100%!important; height:42px!important;
      cursor:pointer!important;
      box-shadow:none!important;
      padding:0!important;
    }
    </style>
    <div class="sb-overlay-btns">""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if st.button("New", key="_ov_new"):
            if st.session_state.chat_messages:
                fu = next((m["content"][:38] for m in st.session_state.chat_messages if m["role"]=="user"),"Chat")
                st.session_state.chat_sessions.append({"label":fu+"...","messages":list(st.session_state.chat_messages)})
            st.session_state.chat_messages = []
            st.session_state.attached_file_name = ""
            st.rerun()
    with c2:
        if st.button("Dash", key="_ov_dash"):
            st.session_state.view = "dashboard"; st.rerun()
    with c3:
        if st.button("Clr", key="_ov_clr"):
            st.session_state.chat_messages = []
            st.session_state.attached_file_name = ""
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


###############################################################################
# DASHBOARD VIEW  (completely unchanged from original)
###############################################################################
st.markdown(DASH_CSS, unsafe_allow_html=True)

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
        "My Schedule":("My Schedule","Weekly timetable renders here."),
        "Academics":("Academics","Grades and CGPA records render here."),
        "Study Material":("Study Material","Uploaded notes render here."),
        "PYQs":("PYQs","Previous year papers render here."),
        "Fee Portal":("Fee Portal","Fee dues and receipts render here."),
        "Mess Menu":("Mess Menu","Weekly hostel menu renders here."),
    }
    title,desc = PMETA.get(dash_page,(dash_page,"Coming soon."))
    st.markdown(f'<div style="padding:24px;"><div style="font-family:\'DM Mono\',monospace;font-size:0.95rem;color:#E2E8F0;border-bottom:1px solid rgba(255,255,255,0.06);padding-bottom:14px;margin-bottom:24px;">{title.upper()}</div><div style="background:linear-gradient(160deg,#0B1120,#060A12);border:1px dashed rgba(59,130,246,0.18);border-radius:16px;padding:60px 40px;text-align:center;"><div style="font-family:\'DM Mono\',monospace;font-size:0.88rem;color:#E2E8F0;margin-bottom:8px;">{title.upper()}</div><div style="font-size:0.76rem;color:rgba(148,163,184,.44);max-width:280px;margin:0 auto;line-height:1.65;">{desc}</div></div></div>', unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# MY DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div style='padding:0 22px 80px;'>", unsafe_allow_html=True)

h_logo,h_mid,h_right = st.columns([2,4,3])
with h_logo:
    st.markdown('<div style="display:flex;align-items:center;gap:8px;padding:13px 0 9px;"><div style="width:30px;height:30px;border-radius:7px;background:linear-gradient(135deg,#2563EB,#4F46E5);display:flex;align-items:center;justify-content:center;font-size:0.85rem;font-weight:700;color:white;">M</div><div><div style="font-family:\'DM Mono\',monospace;font-size:0.76rem;color:#E2E8F0;">MNIT Jaipur</div><div style="font-size:0.52rem;color:rgba(148,163,184,.36);">[ MNIT LOGO ]</div></div></div>', unsafe_allow_html=True)
with h_mid:
    now_str = datetime.datetime.now().strftime("%a, %d %b %Y  ·  %H:%M")
    st.markdown(f'<div style="padding:13px 0 9px;text-align:center;"><span style="font-family:\'DM Mono\',monospace;font-size:0.76rem;color:#60A5FA;letter-spacing:0.8px;">MY DASHBOARD</span><br><span style="font-size:0.57rem;color:rgba(148,163,184,.38);">{now_str}</span></div>', unsafe_allow_html=True)
with h_right:
    nm,br,sem = st.session_state.student_name,st.session_state.branch,st.session_state.semester
    bh=branch_hex(br); pp=st.session_state.profile_pic_b64
    av_html=(f'<img src="{pp}" style="width:36px;height:36px;border-radius:50%;object-fit:cover;border:2px solid {bh}55;">' if pp
             else f'<div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,{bh},{bh}88);display:flex;align-items:center;justify-content:center;font-size:0.85rem;font-weight:700;color:#fff;border:2px solid {bh}55;">{initials(nm)}</div>')
    st.markdown(f'<div style="display:flex;align-items:center;justify-content:flex-end;gap:9px;padding:10px 0 6px;">{av_html}<div><div style="font-weight:700;font-size:0.83rem;color:#E2E8F0;line-height:1.2;">{nm}</div><div style="font-size:0.58rem;color:{bh};font-weight:600;">{br} · {sem}</div></div></div>', unsafe_allow_html=True)

st.markdown('<div style="height:1px;background:linear-gradient(90deg,transparent,rgba(59,130,246,0.22),rgba(34,211,238,0.10),transparent);margin-bottom:20px;"></div>', unsafe_allow_html=True)

srow1,srow2,srow3,_,srow5 = st.columns([1,1,1,1,1])
with srow1:
    st.markdown('<div class="settings-menu-btn">', unsafe_allow_html=True)
    if st.button("Settings & Profile",key="open_settings"):
        st.session_state.settings_mode=None if st.session_state.settings_mode=="profile" else "profile"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with srow2:
    st.markdown('<div class="settings-menu-btn">', unsafe_allow_html=True)
    if st.button("Upload Schedule",key="open_schedule"):
        st.session_state.settings_mode=None if st.session_state.settings_mode=="schedule" else "schedule"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with srow3:
    st.markdown('<div class="settings-menu-btn">', unsafe_allow_html=True)
    if st.button("Notifications",key="open_notif"):
        st.toast("No new notifications.", icon="🔔")
    st.markdown('</div>', unsafe_allow_html=True)
with srow5:
    st.markdown('<div class="open-chat-btn">', unsafe_allow_html=True)
    if st.button("Open AskMNIT AI",key="btn_open_chat_dash"):
        st.session_state.view="chat"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

mode = st.session_state.settings_mode
if mode=="profile":
    with st.expander("Settings & Profile",expanded=True):
        pc1,pc2=st.columns([1,2])
        with pc1:
            pp=st.session_state.profile_pic_b64; bh=branch_hex(st.session_state.branch)
            if pp: st.markdown(f'<img src="{pp}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;border:3px solid {bh}66;display:block;margin:0 auto 8px;">', unsafe_allow_html=True)
            else:  st.markdown(f'<div style="width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,{bh},{bh}88);display:flex;align-items:center;justify-content:center;font-size:1.8rem;font-weight:700;color:#fff;margin:0 auto 8px;">{initials(st.session_state.student_name)}</div>', unsafe_allow_html=True)
            pic_file=st.file_uploader("Upload photo",type=["png","jpg","jpeg"],key="profile_pic_up",label_visibility="collapsed")
            if pic_file: st.session_state.profile_pic_b64=img_to_b64(pic_file); st.rerun()
        with pc2:
            new_name=st.text_input("Full Name",value=st.session_state.student_name,key="inp_name")
            new_id=st.text_input("College ID",value=st.session_state.college_id,key="inp_id")
            new_sem=st.selectbox("Semester",SEMESTERS,index=SEMESTERS.index(st.session_state.semester),key="sel_sem")
            new_br=st.selectbox("Branch",BRANCHES,index=BRANCHES.index(st.session_state.branch),key="sel_br")
            if st.button("Save Profile",key="save_profile"):
                old_br=st.session_state.branch
                st.session_state.student_name=new_name; st.session_state.college_id=new_id
                st.session_state.semester=new_sem; st.session_state.branch=new_br
                if old_br!=new_br: st.session_state.attendance=blank_att(subjects_for_branch(new_br))
                st.toast("Profile saved!",icon="✅"); st.session_state.settings_mode=None; st.rerun()

elif mode=="schedule":
    with st.expander("Upload Weekly Schedule PDF",expanded=True):
        pdf_file=st.file_uploader("Drop schedule PDF here",type=["pdf"],key="sched_upload")
        if pdf_file:
            st.session_state.full_schedule=process_schedule_pdf(pdf_file,st.session_state.branch)
            st.session_state.schedule_loaded=True; st.session_state.pdf_filename=pdf_file.name
            st.toast(f"Schedule loaded: {pdf_file.name}",icon="✅"); st.session_state.settings_mode=None; st.rerun()
        if st.session_state.schedule_loaded:
            st.markdown(f'<div style="font-size:0.75rem;color:#10B981;margin-top:6px;">Active: {st.session_state.pdf_filename}</div>', unsafe_allow_html=True)

ov=overall_pct(st.session_state.attendance); stat_badge_txt,stat_col,_=status_badge(ov)
kpi1,kpi2,kpi3,kpi4=st.columns(4)
for col,ico,val,lbl,c in [
    (kpi1,"📊",f"{ov}%","Overall Attendance",stat_col),
    (kpi2,"📚",str(len(subjects_for_branch(st.session_state.branch))),"Enrolled Subjects","#60A5FA"),
    (kpi3,"📅",str(len(get_today_slots(st.session_state.full_schedule)) if st.session_state.schedule_loaded else 0),"Classes Today","#22D3EE"),
    (kpi4,"📝",str(len(st.session_state.notes_list)),"Active Notes","#A78BFA"),
]:
    with col:
        st.markdown(f'<div style="background:linear-gradient(160deg,#0B1120,#070D1C);border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:16px 18px 14px;margin-bottom:14px;"><div style="font-size:1.4rem;margin-bottom:6px;">{ico}</div><div style="font-size:1.7rem;font-weight:800;color:{c};font-family:\'DM Mono\',monospace;line-height:1.1;">{val}</div><div style="font-size:0.68rem;color:rgba(148,163,184,.46);margin-top:4px;">{lbl}</div></div>', unsafe_allow_html=True)

st.markdown('<div style="background:linear-gradient(160deg,#0B1120,#070D1C);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:18px 18px 14px;margin-bottom:14px;"><div style="font-family:\'DM Mono\',monospace;font-size:0.56rem;color:rgba(148,163,184,.40);text-transform:uppercase;letter-spacing:1.4px;margin-bottom:14px;">// ATTENDANCE TRACKER</div>', unsafe_allow_html=True)

def render_subj_rows(subj_list,section):
    att=st.session_state.attendance
    for idx,subj in enumerate(subj_list):
        if subj not in att: att[subj]={"present":0,"total":0}
        r=att[subj]; pct=att_pct(r); c=att_color(pct); kb=f"{section}_{idx}_{_safe_key(subj)}"
        sc1,sc2,sc3,sc4,sc5,sc6=st.columns([3.5,1.2,0.9,0.9,0.9,0.9])
        with sc1: st.markdown(f'<div style="font-size:0.80rem;color:#E2E8F0;font-weight:600;padding:8px 0 4px;">{subj}</div><div style="background:rgba(255,255,255,.06);border-radius:99px;height:4px;overflow:hidden;width:90%;"><div style="width:{pct}%;height:100%;background:linear-gradient(90deg,{c},{c}88);border-radius:99px;"></div></div>', unsafe_allow_html=True)
        with sc2: st.markdown(f'<div style="font-family:\'DM Mono\',monospace;font-size:0.85rem;font-weight:700;color:{c};padding-top:8px;">{pct}%</div><div style="font-size:0.60rem;color:rgba(148,163,184,.40);">{r["present"]}/{r["total"]}</div>', unsafe_allow_html=True)
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

branch_only=BRANCH_SUBJECTS.get(st.session_state.branch,[])
with st.expander("Common Subjects ("+str(len(COMMON_SUBJECTS))+")",expanded=True): render_subj_rows(COMMON_SUBJECTS,"cmn")
if branch_only:
    with st.expander(st.session_state.branch+" Subjects ("+str(len(branch_only))+")",expanded=True): render_subj_rows(branch_only,"brnch")
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

today_name=datetime.datetime.now().strftime("%A"); now_hm=datetime.datetime.now().hour*60+datetime.datetime.now().minute
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
                if st.button("Pin",key=f"pin_{list_idx}_{i}_{_safe_key(note['text'][:10])}",use_container_width=True): st.session_state.notes_list[i]["pinned"]=True; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with nr3:
                st.markdown('<div class="del-btn">', unsafe_allow_html=True)
                if st.button("Del",key=f"del_{list_idx}_{i}_{_safe_key(note['text'][:10])}",use_container_width=True): st.session_state.notes_list.pop(i); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div style="text-align:center;margin-top:28px;padding:10px 0;border-top:1px solid rgba(255,255,255,0.05);"><span style="font-family:\'DM Mono\',monospace;font-size:0.52rem;color:rgba(148,163,184,0.24);letter-spacing:1.2px;">ASKMNT &nbsp;·&nbsp; MNIT JAIPUR &nbsp;·&nbsp; v8.0 FIXED PREMIUM</span></div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
