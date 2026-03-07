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

is_chat_empty = len(st.session_state.sessions[st.session_state.current_chat]) == 0

# ==========================================
# 3. CSS (Fixing Positions & Original Styling)
# ==========================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        font-family: 'Inter', sans-serif;
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
    }}
    
    [data-testid="stMain"] {{ background-color: #FFFFFF !important; }}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stBottom"] {{ background-color: #FFFFFF !important; border-top: none !important; }}

    section[data-testid="stSidebar"] {{
        background-color: #F0F2F6 !important;
        border-right: 1px solid #DDDDDD !important;
    }}

    /* SHINY VIOLET SIDEBAR TABS */
    .stButton>button, [data-testid="stLinkButton"] > a {{
        width: 100% !important;
        background: linear-gradient(135deg, #8A63FF 0%, #6A3DE8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 14px 20px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(138, 99, 255, 0.3) !important;
    }}

    /* --- SEARCH BAR AREA --- */
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
        height: 80px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08) !important;
    }}

    div[data-testid="stChatInput"] textarea {{ 
        background-color: #FFFFFF !important;
        padding-left: 95px !important; 
        height: 80px !important; 
        border: none !important;
    }}

    /* --- SEARCH BAR BUTTONS STYLING --- */
    div.stButton > button[key="plus_btn"], div.stButton > button[key="mic_btn"] {{
        position: fixed;
        bottom: 44px !important;
        width: 32px !important;
        height: 32px !important;
        background-color: #333333 !important;
        border-radius: 50% !important;
        z-index: 1002;
        padding: 0 !important;
        display: flex; align-items: center; justify-content: center;
        border: none !important;
        box-shadow: none !important;
        transition: 0.3s;
    }}

    div.stButton > button[key="plus_btn"] {{ left: calc(50% - 310px); color: #FFFFFF !important; font-size: 20px !important; }}
    div.stButton > button[key="mic_btn"] {{ left: calc(50% - 270px); color: #A0A0A0 !important; font-size: 18px !important; }}

    div.stButton > button[key="plus_btn"]:hover, div.stButton > button[key="mic_btn"]:hover {{
        background-color: #444444 !important;
        transform: scale(1.05);
    }}

    /* --- SEND ARROW BUTTON --- */
    div[data-testid="stChatInput"] button {{
        background-color: #1A1A1A !important;
        border-radius: 50% !important;
        right: 15px !important; bottom: 22px !important; 
        width: 35px !important; height: 35px !important;
    }}
    div[data-testid="stChatInput"] button::after {{ content: ">"; color: white; font-weight: 900; font-size: 1.2rem; }}
    div[data-testid="stChatInput"] button svg {{ display: none !important; }}

    /* POPUP/DIALOG STYLING */
    div[data-testid="stDialog"] div[role="dialog"] {{ background-color: #2C2C2C !important; border-radius: 15px !important; border: 1px solid #444 !important; }}
    div[data-testid="stDialog"] h2, div[data-testid="stDialog"] p {{ color: white !important; }}

    /* STICKY HEADER */
    .sticky-header-container {{
        position: fixed; top: 0; left: 320px; right: 0; height: 140px;
        background-color: #FFFFFF; z-index: 1000;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
    }}
    
    .title-container-empty {{ margin-top: 20vh; transition: 0.5s; }}
    .title-container-active {{ margin-top: 2vh; scale: 0.7; transition: 0.5s; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. DIALOGS
# ==========================================
@st.dialog("Attach Documents 📄")
def open_attachment_dialog():
    st.write("Upload PDF or Image for analysis:")
    uploaded_file = st.file_uploader("Choose file", type=['pdf', 'png', 'jpg', 'jpeg'])
    if uploaded_file:
        st.success(f"Attached: {uploaded_file.name}")
        if st.button("Submit to AI"):
            st.info("Wait! Processing logic coming soon.")

@st.dialog("Chat History 🕑")
def open_chat_history():
    st.write("Previous Conversations:")
    for session_key, messages in st.session_state.sessions.items():
        display_name = session_key
        if messages:
            content = messages[0]["content"]
            display_name = (content[:30] + '...') if len(content) > 30 else content
        if st.button(display_name, key=f"hist_{session_key}", use_container_width=True):
            st.session_state.current_chat = session_key
            st.rerun()

@st.dialog("University Tools")
def open_uni_tools():
    st.write("MNIT Academic Portals:")
    st.link_button("Class Schedule 📅", "https://www.mnit.ac.in/TimeTable/", use_container_width=True)
    st.link_button("ERP Portal 🌐", "https://mniterp.org/mniterp/", use_container_width=True)

# ==========================================
# 5. SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color: #1A1A1A; text-align: center; margin-bottom: 25px;'>Tools</h2>", unsafe_allow_html=True)
    if st.button("➕ New Session"):
        new_id = f"Session {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[new_id] = []
        st.session_state.current_chat = new_id
        st.rerun()
    if st.button("Chat History 🕑"):
        open_chat_history()
    if st.button("University Tools ⚙️"):
        open_uni_tools()
    st.markdown("<div style='margin-top: 30px; border-top: 1px solid #DDD;'></div>", unsafe_allow_html=True)
    st.markdown(f"""<div style="text-align:center; margin-top:20px; color:#666; font-size:0.8rem;">Architected by<br><b style="color:#1A1A1A; font-size:1rem;">SUMIT CHAUDHARY</b></div>""", unsafe_allow_html=True)

# ==========================================
# 6. HEADER
# ==========================================
title_class = "title-container-empty" if is_chat_empty else "title-container-active"
st.markdown(f"""
    <div class="sticky-header-container">
        <div class="{title_class}">
            <div style="color: #1A1A1A; font-weight: 800; font-size: 3.5rem; text-align: center;">AskMNIT</div>
            <div style="color: #666666; font-size: 1.1rem; margin-top: -5px; text-align: center;">Your Professional AI Assistant</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 7. CHAT DISPLAY
# ==========================================
for message in st.session_state.sessions[st.session_state.current_chat]:
    role = message["role"]
    with st.chat_message(role, avatar="👤" if role == "user" else "🤖"):
        st.markdown(message["content"])

# ==========================================
# 8. FUNCTIONAL SEARCH BAR BUTTONS
# ==========================================
# Positioning Streamlit buttons as icons over the search bar
if st.button("+", key="plus_btn"):
    open_attachment_dialog()

if st.button("🎤", key="mic_btn"):
    st.toast("🎤 Mic is ready (Feature testing...)")

# ==========================================
# 9. CHAT INPUT LOGIC
# ==========================================
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
                    messages=[{"role": "system", "content": "You are 'AskMNIT', an intelligent AI assistant for MNIT Jaipur students."},
                              {"role": "user", "content": user_query}],
                    model="llama-3.3-70b-versatile", temperature=0.7, stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            response_text = st.write_stream(generate_response())
            st.session_state.sessions[st.session_state.current_chat].append({"role": "assistant", "content": response_text})
        except Exception as e:
            st.error(f"Error: {str(e)}")
    st.session_state.pending_generation = False
