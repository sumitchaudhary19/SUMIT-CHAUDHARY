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
# 3. CSS
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

    div[data-testid="stChatMessage"]:nth-child(odd) {{
        background-color: #2C2C2C !important;
        border: 1px solid #444 !important;
        width: fit-content !important;
        max-width: 75% !important;
        margin-left: auto !important;
        margin-right: 0 !important;
    }}

    div[data-testid="stChatMessage"]:nth-child(even) {{
        background-color: #212121 !important;
        border: 1px solid #333 !important;
        width: 100% !important;
        max-width: 100% !important;
        margin-right: auto !important;
        margin-left: 0 !important;
    }}

    section[data-testid="stSidebar"] {{ background-color: #111111 !important; border-right: 1px solid #333 !important; }}

    /* --- Functional Search Bar Styling --- */
    div[data-testid="stChatInput"] {{
        width: 650px !important;
        margin: 0 auto !important;
        background-color: transparent !important;
    }}

    div[data-testid="stChatInput"] > div {{
        background-color: #2C2C2C !important;
        border: 1px solid #444 !important;
        border-radius: 15px !important;
        height: 120px !important;
        padding: 10px !important;
    }}

    div[data-testid="stChatInput"] textarea {{
        background-color: transparent !important;
        color: #E0E0E0 !important;
        font-size: 1.1rem !important;
        padding: 5px 60px 45px 10px !important;
        line-height: 1.5 !important;
    }}

    /* Custom Arrow Button Style to match your design */
    div[data-testid="stChatInput"] button {{
        background-color: #E0E0E0 !important;
        border-radius: 50% !important;
        right: 15px !important;
        bottom: 42px !important; /* Adjusted to stay middle of height */
        width: 35px !important;
        height: 35px !important;
    }}
    
    div[data-testid="stChatInput"] button:hover {{
        background-color: #FFFFFF !important;
    }}

    /* The Fixed Plus Overlay */
    .plus-overlay {{
        position: fixed;
        bottom: 38px; /* Adjusted based on chat input position */
        left: calc(50% - 305px);
        color: #888888;
        font-size: 24px;
        z-index: 1000;
        pointer-events: none;
    }}

    .stButton>button {{
        width: 100%; text-align: left; background-color: #D3D3D3 !important;
        border: 1px solid #999 !important; padding: 10px 15px; border-radius: 8px;
        font-weight: 600; color: #000000 !important; transition: 0.2s;
    }}
    
    .signature-box {{ margin-top: 40px; margin-bottom: 20px; padding: 15px; border-radius: 8px; background: #2C2C2C; border: 1px solid #444; text-align: center; }}
    .signature-box p {{ margin: 0; font-size: 0.75rem; color: #AAAAAA; text-transform: uppercase; letter-spacing: 1px; }}
    .signature-box h3 {{ margin: 5px 0 0 0; font-size: 1.1rem; color: #E0E0E0; font-weight: 700; }}
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

    st.markdown("""<div class="signature-box"><p>Architected by</p><h3>SUMIT CHAUDHARY</h3></div>""", unsafe_allow_html=True)

# ==========================================
# 5. MAIN CHAT DISPLAY
# ==========================================
if is_chat_empty:
    st.markdown("<h1 style='color: #FFFFFF; font-weight: 800; text-align: center; font-size: 3rem; margin-top: 20vh;'>AskMNIT</h1>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; color: #BBBBBB; font-weight: 500; font-size: 1.2rem; margin-bottom: 40px;'>Your Professional AI Assistant</div>", unsafe_allow_html=True)

# Display Chat Messages
for message in st.session_state.sessions[st.session_state.current_chat]:
    avatar_icon = "user.png" if message["role"] == "user" else "logo.png"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

# ==========================================
# 6. CHAT INPUT & GENERATION LOGIC
# ==========================================
# Overlay the + symbol visually
if is_chat_empty:
    st.markdown('<div class="plus-overlay">+</div>', unsafe_allow_html=True)

if prompt := st.chat_input("Ask me anything..."):
    # Save user message
    st.session_state.sessions[st.session_state.current_chat].append({"role": "user", "content": prompt})
    st.session_state.pending_generation = True
    st.rerun()

# AI Response Logic
if st.session_state.pending_generation:
    user_prompt = st.session_state.sessions[st.session_state.current_chat][-1]["content"]
    
    with st.chat_message("assistant", avatar="logo.png"):
        instructions = "You are 'AskMNIT', an exceptionally intelligent and professional AI assistant for MNIT."
        
        try:
            def generate_response():
                stream = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": instructions},
                        {"role": "user", "content": user_prompt}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.7,
                    stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content

            full_response = st.write_stream(generate_response())
            st.session_state.sessions[st.session_state.current_chat].append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.session_state.pending_generation = False
