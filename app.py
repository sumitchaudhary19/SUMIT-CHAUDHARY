import streamlit as st
from groq import Groq
import datetime

# ── PAGE CONFIG ──
st.set_page_config(
    page_title="AskMNIT",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── GROQ CLIENT ──
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("🚨 GROQ_API_KEY missing!")
    st.stop()

# ── SESSION STATE ──
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "ai_messages" not in st.session_state:
    st.session_state.ai_messages = []
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {"Session 1": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Session 1"
if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 1
if "pending" not in st.session_state:
    st.session_state.pending = False
if "ai_pending" not in st.session_state:
    st.session_state.ai_pending = False

# ── GREETING ──
hour = datetime.datetime.now().hour
greeting = "Good Morning ☀️" if hour < 12 else ("Good Afternoon 🌤️" if hour < 17 else "Good Evening 🌙")

# ══════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stAppViewContainer"] {
    background: #070B14 !important;
}
[data-testid="stMainBlockContainer"] {
    padding-top: 24px !important;
    padding-bottom: 40px !important;
    max-width: 100% !important;
}

header[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A0F1E 0%, #060912 100%) !important;
    border-right: 1px solid rgba(59,130,246,0.12) !important;
    width: 258px !important;
}
section[data-testid="stSidebar"] > div { padding: 0 !important; }

section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: rgba(241,245,249,0.65) !important;
    border: none !important;
    border-radius: 9px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.83rem !important;
    padding: 9px 14px !important;
    text-align: left !important;
    width: 100% !important;
    box-shadow: none !important;
    transition: all 0.15s ease !important;
    margin: 1px 0 !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(59,130,246,0.1) !important;
    color: #F1F5F9 !important;
    transform: none !important;
    box-shadow: none !important;
}

[data-testid="stMain"] .stButton > button {
    background: linear-gradient(135deg, #3B82F6 0%, #6D28D9 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    box-shadow: 0 4px 16px rgba(59,130,246,0.25) !important;
    transition: all 0.18s !important;
}
[data-testid="stMain"] .stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 22px rgba(59,130,246,0.35) !important;
}

