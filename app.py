# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║              AskMNIT — Streamlit App  (Final · Copy-Paste Ready)             ║
# ║                                                                              ║
# ║  ROOT CAUSE FIX: Never put Python function calls or .join() inside an        ║
# ║  f-string that is passed to st.markdown(). Streamlit renders the raw         ║
# ║  string before Python evaluates it — nested logic in f-strings breaks HTML.  ║
# ║  All dynamic HTML is built with plain string concatenation BEFORE the        ║
# ║  st.markdown() call.                                                         ║
# ║                                                                              ║
# ║  ROUTING (via st.session_state):                                             ║
# ║   logged_in=False                        → Screen 1: LOGIN                   ║
# ║   logged_in=True, user_role=None         → Screen 2: ROLE SELECTION          ║
# ║   role="guardian", ward_data=None        → Screen 3: WARD ID ENTRY           ║
# ║   role="guardian", ward_data set         → Screen 4: GUARDIAN DASHBOARD      ║
# ║   role="student"/"fresher"               → Screen 5: GENERIC DASHBOARD       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import streamlit as st
from groq import Groq
import datetime

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be the very first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AskMNIT",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# GROQ CLIENT
# Add  GROQ_API_KEY = "gsk_..."  to  .streamlit/secrets.toml
# ─────────────────────────────────────────────────────────────────────────────
client = Groq(api_key=st.secrets["GROQ_API_KEY"]) if "GROQ_API_KEY" in st.secrets else None

# ═════════════════════════════════════════════════════════════════════════════
# MOCK DATABASE
# ─────────────────────────────────────────────────────────────────────────────
# [BACKEND] Replace WARD_DB lookups with a real API/DB call, e.g.:
#   def fetch_ward_data(ward_id):
#       r = requests.get(f"https://erp.mnit.ac.in/api/student/{ward_id}",
#                        headers={"Authorization": f"Bearer {st.secrets['ERP_TOKEN']}"})
#       return r.json() if r.ok else None
# ═════════════════════════════════════════════════════════════════════════════

WARD_DB = {
    "2022UMT1234": {
        "name":          "Sumit Chaudhary",
        "initials":      "SC",
        "course":        "B.Tech Metallurgical Engineering",
        "semester":      "Semester 6",
        "roll":          "2022UMT1234",
        "campus_status": "On Campus",
        "hostel_block":  "H-7, Room 214",
        "warden":        "Dr. Pradeep Mehta",
        "warden_phone":  "+91-141-2529041",
        "cgpa":          8.4,
        "overall_att":   80,
        "att_7d":        "Regular",
        "att_subjects": {
            "Economics":                        85,
            "Mineral Processing":               78,
            "Foundry and Casting":              92,
            "Welding":                          65,
            "Mobility Systems":                 88,
            "Engg. Materials & Metallurgy":     74,
        },
        "fee_pending":   "18,500",
        "fee_symbol":    "₹18,500",
        "fee_due_date":  "17 Mar 2026",
        "fee_semester":  "Semester 6",
        "fee_breakdown": [
            ("Tuition Fee",  "₹10,000"),
            ("Hostel Fee",   "₹5,500"),
            ("Library Fee",  "₹500"),
            ("Sports Fee",   "₹1,000"),
            ("Exam Fee",     "₹1,500"),
        ],
        "next_exam":     "Mineral Processing — 20 Mar 2026",
        "notices": [
            "Mid-Semester exams: Mar 20–27",
            "Parent-Teacher Meet: Mar 15 (10 AM – 1 PM)",
            "Hostel gate extended to 11 PM till exams",
        ],
    },
    "2026CS101": {
        "name":          "Rajesh Sharma",
        "initials":      "RS",
        "course":        "B.Tech Computer Science & Engineering",
        "semester":      "Semester 4",
        "roll":          "2026CS101",
        "campus_status": "On Campus",
        "hostel_block":  "H-3, Room 112",
        "warden":        "Dr. Sunita Agarwal",
        "warden_phone":  "+91-141-2529055",
        "cgpa":          9.1,
        "overall_att":   85,
        "att_7d":        "Regular",
        "att_subjects": {
            "Data Structures":      88,
            "Operating Systems":    82,
            "Computer Networks":    90,
            "DBMS":                 79,
            "Software Engineering": 72,
        },
        "fee_pending":   "15,000",
        "fee_symbol":    "₹15,000",
        "fee_due_date":  "Oct 15, 2026",
        "fee_semester":  "Semester 4",
        "fee_breakdown": [
            ("Tuition Fee",  "₹10,000"),
            ("Hostel Fee",   "₹3,500"),
            ("Library Fee",  "₹500"),
            ("Sports Fee",   "₹1,000"),
        ],
        "next_exam":     "Data Structures — Apr 5, 2026",
        "notices": [
            "Sem 4 results expected May 10",
            "Lab submissions: Mar 25 (hard deadline)",
            "Alumni Mentorship: Register by Mar 20",
        ],
    },
    "2025MT089": {
        "name":          "Priya Verma",
        "initials":      "PV",
        "course":        "B.Tech Metallurgical Engineering",
        "semester":      "Semester 6",
        "roll":          "2025MT089",
        "campus_status": "On Campus",
        "hostel_block":  "Girls Hostel G-1, Room 204",
        "warden":        "Dr. Meera Joshi",
        "warden_phone":  "+91-141-2529062",
        "cgpa":          7.9,
        "overall_att":   78,
        "att_7d":        "1 absence",
        "att_subjects": {
            "Mineral Processing":    80,
            "Phase Transformations": 75,
            "Thermodynamics II":     82,
            "Fluid Mechanics":       74,
            "Engineering Economics": 79,
        },
        "fee_pending":   "8,500",
        "fee_symbol":    "₹8,500",
        "fee_due_date":  "Apr 20, 2026",
        "fee_semester":  "Semester 6",
        "fee_breakdown": [
            ("Mess Fee",     "₹4,000"),
            ("Library Fee",  "₹500"),
            ("Tuition Fee",  "₹4,000"),
        ],
        "next_exam":     "Mineral Processing — Mar 28, 2026",
        "notices": [
            "Sem 6 results expected May 5",
            "Lab submissions: Apr 18 (hard deadline)",
        ],
    },
}

