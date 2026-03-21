# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  AskMNIT — v6.0 PREMIUM  (Pure Streamlit, no iframe hacks)                  ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import streamlit as st
import datetime, random, base64

st.set_page_config(page_title="AskMNIT", page_icon="🎓",
                   layout="wide", initial_sidebar_state="collapsed")

# ─────────────────────────────────────────────────────────────────────────────
# SUBJECT DATABASE
# ─────────────────────────────────────────────────────────────────────────────
COMMON_SUBJECTS = ["Mathematics I/II","Physics","Chemistry","Computer Programming",
    "Basic Electrical","Basic Electronics","Basic Mechanical","Engineering Drawing",
    "Environmental Science","Technical Communication","Basic Economics"]
BRANCH_SUBJECTS = {
    "CSE":["Discrete Mathematics","Problem Solving using C"],
    "AI & ML":["Mathematics for AI","Data Structures and Algorithms"],
    "ECE":["Signals and Systems","Electronic Devices and Circuits"],
    "Civil":["Mechanics of Solid","Engineering Geology"],
    "Metallurgy":["Engineering Materials","Mineral Processing"],
}
BRANCHES  = ["CSE","AI & ML","ECE","Civil","Metallurgy"]
SEMESTERS = [f"Semester {i}" for i in range(1,9)]
DAYS      = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
TYPE_COLORS = {"Lecture":"#22D3EE","Lab":"#F59E0B","Tutorial":"#A78BFA"}

def process_schedule_pdf(file, branch):
    pool = COMMON_SUBJECTS[:4]+BRANCH_SUBJECTS.get(branch,[])
    random.seed(42)
    TP = [("08:00","09:00"),("09:30","10:30"),("11:00","12:00"),
          ("12:00","13:00"),("14:00","15:00"),("15:30","16:30")]
    sched={}
    for day in DAYS[:6]:
        chosen=sorted(random.sample(range(len(TP)),k=random.randint(2,4)))
        sched[day]=[{"time_start":TP[ci][0],"time_end":TP[ci][1],
            "subject":random.choice(pool),"room":random.choice(["LT-1","LT-2","Lab-A","Lab-B","CR-3","CR-5"]),
            "type":random.choice(["Lecture","Lecture","Lab","Tutorial"])} for ci in chosen]
    return sched

