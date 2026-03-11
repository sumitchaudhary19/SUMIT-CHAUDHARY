import streamlit as st
from groq import Groq
import base64
import os

# ==========================================
# 1. PAGE CONFIG & SECRETS
# ==========================================
st.set_page_config(
    page_title="AskMNIT — Student Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("🚨 GROQ_API_KEY missing from secrets!")
    st.stop()

# ==========================================
# 2. SESSION STATE
# ==========================================
defaults = {
    "sessions": {"New Session 1": []},
    "current_chat": "New Session 1",
    "pending_generation": False,
    "page_view": "dashboard",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ==========================================
# 3. HELPER
# ==========================================
def get_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

logo_b64 = get_base64("mnit_logo.png")

# ==========================================
# 4. MASTER CSS — NEON NOIR GLASSMORPHISM
# ==========================================
SW = "280px"

MASTER_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

:root {{
  --cyan:    #00F5FF;
  --violet:  #7C3AED;
  --pink:    #F72585;
  --green:   #06FFA5;
  --amber:   #FFB627;
  --bg:      #04030A;
  --glass:   rgba(255,255,255,0.04);
  --glass2:  rgba(255,255,255,0.07);
  --border:  rgba(255,255,255,0.08);
  --text:    #F0EEFF;
  --muted:   rgba(240,238,255,0.45);
  --font:    'Outfit', sans-serif;
}}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ overflow-x: hidden; background: var(--bg) !important; }}

/* ===== STREAMLIT RESETS ===== */
[data-testid="stAppViewContainer"] {{
    background: var(--bg) !important;
    margin-left: {SW} !important;
    width: calc(100% - {SW}) !important;
    font-family: var(--font);
    min-height: 100vh;
}}
section[data-testid="stSidebar"] {{ display: none !important; }}
header {{ display: none !important; }}
footer {{ display: none !important; }}
[data-testid="stMainBlockContainer"],
[data-testid="stVerticalBlock"] > div,
.block-container {{ padding: 0 !important; max-width: 100% !important; }}

/* ===== ANIMATED BACKGROUND ===== */
.bg-mesh {{
    position: fixed; top: 0; left: {SW}; right: 0; bottom: 0;
    z-index: 0; pointer-events: none; overflow: hidden;
}}
.bg-mesh::before {{
    content: '';
    position: absolute; width: 700px; height: 700px;
    background: radial-gradient(circle, rgba(124,58,237,0.11) 0%, transparent 70%);
    top: -200px; right: -100px;
    animation: drift1 12s ease-in-out infinite alternate;
}}
.bg-mesh::after {{
    content: '';
    position: absolute; width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(0,245,255,0.07) 0%, transparent 70%);
    bottom: -150px; left: 100px;
    animation: drift2 15s ease-in-out infinite alternate;
}}
@keyframes drift1 {{ 0% {{ transform: translate(0,0); }} 100% {{ transform: translate(80px,60px); }} }}
@keyframes drift2 {{ 0% {{ transform: translate(0,0); }} 100% {{ transform: translate(-60px,-80px); }} }}

/* ===== SIDEBAR ===== */
.sidebar {{
    position: fixed; top: 0; left: 0;
    width: {SW}; height: 100vh;
    background: linear-gradient(180deg, #06040F 0%, #030208 100%);
    border-right: 1px solid rgba(0,245,255,0.08);
    z-index: 10000; display: flex; flex-direction: column;
    overflow-y: auto; overflow-x: hidden;
    scrollbar-width: thin;
    scrollbar-color: rgba(124,58,237,0.3) transparent;
}}
.sidebar::-webkit-scrollbar {{ width: 3px; }}
.sidebar::-webkit-scrollbar-thumb {{ background: rgba(124,58,237,0.4); border-radius: 3px; }}
.sidebar::before {{
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--cyan), var(--violet), transparent);
    opacity: 0.5;
}}

/* Brand */
.sb-brand {{
    padding: 26px 20px 20px; border-bottom: 1px solid rgba(255,255,255,0.05);
    display: flex; align-items: center; gap: 13px; flex-shrink: 0;
}}
.sb-logo {{
    width: 44px; height: 44px; border-radius: 13px;
    background: linear-gradient(135deg, rgba(0,245,255,0.12), rgba(124,58,237,0.18));
    border: 1px solid rgba(0,245,255,0.2);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem; flex-shrink: 0; overflow: hidden;
}}
.sb-logo-img {{
    width: 100%; height: 100%; border-radius: 12px;
    background-image: url("data:image/png;base64,{logo_b64}");
    background-size: cover; background-position: center;
}}
.sb-name {{ font-weight: 800; font-size: 1.18rem; color: var(--text); letter-spacing: -0.3px; line-height: 1.1; }}
.sb-sub  {{ font-size: 0.62rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1.8px; margin-top: 3px; }}

