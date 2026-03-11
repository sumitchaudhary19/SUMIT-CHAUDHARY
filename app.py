import streamlit as st
from groq import Groq
import base64
import os
import datetime

# ==========================================
# 1. PAGE CONFIG & SECRETS
# ==========================================
st.set_page_config(
    page_title="AskMNIT — Campus Intelligence",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("🚨 GROQ_API_KEY missing in secrets!")
    st.stop()

# ==========================================
# 2. SESSION STATE
# ==========================================
defaults = {
    "page_view": "dashboard",
    "active_nav": "dashboard",
    "chat_sessions": {"Session 1": []},
    "current_chat": "Session 1",
    "pending_generation": False,
    "chat_counter": 1,
    "ai_panel_open": True,
    "ai_messages": [],
    "ai_pending": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ==========================================
# 3. HELPERS
# ==========================================
def get_b64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

logo_b64 = get_b64("mnit_logo.png")
now = datetime.datetime.now()
greeting = "Good Morning" if now.hour < 12 else ("Good Afternoon" if now.hour < 17 else "Good Evening")

# ==========================================
# 4. GLOBAL CSS — WORLD CLASS DESIGN
# ==========================================
SIDEBAR_W = "260px"
AI_PANEL_W = "360px"

css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Clash+Display:wght@400;500;600;700&family=Satoshi:wght@300;400;500;600;700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

:root {{
  --bg-base: #050810;
  --bg-card: rgba(255,255,255,0.04);
  --bg-card-hover: rgba(255,255,255,0.07);
  --border: rgba(255,255,255,0.08);
  --border-accent: rgba(99,179,237,0.3);
  --accent-blue: #3B82F6;
  --accent-cyan: #06B6D4;
  --accent-violet: #8B5CF6;
  --accent-emerald: #10B981;
  --accent-amber: #F59E0B;
  --accent-rose: #F43F5E;
  --text-primary: #F1F5F9;
  --text-secondary: rgba(241,245,249,0.55);
  --text-muted: rgba(241,245,249,0.3);
  --sidebar-w: {SIDEBAR_W};
  --ai-panel-w: {AI_PANEL_W};
  --header-h: 60px;
  --glow-blue: 0 0 40px rgba(59,130,246,0.15);
  --glow-violet: 0 0 40px rgba(139,92,246,0.15);
}}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ overflow-x: hidden; }}

/* ── HIDE STREAMLIT CHROME ── */
section[data-testid="stSidebar"] {{ display: none !important; }}
header[data-testid="stHeader"] {{ display: none !important; }}
footer {{ display: none !important; }}
[data-testid="stToolbar"] {{ display: none !important; }}
[data-testid="stDecoration"] {{ display: none !important; }}
.stDeployButton {{ display: none !important; }}
#MainMenu {{ display: none !important; }}
[data-testid="stMainBlockContainer"] {{ 
    padding: 0 !important; 
    max-width: 100% !important;
}}

/* ── APP CONTAINER ── */
[data-testid="stAppViewContainer"] {{
    background: var(--bg-base) !important;
    background-image: 
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(59,130,246,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(139,92,246,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 40% 30% at 50% 50%, rgba(6,182,212,0.03) 0%, transparent 70%) !important;
    margin-left: var(--sidebar-w) !important;
    width: calc(100% - var(--sidebar-w)) !important;
    min-height: 100vh;
    font-family: 'Plus Jakarta Sans', sans-serif;
    position: relative;
}}

/* ══════════════════════════════════════
   LEFT SIDEBAR
══════════════════════════════════════ */
.sidebar {{
    position: fixed;
    top: 0; left: 0;
    width: var(--sidebar-w);
    height: 100vh;
    background: linear-gradient(180deg, #080C18 0%, #05080F 100%);
    border-right: 1px solid var(--border);
    z-index: 10000;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}}

/* Sidebar top glow line */
.sidebar::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent-blue), var(--accent-violet), transparent);
    opacity: 0.6;
}}

.sidebar-inner {{
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding-bottom: 8px;
    scrollbar-width: thin;
    scrollbar-color: rgba(59,130,246,0.2) transparent;
}}
.sidebar-inner::-webkit-scrollbar {{ width: 3px; }}
.sidebar-inner::-webkit-scrollbar-thumb {{ background: rgba(59,130,246,0.2); border-radius: 4px; }}

/* Brand */
.brand {{
    padding: 20px 20px 18px;
    display: flex;
    align-items: center;
    gap: 12px;
    border-bottom: 1px solid var(--border);
    position: relative;
}}

.brand-logo {{
    width: 40px; height: 40px;
    border-radius: 10px;
    background: linear-gradient(135deg, rgba(59,130,246,0.2), rgba(139,92,246,0.2));
    border: 1px solid rgba(59,130,246,0.3);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
    position: relative;
    overflow: hidden;
}}
.brand-logo::after {{
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: linear-gradient(45deg, transparent 40%, rgba(255,255,255,0.05) 50%, transparent 60%);
    animation: shimmer 3s infinite;
}}
@keyframes shimmer {{
    0% {{ transform: translateX(-100%) translateY(-100%) rotate(45deg); }}
    100% {{ transform: translateX(100%) translateY(100%) rotate(45deg); }}
}}

.brand-text {{ line-height: 1.1; }}
.brand-name {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800;
    font-size: 1.1rem;
    color: var(--text-primary);
    letter-spacing: -0.3px;
}}
.brand-sub {{
    font-size: 0.62rem;
    font-weight: 500;
    color: var(--text-muted);
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-top: 2px;
}}

/* Online status */
.online-badge {{
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 0.62rem;
    color: var(--accent-emerald);
    font-weight: 600;
}}
.online-dot {{
    width: 6px; height: 6px;
    background: var(--accent-emerald);
    border-radius: 50%;
    animation: pulse-green 2s infinite;
}}
@keyframes pulse-green {{
    0%, 100% {{ box-shadow: 0 0 0 0 rgba(16,185,129,0.4); }}
    50% {{ box-shadow: 0 0 0 5px rgba(16,185,129,0); }}
}}