def get_today_slots(fs): return fs.get(datetime.datetime.now().strftime("%A"),[])
def get_next_class(slots):
    now=datetime.datetime.now()
    for slot in slots:
        h,m=map(int,slot["time_start"].split(":"))
        dt=now.replace(hour=h,minute=m,second=0,microsecond=0)
        if dt>now: return {**slot,"minutes_away":int((dt-now).total_seconds()//60)}
    return None

def subjects_for_branch(b): return COMMON_SUBJECTS+BRANCH_SUBJECTS.get(b,[])
def blank_att(s): return {x:{"present":0,"total":0} for x in s}
def att_pct(r): return round(r["present"]/r["total"]*100,1) if r["total"] else 0.0
def overall_pct(a):
    tp=sum(r["present"] for r in a.values()); tt=sum(r["total"] for r in a.values())
    return round(tp/tt*100,1) if tt else 0.0
def status_badge(p):
    if p>=75: return "Safe","#10B981","rgba(16,185,129,0.12)"
    if p>=65: return "Low","#F59E0B","rgba(245,158,11,0.12)"
    return "Critical","#EF4444","rgba(239,68,68,0.12)"
def att_color(p): return "#10B981" if p>=75 else "#F59E0B" if p>=65 else "#EF4444"
def initials(n): return "".join(w[0].upper() for w in n.split()[:2]) if n else "??"
def branch_hex(b): return {"CSE":"#3B82F6","AI & ML":"#8B5CF6","ECE":"#06B6D4","Civil":"#F59E0B","Metallurgy":"#10B981"}.get(b,"#6366F1")
def img_to_b64(f): d=f.read();m=f.type or "image/png"; return f"data:{m};base64,{base64.b64encode(d).decode()}"
def fmt_time(t):
    try: h,m=map(int,t.split(":")); return f"{h%12 or 12:02d}:{m:02d} {'AM' if h<12 else 'PM'}"
    except: return t
def _safe_key(s): return "".join(c if c.isalnum() else "_" for c in s)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
_def_branch = "CSE"
_DEFAULTS = {
    "view":"dashboard",
    "nav_page":"My Dashboard",
    "student_name":"Sumit Chaudhary","college_id":"2022UMT1234",
    "semester":"Semester 6","branch":_def_branch,"profile_pic_b64":"",
    "settings_mode":None,
    "attendance":blank_att(subjects_for_branch(_def_branch)),
    "schedule_loaded":False,"full_schedule":{},"pdf_filename":"",
    "notes_list":[{"text":"Mid-sem revision starts Monday","pinned":False},
                  {"text":"Submit fee by 17 Mar","pinned":False},
                  {"text":"Collect hall ticket from ERP","pinned":False}],
    "ql_feedback":"",
    # Chat
    "chat_messages":[],"chat_sessions":[],"chat_sb_open":False,
    "show_chat_history":False,"_pending_pill":"",
}
for k,v in _DEFAULTS.items():
    if k not in st.session_state: st.session_state[k]=v

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS  (dashboard + chat both)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
*,html,body{box-sizing:border-box;margin:0;padding:0;}
html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"]{
  font-family:'Inter',sans-serif!important;
  background:#09070f!important;color:#e8e8f0!important;}
header[data-testid="stHeader"],footer,#MainMenu,
[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important;}
[data-testid="stMainBlockContainer"]{padding:0!important;max-width:100%!important;}
/* Dashboard sidebar */
[data-testid="stSidebar"]{background:#0B1120!important;border-right:1px solid rgba(59,130,246,0.16)!important;min-width:260px!important;max-width:260px!important;}
[data-testid="stSidebar"]>div{padding:0!important;}
/* Global buttons */
.stButton>button{background:linear-gradient(135deg,#2563EB,#4F46E5)!important;color:#fff!important;border:none!important;border-radius:9px!important;font-family:'Inter',sans-serif!important;font-weight:600!important;font-size:0.82rem!important;padding:9px 16px!important;box-shadow:0 3px 14px rgba(37,99,235,0.20)!important;transition:all 0.16s ease!important;}
.stButton>button:hover{opacity:.88!important;transform:translateY(-1px)!important;}
.ghost-btn .stButton>button{background:rgba(255,255,255,.05)!important;border:1px solid rgba(255,255,255,0.14)!important;color:rgba(226,232,240,.55)!important;box-shadow:none!important;}
.present-btn .stButton>button{background:linear-gradient(135deg,#065F46,#10B981)!important;padding:6px 11px!important;font-size:0.75rem!important;border-radius:7px!important;}
.absent-btn .stButton>button{background:linear-gradient(135deg,#7F1D1D,#EF4444)!important;padding:6px 11px!important;font-size:0.75rem!important;border-radius:7px!important;}
.save-btn .stButton>button{background:linear-gradient(135deg,#92400E,#F59E0B)!important;padding:7px 13px!important;font-size:0.77rem!important;}
.pin-btn .stButton>button{background:rgba(245,158,11,0.10)!important;border:1px solid rgba(245,158,11,0.28)!important;color:#FCD34D!important;box-shadow:none!important;font-size:0.70rem!important;padding:4px 10px!important;border-radius:7px!important;}
.del-btn .stButton>button{background:rgba(239,68,68,0.07)!important;border:1px solid rgba(239,68,68,0.18)!important;color:rgba(252,165,165,0.70)!important;box-shadow:none!important;font-size:0.68rem!important;padding:3px 8px!important;border-radius:6px!important;}
.ql-btn .stButton>button{background:rgba(255,255,255,.03)!important;border:1px solid rgba(255,255,255,0.14)!important;color:rgba(186,230,253,.65)!important;box-shadow:none!important;font-size:0.80rem!important;padding:9px 14px!important;border-radius:9px!important;}
.logout-btn .stButton>button{background:rgba(239,68,68,.09)!important;border:1px solid rgba(239,68,68,.20)!important;color:#FCA5A5!important;box-shadow:none!important;}
.open-chat-btn .stButton>button{background:linear-gradient(135deg,#059669,#10B981)!important;border-radius:12px!important;font-weight:700!important;font-size:0.88rem!important;padding:11px 22px!important;box-shadow:0 5px 24px rgba(16,185,129,.36)!important;}
.settings-menu-btn .stButton>button{background:rgba(255,255,255,0.06)!important;border:1px solid rgba(255,255,255,0.12)!important;color:rgba(226,232,240,0.75)!important;box-shadow:none!important;font-size:0.82rem!important;padding:8px 16px!important;border-radius:10px!important;}
.nav-btn .stButton>button{background:transparent!important;color:rgba(148,163,184,.65)!important;border:none!important;box-shadow:none!important;text-align:left!important;justify-content:flex-start!important;padding:10px 14px!important;font-size:0.83rem!important;border-radius:8px!important;}
.nav-btn .stButton>button:hover{background:rgba(59,130,246,.10)!important;color:#BAE6FD!important;transform:none!important;}
.nav-btn-active .stButton>button{background:rgba(59,130,246,.14)!important;color:#60A5FA!important;border-left:2px solid #3B82F6!important;font-weight:700!important;box-shadow:none!important;}
/* Inputs */
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{background:rgba(255,255,255,0.04)!important;border:1px solid rgba(255,255,255,0.14)!important;border-radius:10px!important;color:#E2E8F0!important;font-family:'Inter',sans-serif!important;font-size:0.87rem!important;}
[data-testid="stTextInput"] input:focus,[data-testid="stTextArea"] textarea:focus{border-color:rgba(59,130,246,0.55)!important;box-shadow:0 0 0 2.5px rgba(59,130,246,0.13)!important;}
[data-testid="stSelectbox"]>div>div{background:rgba(255,255,255,0.04)!important;border:1px solid rgba(255,255,255,0.14)!important;border-radius:10px!important;color:#E2E8F0!important;}
[data-testid="stFileUploader"]{background:rgba(59,130,246,0.04)!important;border:1px dashed rgba(59,130,246,0.26)!important;border-radius:12px!important;}
[data-testid="stExpander"]{background:rgba(255,255,255,.018)!important;border:1px solid rgba(255,255,255,0.08)!important;border-radius:12px!important;}
[data-testid="stProgress"]>div>div{border-radius:99px!important;background:linear-gradient(90deg,#2563EB,#22D3EE)!important;}
[data-testid="stProgress"]>div{background:rgba(255,255,255,.07)!important;border-radius:99px!important;height:5px!important;}
h1,h2,h3,h4{font-family:'DM Mono',monospace!important;font-weight:500!important;}
hr{border-color:rgba(255,255,255,0.08)!important;}
::-webkit-scrollbar{width:4px;height:4px;}
::-webkit-scrollbar-thumb{background:rgba(100,60,200,.30);border-radius:4px;}
[data-testid="column"]{padding:0 4px!important;}
</style>""", unsafe_allow_html=True)

###############################################################################
# AI RESPONSE
###############################################################################
def generate_ai_response(last):
    import requests
    nm = st.session_state.student_name.split()[0]
    br = st.session_state.branch; sem = st.session_state.semester
    sys_p = f"""You are AskMNIT — {nm}'s brilliant chill senior at MNIT Jaipur.
Mix Hinglish naturally. Short punchy sentences. Warm like a best friend.
Student: {nm} | Branch: {br} | Semester: {sem}
RULES: Call them "{nm}" or "yaar/bhai". Never say "I'm an AI"."""
    msgs = [{"role":m["role"],"content":m["content"]} for m in st.session_state.chat_messages[-14:-1]]
    msgs.append({"role":"user","content":last})
    KEY = st.secrets.get("GROQ_API_KEY","") or st.session_state.get("groq_api_key","")
    if not KEY:
        return "Yaar GROQ_API_KEY set nahi hai 😅 `.streamlit/secrets.toml` mein add kar: `GROQ_API_KEY='gsk_...'`"
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile","messages":[{"role":"system","content":sys_p},*msgs],
                  "max_tokens":900,"temperature":0.82},timeout=30)
        d = r.json()
        if r.status_code==200: return d["choices"][0]["message"]["content"].strip()
        return f"Groq error: {d.get('error',{}).get('message','Unknown')}"
    except requests.Timeout: return "Connection timeout yaar ⏳"
    except Exception as e: return f"Kuch gadbad hai 😅 ({str(e)[:60]})"

def dispatch_message(text):
    text = text.strip()
    if not text: return
    st.session_state.chat_messages.append({"role":"user","content":text})
    with st.spinner("AskMNIT soch raha hai... 🤔"):
        reply = generate_ai_response(text)
    st.session_state.chat_messages.append({"role":"assistant","content":reply})

# ─────────────────────────────────────────────────────────────────────────────
# VIEW ROUTER — CHAT
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.get("view") == "chat":

    st.markdown("""<style>
    [data-testid="stSidebar"],[data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"]{display:none!important;}
    section[data-testid="stMain"]{margin-left:0!important;padding-left:0!important;}

    /* Sidebar panel */
    .cs-panel{
      position:fixed;top:0;left:0;width:200px;height:100vh;
      background:#1a1a2e;border-right:1px solid #333;
      z-index:9000;padding:16px 10px;
      transform:translateX(-100%);
      transition:transform 0.25s ease;
    }
    .cs-panel.open{transform:translateX(0);}

    /* Toggle tab — always sticking out from right edge of sidebar */
    .cs-tab{
      position:absolute;top:12px;right:-30px;
      width:30px;height:34px;
      background:#1a1a2e;border:1px solid #555;border-left:none;
      border-radius:0 6px 6px 0;
      display:flex;align-items:center;justify-content:center;
      cursor:pointer;font-size:0.9rem;color:#ccc;
      user-select:none;z-index:10001;
    }
    .cs-tab:hover{background:#2a2a3e;color:#fff;}

    /* Overlay */
    .cs-overlay{position:fixed;inset:0;z-index:8999;background:rgba(0,0,0,0.4);display:none;}
    .cs-overlay.open{display:block;}

    /* Hamburger st.button — hidden, triggered by JS click on cs-tab */
    .cs-hbtn .stButton>button{
      position:fixed!important;top:-200px!important;left:-200px!important;
      opacity:0!important;pointer-events:none!important;
      width:1px!important;height:1px!important;
    }

    /* Chat area */
    .chat-area{padding:20px 16px 40px;max-width:800px;margin:0 auto;}
    .msg-u{text-align:right;margin:8px 0;}
    .msg-a{text-align:left;margin:8px 0;}
    .bub-u{display:inline-block;background:#2563eb;color:#fff;
      padding:9px 14px;border-radius:14px 14px 2px 14px;font-size:0.85rem;max-width:70%;text-align:left;}
    .bub-a{display:inline-block;background:#2a2a3e;color:#e0e0e0;
      padding:9px 14px;border-radius:14px 14px 14px 2px;font-size:0.85rem;max-width:70%;text-align:left;}
    </style>""", unsafe_allow_html=True)

    # ── Hidden st.button (triggered by JS) ───────────────────────────────
    st.markdown('<div class="cs-hbtn">', unsafe_allow_html=True)
    if st.button("toggle", key="_cs_hbtn"):
        st.session_state.chat_sb_open = not st.session_state.chat_sb_open
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Overlay ───────────────────────────────────────────────────────────
    _oc = "open" if st.session_state.chat_sb_open else ""
    st.markdown(f'<div class="cs-overlay {_oc}" onclick="triggerToggle()"></div>', unsafe_allow_html=True)

    # ── Sidebar with visible tab on its right edge ────────────────────────
    _icon = "✕" if st.session_state.chat_sb_open else "☰"
    st.markdown(f"""
    <div class="cs-panel {_oc}" id="cs-panel">
      <div class="cs-tab" onclick="triggerToggle()">{_icon}</div>
    </div>
    <script>
    function triggerToggle() {{
      var btns = window.parent.document.querySelectorAll('button');
      for (var i = 0; i < btns.length; i++) {{
        if (btns[i].innerText.trim() === 'toggle') {{
          btns[i].click(); break;
        }}
      }}
    }}
    </script>
    """, unsafe_allow_html=True)

    # ── Messages ──────────────────────────────────────────────────────────
    st.markdown('<div class="chat-area">', unsafe_allow_html=True)
    if not st.session_state.chat_messages:
        st.markdown('<p style="color:#666;text-align:center;margin-top:40px;">AskMNIT AI — No messages yet</p>', unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_messages:
            c = msg["content"].replace("<","&lt;").replace(">","&gt;").replace("\n","<br>")
            if msg["role"] == "user":
                st.markdown(f'<div class="msg-u"><div class="bub-u">{c}</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="msg-a"><div class="bub-a">{c}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.stop()
# DASHBOARD VIEW  (100% UNCHANGED)
###############################################################################
NAV_LABELS = ["My Dashboard","My Schedule","Academics","Study Material","PYQs","Fee Portal","Mess Menu"]
with st.sidebar:
    st.markdown('<div style="padding:18px 14px 14px;border-bottom:1px solid rgba(59,130,246,0.14);"><div style="display:flex;align-items:center;gap:9px;"><div style="width:30px;height:30px;border-radius:7px;background:linear-gradient(135deg,#2563EB,#4F46E5);display:flex;align-items:center;justify-content:center;font-size:0.9rem;font-weight:700;color:white;box-shadow:0 3px 12px rgba(37,99,235,0.28);">A</div><div><div style="font-family:\'DM Mono\',monospace;font-size:0.85rem;color:#E2E8F0;">AskMNIT</div><div style="font-size:0.56rem;color:rgba(148,163,184,.40);margin-top:1px;">Student Portal</div></div></div></div>', unsafe_allow_html=True)
    bh=branch_hex(st.session_state.branch)
    st.markdown(f'<div style="padding:8px 12px 4px;"><span style="font-size:0.60rem;font-weight:700;padding:2px 9px;background:rgba(255,255,255,0.05);border:1px solid {bh}44;border-radius:5px;color:{bh};letter-spacing:0.4px;">{st.session_state.branch}</span></div>', unsafe_allow_html=True)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    for label in NAV_LABELS:
        css="nav-btn-active" if st.session_state.nav_page==label else "nav-btn"
        st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
        if st.button(label,key="nav_"+label,use_container_width=True):
            st.session_state.nav_page=label; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div style="position:fixed;bottom:18px;width:182px;padding-top:10px;border-top:1px solid rgba(255,255,255,0.06);">', unsafe_allow_html=True)
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("Logout",key="sidebar_logout",use_container_width=True):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

dash_page=st.session_state.nav_page
if dash_page!="My Dashboard":
    PMETA={"My Schedule":("My Schedule","Weekly timetable renders here."),"Academics":("Academics","Grades and CGPA records render here."),"Study Material":("Study Material","Uploaded notes render here."),"PYQs":("PYQs","Previous year papers render here."),"Fee Portal":("Fee Portal","Fee dues and receipts render here."),"Mess Menu":("Mess Menu","Weekly hostel menu renders here.")}
    title,desc=PMETA.get(dash_page,(dash_page,"Coming soon."))
    st.markdown(f'<div style="padding:24px;"><div style="font-family:\'DM Mono\',monospace;font-size:0.95rem;color:#E2E8F0;border-bottom:1px solid rgba(255,255,255,0.06);padding-bottom:14px;margin-bottom:24px;">{title.upper()}</div><div style="background:linear-gradient(160deg,#0B1120,#060A12);border:1px dashed rgba(59,130,246,0.18);border-radius:16px;padding:60px 40px;text-align:center;"><div style="font-family:\'DM Mono\',monospace;font-size:0.88rem;color:#E2E8F0;margin-bottom:8px;">{title.upper()}</div><div style="font-size:0.76rem;color:rgba(148,163,184,.44);max-width:280px;margin:0 auto;line-height:1.65;">{desc}</div></div></div>', unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# MY DASHBOARD (100% UNCHANGED)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div style='padding:0 22px 80px;'>", unsafe_allow_html=True)
h_logo,h_mid,h_right=st.columns([2,4,3])
with h_logo:
    st.markdown('<div style="display:flex;align-items:center;gap:8px;padding:13px 0 9px;"><div style="width:30px;height:30px;border-radius:7px;background:linear-gradient(135deg,#2563EB,#4F46E5);display:flex;align-items:center;justify-content:center;font-size:0.85rem;font-weight:700;color:white;">M</div><div><div style="font-family:\'DM Mono\',monospace;font-size:0.76rem;color:#E2E8F0;">MNIT Jaipur</div><div style="font-size:0.52rem;color:rgba(148,163,184,.36);">[ MNIT LOGO ]</div></div></div>', unsafe_allow_html=True)
with h_mid:
    now_str=datetime.datetime.now().strftime("%a, %d %b %Y  ·  %H:%M")
    st.markdown(f'<div style="padding:13px 0 9px;text-align:center;"><span style="font-family:\'DM Mono\',monospace;font-size:0.76rem;color:#60A5FA;letter-spacing:0.8px;">MY DASHBOARD</span><br><span style="font-size:0.57rem;color:rgba(148,163,184,.38);">{now_str}</span></div>', unsafe_allow_html=True)
with h_right:
    nm2,br2,sem2=st.session_state.student_name,st.session_state.branch,st.session_state.semester
    bh2=branch_hex(br2); pp=st.session_state.profile_pic_b64
    av_html=(f'<img src="{pp}" style="width:36px;height:36px;border-radius:50%;object-fit:cover;border:2px solid {bh2}55;">' if pp else f'<div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,{bh2},{bh2}88);display:flex;align-items:center;justify-content:center;font-size:0.85rem;font-weight:700;color:#fff;border:2px solid {bh2}55;">{initials(nm2)}</div>')
    st.markdown(f'<div style="display:flex;align-items:center;justify-content:flex-end;gap:9px;padding:10px 0 6px;">{av_html}<div><div style="font-weight:700;font-size:0.83rem;color:#E2E8F0;line-height:1.2;">{nm2}</div><div style="font-size:0.58rem;color:{bh2};font-weight:600;">{br2} · {sem2}</div></div></div>', unsafe_allow_html=True)
st.markdown('<div style="height:1px;background:linear-gradient(90deg,transparent,rgba(59,130,246,0.22),rgba(34,211,238,0.10),transparent);margin-bottom:20px;"></div>', unsafe_allow_html=True)
srow1,srow2,srow3,srow4,_=st.columns([1,1,1,1,1])
with srow1:
    st.markdown('<div class="settings-menu-btn">', unsafe_allow_html=True)
    if st.button("Settings & Profile",key="open_settings"): st.session_state.settings_mode=None if st.session_state.settings_mode=="profile" else "profile"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with srow2:
    st.markdown('<div class="settings-menu-btn">', unsafe_allow_html=True)
    if st.button("Upload Schedule",key="open_schedule"): st.session_state.settings_mode=None if st.session_state.settings_mode=="schedule" else "schedule"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with srow3:
    st.markdown('<div class="settings-menu-btn">', unsafe_allow_html=True)
    if st.button("Notifications",key="open_notif"): st.toast("No new notifications.",icon="🔔")
    st.markdown('</div>', unsafe_allow_html=True)
with srow4:
    st.markdown('<div class="open-chat-btn">', unsafe_allow_html=True)
    if st.button("✦  AskMNIT AI", key="open_chatbot"):
        st.session_state.view = "chat"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
mode=st.session_state.settings_mode
if mode=="profile":
    with st.expander("Settings & Profile",expanded=True):
        pc1,pc2=st.columns([1,2])
        with pc1:
            pp=st.session_state.profile_pic_b64; bh3=branch_hex(st.session_state.branch)
            if pp: st.markdown(f'<img src="{pp}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;border:3px solid {bh3}66;display:block;margin:0 auto 8px;">', unsafe_allow_html=True)
            else: st.markdown(f'<div style="width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,{bh3},{bh3}88);display:flex;align-items:center;justify-content:center;font-size:1.8rem;font-weight:700;color:#fff;margin:0 auto 8px;">{initials(st.session_state.student_name)}</div>', unsafe_allow_html=True)
            pf=st.file_uploader("Upload photo",type=["png","jpg","jpeg"],key="profile_pic_up",label_visibility="collapsed")
            if pf: st.session_state.profile_pic_b64=img_to_b64(pf); st.rerun()
        with pc2:
            nn=st.text_input("Full Name",value=st.session_state.student_name,key="inp_name")
            ni=st.text_input("College ID",value=st.session_state.college_id,key="inp_id")
            ns=st.selectbox("Semester",SEMESTERS,index=SEMESTERS.index(st.session_state.semester),key="sel_sem")
            nb=st.selectbox("Branch",BRANCHES,index=BRANCHES.index(st.session_state.branch),key="sel_br")
            if st.button("Save Profile",key="save_profile"):
                ob=st.session_state.branch; st.session_state.student_name=nn; st.session_state.college_id=ni; st.session_state.semester=ns; st.session_state.branch=nb
                if ob!=nb: st.session_state.attendance=blank_att(subjects_for_branch(nb))
                st.toast("Profile saved!",icon="✅"); st.session_state.settings_mode=None; st.rerun()
elif mode=="schedule":
    with st.expander("Upload Weekly Schedule PDF",expanded=True):
        pf2=st.file_uploader("Drop schedule PDF here",type=["pdf"],key="sched_upload")
        if pf2:
            st.session_state.full_schedule=process_schedule_pdf(pf2,st.session_state.branch); st.session_state.schedule_loaded=True; st.session_state.pdf_filename=pf2.name
            st.toast(f"Schedule loaded: {pf2.name}",icon="✅"); st.session_state.settings_mode=None; st.rerun()
        if st.session_state.schedule_loaded: st.markdown(f'<div style="font-size:0.75rem;color:#10B981;margin-top:6px;">Active: {st.session_state.pdf_filename}</div>', unsafe_allow_html=True)
ov=overall_pct(st.session_state.attendance); stat_badge_txt,stat_col,_=status_badge(ov)
kpi1,kpi2,kpi3,kpi4=st.columns(4)
for col,ico,val,lbl,c in [(kpi1,"📊",f"{ov}%","Overall Attendance",stat_col),(kpi2,"📚",str(len(subjects_for_branch(st.session_state.branch))),"Enrolled Subjects","#60A5FA"),(kpi3,"📅",str(len(get_today_slots(st.session_state.full_schedule)) if st.session_state.schedule_loaded else 0),"Classes Today","#22D3EE"),(kpi4,"📝",str(len(st.session_state.notes_list)),"Active Notes","#A78BFA")]:
    with col: st.markdown(f'<div style="background:linear-gradient(160deg,#0B1120,#070D1C);border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:16px 18px 14px;margin-bottom:14px;"><div style="font-size:1.4rem;margin-bottom:6px;">{ico}</div><div style="font-size:1.7rem;font-weight:800;color:{c};font-family:\'DM Mono\',monospace;line-height:1.1;">{val}</div><div style="font-size:0.68rem;color:rgba(148,163,184,.46);margin-top:4px;">{lbl}</div></div>', unsafe_allow_html=True)
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
        mins=nxt["minutes_away"]; hrs=mins//60; rem=mins%60; cd_str=(f"{hrs}h {rem}m" if hrs else f"{rem} min")+" away"; urg_c="#EF4444" if mins<15 else "#F59E0B" if mins<45 else "#22D3EE"
        st.markdown(f'<div style="background:linear-gradient(90deg,rgba(34,211,238,.06),rgba(37,99,235,.04));border:1px solid rgba(34,211,238,.18);border-radius:10px;padding:10px 16px;margin-bottom:14px;display:flex;align-items:center;justify-content:space-between;"><div><div style="font-size:0.57rem;color:rgba(148,163,184,.46);text-transform:uppercase;letter-spacing:0.8px;margin-bottom:2px;">Next Class</div><div style="font-weight:700;font-size:0.86rem;color:#E2E8F0;">{nxt["subject"]} <span style="font-size:0.67rem;color:rgba(148,163,184,.46);">{nxt["room"]}</span></div></div><div style="font-family:\'DM Mono\',monospace;font-size:0.96rem;font-weight:600;color:{urg_c};text-align:right;">{cd_str}<div style="font-size:0.57rem;color:rgba(148,163,184,.42);font-weight:400;margin-top:1px;">{fmt_time(nxt["time_start"])} – {fmt_time(nxt["time_end"])}</div></div></div>', unsafe_allow_html=True)
    if today_slots:
        rows=[today_slots[i:i+3] for i in range(0,len(today_slots),3)]
        for row in rows:
            cols=st.columns(len(row))
            for ci,(col,slot) in enumerate(zip(cols,row)):
                sh,sm=map(int,slot["time_start"].split(":")); is_past=(sh*60+sm)<now_hm; tc=TYPE_COLORS.get(slot["type"],"#60A5FA")
                is_next=(nxt is not None and slot["time_start"]==nxt["time_start"] and slot["subject"]==nxt["subject"]); bc=tc if not is_past else "rgba(255,255,255,0.06)"; cbg="linear-gradient(160deg,rgba(34,211,238,0.06),rgba(37,99,235,0.03))" if is_next else "rgba(255,255,255,0.02)" if not is_past else "rgba(255,255,255,0.01)"
                with col: st.markdown(f'<div style="background:{cbg};border:1px solid {bc};border-left:3px solid {bc};border-radius:12px;padding:13px 14px;margin-bottom:8px;"><div style="font-family:\'DM Mono\',monospace;font-size:0.78rem;font-weight:700;color:{"#E2E8F0" if not is_past else "rgba(148,163,184,0.32)"};margin-bottom:6px;">{fmt_time(slot["time_start"])}<br><span style="font-size:0.62rem;font-weight:400;color:rgba(148,163,184,0.45);">– {fmt_time(slot["time_end"])}</span></div><div style="font-size:0.82rem;font-weight:700;color:{"#F1F5F9" if not is_past else "rgba(148,163,184,0.28)"};margin-bottom:5px;">{slot["subject"]}</div><div style="display:flex;align-items:center;gap:6px;"><span style="font-size:0.62rem;color:rgba(148,163,184,.48);">{slot["room"]}</span><span style="font-size:0.58rem;padding:1px 7px;border-radius:4px;background:{tc}1A;color:{tc};font-weight:600;">{slot["type"]}</span>{"<span style=\"font-size:0.58rem;color:#22D3EE;font-weight:700;\"> NEXT</span>" if is_next else ""}</div>{"<div style=\"font-size:0.58rem;color:rgba(148,163,184,.28);margin-top:4px;text-decoration:line-through;\">Done</div>" if is_past else ""}</div>', unsafe_allow_html=True)
    else: st.markdown(f'<div style="text-align:center;padding:24px;color:rgba(148,163,184,.40);font-size:0.80rem;">No classes for {today_name}.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div style="background:rgba(59,130,246,.04);border:1px dashed rgba(59,130,246,.20);border-radius:9px;padding:9px 13px;margin-bottom:12px;font-size:0.73rem;color:rgba(148,163,184,.48);">Use <b>Upload Schedule</b> to activate the planner.</div>', unsafe_allow_html=True)
    if "planner_overrides" not in st.session_state: st.session_state.planner_overrides={}
    for st_start,st_end in [("08:00","09:00"),("09:30","10:30"),("11:00","12:00"),("12:00","13:00"),("14:00","15:00"),("15:30","16:30")]:
        override=st.session_state.planner_overrides.get(st_start,""); mp1,mp2,mp3,mp4=st.columns([1.6,4,0.8,2.2])
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
    if not unpinned: st.markdown('<div style="font-size:0.76rem;color:rgba(148,163,184,.38);text-align:center;padding:16px;font-style:italic;">No notes yet.</div>', unsafe_allow_html=True)
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
st.markdown('<div style="text-align:center;margin-top:28px;padding:10px 0;border-top:1px solid rgba(255,255,255,0.05);"><span style="font-family:\'DM Mono\',monospace;font-size:0.52rem;color:rgba(148,163,184,0.24);letter-spacing:1.2px;">ASKMNT · MNIT JAIPUR · v6.0 PREMIUM</span></div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
