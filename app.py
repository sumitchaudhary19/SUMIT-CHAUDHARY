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
if "pending_generation" not in st.session_state:
    st.session_state.pending_generation = False

is_chat_empty = len(st.session_state.sessions[st.session_state.current_chat]) == 0

# ==========================================
# 3. CSS (Updated Tab Length & Dialog Styling)
# ==========================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    /* Body Background */
    html, body, [class*="css"], [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        font-family: 'Inter', sans-serif;
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
    }}
    
    [data-testid="stMain"] {{
        background-color: #FFFFFF !important;
    }}

    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}

    [data-testid="stBottom"] {{
        background-color: #FFFFFF !important;
        border-top: none !important;
    }}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: #F0F2F6 !important;
        border-right: 1px solid #DDDDDD !important;
        width: 320px !important; /* Sidebar width adjusted for longer tabs */
    }}

    /* --- SHINY VIOLET TABS (Longer & Symmetric) --- */
    .stButton>button, .stDownloadButton>button, [data-testid="stLinkButton"] > a {{
        width: 100% !important; /* Spans full sidebar width */
        min-width: 250px !important; /* Minimum length increased */
        background: linear-gradient(135deg, #8A63FF 0%, #6A3DE8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 14px 20px !important; /* Slightly more padding for size */
        font-weight: 600 !important;
        text-align: center !important;
        box-shadow: 0 4px 15px rgba(138, 99, 255, 0.3) !important;
        transition: 0.3s all ease !important;
        text-decoration: none !important;
        display: block !important;
        margin-bottom: 12px !important;
    }}

    .stButton>button:hover, [data-testid="stLinkButton"] > a:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(138, 99, 255, 0.5) !important;
        background: linear-gradient(135deg, #9D7CFF 0%, #7B52F2 100%) !important;
    }}

    /* DIALOG STYLING */
    div[data-testid="stDialog"] div[role="dialog"] {{
        background-color: #2C2C2C !important;
        border-radius: 15px !important;
        border: 1px solid #444 !important;
    }}

    /* SEARCH BAR STYLING */
    div[data-testid="stChatInput"] {{
        width: 650px !important;
        margin: 0 auto !important;
        background-color: transparent !important;
        position: fixed !important;
        bottom: 20px !important;
        left: 0; right: 0; z-index: 999;
    }}

    div[data-testid="stChatInput"] > div {{
        background-color: #FFFFFF !important;
        border: 1px solid #DDDDDD !important;
        border-radius: 15px !important;
        height: 120px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08) !important;
    }}

    /* DARK GREY PLUS TAB */
    .plus-tab-ui {{
        position: fixed;
        left: calc(50% - 310px);
        width: 34px; height: 34px;
        background-color: #333333 !important;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        color: #FFFFFF !important;
        font-size: 22px; font-weight: 400;
        z-index: 1001; bottom: 32px !important;
    }}

    /* Header Positioning */
    .title-container-empty {{ margin-top: 20vh; transition: 0.5s; }}
    .title-container-active {{ margin-top: 2vh; scale: 0.7; transition: 0.5s; }}
    
    .signature-box {{ 
        margin-top: 40px; padding: 15px; border-radius: 8px; 
        background: #EAECEF; border: 1px solid #CCC; text-align: center; 
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. UNIVERSITY TOOLS DIALOG
# ==========================================
@st.dialog("University Tools")
def open_uni_tools():
    st.write("Access MNIT Student Portals:")
    st.link_button("Class Schedule 📅", "https://www.mnit.ac.in/TimeTable/", use_container_width=True)
    st.link_button("ERP Portal 🌐", "https://mniterp.org/mniterp/", use_container_width=True)

# ==========================================
# 5. SIDEBAR (TOOLS SECTION)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color: #1A1A1A; text-align: center; margin-bottom: 25px;'>Tools</h2>", unsafe_allow_html=True)
    
    # Symmetric Sidebar Tabs
    if st.button("➕ New Session"):
        st.session_state.sessions = {"New Session": []}
        st.session_state.current_chat = "New Session"
        st.rerun()

    if st.button("Chat History 🕑"):
        st.toast("Chat history feature coming soon!")

    if st.button("University Tools ⚙️"):
        open_uni_tools()
    
    st.markdown("<div style='margin-top: 30px; border-top: 1px solid #DDD;'></div>", unsafe_allow_html=True)
    st.markdown("""<div class="signature-box"><p style="color:#666; font-size:0.75rem; margin:0;">Architected by</p><h3 style="color:#1A1A1A; margin:0;">SUMIT CHAUDHARY</h3></div>""", unsafe_allow_html=True)

# ==========================================
# 6. MAIN CHAT DISPLAY
# ==========================================
title_class = "title-container-empty" if is_chat_empty else "title-container-active"
st.markdown(f"""
    <div class="{title_class}">
        <div style="color: #1A1A1A; font-weight: 800; text-align: center; font-size: 3.5rem;">AskMNIT</div>
        <div style="text-align: center; color: #666666; font-size: 1.2rem;">Your Professional AI Assistant</div>
    </div>
""", unsafe_allow_html=True)

for message in st.session_state.sessions[st.session_state.current_chat]:
    avatar_icon = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

# ==========================================
# 7. CHAT INPUT & PLUS UI
# ==========================================
st.markdown('<div class="plus-tab-ui">+</div>', unsafe_allow_html=True)

if prompt := st.chat_input("Ask me anything..."):
    st.session_state.sessions[st.session_state.current_chat].append({"role": "user", "content": prompt})
    st.session_state.pending_generation = True
    st.rerun()

if st.session_state.pending_generation:
    user_query = st.session_state.sessions[st.session_state.current_chat][-1]["content"]
    with st.chat_message("assistant", avatar="🤖"):
        try:
            def generate_response():
                stream = client.chat.completions.create(
                    messages=[{"role": "system", "content": "You are 'AskMNIT', an intelligent AI assistant for MNIT Jaipur."},
                              {"role": "user", "content": user_query}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.7,
                    stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content
            response_text = st.write_stream(generate_response())
            st.session_state.sessions[st.session_state.current_chat].append({"role": "assistant", "content": response_text})
        except Exception as e:
            st.error(f"Error: {str(e)}")
    st.session_state.pending_generation = False
