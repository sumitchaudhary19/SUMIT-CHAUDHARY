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
if "show_mini_menu" not in st.session_state:
    st.session_state.show_mini_menu = False
if "page_view" not in st.session_state:
    st.session_state.page_view = "dashboard"

is_chat_empty = len(st.session_state.sessions[st.session_state.current_chat]) == 0

# ==========================================
# 3. CSS (Dynamic Layout & Lavender Theme)
# ==========================================
dashboard_style = """
    <style>
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at center, #4B2C85 0%, #1A0B2E 100%) !important;
    }
    
    /* ANIMATED WELCOME TEXT */
    .welcome-text {
        font-family: 'Inter', sans-serif;
        font-size: 8vw;
        font-weight: 900;
        text-align: center;
        letter-spacing: -2px;
        margin-top: 2vh;
        display: block;
        width: 100%;
        paint-order: stroke fill;
        -webkit-text-stroke: 0.04em rgba(255,255,255,0.5);
        stroke-linecap: round;
        stroke-linejoin: round;
        background: linear-gradient(90deg, #FFFFFF, #D1B3FF, #FFFFFF);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 3s linear infinite, float 4s ease-in-out infinite;
    }

    /* LEFT ALIGNED SUBTEXT */
    .dashboard-label {
        font-family: 'Inter', sans-serif;
        font-size: 2rem;
        font-weight: 400;
        color: #D1B3FF;
        text-align: left;
        margin-left: 5%;
        margin-top: 20px;
        margin-bottom: 20px;
        opacity: 0.8;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    @keyframes shine { to { background-position: 200% center; } }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }

    /* CUSTOM LAVENDER TAB DESIGN */
    .tab-container {
        text-align: left;
        margin-left: 5%;
    }

    div.stButton > button[help="dash_tab_btn"] {
        width: 700px !important; /* Increased width for longer text */
        height: 200px !important; 
        font-size: 2.2rem !important; 
        font-weight: 800 !important;
        border-radius: 50px !important; 
        /* Match image_f6e318 color: Light Lavender Gradient */
        background: linear-gradient(145deg, #E0D4FF 0%, #C8B6FF 100%) !important;
        border: 2px solid rgba(255, 255, 255, 0.5) !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.4) !important;
        transition: 0.4s all ease !important;
        color: #1A0B2E !important; /* Dark text for light background */
        text-transform: uppercase;
        letter-spacing: 2px;
        display: block !important;
    }

    div.stButton > button[help="dash_tab_btn"]:hover {
        transform: scale(1.02) !important;
        filter: brightness(1.05);
        box-shadow: 0 30px 60px rgba(200, 182, 255, 0.3) !important;
    }

    section[data-testid="stSidebar"] { display: none !important; }
    div[data-testid="stSidebarNav"] { display: none !important; }
    header { display: none !important; }
    </style>
"""

chatbot_style = """
    <style>
    [data-testid="stAppViewContainer"] { background-color: #FFFFFF !important; }
    section[data-testid="stSidebar"] { background-color: #F0F2F6 !important; border-right: 1px solid #DDDDDD !important; display: block !important; }
    .stButton>button { background: linear-gradient(135deg, #8A63FF 0%, #6A3DE8 100%) !important; color: white !important; border-radius: 10px !important;}
    .mini-menu-list { background-color: white; border: 1px solid #DDD; border-radius: 8px; padding: 10px; position: absolute; left: 40px; top: 0px; z-index: 999; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 150px; }
    .signature-box-3d { margin-top: 40px; padding: 18px; border-radius: 12px; background: #2C2C2C; border-bottom: 4px solid #1A1A1A; box-shadow: 0 10px 20px rgba(0,0,0,0.2); text-align: center; }
    </style>
"""

if st.session_state.page_view == "dashboard":
    st.markdown(dashboard_style, unsafe_allow_html=True)
else:
    st.markdown(chatbot_style, unsafe_allow_html=True)

# ==========================================
# 4. SIDEBAR LOGIC (Only in Chatbot View)
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
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<h2 style='color: #1A1A1A; text-align: center;'>Tool Section</h2>", unsafe_allow_html=True)
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
if st.session_state.page_view == "dashboard":
    st.markdown('<div class="welcome-text">welcome</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-label">your personal dashboard</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    col_dash, col_empty = st.columns([1.5, 1]) 
    with col_dash:
        # Renamed and color-matched button
        if st.button("ASKMNIT - YOUR PERSONAL AI ASSISTANT", help="dash_tab_btn", key="dash_ask"):
            st.session_state.page_view = "chatbot"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown(f"""<div style="margin-top: 10vh; text-align: center;"><div style="color: #1A1A1A; font-weight: 800; font-size: 3.5rem;">AskMNIT</div><div style="color: #666666; font-size: 1.2rem;">Your Professional AI Assistant</div></div>""", unsafe_allow_html=True)

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
