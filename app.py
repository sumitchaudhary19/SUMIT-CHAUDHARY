import streamlit as st
import urllib.parse
import time
import base64
from groq import Groq

# ==========================================
# 1. PAGE CONFIG
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
# 3. CSS (New Minimalist Purple Tools Section)
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

    /* --- LOCKED SIDEBAR (New Clean Tools Section) --- */
    section[data-testid="stSidebar"] {{
        background-color: #FFFFFF !important; /* White background for clean look */
        border-right: 1px solid #EEEEEE !important;
        width: 300px !important;
    }}
    
    /* Remove sidebar arrow/collapse */
    button[data-testid="sidebar-button-container"] {{ display: none !important; }}
    [data-testid="collapsedControl"] {{ display: none !important; }}

    /* --- PURPLE TABS STYLE --- */
    .stButton>button {{
        width: 100% !important;
        background: linear-gradient(135deg, #8A63FF 0%, #6A3DE8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 18px 20px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin-bottom: 15px !important;
        box-shadow: 0 4px 15px rgba(138, 99, 255, 0.2) !important;
        transition: 0.3s all ease !important;
        text-align: center !important;
    }}

    .stButton>button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(138, 99, 255, 0.4) !important;
    }}

    /* --- STICKY HEADER --- */
    .sticky-header {{
        position: fixed;
        top: 0;
        right: 0;
        left: 300px;
        height: 120px;
        background-color: #FFFFFF;
        z-index: 999;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }}

    .main-title {{ color: #1A1A1A; font-weight: 800; font-size: 3rem; margin: 0; }}
    .title-subtext {{ color: #666666; font-size: 1rem; }}

    /* --- CHAT CONTAINER --- */
    [data-testid="stChatMessageContainer"] {{
        max-width: 800px !important;
        margin: 120px auto 100px auto !important;
    }}

    [data-testid="stChatMessage"] p {{ font-size: 1.15rem !important; }}

    div[data-testid="stChatMessage"]:nth-child(odd) {{ background-color: transparent !important; border: none !important; }}
    div[data-testid="stChatMessage"]:nth-child(even) {{
        background-color: #FFFFFF !important;
        border: 1px solid #F0F0F0 !important;
        border-radius: 12px;
    }}

    /* --- SEARCH BAR --- */
    div[data-testid="stChatInput"] {{
        width: 650px !important;
        margin: 0 auto !important;
        position: fixed !important;
        bottom: 20px !important;
        left: 0; right: 0; z-index: 998;
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
        padding: 15px 60px 15px 95px !important;
        height: 80px !important;
    }}

    /* --- ICONS --- */
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

    div[data-testid="stChatInput"] button {{
        bottom: 22px !important;
        background-color: #1A1A1A !important;
        border-radius: 50% !important;
    }}
    div[data-testid="stChatInput"] button::after {{ content: ">"; color: white; font-weight: 900; }}
    div[data-testid="stChatInput"] button svg {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. NEW TOOLS SECTION (SIDEBAR)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color: #1A1A1A; text-align: center; margin-bottom: 30px; margin-top: 20px;'>Tools</h2>", unsafe_allow_html=True)
    
    # 3 Purple Tabs (Empty for now)
    st.button("Tab 1")
    st.button("Tab 2")
    st.button("Tab 3")

# ==========================================
# 5. HEADER
# ==========================================
st.markdown(f"""
    <div class="sticky-header">
        <h1 class="main-title">AskMNIT</h1>
        <p class="title-subtext">Your Professional AI Assistant</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 6. CHAT DISPLAY
# ==========================================
for message in st.session_state.sessions[st.session_state.current_chat]:
    avatar_icon = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

# ==========================================
# 7. CHAT INPUT & TABS UI
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
                    messages=[{"role": "system", "content": "You are 'AskMNIT', an AI assistant for MNIT Jaipur students."},
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
