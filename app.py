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
if "show_mini_menu" not in st.session_state:
    st.session_state.show_mini_menu = False
if "dashboard_sidebar_open" not in st.session_state:
    st.session_state.dashboard_sidebar_open = False
if "page_view" not in st.session_state:
    st.session_state.page_view = "dashboard"

is_chat_empty = len(st.session_state.sessions[st.session_state.current_chat]) == 0

# ==========================================
# 3. HELPER FUNCTION (For Local Image in CSS)
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
# 4. CSS (Slide-Push Layout & Animations)
# ==========================================
# Calculate shift logic based on state
shift_amount = "280px" if st.session_state.dashboard_sidebar_open else "0px"
sidebar_left = "0px" if st.session_state.dashboard_sidebar_open else "-300px"

# FIX: Careful escaping of curly braces {{ and }}
dashboard_style = f"""
    <style>
    /* Prevent default scrolling on the main container to avoid weird jumps */
    html, body {{ overflow-x: hidden; }}
    
    [data-testid="stAppViewContainer"] {{
        background: radial-gradient(circle at center, #4B2C85 0%, #1A0B2E 100%) !important;
        transition: margin-left 0.4s ease-in-out !important;
        margin-left: {shift_amount} !important; /* PUSHES SCREEN RIGHT */
    }}
    
    /* CUSTOM PUSH SIDEBAR BACKGROUND */
    .custom-sidebar {{
        position: fixed;
        top: 0;
        left: {sidebar_left}; 
        width: 280px;
        height: 100vh;
        background: rgba(20, 10, 40, 0.95);
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        z-index: 10000;
        transition: left 0.4s ease-in-out;
        padding-top: 80px;
        box-shadow: 5px 0 15px rgba(0,0,0,0.5);
    }}

    .custom-sidebar-title {{ 
        color: white; 
        font-family: 'Inter', sans-serif; 
        font-weight: 800; 
        font-size: 1.5rem; 
        text-align: center; 
        margin-bottom: 20px; 
        border-bottom: 1px solid rgba(255,255,255,0.2); 
        padding-bottom: 10px;
        margin-left: 20px;
        margin-right: 20px;
    }}

    /* SIDEBAR LIGHT GREY TAB "ASKMNIT" */
    button[help="side_btn"] {{
        position: fixed !important;
        top: 140px !important; /* Sits right under the Navigation text */
        left: 20px !important;
        width: 240px !important;
        background: #E5E7EB !important; /* LIGHT GREY COLOR */
        color: #1A0B2E !important; /* Dark Text */
        text-align: left !important;
        padding: 12px 15px !important;
        font-size: 1.2rem !important;
        font-weight: 800 !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
        transition: transform 0.4s ease-in-out, filter 0.2s !important;
        transform: translateX({sidebar_left}) !important; /* Syncs slide with sidebar */
        z-index: 10001 !important;
        display: block !important;
    }}
    button[help="side_btn"]:hover {{
        filter: brightness(0.9) !important;
        cursor: pointer !important;
    }}
    
    /* LIGHT GREY TOP HEADER BAR */
    .top-header-bar {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 70px;
        background-color: rgba(211, 211, 211, 0.15);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        z-index: 9998; /* Below Sidebar */
        display: flex;
        align-items: center;
        padding-left: 80px; 
        transition: transform 0.4s ease-in-out;
        transform: translateX({shift_amount}); 
    }}

    .header-logo {{
        height: 50px; 
        width: 50px;
        background-image: url("data:image/png;base64,{logo_base64}");
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        border-radius: 50%;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }}

    /* TOGGLE BUTTON */
    div.stButton > button[help="dash_sidebar_toggle"] {{
        position: fixed !important;
        top: 10px !important; 
        left: 15px !important; 
        width: 50px !important;
        height: 50px !important;
        border-radius: 50% !important;
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(5px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        color: white !important;
        font-size: 1.5rem !important;
        z-index: 10002 !important; 
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
        transition: all 0.4s ease !important;
        transform: translateX({shift_amount});
    }}
    
    div.stButton > button[help="dash_sidebar_toggle"]:hover {{ background: rgba(255, 255, 255, 0.2) !important; transform: translateX({shift_amount}) scale(1.05) !important; }}

    /* ANIMATED WELCOME TEXT */
    .welcome-text {{
        font-family: 'Inter', sans-serif;
        font-size: 8vw;
        font-weight: 900;
        text-align: center;
        letter-spacing: -2px;
        margin-top: 10vh;
        display: block;
        width: 100%;
        paint-order: stroke fill;
        -webkit-text-stroke: 0.04em rgba(255,255,255,0.5);
        stroke-linecap: round;
        stroke-linejoin: round;
        background: linear-gradient(90deg, #FFFFFF, #D1B3FF, #FFFFFF);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 3s linear infinite, floatText 4s ease-in-out infinite;
    }}

    .dashboard-label {{
        font-family: 'Inter', sans-serif;
        font-size: 2rem;
        font-weight: 400;
        color: #D1B3FF;
        text-align: left;
        margin-left: 5%;
        margin-top: 20px;
        margin-bottom: 30px;
        opacity: 0.8;
        letter-spacing: 1px;
        text-transform: uppercase;
    }}

    @keyframes shine {{ to {{ background-position: 200% center; }} }}
    @keyframes floatText {{ 0%, 100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-10px); }} }}
    @keyframes floatingButton {{ 0% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-15px); }} 100% {{ transform: translateY(0px); }} }}

    .tab-container {{ margin-left: 5%; margin-right: 5%; }}

    /* MASSIVE TABS */
    div.stButton > button[help="dash_tab_btn"] {{
        width: 100% !important;
        height: 200px !important; 
        font-size: 1.8rem !important; 
        font-weight: 800 !important;
        border-radius: 40px !important; 
        background: linear-gradient(145deg, #E0D4FF 0%, #C8B6FF 100%) !important;
        border: 2px solid rgba(255, 255, 255, 0.5) !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.4) !important;
        color: #1A0B2E !important; 
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: 0.4s all ease !important;
        animation: floatingButton 4s ease-in-out infinite;
    }}

    div.stButton > button[help="dash_tab_btn"]:hover {{
        transform: scale(1.05) !important;
        filter: brightness(1.1);
        box-shadow: 0 30px 60px rgba(200, 182, 255, 0.3) !important;
        animation-play-state: paused;
    }}

    /* Hide default Streamlit sidebar everywhere now, we use custom */
    section[data-testid="stSidebar"] {{ display: none !important; }}
    div[data-testid="stSidebarNav"] {{ display: none !important; }}
    header {{ display: none !important; }}
    </style>
"""

