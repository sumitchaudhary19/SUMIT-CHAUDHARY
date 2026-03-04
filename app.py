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

# New Session State for Pinned Sessions
if "pinned_sessions" not in st.session_state:
    st.session_state.pinned_sessions = []

# DYNAMIC UI LOGIC: Check if chat is empty to center the Search Bar
is_chat_empty = len(st.session_state.sessions[st.session_state.current_chat]) == 0

if is_chat_empty:
    chat_pos_css = "top: 45vh !important; transform: translate(-50%, -50%) !important;"
else:
    chat_pos_css = "bottom: 30px !important; transform: translateX(-50%) !important;"

# ==========================================
# 3. ADVANCED CSS (Dark Theme, 3-Dot Menu & Premium Gemini Bar)
# ==========================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Global Dark Grey Background */
    html, body, [class*="css"], [data-testid="stAppViewContainer"] {{ 
        font-family: 'Inter', sans-serif; 
        background-color: #1A1A1A !important; 
        color: #E0E0E0 !important; 
    }}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
    [data-testid="stHeader"] {{ background-color: transparent !important; }}
    
    /* 🔴 PITCH BLACK BOTTOM SECTION */
    [data-testid="stBottom"] {{
        background-color: transparent !important; 
        border-top: none !important; 
        padding-top: 20px !important;
    }}
    [data-testid="stBottom"] > div {{ background-color: transparent !important; }}
    
    /* 🛑 KILLING THE WHITE GHOST SEARCH BAR */
    div[data-testid="stChatInput"], div.stChatInput {{
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    /* =========================================
       CHAT MESSAGES ALIGNMENT & WIDTH
       ========================================= */
    [data-testid="stChatMessageContainer"] {{
        padding-left: 0 !important; padding-right: 0 !important;
    }}
    
    div[data-testid="stChatMessage"] {{ 
        border-radius: 12px; padding: 15px 20px; margin-bottom: 20px;
    }}
    
    /* 🔵 USER (Odd) -> Aligned EXACT RIGHT, 75% Width */
    div[data-testid="stChatMessage"]:nth-child(odd) {{ 
        background-color: #2C2C2C !important; 
        border: 1px solid #444 !important; 
        width: fit-content !important; 
        max-width: 75% !important; 
        margin-left: auto !important; 
        margin-right: 0 !important;
    }}
    
    /* 🟢 CHATBOT (Even) -> Aligned EXACT LEFT, FULL WIDTH (100%) */
    div[data-testid="stChatMessage"]:nth-child(even) {{ 
        background-color: #212121 !important; 
        border: 1px solid #333 !important; 
        width: 100% !important; 
        max-width: 100% !important; 
        margin-right: auto !important; 
        margin-left: 0 !important; 
    }}
    
    /* CHAT TEXT COLOR */
    div[data-testid="stChatMessageContent"] p {{
        color: #B0B0B0 !important; font-size: 1rem; line-height: 1.6;
    }}

    /* =========================================
       SIDEBAR & LIGHT GREY BUTTONS
       ========================================= */
    section[data-testid="stSidebar"] {{ background-color: #111111 !important; border-right: 1px solid #333 !important; }}
    
    .stButton>button {{ 
        width: 100%; text-align: left; background-color: #D3D3D3 !important; 
        border: 1px solid #999 !important; padding: 10px 15px; border-radius: 8px; 
        font-weight: 600; color: #000000 !important; transition: 0.2s; 
    }}
    .stButton>button:hover {{ background-color: #BDBDBD !important; }}
    
    .new-chat-btn>div>button {{ 
        background-color: #D3D3D3 !important; color: #000000 !important; 
        justify-content: center; font-weight: 700; margin-bottom: 20px; border-radius: 8px; 
        border: 1px solid #999 !important; 
    }}

    /* ✨ NEW E-BOOKS TAB STYLING */
    .ebook-btn button {{
        background-color: #E0E0E0 !important; /* Light Grey Background */
        color: #333333 !important; /* Dark Grey Text */
        justify-content: center !important;
        font-weight: 800 !important;
        margin-top: 15px !important;
        border: 1px solid #AAAAAA !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
    }}
    .ebook-btn button:hover {{
        background-color: #CCCCCC !important;
        color: #111111 !important;
    }}

    /* =========================================
       ✨ PIN STICKER STYLING
       ========================================= */
    .pin-sticker {{
        position: absolute;
        top: -4px;
        left: -4px;
        font-size: 1.2rem;
        z-index: 100;
        filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.6));
        pointer-events: none; /* Allows clicking the button underneath */
    }}

    /* =========================================
       ✨ 3-DOT POPOVER STYLING (SIDEBAR)
       ========================================= */
    [data-testid="stSidebar"] [data-testid="stPopover"] > button {{
        background-color: transparent !important;
        border: none !important;
        color: #555555 !important; /* Dark Grey 3 dots */
        font-size: 1.5rem !important;
        font-weight: 900 !important;
        line-height: 1 !important;
        padding: 0 !important;
        box-shadow: none !important;
    }}
    [data-testid="stSidebar"] [data-testid="stPopover"] > button:hover {{
        color: #AAAAAA !important;
        background-color: transparent !important;
    }}
    [data-testid="stSidebar"] [data-testid="stPopover"] > button svg {{
        display: none !important; /* Hide default arrow */
    }}

    /* Popover Menu Body */
    [data-testid="stPopoverBody"] {{
        background-color: #E0E0E0 !important; /* Light Grey Background */
        border: 1px solid #CCCCCC !important;
        border-radius: 12px !important; /* Square-shaped with rounded corners */
        padding: 5px !important;
        width: 220px !important;
    }}

    /* Options inside the Popover */
    [data-testid="stPopoverBody"] .stButton > button {{
        background-color: transparent !important;
        border: none !important;
        color: #333333 !important; /* Dark Grey Text */
        text-align: left !important;
        font-weight: 600 !important;
        box-shadow: none !important;
        padding: 8px 10px !important;
        margin: 2px 0 !important;
        border-radius: 8px !important;
        width: 100% !important;
        display: flex !important;
        justify-content: flex-start !important;
    }}
    [data-testid="stPopoverBody"] .stButton > button:hover {{
        background-color: #CCCCCC !important; /* Highlight on hover */
        color: #000000 !important;
    }}

    .signature-box {{ margin-top: 40px; margin-bottom: 20px; padding: 15px; border-radius: 8px; background: #2C2C2C; border: 1px solid #444; text-align: center; }}
    .signature-box p {{ margin: 0; font-size: 0.75rem; color: #AAAAAA; text-transform: uppercase; letter-spacing: 1px; }}
    .signature-box h3 {{ margin: 5px 0 0 0; font-size: 1.1rem; color: #E0E0E0; font-weight: 700; }}

    /* =========================================
       ✨ NEW GEMINI MINIMALIST SEARCH BAR
       ========================================= */
    div[data-testid="stChatInputContainer"] {{ 
        position: fixed !important;
        {chat_pos_css} 
        left: 50% !important;
        width: 90vw !important;
        max-width: 800px !important; 
        min-height: 60px !important; 
        border-radius: 50px !important; 
        background-color: #F0F4F9 !important; 
        border: 1px solid #E0E4E9 !important; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
        padding: 5px 10px !important;
        z-index: 9999 !important;
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) !important; 
    }}
    
    div[data-testid="stChatInputContainer"]:focus-within {{
        background-color: #FFFFFF !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15) !important;
    }}

    div[data-testid="stChatInputContainer"] textarea {{ 
        color: #1F1F1F !important; 
        -webkit-text-fill-color: #1F1F1F !important; 
        font-size: 1.15rem !important; 
        font-weight: 400 !important;
        padding-left: 20px !important; 
        padding-top: 14px !important;
        padding-right: 60px !important; 
        background-color: transparent !important;
        min-height: 50px !important; 
    }}
    div[data-testid="stChatInputContainer"] textarea::placeholder {{
        color: #747775 !important;
        -webkit-text-fill-color: #747775 !important;
    }}
    div[data-testid="stChatInputContainer"] textarea:-webkit-autofill {{
        -webkit-box-shadow: 0 0 0 1000px #F0F4F9 inset !important;
        -webkit-text-fill-color: #1F1F1F !important;
    }}

    /* =========================================
       SEND BUTTON (Paper Plane Icon)
       ========================================= */
    div[data-testid="stChatInputContainer"] button[data-testid="stChatInputSubmit"] {{
        background-color: transparent !important;
        border-radius: 50% !important;
        border: none !important;
        position: absolute !important;
        width: 45px !important; height: 45px !important;
        right: 10px !important; 
        bottom: 7px !important; 
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%231F1F1F"><path d="M3 20v-6l8-2-8-2V4l19 8z"/></svg>') !important;
        background-size: 24px !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        transition: background-color 0.2s ease !important;
        z-index: 10001 !important;
    }}
    div[data-testid="stChatInputContainer"] button[data-testid="stChatInputSubmit"] svg,
    div[data-testid="stChatInputContainer"] button[data-testid="stChatInputSubmit"]::after {{ 
        display: none !important; 
    }}
    div[data-testid="stChatInputContainer"] button[data-testid="stChatInputSubmit"]:hover {{ 
        background-color: #E2E7EB !important; 
    }}
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
        st.markdown("<h3 style='color: #60A5FA; font-weight: 800; text-align: center;'>logo.png AskMNIT</h3>", unsafe_allow_html=True)

    st.markdown("<div class='new-chat-btn'>", unsafe_allow_html=True)
    if st.button("➕ New Session"):
        chat_id = f"Session {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[chat_id] = []
        st.session_state.current_chat = chat_id
        st.session_state.pending_generation = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<p style='color: #BBBBBB; font-size: 0.8rem; font-weight: 600; margin-top: 10px;'>Chat History</p>", unsafe_allow_html=True)
    
    # 🔥 CHAT HISTORY WITH 3-DOT MENU AND PIN LOGIC
    for chat_name in reversed(list(st.session_state.sessions.keys())):
        col1, col2 = st.columns([85, 15])
        
        with col1:
            # Show red pin sticker if the session is pinned
            if chat_name in st.session_state.pinned_sessions:
                st.markdown('<div class="pin-sticker">📍</div>', unsafe_allow_html=True)
                
            if st.button(f"💬 {chat_name}", key=f"btn_{chat_name}", use_container_width=True):
                st.session_state.current_chat = chat_name
                st.session_state.pending_generation = False
                st.rerun()
                
        with col2:
            with st.popover("⋮"): # 3 Vertical Dots
                if st.button("📂 Open this session", key=f"opn_{chat_name}", use_container_width=True):
                    st.session_state.current_chat = chat_name
                    st.session_state.pending_generation = False
                    st.rerun()
                
                # Toggle Pin/Unpin
                pin_label = "🔕 Unpin this session" if chat_name in st.session_state.pinned_sessions else "📌 Pin this session"
                if st.button(pin_label, key=f"pin_{chat_name}", use_container_width=True):
                    if chat_name in st.session_state.pinned_sessions:
                        st.session_state.pinned_sessions.remove(chat_name)
                    else:
                        st.session_state.pinned_sessions.append(chat_name)
                    st.rerun()
                
                # Delete Session
                if st.button("🗑️ Delete this session", key=f"del_{chat_name}", use_container_width=True):
                    del st.session_state.sessions[chat_name]
                    if chat_name in st.session_state.pinned_sessions:
                        st.session_state.pinned_sessions.remove(chat_name)
                    
                    # If active chat is deleted, switch to a new session
                    if st.session_state.current_chat == chat_name:
                        st.session_state.current_chat = "New Session"
                        if "New Session" not in st.session_state.sessions:
                            st.session_state.sessions["New Session"] = []
                    st.rerun()
            
    # ==========================================
    # 🔥 NEW E-BOOKS TAB
    # ==========================================
    st.markdown("<div class='ebook-btn'>", unsafe_allow_html=True)
    if st.button("E-BOOKS 😎", key="ebooks_tab"):
        st.toast("📚 E-BOOKS Section is coming soon!")
    st.markdown("</div>", unsafe_allow_html=True)
            
    st.markdown("---")
    st.markdown("""
        <div class="signature-box">
            <p>Architected by</p>
            <h3>SUMIT CHAUDHARY</h3>
            <p style="font-size: 0.6rem; margin-top: 5px;">Enterprise AI v6.0</p>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 5. MAIN CHAT LOGIC
# ==========================================
if is_chat_empty:
    st.markdown("<h1 style='color: #FFFFFF; font-weight: 800; text-align: center; font-size: 3rem; margin-top: 5vh;'>AskMNIT</h1>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; color: #BBBBBB; font-weight: 500; margin-bottom: 30px; font-size: 1.2rem;'>Your Professional AI Assistant</div>", unsafe_allow_html=True)

st.markdown('<div data-testid="stChatMessageContainer">', unsafe_allow_html=True)

for message in st.session_state.sessions[st.session_state.current_chat]:
    avatar_icon = "user.png" if message["role"] == "user" else "logo.png"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 6. CHAT INPUT & AI GENERATION
# ==========================================
if prompt := st.chat_input("Ask me anything..."):
    
    curr_chat = st.session_state.current_chat
    if curr_chat.startswith("New Session") and len(st.session_state.sessions[curr_chat]) == 0:
        new_name = prompt[:20] + "..."
        st.session_state.sessions[new_name] = st.session_state.sessions.pop(curr_chat)
        st.session_state.current_chat = new_name

    st.session_state.sessions[st.session_state.current_chat].append({"role": "user", "content": prompt})
    st.session_state.pending_generation = True
    st.rerun()

# Processing AI generation
if st.session_state.pending_generation:
    prompt = st.session_state.sessions[st.session_state.current_chat][-1]["content"]
    
    with st.chat_message("assistant", avatar="logo.png"):
        instructions = """
        You are 'AskMNIT', an exceptionally intelligent and professional AI assistant for MNIT.
        1. You possess universal knowledge. You can answer ANY question about coding, science, history, daily life, or business perfectly.
        2. Keep your tone professional, highly accurate, and helpful. Use clear formatting.
        3. YOU ARE AN AI. Do not claim to be human.
        4. IF AND ONLY IF asked about your creator, owner, or who made you, reply exactly with: "I was architected and developed by SUMIT CHAUDHARY."
        """
        
        try:
            def generate_response():
                stream = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": instructions},
                        {"role": "user", "content": prompt}
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
            st.error(f"System Fault: {str(e)}")
            
    st.session_state.pending_generation = False
