import streamlit as st
from groq import Groq
import base64, os, datetime

# ── PAGE CONFIG ──
st.set_page_config(
    page_title="AskMNIT — Campus Intelligence",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── SECRETS ──
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("🚨 GROQ_API_KEY missing!")
    st.stop()

# ── SESSION STATE ──
for k, v in {
    "page_view": "dashboard",
    "ai_messages": [],
    "ai_pending": False,
    "chat_sessions": {"Session 1": []},
    "current_chat": "Session 1",
    "pending_generation": False,
    "chat_counter": 1,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── GREETING ──
h = datetime.datetime.now().hour
greeting = "Good Morning" if h < 12 else ("Good Afternoon" if h < 17 else "Good Evening")

# ══════════════════════════════════════════════
# INJECT GLOBAL CSS
# ══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; }
html, body { overflow-x: hidden; }

/* Hide Streamlit chrome */
#MainMenu, header, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
.stDeployButton { display: none !important; }

section[data-testid="stSidebar"] { display: none !important; }

[data-testid="stAppViewContainer"] {
    background: #060912 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stMainBlockContainer"] {
    padding: 0 !important;
    max-width: 100% !important;
}
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

/* ── SIDEBAR ── */
.mnit-sidebar {
    position: fixed;
    top: 0; left: 0;
    width: 255px;
    height: 100vh;
    background: #08091A;
    border-right: 1px solid rgba(255,255,255,0.07);
    z-index: 9999;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}
.mnit-sidebar-scroll {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding-bottom: 8px;
}
.mnit-sidebar-scroll::-webkit-scrollbar { width: 3px; }
.mnit-sidebar-scroll::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.3); border-radius: 4px; }

