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
if "show_acad_menu" not in st.session_state:
    st.session_state.show_acad_menu = False

is_chat_empty = len(st.session_state.sessions[st.session_state.current_chat]) == 0

# ==========================================
# 3. CSS (UI & Custom Styling)
# ==========================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"], [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        font-family: 'Inter', sans-serif;
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
    }}
    
    [data-testid="stMain"] {{ background-color: #FFFFFF !important; }}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
    [data-testid="stBottom"] {{ background-color: #FFFFFF !important; border-top: none !important; }}

    section[data-testid="stSidebar"] {{
        background-color: #F0F2F6 !important;
        border-right: 1px solid #DDDDDD !important;
        width: 320px !important;
    }}

    /* SHINY VIOLET MAIN TABS */
    .stButton>button, [data-testid="stLinkButton"] > a {{
        width: 100% !important;
        min-width: 250px !important;
        background: linear-gradient(135deg, #8A63FF 0%, #6A3DE8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 14px 20px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(138, 99, 255, 0.3) !important;
        transition: 0.3s all ease !important;
        display: block !important;
        margin-bottom: 12px !important;
    }}

    /* --- SUB-TABS (Dropdown Style) --- */
    div.stButton > button[title="sub_tab"] {{
        width: 85% !important;
        min-width: 0 !important;
        margin-left: 15% !important;
        padding: 10px 15px !important;
        font-size: 0.95rem !important;
        border-radius: 8px !important;
        background: linear-gradient(135deg, #8A63FF 0%, #6A3DE8 100%) !important;
    }}

    /* --- INCREASED CHAT TEXT FONT SIZE --- */
    [data-testid="stChatMessage"] p {{ font-size: 1.25rem !important; line-height: 1.6 !important; }}

    /* --- PURE WHITE SEARCH BAR --- */
    div[data-testid="stChatInput"] > div {{
        background-color: #FFFFFF !important; 
        border: 1px solid #DDDDDD !important;
        border-radius: 15px !important;
        height: 80px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08) !important;
    }}

    /* --- DESIGNED BY BOX (3D DARK GREY EFFECT) --- */
    .signature-box-3d {{
        margin-top: 40px;
        padding: 18px;
        border-radius: 12px;
        background: #2C2C2C;
        border-bottom: 4px solid #1A1A1A; /* Shadow depth */
        box-shadow: 0 10px 20px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.1);
        text-align: center;
        transition: 0.3s;
    }}
    .signature-box-3d:hover {{
        transform: translateY(2px);
        border-bottom: 2px solid #1A1A1A;
        box-shadow: 0 5px 10px rgba(0,0,0,0.2);
    }}

    /* DIALOG STYLING */
    div[data-testid="stDialog"] div[role="dialog"] {{ background-color: #2C2C2C !important; border-radius: 15px !important; text-align: center; }}
    div[data-testid="stDialog"] h2, div[data-testid="stDialog"] p {{ color: white !important; }}

    .title-container-empty {{ margin-top: 20vh; transition: 0.5s; }}
    .title-container-active {{ margin-top: 2vh; scale: 0.7; transition: 0.5s; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. DIALOGS
# ==========================================
@st.dialog("University Tools")
def open_uni_tools():
    st.write("Access MNIT Portals:")
    st.link_button("Class Schedule 📅", "https://www.mnit.ac.in/TimeTable/", use_container_width=True)
    st.link_button("ERP Portal 🌐", "https://mniterp.org/mniterp/", use_container_width=True)

@st.dialog("Chat History 🕑")
def open_chat_history():
    st.write("Pick a session:")
    for session_key, messages in st.session_state.sessions.items():
        display_name = (messages[0]["content"][:35] + "...") if messages else session_key
        if st.button(display_name, key=f"hist_{session_key}", use_container_width=True):
            st.session_state.current_chat = session_key
            st.rerun()

# ==========================================
# 5. SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color: #1A1A1A; text-align: center; margin-bottom: 25px;'>Tools</h2>", unsafe_allow_html=True)
    
    if st.button("➕ New Session"):
        new_id = f"New Session {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[new_id] = []
        st.session_state.current_chat = new_id
        st.rerun()

    if st.button("Chat History 🕑"):
        open_chat_history()

    if st.button("University Tools ⚙️"):
        open_uni_tools()

    if st.button("Academics 📚"):
        st.session_state.show_acad_menu = not st.session_state.show_acad_menu
        st.rerun()

    if st.session_state.show_acad_menu:
        if st.button("Syllabus", help="sub_tab"): st.toast("Syllabus clicked")
        if st.button("Notes", help="sub_tab"): st.toast("Notes clicked")
        if st.button("PYQs", help="sub_tab"): st.toast("PYQs clicked")
            
    if st.button("Admission - Fee 💸"):
        st.toast("Admission and Fee clicked")
    
    # --- UPDATED SIGNATURE TAB (3D DARK GREY) ---
    st.markdown("""
        <div class="signature-box-3d">
            <p style="color:#A0A0A0; font-size:0.8rem; margin:0; text-transform: uppercase; letter-spacing: 1px;">Designed by</p>
            <h3 style="color:#FFFFFF; margin:5px 0 0 0; font-weight:800; font-size:1.3rem; letter-spacing: 0.5px;">SUMIT CHAUDHARY</h3>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 6. MAIN CHAT
# ==========================================
title_class = "title-container-empty" if is_chat_empty else "title-container-active"
st.markdown(f"""
    <div class="{title_class}">
        <div style="color: #1A1A1A; font-weight: 800; text-align: center; font-size: 3.5rem;">AskMNIT</div>
        <div style="text-align: center; color: #666666; font-size: 1.2rem;">Your Professional AI Assistant</div>
    </div>
""", unsafe_allow_html=True)

for message in st.session_state.sessions[st.session_state.current_chat]:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])

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
                    messages=[{"role": "system", "content": "You are 'AskMNIT', an assistant for MNIT Jaipur students."}
                    ,{"role": "user", "content": user_query}],
                    model="llama-3.3-70b-versatile", stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content: yield chunk.choices[0].delta.content
            response_text = st.write_stream(generate_response())
            st.session_state.sessions[st.session_state.current_chat].append({"role": "assistant", "content": response_text})
        except Exception as e:
            st.error(f"Error: {str(e)}")
    st.session_state.pending_generation = False