/* Section labels */
.nav-section {{
    padding: 18px 18px 6px;
    font-size: 0.58rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-muted);
}}

/* Nav items */
.nav-item {{
    display: flex;
    align-items: center;
    gap: 11px;
    padding: 9px 14px;
    margin: 2px 8px;
    border-radius: 9px;
    cursor: pointer;
    transition: all 0.18s ease;
    text-decoration: none;
    position: relative;
    overflow: hidden;
}}
.nav-item::before {{
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-violet));
    opacity: 0;
    transition: opacity 0.18s ease;
    border-radius: 9px;
}}
.nav-item:hover::before {{ opacity: 0.08; }}
.nav-item.active::before {{ opacity: 0.12; }}
.nav-item.active {{
    border: 1px solid rgba(59,130,246,0.2);
    box-shadow: 0 2px 12px rgba(59,130,246,0.1);
}}

.nav-item-icon {{
    font-size: 1rem;
    width: 20px;
    text-align: center;
    flex-shrink: 0;
    position: relative; z-index: 1;
}}
.nav-item-label {{
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--text-secondary);
    flex: 1;
    position: relative; z-index: 1;
    transition: color 0.18s;
}}
.nav-item:hover .nav-item-label {{ color: var(--text-primary); }}
.nav-item.active .nav-item-label {{ color: var(--text-primary); font-weight: 600; }}