.sb-brand {
    padding: 18px 18px 16px;
    display: flex;
    align-items: center;
    gap: 11px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.sb-logo {
    width: 38px; height: 38px;
    border-radius: 10px;
    background: linear-gradient(135deg, #3B82F6, #8B5CF6);
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(59,130,246,0.3);
}
.sb-brand-name {
    font-weight: 800;
    font-size: 1rem;
    color: #F1F5F9;
    line-height: 1.1;
}
.sb-brand-sub {
    font-size: 0.6rem;
    color: rgba(241,245,249,0.35);
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-top: 2px;
}
.sb-live {
    margin-left: auto;
    display: flex; align-items: center; gap: 4px;
    font-size: 0.6rem; font-weight: 600;
    color: #10B981;
}
.sb-live-dot {
    width: 6px; height: 6px;
    background: #10B981; border-radius: 50%;
    animation: blink 2s infinite;
}
@keyframes blink {
    0%,100% { opacity: 1; } 50% { opacity: 0.3; }
}

.sb-section {
    padding: 16px 18px 5px;
    font-size: 0.58rem;
    font-weight: 700;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    color: rgba(241,245,249,0.25);
}
.sb-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    margin: 1px 8px;
    border-radius: 9px;
    cursor: pointer;
    transition: all 0.15s ease;
    text-decoration: none;
}
.sb-item:hover { background: rgba(255,255,255,0.05); }
.sb-item.active {
    background: rgba(59,130,246,0.12);
    border: 1px solid rgba(59,130,246,0.2);
}
.sb-icon { font-size: 0.95rem; width: 18px; text-align: center; flex-shrink: 0; }
.sb-label {
    font-size: 0.8rem; font-weight: 500;
    color: rgba(241,245,249,0.6);
    flex: 1;
    transition: color 0.15s;
}
.sb-item:hover .sb-label, .sb-item.active .sb-label { color: #F1F5F9; font-weight: 600; }
.sb-badge {
    font-size: 0.58rem; font-weight: 700;
    padding: 2px 6px; border-radius: 20px;
}
.bdg-blue { background: rgba(59,130,246,0.15); color: #60A5FA; border: 1px solid rgba(59,130,246,0.25); }
.bdg-green { background: rgba(16,185,129,0.12); color: #34D399; border: 1px solid rgba(16,185,129,0.2); }
.bdg-amber { background: rgba(245,158,11,0.12); color: #FCD34D; border: 1px solid rgba(245,158,11,0.2); }
.bdg-rose { background: rgba(244,63,94,0.12); color: #FB7185; border: 1px solid rgba(244,63,94,0.2); }

.sb-divider { height: 1px; background: rgba(255,255,255,0.05); margin: 8px 16px; }

.sb-profile {
    padding: 12px 14px;
    border-top: 1px solid rgba(255,255,255,0.06);
    display: flex; align-items: center; gap: 10px;
    background: rgba(255,255,255,0.02);
    flex-shrink: 0;
}
.sb-ava {
    width: 34px; height: 34px; border-radius: 50%;
    background: linear-gradient(135deg, #3B82F6, #8B5CF6);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem; font-weight: 800; color: white;
    border: 2px solid rgba(59,130,246,0.3); flex-shrink: 0;
}
.sb-pname { font-size: 0.78rem; font-weight: 700; color: #F1F5F9; }
.sb-psub { font-size: 0.62rem; color: rgba(241,245,249,0.35); margin-top: 1px; }

/* ── TOPBAR ── */
.mnit-topbar {
    position: fixed;
    top: 0; left: 255px;
    width: calc(100% - 255px);
    height: 58px;
    background: rgba(6,9,18,0.9);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(255,255,255,0.06);
    z-index: 9000;
    display: flex;
    align-items: center;
    padding: 0 24px;
    gap: 14px;
}
.tb-breadcrumb { flex: 1; display: flex; align-items: center; gap: 6px; }
.tb-bc { font-size: 0.78rem; font-weight: 600; color: rgba(241,245,249,0.45); }
.tb-sep { color: rgba(241,245,249,0.2); }
.tb-bc-active { color: #F1F5F9; }
.tb-search {
    display: flex; align-items: center; gap: 8px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 8px;
    padding: 6px 12px;
    width: 240px;
}
.tb-search:hover { border-color: rgba(59,130,246,0.3); background: rgba(59,130,246,0.04); }
.tb-s-text { font-size: 0.75rem; color: rgba(241,245,249,0.3); flex: 1; }
.tb-kbd {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 4px; padding: 1px 5px;
    font-size: 0.58rem; color: rgba(241,245,249,0.25);
    font-family: monospace;
}
.tb-actions { display: flex; align-items: center; gap: 10px; }
.tb-btn {
    width: 32px; height: 32px; border-radius: 8px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem; cursor: pointer;
    position: relative;
    transition: all 0.15s;
}
.tb-btn:hover { background: rgba(59,130,246,0.08); border-color: rgba(59,130,246,0.25); }
.tb-notif-dot {
    position: absolute; top: -2px; right: -2px;
    width: 12px; height: 12px;
    background: #F43F5E; border-radius: 50%;
    border: 2px solid #060912;
    font-size: 0.45rem; color: white; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
}
.tb-profile {
    display: flex; align-items: center; gap: 7px;
    padding: 4px 10px; border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.07);
    cursor: pointer; transition: all 0.15s;
}
.tb-profile:hover { background: rgba(255,255,255,0.04); }
.tb-pava {
    width: 24px; height: 24px; border-radius: 50%;
    background: linear-gradient(135deg, #3B82F6, #8B5CF6);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.6rem; font-weight: 700; color: white;
}
.tb-pname { font-size: 0.75rem; font-weight: 600; color: #F1F5F9; }

/* ── MAIN LAYOUT ── */
.mnit-layout {
    margin-left: 255px;
    padding-top: 58px;
    display: grid;
    grid-template-columns: 1fr 345px;
    gap: 0;
    min-height: 100vh;
}
.mnit-main {
    padding: 22px 20px 30px 22px;
    overflow: hidden;
}
.mnit-ai-col {
    border-left: 1px solid rgba(255,255,255,0.06);
    background: #07091A;
    display: flex;
    flex-direction: column;
    height: calc(100vh - 58px);
    position: sticky;
    top: 58px;
}

/* ── HERO ── */
.hero {
    background: linear-gradient(135deg, rgba(59,130,246,0.1), rgba(139,92,246,0.06), rgba(6,182,212,0.04));
    border: 1px solid rgba(59,130,246,0.12);
    border-radius: 16px;
    padding: 24px 26px;
    margin-bottom: 18px;
    position: relative; overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute; top: -60px; right: -60px;
    width: 200px; height: 200px; border-radius: 50%;
    background: radial-gradient(circle, rgba(59,130,246,0.08), transparent 70%);
}
.hero-tag { font-size: 0.65rem; font-weight: 700; color: #06B6D4; letter-spacing: 1.2px; text-transform: uppercase; margin-bottom: 8px; }
.hero-title {
    font-weight: 800; font-size: 1.55rem;
    color: #F1F5F9; line-height: 1.2;
    letter-spacing: -0.5px; margin-bottom: 8px;
}
.hero-title span {
    background: linear-gradient(90deg, #3B82F6, #06B6D4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub { font-size: 0.82rem; color: rgba(241,245,249,0.5); line-height: 1.6; margin-bottom: 16px; }
.hero-chips { display: flex; gap: 8px; flex-wrap: wrap; }
.hchip {
    display: flex; align-items: center; gap: 5px;
    padding: 4px 11px; border-radius: 20px;
    font-size: 0.68rem; font-weight: 600;
}
.hc-green { background: rgba(16,185,129,0.1); color: #34D399; border: 1px solid rgba(16,185,129,0.2); }
.hc-blue  { background: rgba(59,130,246,0.1); color: #60A5FA; border: 1px solid rgba(59,130,246,0.2); }
.hc-amber { background: rgba(245,158,11,0.1); color: #FCD34D; border: 1px solid rgba(245,158,11,0.2); }

/* ── STATS ── */
.stats-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-bottom: 18px; }
.scard {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 13px; padding: 16px 14px;
    transition: all 0.2s ease;
    position: relative; overflow: hidden;
}
.scard::after {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    opacity: 0; transition: opacity 0.2s;
}
.scard:hover { background: rgba(255,255,255,0.05); transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.25); }
.scard:hover::after { opacity: 1; }
.scard.sc-blue::after  { background: linear-gradient(90deg, #3B82F6, #06B6D4); }
.scard.sc-green::after { background: linear-gradient(90deg, #10B981, #34D399); }
.scard.sc-amber::after { background: linear-gradient(90deg, #F59E0B, #FCD34D); }
.scard.sc-rose::after  { background: linear-gradient(90deg, #F43F5E, #FB7185); }
.sc-ico {
    width: 32px; height: 32px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem; margin-bottom: 10px;
}
.ico-b { background: rgba(59,130,246,0.1); }
.ico-g { background: rgba(16,185,129,0.1); }
.ico-a { background: rgba(245,158,11,0.1); }
.ico-r { background: rgba(244,63,94,0.1); }
.sc-val { font-weight: 800; font-size: 1.5rem; color: #F1F5F9; letter-spacing: -1px; line-height: 1; margin-bottom: 3px; }
.sc-lbl { font-size: 0.68rem; color: rgba(241,245,249,0.35); text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 7px; }
.sc-chip { display: inline-flex; align-items: center; gap: 3px; font-size: 0.62rem; font-weight: 600; padding: 2px 7px; border-radius: 20px; }
.ch-g { background: rgba(16,185,129,0.1); color: #34D399; }
.ch-a { background: rgba(245,158,11,0.1); color: #FCD34D; }
.ch-r { background: rgba(244,63,94,0.1); color: #FB7185; }
.ch-b { background: rgba(59,130,246,0.1); color: #60A5FA; }

/* ── MID GRID ── */
.mid-grid { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 14px; margin-bottom: 18px; }
.ccard {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 18px;
    transition: border-color 0.2s;
}
.ccard:hover { border-color: rgba(59,130,246,0.15); }
.ccard-hd { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.ccard-title { font-weight: 700; font-size: 0.85rem; color: #F1F5F9; display: flex; align-items: center; gap: 7px; }
.ccard-link { font-size: 0.7rem; color: #3B82F6; font-weight: 600; cursor: pointer; }
.ccard-link:hover { opacity: 0.7; }

/* Schedule */
.sched-item { display: flex; align-items: center; gap: 10px; padding: 9px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
.sched-item:last-child { border-bottom: none; padding-bottom: 0; }
.sched-bar { width: 3px; height: 28px; border-radius: 2px; flex-shrink: 0; }
.sched-time { font-size: 0.68rem; font-weight: 700; color: rgba(241,245,249,0.35); min-width: 62px; font-variant-numeric: tabular-nums; }
.sched-info { flex: 1; }
.sched-subj { font-size: 0.8rem; font-weight: 600; color: #F1F5F9; margin-bottom: 1px; }
.sched-meta { font-size: 0.65rem; color: rgba(241,245,249,0.3); }
.sched-st { font-size: 0.58rem; font-weight: 700; padding: 2px 7px; border-radius: 20px; flex-shrink: 0; }
.st-live { background: rgba(16,185,129,0.1); color: #34D399; border: 1px solid rgba(16,185,129,0.2); }
.st-next { background: rgba(245,158,11,0.1); color: #FCD34D; border: 1px solid rgba(245,158,11,0.2); }
.st-done { background: rgba(255,255,255,0.04); color: rgba(241,245,249,0.25); }

/* Notices */
.notice-item { display: flex; gap: 10px; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.04); cursor: pointer; transition: padding-left 0.15s; }
.notice-item:last-child { border-bottom: none; }
.notice-item:hover { padding-left: 4px; }
.n-dot { width: 7px; height: 7px; border-radius: 50%; margin-top: 5px; flex-shrink: 0; }
.n-text { font-size: 0.78rem; color: rgba(241,245,249,0.65); line-height: 1.5; margin-bottom: 4px; }
.n-meta { display: flex; align-items: center; gap: 5px; font-size: 0.62rem; color: rgba(241,245,249,0.3); }
.n-tag { padding: 1px 6px; border-radius: 4px; font-size: 0.58rem; font-weight: 700; }

/* ── QUICK ACCESS ── */
.qa-title { font-size: 0.7rem; font-weight: 700; color: rgba(241,245,249,0.35); letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 12px; }
.qa-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; }
.qa-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 14px;
    display: flex; align-items: center; gap: 10px;
    cursor: pointer; transition: all 0.18s ease; text-decoration: none;
}
.qa-card:hover { background: rgba(255,255,255,0.05); border-color: rgba(59,130,246,0.2); transform: translateY(-2px); box-shadow: 0 6px 18px rgba(59,130,246,0.07); }
.qa-ico { width: 34px; height: 34px; border-radius: 9px; display: flex; align-items: center; justify-content: center; font-size: 1rem; flex-shrink: 0; }
.qa-name { font-size: 0.75rem; font-weight: 700; color: #F1F5F9; margin-bottom: 1px; }
.qa-sub { font-size: 0.62rem; color: rgba(241,245,249,0.3); }
.qa-arr { margin-left: auto; font-size: 0.7rem; color: rgba(241,245,249,0.2); transition: all 0.15s; }
.qa-card:hover .qa-arr { color: #3B82F6; transform: translateX(2px); }

/* ── AI PANEL ── */
.ai-hd {
    padding: 14px 16px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    display: flex; align-items: center; gap: 10px;
    background: rgba(59,130,246,0.03);
    flex-shrink: 0;
}
.ai-ava {
    width: 32px; height: 32px; border-radius: 9px;
    background: linear-gradient(135deg, #3B82F6, #8B5CF6);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem; flex-shrink: 0; position: relative;
}
.ai-ava::after {
    content: '';
    position: absolute; bottom: -2px; right: -2px;
    width: 9px; height: 9px; background: #10B981;
    border-radius: 50%; border: 2px solid #07091A;
    animation: blink 2s infinite;
}
.ai-hd-info { flex: 1; }
.ai-hd-name { font-weight: 800; font-size: 0.85rem; color: #F1F5F9; }
.ai-hd-status { font-size: 0.62rem; color: #10B981; margin-top: 1px; }
.ai-model { background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.2); border-radius: 6px; padding: 2px 7px; font-size: 0.58rem; font-weight: 700; color: #60A5FA; }

.ai-chips {
    padding: 10px 14px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    flex-shrink: 0;
}
.ai-chips-lbl { font-size: 0.58rem; color: rgba(241,245,249,0.25); font-weight: 700; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 7px; }
.ai-chip {
    display: inline-block; margin: 2px;
    padding: 4px 9px; border-radius: 20px;
    font-size: 0.67rem; font-weight: 500;
    color: rgba(241,245,249,0.55);
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    cursor: pointer; transition: all 0.15s;
}
.ai-chip:hover { background: rgba(59,130,246,0.1); border-color: rgba(59,130,246,0.25); color: #F1F5F9; }

.ai-msgs {
    flex: 1; overflow-y: auto; padding: 14px 12px;
    display: flex; flex-direction: column; gap: 10px;
}
.ai-msgs::-webkit-scrollbar { width: 3px; }
.ai-msgs::-webkit-scrollbar-thumb { background: rgba(59,130,246,0.2); border-radius: 4px; }

.ai-welcome {
    flex: 1; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    padding: 20px; text-align: center; gap: 10px;
}
.ai-w-ico {
    width: 50px; height: 50px; border-radius: 14px;
    background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(139,92,246,0.15));
    border: 1px solid rgba(59,130,246,0.2);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem;
    box-shadow: 0 0 24px rgba(59,130,246,0.1);
}
.ai-w-title { font-weight: 800; font-size: 0.9rem; color: #F1F5F9; }
.ai-w-sub { font-size: 0.72rem; color: rgba(241,245,249,0.4); line-height: 1.5; max-width: 200px; }

.msg-u {
    align-self: flex-end; max-width: 85%;
    padding: 9px 12px; border-radius: 11px;
    background: linear-gradient(135deg, rgba(59,130,246,0.22), rgba(139,92,246,0.18));
    border: 1px solid rgba(59,130,246,0.18);
    font-size: 0.78rem; color: #F1F5F9; line-height: 1.55;
    border-bottom-right-radius: 3px;
    animation: msgIn 0.2s ease;
}
.msg-a {
    align-self: flex-start; max-width: 90%;
    padding: 9px 12px; border-radius: 11px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    font-size: 0.78rem; color: rgba(241,245,249,0.75); line-height: 1.55;
    border-bottom-left-radius: 3px;
    animation: msgIn 0.2s ease;
}
@keyframes msgIn {
    from { opacity: 0; transform: translateY(5px); }
    to   { opacity: 1; transform: translateY(0); }
}
.msg-meta { font-size: 0.58rem; color: rgba(241,245,249,0.2); margin-top: 3px; }
.msg-u .msg-meta { text-align: right; }

.ai-inp-area {
    padding: 10px 12px;
    border-top: 1px solid rgba(255,255,255,0.06);
    flex-shrink: 0;
}

/* Chat input override */
.stChatInput > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(59,130,246,0.2) !important;
    border-radius: 11px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.8rem !important;
    color: #F1F5F9 !important;
}
.stChatInput > div:focus-within {
    border-color: rgba(59,130,246,0.45) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.07) !important;
}

/* Chat messages (full page) */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
    padding: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.85rem !important;
    color: rgba(241,245,249,0.85) !important;
}

/* Streamlit buttons */
.stButton > button {
    background: linear-gradient(135deg, #3B82F6, #6D28D9) !important;
    color: white !important; border: none !important;
    border-radius: 9px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important; font-size: 0.8rem !important;
    padding: 8px 16px !important;
    box-shadow: 0 4px 14px rgba(59,130,246,0.2) !important;
    transition: all 0.18s !important;
}
.stButton > button:hover {
    opacity: 0.9 !important; transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(59,130,246,0.35) !important;
}

/* Full chatbot page sidebar */
section[data-testid="stSidebar"].chatbot-open {
    display: block !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# DASHBOARD PAGE
# ══════════════════════════════════════════════
if st.session_state.page_view == "dashboard":

    # ── SIDEBAR ──
    st.markdown("""
    <div class="mnit-sidebar">
      <div class="mnit-sidebar-scroll">

        <div class="sb-brand">
          <div class="sb-logo">🎓</div>
          <div>
            <div class="sb-brand-name">AskMNIT</div>
            <div class="sb-brand-sub">Campus Intelligence</div>
          </div>
          <div class="sb-live"><div class="sb-live-dot"></div>Live</div>
        </div>

        <div class="sb-section">Main</div>
        <a class="sb-item active"><span class="sb-icon">🏠</span><span class="sb-label">Dashboard</span></a>
        <a class="sb-item"><span class="sb-icon">📅</span><span class="sb-label">Schedule</span><span class="sb-badge bdg-green">Today</span></a>
        <a class="sb-item"><span class="sb-icon">📚</span><span class="sb-label">Academics</span></a>
        <a class="sb-item"><span class="sb-icon">💰</span><span class="sb-label">Fee Portal</span><span class="sb-badge bdg-amber">Due</span></a>
        <a class="sb-item"><span class="sb-icon">🏢</span><span class="sb-label">Hostel</span></a>

        <div class="sb-divider"></div>
        <div class="sb-section">Resources</div>
        <a class="sb-item"><span class="sb-icon">📄</span><span class="sb-label">Syllabus & Notes</span></a>
        <a class="sb-item"><span class="sb-icon">📝</span><span class="sb-label">Previous Year Qs</span></a>
        <a class="sb-item"><span class="sb-icon">🏛️</span><span class="sb-label">Library Catalog</span></a>
        <a class="sb-item"><span class="sb-icon">📌</span><span class="sb-label">Latest Notices</span><span class="sb-badge bdg-rose">3</span></a>
        <a class="sb-item"><span class="sb-icon">🗓️</span><span class="sb-label">Exam Schedule</span></a>
        <a class="sb-item"><span class="sb-icon">🏆</span><span class="sb-label">Results & Grades</span></a>

        <div class="sb-divider"></div>
        <div class="sb-section">Campus</div>
        <a class="sb-item"><span class="sb-icon">🎉</span><span class="sb-label">Events & Fests</span><span class="sb-badge bdg-blue">New</span></a>
        <a class="sb-item"><span class="sb-icon">🏋️</span><span class="sb-label">Sports & Clubs</span></a>
        <a class="sb-item"><span class="sb-icon">💼</span><span class="sb-label">Placements</span></a>
        <a class="sb-item"><span class="sb-icon">🔬</span><span class="sb-label">Research & Labs</span></a>

        <div class="sb-divider"></div>
        <div class="sb-section">Account</div>
        <a class="sb-item"><span class="sb-icon">⚙️</span><span class="sb-label">Settings</span></a>
        <a class="sb-item"><span class="sb-icon">🔔</span><span class="sb-label">Notifications</span><span class="sb-badge bdg-rose">5</span></a>
        <a class="sb-item"><span class="sb-icon">🚪</span><span class="sb-label">Logout</span></a>

      </div>
      <div class="sb-profile">
        <div class="sb-ava">SC</div>
        <div>
          <div class="sb-pname">Sumit Chaudhary</div>
          <div class="sb-psub">B.Tech Metallurgy · 3rd Yr</div>
        </div>
        <span style="margin-left:auto;color:rgba(241,245,249,0.2);font-size:0.9rem;cursor:pointer;">⋯</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── TOPBAR ──
    st.markdown("""
    <div class="mnit-topbar">
      <div class="tb-breadcrumb">
        <span class="tb-bc">AskMNIT</span>
        <span class="tb-sep">›</span>
        <span class="tb-bc tb-bc-active">Dashboard</span>
      </div>
      <div class="tb-search">
        <span style="font-size:0.8rem;">🔍</span>
        <span class="tb-s-text">Search anything...</span>
        <span class="tb-kbd">⌘K</span>
      </div>
      <div class="tb-actions">
        <div class="tb-btn">📅</div>
        <div class="tb-btn">
          🔔
          <div class="tb-notif-dot">5</div>
        </div>
        <div class="tb-profile">
          <div class="tb-pava">SC</div>
          <span class="tb-pname">Sumit</span>
          <span style="color:rgba(241,245,249,0.25);font-size:0.65rem;margin-left:3px;">▾</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── LAYOUT WRAPPER ──
    st.markdown('<div class="mnit-layout">', unsafe_allow_html=True)

    # ── LEFT: MAIN CONTENT ──
    st.markdown(f"""
    <div class="mnit-main">

      <!-- HERO -->
      <div class="hero">
        <div class="hero-tag">✦ {greeting}</div>
        <div class="hero-title">Welcome back, <span>Sumit Chaudhary</span> 👋</div>
        <div class="hero-sub">Here's everything happening on campus today. Stay on top of your schedule, academics, and campus life.</div>
        <div class="hero-chips">
          <div class="hchip hc-green">● Semester 6 Active</div>
          <div class="hchip hc-blue">⏳ Next class in 20 min</div>
          <div class="hchip hc-amber">📌 3 new notices</div>
        </div>
      </div>

      <!-- STATS -->
      <div class="stats-row">
        <div class="scard sc-blue">
          <div class="sc-ico ico-b">📊</div>
          <div class="sc-val">78%</div>
          <div class="sc-lbl">Attendance</div>
          <span class="sc-chip ch-g">▲ Above minimum</span>
        </div>
        <div class="scard sc-green">
          <div class="sc-ico ico-g">⏳</div>
          <div class="sc-val">20m</div>
          <div class="sc-lbl">Next Class</div>
          <span class="sc-chip ch-a">⚡ Coming soon</span>
        </div>
        <div class="scard sc-amber">
          <div class="sc-ico ico-a">📝</div>
          <div class="sc-val">6/8</div>
          <div class="sc-lbl">Assignments</div>
          <span class="sc-chip ch-r">● 2 Pending</span>
        </div>
        <div class="scard sc-rose">
          <div class="sc-ico ico-r">💰</div>
          <div class="sc-val">₹18.5k</div>
          <div class="sc-lbl">Fee Due</div>
          <span class="sc-chip ch-r">⚠ 5 days left</span>
        </div>
      </div>

      <!-- SCHEDULE + NOTICES -->
      <div class="mid-grid">
        <div class="ccard">
          <div class="ccard-hd">
            <div class="ccard-title">📅 Today's Schedule</div>
            <div class="ccard-link">View Full →</div>
          </div>
          <div class="sched-item">
            <div class="sched-bar" style="background:#3B82F6;"></div>
            <div class="sched-time">09:30 AM</div>
            <div class="sched-info">
              <div class="sched-subj">Mineral Processing</div>
              <div class="sched-meta">Room 302 · Prof. R.K. Sharma</div>
            </div>
            <div class="sched-st st-done">Done</div>
          </div>
          <div class="sched-item">
            <div class="sched-bar" style="background:#10B981;"></div>
            <div class="sched-time">11:30 AM</div>
            <div class="sched-info">
              <div class="sched-subj">Engineering Materials</div>
              <div class="sched-meta">Metallurgy Lab 1 · Dr. Mehta</div>
            </div>
            <div class="sched-st st-live">● Live</div>
          </div>
          <div class="sched-item">
            <div class="sched-bar" style="background:#F59E0B;"></div>
            <div class="sched-time">02:00 PM</div>
            <div class="sched-info">
              <div class="sched-subj">Thermodynamics — II</div>
              <div class="sched-meta">Room 201 · Prof. Agarwal</div>
            </div>
            <div class="sched-st st-next">Next</div>
          </div>
          <div class="sched-item">
            <div class="sched-bar" style="background:#8B5CF6;"></div>
            <div class="sched-time">04:00 PM</div>
            <div class="sched-info">
              <div class="sched-subj">Phase Transformations</div>
              <div class="sched-meta">LT-3 · Prof. Singh</div>
            </div>
            <div class="sched-st st-done" style="opacity:0.4;">—</div>
          </div>
          <div class="sched-item">
            <div class="sched-bar" style="background:#06B6D4;"></div>
            <div class="sched-time">05:30 PM</div>
            <div class="sched-info">
              <div class="sched-subj">Fluid Mechanics</div>
              <div class="sched-meta">Room 105 · Dr. Verma</div>
            </div>
            <div class="sched-st st-done" style="opacity:0.4;">—</div>
          </div>
        </div>

        <div class="ccard">
          <div class="ccard-hd">
            <div class="ccard-title">📌 Latest Notices</div>
            <div class="ccard-link">All →</div>
          </div>
          <div class="notice-item">
            <div class="n-dot" style="background:#F43F5E;"></div>
            <div>
              <div class="n-text">Mid-Semester exam dates officially announced. Check portal for schedule.</div>
              <div class="n-meta"><span class="n-tag" style="background:rgba(244,63,94,0.1);color:#FB7185;">Urgent</span>Today · Academic</div>
            </div>
          </div>
          <div class="notice-item">
            <div class="n-dot" style="background:#3B82F6;"></div>
            <div>
              <div class="n-text">Techfest 2025 registrations OPEN. Last date: 20th March.</div>
              <div class="n-meta"><span class="n-tag" style="background:rgba(59,130,246,0.1);color:#60A5FA;">Events</span>Yesterday</div>
            </div>
          </div>
          <div class="notice-item">
            <div class="n-dot" style="background:#10B981;"></div>
            <div>
              <div class="n-text">Bonafide Certificate requests can now be submitted online.</div>
              <div class="n-meta"><span class="n-tag" style="background:rgba(16,185,129,0.1);color:#34D399;">Admin</span>2 days ago</div>
            </div>
          </div>
          <div class="notice-item">
            <div class="n-dot" style="background:#F59E0B;"></div>
            <div>
              <div class="n-text">Hostel mess revised menu effective 15th March. Feedback open.</div>
              <div class="n-meta"><span class="n-tag" style="background:rgba(245,158,11,0.1);color:#FCD34D;">Hostel</span>3 days ago</div>
            </div>
          </div>
        </div>
      </div>

      <!-- QUICK ACCESS -->
      <div class="qa-title">⚡ Quick Access</div>
      <div class="qa-grid">
        <a class="qa-card"><div class="qa-ico" style="background:rgba(59,130,246,0.1);">📄</div><div><div class="qa-name">Syllabus & Notes</div><div class="qa-sub">Download materials</div></div><div class="qa-arr">›</div></a>
        <a class="qa-card"><div class="qa-ico" style="background:rgba(16,185,129,0.1);">📝</div><div><div class="qa-name">Previous Year Qs</div><div class="qa-sub">Exam prep</div></div><div class="qa-arr">›</div></a>
        <a class="qa-card"><div class="qa-ico" style="background:rgba(245,158,11,0.1);">🏛️</div><div><div class="qa-name">Library Catalog</div><div class="qa-sub">Search & reserve</div></div><div class="qa-arr">›</div></a>
        <a class="qa-card"><div class="qa-ico" style="background:rgba(139,92,246,0.1);">💼</div><div><div class="qa-name">Placements</div><div class="qa-sub">Upcoming drives</div></div><div class="qa-arr">›</div></a>
        <a class="qa-card"><div class="qa-ico" style="background:rgba(244,63,94,0.1);">🏆</div><div><div class="qa-name">Results</div><div class="qa-sub">Grades & CGPA</div></div><div class="qa-arr">›</div></a>
        <a class="qa-card"><div class="qa-ico" style="background:rgba(6,182,212,0.1);">🎉</div><div><div class="qa-name">Events & Fests</div><div class="qa-sub">Campus activities</div></div><div class="qa-arr">›</div></a>
      </div>

    </div>
    """, unsafe_allow_html=True)

    # ── RIGHT: AI PANEL (pure HTML header + chips) ──
    st.markdown("""
    <div class="mnit-ai-col">
      <div class="ai-hd">
        <div class="ai-ava">🤖</div>
        <div class="ai-hd-info">
          <div class="ai-hd-name">AskMNIT AI</div>
          <div class="ai-hd-status">● Online · Ready to help</div>
        </div>
        <div class="ai-model">LLaMA 70B</div>
      </div>
      <div class="ai-chips">
        <div class="ai-chips-lbl">Try asking</div>
        <span class="ai-chip">📅 Mid-sem dates?</span>
        <span class="ai-chip">💰 Fee due?</span>
        <span class="ai-chip">🏛️ Library hours?</span>
        <span class="ai-chip">📝 Exam tips</span>
        <span class="ai-chip">🏢 Hostel rules</span>
      </div>
    """, unsafe_allow_html=True)

    # AI messages display
    if not st.session_state.ai_messages:
        st.markdown("""
      <div class="ai-welcome">
        <div class="ai-w-ico">🎓</div>
        <div class="ai-w-title">Hey Sumit! I'm AskMNIT</div>
        <div class="ai-w-sub">Ask me anything about MNIT — schedules, fees, academics, hostel, exams & more.</div>
      </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="ai-msgs">', unsafe_allow_html=True)
        for msg in st.session_state.ai_messages:
            css_cls = "msg-u" if msg["role"] == "user" else "msg-a"
            meta = "You" if msg["role"] == "user" else "AskMNIT AI"
            st.markdown(f'<div class="{css_cls}">{msg["content"]}<div class="msg-meta">{meta}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
      <div class="ai-inp-area">
        <div style="font-size:0.62rem;color:rgba(241,245,249,0.2);margin-bottom:6px;letter-spacing:0.5px;">↑ Ask anything about MNIT</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Close layout
    st.markdown('</div>', unsafe_allow_html=True)

    # ── POSITION CHAT INPUT INSIDE AI PANEL ──
    st.markdown("""
    <style>
    [data-testid="stChatInputContainer"] {
        position: fixed !important;
        bottom: 0px !important;
        right: 0px !important;
        width: 345px !important;
        padding: 10px 12px !important;
        background: #07091A !important;
        border-top: 1px solid rgba(255,255,255,0.06) !important;
        z-index: 9500 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    if ai_prompt := st.chat_input("Ask AskMNIT anything about MNIT...", key="ai_panel_input"):
        st.session_state.ai_messages.append({"role": "user", "content": ai_prompt})
        st.session_state.ai_pending = True
        st.rerun()

    if st.session_state.ai_pending and st.session_state.ai_messages:
        q = st.session_state.ai_messages[-1]["content"]
        try:
            resp = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are AskMNIT — a smart, friendly AI assistant for MNIT Jaipur students. Help with academics, fees, hostel, schedule, placements, events, library, and campus life. Be concise (2-4 sentences), warm, and accurate."},
                    {"role": "user", "content": q}
                ],
                model="llama-3.3-70b-versatile",
                max_tokens=250
            )
            reply = resp.choices[0].message.content
        except Exception as e:
            reply = f"⚠️ Sorry, something went wrong: {str(e)}"
        st.session_state.ai_messages.append({"role": "assistant", "content": reply})
        st.session_state.ai_pending = False
        st.rerun()


# ══════════════════════════════════════════════
# FULL CHATBOT PAGE
# ══════════════════════════════════════════════
else:
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { margin-left: 0 !important; width: 100% !important; }
    section[data-testid="stSidebar"] {
        display: block !important;
        background: #08091A !important;
        border-right: 1px solid rgba(255,255,255,0.07) !important;
    }
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        box-shadow: none !important;
        font-size: 0.76rem !important;
        padding: 7px 12px !important;
        text-align: left !important;
        justify-content: flex-start !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(59,130,246,0.1) !important;
        border-color: rgba(59,130,246,0.25) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        if st.button("⬅  Back to Dashboard", use_container_width=True):
            st.session_state.page_view = "dashboard"
            st.rerun()

        st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:12px 0;'>", unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;padding:4px 4px 12px;">
          <div style="width:30px;height:30px;border-radius:8px;background:linear-gradient(135deg,#3B82F6,#8B5CF6);display:flex;align-items:center;justify-content:center;font-size:0.8rem;">🤖</div>
          <div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:800;font-size:0.85rem;color:#F1F5F9;">AskMNIT AI</div>
            <div style="font-size:0.6rem;color:#10B981;margin-top:1px;">● Online</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("➕  New Chat", use_container_width=True):
            n = st.session_state.chat_counter + 1
            st.session_state.chat_counter = n
            name = f"Session {n}"
            st.session_state.chat_sessions[name] = []
            st.session_state.current_chat = name
            st.rerun()

        st.markdown('<p style="color:rgba(241,245,249,0.2);font-size:0.58rem;letter-spacing:1.5px;text-transform:uppercase;margin:14px 0 6px 2px;">Topics</p>', unsafe_allow_html=True)

        for icon, label in [
            ("⚙️", "University Tools"), ("📚", "Academics"),
            ("💸", "Admission & Fee"), ("🏢", "Hostel Info"),
            ("📅", "Schedule"), ("📄", "Syllabus & Notes"),
            ("📝", "Previous Year Qs"), ("🏛️", "Library Catalog"),
            ("💼", "Placements"), ("🎉", "Events & Fests"),
            ("🏆", "Results & Grades"), ("🔬", "Research & Labs"),
        ]:
            st.button(f"{icon}  {label}", use_container_width=True)

        st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:14px 0 10px;'>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(59,130,246,0.07);border:1px solid rgba(59,130,246,0.15);border-radius:10px;padding:12px;text-align:center;">
          <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:800;font-size:0.82rem;color:#F1F5F9;">Sumit Chaudhary</div>
          <div style="font-size:0.65rem;color:rgba(99,130,246,0.8);margin-top:3px;">B.Tech Metallurgy · Sem 6</div>
        </div>
        """, unsafe_allow_html=True)

    # ── CHAT AREA ──
    st.markdown("""
    <div style="max-width:720px;margin:0 auto;padding:32px 20px 80px;">
      <div style="text-align:center;margin-bottom:28px;">
        <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:900;font-size:2.6rem;
             background:linear-gradient(90deg,#3B82F6,#8B5CF6);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;
             background-clip:text;letter-spacing:-2px;line-height:1;">AskMNIT</div>
        <div style="font-size:0.9rem;color:rgba(241,245,249,0.35);margin-top:8px;">Your Intelligent MNIT Campus Assistant</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    msgs = st.session_state.chat_sessions[st.session_state.current_chat]
    for msg in msgs:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_prompt := st.chat_input("Ask anything about MNIT Jaipur...", key="chat_page_input"):
        msgs.append({"role": "user", "content": user_prompt})
        st.session_state.pending_generation = True
        st.rerun()

    if st.session_state.pending_generation and msgs:
        q = msgs[-1]["content"]
        with st.chat_message("assistant"):
            try:
                stream = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are AskMNIT — a smart, friendly AI assistant for MNIT Jaipur students. Help with academics, fees, hostel, schedule, placements, events, library, and campus life. Be helpful, accurate, and use a warm student-friendly tone."},
                        *[{"role": m["role"], "content": m["content"]} for m in msgs[:-1]],
                        {"role": "user", "content": q}
                    ],
                    model="llama-3.3-70b-versatile",
                    stream=True
                )
                def gen():
                    for chunk in stream:
                        c = chunk.choices[0].delta.content
                        if c: yield c
                response = st.write_stream(gen())
                msgs.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error: {str(e)}")
        st.session_state.pending_generation = False
        st.rerun()
