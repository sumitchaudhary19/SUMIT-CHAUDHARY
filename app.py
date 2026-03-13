# ╔══════════════════════════════════════════════════════════════════════════╗
# ║          AskMNIT — Current Student Dashboard  (Session-State Driven)     ║
# ║                                                                          ║
# ║  All state persists in st.session_state — no backend required.          ║
# ║  Font: JetBrains Mono (headers) + DM Sans (body) — premium dark mode.   ║
# ╚══════════════════════════════════════════════════════════════════════════╝

import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AskMNIT — Student Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE — initialise all keys once
# ─────────────────────────────────────────────────────────────────────────────
_DEFAULTS = {
    # Navigation
    "nav_page":         "My Dashboard",

    # Profile
    "student_name":     "Sumit Chaudhary",
    "student_semester": "Semester 6  ·  B.Tech Metallurgical Engineering",
    "editing_profile":  False,

    # Attendance — subject 1
    "s1_name":    "Mineral Processing",
    "s1_present": 14,
    "s1_total":   18,
    "editing_s1": False,

    # Attendance — subject 2
    "s2_name":    "Welding Technology",
    "s2_present": 10,
    "s2_total":   18,
    "editing_s2": False,

    # Planner
    "plan_0930":       "",
    "plan_1130":       "",
    "plan_0930_saved": "",
    "plan_1130_saved": "",

    # Notes
    "notes_text": "• Mid-sem revision starts Monday\n• Submit fee by 17 Mar\n• Collect hall ticket from ERP",

    # Quick links feedback
    "ql_feedback": "",

    # AI chatbot overlay
    "show_ai": False,
    "ai_messages": [],
    "ai_pending": False,
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _att_pct(present: int, total: int) -> float:
    return round((present / total * 100) if total > 0 else 0.0, 1)

def _overall_pct() -> float:
    p = st.session_state.s1_present + st.session_state.s2_present
    t = st.session_state.s1_total   + st.session_state.s2_total
    return _att_pct(p, t)

def _status_badge(pct: float) -> tuple[str, str, str]:
    """Returns (label, text_color, bg_color)"""
    if pct >= 75:
        return "Safe ✅",    "#10B981", "rgba(16,185,129,0.12)"
    elif pct >= 65:
        return "Low ⚠️",    "#F59E0B", "rgba(245,158,11,0.12)"
    else:
        return "Critical 🔴","#EF4444", "rgba(239,68,68,0.12)"

def _subj_color(pct: float) -> str:
    return "#10B981" if pct >= 75 else "#F59E0B" if pct >= 65 else "#EF4444"


# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&family=DM+Sans:wght@300;400;500;600;700&display=swap');

/* ── Root vars ── */
:root {
    --bg:        #060B16;
    --surface:   #0D1424;
    --surface2:  #111827;
    --border:    rgba(255,255,255,0.07);
    --border2:   rgba(255,255,255,0.12);
    --accent:    #4F6EF7;
    --accent2:   #7C3AED;
    --green:     #10B981;
    --amber:     #F59E0B;
    --red:       #EF4444;
    --text:      #F1F5F9;
    --muted:     rgba(148,163,184,0.55);
    --mono:      'JetBrains Mono', monospace;
    --sans:      'DM Sans', sans-serif;
}

/* ── Base ── */
*, html, body { box-sizing: border-box; margin: 0; }
html, body, [data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    font-family: var(--sans) !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}

/* ── Hide default chrome ── */
header[data-testid="stHeader"], footer, #MainMenu,
[data-testid="stToolbar"], [data-testid="stDecoration"] {
    display: none !important;
}

/* ── Main content padding ── */
[data-testid="stMainBlockContainer"] {
    padding: 0 28px 80px 28px !important;
    max-width: 100% !important;
}

/* ════════════════════════════════════════
   SIDEBAR
════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
    min-width: 220px !important;
    max-width: 220px !important;
}
[data-testid="stSidebar"] > div {
    padding: 0 !important;
}
/* sidebar collapse arrow */
[data-testid="stSidebarCollapseButton"] button {
    background: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
    color: var(--muted) !important;
    border-radius: 8px !important;
}

/* ════════════════════════════════════════
   INPUTS
════════════════════════════════════════ */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
    font-size: 0.88rem !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(79,110,247,0.55) !important;
    box-shadow: 0 0 0 2px rgba(79,110,247,0.15) !important;
}
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label {
    color: var(--muted) !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    font-family: var(--sans) !important;
}

