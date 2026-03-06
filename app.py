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

is_chat_empty = len(st.session_state.sessions[st.session_state.current_chat]) == 0

# ==========================================
# 3. CSS (Suggested Pills & Layout)
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

    /* --- SIDEBAR --- */
    button[data-testid="sidebar-button-container"] {{ display: none !important; }}
    [data-testid="collapsedControl"] {{ display: none !important; }}

    /* --- STICKY HEADER --- */
    .sticky-header-container {{
        position: fixed;
        top: 0; left: 320px; right: 0;
        height: 140px;
        background-color: #FFFFFF;
        z-index: 1000;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
    }}

    /* --- SUGGESTED PILLS STYLING --- */
    .suggestion-container {{
        position: fixed;
        bottom: 110px; /* Right above the search bar */
        left: 320px; right: 0;
        display: flex; justify-content: center; gap: 10px;
        z-index: 997;
    }}

    /* Targetting only the suggestion buttons to make them white pills */
    div.stButton > button[key^="pill_"] {{
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
        border: 1px solid #DDDDDD !important;
        border-radius: 50px !important; /* Pill Shape */
        padding: 8px 20px !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
        width: auto !important;
        min-width: unset !important;
    }}

    div.stButton > button[key^="pill_"]:hover {{
        background-color: #F8F9FA !important;
        border-color: #8A63FF !important;
    }}

    /* --- CHAT AREA --- */
    [data-testid="stChatMessageContainer"] {{
        max-width: 800px !important;
        margin: 150px auto 120px auto !important;
    }}

    /* --- SIDEBAR TABS --- */
    section[data-testid="stSidebar"] {{
        background-color: #F0F2F6 !important;
        border-right: 1px solid #DDDDDD !important;
        width: 320px !important;
    }}

    .stButton>button {{
        width: 100% !important;
        background: linear-gradient(135deg, #8A63FF 0%, #6A3DE8 100%) !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 14px 20px !important;
        font-weight: 600 !important;
        margin-bottom: 12px !important;
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
        padding: 15px 60px 15px 95px !important;
        height: 80px !important;
    }}

    /* --- ICONS --- */
    .input-btn-base {{
        position: fixed; width: 32px; height: 32px;
        background-color: #333333 !important;
        border-radius: 50%; display: flex; align-items: center; justify-content: center;
        z-index: 1001; bottom: 44px !important;
    }}
    .plus-tab-ui {{ left: calc(50% - 310px); color: #FFFFFF !important; }}
    .mic-tab-ui {{ left: calc(50% - 270px); color: #A0A0A0 !important; }}

    div[data-testid="stChatInput"] button {{
        bottom: 22px !important; background-color: #1A1A1A !important; border-radius: 50% !important;
    }}
    div[data-testid="stChatInput"] button::after {{ content: ">"; color: white; }}
    div[data-testid="stChatInput"] button svg {{ display: none !important; }}

    .signature-box {{ margin-top: 40px; padding: 15px; border-radius: 8px; background: #EAECEF; border: 1px solid #CCC; text-align: center; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. DIALOGS
# ==========================================
@st.dialog("University Tools")
def open_uni_tools():
    st.write("Access MNIT Student Portals:")
    st.link_button("Class Schedule 📅", "https://www.mnit.ac.in/TimeTable/", use_container_width=True)
    st.link_button("ERP Portal 🌐", "https://mniterp.org/mniterp/", use_container_width=True)

@st.dialog("Chat History 🕑")
def open_chat_history():
    st.write("Pick a session:")
    for session_key, messages in st.session_state.sessions.items():
        display_name = messages[0]["content"][:30] + "..." if messages else session_key
        if st.button(display_name, key=f"btn_{session_key}", use_container_width=True):
            st.session_state.current_chat = session_key
            st.rerun()

# ==========================================
# 5. SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color: #1A1A1A; text-align: center; margin-bottom: 25px;'>Tools</h2>", unsafe_allow_html=True)
    if st.button("➕ New Session"):
        new_id = f"Session {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[new_id] = []
        st.session_state.current_chat = new_id
        st.rerun()
    if st.button("Chat History 🕑"):
        open_chat_history()
    if st.button("University Tools ⚙️"):
        open_uni_tools()
    st.markdown("<div style='margin-top: 30px; border-top: 1px solid #DDD;'></div>", unsafe_allow_html=True)
    st.markdown("""<div class="signature-box"><p style="color:#666; font-size:0.75rem; margin:0;">Architected by</p><h3 style="color:#1A1A1A; margin:0;">SUMIT CHAUDHARY</h3></div>""", unsafe_allow_html=True)

# ==========================================
# 6. HEADER
# ==========================================
st.markdown(f"""
    <div class="sticky-header-container">
        <div style="color: #1A1A1A; font-weight: 800; font-size: 3.5rem;">AskMNIT</div>
        <div style="color: #666666; font-size: 1.1rem; margin-top: -5px;">Your Professional AI Assistant</div>
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
# 8. SUGGESTED QUESTIONS (PILLS)
# ==========================================
if is_chat_empty:
    st.markdown('<div class="suggestion-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    
    suggestions = [
        "What is the class schedule?",
        "Explain Mineral Processing notes.",
        "Tell me about Metallurgy syllabus."
    ]
    
    # Render pills
    with st.container():
        # CSS handles the positioning of these columns implicitly via .suggestion-container
        c1, c2, c3 = st.columns([1,1,1])
        if c1.button(suggestions[0], key="pill_1"):
            st.session_state.sessions[st.session_state.current_chat].append({"role": "user", "content": suggestions[0]})
            st.session_state.pending_generation = True
            st.rerun()
        if c2.button(suggestions[1], key="pill_2"):
            st.session_state.sessions[st.session_state.current_chat].append({"role": "user", "content": suggestions[1]})
            st.session_state.pending_generation = True
            st.rerun()
        if c3.button(suggestions[2], key="pill_3"):
            st.session_state.sessions[st.session_state.current_chat].append({"role": "user", "content": suggestions[2]})
            st.session_state.pending_generation = True
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 9. CHAT INPUT & TABS UI
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
