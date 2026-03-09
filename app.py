import streamlit as st
from groq import Groq

# ==========================================
# 1. PAGE CONFIG & SECRETS
# ==========================================
st.set_page_config(page_title="AskMNIT", page_icon="logo.png", layout="wide", initial_sidebar_state="expanded")

if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("🚨 System Error: GROQ_API_KEY is missing!")
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
if "page_view" not in st.session_state:
    st.session_state.page_view = "chatbot"

is_chat_empty = len(st.session_state.sessions[st.session_state.current_chat]) == 0

# ==========================================
# 3. CSS (Dynamic Background & Animated Text)
# ==========================================
dashboard_bg = """
    <style>
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at center, #4B2C85 0%, #1A0B2E 100%) !important;
    }
    section[data-testid="stSidebar"] { display: none !important; }
    div[data-testid="stSidebarNav"] { display: none !important; }

    /* ANIMATED WELCOME TEXT */
    .welcome-text {
        font-family: 'Inter', sans-serif;
        font-size: 8vw;
        font-weight: 900;
        text-align: center;
        letter-spacing: -2px;
        margin-top: 5vh;
        display: block;
        width: 90%;
        margin-left: 5%;
        paint-order: stroke fill;
        -webkit-text-stroke: 0.04em rgba(255,255,255,0.5);
        stroke-linecap: round;
        stroke-linejoin: round;
        background: linear-gradient(90deg, #FFFFFF, #D1B3FF, #FFFFFF);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 3s linear infinite, float 4s ease-in-out infinite, glow 2s ease-in-out infinite alternate;
    }

    @keyframes shine { to { background-position: 200% center; } }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-15px); }
    }
    @keyframes glow {
        from { text-shadow: 0 0 10px rgba(255,255,255,0.2); }
        to { text-shadow: 0 0 30px rgba(209, 179, 255, 0.6), 0 0 10px rgba(255,255,255,0.4); }
    }

    .sub-tagline {
        color: #D1B3FF;
        font-size: 1.4rem;
        text-align: center;
        font-weight: 400;
        letter-spacing: 3px;
        margin-bottom: 40px;
        opacity: 0.8;
    }
    </style>
"""

chatbot_bg = """
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
    }
    </style>
"""

if st.session_state.page_view == "dashboard":
    st.markdown(dashboard_bg, unsafe_allow_html=True)
else:
    st.markdown(chatbot_bg, unsafe_allow_html=True)

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    
    /* DASHBOARD BUTTONS STYLE - LIGHT PINK MASSIVE */
    div.stButton > button[help="dash_tab_btn"] {{
        width: 100% !important;
        height: 320px !important; 
        font-size: 2.2rem !important; 
        font-weight: 900 !important;
        border-radius: 50px !important; 
        background: linear-gradient(145deg, #FFB6C1 0%, #FF69B4 100%) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 25px 50px rgba(0,0,0,0.3) !important;
        transition: 0.4s all ease !important;
        color: white !important;
        text-transform: uppercase;
        letter-spacing: 2px;
    }}

    div.stButton > button[help="dash_tab_btn"]:hover {{
        transform: translateY(-10px) !important;
        filter: brightness(1.1);
    }}

    /* SIDEBAR BUTTONS */
    section[data-testid="stSidebar"] .stButton>button {{
        background: linear-gradient(135deg, #8A63FF 0%, #6A3DE8 100%) !important;
        color: white !important;
    }}

    .mini-menu-list {{
        background-color: white; border: 1px solid #DDD; border-radius: 8px; padding: 10px;
        position: absolute; left: 40px; top: 0px; z-index: 999;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 150px;
    }}

    .signature-box-3d {{ margin-top: 40px; padding: 18px; border-radius: 12px; background: #2C2C2C; border-bottom: 4px solid #1A1A1A; box-shadow: 0 10px 20px rgba(0,0,0,0.2); text-align: center; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. SIDEBAR LOGIC
# ==========================================
if st.session_state.page_view != "dashboard":
    with st.sidebar:
        if st.button("☰", key="hamburger_icon"):
            st.session_state.show_mini_menu = not st.session_state.show_mini_menu
            st.rerun()
        
        if st.session_state.show_mini_menu:
            st.markdown('<div class="mini-menu-list">', unsafe_allow_html=True)
            if st.button("📊 Dashboard", use_container_width=True, key="dash_link"):
                st.session_state.page_view = "dashboard"
                st.session_state.show_mini_menu = False
                st.rerun()
            if st.button("⚙️ Settings", use_container_width=True, key="settings_link"):
                st.toast("Settings coming soon!")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<h2 style='color: #1A1A1A; text-align: center; margin-top: 10px;'>Tool Section</h2>", unsafe_allow_html=True)
        
        if st.button("New Chat"):
            st.session_state.sessions[f"New Session {len(st.session_state.sessions)+1}"] = []
            st.rerun()

        st.button("Chat History 🕑")
        st.button("University Tools ⚙️")
        st.button("Academics 📚")
        st.button("Admission - Fee 💸")
        
        st.markdown(f"""<div class="signature-box-3d"><p style="color:#A0A0A0; font-size:0.8rem; margin:0;">Designed by</p><h3 style="color:#FFFFFF; margin:5px 0 0 0;">SUMIT CHAUDHARY</h3></div>""", unsafe_allow_html=True)

# ==========================================
# 5. MAIN CONTENT ROUTING
# ==========================================

# --- VIEW: DASHBOARD ---
if st.session_state.page_view == "dashboard":
    st.markdown('<div class="welcome-text">welcome</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-tagline">THE FUTURE OF MNIT IS HERE. PICK YOUR GATEWAY.</div>', unsafe_allow_html=True)
    
    # 5 Columns layout to center the 3 tabs [Buffer, Tab1, Tab2, Tab3, Buffer]
    # Ratio: 0.5 buffer, 2 for each tab, 0.5 buffer
    l_spacer, c1, c2, c3, r_spacer = st.columns([0.5, 2, 2, 2, 0.5])
    
    with c1:
        if st.button("AskMNIT", help="dash_tab_btn", key="dash_ask"):
            st.session_state.page_view = "chatbot"
            st.rerun()
            
    with c2:
        if st.button("Coming Soon", help="dash_tab_btn", key="dash_soon"):
            st.toast("Stay tuned!")

    with c3:
        if st.button("New Tab", help="dash_tab_btn", key="dash_new"):
            st.toast("Module locked.")

# --- VIEW: CHATBOT ---
else:
    st.markdown(f"""<div style="margin-top: 15vh; text-align: center;"><div style="color: #1A1A1A; font-weight: 800; font-size: 3.5rem;">AskMNIT</div><div style="color: #666666; font-size: 1.2rem;">Your Professional AI Assistant</div></div>""", unsafe_allow_html=True)

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
