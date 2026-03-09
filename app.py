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
# 4. CSS (Header, Sidebar, Layout & Animations)
# ==========================================
dashboard_style = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background: radial-gradient(circle at center, #4B2C85 0%, #1A0B2E 100%) !important;
    }}
    
    /* LIGHT GREY TOP HEADER BAR */
    .top-header-bar {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 70px;
        background-color: rgba(211, 211, 211, 0.15);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        z-index: 9999;
        display: flex;
        align-items: center;
        padding-left: 40px;
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

    /* CUSTOM DASHBOARD SIDEBAR TOGGLE BUTTON (Circular) */
    div.stButton > button[help="dash_sidebar_toggle"] {{
        position: fixed !important;
        top: 90px !important; /* Just below the header */
        left: 20px !important;
        width: 50px !important;
        height: 50px !important;
        border-radius: 50% !important;
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(5px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        color: white !important;
        font-size: 1.5rem !important;
        z-index: 10000 !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
        transition: all 0.3s ease !important;
    }}
    
    div.stButton > button[help="dash_sidebar_toggle"]:hover {{
        background: rgba(255, 255, 255, 0.2) !important;
        transform: scale(1.1) !important;
    }}

    /* CUSTOM DASHBOARD SIDEBAR MENU */
    .dashboard-sidebar-menu {{
        position: fixed;
        top: 150px; /* Below the toggle button */
        left: 20px;
        background: rgba(30, 15, 55, 0.9);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 20px;
        width: 250px;
        z-index: 9998;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}
    
    /* Styling buttons inside the custom dashboard sidebar */
    .dashboard-sidebar-menu button {{
        width: 100% !important;
        background: transparent !important;
        border: none !important;
        color: white !important;
        text-align: left !important;
        padding: 10px 15px !important;
        font-size: 1.1rem !important;
        border-radius: 8px !important;
        margin-bottom: 5px !important;
        transition: background 0.2s !important;
    }}
    .dashboard-sidebar-menu button:hover {{
        background: rgba(255, 255, 255, 0.1) !important;
    }}

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
    @keyframes floatText {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-10px); }}
    }}
    @keyframes floatingButton {{
        0% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-15px); }}
        100% {{ transform: translateY(0px); }}
    }}

    .tab-container {{ margin-left: 5%; margin-right: 5%; }}

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

    /* Hide default Streamlit sidebar in dashboard view */
    section[data-testid="stSidebar"] {{ display: none !important; }}
    div[data-testid="stSidebarNav"] {{ display: none !important; }}
    header {{ display: none !important; }}
    </style>
