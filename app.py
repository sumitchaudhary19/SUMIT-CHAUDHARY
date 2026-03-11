import streamlit as st
from groq import Groq
import base64
import os

# ==========================================
# 1. PAGE CONFIG & SECRETS
# ==========================================
st.set_page_config(page_title="AskMNIT", page_icon="logo.png", layout="wide", initial_sidebar_state="collapsed")

if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("🚨 System Error: GROQ_API_KEY is missing!")
    st.stop()

# ==========================================
# 2. SESSION STATE SETUP
# ==========================================
if "sessions" not in st.session_state:
    st.session_state.sessions = {"New Session 1": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "New Session 1"
if "pending_generation" not in st.session_state:
    st.session_state.pending_generation = False
if "page_view" not in st.session_state:
    st.session_state.page_view = "dashboard"
if "active_nav" not in st.session_state:
    st.session_state.active_nav = "dashboard"

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

local_logo_path = "mnit_logo.png"
logo_base64 = get_base64_of_bin_file(local_logo_path)

# ==========================================
# 4. CSS STYLES
# ==========================================
sidebar_width = "270px"

dashboard_style = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

    *, *::before, *::after {{ box-sizing: border-box; }}
    html, body {{ overflow-x: hidden; margin: 0; padding: 0; }}

    [data-testid="stAppViewContainer"] {{
        background: #0E0B1A !important;
        margin-left: {sidebar_width} !important;
        width: calc(100% - {sidebar_width}) !important;
        font-family: 'DM Sans', sans-serif;
    }}

    /* ---- DRAWN SIDEBAR ---- */
    .drawn-sidebar {{
        position: fixed;
        top: 0; left: 0;
        width: {sidebar_width};
        height: 100vh;
        background: linear-gradient(180deg, #110D22 0%, #0A0714 100%);
        border-right: 1px solid rgba(138, 99, 255, 0.15);
        z-index: 10000;
        display: flex;
        flex-direction: column;
        padding: 0;
        box-shadow: 4px 0 24px rgba(0,0,0,0.5);
        overflow-y: auto;
        overflow-x: hidden;
    }}

    /* Logo area */
    .sidebar-logo-area {{
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 24px 20px 20px 20px;
        border-bottom: 1px solid rgba(255,255,255,0.07);
        margin-bottom: 8px;
    }}
    .sidebar-logo-img {{
        width: 44px; height: 44px;
        border-radius: 50%;
        background-image: url("data:image/png;base64,{logo_base64}");
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        background-color: rgba(138,99,255,0.15);
        flex-shrink: 0;
    }}
    .sidebar-brand {{
        font-family: 'Syne', sans-serif;
        font-weight: 800;
        font-size: 1.3rem;
        color: #FFFFFF;
        letter-spacing: 0.5px;
        line-height: 1.1;
    }}
    .sidebar-brand span {{
        display: block;
        font-size: 0.65rem;
        font-weight: 400;
        color: rgba(255,255,255,0.45);
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-top: 2px;
    }}

    /* Section label */
    .nav-section-label {{
        font-family: 'DM Sans', sans-serif;
        font-size: 0.62rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: rgba(255,255,255,0.3);
        padding: 14px 22px 6px 22px;
    }}

    /* Nav Items */
    .nav-item {{
        display: flex;
        align-items: center;
        gap: 13px;
        padding: 10px 20px;
        margin: 2px 10px;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
    }}
    .nav-item:hover {{
        background: rgba(138, 99, 255, 0.12);
    }}
    .nav-item.active {{
        background: linear-gradient(135deg, rgba(138,99,255,0.25) 0%, rgba(106,61,232,0.2) 100%);
        border: 1px solid rgba(138,99,255,0.3);
    }}
    .nav-icon {{
        font-size: 1.15rem;
        width: 22px;
        text-align: center;
        flex-shrink: 0;
    }}
    .nav-label {{
        font-family: 'DM Sans', sans-serif;
        font-size: 0.88rem;
        font-weight: 500;
        color: rgba(255,255,255,0.75);
    }}
    .nav-item.active .nav-label {{
        color: #FFFFFF;
        font-weight: 600;
    }}
    .nav-badge {{
        margin-left: auto;
        background: #8A63FF;
        color: white;
        font-size: 0.62rem;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 20px;
    }}
    .nav-badge.green {{
        background: #22C55E;
    }}
    .nav-badge.orange {{
        background: #F97316;
    }}

    /* Divider */
    .sidebar-divider {{
        height: 1px;
        background: rgba(255,255,255,0.06);
        margin: 10px 20px;
    }}

    /* Profile Card at Bottom */
    .sidebar-profile {{
        margin-top: auto;
        padding: 16px 18px;
        border-top: 1px solid rgba(255,255,255,0.07);
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .profile-avatar {{
        width: 38px; height: 38px;
        border-radius: 50%;
        background: linear-gradient(135deg, #8A63FF, #6A3DE8);
        display: flex; align-items: center; justify-content: center;
        font-size: 0.9rem;
        color: white; font-weight: 700;
        flex-shrink: 0;
    }}
    .profile-info {{
        flex: 1;
    }}
    .profile-name {{
        font-family: 'Syne', sans-serif;
        font-size: 0.82rem;
        font-weight: 700;
        color: #FFFFFF;
        line-height: 1.2;
    }}
    .profile-role {{
        font-size: 0.7rem;
        color: rgba(255,255,255,0.4);
    }}
    .logout-btn {{
        font-size: 1rem;
        color: rgba(255,255,255,0.3);
        cursor: pointer;
        transition: color 0.2s;
    }}
    .logout-btn:hover {{ color: #FF6B6B; }}

    /* ---- TOP HEADER ---- */
    .top-header-bar {{
        position: fixed;
        top: 0;
        left: {sidebar_width};
        width: calc(100vw - {sidebar_width});
        height: 64px;
        background: rgba(14, 11, 26, 0.85);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(138,99,255,0.1);
        z-index: 9998;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 32px;
    }}
    .header-title {{
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        font-size: 1.05rem;
        color: #FFFFFF;
    }}
    .header-right {{
        display: flex;
        align-items: center;
        gap: 18px;
    }}
    .header-notif {{
        position: relative;
        cursor: pointer;
    }}
    .header-notif .bell {{ font-size: 1.2rem; }}
    .notif-dot {{
        position: absolute;
        top: -2px; right: -2px;
        width: 8px; height: 8px;
        background: #FF6B6B;
        border-radius: 50%;
        border: 2px solid #0E0B1A;
    }}
    .header-profile-img {{
        width: 36px; height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, #8A63FF, #6A3DE8);
        display: flex; align-items: center; justify-content: center;
        font-size: 0.85rem; color: white; font-weight: 700;
        cursor: pointer;
    }}

    /* ---- MAIN CONTENT AREA ---- */
    .main-content {{
        padding: 88px 32px 40px 32px;
    }}
    .welcome-banner {{
        background: linear-gradient(135deg, rgba(138,99,255,0.18) 0%, rgba(106,61,232,0.08) 100%);
        border: 1px solid rgba(138,99,255,0.2);
        border-radius: 20px;
        padding: 28px 32px;
        margin-bottom: 28px;
        position: relative;
        overflow: hidden;
    }}
    .welcome-banner::before {{
        content: '';
        position: absolute;
        top: -40px; right: -40px;
        width: 180px; height: 180px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(138,99,255,0.12) 0%, transparent 70%);
    }}
    .welcome-banner h1 {{
        font-family: 'Syne', sans-serif;
        font-size: 1.7rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0 0 6px 0;
    }}
    .welcome-banner p {{
        font-size: 0.9rem;
        color: rgba(255,255,255,0.55);
        margin: 0;
    }}

    /* Stats Cards */
    .stats-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 28px;
    }}
    .stat-card {{
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 20px 18px;
        transition: all 0.25s ease;
    }}
    .stat-card:hover {{
        background: rgba(138,99,255,0.1);
        border-color: rgba(138,99,255,0.25);
        transform: translateY(-2px);
    }}
    .stat-icon {{
        font-size: 1.5rem;
        margin-bottom: 10px;
    }}
    .stat-value {{
        font-family: 'Syne', sans-serif;
        font-size: 1.6rem;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1;
        margin-bottom: 4px;
    }}
    .stat-label {{
        font-size: 0.75rem;
        color: rgba(255,255,255,0.45);
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }}
    .stat-pill {{
        display: inline-block;
        margin-top: 8px;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.68rem;
        font-weight: 600;
    }}
    .pill-green {{ background: rgba(34,197,94,0.15); color: #22C55E; }}
    .pill-orange {{ background: rgba(249,115,22,0.15); color: #F97316; }}
    .pill-purple {{ background: rgba(138,99,255,0.2); color: #A78BFA; }}
    .pill-red {{ background: rgba(239,68,68,0.15); color: #EF4444; }}

    /* Content Grid */
    .content-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-bottom: 28px;
    }}
    .content-card {{
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 22px;
    }}
    .content-card h3 {{
        font-family: 'Syne', sans-serif;
        font-size: 0.92rem;
        font-weight: 700;
        color: rgba(255,255,255,0.9);
        margin: 0 0 16px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    /* Schedule items */
    .schedule-item {{
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 12px 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }}
    .schedule-item:last-child {{ border-bottom: none; }}
    .schedule-time {{
        font-family: 'Syne', sans-serif;
        font-size: 0.78rem;
        font-weight: 700;
        color: #8A63FF;
        min-width: 72px;
    }}
    .schedule-details {{
        flex: 1;
    }}
    .schedule-subject {{
        font-size: 0.85rem;
        font-weight: 600;
        color: rgba(255,255,255,0.85);
        margin-bottom: 2px;
    }}
    .schedule-room {{
        font-size: 0.72rem;
        color: rgba(255,255,255,0.38);
    }}
    .schedule-dot {{
        width: 8px; height: 8px;
        border-radius: 50%;
        flex-shrink: 0;
    }}

    /* Notice items */
    .notice-item {{
        display: flex;
        gap: 12px;
        padding: 10px 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }}
    .notice-item:last-child {{ border-bottom: none; }}
    .notice-icon {{ font-size: 1rem; flex-shrink: 0; margin-top: 1px; }}
    .notice-text {{
        font-size: 0.82rem;
        color: rgba(255,255,255,0.7);
        line-height: 1.5;
    }}
    .notice-date {{
        font-size: 0.68rem;
        color: rgba(255,255,255,0.3);
        margin-top: 2px;
    }}

    /* Quick Links row */
    .quick-links-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 14px;
        margin-bottom: 28px;
    }}
    .quick-link-card {{
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 18px;
        display: flex;
        align-items: center;
        gap: 14px;
        cursor: pointer;
        transition: all 0.2s ease;
    }}
    .quick-link-card:hover {{
        background: rgba(138,99,255,0.12);
        border-color: rgba(138,99,255,0.3);
        transform: translateY(-2px);
    }}
    .ql-icon-wrap {{
        width: 42px; height: 42px;
        border-radius: 11px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.2rem;
        flex-shrink: 0;
    }}
    .ql-title {{
        font-family: 'Syne', sans-serif;
        font-size: 0.82rem;
        font-weight: 700;
        color: rgba(255,255,255,0.9);
        margin-bottom: 2px;
    }}
    .ql-sub {{
        font-size: 0.7rem;
        color: rgba(255,255,255,0.38);
    }}

    /* AskMNIT Floating Button */
    .ask-fab {{
        position: fixed;
        bottom: 32px;
        right: 36px;
        z-index: 9999;
        background: linear-gradient(135deg, #8A63FF 0%, #6A3DE8 100%);
        border: none;
        border-radius: 56px;
        padding: 14px 22px;
        display: flex;
        align-items: center;
        gap: 10px;
        cursor: pointer;
        box-shadow: 0 8px 32px rgba(138,99,255,0.45);
        transition: all 0.25s ease;
        color: white;
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        font-size: 0.9rem;
        letter-spacing: 0.3px;
    }}
    .ask-fab:hover {{
        transform: translateY(-3px);
        box-shadow: 0 14px 40px rgba(138,99,255,0.6);
    }}
    .fab-icon {{ font-size: 1.15rem; }}

    /* Scrollbar */
    .drawn-sidebar::-webkit-scrollbar {{ width: 4px; }}
    .drawn-sidebar::-webkit-scrollbar-track {{ background: transparent; }}
    .drawn-sidebar::-webkit-scrollbar-thumb {{ background: rgba(138,99,255,0.3); border-radius: 4px; }}

    /* Hide Streamlit elements */
    section[data-testid="stSidebar"] {{ display: none !important; }}
    header {{ display: none !important; }}
    footer {{ display: none !important; }}
    [data-testid="stMainBlockContainer"] {{ padding: 0 !important; }}
    [data-testid="stVerticalBlock"] > div:first-child {{ padding: 0 !important; }}
    </style>
"""

chatbot_style = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');
    [data-testid="stAppViewContainer"] { background-color: #F7F5FF !important; font-family: 'DM Sans', sans-serif; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #110D22, #0A0714) !important; border-right: 1px solid rgba(138,99,255,0.2) !important; display: block !important; }
    .stButton>button { background: linear-gradient(135deg, #8A63FF 0%, #6A3DE8 100%) !important; color: white !important; border-radius: 10px !important; font-family: 'Syne', sans-serif !important; font-weight: 600 !important; border: none !important; }
    .signature-box { margin-top: 30px; padding: 16px; border-radius: 12px; background: linear-gradient(135deg, rgba(138,99,255,0.2), rgba(106,61,232,0.1)); border: 1px solid rgba(138,99,255,0.3); text-align: center; }
    </style>
"""

if st.session_state.page_view == "dashboard":
    st.markdown(dashboard_style, unsafe_allow_html=True)
else:
    st.markdown(chatbot_style, unsafe_allow_html=True)

# ==========================================
# 5. MAIN CONTENT ROUTING
# ==========================================
if st.session_state.page_view == "dashboard":

    # ---- DRAW SIDEBAR ----
    st.markdown(f'''
        <div class="drawn-sidebar">

            <!-- Logo / Brand -->
            <div class="sidebar-logo-area">
                <div class="sidebar-logo-img"></div>
                <div class="sidebar-brand">
                    AskMNIT
                    <span>MNIT Jaipur Portal</span>
                </div>
            </div>

            <!-- MAIN NAVIGATION -->
            <div class="nav-section-label">Main Menu</div>

            <a class="nav-item active">
                <span class="nav-icon">🏠</span>
                <span class="nav-label">Dashboard</span>
            </a>

            <a class="nav-item">
                <span class="nav-icon">📅</span>
                <span class="nav-label">Schedule</span>
                <span class="nav-badge green">Today</span>
            </a>

            <a class="nav-item">
                <span class="nav-icon">📚</span>
                <span class="nav-label">Academics</span>
            </a>

            <a class="nav-item">
                <span class="nav-icon">💰</span>
                <span class="nav-label">Fee Portal</span>
                <span class="nav-badge orange">Due</span>
            </a>

            <a class="nav-item">
                <span class="nav-icon">🏢</span>
                <span class="nav-label">Hostel</span>
            </a>

            <div class="sidebar-divider"></div>

            <!-- RESOURCES -->
            <div class="nav-section-label">Resources</div>

            <a class="nav-item">
                <span class="nav-icon">📄</span>
                <span class="nav-label">Syllabus & Notes</span>
            </a>

            <a class="nav-item">
                <span class="nav-icon">📝</span>
                <span class="nav-label">Previous Year Qs</span>
            </a>

            <a class="nav-item">
                <span class="nav-icon">🏛️</span>
                <span class="nav-label">Library Catalog</span>
            </a>

            <a class="nav-item">
                <span class="nav-icon">📌</span>
                <span class="nav-label">Latest Notices</span>
                <span class="nav-badge">3</span>
            </a>

            <div class="sidebar-divider"></div>

            <!-- ACCOUNT -->
            <div class="nav-section-label">Account</div>

            <a class="nav-item">
                <span class="nav-icon">⚙️</span>
                <span class="nav-label">Settings</span>
            </a>

            <a class="nav-item">
                <span class="nav-icon">🚪</span>
                <span class="nav-label">Logout</span>
            </a>

            <!-- Profile Card -->
            <div class="sidebar-profile">
                <div class="profile-avatar">SC</div>
                <div class="profile-info">
                    <div class="profile-name">Sumit Chaudhary</div>
                    <div class="profile-role">B.Tech Metallurgy · 3rd Yr</div>
                </div>
                <div class="logout-btn">⇥</div>
            </div>

        </div>
    ''', unsafe_allow_html=True)

    # ---- DRAW HEADER ----
    st.markdown(f'''
        <div class="top-header-bar">
            <div class="header-title">🎓 MNIT Jaipur — Student Portal</div>
            <div class="header-right">
                <div class="header-notif">
                    <span class="bell">🔔</span>
                    <div class="notif-dot"></div>
                </div>
                <div class="header-profile-img">SC</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    # ---- MAIN DASHBOARD BODY ----
    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # Welcome Banner
    st.markdown('''
        <div class="welcome-banner">
            <h1>Welcome back, Sumit! 👋</h1>
            <p>Here is your campus at a glance. Have a productive day ahead.</p>
        </div>
    ''', unsafe_allow_html=True)

    # Quick Stats (4 cards)
    st.markdown('''
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">📊</div>
                <div class="stat-value">78%</div>
                <div class="stat-label">Attendance</div>
                <div class="stat-pill pill-green">● Above Limit</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">⏳</div>
                <div class="stat-value">20 min</div>
                <div class="stat-label">Next Class</div>
                <div class="stat-pill pill-orange">● Coming Soon</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📝</div>
                <div class="stat-value">6/8</div>
                <div class="stat-label">Assignments Done</div>
                <div class="stat-pill pill-purple">● 2 Pending</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">💰</div>
                <div class="stat-value">₹18,500</div>
                <div class="stat-label">Fee Due</div>
                <div class="stat-pill pill-red">● Due in 5 days</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    # Schedule + Notices
    st.markdown('''
        <div class="content-grid">

            <!-- Today's Schedule -->
            <div class="content-card">
                <h3>📅 Today's Schedule</h3>
                <div class="schedule-item">
                    <div class="schedule-dot" style="background:#8A63FF;"></div>
                    <div class="schedule-time">09:30 AM</div>
                    <div class="schedule-details">
                        <div class="schedule-subject">Mineral Processing</div>
                        <div class="schedule-room">Room 302 · Prof. R.K. Sharma</div>
                    </div>
                </div>
                <div class="schedule-item">
                    <div class="schedule-dot" style="background:#22C55E;"></div>
                    <div class="schedule-time">11:30 AM</div>
                    <div class="schedule-details">
                        <div class="schedule-subject">Engineering Materials</div>
                        <div class="schedule-room">Metallurgy Lab 1 · Dr. Mehta</div>
                    </div>
                </div>
                <div class="schedule-item">
                    <div class="schedule-dot" style="background:#F97316;"></div>
                    <div class="schedule-time">02:00 PM</div>
                    <div class="schedule-details">
                        <div class="schedule-subject">Thermodynamics</div>
                        <div class="schedule-room">Room 201 · Prof. Agarwal</div>
                    </div>
                </div>
                <div class="schedule-item">
                    <div class="schedule-dot" style="background:#38BDF8;"></div>
                    <div class="schedule-time">04:00 PM</div>
                    <div class="schedule-details">
                        <div class="schedule-subject">Phase Transformations</div>
                        <div class="schedule-room">LT-3 · Prof. Singh</div>
                    </div>
                </div>
            </div>

            <!-- Latest Notices -->
            <div class="content-card">
                <h3>📌 Latest Notices</h3>
                <div class="notice-item">
                    <div class="notice-icon">🗓️</div>
                    <div>
                        <div class="notice-text">Mid-Semester exam dates have been announced. Check academic portal for full schedule.</div>
                        <div class="notice-date">Today · Academic Section</div>
                    </div>
                </div>
                <div class="notice-item">
                    <div class="notice-icon">🎉</div>
                    <div>
                        <div class="notice-text">Tech Fest 2025 registrations are now open. Last date: 20th March.</div>
                        <div class="notice-date">Yesterday · Student Activities</div>
                    </div>
                </div>
                <div class="notice-item">
                    <div class="notice-icon">📋</div>
                    <div>
                        <div class="notice-text">Submit Bonafide Certificate requests online via the Student Portal before 5 PM.</div>
                        <div class="notice-date">2 days ago · Admin Office</div>
                    </div>
                </div>
                <div class="notice-item">
                    <div class="notice-icon">🏠</div>
                    <div>
                        <div class="notice-text">Hostel mess menu revised. New timings effective from 15th March.</div>
                        <div class="notice-date">3 days ago · Hostel Office</div>
                    </div>
                </div>
            </div>

        </div>
    ''', unsafe_allow_html=True)

    # Quick Access Cards
    st.markdown('''
        <div class="nav-section-label" style="color:rgba(255,255,255,0.35); font-size:0.7rem; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:14px;">Quick Access</div>
        <div class="quick-links-grid">
            <div class="quick-link-card">
                <div class="ql-icon-wrap" style="background:rgba(138,99,255,0.15);">📄</div>
                <div>
                    <div class="ql-title">Syllabus & Notes</div>
                    <div class="ql-sub">Download subject materials</div>
                </div>
            </div>
            <div class="quick-link-card">
                <div class="ql-icon-wrap" style="background:rgba(34,197,94,0.12);">📝</div>
                <div>
                    <div class="ql-title">Previous Year Qs</div>
                    <div class="ql-sub">Exam prep question bank</div>
                </div>
            </div>
            <div class="quick-link-card">
                <div class="ql-icon-wrap" style="background:rgba(249,115,22,0.12);">🏛️</div>
                <div>
                    <div class="ql-title">Library Catalog</div>
                    <div class="ql-sub">Search & reserve books</div>
                </div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close main-content

    # ---- AskMNIT Floating Button ----
    col1, col2, col3 = st.columns([8, 2, 1])
    with col3:
        if st.button("🤖 AskMNIT AI", key="fab_btn", help="Open AI Assistant"):
            st.session_state.page_view = "chatbot"
            st.rerun()

    # CSS to style FAB button
    st.markdown("""
        <style>
        div[data-testid="stHorizontalBlock"] {
            position: fixed;
            bottom: 32px;
            right: 36px;
            z-index: 9999;
            width: auto !important;
        }
        div[data-testid="stHorizontalBlock"] > div:last-child button {
            background: linear-gradient(135deg, #8A63FF 0%, #6A3DE8 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 56px !important;
            padding: 14px 22px !important;
            font-family: 'Syne', sans-serif !important;
            font-weight: 700 !important;
            font-size: 0.9rem !important;
            box-shadow: 0 8px 32px rgba(138,99,255,0.5) !important;
            white-space: nowrap !important;
        }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# CHATBOT VIEW
# ==========================================
else:
    with st.sidebar:
        if st.button("⬅️ Back to Dashboard", use_container_width=True):
            st.session_state.page_view = "dashboard"
            st.rerun()

        st.markdown("<hr style='border-color:rgba(138,99,255,0.3);'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:white; font-family:Syne,sans-serif; text-align:center;'>🤖 AskMNIT</h3>", unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.button("➕  New Chat", use_container_width=True)

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        st.markdown("<p style='color:rgba(255,255,255,0.35); font-size:0.72rem; letter-spacing:1.5px; text-transform:uppercase; margin:10px 0 6px 4px;'>Navigation</p>", unsafe_allow_html=True)

        st.button("🕑  Chat History", use_container_width=True)
        st.button("⚙️  University Tools", use_container_width=True)
        st.button("📚  Academics", use_container_width=True)
        st.button("💸  Admission & Fee", use_container_width=True)
        st.button("🏢  Hostel Info", use_container_width=True)
        st.button("📅  Schedule", use_container_width=True)
        st.button("📄  Syllabus & Notes", use_container_width=True)
        st.button("📝  Previous Year Qs", use_container_width=True)
        st.button("🏛️  Library Catalog", use_container_width=True)

        st.markdown("<hr style='border-color:rgba(138,99,255,0.3); margin-top:16px;'>", unsafe_allow_html=True)
        st.markdown("""
            <div class="signature-box">
                <p style="color:rgba(255,255,255,0.5); font-size:0.7rem; margin:0 0 4px 0; text-transform:uppercase; letter-spacing:1px;">Logged in as</p>
                <h3 style="color:#FFFFFF; margin:0; font-family:'Syne',sans-serif; font-size:0.95rem;">Sumit Chaudhary</h3>
                <p style="color:rgba(138,99,255,0.8); font-size:0.75rem; margin:4px 0 0 0;">B.Tech Metallurgy · 3rd Year</p>
            </div>
        """, unsafe_allow_html=True)

    # Chat area
    st.markdown("""
        <div style="margin-top: 8vh; text-align: center; padding-bottom: 10px;">
            <div style="color: #1A1A1A; font-family:'Syne',sans-serif; font-weight: 800; font-size: 3rem; line-height:1;">AskMNIT</div>
            <div style="color: #888; font-size: 1.05rem; margin-top: 8px;">Your Intelligent Campus Assistant 🎓</div>
        </div>
    """, unsafe_allow_html=True)

    for message in st.session_state.sessions[st.session_state.current_chat]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me anything about MNIT..."):
        st.session_state.sessions[st.session_state.current_chat].append({"role": "user", "content": prompt})
        st.session_state.pending_generation = True
        st.rerun()

    if st.session_state.pending_generation:
        user_query = st.session_state.sessions[st.session_state.current_chat][-1]["content"]
        with st.chat_message("assistant"):
            try:
                stream = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are 'AskMNIT', a helpful and knowledgeable AI assistant for students of MNIT Jaipur (Malaviya National Institute of Technology). Help students with academic queries, campus information, schedules, fee details, hostel info, and general college life questions. Be concise, friendly, and accurate."},
                        {"role": "user", "content": user_query}
                    ],
                    model="llama-3.3-70b-versatile",
                    stream=True
                )
                def gen():
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content
                response_text = st.write_stream(gen())
                st.session_state.sessions[st.session_state.current_chat].append({"role": "assistant", "content": response_text})
            except Exception as e:
                st.error(f"Error: {str(e)}")
        st.session_state.pending_generation = False
