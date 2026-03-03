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
# 3. DARK MODE, BLACK BOTTOM & INSIDE BUTTONS CSS
# ==========================================
st.markdown(f"""
    <style>
    @import url('[https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap](https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap)');
    
    /* Global Dark Grey Background for Chat Area */
    html, body, [class*="css"], [data-testid="stAppViewContainer"] {{ 
        font-family: 'Inter', sans-serif; 
        background-color: #212121 !important; 
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
    
    /* Chat Message Styling (Backgrounds and Width Control) */
    div[data-testid="stChatMessage"] {{ 
        border-radius: 12px; 
        padding: 15px 20px; 
        margin-bottom: 20px;
        max-width: 75% !important; /* Bubble length at 3/4ths maximum */
        width: fit-content !important; /* critical for bubble control */
    }}
    
    /* 🔵 USER (Odd/First instance flow) -> Aligned RIGHT */
    div[data-testid="stChatMessage"]:nth-child(odd) {{ 
        background-color: #2C2C2C !important; border: 1px solid #444 !important; 
        margin-left: auto !important; /* Alignment to right */
        margin-right: 0 !important;
    }}
    
    /* 🟢 CHATBOT (Even instances flow) -> Aligned LEFT */
    div[data-testid="stChatMessage"]:nth-child(even) {{ 
        background-color: #212121 !important; border: 1px solid #444 !important; 
        margin-right: auto !important; /* Alignment to left */
        margin-left: 0 !important;
    }}
    
    /* CHAT TEXT COLOR TO GREY */
    div[data-testid="stChatMessageContent"] p {{
        color: #B0B0B0 !important; /* Nice soothing light grey */
        font-size: 1rem;
        line-height: 1.6;
    }}

    /* Sidebar Dark Styling */
    section[data-testid="stSidebar"] {{ background-color: #1A1A1A !important; border-right: 1px solid #333 !important; }}
    
    /* LIGHT GREY SIDEBAR BUTTONS */
    /* Normal Sidebar Buttons (Chat History) */
    .stButton>button {{ 
        width: 100%; text-align: left; 
        background-color: #D3D3D3 !important; 
        border: 1px solid #999 !important; 
        padding: 10px 15px; border-radius: 8px; 
        font-weight: 600; color: #000000 !important; 
        transition: 0.2s; 
    }}
    .stButton>button:hover {{ 
        background-color: #BDBDBD !important; 
        color: #000000 !important; 
        border: 1px solid #777 !important; 
    }}
    
    /* Top "New Session" Button */
    .new-chat-btn>div>button {{ 
        background-color: #D3D3D3 !important; 
        color: #000000 !important; 
        justify-content: center; font-weight: 700; 
        margin-bottom: 20px; border-radius: 8px; 
        border: 1px solid #999 !important; 
    }}
    .new-chat-btn>div>button:hover {{ 
        background-color: #BDBDBD !important; 
        color: #000000 !important; 
    }}

    .signature-box {{ margin-top: 40px; margin-bottom: 20px; padding: 15px; border-radius: 8px; background: #2C2C2C; border: 1px solid #444; text-align: center; }}
    .signature-box p {{ margin: 0; font-size: 0.75rem; color: #AAAAAA; text-transform: uppercase; letter-spacing: 1px; }}
    .signature-box h3 {{ margin: 5px 0 0 0; font-size: 1.1rem; color: #E0E0E0; font-weight: 700; }}

    /* =========================================
       SEARCH BAR & INSIDE RIGHT ALIGNED BUTTONS
       ========================================= */
       
    /* 1. Chat Input Bar (Light Grey, Pill Shape) */
    div[data-testid="stChatInputContainer"] {{ 
        border-radius: 30px !important; /* Fully rounded pill shape */
        border: 1px solid #999 !important; 
        background-color: #D3D3D3 !important; 
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4) !important;
        padding-right: 110px !important; /* Space so text doesn't hide behind buttons */
        max-width: 800px !important;
        margin: 0 auto !important;
        {chat_pos_css} 
    }}
    div[data-testid="stChatInputContainer"] textarea {{ color: #000000 !important; font-weight: 500; }}
    div[data-testid="stChatInputContainer"] p {{ color: #555555 !important; }}
    div[data-testid="stChatInputContainer"] svg {{ fill: #333333 !important; display: none; /* Hiding default send icon to save space */ }} 
    
    /* 2. Position the Toolbar exactly inside the right edge */
    div[data-testid="stHorizontalBlock"]:last-of-type {{
        position: fixed;
        {tool_pos_css} 
        width: auto !important;
        z-index: 99999;
        display: flex;
        gap: 2px;
        flex-direction: row;
        justify-content: flex-end;
    }}

    /* Media queries to keep buttons snapped to the right side of the 800px box */
    @media (min-width: 850px) {{
        div[data-testid="stHorizontalBlock"]:last-of-type {{
            left: 50%;
            margin-left: 280px; /* Aligns them inside the right edge of max-800px box */
        }}
    }}
    @media (max-width: 849px) {{
        div[data-testid="stHorizontalBlock"]:last-of-type {{
            right: 25px; /* Stick to right side padding on smaller screens */
        }}
    }}
    
    /* 3. Button Styling (Perfectly Circular) */
    div[data-testid="stHorizontalBlock"]:last-of-type [data-testid="stPopover"] > button {{
        width: 38px !important;
        height: 38px !important;
        border-radius: 50% !important; /* PERFECT CIRCLE */
        padding: 0 !important;
        border: none !important;
        background-color: transparent !important; /* Blend into search bar */
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: none !important;
        transition: 0.2s;
    }}
    
    div[data-testid="stHorizontalBlock"]:last-of-type [data-testid="stPopover"] > button p {{
        font-size: 1.4rem !important;
        margin: 0 !important;
        line-height: 1 !important;
    }}

    div[data-testid="stHorizontalBlock"]:last-of-type [data-testid="stPopover"] > button:hover {{
        background-color: #BDBDBD !important; /* Darker grey on hover */
    }}
    
    /* Popover Body */
    [data-testid="stPopoverBody"] {{
        padding: 0 !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        background-color: #D3D3D3 !important;
        border: 1px solid #999 !important;
    }}
    </style>
""", unsafe_allow_html=True)