"""

chatbot_style = """
    <style>
    [data-testid="stAppViewContainer"] { background-color: #FFFFFF !important; }
    /* Show default sidebar only in chatbot view */
    section[data-testid="stSidebar"] { background-color: #F0F2F6 !important; border-right: 1px solid #DDDDDD !important; display: block !important; }
    .stButton>button { background: linear-gradient(135deg, #8A63FF 0%, #6A3DE8 100%) !important; color: white !important; border-radius: 10px !important;}
    .mini-menu-list { background-color: white; border: 1px solid #DDD; border-radius: 8px; padding: 10px; position: absolute; left: 40px; top: 0px; z-index: 999; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 150px; }
    .signature-box-3d { margin-top: 40px; padding: 18px; border-radius: 12px; background: #2C2C2C; border-bottom: 4px solid #1A1A1A; box-shadow: 0 10px 20px rgba(0,0,0,0.2); text-align: center; }
    </style>
"""

if st.session_state.page_view == "dashboard":
    st.markdown(dashboard_style, unsafe_allow_html=True)
else:
    st.markdown(chatbot_style, unsafe_allow_html=True)

# ==========================================
# 5. DEFAULT SIDEBAR LOGIC (Only in Chatbot View)
# ==========================================
if st.session_state.page_view != "dashboard":
    with st.sidebar:
        if st.button("☰", key="hamburger_icon"):
            st.session_state.show_mini_menu = not st.session_state.show_mini_menu
            st.rerun()
        
        if st.session_state.show_mini_menu:
            st.markdown('<div class="mini-menu-list">', unsafe_allow_html=True)
            if st.button("📊 Dashboard", use_container_width=True, key="dash_link_chat"):
                st.session_state.page_view = "dashboard"
                st.session_state.show_mini_menu = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<h2 style='color: #1A1A1A; text-align: center;'>Tool Section</h2>", unsafe_allow_html=True)
        if st.button("New Chat", key="new_chat_btn_chat"):
            st.session_state.sessions[f"New Session {len(st.session_state.sessions)+1}"] = []
            st.rerun()
        st.button("Chat History 🕑", key="hist_chat")
        st.button("University Tools ⚙️", key="uni_chat")
        st.button("Academics 📚", key="acad_chat")
        st.button("Admission - Fee 💸", key="fee_chat")
        st.markdown(f"""<div class="signature-box-3d"><p style="color:#A0A0A0; font-size:0.8rem; margin:0;">Designed by</p><h3 style="color:#FFFFFF; margin:5px 0 0 0;">SUMIT CHAUDHARY</h3></div>""", unsafe_allow_html=True)

# ==========================================
# 6. MAIN CONTENT ROUTING
# ==========================================
if st.session_state.page_view == "dashboard":
    # Header Bar
    st.markdown('''
        <div class="top-header-bar">
            <div class="header-logo"></div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Dashboard Custom Sidebar Toggle (Circular Button)
    toggle_icon = "✖" if st.session_state.dashboard_sidebar_open else "☰"
    if st.button(toggle_icon, help="dash_sidebar_toggle", key="dash_toggle"):
        st.session_state.dashboard_sidebar_open = not st.session_state.dashboard_sidebar_open
        st.rerun()

    # Dashboard Custom Sidebar Menu
    if st.session_state.dashboard_sidebar_open:
        st.markdown('<div class="dashboard-sidebar-menu">', unsafe_allow_html=True)
        st.markdown("<h3 style='color: white; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 5px;'>Menu</h3>", unsafe_allow_html=True)
        if st.button("💬 Chatbot View", key="go_to_chat"):
            st.session_state.page_view = "chatbot"
            st.session_state.dashboard_sidebar_open = False
            st.rerun()
        if st.button("📚 Academics", key="acad_dash"):
            st.toast("Academics opened!")
        if st.button("⚙️ University Tools", key="tools_dash"):
            st.toast("Tools opened!")
        if st.button("💸 Admission - Fee", key="fee_dash"):
            st.toast("Fees opened!")
        st.markdown('</div>', unsafe_allow_html=True)

    
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

else:
    st.markdown(f"""<div style="margin-top: 10vh; text-align: center;"><div style="color: #1A1A1A; font-weight: 800; font-size: 3.5rem;">AskMNIT</div><div style="color: #666666; font-size: 1.2rem;">Your Professional AI Assistant</div></div>""", unsafe_allow_html=True)

    for message in st.session_state.sessions[st.session_state.current_chat]:
        with st.chat_message(message["role"], avatar="👤" if message["role"]=="user" else "🤖"):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me anything..."):
        st.session_state.sessions[st.session_state.current_chat].append({"role": "user", "content": prompt})
        st.session_state.pending_generation = True
        st.rerun()

    if st.session_state.pending_generation:
        user_query = st.session_state.sessions[st.session_state.current_chat][-1]["content"]
        with st.chat_message("assistant", avatar="🤖"):
            try:
                stream = client.chat.completions.create(
                    messages=[{"role": "system", "content": "You are 'AskMNIT', an assistant for MNIT Jaipur students."},{"role": "user", "content": user_query}],
                    model="llama-3.3-70b-versatile", stream=True
                )
                def gen():
                    for chunk in stream:
                        if chunk.choices[0].delta.content: yield chunk.choices[0].delta.content
                response_text = st.write_stream(gen())
                st.session_state.sessions[st.session_state.current_chat].append({"role": "assistant", "content": response_text})
            except Exception as e: st.error(f"Error: {str(e)}")
        st.session_state.pending_generation = False