.nav-badge {{
    font-size: 0.6rem;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 20px;
    position: relative; z-index: 1;
}}
.badge-blue {{ background: rgba(59,130,246,0.2); color: #60A5FA; border: 1px solid rgba(59,130,246,0.3); }}
.badge-green {{ background: rgba(16,185,129,0.15); color: #34D399; border: 1px solid rgba(16,185,129,0.25); }}
.badge-amber {{ background: rgba(245,158,11,0.15); color: #FCD34D; border: 1px solid rgba(245,158,11,0.25); }}
.badge-rose {{ background: rgba(244,63,94,0.15); color: #FB7185; border: 1px solid rgba(244,63,94,0.25); }}

.nav-divider {{
    height: 1px;
    background: var(--border);
    margin: 10px 16px;
}}

/* Sidebar profile */
.sidebar-profile {{
    padding: 14px 16px;
    border-top: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(255,255,255,0.02);
    flex-shrink: 0;
}}
.profile-ava {{
    width: 36px; height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-violet) 100%);
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 0.8rem; color: white;
    flex-shrink: 0;
    border: 2px solid rgba(59,130,246,0.3);
}}
.profile-name {{ font-size: 0.8rem; font-weight: 700; color: var(--text-primary); }}
.profile-sub {{ font-size: 0.65rem; color: var(--text-muted); margin-top: 1px; }}
.profile-menu {{ margin-left: auto; font-size: 0.85rem; color: var(--text-muted); cursor: pointer; }}

/* ══════════════════════════════════════
   TOP HEADER BAR
══════════════════════════════════════ */
.topbar {{
    position: fixed;
    top: 0;
    left: var(--sidebar-w);
    width: calc(100% - var(--sidebar-w));
    height: var(--header-h);
    background: rgba(5,8,16,0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border);
    z-index: 9000;
    display: flex;
    align-items: center;
    padding: 0 28px;
    gap: 16px;
}}

.topbar-breadcrumb {{
    display: flex;
    align-items: center;
    gap: 6px;
    flex: 1;
}}
.breadcrumb-text {{
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-secondary);
}}
.breadcrumb-sep {{ color: var(--text-muted); font-size: 0.8rem; }}
.breadcrumb-active {{ color: var(--text-primary); }}

.topbar-search {{
    flex: 0 0 260px;
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(255,255,255,0.05);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 7px 14px;
    cursor: text;
    transition: all 0.2s;
}}
.topbar-search:hover {{ border-color: rgba(59,130,246,0.3); background: rgba(59,130,246,0.05); }}
.search-icon {{ font-size: 0.85rem; color: var(--text-muted); }}
.search-text {{ font-size: 0.8rem; color: var(--text-muted); user-select: none; }}
.search-kbd {{
    margin-left: auto;
    background: rgba(255,255,255,0.05);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1px 5px;
    font-size: 0.6rem;
    color: var(--text-muted);
    font-family: monospace;
}}

.topbar-actions {{
    display: flex;
    align-items: center;
    gap: 12px;
}}
.topbar-btn {{
    width: 34px; height: 34px;
    border-radius: 8px;
    background: rgba(255,255,255,0.05);
    border: 1px solid var(--border);
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
    transition: all 0.18s;
    position: relative;
    font-size: 0.9rem;
}}
.topbar-btn:hover {{ background: rgba(59,130,246,0.1); border-color: rgba(59,130,246,0.3); }}
.notif-badge {{
    position: absolute;
    top: -3px; right: -3px;
    width: 14px; height: 14px;
    background: var(--accent-rose);
    border-radius: 50%;
    border: 2px solid var(--bg-base);
    font-size: 0.5rem;
    font-weight: 700;
    color: white;
    display: flex; align-items: center; justify-content: center;
}}
.topbar-profile {{
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 5px 10px;
    border-radius: 8px;
    border: 1px solid var(--border);
    cursor: pointer;
    transition: all 0.18s;
}}
.topbar-profile:hover {{ background: rgba(255,255,255,0.05); border-color: rgba(59,130,246,0.3); }}
.tp-ava {{
    width: 26px; height: 26px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-violet));
    display: flex; align-items: center; justify-content: center;
    font-size: 0.65rem; font-weight: 700; color: white;
}}
.tp-name {{ font-size: 0.78rem; font-weight: 600; color: var(--text-primary); }}

/* ══════════════════════════════════════
   MAIN CONTENT LAYOUT (3-column)
══════════════════════════════════════ */
.page-wrapper {{
    padding: calc(var(--header-h) + 20px) 24px 24px 24px;
    display: grid;
    grid-template-columns: 1fr var(--ai-panel-w);
    gap: 20px;
    min-height: 100vh;
    align-items: start;
}}

/* ══════════════════════════════════════
   MAIN DASHBOARD AREA
══════════════════════════════════════ */
.main-area {{
    display: flex;
    flex-direction: column;
    gap: 20px;
    min-width: 0;
}}

/* Welcome Hero */
.hero {{
    background: linear-gradient(135deg, rgba(59,130,246,0.12) 0%, rgba(139,92,246,0.08) 50%, rgba(6,182,212,0.05) 100%);
    border: 1px solid rgba(59,130,246,0.15);
    border-radius: 18px;
    padding: 28px 30px;
    position: relative;
    overflow: hidden;
}}
.hero::after {{
    content: '🎓';
    position: absolute;
    right: 30px; top: 50%;
    transform: translateY(-50%);
    font-size: 4rem;
    opacity: 0.12;
    filter: blur(1px);
}}
.hero-greeting {{
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--accent-cyan);
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 8px;
}}
.hero-title {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800;
    font-size: 1.6rem;
    color: var(--text-primary);
    line-height: 1.2;
    margin-bottom: 10px;
    letter-spacing: -0.5px;
}}
.hero-title span {{ 
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.hero-sub {{
    font-size: 0.85rem;
    color: var(--text-secondary);
    max-width: 480px;
    line-height: 1.6;
    margin-bottom: 20px;
}}
.hero-tags {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}}
.hero-tag {{
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    border: 1px solid;
}}
.tag-blue {{ background: rgba(59,130,246,0.1); color: #60A5FA; border-color: rgba(59,130,246,0.25); }}
.tag-green {{ background: rgba(16,185,129,0.1); color: #34D399; border-color: rgba(16,185,129,0.25); }}
.tag-amber {{ background: rgba(245,158,11,0.1); color: #FCD34D; border-color: rgba(245,158,11,0.25); }}

/* Stats Row */
.stats-row {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
}}
.stat-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 16px;
    transition: all 0.22s ease;
    position: relative;
    overflow: hidden;
    cursor: default;
}}
.stat-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    opacity: 0;
    transition: opacity 0.22s;
}}
.stat-card:hover {{ 
    background: var(--bg-card-hover);
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.3);
}}
.stat-card:hover::before {{ opacity: 1; }}
.stat-card.blue::before {{ background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan)); }}
.stat-card.green::before {{ background: linear-gradient(90deg, var(--accent-emerald), #34D399); }}
.stat-card.amber::before {{ background: linear-gradient(90deg, var(--accent-amber), #FCD34D); }}
.stat-card.rose::before {{ background: linear-gradient(90deg, var(--accent-rose), #FB7185); }}

.stat-icon-wrap {{
    width: 36px; height: 36px;
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
    margin-bottom: 12px;
}}
.icon-blue {{ background: rgba(59,130,246,0.12); }}
.icon-green {{ background: rgba(16,185,129,0.12); }}
.icon-amber {{ background: rgba(245,158,11,0.12); }}
.icon-rose {{ background: rgba(244,63,94,0.12); }}

.stat-value {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800;
    font-size: 1.55rem;
    color: var(--text-primary);
    line-height: 1;
    letter-spacing: -1px;
    margin-bottom: 4px;
}}
.stat-label {{
    font-size: 0.72rem;
    color: var(--text-muted);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 8px;
}}
.stat-chip {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.65rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 20px;
}}
.chip-green {{ background: rgba(16,185,129,0.1); color: #34D399; }}
.chip-amber {{ background: rgba(245,158,11,0.1); color: #FCD34D; }}
.chip-rose {{ background: rgba(244,63,94,0.1); color: #FB7185; }}
.chip-blue {{ background: rgba(59,130,246,0.1); color: #60A5FA; }}

/* Mid row — schedule + notices */
.mid-grid {{
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 16px;
}}

.content-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px;
    transition: border-color 0.2s;
}}
.content-card:hover {{ border-color: rgba(59,130,246,0.15); }}

.card-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
}}
.card-title {{
    font-weight: 700;
    font-size: 0.88rem;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 8px;
}}
.card-action {{
    font-size: 0.72rem;
    color: var(--accent-blue);
    font-weight: 600;
    cursor: pointer;
    transition: opacity 0.18s;
}}
.card-action:hover {{ opacity: 0.7; }}

/* Schedule */
.schedule-item {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    transition: all 0.18s;
}}
.schedule-item:last-child {{ border-bottom: none; padding-bottom: 0; }}
.schedule-item:hover {{ padding-left: 4px; }}

.sched-indicator {{
    width: 3px;
    height: 32px;
    border-radius: 2px;
    flex-shrink: 0;
}}
.sched-time {{
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--text-muted);
    min-width: 65px;
    font-variant-numeric: tabular-nums;
}}
.sched-info {{ flex: 1; min-width: 0; }}
.sched-subject {{
    font-size: 0.83rem;
    font-weight: 600;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 2px;
}}
.sched-meta {{
    font-size: 0.68rem;
    color: var(--text-muted);
}}
.sched-status {{
    font-size: 0.6rem;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 20px;
    flex-shrink: 0;
}}
.status-live {{ background: rgba(16,185,129,0.1); color: #34D399; border: 1px solid rgba(16,185,129,0.2); }}
.status-next {{ background: rgba(245,158,11,0.1); color: #FCD34D; border: 1px solid rgba(245,158,11,0.2); }}
.status-done {{ background: rgba(255,255,255,0.05); color: var(--text-muted); }}

/* Notices */
.notice-item {{
    display: flex;
    gap: 12px;
    padding: 11px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    transition: all 0.18s;
    cursor: pointer;
}}
.notice-item:last-child {{ border-bottom: none; }}
.notice-item:hover {{ padding-left: 4px; }}
.notice-dot-wrap {{
    padding-top: 4px;
    flex-shrink: 0;
}}
.notice-dot {{
    width: 7px; height: 7px;
    border-radius: 50%;
    margin-top: 4px;
}}
.notice-content {{ flex: 1; }}
.notice-text {{
    font-size: 0.8rem;
    color: var(--text-secondary);
    line-height: 1.5;
    margin-bottom: 4px;
}}
.notice-meta {{
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.65rem;
    color: var(--text-muted);
}}
.notice-tag {{
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 0.6rem;
    font-weight: 600;
}}

/* Quick Access */
.quick-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
}}
.quick-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 13px;
    padding: 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
}}
.quick-card:hover {{
    background: var(--bg-card-hover);
    border-color: rgba(59,130,246,0.25);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(59,130,246,0.08);
}}
.quick-icon {{
    width: 38px; height: 38px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}}
.quick-title {{
    font-size: 0.78rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 2px;
}}
.quick-sub {{
    font-size: 0.65rem;
    color: var(--text-muted);
}}
.quick-arrow {{
    margin-left: auto;
    font-size: 0.75rem;
    color: var(--text-muted);
    transition: transform 0.18s;
}}
.quick-card:hover .quick-arrow {{ transform: translateX(3px); color: var(--accent-blue); }}

/* ══════════════════════════════════════
   RIGHT — AI PANEL
══════════════════════════════════════ */
.ai-panel {{
    position: sticky;
    top: calc(var(--header-h) + 20px);
    height: calc(100vh - var(--header-h) - 44px);
    display: flex;
    flex-direction: column;
    background: linear-gradient(180deg, rgba(8,12,24,0.95) 0%, rgba(5,8,16,0.98) 100%);
    border: 1px solid rgba(59,130,246,0.15);
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 0 60px rgba(59,130,246,0.06), inset 0 1px 0 rgba(255,255,255,0.05);
}}

.ai-panel-header {{
    padding: 16px 18px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(59,130,246,0.04);
    flex-shrink: 0;
}}
.ai-avatar {{
    width: 34px; height: 34px;
    border-radius: 10px;
    background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-violet) 100%);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem;
    flex-shrink: 0;
    position: relative;
}}
.ai-avatar::after {{
    content: '';
    position: absolute;
    bottom: -2px; right: -2px;
    width: 10px; height: 10px;
    background: var(--accent-emerald);
    border-radius: 50%;
    border: 2px solid var(--bg-base);
    animation: pulse-green 2s infinite;
}}
.ai-header-info {{ flex: 1; }}
.ai-name {{
    font-weight: 800;
    font-size: 0.88rem;
    color: var(--text-primary);
    letter-spacing: -0.2px;
}}
.ai-status {{
    font-size: 0.65rem;
    color: var(--accent-emerald);
    font-weight: 500;
    margin-top: 1px;
}}
.ai-model-chip {{
    background: rgba(59,130,246,0.1);
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: 6px;
    padding: 3px 8px;
    font-size: 0.6rem;
    font-weight: 700;
    color: #60A5FA;
    letter-spacing: 0.5px;
}}

/* Suggested prompts */
.ai-suggestions {{
    padding: 12px 14px;
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
}}
.suggestion-label {{
    font-size: 0.62rem;
    color: var(--text-muted);
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 8px;
}}
.suggestion-chip {{
    display: inline-block;
    margin: 3px;
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 500;
    color: var(--text-secondary);
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--border);
    cursor: pointer;
    transition: all 0.18s;
    white-space: nowrap;
}}
.suggestion-chip:hover {{
    background: rgba(59,130,246,0.1);
    border-color: rgba(59,130,246,0.3);
    color: var(--text-primary);
}}

/* Chat messages */
.ai-messages {{
    flex: 1;
    overflow-y: auto;
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    scrollbar-width: thin;
    scrollbar-color: rgba(59,130,246,0.15) transparent;
}}
.ai-messages::-webkit-scrollbar {{ width: 3px; }}
.ai-messages::-webkit-scrollbar-thumb {{ background: rgba(59,130,246,0.2); border-radius: 4px; }}

.msg-bubble {{
    max-width: 88%;
    padding: 10px 13px;
    border-radius: 12px;
    font-size: 0.8rem;
    line-height: 1.6;
    animation: fadeUp 0.25s ease;
}}
@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(6px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
.msg-user {{
    align-self: flex-end;
    background: linear-gradient(135deg, rgba(59,130,246,0.25), rgba(139,92,246,0.2));
    border: 1px solid rgba(59,130,246,0.2);
    color: var(--text-primary);
    border-bottom-right-radius: 4px;
}}
.msg-ai {{
    align-self: flex-start;
    background: rgba(255,255,255,0.05);
    border: 1px solid var(--border);
    color: var(--text-secondary);
    border-bottom-left-radius: 4px;
}}
.msg-meta {{
    font-size: 0.6rem;
    color: var(--text-muted);
    margin-top: 3px;
    text-align: right;
}}
.msg-ai .msg-meta {{ text-align: left; }}

/* AI welcome state */
.ai-welcome {{
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 24px;
    text-align: center;
    gap: 12px;
}}
.ai-welcome-icon {{
    width: 54px; height: 54px;
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(59,130,246,0.2), rgba(139,92,246,0.2));
    border: 1px solid rgba(59,130,246,0.2);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.5rem;
    box-shadow: 0 0 30px rgba(59,130,246,0.1);
}}
.ai-welcome-title {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800;
    font-size: 0.95rem;
    color: var(--text-primary);
}}
.ai-welcome-sub {{
    font-size: 0.75rem;
    color: var(--text-secondary);
    line-height: 1.5;
    max-width: 220px;
}}

/* AI input area */
.ai-input-area {{
    padding: 12px 14px;
    border-top: 1px solid var(--border);
    background: rgba(255,255,255,0.02);
    flex-shrink: 0;
}}
.ai-input-row {{
    display: flex;
    align-items: flex-end;
    gap: 8px;
    background: rgba(255,255,255,0.05);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 10px 12px;
    transition: border-color 0.2s;
}}
.ai-input-row:focus-within {{ border-color: rgba(59,130,246,0.4); }}

/* ══════════════════════════════════════
   CHATBOT FULL PAGE
══════════════════════════════════════ */
.chatpage-sidebar {{
    background: linear-gradient(180deg, #080C18 0%, #05080F 100%) !important;
    border-right: 1px solid var(--border) !important;
}}

/* ── SCROLLBAR GLOBAL ── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.08); border-radius: 4px; }}
::-webkit-scrollbar-thumb:hover {{ background: rgba(59,130,246,0.3); }}

/* ── STREAMLIT BUTTON OVERRIDES ── */
.stButton > button {{
    background: linear-gradient(135deg, #3B82F6 0%, #6D28D9 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 9px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 8px 16px !important;
    transition: all 0.18s !important;
    box-shadow: 0 4px 15px rgba(59,130,246,0.2) !important;
}}
.stButton > button:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(59,130,246,0.35) !important;
    opacity: 0.95 !important;
}}

/* ── CHAT INPUT ── */
.stChatInput > div {{
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(59,130,246,0.2) !important;
    border-radius: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}
.stChatInput > div:focus-within {{
    border-color: rgba(59,130,246,0.5) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.08) !important;
}}

/* Streamlit column padding fix */
[data-testid="column"] {{ padding: 0 !important; }}

</style>
"""

st.markdown(css, unsafe_allow_html=True)

# ==========================================
# 5. DASHBOARD VIEW
# ==========================================
if st.session_state.page_view == "dashboard":

    # ── SIDEBAR HTML ──
    st.markdown(f"""
    <div class="sidebar">
      <div class="sidebar-inner">

        <!-- Brand -->
        <div class="brand">
          <div class="brand-logo">🎓</div>
          <div class="brand-text">
            <div class="brand-name">AskMNIT</div>
            <div class="brand-sub">Campus Intelligence</div>
          </div>
          <div class="online-badge">
            <div class="online-dot"></div>
            Live
          </div>
        </div>

        <!-- Main Navigation -->
        <div class="nav-section">Main</div>

        <a class="nav-item active">
          <span class="nav-item-icon">🏠</span>
          <span class="nav-item-label">Dashboard</span>
        </a>
        <a class="nav-item">
          <span class="nav-item-icon">📅</span>
          <span class="nav-item-label">Schedule</span>
          <span class="nav-badge badge-green">Today</span>
        </a>
        <a class="nav-item">
          <span class="nav-item-icon">📚</span>
          <span class="nav-item-label">Academics</span>
        </a>
        <a class="nav-item">
          <span class="nav-item-icon">💰</span>
          <span class="nav-item-label">Fee Portal</span>
          <span class="nav-badge badge-amber">Due</span>
        </a>
        <a class="nav-item">
          <span class="nav-item-icon">🏢</span>
          <span class="nav-item-label">Hostel</span>
        </a>

        <div class="nav-divider"></div>

        <!-- Resources -->
        <div class="nav-section">Resources</div>

        <a class="nav-item">
          <span class="nav-item-icon">📄</span>
          <span class="nav-item-label">Syllabus & Notes</span>
        </a>
        <a class="nav-item">
          <span class="nav-item-icon">📝</span>
          <span class="nav-item-label">Previous Year Qs</span>
        </a>
        <a class="nav-item">
          <span class="nav-item-icon">🏛️</span>
          <span class="nav-item-label">Library Catalog</span>
        </a>
        <a class="nav-item">
          <span class="nav-item-icon">📌</span>
          <span class="nav-item-label">Latest Notices</span>
          <span class="nav-badge badge-rose">3</span>
        </a>
        <a class="nav-item">
          <span class="nav-item-icon">🗓️</span>
          <span class="nav-item-label">Exam Schedule</span>
        </a>
        <a class="nav-item">
          <span class="nav-item-icon">🏆</span>
          <span class="nav-item-label">Results & Grades</span>
        </a>

        <div class="nav-divider"></div>

        <!-- Campus -->
        <div class="nav-section">Campus</div>

        <a class="nav-item">
          <span class="nav-item-icon">🎉</span>
          <span class="nav-item-label">Events & Fests</span>
          <span class="nav-badge badge-blue">New</span>
        </a>
        <a class="nav-item">
          <span class="nav-item-icon">🏋️</span>
          <span class="nav-item-label">Sports & Clubs</span>
        </a>
        <a class="nav-item">
          <span class="nav-item-icon">💼</span>
          <span class="nav-item-label">Placements</span>
        </a>
        <a class="nav-item">
          <span class="nav-item-icon">🔬</span>
          <span class="nav-item-label">Research & Labs</span>
        </a>

        <div class="nav-divider"></div>

        <!-- Account -->
        <div class="nav-section">Account</div>

        <a class="nav-item">
          <span class="nav-item-icon">⚙️</span>
          <span class="nav-item-label">Settings</span>
        </a>
        <a class="nav-item">
          <span class="nav-item-icon">🔔</span>
          <span class="nav-item-label">Notifications</span>
          <span class="nav-badge badge-rose">5</span>
        </a>
        <a class="nav-item">
          <span class="nav-item-icon">🚪</span>
          <span class="nav-item-label">Logout</span>
        </a>

      </div>

      <!-- Profile Card -->
      <div class="sidebar-profile">
        <div class="profile-ava">SC</div>
        <div>
          <div class="profile-name">Sumit Chaudhary</div>
          <div class="profile-sub">B.Tech Metallurgy · 3rd Yr</div>
        </div>
        <div class="profile-menu">⋯</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── TOP BAR ──
    st.markdown("""
    <div class="topbar">
      <div class="topbar-breadcrumb">
        <span class="breadcrumb-text">AskMNIT</span>
        <span class="breadcrumb-sep">›</span>
        <span class="breadcrumb-text breadcrumb-active">Dashboard</span>
      </div>
      <div class="topbar-search">
        <span class="search-icon">🔍</span>
        <span class="search-text">Search anything...</span>
        <span class="search-kbd">⌘K</span>
      </div>
      <div class="topbar-actions">
        <div class="topbar-btn">
          📅
        </div>
        <div class="topbar-btn">
          🔔
          <div class="notif-badge">5</div>
        </div>
        <div class="topbar-profile">
          <div class="tp-ava">SC</div>
          <span class="tp-name">Sumit</span>
          <span style="color:var(--text-muted); font-size:0.7rem; margin-left:4px;">▾</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── PAGE LAYOUT: pure HTML grid ──
    st.markdown("""<div class="page-wrapper">""", unsafe_allow_html=True)

    # ── LEFT/MAIN AREA ──
    st.markdown(f"""
    <div class="main-area">

      <!-- HERO WELCOME -->
      <div class="hero">
        <div class="hero-greeting">✦ {greeting}</div>
        <div class="hero-title">Welcome back, <span>Sumit Chaudhary</span> 👋</div>
        <div class="hero-sub">Here's everything happening at your campus today. Stay on top of your schedule, academics, and campus life — all in one place.</div>
        <div class="hero-tags">
          <div class="hero-tag tag-green">● Semester 6 Active</div>
          <div class="hero-tag tag-blue">⏳ Next class in 20 min</div>
          <div class="hero-tag tag-amber">📌 3 new notices</div>
        </div>
      </div>

      <!-- STATS CARDS -->
      <div class="stats-row">
        <div class="stat-card blue">
          <div class="stat-icon-wrap icon-blue">📊</div>
          <div class="stat-value">78%</div>
          <div class="stat-label">Attendance</div>
          <div class="stat-chip chip-green">▲ Above minimum</div>
        </div>
        <div class="stat-card green">
          <div class="stat-icon-wrap icon-green">⏳</div>
          <div class="stat-value">20m</div>
          <div class="stat-label">Next Class</div>
          <div class="stat-chip chip-amber">⚡ Coming soon</div>
        </div>
        <div class="stat-card amber">
          <div class="stat-icon-wrap icon-amber">📝</div>
          <div class="stat-value">6/8</div>
          <div class="stat-label">Assignments</div>
          <div class="stat-chip chip-rose">● 2 Pending</div>
        </div>
        <div class="stat-card rose">
          <div class="stat-icon-wrap icon-rose">💰</div>
          <div class="stat-value">₹18.5k</div>
          <div class="stat-label">Fee Due</div>
          <div class="stat-chip chip-rose">⚠ 5 days left</div>
        </div>
      </div>

      <!-- SCHEDULE + NOTICES -->
      <div class="mid-grid">

        <!-- Schedule -->
        <div class="content-card">
          <div class="card-header">
            <div class="card-title">📅 Today's Schedule</div>
            <div class="card-action">View Full →</div>
          </div>
          <div class="schedule-item">
            <div class="sched-indicator" style="background:#3B82F6;"></div>
            <div class="sched-time">09:30 AM</div>
            <div class="sched-info">
              <div class="sched-subject">Mineral Processing</div>
              <div class="sched-meta">Room 302 · Prof. R.K. Sharma</div>
            </div>
            <div class="sched-status status-done">Done</div>
          </div>
          <div class="schedule-item">
            <div class="sched-indicator" style="background:#10B981;"></div>
            <div class="sched-time">11:30 AM</div>
            <div class="sched-info">
              <div class="sched-subject">Engineering Materials</div>
              <div class="sched-meta">Metallurgy Lab 1 · Dr. Mehta</div>
            </div>
            <div class="sched-status status-live">● Live</div>
          </div>
          <div class="schedule-item">
            <div class="sched-indicator" style="background:#F59E0B;"></div>
            <div class="sched-time">02:00 PM</div>
            <div class="sched-info">
              <div class="sched-subject">Thermodynamics — II</div>
              <div class="sched-meta">Room 201 · Prof. Agarwal</div>
            </div>
            <div class="sched-status status-next">Next</div>
          </div>
          <div class="schedule-item">
            <div class="sched-indicator" style="background:#8B5CF6;"></div>
            <div class="sched-time">04:00 PM</div>
            <div class="sched-info">
              <div class="sched-subject">Phase Transformations</div>
              <div class="sched-meta">LT-3 · Prof. Singh</div>
            </div>
            <div class="sched-status status-done" style="opacity:0.5;">—</div>
          </div>
          <div class="schedule-item">
            <div class="sched-indicator" style="background:#06B6D4;"></div>
            <div class="sched-time">05:30 PM</div>
            <div class="sched-info">
              <div class="sched-subject">Fluid Mechanics</div>
              <div class="sched-meta">Room 105 · Dr. Verma</div>
            </div>
            <div class="sched-status status-done" style="opacity:0.5;">—</div>
          </div>
        </div>

        <!-- Notices -->
        <div class="content-card">
          <div class="card-header">
            <div class="card-title">📌 Latest Notices</div>
            <div class="card-action">All →</div>
          </div>
          <div class="notice-item">
            <div class="notice-dot-wrap"><div class="notice-dot" style="background:#F43F5E;"></div></div>
            <div class="notice-content">
              <div class="notice-text">Mid-Semester exam dates officially announced. Check your portal for subject-wise schedule.</div>
              <div class="notice-meta">
                <div class="notice-tag" style="background:rgba(244,63,94,0.1);color:#FB7185;">Urgent</div>
                Today · Academic Section
              </div>
            </div>
          </div>
          <div class="notice-item">
            <div class="notice-dot-wrap"><div class="notice-dot" style="background:#3B82F6;"></div></div>
            <div class="notice-content">
              <div class="notice-text">Techfest 2025 registrations are OPEN. Last date to register is 20th March.</div>
              <div class="notice-meta">
                <div class="notice-tag" style="background:rgba(59,130,246,0.1);color:#60A5FA;">Events</div>
                Yesterday
              </div>
            </div>
          </div>
          <div class="notice-item">
            <div class="notice-dot-wrap"><div class="notice-dot" style="background:#10B981;"></div></div>
            <div class="notice-content">
              <div class="notice-text">Bonafide Certificate requests can now be submitted online via the Student Portal.</div>
              <div class="notice-meta">
                <div class="notice-tag" style="background:rgba(16,185,129,0.1);color:#34D399;">Admin</div>
                2 days ago
              </div>
            </div>
          </div>
          <div class="notice-item">
            <div class="notice-dot-wrap"><div class="notice-dot" style="background:#F59E0B;"></div></div>
            <div class="notice-content">
              <div class="notice-text">Hostel mess revised menu & new timings effective 15th March. Feedback form open.</div>
              <div class="notice-meta">
                <div class="notice-tag" style="background:rgba(245,158,11,0.1);color:#FCD34D;">Hostel</div>
                3 days ago
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- QUICK ACCESS -->
      <div class="card-title" style="margin-bottom:12px;">⚡ Quick Access</div>
      <div class="quick-grid">
        <a class="quick-card">
          <div class="quick-icon" style="background:rgba(59,130,246,0.1);">📄</div>
          <div>
            <div class="quick-title">Syllabus & Notes</div>
            <div class="quick-sub">Download materials</div>
          </div>
          <div class="quick-arrow">›</div>
        </a>
        <a class="quick-card">
          <div class="quick-icon" style="background:rgba(16,185,129,0.1);">📝</div>
          <div>
            <div class="quick-title">Previous Year Qs</div>
            <div class="quick-sub">Exam prep bank</div>
          </div>
          <div class="quick-arrow">›</div>
        </a>
        <a class="quick-card">
          <div class="quick-icon" style="background:rgba(245,158,11,0.1);">🏛️</div>
          <div>
            <div class="quick-title">Library Catalog</div>
            <div class="quick-sub">Search & reserve</div>
          </div>
          <div class="quick-arrow">›</div>
        </a>
        <a class="quick-card">
          <div class="quick-icon" style="background:rgba(139,92,246,0.1);">💼</div>
          <div>
            <div class="quick-title">Placements</div>
            <div class="quick-sub">Upcoming drives</div>
          </div>
          <div class="quick-arrow">›</div>
        </a>
        <a class="quick-card">
          <div class="quick-icon" style="background:rgba(244,63,94,0.1);">🏆</div>
          <div>
            <div class="quick-title">Results</div>
            <div class="quick-sub">View grades & CGPA</div>
          </div>
          <div class="quick-arrow">›</div>
        </a>
        <a class="quick-card">
          <div class="quick-icon" style="background:rgba(6,182,212,0.1);">🎉</div>
          <div>
            <div class="quick-title">Events & Fests</div>
            <div class="quick-sub">Campus activities</div>
          </div>
          <div class="quick-arrow">›</div>
        </a>
      </div>

    </div><!-- end main-area -->
    """, unsafe_allow_html=True)

    # ── RIGHT AI PANEL ──
    # We render it via Streamlit components inside a column
    st.markdown("""<div class="ai-panel">

      <div class="ai-panel-header">
        <div class="ai-avatar">🤖</div>
        <div class="ai-header-info">
          <div class="ai-name">AskMNIT AI</div>
          <div class="ai-status">● Online — Ready to help</div>
        </div>
        <div class="ai-model-chip">LLaMA 70B</div>
      </div>

      <div class="ai-suggestions">
        <div class="suggestion-label">Try asking</div>
        <span class="suggestion-chip">📅 When are mid-sems?</span>
        <span class="suggestion-chip">💰 Fee due dates</span>
        <span class="suggestion-chip">🏛️ Library hours</span>
        <span class="suggestion-chip">📝 Exam tips</span>
        <span class="suggestion-chip">🏢 Hostel rules</span>
      </div>
    """, unsafe_allow_html=True)

    # ── AI MESSAGES DISPLAY ──
    if not st.session_state.ai_messages:
        st.markdown("""
        <div class="ai-welcome">
          <div class="ai-welcome-icon">🎓</div>
          <div class="ai-welcome-title">Hey Sumit! I'm AskMNIT</div>
          <div class="ai-welcome-sub">Ask me anything about MNIT — schedules, fees, academics, hostel, exams, placements & more.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="ai-messages">', unsafe_allow_html=True)
        for msg in st.session_state.ai_messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="msg-bubble msg-user">{msg["content"]}<div class="msg-meta">You · just now</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="msg-bubble msg-ai">{msg["content"]}<div class="msg-meta">AskMNIT · just now</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
      <div class="ai-input-area">
        <div style="font-size:0.65rem; color:var(--text-muted); margin-bottom:8px; letter-spacing:0.5px;">↑ Type your question below</div>
      </div>
    </div><!-- end ai-panel -->
    """, unsafe_allow_html=True)

    # Close page-wrapper
    st.markdown("</div>", unsafe_allow_html=True)

    # ── STREAMLIT CHAT INPUT (renders at bottom, we style it) ──
    st.markdown("""
    <style>
    /* Position chat input inside AI panel feel */
    [data-testid="stChatInput"] {{
        position: fixed;
        bottom: 16px;
        right: 20px;
        width: calc(var(--ai-panel-w) - 8px);
        z-index: 8000;
    }}
    </style>
    """.replace("{{", "{").replace("}}", "}"), unsafe_allow_html=True)

    if ai_prompt := st.chat_input("Ask AskMNIT anything about MNIT..."):
        st.session_state.ai_messages.append({"role": "user", "content": ai_prompt})
        st.session_state.ai_pending = True
        st.rerun()

    if st.session_state.ai_pending and st.session_state.ai_messages:
        last_q = st.session_state.ai_messages[-1]["content"]
        try:
            resp = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": """You are AskMNIT — an intelligent, friendly AI assistant for MNIT Jaipur (Malaviya National Institute of Technology, Jaipur) students. 
                    You help with: academic queries, exam schedules, fee details, hostel information, library, placements, events, clubs, and general campus life.
                    Keep answers concise (2-4 sentences), accurate, and student-friendly. Use emojis sparingly. Be warm and helpful."""},
                    {"role": "user", "content": last_q}
                ],
                model="llama-3.3-70b-versatile",
                max_tokens=300,
                stream=False
            )
            reply = resp.choices[0].message.content
            st.session_state.ai_messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            st.session_state.ai_messages.append({"role": "assistant", "content": f"⚠️ Error: {str(e)}"})
        st.session_state.ai_pending = False
        st.rerun()

# ==========================================
# 6. CHATBOT FULL PAGE (optional deep-dive)
# ==========================================
else:
    # Full chatbot page with sidebar
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {{
        background: #050810 !important;
        margin-left: 0 !important;
        width: 100% !important;
    }}
    section[data-testid="stSidebar"] {{
        display: block !important;
        background: linear-gradient(180deg, #080C18 0%, #05080F 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.08) !important;
    }}
    section[data-testid="stSidebar"] .stButton > button {{
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        box-shadow: none !important;
        font-size:0.78rem !important;
        padding: 7px 12px !important;
    }}
    section[data-testid="stSidebar"] .stButton > button:hover {{
        background: rgba(59,130,246,0.12) !important;
        border-color: rgba(59,130,246,0.3) !important;
    }}
    .back-btn > button {{
        background: linear-gradient(135deg, #3B82F6, #6D28D9) !important;
        box-shadow: 0 3px 12px rgba(59,130,246,0.3) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("⬅ Back to Dashboard", use_container_width=True):
            st.session_state.page_view = "dashboard"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<hr style='border-color:rgba(255,255,255,0.07); margin:12px 0;'>", unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;padding:6px 4px 14px;">
          <div style="width:32px;height:32px;border-radius:9px;background:linear-gradient(135deg,#3B82F6,#6D28D9);display:flex;align-items:center;justify-content:center;font-size:0.85rem;">🤖</div>
          <div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:800;font-size:0.88rem;color:#F1F5F9;">AskMNIT AI</div>
            <div style="font-size:0.62rem;color:#10B981;">● Online</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("➕  New Chat", use_container_width=True):
            n = st.session_state.chat_counter + 1
            st.session_state.chat_counter = n
            name = f"Session {n}"
            st.session_state.chat_sessions[name] = []
            st.session_state.current_chat = name

        st.markdown('<p style="color:rgba(255,255,255,0.25);font-size:0.6rem;letter-spacing:1.5px;text-transform:uppercase;margin:14px 0 6px 4px;">Topics</p>', unsafe_allow_html=True)

        nav_items = [
            ("⚙️", "University Tools"),
            ("📚", "Academics"),
            ("💸", "Admission & Fee"),
            ("🏢", "Hostel Info"),
            ("📅", "Schedule"),
            ("📄", "Syllabus & Notes"),
            ("📝", "Previous Year Qs"),
            ("🏛️", "Library Catalog"),
            ("💼", "Placements"),
            ("🎉", "Events & Fests"),
            ("🏆", "Results & Grades"),
        ]
        for icon, label in nav_items:
            st.button(f"{icon}  {label}", use_container_width=True)

        st.markdown("<hr style='border-color:rgba(255,255,255,0.07); margin:12px 0;'>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.2);border-radius:10px;padding:12px;text-align:center;">
          <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:800;font-size:0.82rem;color:#F1F5F9;">Sumit Chaudhary</div>
          <div style="font-size:0.65rem;color:rgba(59,130,246,0.8);margin-top:3px;">B.Tech Metallurgy · Sem 6</div>
        </div>
        """, unsafe_allow_html=True)

    # Chat area
    st.markdown("""
    <div style="max-width:760px;margin:0 auto;padding:30px 20px 10px;">
      <div style="text-align:center;margin-bottom:32px;">
        <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:900;font-size:2.8rem;color:#F1F5F9;letter-spacing:-2px;line-height:1;">AskMNIT</div>
        <div style="font-size:1rem;color:rgba(241,245,249,0.45);margin-top:8px;">Your Intelligent MNIT Campus Assistant</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Render chat history
    for msg in st.session_state.chat_sessions[st.session_state.current_chat]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_prompt := st.chat_input("Ask anything about MNIT Jaipur..."):
        st.session_state.chat_sessions[st.session_state.current_chat].append({"role": "user", "content": user_prompt})
        st.session_state.pending_generation = True
        st.rerun()

    if st.session_state.pending_generation:
        q = st.session_state.chat_sessions[st.session_state.current_chat][-1]["content"]
        with st.chat_message("assistant"):
            try:
                stream = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": """You are AskMNIT — an intelligent, friendly AI assistant for MNIT Jaipur students. 
                        Help with: academic queries, exam schedules, fee, hostel, library, placements, events, and campus life.
                        Be concise, accurate, helpful, and use a warm student-friendly tone."""},
                        *[{"role": m["role"], "content": m["content"]}
                          for m in st.session_state.chat_sessions[st.session_state.current_chat][:-1]],
                        {"role": "user", "content": q}
                    ],
                    model="llama-3.3-70b-versatile",
                    stream=True
                )
                def stream_gen():
                    for chunk in stream:
                        c = chunk.choices[0].delta.content
                        if c:
                            yield c
                response = st.write_stream(stream_gen())
                st.session_state.chat_sessions[st.session_state.current_chat].append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error: {str(e)}")
        st.session_state.pending_generation = False
        st.rerun()
