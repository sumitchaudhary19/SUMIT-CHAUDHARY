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
    # Empty Chat -> Search Bar in Middle
    chat_pos_css = "top: 45vh !important; transform: translateX(-50%) !important;"
else:
    # Chat Started -> Search Bar shifts permanently to Bottom
    chat_pos_css = "bottom: 30px !important; transform: translateX(-50%) !important;"

# ==========================================
# 3. ADVANCED CSS (Dark Theme, Chat Alignment & RGB Gemini Bar)
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
        background-color: #000000 !important;
        border-top: 1px solid #222 !important;
        padding-top: 20px !important;
    }}
    [data-testid="stBottom"] > div {{ background-color: #000000 !important; }}
    
    /* =========================================
       CHAT MESSAGES ALIGNMENT & (3/4)th WIDTH
       ========================================= */
    div[data-testid="stChatMessage"] {{ 
        border-radius: 12px; 
        padding: 15px 20px; 
        margin-bottom: 20px;
        width: fit-content !important; 
        max-width: 75% !important; 
    }}
    
    /* 🔵 USER (Odd) -> Aligned EXACT RIGHT */
    div[data-testid="stChatMessage"]:nth-child(odd) {{ 
        background-color: #2C2C2C !important; 
        border: 1px solid #444 !important; 
        margin-left: auto !important; 
        margin-right: 0 !important;
    }}
    
    /* 🟢 CHATBOT (Even) -> Aligned EXACT LEFT */
    div[data-testid="stChatMessage"]:nth-child(even) {{ 
        background-color: #212121 !important; 
        border: 1px solid #333 !important; 
        margin-right: auto !important; 
        margin-left: 0 !important; 
    }}
    
    /* CHAT TEXT COLOR (Grey) */
    div[data-testid="stChatMessageContent"] p {{
        color: #B0B0B0 !important; 
        font-size: 1rem; line-height: 1.6;
    }}

    /* =========================================
       SIDEBAR & LIGHT GREY BUTTONS
       ========================================= */
    section[data-testid="stSidebar"] {{ background-color: #111111 !important; border-right: 1px solid #333 !important; }}
    
    .stButton>button {{ 
        width: 100%; text-align: left; 
        background-color: #D3D3D3 !important; 
        border: 1px solid #999 !important; 
        padding: 10px 15px; border-radius: 8px; 
        font-weight: 600; color: #000000 !important; 
        transition: 0.2s; 
    }}
    .stButton>button:hover {{ background-color: #BDBDBD !important; }}
    
    .new-chat-btn>div>button {{ 
        background-color: #D3D3D3 !important; 
        color: #000000 !important; 
        justify-content: center; font-weight: 700; 
        margin-bottom: 20px; border-radius: 8px; 
        border: 1px solid #999 !important; 
    }}
    .new-chat-btn>div>button:hover {{ background-color: #BDBDBD !important; }}

    .signature-box {{ margin-top: 40px; margin-bottom: 20px; padding: 15px; border-radius: 8px; background: #2C2C2C; border: 1px solid #444; text-align: center; }}
    .signature-box p {{ margin: 0; font-size: 0.75rem; color: #AAAAAA; text-transform: uppercase; letter-spacing: 1px; }}
    .signature-box h3 {{ margin: 5px 0 0 0; font-size: 1.1rem; color: #E0E0E0; font-weight: 700; }}

    /* =========================================
       GEMINI-STYLE LARGE SEARCH BAR WITH RGB MOTION
       ========================================= */
       
    /* Targeting the toughest Streamlit classes to force changes */
    .stChatInput, div[data-testid="stChatInputContainer"], div[data-testid="stChatInput"] {{ 
        position: fixed !important;
        {chat_pos_css} 
        left: 50% !important;
        width: 90vw !important;
        max-width: 850px !important; /* Huge Gemini Width */
        min-height: 65px !important; /* Taller Bar */
        border-radius: 40px !important; 
        background-color: #1E1E1E !important; 
        border: none !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6) !important;
        padding: 5px !important;
        z-index: 9999 !important;
    }}

    /* Advanced RGB Mask Border (Smoothest performance) */
    .stChatInput::before, div[data-testid="stChatInputContainer"]::before {{
        content: '';
        position: absolute;
        inset: 0;
        border-radius: 40px;
        padding: 3px; /* RGB Border thickness */
        background: conic-gradient(from 0deg, #ff0000, #ff00ff, #0000ff, #00ffff, #00ff00, #ffff00, #ff0000);
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        animation: rotateRGB 3s linear infinite;
        pointer-events: none;
    }}

    @keyframes rotateRGB {{ 
        100% {{ transform: rotate(360deg); }} 
    }}

    /* Text Input Area */
    .stChatInput textarea, div[data-testid="stChatInputContainer"] textarea {{ 
        color: #FFFFFF !important; 
        font-size: 1.15rem !important; /* Larger text */
        padding-left: 20px !important;
        padding-top: 15px !important;
        padding-right: 60px !important; /* Space for send arrow only */
        background-color: transparent !important;
    }}
    .stChatInput textarea::placeholder {{
        color: #888888 !important;
    }}

    /* =========================================
       CUSTOM GEMINI-STYLE SEND BUTTON
       ========================================= */
    .stChatInput button, div[data-testid="stChatInputContainer"] button[data-testid="stChatInputSubmit"] {{
        background-color: #333333 !important;
        border-radius: 50% !important;
        border: 1px solid #555 !important;
        position: absolute !important;
        width: 42px !important; height: 42px !important;
        right: 15px !important; 
        bottom: 50% !important;
        transform: translateY(50%) !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    /* Hide default SVG */
    .stChatInput button svg, div[data-testid="stChatInputContainer"] button svg {{
        display: none !important;
    }}

    /* The Arrow (➤) */
    .stChatInput button::after, div[data-testid="stChatInputContainer"] button::after {{
        content: '➤';
        font-size: 1.4rem;
        color: #E0E0E0; 
        position: absolute;
    }}

    .stChatInput button:hover, div[data-testid="stChatInputContainer"] button:hover {{
        background-color: #3B82F6 !important; /* Glows blue */
        border-color: #60A5FA !important;
    }}
    .stChatInput button:hover::after, div[data-testid="stChatInputContainer"] button:hover::after {{
        color: #FFFFFF !important;
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

for message in st.session_state.sessions[st.session_state.current_chat]:
    avatar_icon = "user.png" if message["role"] == "user" else "logo.png"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

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
    
    # Trigger AI Generation and UI shift
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
