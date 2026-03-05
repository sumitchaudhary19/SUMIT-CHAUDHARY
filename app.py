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
# 3. CSS (Updated Colors)
# ==========================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    /* --- Poore Chat Section Ka Background Dark Grey --- */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        font-family: 'Inter', sans-serif;
        background-color: #121212 !important; /* Base Deep Dark */
        color: #E0E0E0 !important;
    }}
    
    [data-testid="stMain"] {{
        background-color: #1E1E1E !important; /* Chat Section Dark Grey */
    }}

    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}

    /* --- Chat Message Styling --- */
    div[data-testid="stChatMessage"]:nth-child(odd) {{
        background-color: #2C2C2C !important;
        border: 1px solid #444 !important;
        border-radius: 12px;
        max-width: 75% !important;
        margin-left: auto !important;
    }}

    div[data-testid="stChatMessage"]:nth-child(even) {{
        background-color: #252525 !important;
        border: 1px solid #333 !important;
        border-radius: 12px;
    }}

    /* --- Search Bar Interior Colour Grey --- */
    div[data-testid="stChatInput"] {{
        width: 650px !important;
        margin: 0 auto !important;
    }}

    div[data-testid="stChatInput"] > div {{
        background-color: #333333 !important; /* Interior Grey */
        border: 1px solid #555 !important;
        border-radius: 15px !important;
        height: 120px !important;
        padding: 10px !important;
    }}

    div[data-testid="stChatInput"] textarea {{
        background-color: transparent !important;
        color: #FFFFFF !important;
        font-size: 1.1rem !important;
        padding: 10px 60px 45px 10px !important;
        line-height: 1.5 !important;
    }}

    /* Arrow Tab Button */
    div[data-testid="stChatInput"] button {{
        background-color: #E0E0E0 !important;
        border-radius: 50% !important;
        right: 15px !important;
        bottom: 42px !important;
        width: 35px !important;
        height: 35px !important;
    }}

    div[data-testid="stChatInput"] button::after {{
        content: ">";
        color: #1A1A1A;
        font-weight: 900;
        font-size: 1.2rem;
    }}
    div[data-testid="stChatInput"] button svg {{
        display: none !important;
    }}

    /* Plus Icon Overlay */
    .fixed-plus-icon {{
        position: fixed;
        bottom: 35px;
        left: calc(50% - 310px);
        color: #BBBBBB;
        font-size: 24px;
        z-index: 1000;
        pointer-events: none;
    }}

    section[data-testid="stSidebar"] {{ background-color: #111111 !important; border-right: 1px solid #333 !important; }}
    
    .stButton>button {{
        width: 100%; text-align: left; background-color: #D3D3D3 !important;
        border: 1px solid #999 !important; padding: 10px 15px; border-radius: 8px;
        color: #000000 !important;
    }}
    
    .signature-box {{ margin-top: 40px; margin-bottom: 20px; padding: 15px; border-radius: 8px; background: #2C2C2C; border: 1px solid #444; text-align: center; }}
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
        chat_id = f"Session {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[chat_id] = []
        st.session_state.current_chat = chat_id
        st.rerun()

    st.link_button("Class Schedule 📅", "https://www.mnit.ac.in/TimeTable/", use_container_width=True)
    st.link_button("ERP 🌐", "https://mniterp.org/mniterp/", use_container_width=True)

    st.markdown("""<div class="signature-box"><p style="color:#AAA; font-size:0.75rem; margin:0;">Architected by</p><h3>SUMIT CHAUDHARY</h3></div>""", unsafe_allow_html=True)

# ==========================================
# 5. MAIN CHAT DISPLAY
# ==========================================
if is_chat_empty:
    st.markdown("<h1 style='color: #FFFFFF; font-weight: 800; text-align: center; font-size: 3rem; margin-top: 20vh;'>AskMNIT</h1>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; color: #BBBBBB; font-weight: 500; font-size: 1.2rem; margin-bottom: 50px;'>Your Professional AI Assistant</div>", unsafe_allow_html=True)

# Container for messages
for message in st.session_state.sessions[st.session_state.current_chat]:
    avatar_icon = "user.png" if message["role"] == "user" else "logo.png"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

# ==========================================
# 6. CHAT INPUT & BACKEND LOGIC
# ==========================================
if is_chat_empty:
    st.markdown('<div class="fixed-plus-icon">+</div>', unsafe_allow_html=True)

if prompt := st.chat_input("Ask me anything..."):
    st.session_state.sessions[st.session_state.current_chat].append({"role": "user", "content": prompt})
    st.session_state.pending_generation = True
    st.rerun()

if st.session_state.pending_generation:
    user_query = st.session_state.sessions[st.session_state.current_chat][-1]["content"]
    with st.chat_message("assistant", avatar="logo.png"):
        try:
            def generate_response():
                stream = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are 'AskMNIT', a professional AI assistant for MNIT Jaipur students."},
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
            st.error(f"API Error: {str(e)}")
    st.session_state.pending_generation = False
