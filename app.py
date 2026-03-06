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
# 3. CSS (Clean White Theme - No Lines)
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

    /* --- Removing Horizontal Line from Bottom Area --- */
    [data-testid="stBottom"] {{
        background-color: #FFFFFF !important;
        border-top: none !important; /* Line removed */
    }}
    
    [data-testid="stBottom"] > div {{
        background-color: transparent !important;
    }}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: #F0F2F6 !important;
        border-right: 1px solid #DDDDDD !important;
    }}

    /* Chat Messages Container */
    [data-testid="stChatMessageContainer"] {{
        max-width: 800px !important;
        margin: 0 auto !important;
    }}

    div[data-testid="stChatMessage"] {{
        border-radius: 12px;
        margin-bottom: 1.5rem !important;
    }}

    div[data-testid="stChatMessage"]:nth-child(odd) {{
        background-color: #F8F9FA !important;
        border: 1px solid #EEEEEE !important;
    }}

    div[data-testid="stChatMessage"]:nth-child(even) {{
        background-color: #FFFFFF !important;
        border: 1px solid #F0F0F0 !important;
    }}

    /* --- PURE WHITE SEARCH BAR --- */
    div[data-testid="stChatInput"] {{
        width: 650px !important;
        margin: 0 auto !important;
        background-color: transparent !important;
        position: fixed !important;
        bottom: 20px !important;
        left: 0; right: 0; z-index: 999;
    }}

    div[data-testid="stChatInput"] > div {{
        background-color: #FFFFFF !important; /* White Background */
        border: 1px solid #DDDDDD !important;
        border-radius: 15px !important;
        height: 120px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }}

    div[data-testid="stChatInput"] textarea {{
        background-color: #FFFFFF !important; /* White Interior */
        color: #1A1A1A !important;
        font-size: 1.1rem !important;
        padding: 10px 60px 50px 15px !important; 
        line-height: 1.5 !important;
        border: none !important;
    }}

    /* Arrow Tab Design */
    div[data-testid="stChatInput"] button {{
        background-color: #1A1A1A !important;
        border-radius: 50% !important;
        right: 15px !important;
        bottom: 42px !important; 
        width: 35px !important;
    }}

    div[data-testid="stChatInput"] button::after {{
        content: ">";
        color: #FFFFFF; font-weight: 900; font-size: 1.2rem;
    }}
    div[data-testid="stChatInput"] button svg {{ display: none !important; }}

    /* Placeholder Text */
    div[data-testid="stChatInput"] textarea::placeholder {{
        color: #999999 !important;
    }}

    /* Dynamic Header Position */
    .title-container-empty {{ margin-top: 25vh; transition: 0.5s; }}
    .title-container-active {{ margin-top: 2vh; scale: 0.8; transition: 0.5s; }}

    .main-title {{ color: #1A1A1A; font-weight: 800; text-align: center; font-size: 3.5rem; }}
    .title-subtext {{ text-align: center; color: #666666; font-size: 1.2rem; }}

    /* Sidebar Buttons */
    .stButton>button {{
        width: 100%; background-color: #FFFFFF !important;
        border: 1px solid #CCC !important; color: #1A1A1A !important;
        border-radius: 8px; font-weight: 600;
    }}
    
    .signature-box {{ 
        margin-top: 40px; padding: 15px; border-radius: 8px; 
        background: #EAECEF; border: 1px solid #CCC; text-align: center; 
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. SIDEBAR (TOOLS SECTION)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color: #1A1A1A; text-align: center;'>Tools</h2>", unsafe_allow_html=True)
    
    if st.button("➕ New Session"):
        st.session_state.sessions["New Session"] = []
        st.session_state.current_chat = "New Session"
        st.rerun()

    st.link_button("Class Schedule 📅", "https://www.mnit.ac.in/TimeTable/", use_container_width=True)
    st.link_button("ERP 🌐", "https://mniterp.org/mniterp/", use_container_width=True)
    
    st.markdown("""<div class="signature-box"><p style="color:#666; font-size:0.75rem; margin:0;">Architected by</p><h3 style="color:#1A1A1A;">SUMIT CHAUDHARY</h3></div>""", unsafe_allow_html=True)

# ==========================================
# 5. MAIN CHAT DISPLAY
# ==========================================
title_class = "title-container-empty" if is_chat_empty else "title-container-active"
st.markdown(f"""
    <div class="{title_class}">
        <div class="main-title">AskMNIT</div>
        <div class="title-subtext">Your Professional AI Assistant</div>
    </div>
""", unsafe_allow_html=True)

for message in st.session_state.sessions[st.session_state.current_chat]:
    avatar_icon = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

# ==========================================
# 6. CHAT INPUT
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
                    messages=[
                        {"role": "system", "content": "You are 'AskMNIT', a professional assistant for MNIT Jaipur students."},
                        {"role": "user", "content": user_query}
                    ],
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
