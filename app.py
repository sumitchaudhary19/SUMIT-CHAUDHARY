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
    st.session_state.sessions = {"New Session 1": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "New Session 1"
if "pending_generation" not in st.session_state:
    st.session_state.pending_generation = False
if "show_acad_menu" not in st.session_state:
    st.session_state.show_acad_menu = False
if "show_mini_menu" not in st.session_state:
    st.session_state.show_mini_menu = False
if "view" not in st.session_state:
    st.session_state.view = "chatbot" # Default view is chatbot

is_chat_empty = len(st.session_state.sessions[st.session_state.current_chat]) == 0

# ==========================================
# 3. CSS (UI Styling & Dashboard Grid)
# ==========================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"], [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        font-family: 'Inter', sans-serif;
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
    }}
    
    [data-testid="stMain"] {{ background-color: #FFFFFF !important; }}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
    [data-testid="stBottom"] {{ background-color: #FFFFFF !important; border-top: none !important; }}

    section[data-testid="stSidebar"] {{
        background-color: #F0F2F6 !important;
        border-right: 1px solid #DDDDDD !important;
        width: 320px !important;
    }}

    /* SHINY VIOLET MAIN TABS */
    .stButton>button, [data-testid="stLinkButton"] > a {{
        width: 100% !important;
        min-width: 250px !important;
        background: linear-gradient(135deg, #8A63FF 0%, #6A3DE8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 14px 20px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(138, 99, 255, 0.3) !important;
        transition: 0.3s all ease !important;
    }}

    /* --- DASHBOARD BIG TABS STYLING --- */
    div.stButton > button[title="dash_tab"] {{
        height: 180px !important;
        font-size: 1.5rem !important;
        border-radius: 20px !important;
        margin-top: 10vh !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 15px 35px rgba(138, 99, 255, 0.4) !important;
    }}

    /* MINI MENU POPUP */
    .mini-menu-list {{
        background-color: white; border: 1px solid #DDD; border-radius: 8px; padding: 10px;
        position: absolute; left: 40px; top: 0px; z-index: 999;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 130px;
    }}
    .mini-menu-item-btn {{
        background: none !important; border: none !important; color: #333 !important;
        text-align: left !important; padding: 5px 0 !important; font-size: 0.95rem !important;
        width: 100% !important; box-shadow: none !important; cursor: pointer !important;
    }}

    /* SEARCH BAR */
    div[data-testid="stChatInput"] > div {{
        background-color: #FFFFFF !important; border: 1px solid #DDDDDD !important;
        border-radius: 40px !important; height: 70px !important;
    }}

    /* SIGNATURE BOX 3D */
    .signature-box-3d {{ margin-top: 40px; padding: 18px; border-radius: 12px; background: #2C2C2C; border-bottom: 4px solid #1A1A1A; box-shadow: 0 10px 20px rgba(0,0,0,0.2); text-align: center; }}
    
    .title-container-empty {{ margin-top: 15vh; transition: 0.5s; }}
    .title-container-active {{ margin-top: 2vh; scale: 0.7; transition: 0.5s; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. SIDEBAR LOGIC
# ==========================================
with st.sidebar:
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("☰", key="hamburger_icon"):
            st.session_state.show_mini_menu = not st.session_state.show_mini_menu
            st.rerun()
    
    if st.session_state.show_mini_menu:
        # We use small buttons inside the white popup for functionality
        with st.container():
            st.markdown('<div class="mini-menu-list">', unsafe_allow_html=True)
            if st.button("📊 Dashboard", key="btn_dash"):
                st.session_state.view = "dashboard"
                st.session_state.show_mini_menu = False
                st.rerun()
            if st.button("⚙️ Settings", key="btn_settings"):
                st.toast("Settings clicked")
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<h2 style='color: #1A1A1A; text-align: center; margin-top: 10px;'>Tool Section</h2>", unsafe_allow_html=True)
    
    if st.button("New Chat"):
        st.session_state.view = "chatbot"
        st.session_state.sessions[f"New Session {len(st.session_state.sessions)+1}"] = []
        st.rerun()

    if st.button("Chat History 🕑"): st.toast("History clicked")
    if st.button("University Tools ⚙️"): st.toast("Tools clicked")
    if st.button("Academics 📚"):
        st.session_state.show_acad_menu = not st.session_state.show_acad_menu
        st.rerun()
    if st.button("Admission - Fee 💸"): st.toast("Fee clicked")
    
    st.markdown(f"""<div class="signature-box-3d"><p style="color:#A0A0A0; font-size:0.8rem; margin:0;">Designed by</p><h3 style="color:#FFFFFF; margin:5px 0 0 0;">SUMIT CHAUDHARY</h3></div>""", unsafe_allow_html=True)

# ==========================================
# 5. MAIN CONTENT SWITCHER
# ==========================================

# --- DASHBOARD VIEW ---
if st.session_state.view == "dashboard":
    st.markdown("<h1 style='text-align: center; margin-top: 5vh; color: #1A1A1A;'>Dashboard</h1>", unsafe_allow_html=True)
    
    # Centre horizontal alignment with 2 large columns
    _, col_mid1, col_mid2, _ = st.columns([1, 4, 4, 1])
    
    with col_mid1:
        # Title="dash_tab" triggers the specific large button CSS
        if st.button("AskMNIT 🤖", title="dash_tab"):
            st.session_state.view = "chatbot"
            st.rerun()
            
    with col_mid2:
        if st.button("Coming Soon ⏳", title="dash_tab"):
            st.toast("This feature is under development!")

# --- CHATBOT VIEW ---
else:
    title_class = "title-container-empty" if is_chat_empty else "title-container-active"
    st.markdown(f"""<div class="{title_class}"><div style="color: #1A1A1A; font-weight: 800; text-align: center; font-size: 3.5rem;">AskMNIT</div><div style="text-align: center; color: #666666; font-size: 1.2rem;">Your Professional AI Assistant</div></div>""", unsafe_allow_html=True)

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
