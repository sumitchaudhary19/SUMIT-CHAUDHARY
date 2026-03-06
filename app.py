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
# 3. CSS (Purple Arrow, Sticky Header & UI)
# ==========================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Inter', sans-serif;
        background-color: #FFFFFF !important;
    }}
    
    [data-testid="stMain"] {{
        background-color: #FFFFFF !important;
    }}

    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
    [data-testid="stHeader"] {{ display: none !important; }}

    /* --- PURPLE SIDEBAR ARROW BUTTON --- */
    button[data-testid="sidebar-button-container"] svg {{
        fill: #8A63FF !important; /* Purple color */
        color: #8A63FF !important;
        transform: scale(1.2); /* Slightly larger for visibility */
    }}
    
    button[data-testid="sidebar-button-container"] {{
        background-color: transparent !important;
    }}

    /* --- FIXED STICKY HEADER --- */
    /* Dynamic width based on sidebar state */
    .sticky-header-container {{
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 140px;
        background-color: #FFFFFF;
        z-index: 1000;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border-bottom: 1px solid transparent;
    }}

    .main-title {{ color: #1A1A1A; font-weight: 800; font-size: 3.5rem; margin: 0; }}
    .title-subtext {{ color: #666666; font-size: 1.1rem; margin-top: -5px; }}

    /* --- CHAT AREA & FONT --- */
    [data-testid="stChatMessageContainer"] {{
        max-width: 800px !important;
        margin: 150px auto 120px auto !important;
        padding-top: 0 !important;
    }}

    [data-testid="stChatMessage"] p {{
        font-size: 1.15rem !important;
        line-height: 1.6 !important;
        color: #1A1A1A !important;
    }}

    div[data-testid="stChatMessage"]:nth-child(odd) {{
        background-color: transparent !important;
        border: none !important;
    }}

    div[data-testid="stChatMessage"]:nth-child(even) {{
        background-color: #FFFFFF !important;
        border: 1px solid #F0F0F0 !important;
        border-radius: 12px;
        margin-bottom: 1.5rem !important;
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
        margin-bottom: 12px !important;
        text-align: center !important;
        text-decoration: none !important;
        display: block !important;
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
        color: #1A1A1A !important;
        font-size: 1.1rem !important;
        padding: 15px 60px 15px 95px !important; 
        line-height: 1.4 !important;
        border: none !important;
        height: 80px !important;
    }}

    /* --- ICONS --- */
    .input-btn-base {{
        position: fixed;
        width: 32px; height: 32px;
        background-color: #333333 !important;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        z-index: 1001; 
        bottom: 44px !important;
    }}
    .plus-tab-ui {{ left: calc(50% - 310px); color: #FFFFFF !important; font-size: 20px; }}
    .mic-tab-ui {{ left: calc(50% - 270px); color: #A0A0A0 !important; font-size: 18px; }}

    div[data-testid="stChatInput"] button {{
        bottom: 22px !important;
        background-color: #1A1A1A !important;
        border-radius: 50% !important;
    }}
    div[data-testid="stChatInput"] button::after {{ content: ">"; color: white; font-weight: 900; }}
    div[data-testid="stChatInput"] button svg {{ display: none !important; }}

    .signature-box {{ margin-top: 40px; padding: 15px; border-radius: 8px; background: #EAECEF; border: 1px solid #CCC; text-align: center; }}
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
        st.toast("History feature coming soon!")
    if st.button("University Tools ⚙️"):
        open_uni_tools()
    st.markdown("<div style='margin-top: 30px; border-top: 1px solid #DDD;'></div>", unsafe_allow_html=True)
    st.markdown("""<div class="signature-box"><p style="color:#666; font-size:0.75rem; margin:0;">Architected by</p><h3 style="color:#1A1A1A; margin:0;">SUMIT CHAUDHARY</h3></div>""", unsafe_allow_html=True)

# ==========================================
# 6. FIXED HEADER
# ==========================================
st.markdown(f"""
    <div class="sticky-header-container">
        <h1 class="main-title">AskMNIT</h1>
        <p class="title-subtext">Your Professional AI Assistant</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 7. CHAT DISPLAY
# ==========================================
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
                    messages=[{"role": "system", "content": "You are 'AskMNIT', an intelligent AI assistant for MNIT Jaipur students."},
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