/* Nav */
.nav-sec {{ font-size: 0.58rem; font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase; color: rgba(255,255,255,0.2); padding: 16px 22px 6px; }}
.nav-item {{
    display: flex; align-items: center; gap: 11px;
    padding: 10px 14px 10px 18px; margin: 1px 10px; border-radius: 12px;
    cursor: pointer; text-decoration: none !important;
    border: 1px solid transparent; position: relative; overflow: hidden;
    transition: all 0.2s ease;
}}
.nav-item::before {{
    content: ''; position: absolute; inset: 0;
    background: linear-gradient(135deg, rgba(0,245,255,0.05), rgba(124,58,237,0.03));
    opacity: 0; transition: opacity 0.2s;
}}
.nav-item:hover {{ border-color: rgba(0,245,255,0.12); }}
.nav-item:hover::before {{ opacity: 1; }}
.nav-item.active {{
    background: linear-gradient(135deg, rgba(0,245,255,0.09), rgba(124,58,237,0.07));
    border-color: rgba(0,245,255,0.18);
}}
.nav-item.active::after {{
    content: ''; position: absolute; left: 0; top: 22%; bottom: 22%;
    width: 3px; background: linear-gradient(180deg, var(--cyan), var(--violet));
    border-radius: 0 3px 3px 0;
}}
.nav-icon {{ font-size: 1rem; width: 20px; text-align: center; flex-shrink: 0; position: relative; z-index: 1; }}
.nav-label {{ font-size: 0.84rem; font-weight: 500; color: rgba(240,238,255,0.6); flex: 1; position: relative; z-index: 1; transition: color 0.2s; }}
.nav-item:hover .nav-label, .nav-item.active .nav-label {{ color: var(--text); font-weight: 600; }}
.nav-badge {{ font-size: 0.58rem; font-weight: 700; padding: 2px 7px; border-radius: 20px; position: relative; z-index: 1; flex-shrink: 0; }}
.nb-c {{ background: rgba(0,245,255,0.12); color: var(--cyan); border: 1px solid rgba(0,245,255,0.2); }}
.nb-a {{ background: rgba(255,182,39,0.12); color: var(--amber); border: 1px solid rgba(255,182,39,0.2); }}
.nb-p {{ background: rgba(247,37,133,0.12); color: var(--pink); border: 1px solid rgba(247,37,133,0.2); }}
.nb-g {{ background: rgba(6,255,165,0.1); color: var(--green); border: 1px solid rgba(6,255,165,0.18); }}
.sb-div {{ height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent); margin: 9px 18px; }}

/* Profile */
.sb-profile {{ margin-top: auto; padding: 14px 16px 18px; border-top: 1px solid rgba(255,255,255,0.05); flex-shrink: 0; }}
.sb-prof-inner {{
    display: flex; align-items: center; gap: 10px; padding: 11px 12px;
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 13px; transition: all 0.2s;
}}
.sb-prof-inner:hover {{ background: rgba(0,245,255,0.04); border-color: rgba(0,245,255,0.13); }}
.sb-avatar {{
    width: 34px; height: 34px; border-radius: 9px;
    background: linear-gradient(135deg, var(--cyan), var(--violet));
    display: flex; align-items: center; justify-content: center;
    font-size: 0.78rem; font-weight: 800; color: #fff; flex-shrink: 0;
}}
.sb-pname {{ font-size: 0.8rem; font-weight: 700; color: var(--text); line-height: 1.2; }}
.sb-prole {{ font-size: 0.63rem; color: var(--muted); margin-top: 1px; }}
.sb-out {{ margin-left: auto; font-size: 0.88rem; color: rgba(255,255,255,0.22); cursor: pointer; flex-shrink: 0; }}
.sb-out:hover {{ color: var(--pink); }}

/* ===== TOPBAR ===== */
.topbar {{
    position: fixed; top: 0; left: {SW}; width: calc(100vw - {SW}); height: 66px;
    background: rgba(4,3,10,0.82); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(0,245,255,0.07);
    z-index: 9998; display: flex; align-items: center; justify-content: space-between; padding: 0 34px;
}}
.tb-title {{ font-weight: 700; font-size: 0.98rem; color: var(--text); letter-spacing: -0.2px; }}
.tb-bc {{ font-size: 0.7rem; color: var(--muted); display: flex; align-items: center; gap: 5px; margin-top: 2px; }}
.tb-right {{ display: flex; align-items: center; gap: 18px; }}
.tb-search {{
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px; padding: 7px 14px; display: flex; align-items: center; gap: 8px;
    font-size: 0.78rem; color: var(--muted); cursor: pointer; min-width: 175px; transition: all 0.2s;
}}
.tb-search:hover {{ background: rgba(0,245,255,0.05); border-color: rgba(0,245,255,0.18); }}
.tb-icon {{
    width: 36px; height: 36px; border-radius: 9px;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07);
    display: flex; align-items: center; justify-content: center; font-size: 0.95rem;
    cursor: pointer; position: relative; transition: all 0.2s;
}}
.tb-icon:hover {{ background: rgba(0,245,255,0.07); border-color: rgba(0,245,255,0.18); }}
.tb-ping {{
    position: absolute; top: 5px; right: 5px; width: 7px; height: 7px;
    background: var(--pink); border-radius: 50%; border: 2px solid var(--bg);
    animation: ping 1.8s ease-in-out infinite;
}}
@keyframes ping {{ 0%,100% {{ transform: scale(1); opacity: 1; }} 50% {{ transform: scale(1.5); opacity: 0.6; }} }}
.tb-av {{
    width: 36px; height: 36px; border-radius: 9px;
    background: linear-gradient(135deg, var(--cyan), var(--violet));
    display: flex; align-items: center; justify-content: center;
    font-size: 0.78rem; font-weight: 800; color: white; cursor: pointer;
    border: 1px solid rgba(0,245,255,0.25);
}}

