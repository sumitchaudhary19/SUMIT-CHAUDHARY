import streamlit as st
import streamlit.components.v1 as components
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
    # Empty Chat -> Search Bar in Middle
    chat_pos_css = "top: 50% !important; margin-top: -25px !important;"
    tool_pos_css = "top: 50%; margin-top: -18px;"
else:
    # Chat Started -> Search Bar shifts to Bottom
    chat_pos_css = "bottom: 20px !important;"
    tool_pos_css = "bottom: 27px;"

# ==========================================
# 3. DARK MODE, Black Bottom, Chat Alignment & RGB SEARCH CSS
# ==========================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Global Backgrounds */
    html, body, [class*="css"], [data-testid="stAppViewContainer"] {{ 
        font-family: 'Inter', sans-serif; 
        background-color: #1A1A1A !important; 
        color: #E0E0E0 !important; 
    }}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
    [data-testid="stHeader"] {{ background-color: transparent !important; }}
    
    /* 🔴 PITCH BLACK BOTTOM SECTION */
    [data-testid="stBottom"] {{
        background-color: #000000 !important;
        border-top: 1px solid #222 !important;
    }}
    [data-testid="stBottom"] > div {{ background-color: #000000 !important; }}
    
    /* =========================================
       CHAT MESSAGES ALIGNMENT & STYLE
       ========================================= */
    div[data-testid="stChatMessage"] {{ 
        border-radius: 12px; padding: 15px 20px; 
        margin-bottom: 20px;
        width: fit-content !important; 
        max-width: 75% !important; 
    }}
    
    /* 🔵 USER (Odd) -> Aligned RIGHT */
    div[data-testid="stChatMessage"]:nth-child(odd) {{ 
        background-color: #2C2C2C !important; 
        margin-left: auto !important; 
        margin-right: 1rem !important;
    }}
    
    /* 🟢 CHATBOT (Even) -> Aligned EXACT LEFT */
    div[data-testid="stChatMessage"]:nth-child(even) {{ 
        background-color: #212121 !important; 
        margin-right: auto !important; 
        margin-left: 0 !important; /* Fixed left side chipka hua */
        border: 1px solid #333 !important;
    }}
    
    /* CHAT TEXT COLOR */
    div[data-testid="stChatMessageContent"] p {{
        color: #B0B0B0 !important;
        font-size: 1rem; line-height: 1.6;
    }}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{ background-color: #111111 !important; border-right: 1px solid #333 !important; }}
    .stButton>button {{ width: 100%; text-align: left; background-color: #D3D3D3; border: none; color: #000; font-weight: 600; }}
    .stButton>button:hover {{ background-color: #BDBDBD !important; color: #000 !important; }}
    .new-chat-btn>div>button {{ background-color: #D3D3D3; color: #000; font-weight: 700; }}

    /* =========================================
       FUTURISTIC RGB SEARCH BAR (MOTION)
       ========================================= */
       
    /* The main input container modification */
    div[data-testid="stChatInputContainer"] {{ 
        border: none !important;
        background-color: #2C2C2C !important; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important;
        max-width: 800px !important; margin: 0 auto !important;
        position: relative;
        overflow: hidden; /* For border effect */
        z-index: 1;
        {chat_pos_css} 
    }}

    /* Creating the rotating RGB border with pseudo-elements */
    div[data-testid="stChatInputContainer"]::before {{
        content: '';
        position: absolute;
        z-index: -2;
        left: -50%; top: -50%;
        width: 200%; height: 200%;
        background-color: #1A1A1A;
        background-repeat: no-repeat;
        background-size: 50% 50%, 50% 50%;
        background-position: 0 0, 100% 0, 100% 100%, 0 100%;
        /* RGB Gradient colors */
        background-image: linear-gradient(#1A1A1A, #1A1A1A), linear-gradient(#ff0000, #ff0000), linear-gradient(#1A1A1A, #1A1A1A), linear-gradient(#0000ff, #ff0000);
        background-image: conic-gradient(#ff0000, #ff00ff, #0000ff, #00ffff, #00ff00, #ffff00, #ff0000);
        animation: rotateRGB 4s linear infinite;
    }}

    @keyframes rotateRGB {{
        100% {{ transform: rotate(360deg); }}
    }}

    /* Inner box to hide excess rotating gradient */
    div[data-testid="stChatInputContainer"]::after {{
        content: '';
        position: absolute;
        z-index: -1;
        left: 3px; top: 3px;
        width: calc(100% - 6px); height: calc(100% - 6px);
        background: #2C2C2C;
        border-radius: 28px;
    }}
    
    /* Text input area adjustments */
    div[data-testid="stChatInputContainer"] textarea {{ 
        color: #FFFFFF !important; 
        font-weight: 500; 
        padding-right: 60px !important; /* Space for send button */
        background-color: transparent !important;
    }}
    
    /* Hiding default streamlit send icon to use custom Gemini style */
    div[data-testid="stChatInputContainer"] button[data-testid="stChatInputSubmit"] svg {{
        display: none !important;
    }}

    /* =========================================
       CUSTOM GEMINI-STYLE SEND BUTTON
       ========================================= */
    div[data-testid="stChatInputContainer"] button[data-testid="stChatInputSubmit"] {{
        background: transparent !important;
        border: none !important;
        position: relative;
        width: 40px !important; height: 40px !important;
    }}

    /* Adding custom arrow icon */
    div[data-testid="stChatInputContainer"] button[data-testid="stChatInputSubmit"]::after {{
        content: '➤'; /* Arrow symbol or SVG content */
        font-size: 1.5rem;
        color: #A0A0A0; /* Static color */
        position: absolute;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%) rotate(0deg);
        transition: color 0.3s, transform 0.3s;
    }}

    /* Hover effect */
    div[data-testid="stChatInputContainer"] button[data-testid="stChatInputSubmit"]:hover::after {{
        color: #00ffff !important; /* Light blue on hover */
        transform: translate(-50%, -50%) scale(1.1);
    }}

    /* Disabled state */
    div[data-testid="stChatInputContainer"] button[data-testid="stChatInputSubmit"]:disabled::after {{
        color: #444 !important;
    }}
    
    /* Sidebar Popover Styling */
    div[data-testid="stHorizontalBlock"]:last-of-type [data-testid="stPopover"] > button {{
        width: 38px !important; height: 38px !important;
        border-radius: 50% !important; background-color: transparent !important; border: none !important;
    }}
    [data-testid="stPopoverBody"] {{ background-color: #2C2C2C !important; border: 1px solid #444 !important; }}
    </style>
""", unsafe_allow_html=True)

# Function to encode image
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

# ==========================================
# 4. SIDEBAR LOGO & HISTORY
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
        st.markdown("<h3 style='color: #60A5FA; text-align: center;'>AskMNIT</h3>", unsafe_allow_html=True)

    st.markdown("<div class='new-chat-btn'>", unsafe_allow_html=True)
    if st.button("➕ New Session"):
        chat_id = f"Session {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[chat_id] = []
        st.session_state.current_chat = chat_id
        st.session_state.pending_generation = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    for chat_name in reversed(list(st.session_state.sessions.keys())):
        if st.button(f"💬 {chat_name}", key=f"btn_{chat_name}"):
            st.session_state.current_chat = chat_name
            st.session_state.pending_generation = False
            st.rerun()

# ==========================================
# 5. MAIN CHAT LOGIC
# ==========================================
st.markdown("<h1 style='color: #FFFFFF; text-align: center;'>AskMNIT</h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #BBBBBB; margin-bottom: 30px;'>Your Professional AI Assistant</div>", unsafe_allow_html=True)

for message in st.session_state.sessions[st.session_state.current_chat]:
    avatar_icon = "user.png" if message["role"] == "user" else "logo.png"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

# ==========================================
# 6. ATTACHMENT POPOVER
# ==========================================
tool_col1, tool_col2 = st.columns([1, 1]) 
chat_img_bottom = None

with tool_col1:
    with st.popover("😀"): 
        st.write("Emojis go here") # Placeholder as exact implementation depends on js
        
with tool_col2:
    with st.popover("📎"): 
        chat_img_bottom = st.file_uploader("", type=['png', 'jpg', 'jpeg'], key="bottom_img")

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

if st.session_state.pending_generation:
    prompt = st.session_state.sessions[st.session_state.current_chat][-1]["content"]
    
    with st.chat_message("assistant", avatar="logo.png"):
        instructions = "You are 'AskMNIT', an exceptionally intelligent and professional AI assistant for MNIT."
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
                        stream=True
                    )
                else:
                    stream = client.chat.completions.create(
                        messages=[{"role": "system", "content": instructions}, {"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",
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
