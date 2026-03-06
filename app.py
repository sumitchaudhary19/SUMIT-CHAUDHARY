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
# 3. CSS (Sticky Header & Scroll Control)
# ==========================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    /* Body & Main Container */
    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Inter', sans-serif;
        background-color: #FFFFFF !important;
    }}
    
    [data-testid="stMain"] {{
        background-color: #FFFFFF !important;
    }}

    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
    [data-testid="stHeader"] {{ display: none !important; }}

    /* --- FIXED STICKY HEADER (AskMNIT) --- */
    .sticky-header-container {{
        position: fixed;
        top: 0;
        left: 320px; /* Sidebar width */
        right: 0;
        height: 140px;
        background-color: #FFFFFF;
        z-index: 1000;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }}
    
    /* Responsive adjustment for mobile/collapsed sidebar */
    @media (max-width: 768px) {{
        .sticky-header-container {{ left: 0; }}
    }}

    .main-title {{
        color: #1A1A1A;
        font-weight: 800;
        font-size: 3.5rem;
        margin: 0;
    }}

    .title-subtext {{
        color: #666666;
        font-size: 1.1rem;
        margin-top: -5px;
    }}

    /* --- CHAT AREA POSITIONING --- */
    /* Chats will start below the fixed header */
    [data-testid="stChatMessageContainer"] {{
        max-width: 800px !important;
        margin: 150px auto 120px auto !important; /* Top margin for header, Bottom for search bar */
        padding-top: 0 !important;
    }}

    div[data-testid="stChatMessage"] {{
        border-radius: 12px;
        margin-bottom: 1rem !important;
        border: 1px solid #EEEEEE !important;
    }}

    /* --- SIDEBAR TABS --- */
    section[data-testid="stSidebar"] {{
        background-color: #F0F2F6 !important;
        border-right: 1px solid #DDDDDD !important;
    }}

    .stButton>button, [data-testid="stLinkButton"] > a {{
        width: 100% !important;
        background: linear-gradient(135deg, #8A63FF 0%, #6A3DE8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 14px 20px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(138, 99, 255, 0.3) !important;
        margin-bottom: 12px !important;
    }}

    /* --- BOTTOM SEARCH BAR --- */
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

    /* --- PLUS & MIC TABS --- */
    .input-btn-base {{
        position: fixed;
        width: 32px; height: 32px;
        background-color: #333333 !important;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        z-index: 1001; bottom: 44px !important;
    }}
    .plus-tab-ui {{ left: calc(50% - 310px); color: #FFFFFF !important; }}
    .mic-tab-ui {{ left: calc(50% - 270px); color: #A0A0A0 !important; }}

    /* Arrow button adjustments */
    div[data-testid="stChatInput"] button {{
        bottom: 22px !important;
        background-color: #1A1A1A !important;
        border-radius: 50% !important;
    }}
    div[data-testid="stChatInput"] button::after {{ content: ">"; color: white; font-weight: 900; }}
    div[data-testid="stChatInput"] button svg {{ display: none !important; }}

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
# 6. FIXED HEADER RENDER
# ==========================================
# This div stays fixed at the top and hides chats scrolling underneath
st.markdown(f"""
    <div class="sticky-header-container">
        <h1 class="main-title">AskMNIT</h1>
        <p class="title-subtext">Your Professional AI Assistant</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 7. CHAT DISPLAY AREA
# ==========================================
# Chat messages are inside the container defined in CSS with top margin
for message in st.session_state.sessions[st.session_state.current_chat]:
    avatar_icon = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

# ==========================================
# 8. CHAT INPUT & TABS UI
# ==========================================
st.markdown('<div class="input-btn-base plus-tab-ui">+</div>', unsafe_allow_html=True)
st.markdown('<div class="input-btn-base mic-tab-ui">🎤</div>', unsafe_allow_html=True)

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
                    messages=[{"role": "system", "content": "You are 'AskMNIT', an AI assistant for MNIT Jaipur students."} , 
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