/* ===== PAGE ===== */
.page {{ position: relative; z-index: 1; padding: 86px 34px 60px; min-height: 100vh; }}

/* Welcome */
.welcome-row {{
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 30px; gap: 22px;
}}
.w-text h1 {{
    font-size: 2rem; font-weight: 900; color: var(--text);
    line-height: 1.1; letter-spacing: -0.6px;
}}
.w-text h1 span {{
    background: linear-gradient(90deg, var(--cyan), var(--violet));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}}
.w-text p {{ font-size: 0.88rem; color: var(--muted); margin-top: 7px; }}
.w-badge {{
    display: inline-flex; align-items: center; gap: 6px; margin-top: 12px;
    background: rgba(6,255,165,0.07); border: 1px solid rgba(6,255,165,0.18);
    border-radius: 30px; padding: 6px 15px; font-size: 0.76rem; font-weight: 600; color: var(--green);
}}
.w-card {{
    background: var(--glass); border: 1px solid var(--border); border-radius: 20px;
    padding: 22px 26px; min-width: 290px; flex-shrink: 0; position: relative; overflow: hidden;
}}
.w-card::before {{
    content: ''; position: absolute; top: -40px; right: -40px;
    width: 140px; height: 140px;
    background: radial-gradient(circle, rgba(0,245,255,0.07), transparent 70%);
    pointer-events: none;
}}
.wc-lbl {{ font-size: 0.65rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 5px; }}
.wc-val {{
    font-size: 2.3rem; font-weight: 900; letter-spacing: -2px;
    background: linear-gradient(90deg, var(--cyan), #7C3AED);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; line-height: 1;
}}
.wc-sub {{ font-size: 0.72rem; color: var(--muted); margin-top: 4px; }}
.bar-bg {{ height: 5px; background: rgba(255,255,255,0.07); border-radius: 5px; overflow: hidden; margin-top: 12px; }}
.bar-fill {{ height: 100%; width: 78%; background: linear-gradient(90deg, var(--cyan), var(--violet)); border-radius: 5px; animation: grow 1.5s ease-out; }}
@keyframes grow {{ from {{ width: 0%; }} to {{ width: 78%; }} }}
.bar-lbls {{ display: flex; justify-content: space-between; margin-top: 5px; font-size: 0.63rem; color: var(--muted); }}

/* Stats */
.stats-grid {{ display: grid; grid-template-columns: repeat(4,1fr); gap: 15px; margin-bottom: 26px; }}
.scard {{
    background: var(--glass); border: 1px solid var(--border); border-radius: 18px;
    padding: 20px 18px; position: relative; overflow: hidden;
    transition: all 0.28s ease; cursor: pointer;
}}
.scard:hover {{ transform: translateY(-4px); box-shadow: 0 20px 40px rgba(0,0,0,0.4); }}
.scard::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; border-radius: 18px 18px 0 0; }}
.sc1::before {{ background: linear-gradient(90deg, var(--cyan), transparent); }}
.sc2::before {{ background: linear-gradient(90deg, var(--amber), transparent); }}
.sc3::before {{ background: linear-gradient(90deg, var(--violet), transparent); }}
.sc4::before {{ background: linear-gradient(90deg, var(--pink), transparent); }}
.sc1:hover {{ border-color: rgba(0,245,255,0.22); background: rgba(0,245,255,0.04); }}
.sc2:hover {{ border-color: rgba(255,182,39,0.22); background: rgba(255,182,39,0.03); }}
.sc3:hover {{ border-color: rgba(124,58,237,0.22); background: rgba(124,58,237,0.04); }}
.sc4:hover {{ border-color: rgba(247,37,133,0.22); background: rgba(247,37,133,0.04); }}
.sic {{
    width: 42px; height: 42px; border-radius: 11px;
    display: flex; align-items: center; justify-content: center; font-size: 1.2rem; margin-bottom: 13px;
}}
.ic1 {{ background: rgba(0,245,255,0.09); border: 1px solid rgba(0,245,255,0.14); }}
.ic2 {{ background: rgba(255,182,39,0.09); border: 1px solid rgba(255,182,39,0.14); }}
.ic3 {{ background: rgba(124,58,237,0.1); border: 1px solid rgba(124,58,237,0.18); }}
.ic4 {{ background: rgba(247,37,133,0.09); border: 1px solid rgba(247,37,133,0.14); }}
.sv {{ font-size: 1.8rem; font-weight: 900; color: var(--text); line-height: 1; letter-spacing: -1.5px; margin-bottom: 4px; }}
.sl {{ font-size: 0.68rem; text-transform: uppercase; letter-spacing: 1px; color: var(--muted); margin-bottom: 9px; }}
.schip {{ display: inline-flex; align-items: center; gap: 3px; font-size: 0.64rem; font-weight: 600; padding: 3px 8px; border-radius: 20px; }}
.ch1 {{ background: rgba(0,245,255,0.09); color: var(--cyan); }}
.ch2 {{ background: rgba(255,182,39,0.09); color: var(--amber); }}
.ch3 {{ background: rgba(124,58,237,0.1); color: #A78BFA; }}
.ch4 {{ background: rgba(247,37,133,0.09); color: var(--pink); }}

/* Two column */
.two-col {{ display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 18px; margin-bottom: 22px; }}
.three-col {{ display: grid; grid-template-columns: repeat(3,1fr); gap: 15px; margin-bottom: 22px; }}

/* Glass card */
.gc {{
    background: var(--glass); border: 1px solid var(--border); border-radius: 20px; padding: 22px;
    position: relative; overflow: hidden; transition: border-color 0.2s;
}}
.gc:hover {{ border-color: rgba(0,245,255,0.1); }}
.gc::after {{
    content: ''; position: absolute; top: 0; right: 0;
    width: 70px; height: 70px;
    background: radial-gradient(circle, rgba(0,245,255,0.04), transparent 70%);
    pointer-events: none;
}}
.gc-head {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; }}
.gc-title {{ font-size: 0.88rem; font-weight: 700; color: var(--text); display: flex; align-items: center; gap: 8px; }}
.gc-action {{ font-size: 0.68rem; color: var(--cyan); cursor: pointer; font-weight: 500; }}

/* Schedule */
.si {{
    display: flex; align-items: center; gap: 13px; padding: 11px 12px; border-radius: 11px;
    margin-bottom: 7px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04);
    transition: all 0.2s;
}}
.si:hover {{ background: rgba(0,245,255,0.04); border-color: rgba(0,245,255,0.1); transform: translateX(3px); }}
.si.live {{
    background: rgba(0,245,255,0.045); border-color: rgba(0,245,255,0.14);
}}
.si.live::after {{
    content: 'NOW';
    margin-left: auto; font-size: 0.52rem; font-weight: 800; letter-spacing: 1.5px;
    color: var(--cyan); background: rgba(0,245,255,0.09); border: 1px solid rgba(0,245,255,0.18);
    padding: 2px 6px; border-radius: 7px;
}}
.si-line {{ width: 3px; border-radius: 3px; align-self: stretch; flex-shrink: 0; }}
.si-time {{ font-size: 0.7rem; font-weight: 700; color: var(--muted); min-width: 60px; }}
.si-sub {{ font-size: 0.82rem; font-weight: 600; color: var(--text); line-height: 1.2; }}
.si-room {{ font-size: 0.65rem; color: var(--muted); margin-top: 2px; }}