def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

# ==========================================
# 4. SIDEBAR WITH CUSTOM AskMNIT LOGO
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
        st.warning("⚠️ logo.png not found. Upload it to GitHub!")
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
st.markdown("<h1 style='color: #FFFFFF; font-weight: 800; text-align: center; font-size: 2.5rem;'>AskMNIT</h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #BBBBBB; font-weight: 500; margin-bottom: 30px; margin-top: -10px;'>Your Professional AI Assistant</div>", unsafe_allow_html=True)

for message in st.session_state.sessions[st.session_state.current_chat]:
    avatar_icon = "user.png" if message["role"] == "user" else "logo.png"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

# ==========================================
# 6. RIGHT ALIGNED TOOLBAR & EMOJI SCRIPT
# ==========================================
tool_col1, tool_col2 = st.columns([1, 1]) 
chat_img_bottom = None

with tool_col1:
    with st.popover("😀"): 
        emoji_list = [
            "😀","😃","😄","😁","😆","😅","😂","🤣","🥲","☺️","😊","😇","🙂","🙃","😉","😌","😍","🥰","😘","😗",
            "😙","😚","😋","😛","😝","😜","🤪","🤨","🧐","🤓","😎","🤩","🥳","😏","😒","😞","😔","😟","😕","🙁",
            "☹️","😣","😖","😫","😩","🥺","😢","😭","😤","😠","😡","🤬","🤯","😳","🥵","🥶","😱","😨","😰","😥",
            "👍","👎","👏","🙌","👐","🤲","🤝","🙏","✌️","🤞","🤟","🤘","🤙","👈","👉","👆","👇","❤️","🔥","✨","🚀"
        ]
        
        emoji_divs = "".join([f'<div class="emoji-btn">{e}</div>' for e in emoji_list])
        
        html_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        body {{ margin: 0; padding: 10px; font-family: sans-serif; background: #D3D3D3; color: #000000; }}
        .emoji-grid {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; height: 190px; overflow-y: auto; padding-right: 5px; }}
        .emoji-btn {{ font-size: 1.6rem; cursor: pointer; text-align: center; user-select: none; transition: transform 0.1s; padding: 5px; border-radius: 8px; }}
        .emoji-btn:hover {{ transform: scale(1.2); background-color: #BDBDBD; }}
        .emoji-grid::-webkit-scrollbar {{ width: 6px; }}
        .emoji-grid::-webkit-scrollbar-track {{ background: #D3D3D3; border-radius: 4px; }}
        .emoji-grid::-webkit-scrollbar-thumb {{ background: #999; border-radius: 4px; }}
        .emoji-grid::-webkit-scrollbar-thumb:hover {{ background: #777; }}
        </style>
        </head>
        <body>
        <div class="emoji-grid" id="grid">
            {emoji_divs}
        </div>
        <script>
            document.getElementById('grid').addEventListener('click', function(e) {{
                if(e.target.classList.contains('emoji-btn')) {{
                    const emoji = e.target.innerText;
                    const parentDoc = window.parent.document;
                    const chatInput = parentDoc.querySelector('[data-testid="stChatInputTextArea"]') || 
                                      parentDoc.querySelector('[data-testid="stChatInputContainer"] textarea');
                    if(chatInput) {{
                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
                        nativeInputValueSetter.call(chatInput, chatInput.value + emoji);
                        chatInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        chatInput.focus();
                    }}
                }}
            }});
        </script>
        </body>
        </html>
        """
        components.html(html_code, height=210)
        
with tool_col2:
    with st.popover("📎"): 
        st.markdown("<p style='font-size:0.9rem; font-weight:600; color:#000000; margin-bottom:5px;'>Upload context image:</p>", unsafe_allow_html=True)
        chat_img_bottom = st.file_uploader("", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed", key="bottom_img")
        if chat_img_bottom:
            st.success("✅ Attached!")

final_vision_image = chat_img_bottom

# ==========================================
# 7. CHAT INPUT & AI GENERATION
# ==========================================
# 7A. Taking the user input
if prompt := st.chat_input("Ask me anything..."):
    
    curr_chat = st.session_state.current_chat
    if curr_chat.startswith("New Session") and len(st.session_state.sessions[curr_chat]) == 0:
        new_name = prompt[:20] + "..."
        st.session_state.sessions[new_name] = st.session_state.sessions.pop(curr_chat)
        st.session_state.current_chat = new_name

    st.session_state.sessions[st.session_state.current_chat].append({"role": "user", "content": prompt})
    
    # Trigger generation
    st.session_state.pending_generation = True
    st.rerun()

# 7B. Processing AI generation
if st.session_state.pending_generation:
    prompt = st.session_state.sessions[st.session_state.current_chat][-1]["content"]
    
    with st.chat_message("assistant", avatar="logo.png"):
        if any(word in prompt.lower() for word in ["draw", "pic", "image", "photo bana"]):
            with st.spinner("Generating visualization..."):
                time.sleep(1.5)
                safe_prompt = urllib.parse.quote(prompt)
                img_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=800&height=400&nologo=true"
                st.image(img_url)
                st.session_state.sessions[st.session_state.current_chat].append({"role": "assistant", "content": f"![Generated Image]({img_url})"})
        else:
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
