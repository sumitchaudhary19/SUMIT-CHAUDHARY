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
# 3. CSS (Buttons, Pills & Animations)
# ==========================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Inter', sans-serif;
        background-color: #FFFFFF !important;
    }}
    
    [data-testid="stMain"] {{ background-color: #FFFFFF !important; }}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
    [data-testid="stHeader"] {{ display: none !important; }}

    /* --- SIDEBAR --- */
    button[data-testid="sidebar-button-container"] {{ display: none !important; }}
    [data-testid="collapsedControl"] {{ display: none !important; }}

    /* --- FIXED STICKY HEADER --- */
    .sticky-header-container {{
        position: fixed;
        top: 0; left: 320px; right: 0;
        height: 140px;
        background-color: #FFFFFF;
        z-index: 1000;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
    }}

    /* --- CENTERED SUGGESTION PILLS --- */
    .pill-wrapper {{
        display: flex; justify-content: center; gap: 12px;
        margin-top: 150px; width: 100%;
    }}

    div.stButton > button[key^="pill_"] {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #E0E0E0 !important;
        border-radius: 50px !important;
        padding: 10px 22px !important;
        font-size: 0.95rem !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important;
    }}

    /* --- CHAT AREA --- */
    [data-testid="stChatMessageContainer"] {{
        max-width: 800px !important;
        margin: 140px auto 120px auto !important;
    }}

    /* --- SIDEBAR TABS --- */
    section[data-testid="stSidebar"] {{
        background-color: #F0F2F6 !important;
        border-right: 1px solid #DDDDDD !important;
        width: 320px !important;
    }}

    .stButton>button {{
        width: 100% !important;
        background: linear-gradient(135deg, #8A63FF 0%, #6A3DE8 100%) !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }}

    /* --- SEARCH BAR (80PX) --- */
    div[data-testid="stChatInput"] {{
        width: 650px !important;
        margin: 0 auto !important;
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
        padding: 15px 60px 15px 95px !important;
        height: 80px !important;
    }}

    /* --- CLICKABLE ICONS (Now using st.button logic) --- */
    .icon-click-zone {{
        position: fixed;
        z-index: 1002;
        bottom: 44px !important;
    }}

    /* Floating Dialog for Voice */
    .voice-pulse {{
        width: 60px; height: 60px;
        background: #8A63FF;
        border-radius: 50%;
        margin: 20px auto;
        animation: pulse 1.5s infinite;
    }}

    @keyframes pulse {{
        0% {{ transform: scale(0.9); opacity: 0.7; }}
        50% {{ transform: scale(1.1); opacity: 1; }}
        100% {{ transform: scale(0.9); opacity: 0.7; }}
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. DIALOGS (File Upload & Voice)
# ==========================================
@st.dialog("Upload Documents 📄")
def open_upload_dialog():
    st.write("Upload your notes or images for analysis:")
    uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'png', 'jpg', 'jpeg'])
    if uploaded_file:
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        if st.button("Analyze with AI"):
            st.toast("Feature coming soon: Image/PDF analysis!")

@st.dialog("Voice Search 🎤")
def open_voice_dialog():
    st.markdown('<div class="voice-pulse"></div>', unsafe_allow_html=True)
    st.write("Listening to your voice...")
    st.info("Tip: Speak clearly about MNIT academics or campus.")
    if st.button("Stop Recording"):
        st.rerun()

@st.dialog("University Tools")
def open_uni_tools():
    st.write("Access MNIT Student Portals:")
    st.link_button("Class Schedule 📅", "https://www.mnit.ac.in/TimeTable/", use_container_width=True)
    st.link_button("ERP Portal 🌐", "https://mniterp.org/mniterp/", use_container_width=True)

@st.dialog("Chat History 🕑")
def open_chat_history():
    st.write("Pick a session:")
    for session_key, messages in st.session_state.sessions.items():
        display_name = messages[0]["content"][:30] + "..." if messages else session_key
        if st.button(display_name, key=f"btn_{session_key}", use_container_width=True):
            st.session_state.current_chat = session_key
            st.rerun()

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
    st.markdown(f"""<div style="text-align:center; margin-top:20px; color:#666;">Architected by<br><b>SUMIT CHAUDHARY</b></div>""", unsafe_allow_html=True)

# ==========================================
# 6. HEADER
# ==========================================
st.markdown(f"""
    <div class="sticky-header-container">
        <div style="color: #1A1A1A; font-weight: 800; font-size: 3.5rem;">AskMNIT</div>
        <div style="color: #666666; font-size: 1.1rem; margin-top: -5px;">Your Professional AI Assistant</div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 7. CHAT DISPLAY & SUGGESTIONS
# ==========================================
if is_chat_empty:
    st.markdown('<div class="pill-wrapper">', unsafe_allow_html=True)
    cols = st.columns([2, 1, 1, 1, 2])
    suggestions = ["Class schedule?", "Mineral Processing notes", "Metallurgy Syllabus"]
    if cols[1].button(suggestions[0], key="pill_1"):
        st.session_state.sessions[st.session_state.current_chat].append({"role": "user", "content": suggestions[0]}); st.session_state.pending_generation = True; st.rerun()
    if cols[2].button(suggestions[1], key="pill_2"):
        st.session_state.sessions[st.session_state.current_chat].append({"role": "user", "content": suggestions[1]}); st.session_state.pending_generation = True; st.rerun()
    if cols[3].button(suggestions[2], key="pill_3"):
        st.session_state.sessions[st.session_state.current_chat].append({"role": "user", "content": suggestions[2]}); st.session_state.pending_generation = True; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

for message in st.session_state.sessions[st.session_state.current_chat]:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])

# ==========================================
# 8. CHAT INPUT & CLICKABLE ICONS
# ==========================================
# Fixed Position Buttons that trigger Dialogs
col_plus, col_mic = st.columns([1, 1])
with st.container():
    # Render invisible buttons over the UI icons
    st.markdown(f"""
        <div class="icon-click-zone" style="left: calc(50% - 310px);">
    """, unsafe_allow_html=True)
    if st.button("+", key="plus_click", help="Upload Files"):
        open_upload_dialog()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
        <div class="icon-click-zone" style="left: calc(50% - 270px);">
    """, unsafe_allow_html=True)
    if st.button("🎤", key="mic_click", help="Voice Search"):
        open_voice_dialog()
    st.markdown('</div>', unsafe_allow_html=True)

if prompt := st.chat_input("Ask me anything..."):
    st.session_state.sessions[st.session_state.current_chat].append({"role": "user", "content": prompt})
    st.session_state.pending_generation = True
    st.rerun()

if st.session_state.pending_generation:
    user_query = st.session_state.sessions[st.session_state.current_chat][-1]["content"]
    with st.chat_message("assistant", avatar="🤖"):
        def generate_response():
            stream = client.chat.completions.create(
                messages=[{"role": "system", "content": "You are AskMNIT Jaipur Assistant."},
                          {"role": "user", "content": user_query}],
                model="llama-3.3-70b-versatile", stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content: yield chunk.choices[0].delta.content
        response_text = st.write_stream(generate_response())
        st.session_state.sessions[st.session_state.current_chat].append({"role": "assistant", "content": response_text})
    st.session_state.pending_generation = False