[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
    padding: 18px 16px !important;
    transition: all 0.2s !important;
}
[data-testid="stMetric"]:hover {
    background: rgba(59,130,246,0.08) !important;
    border-color: rgba(59,130,246,0.2) !important;
    transform: translateY(-2px) !important;
}
[data-testid="stMetricLabel"] {
    color: rgba(241,245,249,0.45) !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stMetricValue"] {
    color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.7rem !important;
    letter-spacing: -1px !important;
}
[data-testid="stMetricDelta"] {
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

[data-testid="stMarkdown"] p, [data-testid="stMarkdown"] li {
    color: rgba(241,245,249,0.75) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
h1, h2, h3 {
    color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 800 !important;
    letter-spacing: -0.5px !important;
}

[data-testid="stAlert"] {
    border-radius: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    border: none !important;
}

[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"]:hover { border-color: rgba(59,130,246,0.2) !important; }
summary {
    color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
}

hr { border-color: rgba(255,255,255,0.07) !important; margin: 10px 0 !important; }

/* Chat input base — detailed styling handled inline on AI page */
[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(241,245,249,0.25) !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Suggestion pills */
.mnit-pill-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 14px;
}
.mnit-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 14px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 999px;
    color: rgba(241,245,249,0.6);
    font-size: 0.75rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease;
    white-space: nowrap;
    font-family: 'Plus Jakarta Sans', sans-serif;
    letter-spacing: 0.01em;
    text-decoration: none;
}
.mnit-pill:hover {
    background: rgba(59,130,246,0.12);
    border-color: rgba(59,130,246,0.32);
    color: #CBD5E1;
    transform: translateY(-1px);
    box-shadow: 0 2px 12px rgba(59,130,246,0.12);
}

/* Input icon row */
.mnit-input-icons {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 0 10px 10px 14px;
}
.mnit-icon-btn {
    background: none;
    border: none;
    cursor: pointer;
    color: rgba(148,163,184,0.45);
    display: flex;
    align-items: center;
    padding: 5px;
    border-radius: 7px;
    transition: all 0.15s;
}
.mnit-icon-btn:hover {
    color: rgba(148,163,184,0.85);
    background: rgba(255,255,255,0.05);
}
.mnit-disclaimer {
    text-align: center;
    font-size: 0.67rem;
    color: rgba(100,116,139,0.65);
    margin-top: 8px;
    letter-spacing: 0.01em;
    line-height: 1.5;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

[data-testid="stHorizontalBlock"] { gap: 14px !important; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(59,130,246,0.2); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:20px 16px 16px; border-bottom:1px solid rgba(255,255,255,0.07);">
        <div style="display:flex; align-items:center; gap:10px;">
            <div style="width:38px;height:38px;background:linear-gradient(135deg,#3B82F6,#6D28D9);border-radius:10px;
                        display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0;">🎓</div>
            <div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:800;font-size:1rem;color:#F1F5F9;letter-spacing:-0.3px;">AskMNIT</div>
                <div style="font-size:0.6rem;color:rgba(241,245,249,0.35);letter-spacing:1.2px;text-transform:uppercase;margin-top:1px;">Campus Intelligence</div>
            </div>
            <div style="margin-left:auto;display:flex;align-items:center;gap:4px;">
                <div style="width:6px;height:6px;background:#10B981;border-radius:50%;"></div>
                <span style="font-size:0.6rem;color:#10B981;font-weight:600;">Live</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    st.markdown("<p style='color:rgba(255,255,255,0.25);font-size:0.58rem;letter-spacing:2px;text-transform:uppercase;margin:10px 16px 4px;font-family:Plus Jakarta Sans,sans-serif;font-weight:700;'>Main</p>", unsafe_allow_html=True)

    if st.button("🏠  Dashboard", key="nav_dash", use_container_width=True):
        st.session_state.page = "dashboard"; st.rerun()
    if st.button("📅  Schedule", key="nav_schedule", use_container_width=True):
        st.session_state.page = "schedule"; st.rerun()
    if st.button("📚  Academics", key="nav_academics", use_container_width=True):
        st.session_state.page = "academics"; st.rerun()
    if st.button("💰  Fee Portal", key="nav_fee", use_container_width=True):
        st.session_state.page = "fee"; st.rerun()
    if st.button("🏢  Hostel", key="nav_hostel", use_container_width=True):
        st.session_state.page = "hostel"; st.rerun()

    st.divider()

    st.markdown("<p style='color:rgba(255,255,255,0.25);font-size:0.58rem;letter-spacing:2px;text-transform:uppercase;margin:4px 16px 4px;font-family:Plus Jakarta Sans,sans-serif;font-weight:700;'>Resources</p>", unsafe_allow_html=True)

    if st.button("📄  Syllabus & Notes", key="nav_syllabus", use_container_width=True):
        st.session_state.page = "syllabus"; st.rerun()
    if st.button("📝  Previous Year Qs", key="nav_pyq", use_container_width=True):
        st.session_state.page = "pyq"; st.rerun()
    if st.button("🏛️  Library Catalog", key="nav_library", use_container_width=True):
        st.session_state.page = "library"; st.rerun()
    if st.button("📌  Latest Notices  🔴 3", key="nav_notices", use_container_width=True):
        st.session_state.page = "notices"; st.rerun()
    if st.button("🗓️  Exam Schedule", key="nav_exam", use_container_width=True):
        st.session_state.page = "exam"; st.rerun()
    if st.button("🏆  Results & Grades", key="nav_results", use_container_width=True):
        st.session_state.page = "results"; st.rerun()

    st.divider()

    st.markdown("<p style='color:rgba(255,255,255,0.25);font-size:0.58rem;letter-spacing:2px;text-transform:uppercase;margin:4px 16px 4px;font-family:Plus Jakarta Sans,sans-serif;font-weight:700;'>Campus</p>", unsafe_allow_html=True)

    if st.button("🎉  Events & Fests  🆕", key="nav_events", use_container_width=True):
        st.session_state.page = "events"; st.rerun()
    if st.button("🏋️  Sports & Clubs", key="nav_sports", use_container_width=True):
        st.session_state.page = "sports"; st.rerun()
    if st.button("💼  Placements", key="nav_placements", use_container_width=True):
        st.session_state.page = "placements"; st.rerun()
    if st.button("🔬  Research & Labs", key="nav_research", use_container_width=True):
        st.session_state.page = "research"; st.rerun()

    st.divider()

    st.markdown("<p style='color:rgba(255,255,255,0.25);font-size:0.58rem;letter-spacing:2px;text-transform:uppercase;margin:4px 16px 4px;font-family:Plus Jakarta Sans,sans-serif;font-weight:700;'>Account</p>", unsafe_allow_html=True)

    if st.button("🤖  AskMNIT AI", key="nav_ai", use_container_width=True):
        st.session_state.page = "ai"; st.rerun()
    if st.button("⚙️  Settings", key="nav_settings", use_container_width=True):
        st.session_state.page = "settings"; st.rerun()
    if st.button("🔔  Notifications  🔴 5", key="nav_notif", use_container_width=True):
        st.session_state.page = "notifications"; st.rerun()
    if st.button("🚪  Logout", key="nav_logout", use_container_width=True):
        st.warning("Logging out...")

    st.divider()

    st.markdown("""
    <div style="padding:10px 14px 14px;">
        <div style="background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.15);
                    border-radius:12px;padding:12px;display:flex;align-items:center;gap:10px;">
            <div style="width:34px;height:34px;background:linear-gradient(135deg,#3B82F6,#6D28D9);
                        border-radius:50%;display:flex;align-items:center;justify-content:center;
                        font-weight:800;font-size:0.78rem;color:white;flex-shrink:0;">SC</div>
            <div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;font-size:0.82rem;color:#F1F5F9;">Sumit Chaudhary</div>
                <div style="font-size:0.62rem;color:rgba(59,130,246,0.8);margin-top:1px;">B.Tech Metallurgy · Sem 6</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════
if st.session_state.page == "dashboard":

    col_title, col_btn = st.columns([4, 1])
    with col_title:
        st.markdown(f"""
        <div style="margin-bottom:4px;">
            <span style="font-size:0.72rem;font-weight:600;color:#06B6D4;letter-spacing:1.5px;text-transform:uppercase;">✦ {greeting}</span>
        </div>
        <h1 style="font-size:1.8rem;margin:0 0 6px 0;letter-spacing:-1px;">
            Welcome back, <span style="background:linear-gradient(90deg,#3B82F6,#06B6D4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">Sumit Chaudhary</span> 👋
        </h1>
        <p style="color:rgba(241,245,249,0.5);font-size:0.88rem;margin:0;">Here's your campus at a glance. Stay on top of everything.</p>
        """, unsafe_allow_html=True)
    with col_btn:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("🤖 Open AskMNIT AI", use_container_width=True):
            st.session_state.page = "ai"; st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("📊 Attendance", "78%", "Above minimum ✓")
    with c2: st.metric("⏳ Next Class", "20 min", "Mineral Processing")
    with c3: st.metric("📝 Assignments", "6 / 8", "-2 pending")
    with c4: st.metric("💰 Fee Due", "₹18,500", "-5 days left")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    col_sched, col_notice = st.columns([1.1, 0.9])

    with col_sched:
        st.markdown("### 📅 Today's Schedule")
        schedule = [
            ("09:30 AM", "Mineral Processing", "Room 302 · Prof. R.K. Sharma", "✅ Done", "#6B7280"),
            ("11:30 AM", "Engineering Materials", "Metallurgy Lab 1 · Dr. Mehta", "🟢 Live", "#10B981"),
            ("02:00 PM", "Thermodynamics — II", "Room 201 · Prof. Agarwal", "⏭️ Next", "#F59E0B"),
            ("04:00 PM", "Phase Transformations", "LT-3 · Prof. Singh", "—", "#8B5CF6"),
            ("05:30 PM", "Fluid Mechanics", "Room 105 · Dr. Verma", "—", "#06B6D4"),
        ]
        for time, subject, room, status, color in schedule:
            with st.expander(f"{status}  **{subject}**  —  {time}"):
                st.markdown(f"📍 **Location:** {room}")
                st.markdown(f"🕐 **Time:** {time}")

    with col_notice:
        st.markdown("### 📌 Latest Notices")
        notices = [
            ("🔴 Urgent", "Mid-Semester exam dates announced. Check portal for schedule.", "Today · Academic Section"),
            ("🔵 Events", "Techfest 2025 registrations OPEN. Last date: 20th March.", "Yesterday · Student Activities"),
            ("🟢 Admin", "Bonafide Certificate requests now online via Student Portal.", "2 days ago · Admin Office"),
            ("🟡 Hostel", "Revised mess menu & new timings from 15th March.", "3 days ago · Hostel Office"),
        ]
        for tag, text, meta in notices:
            with st.expander(f"{tag}  {text[:45]}..."):
                st.markdown(f"📝 {text}")
                st.caption(f"🕐 {meta}")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    st.markdown("### ⚡ Quick Access")
    qa1, qa2, qa3, qa4, qa5, qa6 = st.columns(6)
    quick = [
        (qa1, "📄", "Syllabus", "syllabus"),
        (qa2, "📝", "Prev Qs", "pyq"),
        (qa3, "🏛️", "Library", "library"),
        (qa4, "💼", "Placements", "placements"),
        (qa5, "🏆", "Results", "results"),
        (qa6, "🎉", "Events", "events"),
    ]
    for col, icon, label, page in quick:
        with col:
            if st.button(f"{icon}\n{label}", use_container_width=True, key=f"qa_{page}"):
                st.session_state.page = page; st.rerun()


# ══════════════════════════════════════════════════════
# PAGE: AskMNIT AI  ← FULLY UPDATED SECTION
# ══════════════════════════════════════════════════════
elif st.session_state.page == "ai":

    # ── Header ──
    col_h1, col_h2, col_h3 = st.columns([0.5, 3, 1])
    with col_h1:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("←", key="back_ai"):
            st.session_state.page = "dashboard"; st.rerun()
    with col_h2:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;padding-top:4px;">
            <div style="width:40px;height:40px;background:linear-gradient(135deg,#3B82F6,#6D28D9);
                        border-radius:11px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;">🤖</div>
            <div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:800;font-size:1.1rem;color:#F1F5F9;">AskMNIT AI</div>
                <div style="font-size:0.68rem;color:#10B981;font-weight:500;">● Online · Powered by LLaMA 3.3 70B</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_h3:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("➕ New Chat", use_container_width=True, key="new_chat_btn"):
            n = st.session_state.chat_counter + 1
            st.session_state.chat_counter = n
            name = f"Session {n}"
            st.session_state.chat_sessions[name] = []
            st.session_state.current_chat = name
            st.rerun()

    st.divider()

    # ══════════════════════════════════════
    # UPDATED SUGGESTION PILLS
    # ══════════════════════════════════════
    st.markdown("<p style='color:rgba(241,245,249,0.28);font-size:0.65rem;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:10px;font-family:Plus Jakarta Sans,sans-serif;font-weight:600;'>💡 Try asking</p>", unsafe_allow_html=True)

    suggestions = [
        ("📚", "Mineral Processing PYQs"),
        ("🧪", "Metallurgy Lab Schedule"),
        ("📥", "Download Academic Calendar"),
        ("🏢", "Hostel Rules"),
        ("💼", "Placements info"),
    ]

    # Render pills as Streamlit buttons styled via CSS
    pill_cols = st.columns(len(suggestions))
    for idx, (icon, label) in enumerate(suggestions):
        with pill_cols[idx]:
            # We use a custom HTML pill that triggers via a hidden st.button trick
            pill_key = f"pill_{idx}"
            if st.button(f"{icon} {label}", key=pill_key, use_container_width=True):
                st.session_state.chat_sessions[st.session_state.current_chat].append(
                    {"role": "user", "content": label}
                )
                st.session_state.pending = True
                st.rerun()

    # Override pill button styles specifically
    st.markdown("""
    <style>
    /* Pill buttons override — only inside AI page suggestion row */
    div[data-testid="stMain"] div[data-testid="stHorizontalBlock"]:first-of-type .stButton > button {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: 999px !important;
        color: rgba(241,245,249,0.60) !important;
        font-size: 0.74rem !important;
        font-weight: 500 !important;
        padding: 7px 12px !important;
        box-shadow: none !important;
        transition: all 0.15s ease !important;
        letter-spacing: 0.01em !important;
    }
    div[data-testid="stMain"] div[data-testid="stHorizontalBlock"]:first-of-type .stButton > button:hover {
        background: rgba(59,130,246,0.12) !important;
        border-color: rgba(59,130,246,0.32) !important;
        color: #CBD5E1 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 12px rgba(59,130,246,0.12) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── Chat history ──
    msgs = st.session_state.chat_sessions[st.session_state.current_chat]
    if not msgs:
        st.markdown("""
        <div style="text-align:center;padding:48px 20px;opacity:0.5;">
            <div style="font-size:2.5rem;margin-bottom:12px;">🎓</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;font-size:1rem;color:#F1F5F9;margin-bottom:6px;">Hey Sumit! I'm AskMNIT</div>
            <div style="font-size:0.82rem;color:rgba(241,245,249,0.6);">Ask me anything about MNIT — academics, fees, hostel, exams, placements & more.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in msgs:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # ── Handle pending AI response ──
    if st.session_state.pending and msgs:
        with st.chat_message("assistant"):
            try:
                stream = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are AskMNIT — a helpful, friendly AI assistant for MNIT Jaipur students. Help with academics, exams, fee, hostel, library, placements, events, and campus life. Be concise and warm."},
                        *[{"role": m["role"], "content": m["content"]} for m in msgs]
                    ],
                    model="llama-3.3-70b-versatile",
                    stream=True
                )
                def gen():
                    for chunk in stream:
                        c = chunk.choices[0].delta.content
                        if c: yield c
                response = st.write_stream(gen())
                st.session_state.chat_sessions[st.session_state.current_chat].append(
                    {"role": "assistant", "content": response}
                )
            except Exception as e:
                st.error(f"Error: {e}")
        st.session_state.pending = False
        st.rerun()

    # ══════════════════════════════════════
    # CHAT INPUT — CSS-injected icons into real st.chat_input
    # ══════════════════════════════════════

    # Inject icons into the actual Streamlit chat input using CSS pseudo-elements + background-image SVGs
    st.markdown("""
    <style>
    /* Wrapper styling */
    [data-testid="stChatInput"] {
        position: relative !important;
    }
    [data-testid="stChatInput"] > div {
        background: rgba(10, 14, 26, 0.95) !important;
        border: 1px solid rgba(80, 90, 160, 0.32) !important;
        border-radius: 14px !important;
        box-shadow: 0 0 0 1px rgba(59,130,246,0.04), 0 4px 28px rgba(0,0,0,0.4) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
        padding-left: 42px !important;
        padding-right: 96px !important;
    }
    [data-testid="stChatInput"] > div:focus-within {
        border-color: rgba(59,130,246,0.45) !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.08), 0 4px 28px rgba(0,0,0,0.4) !important;
    }
    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #F1F5F9 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.875rem !important;
        padding: 14px 0px !important;
        caret-color: #3B82F6 !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: rgba(241,245,249,0.25) !important;
    }

    /* Send button styling */
    [data-testid="stChatInput"] button[data-testid="stChatInputSubmitButton"] {
        background: linear-gradient(135deg, #3B82F6, #6D28D9) !important;
        border-radius: 9px !important;
        border: none !important;
        width: 34px !important;
        height: 34px !important;
        box-shadow: 0 2px 12px rgba(59,130,246,0.35) !important;
        transition: all 0.18s !important;
        margin-right: 2px !important;
    }
    [data-testid="stChatInput"] button[data-testid="stChatInputSubmitButton"]:hover {
        opacity: 0.88 !important;
        transform: scale(1.05) !important;
        box-shadow: 0 4px 18px rgba(59,130,246,0.45) !important;
    }

    /* Paperclip icon — injected on the LEFT via ::before on the wrapper */
    [data-testid="stChatInput"] > div::before {
        content: "";
        position: absolute;
        left: 13px;
        top: 50%;
        transform: translateY(-50%);
        width: 16px;
        height: 16px;
        opacity: 0.4;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%2394A3B8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66L9.41 17.41a2 2 0 0 1-2.83-2.83l8.49-8.48'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-size: contain;
        pointer-events: none;
        z-index: 10;
    }
    [data-testid="stChatInput"] > div:focus-within::before {
        opacity: 0.65;
    }

    /* Mic icon — injected on the RIGHT via ::after, sits left of the send button */
    [data-testid="stChatInput"] > div::after {
        content: "";
        position: absolute;
        right: 54px;
        top: 50%;
        transform: translateY(-50%);
        width: 16px;
        height: 16px;
        opacity: 0.38;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%2394A3B8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z'/%3E%3Cpath d='M19 10v2a7 7 0 0 1-14 0v-2'/%3E%3Cline x1='12' y1='19' x2='12' y2='23'/%3E%3Cline x1='8' y1='23' x2='16' y2='23'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-size: contain;
        pointer-events: none;
        z-index: 10;
    }
    [data-testid="stChatInput"] > div:focus-within::after {
        opacity: 0.6;
    }
    </style>
    """, unsafe_allow_html=True)

    # The ONE real functional chat input
    if prompt := st.chat_input("Ask anything about MNIT Jaipur...", key="main_chat_input"):
        st.session_state.chat_sessions[st.session_state.current_chat].append(
            {"role": "user", "content": prompt}
        )
        st.session_state.pending = True
        st.rerun()

    # ── Disclaimer ──
    st.markdown("""
    <p style="
        text-align: center;
        font-size: 0.665rem;
        color: rgba(100,116,139,0.55);
        margin-top: 8px;
        margin-bottom: 0;
        letter-spacing: 0.01em;
        line-height: 1.5;
        font-family: 'Plus Jakarta Sans', sans-serif;
    ">
        AskMNIT can make mistakes. Please verify important information with the official admin.
    </p>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# PAGE: SCHEDULE
# ══════════════════════════════════════════════════════
elif st.session_state.page == "schedule":
    if st.button("← Back", key="back_sched"): st.session_state.page = "dashboard"; st.rerun()
    st.markdown("# 📅 Weekly Schedule")
    st.divider()
    days = {
        "Monday": [("09:30","Mineral Processing","302","R.K. Sharma"),("11:30","Engineering Materials","Lab 1","Dr. Mehta"),("02:00","Thermodynamics","201","Prof. Agarwal")],
        "Tuesday": [("10:00","Phase Transformations","LT-3","Prof. Singh"),("02:00","Fluid Mechanics","105","Dr. Verma")],
        "Wednesday": [("09:30","Mineral Processing","302","R.K. Sharma"),("11:30","Corrosion Science","Lab 2","Dr. Joshi")],
        "Thursday": [("10:00","Phase Transformations","LT-3","Prof. Singh"),("03:00","Engineering Materials","201","Dr. Mehta")],
        "Friday": [("09:30","Thermodynamics","201","Prof. Agarwal"),("02:00","Fluid Mechanics","105","Dr. Verma")]
    }
    for day, classes in days.items():
        with st.expander(f"📆 {day} — {len(classes)} classes"):
            for time, subj, room, prof in classes:
                c1, c2, c3, c4 = st.columns([1,2,1,1])
                c1.markdown(f"**{time}**")
                c2.markdown(f"**{subj}**")
                c3.markdown(f"Room {room}")
                c4.markdown(f"_{prof}_")


# ══════════════════════════════════════════════════════
# PAGE: ACADEMICS
# ══════════════════════════════════════════════════════
elif st.session_state.page == "academics":
    if st.button("← Back", key="back_acad"): st.session_state.page = "dashboard"; st.rerun()
    st.markdown("# 📚 Academics")
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("CGPA", "8.4", "+0.2 this sem")
    c2.metric("Credits Completed", "96 / 160", "Sem 6 ongoing")
    c3.metric("Active Courses", "6", "This semester")
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("### 📖 Current Subjects")
    subjects = [
        ("MT-601","Mineral Processing","R.K. Sharma","A","92%"),
        ("MT-603","Engineering Materials","Dr. Mehta","B+","85%"),
        ("MT-605","Thermodynamics II","Prof. Agarwal","A-","88%"),
        ("MT-607","Phase Transformations","Prof. Singh","B","76%"),
        ("ME-501","Fluid Mechanics","Dr. Verma","A","91%"),
        ("HS-601","Engineering Economics","Dr. Gupta","A+","95%"),
    ]
    for code, name, prof, grade, attend in subjects:
        with st.expander(f"**{code}** — {name}"):
            a, b, c, d = st.columns(4)
            a.markdown(f"👨‍🏫 **Prof:** {prof}")
            b.markdown(f"📊 **Grade:** {grade}")
            c.markdown(f"📅 **Attendance:** {attend}")
            d.markdown(f"📘 **Credits:** 4")


# ══════════════════════════════════════════════════════
# PAGE: FEE PORTAL
# ══════════════════════════════════════════════════════
elif st.session_state.page == "fee":
    if st.button("← Back", key="back_fee"): st.session_state.page = "dashboard"; st.rerun()
    st.markdown("# 💰 Fee Portal")
    st.divider()
    st.warning("⚠️ Fee payment due in **5 days** — ₹18,500 pending")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Fee (Sem 6)", "₹45,000", "")
    c2.metric("Paid", "₹26,500", "✓ Paid")
    c3.metric("Remaining", "₹18,500", "Due: 17 Mar 2026")
    st.markdown("### 💳 Payment Breakdown")
    items = [("Tuition Fee","₹32,000","✅ Paid"),("Hostel Fee","₹8,000","✅ Paid"),("Mess Fee","₹4,000","⚠️ Pending"),("Library Fee","₹500","⚠️ Pending"),("Sports Fee","₹500","⚠️ Pending")]
    for item, amount, status in items:
        c1, c2, c3 = st.columns([3,1,1])
        c1.markdown(item)
        c2.markdown(f"**{amount}**")
        c3.markdown(status)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("💳 Pay Now — ₹18,500", use_container_width=True):
        st.success("Redirecting to payment gateway...")


# ══════════════════════════════════════════════════════
# PAGE: HOSTEL
# ══════════════════════════════════════════════════════
elif st.session_state.page == "hostel":
    if st.button("← Back", key="back_hostel"): st.session_state.page = "dashboard"; st.rerun()
    st.markdown("# 🏢 Hostel Information")
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Hostel Block", "H-7", "Room 214")
    c2.metric("Roommate", "Rahul Singh", "2nd Year")
    c3.metric("Mess Balance", "₹2,400", "Rechargeable")
    st.markdown("### 🍽️ Mess Timings")
    timings = [("Breakfast","7:30 AM – 9:00 AM"),("Lunch","12:30 PM – 2:00 PM"),("Snacks","5:00 PM – 6:00 PM"),("Dinner","7:30 PM – 9:30 PM")]
    for meal, time in timings:
        c1, c2 = st.columns(2)
        c1.markdown(f"**{meal}**")
        c2.markdown(time)
    st.markdown("### 📋 Important Rules")
    rules = ["Gate closes at 11:00 PM. Late entry requires warden permission.","Visitors allowed only in visitor's room. Not permitted inside blocks.","Electricals: Iron, heater, induction NOT allowed in rooms.","Ragging strictly prohibited. Report immediately to Warden."]
    for r in rules:
        st.markdown(f"• {r}")


# ══════════════════════════════════════════════════════
# PAGE: SYLLABUS & NOTES
# ══════════════════════════════════════════════════════
elif st.session_state.page == "syllabus":
    if st.button("← Back", key="back_syl"): st.session_state.page = "dashboard"; st.rerun()
    st.markdown("# 📄 Syllabus & Notes")
    st.divider()
    sems = st.selectbox("Select Semester", ["Semester 6 (Current)","Semester 5","Semester 4","Semester 3","Semester 2","Semester 1"])
    st.markdown(f"### 📘 {sems} — Study Materials")
    subjects = ["Mineral Processing","Engineering Materials","Thermodynamics II","Phase Transformations","Fluid Mechanics","Engineering Economics"]
    for subj in subjects:
        with st.expander(f"📗 {subj}"):
            c1, c2, c3 = st.columns(3)
            if c1.button(f"📄 Syllabus", key=f"syl_{subj}"): st.success(f"Opening {subj} syllabus...")
            if c2.button(f"📓 Notes", key=f"notes_{subj}"): st.success(f"Opening {subj} notes...")
            if c3.button(f"🎥 Lectures", key=f"lec_{subj}"): st.success(f"Opening {subj} lecture videos...")


# ══════════════════════════════════════════════════════
# PAGE: PREVIOUS YEAR QS
# ══════════════════════════════════════════════════════
elif st.session_state.page == "pyq":
    if st.button("← Back", key="back_pyq"): st.session_state.page = "dashboard"; st.rerun()
    st.markdown("# 📝 Previous Year Question Papers")
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        dept = st.selectbox("Department", ["Metallurgical Engineering","Mechanical","Civil","Electrical","CSE","Chemical"])
    with col2:
        year = st.selectbox("Year", ["2024-25","2023-24","2022-23","2021-22","2020-21"])
    st.markdown(f"### 📂 {dept} — {year}")
    papers = [("Mid-Semester","Mineral Processing",year),("End-Semester","Engineering Materials",year),
              ("Mid-Semester","Thermodynamics II",year),("End-Semester","Phase Transformations",year)]
    for exam, subject, yr in papers:
        c1, c2, c3 = st.columns([2,2,1])
        c1.markdown(f"**{subject}**")
        c2.markdown(f"_{exam} · {yr}_")
        if c3.button("⬇ Download", key=f"dl_{subject}_{exam}"): st.success(f"Downloading {subject} {exam} paper...")


# ══════════════════════════════════════════════════════
# PAGE: LIBRARY
# ══════════════════════════════════════════════════════
elif st.session_state.page == "library":
    if st.button("← Back", key="back_lib"): st.session_state.page = "dashboard"; st.rerun()
    st.markdown("# 🏛️ Library Catalog")
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Books Issued", "2", "Max 4 allowed")
    c2.metric("Due Date", "18 Mar", "In 6 days")
    c3.metric("Library Hours", "8AM–10PM", "Mon–Sat")
    st.markdown("### 🔍 Search Books")
    query = st.text_input("Search by title, author or subject...", placeholder="e.g. Physical Metallurgy")
    if query:
        st.info(f"Searching for: **{query}**")
        books = ["Physical Metallurgy — Reed Hill","Introduction to Materials Science — Shackelford","Metallurgy Fundamentals — Brandt"]
        for b in books:
            c1, c2 = st.columns([3,1])
            c1.markdown(f"📖 {b}")
            if c2.button("Reserve", key=f"res_{b}"): st.success(f"Reserved: {b}")
    st.markdown("### 📚 My Issued Books")
    issued = [("Physical Metallurgy","Reed Hill","12 Mar","18 Mar"),("Fluid Mechanics","Frank White","10 Mar","16 Mar")]
    for title, author, issued_d, due in issued:
        with st.expander(f"📖 {title} — {author}"):
            st.markdown(f"📅 Issued: {issued_d} · Due: {due}")
            if st.button("🔄 Renew", key=f"renew_{title}"): st.success("Renewed for 7 more days!")


# ══════════════════════════════════════════════════════
# PAGE: NOTICES
# ══════════════════════════════════════════════════════
elif st.session_state.page == "notices":
    if st.button("← Back", key="back_notices"): st.session_state.page = "dashboard"; st.rerun()
    st.markdown("# 📌 Latest Notices")
    st.divider()
    notices = [
        ("🔴 Urgent","Academic","Mid-Semester Examination Schedule Released","The mid-semester exams will be held from March 20–27, 2026. Detailed schedule available on the academic portal. Students must carry ID cards.","Today"),
        ("🔵 Events","Student Activities","Techfest 2025 — Registrations Open","MNIT's annual technical festival registrations are now live. Events include coding, robotics, paper presentations & more. Last date: 20th March.","Yesterday"),
        ("🟢 Admin","Administration","Online Bonafide Certificate Portal Live","Students can now apply for Bonafide Certificates online via the Student Portal. No physical visits needed. Processing time: 48 hours.","2 days ago"),
        ("🟡 Hostel","Hostel Office","Revised Mess Menu & New Timings","Mess committee has revised the weekly menu. New timings effective from March 15. Dinner now till 9:30 PM. Feedback: mess@mnit.ac.in","3 days ago"),
        ("🔵 Placement","Training & Placement","Amazon, Google & Infosys Visiting Next Month","Major recruiters scheduled for April 2026. Pre-placement talks in last week of March. Register on placement portal.","4 days ago"),
    ]
    for tag, category, title, body, when in notices:
        with st.expander(f"{tag} **{title}**  ·  {when}"):
            st.markdown(f"🏷️ **Category:** {category}")
            st.markdown(f"📝 {body}")
            st.caption(f"🕐 Posted: {when}")


# ══════════════════════════════════════════════════════
# PAGE: EXAM SCHEDULE
# ══════════════════════════════════════════════════════
elif st.session_state.page == "exam":
    if st.button("← Back", key="back_exam"): st.session_state.page = "dashboard"; st.rerun()
    st.markdown("# 🗓️ Exam Schedule")
    st.divider()
    st.info("📢 Mid-Semester Exams: **March 20 – 27, 2026**")
    st.markdown("### 📋 Mid-Semester Schedule")
    exams = [
        ("20 Mar","09:30 AM","Mineral Processing","MT-601","Hall A"),
        ("21 Mar","09:30 AM","Engineering Materials","MT-603","Hall B"),
        ("22 Mar","02:00 PM","Thermodynamics II","MT-605","Hall A"),
        ("24 Mar","09:30 AM","Phase Transformations","MT-607","Hall C"),
        ("25 Mar","02:00 PM","Fluid Mechanics","ME-501","Hall D"),
        ("27 Mar","09:30 AM","Engineering Economics","HS-601","Hall B")
    ]
    for date, time, subj, code, hall in exams:
        c1, c2, c3, c4, c5 = st.columns([1.2,1,2,1,1])
        c1.markdown(f"**{date}**")
        c2.markdown(time)
        c3.markdown(f"**{subj}**")
        c4.markdown(code)
        c5.markdown(f"📍 {hall}")


# ══════════════════════════════════════════════════════
# PAGE: RESULTS & GRADES
# ══════════════════════════════════════════════════════
elif st.session_state.page == "results":
    if st.button("← Back", key="back_results"): st.session_state.page = "dashboard"; st.rerun()
    st.markdown("# 🏆 Results & Grades")
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("CGPA", "8.4 / 10", "+0.2 this sem")
    c2.metric("SGPA (Last Sem)", "8.7 / 10", "Semester 5")
    c3.metric("Class Rank", "#12 / 65", "Metallurgy Dept")
    st.markdown("### 📊 Semester-wise Performance")
    semesters = [("Sem 1","7.8"),("Sem 2","8.1"),("Sem 3","8.3"),("Sem 4","8.2"),("Sem 5","8.7"),("Sem 6","In Progress")]
    for sem, sgpa in semesters:
        c1, c2 = st.columns([2,1])
        c1.markdown(f"**{sem}**")
        c2.markdown(f"SGPA: **{sgpa}**")


# ══════════════════════════════════════════════════════
# PAGE: EVENTS
# ══════════════════════════════════════════════════════
elif st.session_state.page == "events":
    if st.button("← Back", key="back_events"): st.session_state.page = "dashboard"; st.rerun()
    st.markdown("# 🎉 Events & Fests")
    st.divider()
    events = [
        ("🔵 Upcoming","Techfest 2025","March 22–24, 2026","MNIT Campus","Annual technical festival with 40+ events — coding, robotics, hackathon, paper presentations."),
        ("🟢 Open","Cultural Fest — Bliss","April 5–7, 2026","Open Air Theatre","3-day cultural extravaganza with music, dance, drama, and celebrity performances."),
        ("🟡 Upcoming","Research Symposium","March 28, 2026","Seminar Hall","Annual research paper presentation by B.Tech, M.Tech and PhD students."),
        ("🔴 Deadline","Hackathon 2026","Register by Mar 20","Online + Campus","48-hour national-level hackathon. Prizes worth ₹2 Lakhs. Teams of 3-5."),
    ]
    for tag, name, date, venue, desc in events:
        with st.expander(f"{tag}  **{name}**  —  {date}"):
            st.markdown(f"📍 **Venue:** {venue}")
            st.markdown(f"📝 {desc}")
            if st.button(f"Register for {name}", key=f"reg_{name}"): st.success(f"Registered for {name}!")


# ══════════════════════════════════════════════════════
# PAGE: SPORTS & CLUBS
# ══════════════════════════════════════════════════════
elif st.session_state.page == "sports":
    if st.button("← Back", key="back_sports"): st.session_state.page = "dashboard"; st.rerun()
    st.markdown("# 🏋️ Sports & Clubs")
    st.divider()
    st.markdown("### 🏅 Sports Facilities")
    sports_list = [("⚽","Football","Ground A","7AM–8PM"),("🏀","Basketball","Court 1","6AM–9PM"),("🏸","Badminton","Hall 3","6AM–10PM"),("🏊","Swimming Pool","Sports Complex","6AM–8PM"),("🎾","Tennis","Court 2","7AM–7PM"),("🏋️","Gym","Sports Block","5AM–10PM")]
    for icon, sport, venue, timing in sports_list:
        c1, c2, c3 = st.columns([0.3,2,1])
        c1.markdown(icon)
        c2.markdown(f"**{sport}** — {venue}")
        c3.markdown(timing)
    st.divider()
    st.markdown("### 🎭 Technical & Cultural Clubs")
    clubs = [("💻","Coding Club","Weekly sessions, competitive programming"),("🤖","Robotics Club","Build & compete in national robotics events"),("🎵","Music Club","Jam sessions, fests, recordings"),("📸","Photography Club","Campus shoots, exhibitions"),("♟️","Chess Club","Daily practice, inter-college tournaments")]
    for icon, club, desc in clubs:
        with st.expander(f"{icon} {club}"):
            st.markdown(desc)
            if st.button(f"Join {club}", key=f"join_{club}"): st.success(f"Request sent to join {club}!")


# ══════════════════════════════════════════════════════
# PAGE: PLACEMENTS
# ══════════════════════════════════════════════════════
elif st.session_state.page == "placements":
    if st.button("← Back", key="back_place"): st.session_state.page = "dashboard"; st.rerun()
    st.markdown("# 💼 Placements")
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Package (2025)", "₹12.4 LPA", "+8% YoY")
    c2.metric("Highest Package", "₹48 LPA", "Amazon")
    c3.metric("Placement Rate", "94%", "Batch 2025")
    st.markdown("### 🏢 Upcoming Recruiters (April 2026)")
    companies = [("Amazon","SDE","₹32–48 LPA","Apr 5"),("Tata Steel","Metallurgist","₹8–12 LPA","Apr 8"),("SAIL","Graduate Engineer","₹9 LPA","Apr 10"),("Google","SWE Intern","₹2L/month","Apr 12"),("Infosys","Systems Eng","₹6.5 LPA","Apr 15")]
    for company, role, pkg, date in companies:
        c1, c2, c3, c4 = st.columns([2,2,1.5,1])
        c1.markdown(f"**{company}**")
        c2.markdown(role)
        c3.markdown(f"💰 {pkg}")
        if c4.button("Apply", key=f"apply_{company}"): st.success(f"Applied to {company}!")


# ══════════════════════════════════════════════════════
# PAGE: RESEARCH & LABS
# ══════════════════════════════════════════════════════
elif st.session_state.page == "research":
    if st.button("← Back", key="back_research"): st.session_state.page = "dashboard"; st.rerun()
    st.markdown("# 🔬 Research & Labs")
    st.divider()
    labs = [
        ("Metallography Lab","Equipment: SEM, XRD, Optical Microscope. Timings: 9AM–5PM","Dr. Mehta"),
        ("Heat Treatment Lab","Furnaces, quenching tanks, hardness testers. 9AM–6PM","Prof. Singh"),
        ("Corrosion Lab","Salt spray, electrochemical workstations. 10AM–5PM","Dr. Joshi"),
        ("Casting Lab","Sand casting, die casting equipment. 9AM–4PM","Prof. Sharma")
    ]
    for lab, desc, incharge in labs:
        with st.expander(f"🧪 {lab}"):
            st.markdown(f"🔧 {desc}")
            st.markdown(f"👨‍🔬 **In-charge:** {incharge}")
            if st.button(f"Book Slot in {lab}", key=f"book_{lab}"): st.success(f"Slot booking request sent for {lab}!")


# ══════════════════════════════════════════════════════
# PAGE: NOTIFICATIONS
# ══════════════════════════════════════════════════════
elif st.session_state.page == "notifications":
    if st.button("← Back", key="back_notif"): st.session_state.page = "dashboard"; st.rerun()
    st.markdown("# 🔔 Notifications")
    st.divider()
    notifs = [
        ("🔴","Fee payment due in 5 days — ₹18,500 pending","2 hours ago"),
        ("🔵","Mid-sem exam schedule released","Today, 9 AM"),
        ("🟢","Library book renewal successful","Yesterday"),
        ("🟡","New mess menu from March 15","Yesterday"),
        ("🔵","Techfest registrations open","2 days ago")
    ]
    for dot, msg, time in notifs:
        c1, c2, c3 = st.columns([0.2,4,1])
        c1.markdown(dot)
        c2.markdown(msg)
        c3.caption(time)
        st.divider()


# ══════════════════════════════════════════════════════
# PAGE: SETTINGS
# ══════════════════════════════════════════════════════
elif st.session_state.page == "settings":
    if st.button("← Back", key="back_settings"): st.session_state.page = "dashboard"; st.rerun()
    st.markdown("# ⚙️ Settings")
    st.divider()
    st.markdown("### 👤 Profile")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Full Name", value="Sumit Chaudhary")
        st.text_input("Roll Number", value="2022UMT1234")
        st.text_input("Branch", value="B.Tech Metallurgical Engineering")
    with c2:
        st.text_input("Email", value="sumit.22@mnit.ac.in")
        st.text_input("Phone", value="+91 98765 43210")
        st.text_input("Semester", value="6th Semester")
    st.divider()
    st.markdown("### 🔔 Notification Preferences")
    st.checkbox("Fee due reminders", value=True)
    st.checkbox("Class schedule alerts", value=True)
    st.checkbox("Notice board updates", value=True)
    st.checkbox("Placement alerts", value=False)
    st.divider()
    if st.button("💾 Save Changes"):
        st.success("✅ Settings saved successfully!")


# ══════════════════════════════════════════════════════
# FALLBACK
# ══════════════════════════════════════════════════════
else:
    st.session_state.page = "dashboard"
    st.rerun()