STUDENT_DB = {
    "9876543210": {
        "name":    "Sumit Chaudhary",
        "roll":    "2022UMT1234",
        "branch":  "B.Tech Metallurgy · Sem 6",
        "cgpa":    8.4,
        "attendance": {
            "Economics":                        85,
            "Mineral Processing":               78,
            "Foundry and Casting":              92,
            "Welding":                          65,
            "Mobility Systems":                 88,
            "Engg. Materials & Metallurgy":     74,
        },
        "fee_due":   "₹18,500 by 17 Mar 2026",
        "next_exam": "Mineral Processing — 20 Mar 2026",
    },
}

FRESHER_DATA = {
    "placement_avg":      "₹12.4 LPA",
    "placement_highest":  "₹48 LPA (Amazon)",
    "placement_rate":     "94%",
    "fee_per_sem":        "₹45,000 (approx)",
    "admission_deadline": "15 June 2026 (JoSAA Round 1)",
    "cutoff_general":     "CRL Rank ≤ 14,800 (Metallurgy, 2025)",
}


def fetch_ward_data(ward_id: str):
    """Lookup by ward college ID. Returns dict or None."""
    return WARD_DB.get(ward_id.strip().upper())


def fetch_student_data(phone: str):
    return STUDENT_DB.get(phone, list(STUDENT_DB.values())[0])


