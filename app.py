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

# ==========================================
# 3. HELPER FUNCTION (For Local Image)
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
# 4. CSS (Fixed Sidebar with New Tab)
# ==========================================
sidebar_width = "280px"

dashboard_style = f"""
    <style>
    html, body {{ overflow-x: hidden; }}
    
    /* Main Dashboard Area - Shifted Right */
    [data-testid="stAppViewContainer"] {{
        background: radial-gradient(circle at center, #4B2C85 0%, #1A0B2E 100%) !important;
        margin-left: {sidebar_width} !important;
        width: calc(100% - {sidebar_width}) !important;
    }}
    
    /* PERMANENT FIXED SIDEBAR */
    .custom-sidebar {{
        position: fixed;
        top: 0;
        left: 0;
        width: {sidebar_width};
        height: 100vh;
        background: rgba(20, 10, 40, 0.95);
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        z-index: 9999; 
        padding-top: 30px;
        box-shadow: 5px 0 15px rgba(0,0,0,0.5);
    }}

    .custom-sidebar-title {{ 
        color: white; 
        font-family: 'Inter', sans-serif; 
        font-weight: 800; 
        font-size: 1.6rem; 
        text-align: left; 
        margin-left: 25px;
        margin-right: 25px;
        padding-bottom: 15px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        letter-spacing: 1px;
        margin-bottom: 20px;
    }}

    /* POSITIONING THE BUTTON INSIDE THE SIDEBAR */
    div.stButton > button[help="sidebar_new_tab"] {{
        position: fixed !important;
        top: 100px !important; /* Positioned directly under Navigation header */
        left: 20px !important;
        width: 240px !important;
        background: #E5E7EB !important; /* LIGHT GREY */
        color: #1A0B2E !important; 
        text-align: left !important;
        font-weight: 800 !important;
        border-radius: 10px !important;
        border: none !important;
        z-index: 10000 !important;
        padding: 10px 15px !important;
        transition: 0.2s all ease !important;
    }}
    
    div.stButton > button[help="sidebar_new_tab"]:hover {{
        filter: brightness(0.9) !important;
        transform: scale(1.02) !important;
    }}

    /* HEADER BAR */
    .top-header-bar {{
        position: fixed;
        top: 0;
        left: {sidebar_width};
        width: calc(100vw - {sidebar_width});
        height: 70px;
        background-color: rgba(211, 211, 211, 0.15);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        z-index: 9998; 
        display: flex;
        align-items: center;
        padding-left: 40px; 
    }}

    .header-logo {{
        height: 50px; width: 50px;
        background-image: url("data:image/png;base64,{logo_base64}");
        background-size: contain; background-repeat: no-repeat; background-position: center;
        border-radius: 50%; box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }}

    section[data-testid="stSidebar"] {{ display: none !important; }}
    header {{ display: none !important; }}
    footer {{ display: none !important; }}
    </style>
"""

chatbot_style = """
    <style>
    [data-testid="stAppViewContainer"] { background-color: #FFFFFF !important; }
    section[data-testid="stSidebar"] { background-color: #F0F2F6 !important; border-right: 1px solid #DDDDDD !important; display: block !important; }
    .stButton>button { background: linear-gradient(135deg, #8A63FF 0%, #6A3DE8 100%) !important; color: white !important; border-radius: 10px !important;}
    .signature-box-3d { margin-top: 40px; padding: 18px; border-radius: 12px; background: #2C2C2C; border-bottom: 4px solid #1A1A1A; box-shadow: 0 10px 20px rgba(0,0,0,0.2); text-align: center; }
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
    # Sidebar UI
    st.markdown('''
        <div class="custom-sidebar">
            <div class="custom-sidebar-title">Navigation</div>
        </div>
    ''', unsafe_allow_html=True)
    
    # NEW TAB Button inside sidebar
    if st.button("NEW TAB", help="sidebar_new_tab", key="btn_new_tab"):
        st.toast("New Tab Clicked!")

    # Top Header
    st.markdown(f'''<div class="top-header-bar"><div class="header-logo"></div></div>''', unsafe_allow_html=True)
    
else:
    # CHATBOT VIEW
    with st.sidebar:
        if st.button("⬅️ Back to Dashboard", use_container_width=True):
            st.session_state.page_view = "dashboard"
            st.rerun()
        st.markdown("<h2 style='text-align: center;'>Tool Section</h2>", unsafe_allow_html=True)
        st.button("New Chat")
        st.button("Chat History 🕑")
        st.button("University Tools ⚙️")
        st.button("Academics 📚")
        st.button("Admission - Fee 💸")
        st.markdown("""<div class="signature-box-3d"><h3 style="color:#FFFFFF; margin:5px 0 0 0;">SUMIT CHAUDHARY</h3></div>""", unsafe_allow_html=True)

    st.markdown("""<div style="margin-top: 10vh; text-align: center;"><div style="color: #1A1A1A; font-weight: 800; font-size: 3.5rem;">AskMNIT</div><div style="color: #666666; font-size: 1.2rem;">Your Professional AI Assistant</div></div>""", unsafe_allow_html=True)

    for message in st.session_state.sessions[st.session_state.current_chat]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me anything..."):
        st.session_state.sessions[st.session_state.current_chat].append({"role": "user", "content": prompt})
        st.session_state.pending_generation = True
        st.rerun()

    if st.session_state.pending_generation:
        user_query = st.session_state.sessions[st.session_state.current_chat][-1]["content"]
        with st.chat_message("assistant"):
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
