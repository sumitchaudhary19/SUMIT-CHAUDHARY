import streamlit as st
from groq import Groq
import base64
import os

# ==========================================
# 1. PAGE CONFIG & SECRETS
# ==========================================
st.set_page_config(page_title="AskMNIT", page_icon="logo.png", layout="wide", initial_sidebar_state="expanded")

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
# 4. UNIVERSAL CSS (Header & Fonts)
# ==========================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    
    /* TOP HEADER BAR */
    .top-header-bar {{
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 70px;
        background-color: rgba(211, 211, 211, 0.15);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        z-index: 99999; 
        display: flex; align-items: center; padding-left: 80px; 
    }}
    .header-logo {{
        height: 50px; width: 50px;
        background-image: url("data:image/png;base64,{logo_base64}");
        background-size: contain; background-repeat: no-repeat; background-position: center;
        border-radius: 50%; box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }}
    header {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 5. DASHBOARD SPECIFIC CSS
# ==========================================
if st.session_state.page_view == "dashboard":
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] {
            background: radial-gradient(circle at center, #4B2C85 0%, #1A0B2E 100%) !important;
        }
        
        /* STYLE THE NATIVE STREAMLIT SIDEBAR TO LOOK LIKE CUSTOM DARK PUSH SIDEBAR */
        [data-testid="stSidebar"] {
            background-color: rgba(20, 10, 40, 0.95) !important;
            backdrop-filter: blur(15px) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding-top: 80px !important;
            box-shadow: 5px 0 15px rgba(0,0,0,0.5) !important;
        }
        [data-testid="stSidebarUserContent"] {
            padding-top: 80px !important; 
        }
        
        /* ANIMATED WELCOME TEXT */
        .welcome-text {
            font-size: 8vw; font-weight: 900; text-align: center; letter-spacing: -2px; margin-top: 15vh;
            display: block; width: 100%; paint-order: stroke fill; -webkit-text-stroke: 0.04em rgba(255,255,255,0.5);
            background: linear-gradient(90deg, #FFFFFF, #D1B3FF, #FFFFFF); background-size: 200% auto;
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            animation: shine 3s linear infinite, floatText 4s ease-in-out infinite;
        }
        .dashboard-label {
            font-size: 2rem; font-weight: 400; color: #D1B3FF; text-align: left; margin-left: 5%;
            margin-top: 20px; margin-bottom: 30px; opacity: 0.8; letter-spacing: 1px; text-transform: uppercase;
        }
        @keyframes shine { to { background-position: 200% center; } }
        @keyframes floatText { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-10px); } }
        @keyframes floatingButton { 0% { transform: translateY(0px); } 50% { transform: translateY(-15px); } 100% { transform: translateY(0px); } }

        .tab-container { margin-left: 5%; margin-right: 5%; }
        
        /* MASSIVE TABS */
        div.stButton > button[help="dash_tab_btn"] {
            width: 100% !important; height: 200px !important; font-size: 1.8rem !important; font-weight: 800 !important;
            border-radius: 40px !important; background: linear-gradient(145deg, #E0D4FF 0%, #C8B6FF 100%) !important;
            border: 2px solid rgba(255, 255, 255, 0.5) !important; box-shadow: 0 20px 40px rgba(0,0,0,0.4) !important;
            color: #1A0B2E !important; text-transform: uppercase; letter-spacing: 1px; transition: 0.4s all ease !important;
            animation: floatingButton 4s ease-in-out infinite;
        }
        div.stButton > button[help="dash_tab_btn"]:hover { transform: scale(1.05) !important; filter: brightness(1.1); animation-play-state: paused; }

        /* Custom Sidebar Button Styling */
        div[data-testid="stSidebar"] div.stButton > button {
            background: #E5E7EB !important; color: #1A0B2E !important; font-weight: 800 !important; font-size: 1.1rem !important;
            border-radius: 8px !important; border: none !important; margin-bottom: 10px !important; transition: filter 0.2s !important;
        }
        div[data-testid="stSidebar"] div.stButton > button:hover { filter: brightness(0.9) !important; }
        
        /* Collapse toggle button override */
        button[kind="header"] { color: white !important; background: rgba(255, 255, 255, 0.1) !important; border-radius: 50% !important; margin-top:10px !important; margin-left: 10px !important; }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 6. CHATBOT SPECIFIC CSS
# ==========================================
else:
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] { background-color: #FFFFFF !important; }
        [data-testid="stSidebar"] { background-color: #F0F2F6 !important; border-right: 1px solid #DDDDDD !important; }
        div[data-testid="stSidebar"] div.stButton > button { background: linear-gradient(135deg, #8A63FF 0%, #6A3DE8 100%) !important; color: white !important; border-radius: 10px !important; }
        .signature-box-3d { margin-top: 40px; padding: 18px; border-radius: 12px; background: #2C2C2C; border-bottom: 4px solid #1A1A1A; box-shadow: 0 10px 20px rgba(0,0,0,0.2); text-align: center; }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 7. RENDER NATIVE SIDEBAR (Changes based on View)
# ==========================================
with st.sidebar:
    if st.session_state.page_view == "dashboard":
        st.markdown("<h3 style='color: white; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 10px;'>Navigation</h3>", unsafe_allow_html=True)
        if st.button("ASKMNIT 🤖"):
            st.session_state.page_view = "chatbot"
            st.rerun()
    else:
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
        st.markdown("""<div class="signature-box-3d"><p style="color:#A0A0A0; font-size:0.8rem; margin:0;">Designed by</p><h3 style="color:#FFFFFF; margin:5px 0 0 0;">SUMIT CHAUDHARY</h3></div>""", unsafe_allow_html=True)

# ==========================================
# 8. MAIN CONTENT ROUTING
# ==========================================
# Persistent Header
st.markdown(f'''<div class="top-header-bar"><div class="header-logo"></div></div>''', unsafe_allow_html=True)

if st.session_state.page_view == "dashboard":
    
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
    st.markdown("""<div style="margin-top: 10vh; text-align: center;"><div style="color: #1A1A1A; font-weight: 800; font-size: 3.5rem;">AskMNIT</div><div style="color: #666666; font-size: 1.2rem;">Your Professional AI Assistant</div></div>""", unsafe_allow_html=True)

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
