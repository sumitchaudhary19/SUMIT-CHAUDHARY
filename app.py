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
# 3. CSS (Dynamic Background & Navigation)
# ==========================================
# Gradient background pattern matching the provided image for Dashboard
dashboard_bg = """
    <style>
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at center, #4B2C85 0%, #1A0B2E 100%) !important;
    }
    section[data-testid="stSidebar"] { display: none !important; }
    div[data-testid="stSidebarNav"] { display: none !important; }
    </style>
"""

chatbot_bg = """
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
    }
    </style>
"""

# Inject background based on view
if st.session_state.page_view == "dashboard":
    st.markdown(dashboard_bg, unsafe_allow_html=True)
else:
    st.markdown(chatbot_bg, unsafe_allow_html=True)

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    
    /* SIDEBAR STYLING */
    section[data-testid="stSidebar"] {{
        background-color: #F0F2F6 !important;
        border-right: 1px solid #DDDDDD !important;
    }}

    /* SHINY VIOLET MAIN TABS */
    .stButton>button {{
        width: 100% !important;
        background: linear-gradient(135deg, #8A63FF 0%, #6A3DE8 100%) !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 14px 20px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(138, 99, 255, 0.3) !important;
        border: none !important;
    }}

    /* DASHBOARD LARGE BUTTONS */
    div.stButton > button[title="dash_tab_btn"] {{
        height: 200px !important;
        font-size: 2.2rem !important;
        font-weight: 900 !important;
        border-radius: 30px !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }}

    /* MINI MENU POPUP */
    .mini-menu-list {{
        background-color: white; border: 1px solid #DDD; border-radius: 8px; padding: 10px;
        position: absolute; left: 40px; top: 0px; z-index: 999;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 150px;
    }}

    /* SIGNATURE BOX */
    .signature-box-3d {{ margin-top: 40px; padding: 18px; border-radius: 12px; background: #2C2C2C; border-bottom: 4px solid #1A1A1A; box-shadow: 0 10px 20px rgba(0,0,0,0.2); text-align: center; }}
    
    .title-container-empty {{ margin-top: 15vh; transition: 0.5s; }}
    .title-container-active {{ margin-top: 2vh; scale: 0.7; transition: 0.5s; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. SIDEBAR (Only visible when NOT in Dashboard)
# ==========================================
if st.session_state.page_view != "dashboard":
    with st.sidebar:
        # Hamburger Menu
        if st.button("☰", key="hamburger_icon"):
            st.session_state.show_mini_menu = not st.session_state.show_mini_menu
            st.rerun()
        
        if st.session_state.show_mini_menu:
            st.markdown('<div class="mini-menu-list">', unsafe_allow_html=True)
            if st.button("📊 Dashboard", use_container_width=True):
                st.session_state.page_view = "dashboard"
                st.session_state.show_mini_menu = False
                st.rerun()
            if st.button("⚙️ Settings", use_container_width=True):
                st.toast("Settings coming soon!")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<h2 style='color: #1A1A1A; text-align: center;'>Tool Section</h2>", unsafe_allow_html=True)
        
        if st.button("New Chat"):
            st.session_state.sessions[f"New Session {len(st.session_state.sessions)+1}"] = []
            st.rerun()

        st.button("Chat History 🕑")
        st.button("University Tools ⚙️")
        
        if st.button("Academics 📚"):
            st.session_state.show_acad_menu = not st.session_state.show_acad_menu
            st.rerun()
            
        st.button("Admission - Fee 💸")
        
        st.markdown(f"""<div class="signature-box-3d"><p style="color:#A0A0A0; font-size:0.8rem; margin:0;">Designed by</p><h3 style="color:#FFFFFF; margin:5px 0 0 0;">SUMIT CHAUDHARY</h3></div>""", unsafe_allow_html=True)

# ==========================================
# 5. MAIN CONTENT ROUTING
# ==========================================

# --- VIEW: DASHBOARD ---
if st.session_state.page_view == "dashboard":
    st.markdown("<div style='height: 30vh;'></div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([0.5, 2, 2, 0.5])
    
    with c2:
        if st.button("AskMNIT", help="dash_tab_btn", key="dash_ask"):
            st.session_state.page_view = "chatbot"
            st.rerun()
            
    with c3:
        if st.button("Coming Soon", help="dash_tab_btn", key="dash_soon"):
            st.toast("Stay tuned!")

# --- VIEW: CHATBOT ---
else:
    title_class = "title-container-empty" if is_chat_empty else "title-container-active"
    st.markdown(f"""<div class="{title_class}"><div style="color: #1A1A1A; font-weight: 800; text-align: center; font-size: 3.5rem;">AskMNIT</div><div style="text-align: center; color: #666666; font-size: 1.2rem;">Your Professional AI Assistant</div></div>""", unsafe_allow_html=True)

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
