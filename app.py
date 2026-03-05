import streamlit as st
import urllib.parse
import time
import base64
from groq import Groq

# ==========================================
# 1. PAGE CONFIG & SECRETS VALIDATION
# ==========================================
st.set_page_config(page_title="AskMNIT", page_icon="logo.png", layout="wide", initial_sidebar_state="expanded")

if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("🚨 System Error: GROQ_API_KEY is missing in Streamlit Secrets!")
    st.stop()

# ==========================================
# 2. SESSION STATE SETUP
# ==========================================
if "sessions" not in st.session_state:
    st.session_state.sessions = {"New Session": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "New Session"

is_chat_empty = len(st.session_state.sessions[st.session_state.current_chat]) == 0

# ==========================================
# 3. CSS (Custom UI for Search Bar & Plus Icon)
# ==========================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"], [data-testid="stAppViewContainer"] {{
        font-family: 'Inter', sans-serif;
        background-color: #1A1A1A !important;
        color: #E0E0E0 !important;
    }}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
    [data-testid="stHeader"] {{ background-color: transparent !important; }}

    [data-testid="stChatMessageContainer"] {{
        padding-left: 0 !important; padding-right: 0 !important;
    }}

    div[data-testid="stChatMessage"] {{
        border-radius: 12px; padding: 15px 20px; margin-bottom: 20px;
    }}

    section[data-testid="stSidebar"] {{ background-color: #111111 !important; border-right: 1px solid #333 !important; }}

    .stButton>button {{
        width: 100%; text-align: left; background-color: #D3D3D3 !important;
        border: 1px solid #999 !important; padding: 10px 15px; border-radius: 8px;
        font-weight: 600; color: #000000 !important; transition: 0.2s;
    }}
    
    .signature-box {{ margin-top: 40px; margin-bottom: 20px; padding: 15px; border-radius: 8px; background: #2C2C2C; border: 1px solid #444; text-align: center; }}
    .signature-box p {{ margin: 0; font-size: 0.75rem; color: #AAAAAA; text-transform: uppercase; letter-spacing: 1px; }}
    .signature-box h3 {{ margin: 5px 0 0 0; font-size: 1.1rem; color: #E0E0E0; font-weight: 700; }}

    /* --- Custom Search Bar Wrapper --- */
    .search-wrapper {{
        position: relative;
        width: 650px; /* 2.3x approx of text length */
        margin: 0 auto;
    }}

    .custom-search-bar {{
        width: 100%;
        height: 110px; /* Double lined text height */
        background-color: #2C2C2C;
        border: 1px solid #444;
        border-radius: 15px;
        color: #E0E0E0;
        padding: 15px 15px 45px 15px; /* Bottom padding for icon space */
        font-size: 1.1rem;
        outline: none;
        resize: none;
        font-family: 'Inter', sans-serif;
    }}

    .custom-search-bar:focus {{
        border-color: #60A5FA;
    }}

    /* --- Plus Icon Styling --- */
    .plus-icon-container {{
        position: absolute;
        bottom: 12px;
        left: 18px;
        color: #BBBBBB; /* Light Grey */
        font-size: 24px;
        font-weight: 300;
        cursor: pointer;
        transition: 0.3s;
        pointer-events: none; /* Let clicks pass through to uploader */
        z-index: 5;
    }}

    /* Overlaying uploader to make icon clickable */
    div[data-testid="stFileUploader"] {{
        position: absolute;
        bottom: 5px;
        left: 10px;
        width: 40px;
        height: 40px;
        opacity: 0; /* Hidden but functional */
        z-index: 10;
        cursor: pointer;
    }}

    div[data-testid="stFileUploader"] section {{
        padding: 0 !important;
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. SIDEBAR & BRANDING
# ==========================================
with st.sidebar:
    try:
        with open("logo.png", "rb") as image_file:
            logo_base64 = base64.b64encode(image_file.read()).decode()
        logo_html = f"""
        <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 25px; padding-top: 10px;">
            <img src="data:image/png;base64,{logo_base64}" style="width: 50px; margin-right: 12px;">
            <span style="font-family: 'Inter', sans-serif; font-size: 2.2rem; font-weight: 800; color: #60A5FA; letter-spacing: 1.5px;">AskMNIT</span>
        </div>
        """
        st.markdown(logo_html, unsafe_allow_html=True)
    except FileNotFoundError:
        st.markdown("<h3 style='color: #60A5FA; font-weight: 800; text-align: center;'>AskMNIT</h3>", unsafe_allow_html=True)

    if st.button("➕ New Session"):
        st.session_state.sessions[f"Session {len(st.session_state.sessions) + 1}"] = []
        st.rerun()

    st.link_button("Class Schedule 📅", "https://www.mnit.ac.in/TimeTable/", use_container_width=True)
    st.link_button("ERP 🌐", "https://mniterp.org/mniterp/", use_container_width=True)

    st.markdown(f"""<div class="signature-box"><p>Architected by</p><h3>SUMIT CHAUDHARY</h3></div>""", unsafe_allow_html=True)

# ==========================================
# 5. MAIN CHAT LOGIC (DISPLAY ONLY)
# ==========================================
if is_chat_empty:
    st.markdown("<h1 style='color: #FFFFFF; font-weight: 800; text-align: center; font-size: 3rem; margin-top: 15vh;'>AskMNIT</h1>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; color: #BBBBBB; font-weight: 500; font-size: 1.2rem; margin-bottom: 20px;'>Your Professional AI Assistant</div>", unsafe_allow_html=True)
    
    # Custom UI Search Box with Plus Icon
    st.markdown('<div class="search-wrapper">', unsafe_allow_html=True)
    
    # The Textarea
    st.markdown('<textarea class="custom-search-bar" placeholder="Ask me anything..."></textarea>', unsafe_allow_html=True)
    
    # The Visual Plus Icon
    st.markdown('<div class="plus-icon-container">+</div>', unsafe_allow_html=True)
    
    # Hidden File Uploader Overlay
    uploaded_file = st.file_uploader("", type=["pdf", "txt", "png", "jpg"], key="file_input", label_visibility="collapsed")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Toast or Success message when file is attached
    if uploaded_file:
        st.toast(f"📎 Attached: {uploaded_file.name}")

else:
    for message in st.session_state.sessions[st.session_state.current_chat]:
        avatar_icon = "user.png" if message["role"] == "user" else "logo.png"
        with st.chat_message(message["role"], avatar=avatar_icon):
            st.markdown(message["content"])
