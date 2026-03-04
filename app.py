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

# DYNAMIC UI LOGIC: Check if chat is empty to center the Search Bar
is_chat_empty = len(st.session_state.sessions[st.session_state.current_chat]) == 0

if is_chat_empty:
    chat_pos_css = "top: 45vh !important; transform: translate(-50%, -50%) !important;"
else:
    chat_pos_css = "bottom: 30px !important; transform: translateX(-50%) !important;"

# ==========================================
# 3. ADVANCED CSS (Dark Theme, User Right/Bot Left & Premium Gemini Bar)
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
        border-radius: 50px !important; /* Perfect Pill Shape */
        background-color: #F0F4F9 !important; /* Gemini Light Grey */
        border: 1px solid #E0E4E9 !important; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
        padding: 5px 10px !important;
        z-index: 9999 !important;
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) !important; 
    }}
    
    /* Glow on focus */
    div[data-testid="stChatInputContainer"]:focus-within {{
        background-color: #FFFFFF !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15) !important;
    }}

    /* Placeholder and Text Styling */
    div[data-testid="stChatInputContainer"] textarea {{ 
        color: #1F1F1F !important; 
        -webkit-text-fill-color: #1F1F1F !important; 
        font-size: 1.15rem !important; 
        font-weight: 400 !important;
        padding-left: 20px !important; 
        padding-top: 14px !important;
        padding-right: 140px !important; /* Room for Upload, Mic, and Send */
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
        background-color: #E2E7EB !important; /* Subtle hover effect */
    }}
    
    /* =========================================
       UPLOAD & MIC ICONS (Right Aligned)
       ========================================= */
    [data-testid="stHorizontalBlock"]:last-of-type {{
        position: fixed !important;
        {chat_pos_css} 
        left: 50% !important;
        width: 90vw !important;
        max-width: 800px !important; 
        height: 60px !important; 
        z-index: 10000 !important;
        pointer-events: none !important; 
        display: flex;
        align-items: center; 
        justify-content: flex-end; 
        padding-right: 60px; /* Aligns just left of Send button */
        gap: 5px !important;
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }}
    
    @media (min-width: 800px) {{
        [data-testid="stHorizontalBlock"]:last-of-type {{
            transform: { "translate(-50%, -50%)" if is_chat_empty else "translateX(-50%)" } !important;
        }}
    }}
    
    /* Common Icon Button Styling */
    [data-testid="stPopover"] > button {{
        pointer-events: auto !important; 
        width: 40px !important; height: 40px !important;
        background-color: transparent !important; 
        border: none !important;
        border-radius: 50% !important; 
        padding: 0 !important;
        box-shadow: none !important;
        background-size: 22px !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        transition: background-color 0.2s !important;
    }}
    
    /* 1. Upload/Gallery Icon */
    div[data-testid="column"]:nth-child(1) [data-testid="stPopover"] > button {{
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23444746"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>') !important;
    }}

    /* 2. Microphone Icon */
    div[data-testid="column"]:nth-child(2) [data-testid="stPopover"] > button {{
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23444746"><path d="M12 14c1.66 0 2.99-1.34 2.99-3L15 5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z"/></svg>') !important;
    }}
    
    [data-testid="stPopover"] > button p, [data-testid="stPopover"] > button div, [data-testid="stPopover"] > button svg {{ 
        display: none !important; 
    }}
    
    [data-testid="stPopover"] > button:hover {{ background-color: #E2E7EB !important; }}
    
    /* Popover Body */
    [data-testid="stPopoverBody"] {{
        background-color: #2C2C2C !important; border: 1px solid #444 !important;
        border-radius: 12px !important; padding: 15px !important; pointer-events: auto !important;
    }}
    </style>
""", unsafe_allow_html=True)

def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

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
    for chat_name in reversed(list(st.session_state.sessions.keys())):
        if st.button(f"💬 {chat_name}", key=f"btn_{chat_name}"):
            st.session_state.current_chat = chat_name
            st.session_state.pending_generation = False
            st.rerun()
            
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
# 6. ATTACHMENT & MIC TOOLS (Inside Search Bar)
# ==========================================
tool_col1, tool_col2 = st.columns([1, 1]) 
chat_img_bottom = None

with tool_col1:
    with st.popover(" "): # Upload Icon Popover
        st.markdown("<p style='font-size:0.9rem; font-weight:600; color:#FFFFFF; margin-bottom:5px;'>Upload context image:</p>", unsafe_allow_html=True)
        chat_img_bottom = st.file_uploader("", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed", key="bottom_img")
        if chat_img_bottom:
            st.success("✅ Attached!")

with tool_col2:
    with st.popover("  "): # Mic Icon Popover (double space to separate key)
        st.markdown("<p style='font-size:0.9rem; font-weight:600; color:#FFFFFF; margin-bottom:5px;'>🎤 Voice input coming soon!</p>", unsafe_allow_html=True)

final_vision_image = chat_img_bottom

# ==========================================
# 7. CHAT INPUT & AI GENERATION
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
                if final_vision_image:
                    base64_image = encode_image(final_vision_image)
                    stream = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": instructions},
                            {"role": "user", "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ]}
                        ],
                        model="llama-3.2-11b-vision-preview",
                        temperature=0.7,
                        stream=True
                    )
                else:
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