/* Notice */
.ni {{ display: flex; gap: 12px; padding: 11px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }}
.ni:last-child {{ border-bottom: none; padding-bottom: 0; }}
.ni-dot {{ width: 7px; height: 7px; border-radius: 50%; margin-top: 17px; flex-shrink: 0; }}
.ni-body {{ flex: 1; }}
.ni-tag {{ display: inline-block; font-size: 0.56rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; padding: 1px 7px; border-radius: 8px; margin-bottom: 4px; }}
.t-u {{ background: rgba(247,37,133,0.1); color: var(--pink); border: 1px solid rgba(247,37,133,0.18); }}
.t-e {{ background: rgba(124,58,237,0.1); color: #A78BFA; border: 1px solid rgba(124,58,237,0.18); }}
.t-a {{ background: rgba(0,245,255,0.07); color: var(--cyan); border: 1px solid rgba(0,245,255,0.14); }}
.t-h {{ background: rgba(255,182,39,0.09); color: var(--amber); border: 1px solid rgba(255,182,39,0.18); }}
.ni-txt {{ font-size: 0.8rem; color: rgba(240,238,255,0.7); line-height: 1.52; }}
.ni-date {{ font-size: 0.63rem; color: rgba(255,255,255,0.24); margin-top: 3px; }}

/* Quick links */
.qlc {{
    background: var(--glass); border: 1px solid var(--border); border-radius: 16px;
    padding: 20px 18px; display: flex; flex-direction: column; gap: 12px;
    cursor: pointer; transition: all 0.25s ease; position: relative; overflow: hidden;
}}
.qlc:hover {{
    transform: translateY(-4px); border-color: rgba(0,245,255,0.18);
    background: rgba(0,245,255,0.025); box-shadow: 0 16px 32px rgba(0,0,0,0.3);
}}
.qlc-top {{ display: flex; align-items: flex-start; justify-content: space-between; }}
.qlc-icon {{ width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; }}
.qlc-arr {{ font-size: 0.8rem; color: rgba(255,255,255,0.18); transition: all 0.2s; }}
.qlc:hover .qlc-arr {{ color: var(--cyan); transform: translate(3px,-3px); }}
.qlc-title {{ font-size: 0.86rem; font-weight: 700; color: var(--text); }}
.qlc-sub {{ font-size: 0.68rem; color: var(--muted); margin-top: 2px; line-height: 1.4; }}
.pb-bg {{ height: 4px; background: rgba(255,255,255,0.06); border-radius: 4px; overflow: hidden; margin-top: 4px; }}
.pb-fill {{ height: 100%; border-radius: 4px; background: linear-gradient(90deg, var(--cyan), var(--violet)); }}

/* Section header */
.sec-h {{ display: flex; align-items: center; margin-bottom: 14px; }}
.sec-t {{ font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; color: rgba(255,255,255,0.3); white-space: nowrap; }}
.sec-l {{ flex: 1; height: 1px; background: rgba(255,255,255,0.05); margin-left: 12px; }}

/* FAB */
div[data-testid="stHorizontalBlock"] {{
    position: fixed !important; bottom: 30px !important; right: 34px !important;
    z-index: 9999 !important; width: auto !important;
}}
div[data-testid="stHorizontalBlock"] > div:last-child > div > button {{
    background: linear-gradient(135deg, #00F5FF 0%, #7C3AED 100%) !important;
    color: #04030A !important; border: none !important;
    border-radius: 50px !important; padding: 13px 24px !important;
    font-weight: 800 !important; font-size: 0.88rem !important; letter-spacing: 0.3px !important;
    box-shadow: 0 8px 30px rgba(0,245,255,0.32), 0 0 0 1px rgba(0,245,255,0.18) !important;
    white-space: nowrap !important;
    animation: fabpulse 2.5s ease-in-out infinite !important;
    font-family: 'Outfit', sans-serif !important;
}}
@keyframes fabpulse {{
    0%,100% {{ box-shadow: 0 8px 30px rgba(0,245,255,0.32), 0 0 0 1px rgba(0,245,255,0.18); }}
    50%      {{ box-shadow: 0 14px 42px rgba(0,245,255,0.48), 0 0 0 3px rgba(0,245,255,0.08); }}
}}

/* Entrance anims */
@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(22px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.a1 {{ animation: fadeUp 0.5s ease both; }}
.a2 {{ animation: fadeUp 0.5s 0.1s ease both; }}
.a3 {{ animation: fadeUp 0.5s 0.2s ease both; }}
.a4 {{ animation: fadeUp 0.5s 0.3s ease both; }}
.a5 {{ animation: fadeUp 0.5s 0.4s ease both; }}
</style>
"""

CHAT_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');
:root {{
  --cyan:#00F5FF; --violet:#7C3AED; --pink:#F72585; --green:#06FFA5; --amber:#FFB627;
  --bg:#04030A; --glass:rgba(255,255,255,0.04); --border:rgba(255,255,255,0.08);
  --text:#F0EEFF; --muted:rgba(240,238,255,0.45); --font:'Outfit',sans-serif;
}}
[data-testid="stAppViewContainer"] {{ background: var(--bg) !important; margin-left:{SW}!important; width:calc(100% - {SW})!important; font-family:var(--font); }}
section[data-testid="stSidebar"] {{ background:linear-gradient(180deg,#06040F,#030208)!important; border-right:1px solid rgba(0,245,255,0.08)!important; display:block!important; width:{SW}!important; }}
section[data-testid="stSidebar"] > div {{ padding:0!important; }}
header,footer {{ display:none!important; }}
[data-testid="stMainBlockContainer"],.block-container {{ padding:0!important; max-width:100%!important; }}
[data-testid="stChatMessageContent"] {{ background:rgba(255,255,255,0.04)!important; border:1px solid rgba(255,255,255,0.07)!important; border-radius:16px!important; padding:16px!important; color:var(--text)!important; font-family:var(--font)!important; }}
[data-testid="chatAvatarIcon-assistant"] {{ background:linear-gradient(135deg,var(--cyan),var(--violet))!important; border-radius:10px!important; }}
.stChatInputContainer {{ background:rgba(255,255,255,0.04)!important; border:1px solid rgba(0,245,255,0.12)!important; border-radius:16px!important; }}
.stChatInputContainer textarea {{ color:var(--text)!important; font-family:var(--font)!important; background:transparent!important; }}
.stButton>button {{ background:rgba(255,255,255,0.04)!important; color:var(--text)!important; border:1px solid rgba(255,255,255,0.08)!important; border-radius:10px!important; font-family:var(--font)!important; font-weight:600!important; font-size:0.82rem!important; transition:all 0.2s!important; padding:8px 14px!important; width:100%; }}
.stButton>button:hover {{ background:rgba(0,245,255,0.07)!important; border-color:rgba(0,245,255,0.22)!important; color:var(--cyan)!important; transform:translateX(3px)!important; }}
</style>
"""

# ==========================================
# APPLY CSS
# ==========================================
if st.session_state.page_view == "dashboard":
    st.markdown(MASTER_CSS, unsafe_allow_html=True)
else:
    st.markdown(MASTER_CSS + CHAT_CSS, unsafe_allow_html=True)


# ==========================================
# 5. DASHBOARD
# ==========================================
if st.session_state.page_view == "dashboard":

    st.markdown('<div class="bg-mesh"></div>', unsafe_allow_html=True)

    # --- SIDEBAR ---
    logo_inner = f'<div class="sb-logo-img"></div>' if logo_b64 else '🎓'
    st.markdown(f"""
    <div class="sidebar">
      <div class="sb-brand">
        <div class="sb-logo">{logo_inner}</div>
        <div><div class="sb-name">AskMNIT</div><div class="sb-sub">MNIT Jaipur · Portal</div></div>
      </div>

      <div class="nav-sec">Main Menu</div>
      <a class="nav-item active"><span class="nav-icon">🏠</span><span class="nav-label">Dashboard</span></a>
      <a class="nav-item"><span class="nav-icon">📅</span><span class="nav-label">Schedule</span><span class="nav-badge nb-c">Today</span></a>
      <a class="nav-item"><span class="nav-icon">📚</span><span class="nav-label">Academics</span></a>
      <a class="nav-item"><span class="nav-icon">💰</span><span class="nav-label">Fee Portal</span><span class="nav-badge nb-a">Due</span></a>
      <a class="nav-item"><span class="nav-icon">🏢</span><span class="nav-label">Hostel</span></a>

      <div class="sb-div"></div>

      <div class="nav-sec">Resources</div>
      <a class="nav-item"><span class="nav-icon">📄</span><span class="nav-label">Syllabus &amp; Notes</span></a>
      <a class="nav-item"><span class="nav-icon">📝</span><span class="nav-label">Previous Year Qs</span></a>
      <a class="nav-item"><span class="nav-icon">🏛️</span><span class="nav-label">Library Catalog</span></a>
      <a class="nav-item"><span class="nav-icon">📌</span><span class="nav-label">Latest Notices</span><span class="nav-badge nb-p">4</span></a>
      <a class="nav-item"><span class="nav-icon">🔬</span><span class="nav-label">Research Portal</span></a>
      <a class="nav-item"><span class="nav-icon">🏆</span><span class="nav-label">Placements</span><span class="nav-badge nb-g">New</span></a>

      <div class="sb-div"></div>

      <div class="nav-sec">Account</div>
      <a class="nav-item"><span class="nav-icon">⚙️</span><span class="nav-label">Settings</span></a>
      <a class="nav-item"><span class="nav-icon">🛟</span><span class="nav-label">Help &amp; Support</span></a>
      <a class="nav-item"><span class="nav-icon">🚪</span><span class="nav-label">Logout</span></a>

      <div class="sb-profile">
        <div class="sb-prof-inner">
          <div class="sb-avatar">SC</div>
          <div><div class="sb-pname">Sumit Chaudhary</div><div class="sb-prole">Metallurgy · 3rd Yr · 21UMT045</div></div>
          <div class="sb-out">⇥</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # --- TOPBAR ---
    st.markdown("""
    <div class="topbar">
      <div>
        <div class="tb-title">🎓 MNIT Jaipur — Student Portal</div>
        <div class="tb-bc"><span>Home</span><span style="color:rgba(255,255,255,0.2)">›</span><span style="color:var(--cyan)">Dashboard</span></div>
      </div>
      <div class="tb-right">
        <div class="tb-search"><span>🔍</span><span>Search anything...</span><span style="margin-left:auto;font-size:0.62rem;background:rgba(255,255,255,0.07);padding:2px 6px;border-radius:5px;">⌘K</span></div>
        <div class="tb-icon tb-date" style="width:auto;padding:0 12px;gap:6px;font-size:0.72rem;color:var(--muted);">📆 Wed, 11 Mar 2026</div>
        <div class="tb-icon">🔔<div class="tb-ping"></div></div>
        <div class="tb-av">SC</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # --- PAGE BODY ---
    st.markdown('<div class="page">', unsafe_allow_html=True)

    # Welcome
    st.markdown("""
    <div class="welcome-row a1">
      <div class="w-text">
        <h1>Welcome back, <span>Sumit</span> 👋</h1>
        <p>Everything happening on campus, right at your fingertips.</p>
        <div class="w-badge">🟢 Semester 6 Active · All Systems Online</div>
      </div>
      <div class="w-card">
        <div class="wc-lbl">Attendance This Semester</div>
        <div class="wc-val">78%</div>
        <div class="wc-sub">Minimum: 75% · You're safe ✓</div>
        <div class="bar-bg"><div class="bar-fill"></div></div>
        <div class="bar-lbls"><span>0%</span><span style="color:var(--cyan);font-weight:600;">78%</span><span>100%</span></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    st.markdown("""
    <div class="stats-grid a2">
      <div class="scard sc1"><div class="sic ic1">📊</div><div class="sv">78%</div><div class="sl">Attendance</div><div class="schip ch1">● Above Limit</div></div>
      <div class="scard sc2"><div class="sic ic2">⏳</div><div class="sv">20 min</div><div class="sl">Next Class</div><div class="schip ch2">● Coming Soon</div></div>
      <div class="scard sc3"><div class="sic ic3">📝</div><div class="sv">6/8</div><div class="sl">Assignments</div><div class="schip ch3">● 2 Pending</div></div>
      <div class="scard sc4"><div class="sic ic4">💰</div><div class="sv">₹18.5K</div><div class="sl">Fee Due</div><div class="schip ch4">● Due in 5 Days</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Schedule + Notices
    st.markdown("""
    <div class="two-col a3">
      <div class="gc">
        <div class="gc-head">
          <div class="gc-title"><span style="font-size:1rem;">📅</span> Today's Schedule</div>
          <div class="gc-action">View All ›</div>
        </div>
        <div class="si live">
          <div class="si-line" style="background:var(--cyan);"></div>
          <div class="si-time">09:30 AM</div>
          <div><div class="si-sub">Mineral Processing</div><div class="si-room">Room 302 · Prof. R.K. Sharma</div></div>
        </div>
        <div class="si">
          <div class="si-line" style="background:var(--green);"></div>
          <div class="si-time">11:30 AM</div>
          <div><div class="si-sub">Engineering Materials</div><div class="si-room">Metallurgy Lab 1 · Dr. Mehta</div></div>
        </div>
        <div class="si">
          <div class="si-line" style="background:var(--amber);"></div>
          <div class="si-time">02:00 PM</div>
          <div><div class="si-sub">Thermodynamics of Materials</div><div class="si-room">Room 201 · Prof. Agarwal</div></div>
        </div>
        <div class="si">
          <div class="si-line" style="background:var(--violet);"></div>
          <div class="si-time">04:00 PM</div>
          <div><div class="si-sub">Phase Transformations</div><div class="si-room">LT-3 · Prof. Singh</div></div>
        </div>
      </div>
      <div class="gc">
        <div class="gc-head">
          <div class="gc-title"><span style="font-size:1rem;">📌</span> Latest Notices</div>
          <div class="gc-action">All Notices ›</div>
        </div>
        <div class="ni">
          <div class="ni-dot" style="background:var(--pink);"></div>
          <div class="ni-body"><div class="ni-tag t-u">Urgent</div><div class="ni-txt">Mid-Semester exam dates announced. Check academic portal for full timetable.</div><div class="ni-date">📅 Today · Academic Section</div></div>
        </div>
        <div class="ni">
          <div class="ni-dot" style="background:#A78BFA;"></div>
          <div class="ni-body"><div class="ni-tag t-e">Event</div><div class="ni-txt">Techno-Fest 2026 registrations open. Last date 20th March.</div><div class="ni-date">📅 Yesterday · Student Wing</div></div>
        </div>
        <div class="ni">
          <div class="ni-dot" style="background:var(--cyan);"></div>
          <div class="ni-body"><div class="ni-tag t-a">Admin</div><div class="ni-txt">Submit Bonafide certificate requests via Student Portal before 5 PM.</div><div class="ni-date">📅 2 days ago · Admin Office</div></div>
        </div>
        <div class="ni">
          <div class="ni-dot" style="background:var(--amber);"></div>
          <div class="ni-body"><div class="ni-tag t-h">Hostel</div><div class="ni-txt">Mess menu revised. New timings effective from 15th March.</div><div class="ni-date">📅 3 days ago · Hostel Office</div></div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Quick Links
    st.markdown("""
    <div class="sec-h a4"><div class="sec-t">⚡ Quick Access</div><div class="sec-l"></div></div>
    <div class="three-col a4">
      <div class="qlc">
        <div class="qlc-top"><div class="qlc-icon ic1">📄</div><div class="qlc-arr">↗</div></div>
        <div><div class="qlc-title">Syllabus &amp; Notes</div><div class="qlc-sub">Download PDFs, lecture slides, and study materials</div></div>
        <div><div style="display:flex;justify-content:space-between;font-size:0.63rem;color:var(--muted);margin-bottom:4px;"><span>6 subjects</span><span style="color:var(--cyan);">4 updated</span></div><div class="pb-bg"><div class="pb-fill" style="width:70%;"></div></div></div>
      </div>
      <div class="qlc">
        <div class="qlc-top"><div class="qlc-icon ic3">📝</div><div class="qlc-arr">↗</div></div>
        <div><div class="qlc-title">Previous Year Qs</div><div class="qlc-sub">Exam-ready question bank from last 10 years</div></div>
        <div><div style="display:flex;justify-content:space-between;font-size:0.63rem;color:var(--muted);margin-bottom:4px;"><span>240+ papers</span><span style="color:var(--green);">Ready</span></div><div class="pb-bg"><div class="pb-fill" style="width:100%;background:linear-gradient(90deg,var(--green),var(--cyan));"></div></div></div>
      </div>
      <div class="qlc">
        <div class="qlc-top"><div class="qlc-icon ic2">🏛️</div><div class="qlc-arr">↗</div></div>
        <div><div class="qlc-title">Library Catalog</div><div class="qlc-sub">Search books, journals, and reserve copies online</div></div>
        <div><div style="display:flex;justify-content:space-between;font-size:0.63rem;color:var(--muted);margin-bottom:4px;"><span>1 book issued</span><span style="color:var(--amber);">Due 3 days</span></div><div class="pb-bg"><div class="pb-fill" style="width:38%;background:linear-gradient(90deg,var(--amber),var(--pink));"></div></div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # FAB
    _, col_fab = st.columns([10, 1])
    with col_fab:
        if st.button("🤖 AskMNIT AI", key="fab"):
            st.session_state.page_view = "chatbot"
            st.rerun()

# ==========================================
# 6. CHATBOT
# ==========================================
else:
    with st.sidebar:
        # Back
        if st.button("← Back to Dashboard", use_container_width=True, key="back"):
            st.session_state.page_view = "dashboard"
            st.rerun()

        st.markdown("""
        <div style="padding:16px 4px 10px;">
          <div style="display:flex;align-items:center;gap:10px;padding:13px;background:rgba(0,245,255,0.05);border:1px solid rgba(0,245,255,0.12);border-radius:13px;margin-bottom:14px;">
            <div style="font-size:1.3rem;">🤖</div>
            <div>
              <div style="font-family:'Outfit',sans-serif;font-weight:800;font-size:0.95rem;color:#F0EEFF;">AskMNIT AI</div>
              <div style="font-size:0.6rem;color:rgba(240,238,255,0.35);letter-spacing:1px;text-transform:uppercase;margin-top:2px;">LLaMA 3.3 · 70B</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.button("➕  New Chat", use_container_width=True)

        st.markdown('<div style="padding:8px 4px 4px;font-size:0.58rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:rgba(255,255,255,0.2);">Navigation</div>', unsafe_allow_html=True)

        nav_items = [
            ("🕑", "Chat History"), ("⚙️", "University Tools"), ("📚", "Academics"),
            ("💸", "Admission & Fee"), ("🏢", "Hostel Info"), ("📅", "My Schedule"),
            ("📄", "Syllabus & Notes"), ("📝", "Previous Year Qs"), ("🏛️", "Library Catalog"),
            ("🔬", "Research Portal"), ("🏆", "Placements"), ("📌", "Latest Notices"),
        ]
        for icon, label in nav_items:
            st.button(f"{icon}  {label}", use_container_width=True, key=f"nav_{label}")

        st.markdown("""
        <div style="margin:14px 4px 0;padding:13px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:13px;">
          <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:32px;height:32px;border-radius:8px;background:linear-gradient(135deg,#00F5FF,#7C3AED);display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:800;color:#fff;">SC</div>
            <div>
              <div style="font-size:0.79rem;font-weight:700;color:#F0EEFF;">Sumit Chaudhary</div>
              <div style="font-size:0.62rem;color:rgba(240,238,255,0.38);">Metallurgy · 3rd Year</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Chat header
    st.markdown("""
    <div style="margin-top:8vh;text-align:center;padding-bottom:18px;">
      <div style="font-family:'Outfit',sans-serif;font-weight:900;font-size:3.1rem;
                  background:linear-gradient(90deg,#00F5FF,#7C3AED,#F72585);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                  background-clip:text;line-height:1;letter-spacing:-2px;">
        AskMNIT
      </div>
      <div style="color:rgba(240,238,255,0.42);font-size:0.95rem;margin-top:10px;font-family:'Outfit',sans-serif;">
        Your Intelligent Campus AI · Powered by LLaMA 3.3 70B 🧠
      </div>
      <div style="display:inline-flex;align-items:center;gap:6px;margin-top:12px;
                  background:rgba(6,255,165,0.07);border:1px solid rgba(6,255,165,0.18);
                  border-radius:30px;padding:6px 16px;font-size:0.73rem;font-weight:600;
                  color:#06FFA5;font-family:'Outfit',sans-serif;">
        🟢 Online · Ready to Help
      </div>
    </div>
    """, unsafe_allow_html=True)

    for message in st.session_state.sessions[st.session_state.current_chat]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask anything about MNIT — exams, fees, hostel, schedules..."):
        st.session_state.sessions[st.session_state.current_chat].append({"role": "user", "content": prompt})
        st.session_state.pending_generation = True
        st.rerun()

    if st.session_state.pending_generation:
        user_query = st.session_state.sessions[st.session_state.current_chat][-1]["content"]
        with st.chat_message("assistant"):
            try:
                stream = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are 'AskMNIT', a highly knowledgeable, friendly, and helpful AI assistant "
                                "for students of MNIT Jaipur (Malaviya National Institute of Technology, Jaipur, India). "
                                "Help students with: academic queries, exam schedules, course materials, fee payment, "
                                "hostel info, campus events, placements, research opportunities, and college life. "
                                "Be concise, accurate, warm, and format responses clearly using markdown when helpful."
                            )
                        },
                        {"role": "user", "content": user_query}
                    ],
                    model="llama-3.3-70b-versatile",
                    stream=True
                )
                def gen():
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content
                response_text = st.write_stream(gen())
                st.session_state.sessions[st.session_state.current_chat].append({
                    "role": "assistant", "content": response_text
                })
            except Exception as e:
                st.error(f"Error: {str(e)}")
        st.session_state.pending_generation = False