/* ════════════════════════════════════════
   BUTTONS — base gradient
════════════════════════════════════════ */
.stButton > button {
    background: linear-gradient(135deg, #4F6EF7, #7C3AED) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 9px !important;
    font-family: var(--sans) !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 9px 16px !important;
    box-shadow: 0 3px 12px rgba(79,110,247,0.22) !important;
    transition: all 0.16s ease !important;
    letter-spacing: 0.1px !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: scale(0.97) !important; }

/* ── Nav buttons (sidebar) ── */
.nav-btn .stButton > button {
    background: transparent !important;
    color: rgba(148,163,184,0.70) !important;
    border: none !important;
    border-radius: 9px !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 10px 14px !important;
    box-shadow: none !important;
    width: 100% !important;
    justify-content: flex-start !important;
}
.nav-btn .stButton > button:hover {
    background: rgba(79,110,247,0.10) !important;
    color: #C7D2FE !important;
    transform: none !important;
}
.nav-btn-active .stButton > button {
    background: rgba(79,110,247,0.15) !important;
    color: #818CF8 !important;
    border-left: 2px solid #4F6EF7 !important;
    font-weight: 700 !important;
    box-shadow: none !important;
}
.nav-btn-active .stButton > button:hover {
    background: rgba(79,110,247,0.20) !important;
}

/* ── Ghost button ── */
.ghost-btn .stButton > button {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid var(--border2) !important;
    color: rgba(241,245,249,0.55) !important;
    box-shadow: none !important;
}
.ghost-btn .stButton > button:hover {
    background: rgba(79,110,247,0.10) !important;
    color: var(--text) !important;
}

/* ── Present button (green) ── */
.present-btn .stButton > button {
    background: linear-gradient(135deg, #065F46, #10B981) !important;
    box-shadow: 0 3px 10px rgba(16,185,129,0.20) !important;
    font-size: 0.78rem !important;
    padding: 7px 14px !important;
}

/* ── Absent button (red) ── */
.absent-btn .stButton > button {
    background: linear-gradient(135deg, #7F1D1D, #EF4444) !important;
    box-shadow: 0 3px 10px rgba(239,68,68,0.18) !important;
    font-size: 0.78rem !important;
    padding: 7px 14px !important;
}

/* ── Save button (amber) ── */
.save-btn .stButton > button {
    background: linear-gradient(135deg, #92400E, #F59E0B) !important;
    box-shadow: 0 3px 10px rgba(245,158,11,0.20) !important;
    font-size: 0.78rem !important;
    padding: 7px 13px !important;
}

/* ── Edit button ── */
.edit-btn .stButton > button {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid var(--border2) !important;
    color: rgba(148,163,184,0.70) !important;
    font-size: 0.72rem !important;
    padding: 4px 10px !important;
    box-shadow: none !important;
}
.edit-btn .stButton > button:hover {
    color: #C7D2FE !important;
    background: rgba(79,110,247,0.12) !important;
    border-color: rgba(79,110,247,0.35) !important;
}

/* ── Quick-link buttons ── */
.ql-btn .stButton > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--border2) !important;
    color: rgba(199,210,254,0.70) !important;
    box-shadow: none !important;
    font-size: 0.80rem !important;
    padding: 9px 14px !important;
    text-align: left !important;
    justify-content: flex-start !important;
}
.ql-btn .stButton > button:hover {
    background: rgba(79,110,247,0.12) !important;
    border-color: rgba(79,110,247,0.35) !important;
    color: #C7D2FE !important;
    transform: none !important;
}

/* ── Logout button ── */
.logout-btn .stButton > button {
    background: rgba(239,68,68,0.10) !important;
    border: 1px solid rgba(239,68,68,0.22) !important;
    color: #FCA5A5 !important;
    box-shadow: none !important;
    font-size: 0.80rem !important;
}
.logout-btn .stButton > button:hover {
    background: rgba(239,68,68,0.20) !important;
}

/* ── Floating AI button ── */
.floating-ai-btn .stButton > button {
    background: linear-gradient(135deg, #059669, #10B981) !important;
    border-radius: 999px !important;
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    padding: 13px 24px !important;
    box-shadow: 0 6px 28px rgba(16,185,129,0.40) !important;
    letter-spacing: 0.2px !important;
    font-family: var(--mono) !important;
}
.floating-ai-btn .stButton > button:hover {
    box-shadow: 0 8px 36px rgba(16,185,129,0.55) !important;
    transform: translateY(-2px) scale(1.02) !important;
}

/* ── AI chat send button ── */
.ai-send-btn .stButton > button {
    background: linear-gradient(135deg, #059669, #10B981) !important;
    padding: 10px 18px !important;
    font-size: 0.80rem !important;
    box-shadow: none !important;
}

/* ── Progress bar ── */
[data-testid="stProgress"] > div > div {
    border-radius: 99px !important;
    background: linear-gradient(90deg, #4F6EF7, #7C3AED) !important;
}
[data-testid="stProgress"] > div {
    background: rgba(255,255,255,0.07) !important;
    border-radius: 99px !important;
}

/* ── Chat message ── */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    font-family: var(--sans) !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] > div {
    background: rgba(13,20,36,0.98) !important;
    border: 1px solid rgba(79,110,247,0.30) !important;
    border-radius: 14px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
}
[data-testid="stChatInput"] button[data-testid="stChatInputSubmitButton"] {
    background: linear-gradient(135deg, #4F6EF7, #7C3AED) !important;
    border-radius: 8px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(79,110,247,0.22); border-radius: 4px; }

/* ── Misc markdown text ── */
[data-testid="stMarkdown"] p,
[data-testid="stMarkdown"] li {
    color: rgba(241,245,249,0.70) !important;
    font-family: var(--sans) !important;
}
h1, h2, h3, h4 {
    font-family: var(--mono) !important;
    color: var(--text) !important;
    font-weight: 700 !important;
}
hr { border-color: var(--border) !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}
summary {
    font-family: var(--sans) !important;
    font-weight: 600 !important;
    color: var(--text) !important;
}

/* ── Columns gap fix ── */
[data-testid="column"] { padding: 0 6px !important; }
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════════════════════
NAV_ITEMS = [
    ("🏠", "My Dashboard"),
    ("📅", "My Schedule"),
    ("📚", "Academics"),
    ("📝", "Study Material"),
    ("📂", "PYQs"),
    ("💰", "Fee Portal"),
    ("🍱", "Mess Menu"),
]

with st.sidebar:
    # ── Brand ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="padding:22px 16px 18px;border-bottom:1px solid rgba(255,255,255,0.07);">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:34px;height:34px;border-radius:9px;
                        background:linear-gradient(135deg,#4F6EF7,#7C3AED);
                        display:flex;align-items:center;justify-content:center;
                        font-size:1.1rem;box-shadow:0 4px 14px rgba(79,110,247,0.30);">
                &#127891;
            </div>
            <div>
                <div style="font-family:'JetBrains Mono',monospace;font-weight:800;
                            font-size:0.90rem;color:#F1F5F9;letter-spacing:-0.3px;">AskMNIT</div>
                <div style="font-size:0.60rem;color:rgba(148,163,184,0.50);margin-top:1px;">
                    Student Portal
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Nav items ──────────────────────────────────────────────────────────
    for icon, label in NAV_ITEMS:
        is_active = st.session_state.nav_page == label
        css_class = "nav-btn-active" if is_active else "nav-btn"
        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.button(f"{icon}  {label}", key="nav_" + label, use_container_width=True):
            st.session_state.nav_page = label
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Spacer + logout ────────────────────────────────────────────────────
    st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="position:fixed;bottom:24px;width:188px;
                border-top:1px solid rgba(255,255,255,0.07);padding-top:12px;">
    """, unsafe_allow_html=True)
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("🚪  Logout", key="sidebar_logout", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# NON-DASHBOARD PAGES (placeholder views)
# ═════════════════════════════════════════════════════════════════════════════
page = st.session_state.nav_page

if page != "My Dashboard":
    PAGE_META = {
        "My Schedule":   ("📅", "My Schedule",   "Your weekly class schedule will appear here."),
        "Academics":     ("📚", "Academics",      "Grades, CGPA, and academic records will appear here."),
        "Study Material":("📝", "Study Material", "Uploaded notes and resources will appear here."),
        "PYQs":          ("📂", "PYQs",           "Previous year question papers will appear here."),
        "Fee Portal":    ("💰", "Fee Portal",     "Fee dues, payment history and receipts will appear here."),
        "Mess Menu":     ("🍱", "Mess Menu",      "Weekly mess menu from the hostel will appear here."),
    }
    icon, title, desc = PAGE_META.get(page, ("📄", page, "Content coming soon."))

    # Header bar
    st.markdown(
        '<div style="display:flex;align-items:center;justify-content:space-between;'
        'padding:18px 0 14px;border-bottom:1px solid rgba(255,255,255,0.07);margin-bottom:28px;">'
        '<div style="display:flex;align-items:center;gap:10px;">'
        '<span style="font-size:1.4rem;">' + icon + '</span>'
        '<span style="font-family:\'JetBrains Mono\',monospace;font-weight:700;'
        'font-size:1.1rem;color:#F1F5F9;">' + title + '</span>'
        '</div>'
        '<div style="font-size:0.65rem;color:rgba(100,116,139,0.50);font-weight:600;">'
        'AskMNIT Student Portal</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="background:linear-gradient(160deg,#0D1424,#060B16);'
        'border:1px dashed rgba(79,110,247,0.20);border-radius:16px;'
        'padding:60px 40px;text-align:center;">'
        '<div style="font-size:3rem;margin-bottom:16px;opacity:0.35;">' + icon + '</div>'
        '<div style="font-family:\'JetBrains Mono\',monospace;font-weight:700;'
        'font-size:1rem;color:#F1F5F9;margin-bottom:8px;">' + title + '</div>'
        '<div style="font-size:0.80rem;color:rgba(148,163,184,0.50);max-width:320px;'
        'margin:0 auto;line-height:1.65;">' + desc + '</div>'
        '<div style="margin-top:18px;font-size:0.65rem;color:rgba(79,110,247,0.50);">'
        '[ Functionality will be wired in a future update ]</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.stop()


# ═════════════════════════════════════════════════════════════════════════════
# MAIN DASHBOARD  (page == "My Dashboard")
# ═════════════════════════════════════════════════════════════════════════════

# ── TOP HEADER BAR ────────────────────────────────────────────────────────────
hdr_l, hdr_mid, hdr_r = st.columns([2, 5, 2])

with hdr_l:
    # MNIT Logo placeholder
    st.markdown(
        '<div style="display:flex;align-items:center;gap:9px;padding:14px 0 10px;">'
        '<div style="width:36px;height:36px;border-radius:9px;'
        'background:linear-gradient(135deg,#4F6EF7,#7C3AED);'
        'display:flex;align-items:center;justify-content:center;'
        'font-size:1.0rem;font-weight:800;color:white;'
        'box-shadow:0 4px 14px rgba(79,110,247,0.28);">M</div>'
        '<div>'
        '<div style="font-family:\'JetBrains Mono\',monospace;font-weight:800;'
        'font-size:0.82rem;color:#F1F5F9;letter-spacing:-0.2px;">MNIT Jaipur</div>'
        '<div style="font-size:0.58rem;color:rgba(148,163,184,0.45);margin-top:1px;">'
        '[ MNIT LOGO ]</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

with hdr_mid:
    # Page title
    st.markdown(
        '<div style="padding:14px 0 10px;text-align:center;">'
        '<span style="font-family:\'JetBrains Mono\',monospace;font-weight:800;'
        'font-size:0.95rem;color:#818CF8;letter-spacing:0.5px;">MY DASHBOARD</span>'
        '</div>',
        unsafe_allow_html=True,
    )

with hdr_r:
    # Notification + Profile icons
    st.markdown(
        '<div style="display:flex;align-items:center;justify-content:flex-end;'
        'gap:10px;padding:14px 0 10px;">'
        '<div title="Notifications" style="width:34px;height:34px;border-radius:9px;'
        'background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.10);'
        'display:flex;align-items:center;justify-content:center;font-size:1rem;'
        'cursor:pointer;transition:background 0.15s;" '
        'onmouseover="this.style.background=\'rgba(79,110,247,0.15)\'" '
        'onmouseout="this.style.background=\'rgba(255,255,255,0.05)\'">&#128276;</div>'
        '<div title="Profile" style="width:34px;height:34px;border-radius:9px;'
        'background:linear-gradient(135deg,#4F6EF7,#7C3AED);'
        'display:flex;align-items:center;justify-content:center;font-size:1rem;'
        'font-weight:700;color:white;cursor:pointer;'
        'box-shadow:0 3px 10px rgba(79,110,247,0.22);">SC</div>'
        '</div>',
        unsafe_allow_html=True,
    )

# Thin separator line
st.markdown(
    '<div style="height:1px;background:linear-gradient(90deg,'
    'transparent,rgba(79,110,247,0.35),transparent);margin-bottom:20px;"></div>',
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# ROW 1 — PROFILE  +  ATTENDANCE METER
# ══════════════════════════════════════════════════════════════════════════════
col_profile, col_att = st.columns([1, 1.8], gap="large")

# ─────────────────────────────
# LEFT: STUDENT PROFILE CARD
# ─────────────────────────────
with col_profile:
    st.markdown(
        '<div style="background:linear-gradient(160deg,#0D1424,#0A1020);'
        'border:1px solid rgba(79,110,247,0.22);border-radius:18px;'
        'padding:22px 22px 18px;height:100%;">'

        '<div style="display:flex;align-items:center;justify-content:space-between;'
        'margin-bottom:16px;">'
        '<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.60rem;'
        'font-weight:700;color:rgba(100,116,139,0.55);'
        'text-transform:uppercase;letter-spacing:1.2px;">Student Profile</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.editing_profile:
        new_name = st.text_input("Full Name", value=st.session_state.student_name,
                                  key="edit_name_input")
        new_sem  = st.text_input("Course / Semester", value=st.session_state.student_semester,
                                  key="edit_sem_input")
        sv1, sv2 = st.columns(2)
        with sv1:
            if st.button("💾 Save", key="save_profile", use_container_width=True):
                st.session_state.student_name     = new_name
                st.session_state.student_semester = new_sem
                st.session_state.editing_profile  = False
                st.rerun()
        with sv2:
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("Cancel", key="cancel_profile", use_container_width=True):
                st.session_state.editing_profile = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Avatar + name
        initials = "".join(w[0].upper() for w in st.session_state.student_name.split()[:2])
        st.markdown(
            '<div style="display:flex;align-items:center;gap:14px;margin-bottom:14px;">'
            '<div style="width:52px;height:52px;border-radius:14px;flex-shrink:0;'
            'background:linear-gradient(135deg,#4F6EF7,#7C3AED);'
            'display:flex;align-items:center;justify-content:center;'
            'font-family:\'JetBrains Mono\',monospace;font-weight:800;'
            'font-size:1.1rem;color:white;'
            'box-shadow:0 4px 16px rgba(79,110,247,0.28);">'
            + initials + '</div>'
            '<div>'
            '<div style="font-weight:700;font-size:1.0rem;color:#F1F5F9;'
            'font-family:\'DM Sans\',sans-serif;margin-bottom:4px;">'
            + st.session_state.student_name + '</div>'
            '<div style="font-size:0.72rem;color:rgba(148,163,184,0.60);line-height:1.5;">'
            + st.session_state.student_semester + '</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )

        # Info pills row
        st.markdown(
            '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px;">'
            '<span style="font-size:0.65rem;background:rgba(79,110,247,0.12);'
            'border:1px solid rgba(79,110,247,0.25);border-radius:6px;'
            'padding:3px 10px;color:#818CF8;font-weight:600;">MNIT Jaipur</span>'
            '<span style="font-size:0.65rem;background:rgba(16,185,129,0.10);'
            'border:1px solid rgba(16,185,129,0.22);border-radius:6px;'
            'padding:3px 10px;color:#34D399;font-weight:600;">Active</span>'
            '<span style="font-size:0.65rem;background:rgba(245,158,11,0.10);'
            'border:1px solid rgba(245,158,11,0.22);border-radius:6px;'
            'padding:3px 10px;color:#FCD34D;font-weight:600;">Sem 6</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="edit-btn">', unsafe_allow_html=True)
        if st.button("✏️  Edit Profile", key="edit_profile_btn", use_container_width=True):
            st.session_state.editing_profile = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────
# RIGHT: ATTENDANCE METER
# ─────────────────────────────
with col_att:
    overall   = _overall_pct()
    badge_lbl, badge_tc, badge_bg = _status_badge(overall)

    st.markdown(
        '<div style="background:linear-gradient(160deg,#0D1424,#0A1020);'
        'border:1px solid rgba(255,255,255,0.07);border-radius:18px;'
        'padding:22px 22px 18px;">'

        '<div style="display:flex;align-items:center;justify-content:space-between;'
        'margin-bottom:16px;">'
        '<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.60rem;'
        'font-weight:700;color:rgba(100,116,139,0.55);'
        'text-transform:uppercase;letter-spacing:1.2px;">Attendance Meter</div>'
        '<span style="font-size:0.68rem;font-weight:700;padding:4px 12px;'
        'border-radius:999px;background:' + badge_bg + ';color:' + badge_tc + ';'
        'border:1px solid ' + badge_tc + '44;">' + badge_lbl + '</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Overall %
    att_color_str = _subj_color(overall)
    st.markdown(
        '<div style="display:flex;align-items:center;gap:16px;margin-bottom:14px;">'
        '<div style="font-family:\'JetBrains Mono\',monospace;font-weight:800;'
        'font-size:2.6rem;color:' + att_color_str + ';letter-spacing:-2px;line-height:1;">'
        + str(overall) + '<span style="font-size:1.4rem;">%</span></div>'
        '<div>'
        '<div style="font-size:0.72rem;color:rgba(148,163,184,0.55);">Overall this semester</div>'
        '<div style="font-size:0.68rem;color:rgba(100,116,139,0.45);margin-top:2px;">'
        'Min required: 75%</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )
    st.progress(min(overall / 100, 1.0))

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ── Subject rows ─────────────────────────────────────────────────────
    for subj_key, name_key, present_key, total_key, edit_key, idx in [
        ("s1", "s1_name", "s1_present", "s1_total", "editing_s1", 1),
        ("s2", "s2_name", "s2_present", "s2_total", "editing_s2", 2),
    ]:
        sname   = st.session_state[name_key]
        spres   = st.session_state[present_key]
        stotal  = st.session_state[total_key]
        spct    = _att_pct(spres, stotal)
        sc      = _subj_color(spct)

        st.markdown(
            '<div style="background:rgba(255,255,255,0.025);'
            'border:1px solid rgba(255,255,255,0.07);'
            'border-radius:12px;padding:12px 14px;margin-bottom:10px;">',
            unsafe_allow_html=True,
        )

        if st.session_state[edit_key]:
            # ── Edit subject name mode ──────────────────────────────────
            new_sname = st.text_input(
                "Subject Name", value=sname, key="edit_" + subj_key + "_name_val"
            )
            ec1, ec2 = st.columns(2)
            with ec1:
                if st.button("💾 Save", key="save_" + subj_key + "_name", use_container_width=True):
                    st.session_state[name_key] = new_sname
                    st.session_state[edit_key] = False
                    st.rerun()
            with ec2:
                st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
                if st.button("Cancel", key="cancel_" + subj_key + "_name", use_container_width=True):
                    st.session_state[edit_key] = False
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            # ── Normal view ─────────────────────────────────────────────
            sa, sb, sc_col, sd_col, se_col = st.columns([4, 2, 1.2, 1.2, 1])

            with sa:
                st.markdown(
                    '<div style="font-size:0.82rem;font-weight:600;'
                    'color:#E2E8F0;margin-bottom:2px;">' + sname + '</div>'
                    '<div style="font-family:\'JetBrains Mono\',monospace;'
                    'font-size:0.70rem;color:rgba(148,163,184,0.55);">'
                    'Total: ' + str(spres) + '/' + str(stotal) + '</div>',
                    unsafe_allow_html=True,
                )
            with sb:
                pct_color = _subj_color(spct)
                st.markdown(
                    '<div style="text-align:right;font-family:\'JetBrains Mono\',monospace;'
                    'font-weight:800;font-size:1.1rem;color:' + pct_color + ';padding-top:2px;">'
                    + str(spct) + '%</div>',
                    unsafe_allow_html=True,
                )
            with sc_col:
                st.markdown('<div class="present-btn">', unsafe_allow_html=True)
                if st.button("✓ Present", key="pres_" + subj_key, use_container_width=True):
                    st.session_state[present_key] += 1
                    st.session_state[total_key]   += 1
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with sd_col:
                st.markdown('<div class="absent-btn">', unsafe_allow_html=True)
                if st.button("✗ Absent", key="abs_" + subj_key, use_container_width=True):
                    st.session_state[total_key] += 1
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with se_col:
                st.markdown('<div class="edit-btn">', unsafe_allow_html=True)
                if st.button("✏", key="edit_" + subj_key + "_btn", use_container_width=True):
                    st.session_state[edit_key] = True
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ROW 2 — TODAY'S PLANNER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div style="background:linear-gradient(160deg,#0D1424,#0A1020);'
    'border:1px solid rgba(255,255,255,0.07);border-radius:18px;'
    'padding:22px 22px 18px;margin-bottom:16px;">'
    '<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.60rem;'
    'font-weight:700;color:rgba(100,116,139,0.55);text-transform:uppercase;'
    'letter-spacing:1.2px;margin-bottom:16px;">Today\'s Planner</div>',
    unsafe_allow_html=True,
)

PLANNER_SLOTS = [
    ("09:30 AM", "plan_0930", "plan_0930_saved"),
    ("11:30 AM", "plan_1130", "plan_1130_saved"),
]

for time_label, input_key, saved_key in PLANNER_SLOTS:
    p1, p2, p3, p4 = st.columns([1.2, 5, 1, 2])

    with p1:
        st.markdown(
            '<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.72rem;'
            'font-weight:700;color:rgba(79,110,247,0.80);'
            'padding-top:10px;white-space:nowrap;">' + time_label + '</div>',
            unsafe_allow_html=True,
        )
    with p2:
        entry = st.text_input(
            label="",
            value=st.session_state[input_key],
            placeholder="Add a task, note, or reminder…",
            key="planner_input_" + input_key,
            label_visibility="collapsed",
        )
        st.session_state[input_key] = entry
    with p3:
        st.markdown('<div class="save-btn">', unsafe_allow_html=True)
        if st.button("💾", key="save_planner_" + input_key, use_container_width=True):
            st.session_state[saved_key] = st.session_state[input_key]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with p4:
        saved_text = st.session_state[saved_key]
        if saved_text:
            st.markdown(
                '<div style="font-size:0.72rem;color:#34D399;'
                'background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.18);'
                'border-radius:7px;padding:5px 10px;margin-top:2px;'
                'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'
                '✓ ' + saved_text + '</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="font-size:0.68rem;color:rgba(100,116,139,0.40);'
                'padding-top:8px;font-style:italic;">not saved yet</div>',
                unsafe_allow_html=True,
            )

st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ROW 3 — QUICK LINKS  +  PERSONAL NOTES
# ══════════════════════════════════════════════════════════════════════════════
ql_col, notes_col = st.columns([1, 1.2], gap="large")

# ── QUICK LINKS ────────────────────────────────────────────────────────────
with ql_col:
    st.markdown(
        '<div style="background:linear-gradient(160deg,#0D1424,#0A1020);'
        'border:1px solid rgba(255,255,255,0.07);border-radius:18px;'
        'padding:22px 22px 18px;height:100%;">'
        '<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.60rem;'
        'font-weight:700;color:rgba(100,116,139,0.55);text-transform:uppercase;'
        'letter-spacing:1.2px;margin-bottom:14px;">Quick Links</div>',
        unsafe_allow_html=True,
    )

    QUICK_LINKS = [
        ("📤", "Upload Syllabus",   "Syllabus file uploader will be enabled here."),
        ("🔗", "Add PYQ Link",      "PYQ link manager will be enabled here."),
        ("🔍", "Library Search",    "Library catalogue search will open here."),
    ]

    st.markdown('<div class="ql-btn">', unsafe_allow_html=True)
    for icon, label, feedback in QUICK_LINKS:
        if st.button(icon + "  " + label, key="ql_" + label, use_container_width=True):
            st.session_state.ql_feedback = feedback
            st.rerun()
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.ql_feedback:
        st.markdown(
            '<div style="background:rgba(79,110,247,0.08);'
            'border:1px solid rgba(79,110,247,0.22);border-radius:9px;'
            'padding:9px 13px;margin-top:8px;font-size:0.74rem;'
            'color:rgba(199,210,254,0.70);line-height:1.5;">'
            '&#128276; ' + st.session_state.ql_feedback + '</div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

# ── PERSONAL NOTES ─────────────────────────────────────────────────────────
with notes_col:
    st.markdown(
        '<div style="background:linear-gradient(160deg,#0D1424,#0A1020);'
        'border:1px solid rgba(255,255,255,0.07);border-radius:18px;'
        'padding:22px 22px 18px;height:100%;">'
        '<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.60rem;'
        'font-weight:700;color:rgba(100,116,139,0.55);text-transform:uppercase;'
        'letter-spacing:1.2px;margin-bottom:14px;">Personal Notes</div>',
        unsafe_allow_html=True,
    )

    notes_val = st.text_area(
        label="",
        value=st.session_state.notes_text,
        height=140,
        placeholder="• Add a note…",
        key="notes_textarea",
        label_visibility="collapsed",
    )

    n1, n2 = st.columns([1, 1])
    with n1:
        st.markdown('<div class="save-btn">', unsafe_allow_html=True)
        if st.button("💾  Save Notes", key="save_notes_btn", use_container_width=True):
            st.session_state.notes_text = notes_val
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with n2:
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("🗑  Clear", key="clear_notes_btn", use_container_width=True):
            st.session_state.notes_text = ""
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Saved preview
    if st.session_state.notes_text:
        lines = st.session_state.notes_text.strip().split("\n")
        preview_html = "".join(
            '<div style="font-size:0.76rem;color:rgba(148,163,184,0.65);'
            'padding:3px 0;line-height:1.55;border-bottom:1px solid rgba(255,255,255,0.04);">'
            + (line if line.startswith("•") else "• " + line) +
            '</div>'
            for line in lines if line.strip()
        )
        st.markdown(
            '<div style="margin-top:12px;background:rgba(255,255,255,0.02);'
            'border:1px solid rgba(255,255,255,0.06);border-radius:9px;'
            'padding:10px 14px;max-height:100px;overflow-y:auto;">'
            + preview_html + '</div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FLOATING AI BUTTON + CHATBOT OVERLAY
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)

# Floating container — right-aligned
_, _, float_col = st.columns([3, 2, 1])
with float_col:
    st.markdown('<div class="floating-ai-btn">', unsafe_allow_html=True)
    if st.button("🤖 AskMNIT AI", key="float_ai_btn", use_container_width=True):
        st.session_state.show_ai    = not st.session_state.show_ai
        st.session_state.ai_messages = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Chatbot overlay panel
if st.session_state.show_ai:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    st.markdown(
        '<div style="background:linear-gradient(160deg,#0D1424,#070E1C);'
        'border:1px solid rgba(16,185,129,0.28);border-radius:20px;'
        'padding:22px 22px 10px;'
        'box-shadow:0 12px 48px rgba(16,185,129,0.14);">'

        '<div style="display:flex;align-items:center;justify-content:space-between;'
        'margin-bottom:16px;">'
        '<div style="display:flex;align-items:center;gap:10px;">'
        '<div style="width:32px;height:32px;border-radius:9px;'
        'background:linear-gradient(135deg,#059669,#10B981);'
        'display:flex;align-items:center;justify-content:center;font-size:0.9rem;'
        'box-shadow:0 3px 12px rgba(16,185,129,0.30);">&#129302;</div>'
        '<div>'
        '<div style="font-family:\'JetBrains Mono\',monospace;font-weight:800;'
        'font-size:0.88rem;color:#F1F5F9;">AskMNIT AI</div>'
        '<div style="font-size:0.58rem;color:#10B981;font-weight:600;">&#9679; Live</div>'
        '</div></div>'
        '<div style="font-size:0.68rem;color:rgba(100,116,139,0.45);">'
        'Powered by LLaMA 3.3 70B</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Chat history
    if not st.session_state.ai_messages:
        st.markdown(
            '<div style="text-align:center;padding:28px 16px 20px;opacity:0.55;">'
            '<div style="font-size:2rem;margin-bottom:10px;">&#129302;</div>'
            '<div style="font-family:\'JetBrains Mono\',monospace;font-weight:700;'
            'font-size:0.88rem;color:#F1F5F9;margin-bottom:6px;">'
            'What can I help you with, '
            + st.session_state.student_name.split()[0] + '?</div>'
            '<div style="font-size:0.75rem;color:rgba(241,245,249,0.45);'
            'max-width:320px;margin:0 auto;line-height:1.65;">'
            'Ask about PYQs, attendance shortage, exam schedule, '
            'fee deadlines, or any campus query.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        for msg in st.session_state.ai_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # AI response (demo — no API key needed for basic demo responses)
    if st.session_state.ai_pending and st.session_state.ai_messages:
        last = st.session_state.ai_messages[-1]["content"]
        lower = last.lower()
        with st.chat_message("assistant"):
            if "attendance" in lower or "present" in lower:
                overall_now = _overall_pct()
                s1_pct = _att_pct(st.session_state.s1_present, st.session_state.s1_total)
                s2_pct = _att_pct(st.session_state.s2_present, st.session_state.s2_total)
                resp = (
                    "**Your current attendance summary:**\n\n"
                    "- Overall: **" + str(overall_now) + "%**\n"
                    "- " + st.session_state.s1_name + ": **" + str(s1_pct) + "%** "
                    "(" + str(st.session_state.s1_present) + "/" + str(st.session_state.s1_total) + ")\n"
                    "- " + st.session_state.s2_name + ": **" + str(s2_pct) + "%** "
                    "(" + str(st.session_state.s2_present) + "/" + str(st.session_state.s2_total) + ")\n\n"
                    + ("✅ You're above the 75% threshold — keep it up!" if overall_now >= 75
                       else "⚠️ You're below 75% — try not to miss any more classes.")
                )
            elif "fee" in lower or "due" in lower or "pay" in lower:
                resp = ("Your semester fee status is available in the **Fee Portal** section. "
                        "Head to the sidebar → 💰 Fee Portal. "
                        "Remember to pay before the due date to avoid late charges.")
            elif "pyq" in lower or "previous year" in lower or "question" in lower:
                resp = ("You can access Previous Year Papers from the **PYQs** section in the sidebar. "
                        "You can also add custom PYQ links using the 'Add PYQ Link' quick-link on this dashboard.")
            elif "timetable" in lower or "schedule" in lower or "class" in lower:
                resp = ("Your full weekly timetable is in the **My Schedule** section. "
                        "Today's planner on this dashboard is for quick personal reminders — "
                        "use the 💾 Save button to lock them in.")
            elif "planner" in lower or "task" in lower or "reminder" in lower:
                s1 = st.session_state.plan_0930_saved
                s2 = st.session_state.plan_1130_saved
                resp = ("**Your saved planner entries for today:**\n\n"
                        "- 09:30 AM: " + (s1 if s1 else "_nothing saved_") + "\n"
                        "- 11:30 AM: " + (s2 if s2 else "_nothing saved_") + "\n\n"
                        "You can edit them directly in the planner section above.")
            elif "exam" in lower or "mid" in lower or "end" in lower:
                resp = ("**Upcoming exam info** is available in the Academics section. "
                        "Mid-semester exams are typically announced 2 weeks prior on the ERP portal. "
                        "Check your notice board or ERP for official dates.")
            elif "hostel" in lower or "mess" in lower or "food" in lower:
                resp = ("The weekly mess menu is in the **🍱 Mess Menu** section of the sidebar. "
                        "For hostel-related queries, contact your hostel warden directly.")
            else:
                resp = (
                    "I'm AskMNIT — your campus AI assistant. I can help you with:\n\n"
                    "- **Attendance** — track and analyse your subject-wise data\n"
                    "- **PYQs** — access and organise previous year papers\n"
                    "- **Planner** — review your saved daily tasks\n"
                    "- **Fees** — understand due dates and payment steps\n"
                    "- **Exams** — schedule, tips, and prep strategies\n\n"
                    "What would you like to know?"
                )
            st.markdown(resp)
            st.session_state.ai_messages.append({"role": "assistant", "content": resp})
        st.session_state.ai_pending = False
        st.rerun()

    # Chat input
    if prompt := st.chat_input("Ask me anything about your academics…", key="ai_chat_input"):
        st.session_state.ai_messages.append({"role": "user", "content": prompt})
        st.session_state.ai_pending = True
        st.rerun()

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # Close button
    st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
    if st.button("✕  Close AI Panel", key="close_ai_btn", use_container_width=True):
        st.session_state.show_ai     = False
        st.session_state.ai_messages = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-top:32px;padding:12px 0;
            border-top:1px solid rgba(255,255,255,0.05);">
    <span style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;
                 color:rgba(100,116,139,0.35);letter-spacing:1px;">
        ASKMNT STUDENT PORTAL  ·  SESSION DATA ONLY  ·  MNIT JAIPUR
    </span>
</div>
""", unsafe_allow_html=True)