# Simplified Chatbot Style 
chatbot_style = """
    <style>
    [data-testid="stAppViewContainer"] { background-color: #FFFFFF !important; }
    /* Show default sidebar only in chatbot view */
    section[data-testid="stSidebar"] { background-color: #F0F2F6 !important; border-right: 1px solid #DDDDDD !important; display: block !important; }
    .stButton>button { background: linear-gradient(135deg, #8A63FF 0%, #6A3DE8 100%) !important; color: white !important; border-radius: 10px !important;}
    .signature-box-3d { margin-top: 40px; padding: 18px; border-radius: 12px; background: #2C2C2C; border-bottom: 4px solid #1A1A1A; box-shadow: 0 10px 20px rgba(0,0,0,0.2); text-align: center; }
    header { display: none !important; }
    </style>
"""

# Apply styles based on view
if st.session_state.page_view == "dashboard":
    st.markdown(dashboard_style, unsafe_allow_html=True)
else:
    st.markdown(chatbot_style, unsafe_allow_html=True)

# ==========================================
# 5. CHATBOT NATIVE SIDEBAR (Only in Chatbot View)
# ==========================================
if st.session_state.page_view == "chatbot":
    with st.sidebar:
        if st.button("⬅️ Back to Dashboard", use_container_width=True):
            st.session_state.page_view = "dashboard"
            st.rerun()

        st.markdown("<h2 style='color: #1A1A1A; text-align: center;'>Tool Section</h2>", unsafe_allow_html=True)
        if st.button("New Chat"):
            st.session_state.sessions[f"New Session {len(st.session_state.sessions)+1}"] = []
            st.rerun()
        st.button("Chat History 🕑")
        st.button("University Tools ⚙️")
        st.button("Academics 📚")
        st.button("Admission - Fee 💸")
        st.markdown(f"""<div class="signature-box-3d"><p style="color:#A0A0A0; font-size:0.8rem; margin:0;">Designed by</p><h3 style="color:#FFFFFF; margin:5px 0 0 0;">SUMIT CHAUDHARY</h3></div>""", unsafe_allow_html=True)

# ==========================================
# 6. MAIN CONTENT ROUTING
# ==========================================
if st.session_state.page_view == "dashboard":
    
    # --- RENDER PROPER CUSTOM HTML SIDEBAR FOR DASHBOARD ---
    # Toggle Button
    toggle_icon = "✖" if st.session_state.dashboard_sidebar_open else "☰"
    if st.button(toggle_icon, help="dash_sidebar_toggle", key="dash_toggle"):
        st.session_state.dashboard_sidebar_open = not st.session_state.dashboard_sidebar_open
        st.rerun()

    # Sidebar Background & Title
    st.markdown('<div class="custom-sidebar"><div class="custom-sidebar-title">Navigation</div></div>', unsafe_allow_html=True)
    
    # The New "ASKMNIT 🤖" Light Grey Sidebar Tab
    if st.button("ASKMNIT 🤖", help="side_btn", key="dash_side_askmnit"):
        st.session_state.page_view = "chatbot"
        st.session_state.dashboard_sidebar_open = False
        st.rerun()

    # --- MAIN DASHBOARD CONTENT ---
    # Header Bar
    st.markdown(f'''
        <div class="top-header-bar">
            <div class="header-logo"></div>
        </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('<div class="welcome-text">welcome</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-label">your personal dashboard</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1]) 
    
    with col1:
        if st.button("ASKMNIT - YOUR PERSONAL AI ASSISTANT", help="dash_tab_btn", key="dash_ask"):
            st.session_state.page_view = "chatbot"
            st.rerun()
            
    with col2:
        if st.button("ERP LOGIN", help="dash_tab_btn", key="dash_erp"):
            st.toast("ERP Login coming soon!")
            
    st.markdown('</div>', unsafe_allow_html=True)

# --- VIEW: CHATBOT ---
else:
    st.markdown(f"""<div style="margin-top: 10vh; text-align: center;"><div style="color: #1A1A1A; font-weight: 800; font-size: 3.5rem;">AskMNIT</div><div style="color: #666666; font-size: 1.2rem;">Your Professional AI Assistant</div></div>""", unsafe_allow_html=True)

    for message in st.session_state.sessions[st.session_state.current_chat]:
        with st.chat_message(message["role"], avatar="👤" if message["role"]=="user" else "🤖"):
            st.markdown(
