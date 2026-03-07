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
# 3. CSS (UI & Static Dark Grey Subject Tabs)
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
    [data-testid="stHeader"] {{ display: none !important; }}
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
    }}

    /* --- DARK GREY SUBJECT TABS --- */
    /* Applied to Syllabus List for Fixed Color & No Hover */
    div.stButton > button[title="subject_tab"], div[data-testid="stLinkButton"] > a[title="subject_tab"] {{
        background-color: #333333 !important;
        background: #333333 !important;
        color: white !important;
        border: none !important;
        text-align: left !important;
        padding: 12px 15px !important;
        margin-bottom: 8px !important;
        font-size: 1.1rem !important;
        border-radius: 8px !important;
        width: 100% !important;
        box-shadow: none !important;
        transition: none !important;
    }}

    div.stButton > button[title="subject_tab"]:hover, 
    div[data-testid="stLinkButton"] > a[title="subject_tab"]:hover {{
        background-color: #333333 !important;
        color: white !important;
    }}

    /* CHAT STYLING */
    [data-testid="stChatMessage"] p {{ font-size: 1.25rem !important; line-height: 1.6 !important; }}
    div[data-testid="stChatInput"] {{ width: 650px !important; margin: 0 auto !important; position: fixed !important; bottom: 20px !important; left: 0; right: 0; z-index: 999; }}
    div[data-testid="stChatInput"] > div {{ background-color: #FFFFFF !important; border: 1px solid #DDDDDD !important; border-radius: 15px !important; height: 80px !important; }}
    div[data-testid="stChatInput"] textarea {{ background-color: #FFFFFF !important; font-size: 1.2rem; height: 80px !important; padding: 15px 60px 15px 25px !important; }}
    
    /* DIALOG STYLING */
    div[data-testid="stDialog"] div[role="dialog"] {{ background-color: #2C2C2C !important; border-radius: 15px !important; text-align: center; }}
    div[data-testid="stDialog"] h2, div[data-testid="stDialog"] p {{ color: white !important; }}

    .title-container-empty {{ margin-top: 20vh; transition: 0.5s; }}
    .title-container-active {{ margin-top: 2vh; scale: 0.7; transition: 0.5s; }}
    .signature-box {{ margin-top: 40px; padding: 15px; border-radius: 8px; background: #EAECEF; border: 1px solid #CCC; text-align: center; }}
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
    st.write("Recent Chats:")
    for session_key, messages in st.session_state.sessions.items():
        display_name = (messages[0]["content"][:30] + '...') if messages else session_key
        if st.button(display_name, key=f"hist_{session_key}", use_container_width=True):
            st.session_state.current_chat = session_key
            st.rerun()

@st.dialog("Syllabus Subjects 📖")
def open_syllabus_list():
    st.markdown('<p style="color:#BBB; font-size:0.9rem;">Click a subject to view PDF</p>', unsafe_allow_html=True)
    
    # DATA STRUCTURES PDF LINK
    ds_link = "https://drive.google.com/file/d/1I8D1-DIZHkJNgle9WtCh5pTt7OTkAtJz/preview"
    
    # Subject Tabs as Buttons/Links
    st.link_button("Data Structures", ds_link, use_container_width=True, help="subject_tab")
    
    other_subjects = ["Digital Electronics", "OOP (C++ / Java)", "Discrete Mathematics", "COA", "Data Structures Lab"]
    for sub in other_subjects:
        if st.button(sub, use_container_width=True, help="subject_tab"):
            st.toast(f"Syllabus for {sub} coming soon!")

# ==========================================
# 5. SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color: #1A1A1A; text-align: center;'>Tools</h2>", unsafe_allow_html=True)
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
        if st.button("Syllabus", use_container_width=True): open_syllabus_list()
        if st.button("Notes", use_container_width=True): st.toast("Coming soon!")
        if st.button("PYQs", use_container_width=True): st.toast("Coming soon!")
    
    st.markdown("<div style='margin-top: 30px; border-top: 1px solid #DDD;'></div>", unsafe_allow_html=True)
    st.markdown("""<div class="signature-box"><p style="color:#666; font-size:0.75rem; margin:0;">Architected by</p><h3 style="color:#1A1A1A; margin:0;">SUMIT CHAUDHARY</h3></div>""", unsafe_allow_html=True)

# ==========================================
# 6. MAIN CHAT
# ==========================================
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
            def generate_response():
                stream = client.chat.completions.create(
                    messages=[{"role": "system", "content": "You are 'AskMNIT', an assistant for MNIT Jaipur students."},
                              {"role": "user", "content": user_query}],
                    model="llama-3.3-70b-versatile", stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content: yield chunk.choices[0].delta.content
            response_text = st.write_stream(generate_response())
            st.session_state.sessions[st.session_state.current_chat].append({"role": "assistant", "content": response_text})
        except Exception as e:
            st.error(f"Error: {str(e)}")
    st.session_state.pending_generation = False
