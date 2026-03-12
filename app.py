# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                    AskMNIT — Complete Streamlit App                      ║
# ║  Authentication → Role Selection → Role-Based Dynamic Dashboard          ║
# ║                                                                          ║
# ║  PAGE ROUTING (handled entirely via st.session_state):                   ║
# ║   Step 1 │ logged_in = False          → show LOGIN screen                ║
# ║   Step 2 │ logged_in = True,          → show ROLE SELECTION screen       ║
# ║           │ user_role = None                                              ║
# ║   Step 3 │ logged_in = True,          → show MAIN DASHBOARD              ║
# ║           │ user_role = <role string>                                     ║
# ║                                                                          ║
# ║  No st.experimental_rerun hacks needed — st.rerun() handles all routing. ║
# ╚══════════════════════════════════════════════════════════════════════════╝

import streamlit as st
from groq import Groq
import datetime

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG  (must be the very first Streamlit call)
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AskMNIT",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
# GROQ CLIENT
# ══════════════════════════════════════════════════════════════════════════════
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    client = None  # Graceful fallback — chat will show a warning instead of crashing

# ══════════════════════════════════════════════════════════════════════════════
# MOCK DATABASE
# ──────────────────────────────────────────────────────────────────────────────
# In production replace this dict with actual DB calls, e.g.:
#   data = supabase.table("students").select("*").eq("phone", phone).execute()
# ══════════════════════════════════════════════════════════════════════════════
MOCK_DB = {
    # ── CURRENT STUDENT DATA (keyed by phone number) ──
    "student_data": {
        "9876543210": {
            "name": "Sumit Chaudhary",
            "roll": "2022UMT1234",
            "branch": "B.Tech Metallurgy · Sem 6",
            "cgpa": 8.4,
            "attendance": {
                # subject: (attended_classes, total_classes)  →  pct computed below
                "Economics":                            85,
                "Mineral Processing":                   78,
                "Foundry & Casting":                    92,
                "Welding":                              65,   # ⚠ below 75
                "Mobility Systems":                     88,
                "Engineering Materials & Metallurgy":   74,   # ⚠ caution
            },
            "fee_due": "₹18,500 by 17 Mar 2026",
            "next_exam": "Mineral Processing — 20 Mar 2026",
        }
    },
    # ── GUARDIAN DATA ──
    "guardian_data": {
        "9999999999": {
            "ward_name": "Sumit Chaudhary",
            "ward_roll": "2022UMT1234",
            "overall_attendance": 80,
            "fee_due": "₹18,500",
            "fee_due_date": "17 Mar 2026",
            "hostel_block": "H-7, Room 214",
            "warden_contact": "+91-141-2529087",
        }
    },
    # ── FRESHER / PROSPECTIVE STUDENT DATA ──
    "fresher_data": {
        "general": {
            "admission_deadline": "15 June 2026 (JoSAA Round 1)",
            "last_cutoff_general": "CRL Rank ≤ 14,800 (Metallurgy, 2025)",
            "last_cutoff_sc":      "SC Rank  ≤  4,200 (Metallurgy, 2025)",
            "placement_2025": {
                "avg_package":     "₹12.4 LPA",
                "highest_package": "₹48 LPA (Amazon)",
                "placement_rate":  "94%",
                "top_recruiters":  ["Amazon", "Google", "Tata Steel", "SAIL", "Infosys"],
            },
            "fee_structure": {
                "tuition_per_sem": "₹32,000",
                "hostel_per_sem":  "₹8,000",
                "mess_per_sem":    "₹4,000",
                "total_per_sem":   "₹45,000 (approx)",
            },
            "campus_highlights": [
                "350+ acre campus in Jaipur",
                "25+ state-of-the-art labs",
                "NBA & NAAC A+ accredited",
                "Active placement cell — 200+ companies",
            ],
        }
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALISATION
# ──────────────────────────────────────────────────────────────────────────────
# These keys are set ONCE on first load and never wiped by a button click.
# st.session_state persists across reruns within the same browser session.
# ══════════════════════════════════════════════════════════════════════════════
_defaults = {
    # ── AUTH / ROUTING ──────────────────────────────────────────────────────
    "logged_in":       False,   # True after successful OTP login
    "user_phone":      "",      # stores phone number after login
    "user_role":       None,    # "student" | "guardian" | "fresher" | None
    "user_name":       "",      # resolved from mock DB after login

    # ── CHAT ────────────────────────────────────────────────────────────────
    "chat_messages":   [],      # list of {"role": ..., "content": ...}
    "pending_ai":      False,   # True while waiting for Groq response

    # ── UI FLAGS ────────────────────────────────────────────────────────────
    "show_attendance": False,   # toggle attendance modal for current students
    "otp_sent":        False,   # True after "Send OTP" clicked on login screen
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS  — dark premium theme, Plus Jakarta Sans
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

*, html, body { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: #070B14 !important;
}
[data-testid="stMainBlockContainer"] {
    padding-top: 28px !important;
    padding-bottom: 48px !important;
    max-width: 100% !important;
}
header[data-testid="stHeader"],
footer, #MainMenu,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A0F1E 0%, #060912 100%) !important;
    border-right: 1px solid rgba(59,130,246,0.12) !important;
    width: 260px !important;
}
section[data-testid="stSidebar"] > div { padding: 0 !important; }
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: rgba(241,245,249,0.65) !important;
    border: none !important;
    border-radius: 9px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.83rem !important;
    padding: 9px 14px !important;
    text-align: left !important;
    width: 100% !important;
    box-shadow: none !important;
    transition: background 0.15s ease !important;
    margin: 1px 0 !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(59,130,246,0.10) !important;
    color: #F1F5F9 !important;
}

/* ── MAIN BUTTONS (gradient style) ── */
[data-testid="stMain"] .stButton > button {
    background: linear-gradient(135deg, #3B82F6 0%, #6D28D9 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    box-shadow: 0 4px 16px rgba(59,130,246,0.25) !important;
    transition: all 0.18s !important;
}
[data-testid="stMain"] .stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 22px rgba(59,130,246,0.35) !important;
}

/* ── TEXT INPUTS ── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 10px !important;
    color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.9rem !important;
}
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label {
    color: rgba(241,245,249,0.65) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
}

/* ── PROGRESS BARS ── */
[data-testid="stProgress"] > div > div {
    border-radius: 99px !important;
}

/* ── METRICS ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
    padding: 18px 16px !important;
}
[data-testid="stMetricLabel"] {
    color: rgba(241,245,249,0.45) !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stMetricValue"] {
    color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.6rem !important;
}

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* ── EXPANDERS ── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
}
summary {
    color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
}

/* ── HIDE default chat input (we add our own below it) ── */
[data-testid="stChatInput"] > div {
    background: rgba(10,14,26,0.96) !important;
    border: 1px solid rgba(80,90,160,0.32) !important;
    border-radius: 14px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.875rem !important;
}
[data-testid="stChatInput"] button[data-testid="stChatInputSubmitButton"] {
    background: linear-gradient(135deg, #3B82F6, #6D28D9) !important;
    border-radius: 9px !important;
    border: none !important;
}

/* ── PILL OVERRIDE (first horizontal block = suggestion pills) ── */
.pill-zone .stButton > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 999px !important;
    color: rgba(241,245,249,0.62) !important;
    font-size: 0.74rem !important;
    font-weight: 500 !important;
    padding: 7px 14px !important;
    box-shadow: none !important;
    transition: all 0.15s ease !important;
}
.pill-zone .stButton > button:hover {
    background: rgba(59,130,246,0.12) !important;
    border-color: rgba(59,130,246,0.32) !important;
    color: #CBD5E1 !important;
    transform: translateY(-1px) !important;
}

/* ── ALERTS ── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* ── GENERAL TEXT ── */
[data-testid="stMarkdown"] p,
[data-testid="stMarkdown"] li {
    color: rgba(241,245,249,0.75) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
h1, h2, h3 {
    color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 800 !important;
    letter-spacing: -0.5px !important;
}
hr { border-color: rgba(255,255,255,0.07) !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(59,130,246,0.18); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def logout():
    """Clear all auth-related session state and rerun → goes back to login."""
    for key in ["logged_in", "user_phone", "user_role", "user_name",
                "chat_messages", "pending_ai", "show_attendance", "otp_sent"]:
        st.session_state[key] = _defaults[key]
    st.rerun()

def get_student_data(phone: str) -> dict:
    """Fetch student data from mock DB. In production: DB query here."""
    return MOCK_DB["student_data"].get(phone, MOCK_DB["student_data"]["9876543210"])

def get_guardian_data(phone: str) -> dict:
    return MOCK_DB["guardian_data"].get(phone, MOCK_DB["guardian_data"]["9999999999"])

def get_fresher_data() -> dict:
    return MOCK_DB["fresher_data"]["general"]

def attendance_color(pct: int) -> str:
    if pct < 65:  return "#EF4444"   # red
    if pct < 75:  return "#F59E0B"   # amber
    return         "#10B981"          # green

def attendance_label(pct: int) -> str:
    if pct < 65:  return "🔴 Critical"
    if pct < 75:  return "🟡 Low"
    return         "🟢 Safe"

# ══════════════════════════════════════════════════════════════════════════════
#  ███████╗████████╗███████╗██████╗      ██╗
#  ██╔════╝╚══██╔══╝██╔════╝██╔══██╗    ███║
#  ███████╗   ██║   █████╗  ██████╔╝    ╚██║
#  ╚════██║   ██║   ██╔══╝  ██╔═══╝      ██║
#  ███████║   ██║   ███████╗██║          ██║
#  ╚══════╝   ╚═╝   ╚══════╝╚═╝          ╚═╝
#  LOGIN SCREEN
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:

    # Centre the card
    _, col_card, _ = st.columns([1, 1.6, 1])

    with col_card:
        # ── Logo / Brand ──
        st.markdown("""
        <div style="text-align:center;padding:40px 0 28px;">
            <div style="width:60px;height:60px;margin:0 auto 16px;
                        background:linear-gradient(135deg,#3B82F6,#6D28D9);
                        border-radius:16px;display:flex;align-items:center;
                        justify-content:center;font-size:1.7rem;
                        box-shadow:0 8px 28px rgba(59,130,246,0.32);">🎓</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;
                        font-size:1.6rem;font-weight:800;color:#F1F5F9;
                        letter-spacing:-0.6px;">AskMNIT</div>
            <div style="font-size:0.74rem;color:rgba(100,116,139,0.7);
                        margin-top:4px;">Your campus AI — powered by LLaMA 3.3 70B</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Card container ──
        st.markdown("""
        <div style="background:linear-gradient(160deg,#0C1120,#080D19);
                    border:1px solid rgba(100,120,220,0.18);border-radius:20px;
                    padding:32px 32px 28px;
                    box-shadow:0 24px 80px rgba(0,0,0,0.70);">
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="font-family:'Plus Jakarta Sans',sans-serif;
                    font-size:1.1rem;font-weight:800;color:#F1F5F9;
                    margin-bottom:4px;">Sign in to continue</div>
        <div style="font-size:0.74rem;color:rgba(148,163,184,0.55);
                    margin-bottom:22px;">Enter your registered mobile number.</div>
        """, unsafe_allow_html=True)

        phone_input = st.text_input(
            "📱 Mobile Number",
            placeholder="10-digit mobile number",
            max_chars=10,
            key="login_phone",
        )

        # ── Send OTP ──
        if not st.session_state.otp_sent:
            if st.button("📨  Send OTP", use_container_width=True, key="send_otp_btn"):
                if len(phone_input) == 10 and phone_input.isdigit():
                    st.session_state.otp_sent = True
                    # ──────────────────────────────────────────────────────
                    # [BACKEND] Send real OTP here, e.g. via Twilio/Firebase:
                    #   import requests
                    #   requests.post("https://api.your-auth.com/send-otp",
                    #                 json={"phone": "+91" + phone_input})
                    # ──────────────────────────────────────────────────────
                    st.rerun()
                else:
                    st.error("Please enter a valid 10-digit mobile number.")

        # ── Verify OTP ──
        if st.session_state.otp_sent:
            st.success(f"✓ OTP sent to +91 {phone_input}")
            otp_input = st.text_input(
                "🔐 Enter OTP",
                placeholder="e.g. 1234",
                max_chars=6,
                type="password",
                key="login_otp",
            )

            if st.button("✅  Verify & Login", use_container_width=True, key="verify_otp_btn"):
                # ──────────────────────────────────────────────────────────
                # [BACKEND] Verify OTP — replace dummy check with real call:
                #   response = requests.post("https://api.your-auth.com/verify-otp",
                #                            json={"phone": phone_input, "otp": otp_input})
                #   if response.status_code == 200:
                #       ... (continue flow)
                #   else:
                #       st.error("Invalid OTP")
                # For demo: any 4+ digit OTP is accepted.
                # ──────────────────────────────────────────────────────────
                if len(otp_input) >= 4:
                    st.session_state.logged_in   = True
                    st.session_state.user_phone  = phone_input
                    st.session_state.otp_sent    = False
                    # Resolve display name from mock DB (fallback = phone)
                    sdata = MOCK_DB["student_data"].get(phone_input)
                    if sdata:
                        st.session_state.user_name = sdata["name"]
                    else:
                        st.session_state.user_name = f"+91 {phone_input}"
                    # user_role is still None → next screen = role selection
                    st.rerun()
                else:
                    st.error("Enter a valid OTP (min 4 digits).")

            if st.button("← Change Number", key="change_number_btn"):
                st.session_state.otp_sent = False
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)  # close card

        st.markdown("""
        <p style="text-align:center;font-size:0.62rem;color:rgba(100,116,139,0.45);
                  margin-top:16px;line-height:1.6;">
            By continuing you agree to MNIT's Terms of Service & Privacy Policy.
        </p>
        """, unsafe_allow_html=True)

    st.stop()   # ← IMPORTANT: stops rendering anything below this point


# ══════════════════════════════════════════════════════════════════════════════
#  ███████╗████████╗███████╗██████╗     ██████╗
#  ██╔════╝╚══██╔══╝██╔════╝██╔══██╗    ╚════██╗
#  ███████╗   ██║   █████╗  ██████╔╝     █████╔╝
#  ╚════██║   ██║   ██╔══╝  ██╔═══╝     ██╔═══╝
#  ███████║   ██║   ███████╗██║         ███████╗
#  ╚══════╝   ╚═╝   ╚══════╝╚═╝         ╚══════╝
#  ROLE SELECTION SCREEN
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.logged_in and st.session_state.user_role is None:

    _, col_r, _ = st.columns([1, 2, 1])

    with col_r:
        st.markdown(f"""
        <div style="text-align:center;padding:36px 0 28px;">
            <div style="font-family:'Plus Jakarta Sans',sans-serif;
                        font-size:1.5rem;font-weight:800;color:#F1F5F9;
                        letter-spacing:-0.5px;margin-bottom:6px;">
                Tell us who you are
            </div>
            <div style="font-size:0.78rem;color:rgba(148,163,184,0.55);">
                Welcome, {st.session_state.user_name or st.session_state.user_phone} 👋 — We'll personalise AskMNIT for you.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Role cards ──
        role_options = [
            {
                "id":    "fresher",
                "icon":  "🎓",
                "title": "Prospective Student (Fresher)",
                "desc":  "Looking to apply for admission.",
                "grad":  "linear-gradient(135deg,#1D4ED8,#3B82F6)",
                "glow":  "rgba(59,130,246,0.28)",
            },
            {
                "id":    "guardian",
                "icon":  "👨‍👧",
                "title": "Guardian / Parent",
                "desc":  "Here for my ward or child.",
                "grad":  "linear-gradient(135deg,#7C3AED,#A78BFA)",
                "glow":  "rgba(139,92,246,0.28)",
            },
            {
                "id":    "student",
                "icon":  "🏫",
                "title": "Current Student",
                "desc":  "Already enrolled in the college.",
                "grad":  "linear-gradient(135deg,#065F46,#10B981)",
                "glow":  "rgba(16,185,129,0.28)",
            },
        ]

        for role in role_options:
            # HTML card wrapper for aesthetics; real click via Streamlit button below
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.025);
                        border:1px solid rgba(255,255,255,0.08);
                        border-radius:14px;padding:16px 18px 10px;
                        margin-bottom:4px;">
                <div style="display:flex;align-items:center;gap:14px;margin-bottom:6px;">
                    <div style="width:46px;height:46px;border-radius:12px;
                                background:{role['grad']};
                                display:flex;align-items:center;justify-content:center;
                                font-size:1.3rem;flex-shrink:0;
                                box-shadow:0 4px 14px {role['glow']};">
                        {role['icon']}
                    </div>
                    <div>
                        <div style="font-family:'Plus Jakarta Sans',sans-serif;
                                    font-weight:700;font-size:0.92rem;color:#F1F5F9;">
                            {role['title']}
                        </div>
                        <div style="font-size:0.73rem;color:rgba(148,163,184,0.55);margin-top:1px;">
                            {role['desc']}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # The actual clickable Streamlit button
            if st.button(f"Select — {role['title']}", key=f"role_{role['id']}", use_container_width=True):
                # ────────────────────────────────────────────────────────
                # [BACKEND] Persist role to your database:
                #   requests.patch("/api/user/role",
                #       json={"phone": st.session_state.user_phone, "role": role["id"]})
                # ────────────────────────────────────────────────────────
                st.session_state.user_role = role["id"]
                st.rerun()   # ← triggers re-render → lands on dashboard (Step 3)

            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    st.stop()   # ← stop; nothing below should render until role is chosen


# ══════════════════════════════════════════════════════════════════════════════
#  ███████╗████████╗███████╗██████╗     ██████╗
#  ██╔════╝╚══██╔══╝██╔════╝██╔══██╗    ╚════██╗
#  ███████╗   ██║   █████╗  ██████╔╝        ██╔╝
#  ╚════██║   ██║   ██╔══╝  ██╔═══╝        ██╔╝
#  ███████║   ██║   ███████╗██║            ██║
#  ╚══════╝   ╚═╝   ╚══════╝╚═╝            ╚═╝
#  MAIN DASHBOARD  (only reached when logged_in=True AND user_role is set)
# ══════════════════════════════════════════════════════════════════════════════

role  = st.session_state.user_role   # "student" | "guardian" | "fresher"
phone = st.session_state.user_phone

# Resolve current hour for greeting
_hour    = datetime.datetime.now().hour
_greeting = "Good Morning ☀️" if _hour < 12 else ("Good Afternoon 🌤️" if _hour < 17 else "Good Evening 🌙")

# ── Role display config ──
ROLE_META = {
    "student":  {"icon": "🏫", "label": "Current Student",  "color": "#10B981", "border": "rgba(16,185,129,0.25)"},
    "guardian": {"icon": "👨‍👧", "label": "Guardian / Parent", "color": "#A78BFA", "border": "rgba(139,92,246,0.25)"},
    "fresher":  {"icon": "🎓", "label": "Prospective Student","color": "#60A5FA", "border": "rgba(59,130,246,0.25)"},
}
rmeta = ROLE_META[role]

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:20px 16px 16px;border-bottom:1px solid rgba(255,255,255,0.07);">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:38px;height:38px;
                        background:linear-gradient(135deg,#3B82F6,#6D28D9);
                        border-radius:10px;display:flex;align-items:center;
                        justify-content:center;font-size:1.1rem;">🎓</div>
            <div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif;
                            font-weight:800;font-size:1rem;color:#F1F5F9;">AskMNIT</div>
                <div style="font-size:0.58rem;color:rgba(241,245,249,0.35);
                            letter-spacing:1.2px;text-transform:uppercase;">Campus Intelligence</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # User card
    display_name = st.session_state.user_name or f"+91 {phone}"
    st.markdown(f"""
    <div style="margin:6px 12px 12px;background:rgba(59,130,246,0.07);
                border:1px solid {rmeta['border']};border-radius:12px;padding:12px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:34px;height:34px;background:linear-gradient(135deg,#3B82F6,#6D28D9);
                        border-radius:50%;display:flex;align-items:center;justify-content:center;
                        font-size:0.75rem;font-weight:800;color:white;flex-shrink:0;">
                {display_name[:2].upper()}
            </div>
            <div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;
                            font-size:0.82rem;color:#F1F5F9;">{display_name}</div>
                <div style="font-size:0.62rem;color:{rmeta['color']};margin-top:1px;">
                    {rmeta['icon']} {rmeta['label']}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Switch Role ──
    if st.button("🔄  Switch Role", use_container_width=True, key="switch_role"):
        st.session_state.user_role   = None
        st.session_state.chat_messages = []
        st.session_state.show_attendance = False
        st.rerun()

    # ── Logout ──
    if st.button("🚪  Logout", use_container_width=True, key="logout_btn"):
        logout()

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Role info panel in sidebar ──
    st.markdown(f"""
    <div style="margin:0 12px;padding:12px;background:rgba(255,255,255,0.02);
                border:1px solid rgba(255,255,255,0.07);border-radius:10px;">
        <div style="font-size:0.58rem;color:rgba(255,255,255,0.25);
                    letter-spacing:2px;text-transform:uppercase;
                    font-family:'Plus Jakarta Sans',sans-serif;margin-bottom:8px;">
            Session
        </div>
        <div style="font-size:0.72rem;color:rgba(241,245,249,0.55);line-height:1.8;
                    font-family:'Plus Jakarta Sans',sans-serif;">
            📱 {phone}<br>
            🎭 {rmeta['label']}<br>
            🕐 {_greeting.split()[0]}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT AREA
# ══════════════════════════════════════════════════════════════════════════════

# ── Top bar (minimal — no big header text per spec) ──
top_l, top_r = st.columns([5, 1])
with top_l:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;padding-bottom:4px;">
        <div style="width:38px;height:38px;background:linear-gradient(135deg,#3B82F6,#6D28D9);
                    border-radius:10px;display:flex;align-items:center;justify-content:center;
                    font-size:1rem;">🤖</div>
        <div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:800;
                        font-size:1.1rem;color:#F1F5F9;">AskMNIT AI</div>
            <div style="font-size:0.65rem;color:#10B981;font-weight:600;">
                ● Online · LLaMA 3.3 70B
            </div>
        </div>
        <div style="margin-left:12px;padding:4px 12px;
                    background:{rmeta['border'].replace('0.25','0.10')};
                    border:1px solid {rmeta['border']};
                    border-radius:99px;font-size:0.67rem;font-weight:700;
                    color:{rmeta['color']};font-family:'Plus Jakarta Sans',sans-serif;">
            {rmeta['icon']} {rmeta['label']}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# DYNAMIC "TRY ASKING" PILLS — changes completely based on user_role
# ══════════════════════════════════════════════════════════════════════════════

# Each role has its own pill set — this is the core conditional rendering logic.
PILLS = {
    "fresher": [
        ("🎓", "Admission Process 2026"),
        ("📊", "Last Year Cut-offs"),
        ("💼", "Placement Stats"),
        ("🏛️", "Campus Tour & Facilities"),
        ("💰", "Fee Structure"),
    ],
    "guardian": [
        ("📋", "Check Ward's Attendance"),
        ("💳", "Fee Payment & Dues"),
        ("🏢", "Hostel Rules & Security"),
        ("📅", "Academic Calendar"),
        ("📞", "Contact HOD / Admin"),
    ],
    "student": [
        ("🕐", "Today's Timetable"),
        ("📊", "View Detailed Attendance"),   # triggers modal below
        ("📝", "Download PYQs"),
        ("🏆", "Result Dashboard"),
        ("🔗", "ERP Login"),
    ],
}

current_pills = PILLS[role]

st.markdown("""
<p style='color:rgba(241,245,249,0.28);font-size:0.63rem;letter-spacing:1.2px;
text-transform:uppercase;margin-bottom:8px;font-family:Plus Jakarta Sans,sans-serif;
font-weight:700;'>💡 Try asking</p>
""", unsafe_allow_html=True)

st.markdown('<div class="pill-zone">', unsafe_allow_html=True)
pill_cols = st.columns(len(current_pills))
for i, (icon, label) in enumerate(current_pills):
    with pill_cols[i]:
        if st.button(f"{icon} {label}", key=f"pill_{i}", use_container_width=True):
            # ── Special action: "View Detailed Attendance" ──
            if label == "View Detailed Attendance":
                st.session_state.show_attendance = not st.session_state.show_attendance
                st.rerun()
            else:
                # Inject the pill text as a user chat message
                st.session_state.chat_messages.append({"role": "user", "content": label})
                st.session_state.pending_ai = True
                st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ATTENDANCE DETAIL PANEL  (current student only)
# Shows when show_attendance = True
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.show_attendance and role == "student":

    sdata = get_student_data(phone)
    attendance = sdata["attendance"]   # dict: subject → pct

    st.markdown("""
    <div style="background:linear-gradient(160deg,#0D1221,#080C18);
                border:1px solid rgba(100,120,200,0.20);border-radius:16px;
                padding:20px 24px 14px;margin-bottom:16px;
                box-shadow:0 8px 32px rgba(0,0,0,0.40);">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
            <div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:800;
                            font-size:1rem;color:#F1F5F9;">📊 Subject-wise Attendance</div>
                <div style="font-size:0.68rem;color:rgba(148,163,184,0.55);margin-top:2px;">
                    Semester 6 · B.Tech Metallurgical Engineering
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Legend
    leg1, leg2, leg3 = st.columns(3)
    leg1.markdown("<span style='color:#10B981;font-size:0.7rem;font-weight:700;'>🟢 ≥75% Safe</span>", unsafe_allow_html=True)
    leg2.markdown("<span style='color:#F59E0B;font-size:0.7rem;font-weight:700;'>🟡 74–75% Caution</span>", unsafe_allow_html=True)
    leg3.markdown("<span style='color:#EF4444;font-size:0.7rem;font-weight:700;'>🔴 &lt;65% Critical</span>", unsafe_allow_html=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    overall_avg = round(sum(attendance.values()) / len(attendance))

    for subject, pct in attendance.items():
        color = attendance_color(pct)
        badge = attendance_label(pct)

        col_subj, col_pct = st.columns([4, 1])
        with col_subj:
            st.markdown(f"""
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:600;
                        font-size:0.82rem;color:{'#FCA5A5' if pct < 65 else '#FCD34D' if pct < 75 else '#E2E8F0'};
                        margin-bottom:4px;">
                {subject}
                <span style="margin-left:6px;font-size:0.6rem;
                             background:{'rgba(239,68,68,0.15)' if pct < 65 else 'rgba(245,158,11,0.12)' if pct < 75 else 'rgba(16,185,129,0.10)'};
                             color:{color};padding:1px 7px;border-radius:4px;">{badge}</span>
            </div>
            """, unsafe_allow_html=True)
            st.progress(pct / 100)   # ← st.progress (0.0 – 1.0)
        with col_pct:
            st.markdown(f"""
            <div style="text-align:right;font-family:'Plus Jakarta Sans',sans-serif;
                        font-weight:800;font-size:1.1rem;color:{color};
                        padding-top:2px;">{pct}%</div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)   # close card

    # Overall metric
    oc1, oc2, oc3 = st.columns([1, 1, 1])
    with oc1:
        st.metric("Overall Attendance", f"{overall_avg}%",
                  "+2% from last month" if overall_avg >= 75 else "Below 75% threshold ⚠️")
    with oc2:
        low_count = sum(1 for p in attendance.values() if p < 75)
        st.metric("Subjects Below 75%", str(low_count), "Need attention" if low_count else "All clear ✓")
    with oc3:
        st.metric("Next Exam", sdata["next_exam"].split("—")[0].strip(), sdata["next_exam"].split("—")[-1].strip())

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if st.button("✖ Close Attendance Panel", key="close_attend"):
        st.session_state.show_attendance = False
        st.rerun()

    st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# QUICK INFO CARDS  — pulled from mock DB, differ per role
# ══════════════════════════════════════════════════════════════════════════════
if role == "student":
    sdata = get_student_data(phone)
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("CGPA",          f"{sdata['cgpa']} / 10",  "+0.2 this sem")
    with m2: st.metric("Fee Due",        sdata["fee_due"],          "5 days left")
    with m3: st.metric("Next Exam",      sdata["next_exam"].split("—")[0], sdata["next_exam"].split("—")[-1].strip() if "—" in sdata["next_exam"] else "")

elif role == "guardian":
    gdata = get_guardian_data(phone)
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("Ward",           gdata["ward_name"],          gdata["ward_roll"])
    with m2: st.metric("Fee Due",        gdata["fee_due"],            f"By {gdata['fee_due_date']}")
    with m3: st.metric("Overall Attend.", f"{gdata['overall_attendance']}%", "Above 75% ✓" if gdata["overall_attendance"] >= 75 else "Below 75% ⚠️")

elif role == "fresher":
    fdata = get_fresher_data()
    pstats = fdata["placement_2025"]
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("Avg Package 2025",  pstats["avg_package"],  "+8% YoY")
    with m2: st.metric("Highest Package",   pstats["highest_package"], "Amazon")
    with m3: st.metric("Placement Rate",    pstats["placement_rate"], "Batch 2025")

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHAT HISTORY
# ══════════════════════════════════════════════════════════════════════════════

# Empty state
if not st.session_state.chat_messages:
    st.markdown(f"""
    <div style="text-align:center;padding:40px 20px;opacity:0.55;">
        <div style="font-size:2.4rem;margin-bottom:12px;">{rmeta['icon']}</div>
        <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;
                    font-size:0.95rem;color:#F1F5F9;margin-bottom:6px;">
            {"Hey " + display_name.split()[0] + "!" if display_name else "Hey!"} I'm AskMNIT
        </div>
        <div style="font-size:0.8rem;color:rgba(241,245,249,0.55);max-width:360px;margin:0 auto;">
            {
                "Ask me about PYQs, timetable, results, ERP & more." if role == "student"
                else "Ask me about your ward's attendance, fees, hostel & academic updates." if role == "guardian"
                else "Ask me about MNIT admissions, cut-offs, placements, fees & campus life."
            }
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ── Pending AI response ──
if st.session_state.pending_ai and st.session_state.chat_messages:
    last_user_msg = st.session_state.chat_messages[-1]["content"]

    with st.chat_message("assistant"):
        if client is None:
            # No API key → informative fallback
            response_text = (
                f"I'm AskMNIT. You asked: **{last_user_msg}**. "
                "Please add your GROQ_API_KEY to `.streamlit/secrets.toml` for live AI responses."
            )
            st.markdown(response_text)
        else:
            try:
                # ────────────────────────────────────────────────────────────
                # [BACKEND] Real Groq streaming call — role-aware system prompt
                # ────────────────────────────────────────────────────────────
                role_context = {
                    "student":  "The user is a current MNIT Jaipur student (B.Tech). Help with academics, PYQs, timetable, attendance, results, ERP, placements.",
                    "guardian": "The user is a guardian/parent of an MNIT Jaipur student. Help with attendance queries, fee dues, hostel info, academic calendar, contacting admin.",
                    "fresher":  "The user is a prospective student planning to join MNIT Jaipur. Help with admission process, JoSAA, cut-offs, fee structure, placement statistics, campus life.",
                }
                system_prompt = (
                    f"You are AskMNIT — a helpful, friendly AI assistant for MNIT Jaipur. "
                    f"{role_context[role]} Be concise, warm and accurate."
                )

                stream = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *[{"role": m["role"], "content": m["content"]}
                          for m in st.session_state.chat_messages],
                    ],
                    model="llama-3.3-70b-versatile",
                    stream=True,
                )

                def _stream_gen():
                    for chunk in stream:
                        delta = chunk.choices[0].delta.content
                        if delta:
                            yield delta

                response_text = st.write_stream(_stream_gen())

            except Exception as e:
                response_text = f"⚠️ Error calling AI: {e}"
                st.error(response_text)

        st.session_state.chat_messages.append(
            {"role": "assistant", "content": response_text}
        )

    st.session_state.pending_ai = False
    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# CHAT INPUT BOX
# ══════════════════════════════════════════════════════════════════════════════

_placeholder_map = {
    "student":  "Ask about PYQs, timetable, attendance, ERP…",
    "guardian": "Ask about your ward's attendance, fees, hostel…",
    "fresher":  "Ask about admissions, cut-offs, placements, fees…",
}

if prompt := st.chat_input(_placeholder_map[role], key="main_chat_input"):
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    st.session_state.pending_ai = True
    st.rerun()

# ── Disclaimer ──
st.markdown("""
<p style="text-align:center;font-size:0.63rem;color:rgba(100,116,139,0.45);
          margin-top:8px;letter-spacing:0.01em;line-height:1.5;
          font-family:'Plus Jakarta Sans',sans-serif;">
    AskMNIT can make mistakes. Please verify important information with the official admin.
</p>
""", unsafe_allow_html=True)