# ═════════════════════════════════════════════════════════════════════════════
# SESSION STATE  — initialise all keys exactly once
# ═════════════════════════════════════════════════════════════════════════════
_DEFAULTS = {
    "logged_in":       False,
    "user_phone":      "",
    "user_role":       None,
    "user_name":       "",
    "otp_sent":        False,
    # Guardian-specific
    "ward_id":         "",
    "ward_data":       None,
    "ward_id_error":   "",
    "show_att_detail": False,
    # Chat
    "chat_messages":   [],
    "pending_ai":      False,
    # Student
    "show_attendance": False,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


def logout():
    for k, v in _DEFAULTS.items():
        st.session_state[k] = v
    st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

*, html, body { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: #070B14 !important;
}
[data-testid="stMainBlockContainer"] {
    padding-top: 20px !important;
    padding-bottom: 48px !important;
    max-width: 100% !important;
}
header[data-testid="stHeader"], footer, #MainMenu,
[data-testid="stToolbar"], [data-testid="stDecoration"],
section[data-testid="stSidebar"] { display: none !important; }

/* Inputs */
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 10px !important;
    color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stTextInput"] label {
    color: rgba(241,245,249,0.60) !important;
    font-size: 0.76rem !important; font-weight: 700 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* All buttons — gradient default */
.stButton > button {
    background: linear-gradient(135deg,#3B82F6,#6D28D9) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important; font-size: 0.85rem !important;
    box-shadow: 0 4px 16px rgba(59,130,246,0.22) !important;
    transition: all 0.18s !important;
}
.stButton > button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }

/* Ghost button override */
.ghost-btn .stButton > button {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    color: rgba(241,245,249,0.60) !important;
    box-shadow: none !important;
}
.ghost-btn .stButton > button:hover {
    background: rgba(59,130,246,0.10) !important; color: #F1F5F9 !important;
}

/* Amber "Pay Now" button */
.pay-btn .stButton > button {
    background: linear-gradient(135deg,#D97706,#F59E0B) !important;
    box-shadow: 0 4px 18px rgba(245,158,11,0.28) !important;
}

/* Pill buttons */
.pill-zone .stButton > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 999px !important;
    color: rgba(241,245,249,0.60) !important;
    font-size: 0.74rem !important; font-weight: 500 !important;
    box-shadow: none !important;
}
.pill-zone .stButton > button:hover {
    background: rgba(139,92,246,0.14) !important;
    border-color: rgba(139,92,246,0.32) !important;
    color: #CBD5E1 !important; transform: translateY(-1px) !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important; padding: 16px !important;
}
[data-testid="stMetricLabel"] {
    color: rgba(241,245,249,0.40) !important;
    font-size: 0.68rem !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: 0.8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stMetricValue"] {
    color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 800 !important;
}

/* Progress bars */
[data-testid="stProgress"] > div > div { border-radius: 99px !important; }

/* Chat */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stChatInput"] > div {
    background: rgba(10,14,26,0.96) !important;
    border: 1px solid rgba(80,90,160,0.32) !important;
    border-radius: 14px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important; color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stChatInput"] button[data-testid="stChatInputSubmitButton"] {
    background: linear-gradient(135deg,#3B82F6,#6D28D9) !important;
    border-radius: 9px !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
}
summary {
    color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
}

/* Text */
[data-testid="stMarkdown"] p, [data-testid="stMarkdown"] li {
    color: rgba(241,245,249,0.70) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
h1,h2,h3 {
    color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 800 !important;
}
hr { border-color: rgba(255,255,255,0.07) !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(59,130,246,0.18); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# COLOUR HELPERS  (used in guardian dashboard — computed before st.markdown)
# ─────────────────────────────────────────────────────────────────────────────
def att_color(pct):
    if pct < 65: return "#EF4444"
    if pct < 75: return "#F59E0B"
    return "#10B981"

def att_text_color(pct):
    if pct < 65: return "#FCA5A5"
    if pct < 75: return "#FCD34D"
    return "#E2E8F0"

def att_badge_bg(pct):
    if pct < 65: return "rgba(239,68,68,0.14)"
    if pct < 75: return "rgba(245,158,11,0.12)"
    return "rgba(16,185,129,0.10)"

def att_badge_label(pct):
    if pct < 65: return "Critical"
    if pct < 75: return "Low"
    return "Safe"


# ═════════════════════════════════════════════════════════════════════════════
# ████  SCREEN 1 — LOGIN  ████
# ═════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:

    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("""
        <div style="text-align:center;padding:44px 0 28px;">
            <div style="width:58px;height:58px;margin:0 auto 14px;
                        background:linear-gradient(135deg,#3B82F6,#6D28D9);
                        border-radius:15px;display:flex;align-items:center;
                        justify-content:center;font-size:1.7rem;
                        box-shadow:0 8px 28px rgba(59,130,246,0.30);">🎓</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.5rem;
                        font-weight:800;color:#F1F5F9;letter-spacing:-0.6px;">AskMNIT</div>
            <div style="font-size:0.72rem;color:rgba(100,116,139,0.65);margin-top:4px;">
                Your campus AI — powered by LLaMA 3.3 70B
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:linear-gradient(160deg,#0C1120,#080D19);
                    border:1px solid rgba(100,120,220,0.16);border-radius:20px;
                    padding:22px 24px 8px;box-shadow:0 24px 80px rgba(0,0,0,0.68);">
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.05rem;
                        font-weight:800;color:#F1F5F9;margin-bottom:4px;">
                Sign in to continue
            </div>
            <div style="font-size:0.72rem;color:rgba(148,163,184,0.50);margin-bottom:4px;">
                Enter your registered mobile number.
            </div>
        </div>
        """, unsafe_allow_html=True)

        phone_val = st.text_input(
            "📱 Mobile Number", placeholder="10-digit number",
            max_chars=10, key="login_phone"
        )

        if not st.session_state.otp_sent:
            if st.button("📨  Send OTP", use_container_width=True, key="btn_send_otp"):
                if len(phone_val) == 10 and phone_val.isdigit():
                    # [BACKEND] Send real OTP here
                    st.session_state.otp_sent = True
                    st.rerun()
                else:
                    st.error("Please enter a valid 10-digit mobile number.")

        if st.session_state.otp_sent:
            st.success(f"✅ OTP sent to +91 {phone_val}")
            otp_val = st.text_input(
                "🔐 Enter OTP", placeholder="4–6 digit OTP",
                max_chars=6, type="password", key="login_otp"
            )
            c1, c2 = st.columns([2, 1])
            with c1:
                if st.button("✅  Verify & Continue", use_container_width=True, key="btn_verify"):
                    if len(otp_val) >= 4:
                        # [BACKEND] Verify OTP here
                        st.session_state.logged_in  = True
                        st.session_state.user_phone = phone_val
                        st.session_state.otp_sent   = False
                        if phone_val in STUDENT_DB:
                            st.session_state.user_name = STUDENT_DB[phone_val]["name"]
                        st.rerun()
                    else:
                        st.error("Enter a valid OTP (min 4 digits).")
            with c2:
                st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
                if st.button("← Change", use_container_width=True, key="btn_change"):
                    st.session_state.otp_sent = False
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <p style="text-align:center;font-size:0.60rem;color:rgba(100,116,139,0.40);
                  margin-top:12px;line-height:1.6;">
            By continuing you agree to MNIT's Terms of Service & Privacy Policy.
        </p>
        """, unsafe_allow_html=True)

    st.stop()


# ═════════════════════════════════════════════════════════════════════════════
# ████  SCREEN 2 — ROLE SELECTION  ████
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.user_role is None:

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("""
        <div style="text-align:center;padding:40px 0 28px;">
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.45rem;
                        font-weight:800;color:#F1F5F9;letter-spacing:-0.5px;margin-bottom:6px;">
                Tell us who you are
            </div>
            <div style="font-size:0.77rem;color:rgba(148,163,184,0.50);">
                We'll personalise AskMNIT based on your role.
            </div>
        </div>
        """, unsafe_allow_html=True)

        ROLE_LIST = [
            ("fresher",  "🎓", "Prospective Student", "FRESHER",
             "Looking to apply for admission.",
             "linear-gradient(135deg,#1D4ED8,#3B82F6)", "rgba(59,130,246,0.28)"),
            ("guardian", "👨‍👧", "Guardian / Parent", "",
             "Here for my ward or child.",
             "linear-gradient(135deg,#7C3AED,#A78BFA)", "rgba(139,92,246,0.28)"),
            ("student",  "🏫", "Current Student", "",
             "Already enrolled in the college.",
             "linear-gradient(135deg,#065F46,#10B981)", "rgba(16,185,129,0.28)"),
        ]

        for rid, icon, title, badge, desc, grad, glow in ROLE_LIST:
            # Build badge span string BEFORE the f-string
            if badge:
                badge_html = (
                    '<span style="font-size:0.58rem;padding:2px 7px;'
                    'background:rgba(255,255,255,0.14);border-radius:4px;'
                    'font-weight:700;letter-spacing:0.5px;text-transform:uppercase;'
                    'margin-left:8px;">' + badge + '</span>'
                )
            else:
                badge_html = ""

            st.markdown(
                '<div style="background:rgba(255,255,255,0.025);'
                'border:1px solid rgba(255,255,255,0.08);'
                'border-radius:14px;padding:16px 18px 10px;margin-bottom:4px;">'
                '<div style="display:flex;align-items:center;gap:14px;margin-bottom:4px;">'
                '<div style="width:46px;height:46px;border-radius:12px;'
                'background:' + grad + ';display:flex;align-items:center;'
                'justify-content:center;font-size:1.3rem;flex-shrink:0;'
                'box-shadow:0 4px 14px ' + glow + ';">' + icon + '</div>'
                '<div>'
                '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;'
                'font-weight:700;font-size:0.92rem;color:#F1F5F9;">'
                + title + badge_html +
                '</div>'
                '<div style="font-size:0.73rem;color:rgba(148,163,184,0.55);margin-top:2px;">'
                + desc +
                '</div>'
                '</div></div></div>',
                unsafe_allow_html=True
            )

            if st.button(f"Select — {title}", key=f"role_{rid}", use_container_width=True):
                # [BACKEND] Save role to your DB here
                st.session_state.user_role     = rid
                st.session_state.chat_messages = []
                st.session_state.ward_data     = None
                st.session_state.ward_id_error = ""
                st.rerun()

            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    st.stop()


# ═════════════════════════════════════════════════════════════════════════════
# ████  SCREEN 3 — GUARDIAN WARD ID ENTRY  ████
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.user_role == "guardian" and st.session_state.ward_data is None:

    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("""
        <div style="text-align:center;padding:40px 0 24px;">
            <div style="width:58px;height:58px;margin:0 auto 16px;
                        background:linear-gradient(135deg,#7C3AED,#A78BFA);
                        border-radius:15px;display:flex;align-items:center;
                        justify-content:center;font-size:1.7rem;
                        box-shadow:0 8px 28px rgba(139,92,246,0.30);">👨‍👧</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;
                        font-size:1.2rem;font-weight:800;color:#F1F5F9;
                        letter-spacing:-0.4px;margin-bottom:6px;">
                Enter Ward's College ID
            </div>
            <div style="font-size:0.75rem;color:rgba(148,163,184,0.52);
                        line-height:1.6;max-width:320px;margin:0 auto;">
                Enter your child's enrollment or roll number to link
                their academic data to your account.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:linear-gradient(160deg,#0C1120,#080D19);
                    border:1px solid rgba(139,92,246,0.20);border-radius:20px;
                    padding:24px 24px 8px;box-shadow:0 24px 80px rgba(0,0,0,0.68);">
        </div>
        """, unsafe_allow_html=True)

        ward_input = st.text_input(
            "🎓 Ward's College ID / Enrollment Number *",
            placeholder="e.g. 2022UMT1234  or  2026CS101",
            key="ward_id_input",
            help="Roll No. or Enrollment No. from your ward's identity card.",
        )

        if st.session_state.ward_id_error:
            st.markdown(
                '<div style="background:rgba(239,68,68,0.08);'
                'border:1px solid rgba(239,68,68,0.22);border-radius:8px;'
                'padding:10px 14px;margin:4px 0 8px;'
                'font-size:0.74rem;color:#FCA5A5;">⚠ '
                + st.session_state.ward_id_error +
                '</div>',
                unsafe_allow_html=True
            )

        if st.button("🔍  Link Ward's Account", use_container_width=True, key="btn_link_ward"):
            raw = ward_input.strip()
            if not raw:
                st.session_state.ward_id_error = (
                    "This field is required. Please enter your ward's College ID."
                )
                st.rerun()
            else:
                # ── Core data-fetch using wardCollegeId as key ──────────────
                # [BACKEND] Replace with real API call:
                #   fetched = requests.get(f"{ERP_URL}/student/{raw}").json()
                fetched = fetch_ward_data(raw)
                # ────────────────────────────────────────────────────────────
                if fetched is None:
                    st.session_state.ward_id_error = (
                        f'Ward ID "{raw.upper()}" not found. '
                        f"Demo IDs: 2022UMT1234 · 2026CS101 · 2025MT089"
                    )
                    st.rerun()
                else:
                    # Save fetched data — entire dashboard reads from here
                    st.session_state.ward_id        = raw.upper()
                    st.session_state.ward_data      = fetched
                    st.session_state.ward_id_error  = ""
                    st.session_state.chat_messages  = []
                    st.rerun()

        st.markdown("""
        <p style="text-align:center;font-size:0.63rem;color:rgba(100,116,139,0.42);
                  margin-top:12px;line-height:1.6;">
            Don't know the ID? Check the admit card or contact the Academic Section.
        </p>
        """, unsafe_allow_html=True)

        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("← Change Role", use_container_width=True, key="btn_back_role"):
            st.session_state.user_role     = None
            st.session_state.ward_id_error = ""
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()


# ═════════════════════════════════════════════════════════════════════════════
# ████  SCREEN 4 — GUARDIAN DASHBOARD  ████
#
# All HTML is built as plain strings BEFORE st.markdown().
# No Python logic (.join, if-else, comprehensions) inside f-string { }.
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.user_role == "guardian":

    wd = st.session_state.ward_data   # all ward data lives here

    # ── Top bar ──────────────────────────────────────────────────────────────
    top_l, top_r = st.columns([5, 1])
    with top_l:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:12px;padding-bottom:4px;">'
            '<div style="width:36px;height:36px;'
            'background:linear-gradient(135deg,#3B82F6,#6D28D9);'
            'border-radius:10px;display:flex;align-items:center;'
            'justify-content:center;font-size:0.9rem;">🎓</div>'
            '<div>'
            '<span style="font-family:\'Plus Jakarta Sans\',sans-serif;'
            'font-weight:800;font-size:0.95rem;color:#F1F5F9;">AskMNIT</span>'
            '<span style="margin-left:8px;font-size:0.6rem;color:#10B981;font-weight:700;">'
            '● Online · Guardian Mode</span>'
            '</div>'
            '<div style="margin-left:8px;padding:4px 12px;border-radius:99px;'
            'background:rgba(139,92,246,0.12);border:1px solid rgba(139,92,246,0.28);'
            'font-size:0.65rem;font-weight:700;color:#A78BFA;">'
            '👨‍👧 Guardian · ' + wd["roll"] + '</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with top_r:
        if st.button("🚪 Sign Out", key="guardian_logout"):
            logout()

    st.divider()

    # ── Two-column layout: left = data cards, right = chatbot ────────────────
    left_col, right_col = st.columns([1, 1], gap="large")

    # ══════════════════════════════════════════════════════
    # LEFT COLUMN — DATA CARDS
    # ══════════════════════════════════════════════════════
    with left_col:

        # ── CARD 1: WARD SUMMARY ─────────────────────────
        st.markdown(
            '<div style="background:linear-gradient(160deg,#0D1221,#080C18);'
            'border:1px solid rgba(139,92,246,0.20);border-radius:16px;'
            'padding:20px 20px 4px;margin-bottom:4px;">',
            unsafe_allow_html=True
        )

        # Avatar + name row — using Streamlit columns so no nested HTML logic
        av_col, info_col = st.columns([1, 4])
        with av_col:
            st.markdown(
                '<div style="width:52px;height:52px;border-radius:13px;'
                'background:linear-gradient(135deg,#7C3AED,#A78BFA);'
                'display:flex;align-items:center;justify-content:center;'
                'font-size:1.1rem;font-weight:800;color:white;'
                'box-shadow:0 4px 16px rgba(139,92,246,0.28);">'
                + wd["initials"] + '</div>',
                unsafe_allow_html=True
            )
        with info_col:
            st.markdown(
                '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;'
                'font-weight:800;font-size:1rem;color:#F1F5F9;margin-bottom:2px;">'
                + wd["name"] + '</div>'
                '<div style="font-size:0.72rem;color:rgba(148,163,184,0.60);'
                'line-height:1.5;margin-bottom:6px;">'
                + wd["course"] + " · " + wd["semester"] + '</div>'
                '<span style="display:inline-flex;align-items:center;gap:5px;'
                'padding:3px 10px;border-radius:999px;'
                'background:rgba(16,185,129,0.12);font-size:0.67rem;'
                'font-weight:700;color:#34D399;">'
                '<span style="width:6px;height:6px;border-radius:50%;'
                'background:#34D399;display:inline-block;"></span>'
                + wd["campus_status"] + '</span>',
                unsafe_allow_html=True
            )

        # Info grid — 4 cells using st.columns (safe, no HTML join)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div style="border-top:1px solid rgba(255,255,255,0.07);'
            'padding-top:12px;margin-bottom:4px;">',
            unsafe_allow_html=True
        )
        g1, g2 = st.columns(2)
        with g1:
            st.markdown(
                '<div style="background:rgba(255,255,255,0.04);border-radius:10px;'
                'padding:10px 12px;margin-bottom:8px;">'
                '<div style="font-size:0.58rem;color:rgba(100,116,139,0.55);'
                'font-weight:700;text-transform:uppercase;letter-spacing:0.8px;'
                'margin-bottom:3px;">🏢 Hostel</div>'
                '<div style="font-size:0.74rem;color:#E2E8F0;font-weight:600;">'
                + wd["hostel_block"] + '</div></div>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<div style="background:rgba(255,255,255,0.04);border-radius:10px;'
                'padding:10px 12px;">'
                '<div style="font-size:0.58rem;color:rgba(100,116,139,0.55);'
                'font-weight:700;text-transform:uppercase;letter-spacing:0.8px;'
                'margin-bottom:3px;">📱 Contact</div>'
                '<div style="font-size:0.74rem;color:#E2E8F0;font-weight:600;">'
                + wd["warden_phone"] + '</div></div>',
                unsafe_allow_html=True
            )
        with g2:
            st.markdown(
                '<div style="background:rgba(255,255,255,0.04);border-radius:10px;'
                'padding:10px 12px;margin-bottom:8px;">'
                '<div style="font-size:0.58rem;color:rgba(100,116,139,0.55);'
                'font-weight:700;text-transform:uppercase;letter-spacing:0.8px;'
                'margin-bottom:3px;">👷 Warden</div>'
                '<div style="font-size:0.74rem;color:#E2E8F0;font-weight:600;">'
                + wd["warden"] + '</div></div>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<div style="background:rgba(255,255,255,0.04);border-radius:10px;'
                'padding:10px 12px;">'
                '<div style="font-size:0.58rem;color:rgba(100,116,139,0.55);'
                'font-weight:700;text-transform:uppercase;letter-spacing:0.8px;'
                'margin-bottom:3px;">🎓 Roll No</div>'
                '<div style="font-size:0.74rem;color:#E2E8F0;font-weight:600;">'
                + wd["roll"] + '</div></div>',
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # ── CARD 2: ATTENDANCE ────────────────────────────
        att_pct   = wd["overall_att"]
        att_c     = att_color(att_pct)
        att_7d    = wd["att_7d"]

        st.markdown(
            '<div style="background:linear-gradient(160deg,#0D1221,#080C18);'
            'border:1px solid rgba(255,255,255,0.08);border-radius:16px;'
            'padding:20px 20px 16px;margin-bottom:4px;">',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div style="font-size:0.63rem;color:rgba(100,116,139,0.55);'
            'font-weight:700;text-transform:uppercase;letter-spacing:1px;'
            'margin-bottom:12px;">Attendance</div>',
            unsafe_allow_html=True
        )

        att_left, att_right = st.columns([3, 1])
        with att_left:
            st.markdown(
                '<div style="font-size:2.2rem;font-weight:800;color:' + att_c + ';'
                'letter-spacing:-1px;line-height:1;">' + str(att_pct) + '%</div>'
                '<div style="font-size:0.72rem;color:rgba(148,163,184,0.55);margin-top:4px;">'
                'Overall · Last 7 days: <span style="color:' + att_c + ';font-weight:600;">'
                + att_7d + '</span></div>',
                unsafe_allow_html=True
            )
        with att_right:
            # Conic-gradient circle — pre-computed fill value
            fill_pct  = str(att_pct)
            empty_pct = str(att_pct)
            st.markdown(
                '<div style="width:56px;height:56px;border-radius:50%;'
                'background:conic-gradient(' + att_c + ' 0% ' + fill_pct + '%,'
                'rgba(255,255,255,0.07) ' + empty_pct + '% 100%);'
                'display:flex;align-items:center;justify-content:center;">'
                '<div style="width:40px;height:40px;border-radius:50%;'
                'background:#0D1221;display:flex;align-items:center;'
                'justify-content:center;font-size:0.65rem;font-weight:800;'
                'color:' + att_c + ';">' + str(att_pct) + '%</div></div>',
                unsafe_allow_html=True
            )

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.progress(att_pct / 100)

        if att_pct < 75:
            st.markdown(
                '<div style="background:rgba(245,158,11,0.08);'
                'border:1px solid rgba(245,158,11,0.20);border-radius:8px;'
                'padding:8px 12px;margin-top:10px;'
                'font-size:0.72rem;color:#FCD34D;line-height:1.5;">'
                '⚠️ Below 75% threshold — exam eligibility may be affected.</div>',
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

        # Subject-wise expander — each subject rendered via Streamlit widgets
        with st.expander("📊 View Subject-wise Attendance", expanded=False):
            for subj, pct in wd["att_subjects"].items():
                col_s, col_p = st.columns([4, 1])
                with col_s:
                    badge_bg  = att_badge_bg(pct)
                    badge_lbl = att_badge_label(pct)
                    txt_c     = att_text_color(pct)
                    bar_c     = att_color(pct)
                    st.markdown(
                        '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;'
                        'font-weight:600;font-size:0.80rem;color:' + txt_c + ';'
                        'margin-bottom:4px;">' + subj +
                        '<span style="margin-left:6px;font-size:0.58rem;'
                        'background:' + badge_bg + ';color:' + bar_c + ';'
                        'padding:1px 7px;border-radius:4px;">' + badge_lbl + '</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )
                    st.progress(pct / 100)
                with col_p:
                    st.markdown(
                        '<div style="text-align:right;font-weight:800;font-size:1rem;'
                        'color:' + att_color(pct) + ';padding-top:2px;">'
                        + str(pct) + '%</div>',
                        unsafe_allow_html=True
                    )
                st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)

            st.markdown(
                '<p style="font-size:0.62rem;color:rgba(100,116,139,0.45);'
                'text-align:center;margin-top:8px;">'
                'Min. required: 75% · Data synced from ERP</p>',
                unsafe_allow_html=True
            )

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # ── CARD 3: FEE & FINANCE ─────────────────────────
        st.markdown(
            '<div style="background:linear-gradient(160deg,#0D1221,#080C18);'
            'border:1px solid rgba(245,158,11,0.20);border-radius:16px;'
            'padding:20px 20px 16px;margin-bottom:4px;">',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div style="font-size:0.63rem;color:rgba(100,116,139,0.55);'
            'font-weight:700;text-transform:uppercase;letter-spacing:1px;'
            'margin-bottom:12px;">Fee &amp; Finance · ' + wd["fee_semester"] + '</div>',
            unsafe_allow_html=True
        )

        fee_l, fee_r = st.columns([1, 1])
        with fee_l:
            st.markdown(
                '<div style="font-size:0.72rem;color:rgba(148,163,184,0.55);'
                'margin-bottom:3px;">Pending Amount</div>'
                '<div style="font-size:2rem;font-weight:800;color:#F59E0B;'
                'letter-spacing:-1px;">₹' + wd["fee_pending"] + '</div>',
                unsafe_allow_html=True
            )
        with fee_r:
            st.markdown(
                '<div style="text-align:right;">'
                '<div style="font-size:0.62rem;color:rgba(100,116,139,0.50);'
                'margin-bottom:2px;">Due Date</div>'
                '<div style="font-size:0.88rem;font-weight:700;color:#EF4444;">'
                + wd["fee_due_date"] + '</div></div>',
                unsafe_allow_html=True
            )

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # Fee breakdown — each row rendered individually (no join)
        for item, amount in wd["fee_breakdown"]:
            fi_col, fa_col = st.columns([3, 1])
            with fi_col:
                st.markdown(
                    '<div style="font-size:0.78rem;color:rgba(148,163,184,0.55);'
                    'padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.05);">'
                    + item + '</div>',
                    unsafe_allow_html=True
                )
            with fa_col:
                st.markdown(
                    '<div style="font-size:0.78rem;font-weight:700;color:#F1F5F9;'
                    'text-align:right;padding:6px 0;'
                    'border-bottom:1px solid rgba(255,255,255,0.05);">'
                    + amount + '</div>',
                    unsafe_allow_html=True
                )

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Pay Now button
        st.markdown('<div class="pay-btn">', unsafe_allow_html=True)
        if st.button("💳  Pay Now →", use_container_width=True, key="guardian_pay_now"):
            st.info("🔗 Redirecting to MNIT fee payment portal… (wire real URL here)")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # ── CARD 4: NOTICES ───────────────────────────────
        st.markdown(
            '<div style="background:linear-gradient(160deg,#0D1221,#080C18);'
            'border:1px solid rgba(255,255,255,0.08);border-radius:16px;'
            'padding:18px 20px 14px;margin-bottom:4px;">'
            '<div style="font-size:0.63rem;color:rgba(100,116,139,0.55);'
            'font-weight:700;text-transform:uppercase;letter-spacing:1px;'
            'margin-bottom:12px;">📌 Notices</div>',
            unsafe_allow_html=True
        )
        for i, notice in enumerate(wd["notices"]):
            num = "0" + str(i + 1)
            st.markdown(
                '<div style="display:flex;gap:10px;padding:9px 12px;'
                'background:rgba(255,255,255,0.03);border-radius:9px;margin-bottom:6px;">'
                '<span style="font-size:0.62rem;color:rgba(100,116,139,0.50);'
                'font-weight:700;margin-top:1px;flex-shrink:0;">' + num + '</span>'
                '<span style="font-size:0.77rem;color:rgba(148,163,184,0.65);'
                'line-height:1.5;">' + notice + '</span></div>',
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # Quick metrics strip
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("CGPA", f"{wd['cgpa']} / 10", "Current sem")
        with m2:
            st.metric("Fee Pending", "₹" + wd["fee_pending"], f"Due {wd['fee_due_date']}")
        with m3:
            att_delta = "Above 75% ✓" if wd["overall_att"] >= 75 else "Below 75% ⚠️"
            st.metric("Attendance", f"{wd['overall_att']}%", att_delta)

    # ══════════════════════════════════════════════════════
    # RIGHT COLUMN — CHATBOT
    # ══════════════════════════════════════════════════════
    with right_col:

        # Chat header
        first_name = wd["name"].split()[0]
        st.markdown(
            '<div style="display:flex;align-items:center;gap:12px;'
            'padding-bottom:16px;border-bottom:1px solid rgba(255,255,255,0.07);'
            'margin-bottom:16px;">'
            '<div style="width:38px;height:38px;border-radius:10px;'
            'background:linear-gradient(135deg,#3B82F6,#6D28D9);'
            'display:flex;align-items:center;justify-content:center;font-size:1rem;">🤖</div>'
            '<div>'
            '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;'
            'font-weight:800;font-size:0.95rem;color:#F1F5F9;">AskMNIT AI</div>'
            '<div style="font-size:0.62rem;color:#10B981;font-weight:600;">'
            '● Guardian Mode · Focused on ' + wd["name"] + '</div>'
            '</div></div>',
            unsafe_allow_html=True
        )

        # Suggestion pills (shown only when chat is empty)
        GUARDIAN_PILLS = [
            ("📋", "Check Ward's Attendance"),
            ("💳", "Pay Semester Fees"),
            ("🏢", "Hostel Leave Rules"),
            ("📞", "Contact Warden"),
            ("📅", "Academic Calendar"),
        ]

        if not st.session_state.chat_messages:
            st.markdown(
                '<div style="text-align:center;padding:28px 16px 20px;opacity:0.55;">'
                '<div style="font-size:2rem;margin-bottom:10px;">👨‍👧</div>'
                '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;'
                'font-weight:700;font-size:0.88rem;color:#F1F5F9;margin-bottom:5px;">'
                'Ask me about ' + first_name + "'s academics</div>"
                '<div style="font-size:0.75rem;color:rgba(241,245,249,0.48);'
                'max-width:280px;margin:0 auto;line-height:1.6;">'
                'Attendance, fees, hostel, exams — I have it all.</div>'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<p style="color:rgba(241,245,249,0.25);font-size:0.60rem;'
                'letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;'
                'font-family:Plus Jakarta Sans,sans-serif;font-weight:700;">💡 Try asking</p>',
                unsafe_allow_html=True
            )

            st.markdown('<div class="pill-zone">', unsafe_allow_html=True)
            pill_cols = st.columns(len(GUARDIAN_PILLS))
            for i, (emoji, label) in enumerate(GUARDIAN_PILLS):
                with pill_cols[i]:
                    if st.button(f"{emoji} {label}", key=f"gpill_{i}", use_container_width=True):
                        st.session_state.chat_messages.append({"role": "user", "content": label})
                        st.session_state.pending_ai = True
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        else:
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # ── AI response ──────────────────────────────────
        if st.session_state.pending_ai and st.session_state.chat_messages:
            last_msg = st.session_state.chat_messages[-1]["content"]
            with st.chat_message("assistant"):
                if client is None:
                    lower = last_msg.lower()
                    if "attendance" in lower:
                        resp = (
                            f"📊 **{wd['name']}'s Attendance:** Overall **{wd['overall_att']}%**. "
                            f"Last 7 days: **{wd['att_7d']}**. "
                            + ("⚠️ Below 75% threshold." if wd["overall_att"] < 75 else "✅ Above minimum.")
                        )
                    elif "fee" in lower or "pay" in lower:
                        resp = (
                            f"💳 Outstanding fee for {wd['fee_semester']}: **₹{wd['fee_pending']}**, "
                            f"due by **{wd['fee_due_date']}**. Click 'Pay Now' to proceed."
                        )
                    elif "hostel" in lower or "warden" in lower:
                        resp = (
                            f"🏢 **{wd['name']}** stays in **{wd['hostel_block']}**. "
                            f"Warden: **{wd['warden']}** · 📞 {wd['warden_phone']}. "
                            "Hostel leave requires ERP form submission 48 hrs in advance."
                        )
                    elif "contact" in lower or "hod" in lower or "admin" in lower:
                        resp = (
                            f"📞 For HOD / admin queries, visit the MNIT Academic Section (Block A). "
                            f"Warden: **{wd['warden']}** at {wd['warden_phone']}."
                        )
                    elif "exam" in lower or "schedule" in lower:
                        resp = f"📅 Next exam: **{wd['next_exam']}**. Full schedule on the ERP portal."
                    elif "calendar" in lower:
                        resp = "📅 The academic calendar is available at erp.mnit.ac.in. Key dates: Mid-sems Mar 20–27, End-sems Apr 28 – May 10."
                    else:
                        resp = (
                            f"I'm AskMNIT — your guardian assistant for **{wd['name']}** ({wd['roll']}). "
                            f"You asked: *{last_msg}*. "
                            "Add `GROQ_API_KEY` to `.streamlit/secrets.toml` for full AI responses."
                        )
                    st.markdown(resp)
                    response_text = resp
                else:
                    # [BACKEND] Live Groq call with guardian-aware system prompt
                    system_prompt = (
                        f"You are AskMNIT, a helpful AI assistant for MNIT Jaipur, serving a Guardian/Parent. "
                        f"Ward: {wd['name']}, {wd['course']}, {wd['semester']}, Roll: {wd['roll']}. "
                        f"Attendance: {wd['overall_att']}% overall. "
                        f"Fee pending: ₹{wd['fee_pending']} due {wd['fee_due_date']}. "
                        f"Hostel: {wd['hostel_block']}. Warden: {wd['warden']} ({wd['warden_phone']}). "
                        f"Next exam: {wd['next_exam']}. "
                        "Answer only about this specific student. Be concise and factual."
                    )
                    try:
                        stream = client.chat.completions.create(
                            messages=[
                                {"role": "system", "content": system_prompt},
                                *[{"role": m["role"], "content": m["content"]}
                                  for m in st.session_state.chat_messages],
                            ],
                            model="llama-3.3-70b-versatile",
                            stream=True,
                        )
                        def _gen():
                            for chunk in stream:
                                delta = chunk.choices[0].delta.content
                                if delta:
                                    yield delta
                        response_text = st.write_stream(_gen())
                    except Exception as e:
                        response_text = f"⚠️ Error: {e}"
                        st.error(response_text)

                st.session_state.chat_messages.append(
                    {"role": "assistant", "content": response_text}
                )
            st.session_state.pending_ai = False
            st.rerun()

        # Chat input
        if prompt := st.chat_input(
            f"Ask about {first_name}'s attendance, fees, hostel…",
            key="guardian_chat_input"
        ):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            st.session_state.pending_ai = True
            st.rerun()

        st.markdown("""
        <p style="text-align:center;font-size:0.61rem;color:rgba(100,116,139,0.40);
                  margin-top:8px;line-height:1.5;">
            AskMNIT can make mistakes. Verify critical info with official college admin.
        </p>
        """, unsafe_allow_html=True)

    st.stop()


# ═════════════════════════════════════════════════════════════════════════════
# ████  SCREEN 5 — GENERIC DASHBOARD (student / fresher)  ████
# ═════════════════════════════════════════════════════════════════════════════
role  = st.session_state.user_role
phone = st.session_state.user_phone

ROLE_META = {
    "student": {"icon": "🏫", "label": "Current Student",    "color": "#10B981", "border": "rgba(16,185,129,0.22)"},
    "fresher": {"icon": "🎓", "label": "Prospective Student", "color": "#60A5FA", "border": "rgba(59,130,246,0.22)"},
}
rmeta = ROLE_META.get(role, ROLE_META["fresher"])

# Top bar
top_l, top_r = st.columns([5, 1])
with top_l:
    st.markdown(
        '<div style="display:flex;align-items:center;gap:12px;padding-bottom:4px;">'
        '<div style="width:34px;height:34px;'
        'background:linear-gradient(135deg,#3B82F6,#6D28D9);'
        'border-radius:9px;display:flex;align-items:center;'
        'justify-content:center;font-size:0.85rem;">🎓</div>'
        '<div>'
        '<span style="font-family:\'Plus Jakarta Sans\',sans-serif;'
        'font-weight:800;font-size:0.92rem;color:#F1F5F9;">AskMNIT</span>'
        '<span style="margin-left:8px;font-size:0.6rem;color:#10B981;font-weight:700;">'
        '● Online</span>'
        '</div>'
        '<div style="margin-left:8px;padding:3px 10px;border-radius:99px;'
        'background:' + rmeta["border"].replace("0.22", "0.10") + ';'
        'border:1px solid ' + rmeta["border"] + ';'
        'font-size:0.65rem;font-weight:700;color:' + rmeta["color"] + ';">'
        + rmeta["icon"] + " " + rmeta["label"] + '</div></div>',
        unsafe_allow_html=True
    )
with top_r:
    if st.button("🚪 Sign Out", key="generic_logout"):
        logout()

st.divider()

# Suggestion pills
PILLS = {
    "student": [
        ("🕐","Today's Timetable"), ("📊","View Detailed Attendance"),
        ("📝","Download PYQs"), ("🏆","Result Dashboard"), ("🔗","ERP Login"),
    ],
    "fresher": [
        ("🎓","Admission Process 2026"), ("📊","Last Year Cut-offs"),
        ("💼","Placement Statistics"), ("🏛️","Campus Tour & Facilities"), ("💰","Fee Structure"),
    ],
}
current_pills = PILLS.get(role, PILLS["fresher"])

st.markdown(
    '<p style="color:rgba(241,245,249,0.25);font-size:0.6rem;letter-spacing:1.5px;'
    'text-transform:uppercase;margin-bottom:8px;'
    'font-family:Plus Jakarta Sans,sans-serif;font-weight:700;">💡 Try asking</p>',
    unsafe_allow_html=True
)

st.markdown('<div class="pill-zone">', unsafe_allow_html=True)
pcols = st.columns(len(current_pills))
for i, (emoji, label) in enumerate(current_pills):
    with pcols[i]:
        if st.button(f"{emoji} {label}", key=f"pill_{i}", use_container_width=True):
            if label == "View Detailed Attendance" and role == "student":
                st.session_state.show_attendance = not st.session_state.show_attendance
                st.rerun()
            else:
                st.session_state.chat_messages.append({"role": "user", "content": label})
                st.session_state.pending_ai = True
                st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# Attendance detail panel (student only)
if st.session_state.show_attendance and role == "student":
    sdata      = fetch_student_data(phone)
    attendance = sdata["attendance"]
    overall    = round(sum(attendance.values()) / len(attendance))

    st.markdown(
        '<div style="background:linear-gradient(160deg,#0D1221,#080C18);'
        'border:1px solid rgba(100,120,200,0.20);border-radius:16px;'
        'padding:20px 24px 14px;margin-bottom:16px;">'
        '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;font-weight:800;'
        'font-size:0.95rem;color:#F1F5F9;margin-bottom:4px;">📊 Subject-wise Attendance</div>'
        '<div style="font-size:0.67rem;color:rgba(148,163,184,0.50);margin-bottom:14px;">'
        'Minimum required: 75% · Data synced from ERP</div>',
        unsafe_allow_html=True
    )

    for subj, pct in attendance.items():
        badge_bg  = att_badge_bg(pct)
        badge_lbl = att_badge_label(pct)
        txt_c     = att_text_color(pct)
        bar_c     = att_color(pct)
        col_s, col_p = st.columns([4, 1])
        with col_s:
            st.markdown(
                '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;'
                'font-weight:600;font-size:0.82rem;color:' + txt_c + ';margin-bottom:4px;">'
                + subj +
                '<span style="margin-left:6px;font-size:0.60rem;'
                'background:' + badge_bg + ';color:' + bar_c + ';'
                'padding:1px 7px;border-radius:4px;">' + badge_lbl + '</span>'
                '</div>',
                unsafe_allow_html=True
            )
            st.progress(pct / 100)
        with col_p:
            st.markdown(
                '<div style="text-align:right;font-weight:800;font-size:1rem;'
                'color:' + bar_c + ';padding-top:2px;">' + str(pct) + '%</div>',
                unsafe_allow_html=True
            )
        st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    oc1, oc2, oc3 = st.columns(3)
    with oc1:
        st.metric("Overall Attendance", f"{overall}%",
                  "+2% from last month" if overall >= 75 else "Below 75% ⚠️")
    with oc2:
        low = sum(1 for p in attendance.values() if p < 75)
        st.metric("Subjects Below 75%", str(low), "All clear ✓" if not low else "Need attention")
    with oc3:
        ne = fetch_student_data(phone)["next_exam"]
        parts = ne.split("—")
        st.metric("Next Exam", parts[0].strip(), parts[1].strip() if len(parts) > 1 else "")

    if st.button("✖ Close Attendance Panel", key="close_att"):
        st.session_state.show_attendance = False
        st.rerun()
    st.divider()

# Quick metrics
if role == "student":
    sdata = fetch_student_data(phone)
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("CGPA", f"{sdata['cgpa']} / 10", "+0.2 this sem")
    with m2: st.metric("Fee Due", sdata["fee_due"], "5 days left")
    with m3:
        ne = sdata["next_exam"]
        parts = ne.split("—")
        st.metric("Next Exam", parts[0].strip(), parts[1].strip() if len(parts) > 1 else "")
elif role == "fresher":
    fd = FRESHER_DATA
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("Avg Package 2025",  fd["placement_avg"],     "+8% YoY")
    with m2: st.metric("Highest Package",   fd["placement_highest"],  "Amazon")
    with m3: st.metric("Placement Rate",    fd["placement_rate"],     "Batch 2025")

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# Chat history
if not st.session_state.chat_messages:
    st.markdown(
        '<div style="text-align:center;padding:40px 20px;opacity:0.55;">'
        '<div style="font-size:2.2rem;margin-bottom:12px;">' + rmeta["icon"] + '</div>'
        '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;font-weight:700;'
        'font-size:0.95rem;color:#F1F5F9;margin-bottom:6px;">I\'m AskMNIT</div>'
        '<div style="font-size:0.8rem;color:rgba(241,245,249,0.50);'
        'max-width:360px;margin:0 auto;">'
        + ("Ask me about PYQs, timetable, results, ERP & more." if role == "student"
           else "Ask me about MNIT admissions, cut-offs, placements, fees & campus life.")
        + '</div></div>',
        unsafe_allow_html=True
    )
else:
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Pending AI
if st.session_state.pending_ai and st.session_state.chat_messages:
    last_msg = st.session_state.chat_messages[-1]["content"]
    with st.chat_message("assistant"):
        if client is None:
            resp = (
                f"I'm AskMNIT. You asked: **{last_msg}**. "
                "Add `GROQ_API_KEY` to `.streamlit/secrets.toml` for live AI responses."
            )
            st.markdown(resp)
            response_text = resp
        else:
            role_ctx = {
                "student": "The user is a current MNIT Jaipur B.Tech student. Help with PYQs, timetable, attendance, results, ERP, placements.",
                "fresher": "The user is a prospective student interested in joining MNIT Jaipur. Help with admissions, JoSAA, cut-offs, fee structure, placement stats, campus life.",
            }
            sp = (
                "You are AskMNIT — a helpful AI assistant for MNIT Jaipur. "
                + role_ctx.get(role, "") + " Be concise, warm and accurate."
            )
            try:
                stream = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": sp},
                        *[{"role": m["role"], "content": m["content"]}
                          for m in st.session_state.chat_messages],
                    ],
                    model="llama-3.3-70b-versatile",
                    stream=True,
                )
                def _gen2():
                    for chunk in stream:
                        delta = chunk.choices[0].delta.content
                        if delta:
                            yield delta
                response_text = st.write_stream(_gen2())
            except Exception as e:
                response_text = f"⚠️ Error: {e}"
                st.error(response_text)

        st.session_state.chat_messages.append(
            {"role": "assistant", "content": response_text}
        )
    st.session_state.pending_ai = False
    st.rerun()

_ph = {
    "student": "Ask about PYQs, timetable, attendance, ERP…",
    "fresher": "Ask about admissions, cut-offs, placements, fees…",
}
if prompt := st.chat_input(_ph.get(role, "Ask me anything…"), key="generic_chat_input"):
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    st.session_state.pending_ai = True
    st.rerun()

st.markdown("""
<p style="text-align:center;font-size:0.62rem;color:rgba(100,116,139,0.42);
          margin-top:8px;line-height:1.5;">
    AskMNIT can make mistakes. Please verify important info with official admin.
</p>
""", unsafe_allow_html=True)
