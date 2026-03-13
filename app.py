# ╔══════════════════════════════════════════════════════════════════════════╗
# ║            AskMNIT — Streamlit App  (Final · Copy-Paste Ready)           ║
# ║                                                                          ║
# ║  BUG FIX: All HTML helpers are pre-computed BEFORE st.markdown() calls. ║
# ║  Never call Python functions inside { } in an f-string passed to         ║
# ║  st.markdown() — Streamlit escapes the return value and prints raw       ║
# ║  code on screen instead of rendering it as HTML.                         ║
# ║                                                                          ║
# ║  ROUTING (st.session_state):                                             ║
# ║   logged_in=False                       → LOGIN                          ║
# ║   logged_in=True, user_role=None        → ROLE SELECTION                 ║
# ║   role="guardian", ward_data=None       → WARD ID ENTRY                  ║
# ║   role="guardian", ward_data set        → GUARDIAN DASHBOARD             ║
# ║   role="student" / "fresher"            → GENERIC DASHBOARD              ║
# ╚══════════════════════════════════════════════════════════════════════════╝

import streamlit as st
from groq import Groq

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
# Guardian ward data is keyed by the STUDENT's roll / enrollment number.
#
# [BACKEND] Replace fetch_ward() with a real API call, e.g.:
#   import requests
#   def fetch_ward(ward_id):
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
            "Economics":                     85,
            "Mineral Processing":            78,
            "Foundry & Casting":             92,
            "Welding":                       65,
            "Mobility Systems":              88,
            "Engg. Materials & Metallurgy":  74,
        },
        "fee_pending":  "Rs. 18,500",
        "fee_due_date": "17 Mar 2026",
        "fee_semester": "Semester 6",
        "fee_breakdown": [
            ("Tuition Fee", "Rs. 10,000"),
            ("Hostel Fee",  "Rs. 5,500"),
            ("Library Fee", "Rs. 500"),
            ("Sports Fee",  "Rs. 1,000"),
            ("Exam Fee",    "Rs. 1,500"),
        ],
        "next_exam": "Mineral Processing - 20 Mar 2026",
        "notices": [
            "Mid-Semester exams: Mar 20-27",
            "Parent-Teacher Meet: Mar 15 (10 AM - 1 PM)",
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
        "fee_pending":  "Rs. 15,000",
        "fee_due_date": "Oct 15, 2026",
        "fee_semester": "Semester 4",
        "fee_breakdown": [
            ("Tuition Fee", "Rs. 10,000"),
            ("Hostel Fee",  "Rs. 3,500"),
            ("Library Fee", "Rs. 500"),
            ("Sports Fee",  "Rs. 1,000"),
        ],
        "next_exam": "Data Structures - Apr 5, 2026",
        "notices": [
            "Sem 4 results expected May 10",
            "Lab submissions: Mar 25 (hard deadline)",
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
        "fee_pending":  "Rs. 8,500",
        "fee_due_date": "Apr 20, 2026",
        "fee_semester": "Semester 6",
        "fee_breakdown": [
            ("Mess Fee",    "Rs. 4,000"),
            ("Library Fee", "Rs. 500"),
            ("Tuition Fee", "Rs. 4,000"),
        ],
        "next_exam": "Mineral Processing - Mar 28, 2026",
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
        "branch":  "B.Tech Metallurgy - Sem 6",
        "cgpa":    8.4,
        "attendance": {
            "Economics":                     85,
            "Mineral Processing":            78,
            "Foundry & Casting":             92,
            "Welding":                       65,
            "Mobility Systems":              88,
            "Engg. Materials & Metallurgy":  74,
        },
        "fee_due":   "Rs. 18,500 by 17 Mar 2026",
        "next_exam": "Mineral Processing - 20 Mar 2026",
    },
}

FRESHER_DATA = {
    "placement_avg":     "Rs. 12.4 LPA",
    "placement_highest": "Rs. 48 LPA (Amazon)",
    "placement_rate":    "94%",
}


# ─────────────────────────────────────────────────────────────────────────────
# PURE HELPERS  (return plain values — no HTML returned from these)
# ─────────────────────────────────────────────────────────────────────────────
def fetch_ward(ward_id: str):
    """Look up ward by college ID. Returns dict or None."""
    return WARD_DB.get(ward_id.strip().upper())

def get_student(phone: str):
    return STUDENT_DB.get(phone, list(STUDENT_DB.values())[0])

def att_color(pct: int) -> str:
    return "#EF4444" if pct < 65 else "#F59E0B" if pct < 75 else "#10B981"

def att_badge(pct: int) -> str:
    return "Critical" if pct < 65 else "Low" if pct < 75 else "Safe"

def att_text_color(pct: int) -> str:
    return "#FCA5A5" if pct < 65 else "#FCD34D" if pct < 75 else "#E2E8F0"

def att_bg_color(pct: int) -> str:
    if pct < 65:
        return "rgba(239,68,68,0.14)"
    elif pct < 75:
        return "rgba(245,158,11,0.12)"
    return "rgba(16,185,129,0.10)"


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE — initialise all keys once on first load
# ─────────────────────────────────────────────────────────────────────────────
_DEFAULTS = {
    "logged_in":       False,
    "user_phone":      "",
    "user_role":       None,
    "user_name":       "",
    "otp_sent":        False,
    "ward_id":         "",
    "ward_data":       None,
    "ward_id_error":   "",
    "show_att_detail": False,
    "chat_messages":   [],
    "pending_ai":      False,
    "show_attendance": False,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

def logout():
    for k, v in _DEFAULTS.items():
        st.session_state[k] = v
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
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

[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 10px !important;
    color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stTextInput"] label {
    color: rgba(241,245,249,0.60) !important;
    font-size: 0.76rem !important;
    font-weight: 700 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

.stButton > button {
    background: linear-gradient(135deg,#3B82F6,#6D28D9) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    box-shadow: 0 4px 16px rgba(59,130,246,0.25) !important;
    transition: all 0.18s !important;
}
.stButton > button:hover { opacity: 0.90 !important; transform: translateY(-1px) !important; }

.ghost-btn .stButton > button {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    color: rgba(241,245,249,0.55) !important;
    box-shadow: none !important;
}
.ghost-btn .stButton > button:hover {
    background: rgba(59,130,246,0.10) !important;
    color: #F1F5F9 !important;
}

.pill-zone .stButton > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 999px !important;
    color: rgba(241,245,249,0.60) !important;
    font-size: 0.74rem !important;
    font-weight: 500 !important;
    box-shadow: none !important;
}
.pill-zone .stButton > button:hover {
    background: rgba(139,92,246,0.14) !important;
    border-color: rgba(139,92,246,0.32) !important;
    color: #CBD5E1 !important;
}

.pay-btn .stButton > button {
    background: linear-gradient(135deg,#D97706,#F59E0B) !important;
    box-shadow: 0 4px 18px rgba(245,158,11,0.30) !important;
}

[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
    padding: 16px !important;
}
[data-testid="stMetricLabel"] {
    color: rgba(241,245,249,0.40) !important;
    font-size: 0.68rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stMetricValue"] {
    color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 800 !important;
}

[data-testid="stProgress"] > div > div { border-radius: 99px !important; }

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
    background: transparent !important;
    color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stChatInput"] button[data-testid="stChatInputSubmitButton"] {
    background: linear-gradient(135deg,#3B82F6,#6D28D9) !important;
    border-radius: 9px !important;
}

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

[data-testid="stMarkdown"] p, [data-testid="stMarkdown"] li {
    color: rgba(241,245,249,0.70) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
h1, h2, h3 {
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


# =============================================================================
# SCREEN 1 — LOGIN
# =============================================================================
if not st.session_state.logged_in:

    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("""
        <div style="text-align:center;padding:44px 0 28px;">
            <div style="width:58px;height:58px;margin:0 auto 14px;
                        background:linear-gradient(135deg,#3B82F6,#6D28D9);
                        border-radius:15px;display:flex;align-items:center;
                        justify-content:center;font-size:1.7rem;
                        box-shadow:0 8px 28px rgba(59,130,246,0.30);">&#127891;</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.5rem;
                        font-weight:800;color:#F1F5F9;letter-spacing:-0.6px;">AskMNIT</div>
            <div style="font-size:0.72rem;color:rgba(100,116,139,0.65);margin-top:4px;">
                Your campus AI powered by LLaMA 3.3 70B
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:linear-gradient(160deg,#0C1120,#080D19);
                    border:1px solid rgba(100,120,220,0.16);border-radius:20px;
                    padding:24px 28px 10px;box-shadow:0 24px 80px rgba(0,0,0,0.68);">
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.05rem;
                        font-weight:800;color:#F1F5F9;margin-bottom:4px;">Sign in to continue</div>
            <div style="font-size:0.72rem;color:rgba(148,163,184,0.50);margin-bottom:18px;">
                Enter your registered mobile number.
            </div>
        </div>
        """, unsafe_allow_html=True)

        phone_val = st.text_input(
            "Mobile Number",
            placeholder="10-digit number",
            max_chars=10,
            key="login_phone",
        )

        if not st.session_state.otp_sent:
            if st.button("Send OTP", use_container_width=True, key="btn_send_otp"):
                if len(phone_val) == 10 and phone_val.isdigit():
                    # [BACKEND] Send real OTP via Twilio / Firebase here
                    st.session_state.otp_sent = True
                    st.rerun()
                else:
                    st.error("Please enter a valid 10-digit mobile number.")

        if st.session_state.otp_sent:
            st.success("OTP sent to +91 " + phone_val)
            otp_val = st.text_input(
                "Enter OTP",
                placeholder="4 to 6 digit OTP",
                max_chars=6,
                type="password",
                key="login_otp",
            )
            c1, c2 = st.columns([2, 1])
            with c1:
                if st.button("Verify and Continue", use_container_width=True, key="btn_verify"):
                    if len(otp_val) >= 4:
                        # [BACKEND] Verify OTP with your auth provider here
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
                if st.button("Change", use_container_width=True, key="btn_change"):
                    st.session_state.otp_sent = False
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <p style="text-align:center;font-size:0.60rem;color:rgba(100,116,139,0.40);
                  margin-top:14px;line-height:1.6;">
            By continuing you agree to MNIT Terms of Service and Privacy Policy.</p>
        """, unsafe_allow_html=True)

    st.stop()


# =============================================================================
# SCREEN 2 — ROLE SELECTION
# =============================================================================
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
                We will personalise AskMNIT based on your role.
            </div>
        </div>
        """, unsafe_allow_html=True)

        ROLES = [
            ("fresher",  "Prospective Student", "Fresher",
             "Looking to apply for admission.",
             "linear-gradient(135deg,#1D4ED8,#3B82F6)", "rgba(59,130,246,0.28)"),
            ("guardian", "Guardian or Parent", "",
             "Here for my ward or child.",
             "linear-gradient(135deg,#7C3AED,#A78BFA)", "rgba(139,92,246,0.28)"),
            ("student",  "Current Student", "",
             "Already enrolled in the college.",
             "linear-gradient(135deg,#065F46,#10B981)", "rgba(16,185,129,0.28)"),
        ]

        for rid, title, badge, desc, grad, glow in ROLES:
            badge_html = ""
            if badge:
                badge_html = (
                    '<span style="font-size:0.58rem;padding:2px 7px;'
                    'background:rgba(255,255,255,0.14);border-radius:4px;'
                    'font-weight:700;letter-spacing:0.5px;text-transform:uppercase;'
                    'margin-left:8px;">' + badge + '</span>'
                )

            card_html = (
                '<div style="background:rgba(255,255,255,0.025);'
                'border:1px solid rgba(255,255,255,0.08);'
                'border-radius:14px;padding:16px 18px 10px;margin-bottom:4px;">'
                '<div style="display:flex;align-items:center;gap:14px;">'
                '<div style="width:46px;height:46px;border-radius:12px;'
                'background:' + grad + ';display:flex;align-items:center;'
                'justify-content:center;font-size:0.9rem;flex-shrink:0;'
                'box-shadow:0 4px 14px ' + glow + ';">&#128100;</div>'
                '<div>'
                '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;'
                'font-weight:700;font-size:0.92rem;color:#F1F5F9;">'
                + title + badge_html + '</div>'
                '<div style="font-size:0.73rem;color:rgba(148,163,184,0.55);margin-top:2px;">'
                + desc + '</div>'
                '</div></div></div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)

            if st.button("Select  " + title, key="role_" + rid, use_container_width=True):
                # [BACKEND] Persist role to your DB here
                st.session_state.user_role     = rid
                st.session_state.chat_messages = []
                st.session_state.ward_data     = None
                st.session_state.ward_id_error = ""
                st.rerun()

            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    st.stop()


# =============================================================================
# SCREEN 3 — GUARDIAN WARD ID ENTRY
# Condition: role="guardian" AND ward_data is still None
# =============================================================================
if st.session_state.user_role == "guardian" and st.session_state.ward_data is None:

    _, col, _ = st.columns([1, 1.6, 1])
    with col:
        st.markdown("""
        <div style="text-align:center;padding:40px 0 28px;">
            <div style="width:60px;height:60px;margin:0 auto 16px;
                        background:linear-gradient(135deg,#7C3AED,#A78BFA);
                        border-radius:16px;display:flex;align-items:center;
                        justify-content:center;font-size:1.7rem;
                        box-shadow:0 8px 28px rgba(139,92,246,0.32);">&#128106;</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.2rem;
                        font-weight:800;color:#F1F5F9;letter-spacing:-0.4px;margin-bottom:6px;">
                Enter Ward's College ID
            </div>
            <div style="font-size:0.76rem;color:rgba(148,163,184,0.52);
                        line-height:1.6;max-width:320px;margin:0 auto;">
                Enter your child's enrollment or roll number to link
                their academic data to your account.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:linear-gradient(160deg,#0C1120,#080D19);
                    border:1px solid rgba(139,92,246,0.22);border-radius:20px;
                    padding:24px 28px 10px;box-shadow:0 24px 80px rgba(0,0,0,0.70);">
        """, unsafe_allow_html=True)

        ward_input = st.text_input(
            "Ward's College ID or Enrollment Number (required)",
            placeholder="e.g. 2022UMT1234  or  2026CS101",
            key="ward_id_field",
        )

        if st.session_state.ward_id_error:
            err_html = (
                '<div style="background:rgba(239,68,68,0.08);'
                'border:1px solid rgba(239,68,68,0.22);border-radius:8px;'
                'padding:10px 14px;margin:8px 0;font-size:0.74rem;color:#FCA5A5;">'
                + st.session_state.ward_id_error + '</div>'
            )
            st.markdown(err_html, unsafe_allow_html=True)

        if st.button("Link Ward Account", use_container_width=True, key="btn_link_ward"):
            raw = ward_input.strip()
            if not raw:
                st.session_state.ward_id_error = (
                    "This field is required. Please enter your ward's College ID."
                )
                st.rerun()
            else:
                # CORE DATA FETCH — wardCollegeId is the primary key
                # [BACKEND] Replace with real API call (see top of file)
                fetched = fetch_ward(raw)
                if fetched is None:
                    st.session_state.ward_id_error = (
                        'ID "' + raw.upper() + '" not found in college records. '
                        "Demo IDs: 2022UMT1234  or  2026CS101  or  2025MT089"
                    )
                    st.rerun()
                else:
                    # Save ward data — guardian dashboard reads ONLY from here
                    st.session_state.ward_id       = raw.upper()
                    st.session_state.ward_data     = fetched
                    st.session_state.ward_id_error = ""
                    st.session_state.chat_messages = []
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <p style="text-align:center;font-size:0.65rem;color:rgba(100,116,139,0.45);
                  margin-top:12px;line-height:1.6;">
            Do not know the ID? Check the admit card or contact the Academic Section.</p>
        """, unsafe_allow_html=True)

        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("Change Role", use_container_width=True, key="btn_back_role"):
            st.session_state.user_role     = None
            st.session_state.ward_id_error = ""
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()


# =============================================================================
# SCREEN 4a — GUARDIAN DASHBOARD
#
# ALL data comes from  wd = st.session_state.ward_data
# That dict was fetched using the guardian's wardCollegeId.
#
# HTML FIX: Every fragment ({info_grid}, {warn_html}, etc.) is built as a
# plain Python string BEFORE the st.markdown() call.
# We never call Python functions inside { } of an f-string passed to
# st.markdown() — Streamlit escapes the return value and prints raw source
# code on screen instead of rendering HTML.
#
# Layout: NO sidebar | NO nav tabs | NO greeting headings
#         Left = data cards   |   Right = AI chatbot
# =============================================================================
if st.session_state.user_role == "guardian":

    wd          = st.session_state.ward_data
    att_overall = wd["overall_att"]
    att_c       = att_color(att_overall)   # plain string like "#10B981"

    # ── Top bar ──────────────────────────────────────────────────────────────
    tb_l, tb_r = st.columns([6, 1])
    with tb_l:
        topbar = (
            '<div style="display:flex;align-items:center;gap:12px;padding-bottom:4px;">'
            '<div style="width:36px;height:36px;'
            'background:linear-gradient(135deg,#3B82F6,#6D28D9);'
            'border-radius:9px;display:flex;align-items:center;'
            'justify-content:center;font-size:0.95rem;">&#127891;</div>'
            '<span style="font-family:\'Plus Jakarta Sans\',sans-serif;'
            'font-weight:800;font-size:1rem;color:#F1F5F9;">AskMNIT</span>'
            '<span style="margin-left:8px;font-size:0.58rem;'
            'color:#10B981;font-weight:700;">&#9679; Online Guardian Mode</span>'
            '<div style="margin-left:6px;padding:3px 11px;'
            'background:rgba(139,92,246,0.12);'
            'border:1px solid rgba(139,92,246,0.28);'
            'border-radius:99px;font-size:0.63rem;font-weight:700;color:#A78BFA;">'
            'Guardian  ' + wd["roll"] + '</div>'
            '</div>'
        )
        st.markdown(topbar, unsafe_allow_html=True)
    with tb_r:
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True, key="guardian_logout"):
            logout()
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    left_col, right_col = st.columns([1.1, 1], gap="large")

    # =========================================================================
    # LEFT COLUMN — DATA CARDS
    # =========================================================================
    with left_col:

        # ── CARD 1: WARD SUMMARY ─────────────────────────────────────────────
        # Build status tag as a plain string first
        status_tag = (
            '<span style="display:inline-flex;align-items:center;gap:5px;'
            'padding:3px 10px;border-radius:999px;background:rgba(16,185,129,0.12);'
            'font-size:0.67rem;font-weight:700;color:#34D399;">'
            '<span style="width:6px;height:6px;border-radius:50%;'
            'background:#34D399;display:inline-block;"></span>'
            + wd["campus_status"] + '</span>'
        )

        # Build info grid as a plain string — four tiles
        info_grid = ""
        for ico, lbl, val in [
            ("Hostel",  "Hostel",  wd["hostel_block"]),
            ("Warden",  "Warden",  wd["warden"]),
            ("Contact", "Contact", wd["warden_phone"]),
            ("Roll",    "Roll No", wd["roll"]),
        ]:
            info_grid += (
                '<div style="background:rgba(255,255,255,0.04);'
                'border-radius:10px;padding:10px 12px;">'
                '<div style="font-size:0.56rem;color:rgba(100,116,139,0.52);'
                'font-weight:700;text-transform:uppercase;'
                'letter-spacing:0.8px;margin-bottom:3px;">' + lbl + '</div>'
                '<div style="font-size:0.74rem;color:#E2E8F0;'
                'font-weight:600;line-height:1.4;">' + val + '</div>'
                '</div>'
            )

        # Render card 1 — plain string concatenation, no function calls inside
        st.markdown(
            '<div style="background:linear-gradient(160deg,#0D1221,#080C18);'
            'border:1px solid rgba(139,92,246,0.20);border-radius:16px;'
            'padding:20px 22px 18px;margin-bottom:14px;">'

            '<div style="display:flex;align-items:flex-start;gap:14px;margin-bottom:16px;">'
            '<div style="width:54px;height:54px;border-radius:14px;flex-shrink:0;'
            'background:linear-gradient(135deg,#7C3AED,#A78BFA);'
            'display:flex;align-items:center;justify-content:center;'
            'font-size:1.1rem;font-weight:800;color:white;'
            'box-shadow:0 4px 16px rgba(139,92,246,0.28);">'
            + wd["initials"] + '</div>'

            '<div style="flex:1;min-width:0;">'
            '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;'
            'font-weight:800;font-size:1.05rem;color:#F1F5F9;margin-bottom:2px;">'
            + wd["name"] + '</div>'
            '<div style="font-size:0.71rem;color:rgba(148,163,184,0.55);'
            'line-height:1.5;margin-bottom:8px;">'
            + wd["course"] + "  " + wd["semester"] + '</div>'
            + status_tag +
            '</div></div>'

            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:9px;'
            'border-top:1px solid rgba(255,255,255,0.06);padding-top:14px;">'
            + info_grid +
            '</div></div>',
            unsafe_allow_html=True,
        )

        # ── CARD 2: ATTENDANCE ───────────────────────────────────────────────
        # Warning banner — built as plain string before markdown call
        warn_html = ""
        if att_overall < 75:
            warn_html = (
                '<div style="background:rgba(245,158,11,0.08);'
                'border:1px solid rgba(245,158,11,0.22);border-radius:8px;'
                'padding:8px 12px;margin-bottom:14px;font-size:0.71rem;'
                'color:#FCD34D;line-height:1.5;">'
                'Attendance below 75 percent threshold. '
                'Exam eligibility may be affected. Contact HOD.'
                '</div>'
            )

        # Circular ring — plain string, no f-string
        ring_html = (
            '<div style="width:62px;height:62px;border-radius:50%;flex-shrink:0;'
            'background:conic-gradient(' + att_c + ' 0% ' + str(att_overall) + '%,'
            'rgba(255,255,255,0.07) ' + str(att_overall) + '% 100%);'
            'display:flex;align-items:center;justify-content:center;">'
            '<div style="width:46px;height:46px;border-radius:50%;background:#0D1221;'
            'display:flex;align-items:center;justify-content:center;'
            'font-size:0.68rem;font-weight:800;color:' + att_c + ';">'
            + str(att_overall) + '%</div></div>'
        )

        st.markdown(
            '<div style="background:linear-gradient(160deg,#0D1221,#080C18);'
            'border:1px solid rgba(255,255,255,0.09);border-radius:16px;'
            'padding:20px 22px 18px;margin-bottom:14px;">'
            '<div style="font-size:0.60rem;color:rgba(100,116,139,0.52);'
            'font-weight:700;text-transform:uppercase;'
            'letter-spacing:1px;margin-bottom:12px;">Attendance</div>'
            '<div style="display:flex;align-items:center;'
            'justify-content:space-between;margin-bottom:14px;">'
            '<div>'
            '<div style="font-size:2.2rem;font-weight:800;color:' + att_c + ';'
            'letter-spacing:-1px;line-height:1;">' + str(att_overall) + '%</div>'
            '<div style="font-size:0.70rem;color:rgba(148,163,184,0.52);margin-top:4px;">'
            'Overall  Last 7 days: '
            '<span style="color:' + att_c + ';font-weight:700;">'
            + wd["att_7d"] + '</span></div>'
            '</div>'
            + ring_html +
            '</div>'
            + warn_html +
            '</div>',
            unsafe_allow_html=True,
        )

        # Subject-wise toggle
        toggle_label = (
            "View Subject-wise Attendance"
            if not st.session_state.show_att_detail
            else "Hide Subject Details"
        )
        if st.button(toggle_label, key="toggle_att", use_container_width=True):
            st.session_state.show_att_detail = not st.session_state.show_att_detail
            st.rerun()

        if st.session_state.show_att_detail:
            st.markdown(
                '<div style="background:rgba(255,255,255,0.02);'
                'border:1px solid rgba(100,120,200,0.16);border-radius:12px;'
                'padding:16px 18px 12px;margin-top:10px;margin-bottom:14px;">'
                '<div style="font-size:0.60rem;color:rgba(100,116,139,0.52);'
                'font-weight:700;text-transform:uppercase;'
                'letter-spacing:1px;margin-bottom:10px;">'
                'Subject-wise  ' + wd["semester"] + '</div>',
                unsafe_allow_html=True,
            )
            for subj, pct in wd["att_subjects"].items():
                sc  = att_color(pct)
                stc = att_text_color(pct)
                sbg = att_bg_color(pct)
                sb  = att_badge(pct)
                cn, cp = st.columns([4, 1])
                with cn:
                    st.markdown(
                        '<div style="font-size:0.79rem;font-weight:600;color:' + stc + ';'
                        'margin-bottom:4px;">' + subj +
                        '  <span style="font-size:0.57rem;background:' + sbg + ';'
                        'color:' + sc + ';padding:1px 6px;border-radius:4px;">'
                        + sb + '</span></div>',
                        unsafe_allow_html=True,
                    )
                    st.progress(pct / 100)
                with cp:
                    st.markdown(
                        '<div style="text-align:right;font-weight:800;font-size:0.95rem;'
                        'color:' + sc + ';padding-top:2px;">' + str(pct) + '%</div>',
                        unsafe_allow_html=True,
                    )
                st.markdown("<div style='height:3px'></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # ── CARD 3: FEE AND FINANCE ──────────────────────────────────────────
        # Pre-build fee rows as plain string
        fee_rows_html = ""
        for item, amt in wd["fee_breakdown"]:
            fee_rows_html += (
                '<div style="display:flex;justify-content:space-between;'
                'padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);">'
                '<span style="font-size:0.77rem;color:rgba(148,163,184,0.52);">'
                + item + '</span>'
                '<span style="font-size:0.77rem;font-weight:700;color:#F1F5F9;">'
                + amt + '</span></div>'
            )

        st.markdown(
            '<div style="background:linear-gradient(160deg,#0D1221,#080C18);'
            'border:1px solid rgba(245,158,11,0.18);border-radius:16px;'
            'padding:20px 22px 18px;margin-bottom:14px;">'
            '<div style="font-size:0.60rem;color:rgba(100,116,139,0.52);'
            'font-weight:700;text-transform:uppercase;'
            'letter-spacing:1px;margin-bottom:14px;">'
            'Fee and Finance  ' + wd["fee_semester"] + '</div>'
            '<div style="display:flex;align-items:flex-end;'
            'justify-content:space-between;margin-bottom:16px;">'
            '<div>'
            '<div style="font-size:0.70rem;color:rgba(148,163,184,0.50);margin-bottom:3px;">'
            'Pending Amount</div>'
            '<div style="font-size:2rem;font-weight:800;color:#F59E0B;letter-spacing:-1px;">'
            + wd["fee_pending"] + '</div>'
            '</div>'
            '<div style="text-align:right;">'
            '<div style="font-size:0.58rem;color:rgba(100,116,139,0.48);margin-bottom:2px;">'
            'Due Date</div>'
            '<div style="font-size:0.88rem;font-weight:700;color:#EF4444;">'
            + wd["fee_due_date"] + '</div>'
            '</div></div>'
            + fee_rows_html +
            '<div style="display:flex;justify-content:space-between;'
            'padding:10px 0 0;margin-top:4px;">'
            '<span style="font-size:0.85rem;font-weight:700;color:#F1F5F9;">Total</span>'
            '<span style="font-size:0.92rem;font-weight:800;color:#F59E0B;">'
            + wd["fee_pending"] + '</span>'
            '</div></div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="pay-btn">', unsafe_allow_html=True)
        if st.button("Pay Now", use_container_width=True, key="guardian_pay"):
            # [BACKEND] Redirect to MNIT payment gateway URL
            st.info("Redirecting to MNIT payment gateway. Wire the real URL here.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # ── CARD 4: NOTICES ──────────────────────────────────────────────────
        # Pre-build notices as plain string
        notices_html = ""
        for i, notice in enumerate(wd["notices"]):
            notices_html += (
                '<div style="display:flex;gap:10px;padding:9px 12px;'
                'background:rgba(255,255,255,0.03);border-radius:9px;margin-bottom:6px;">'
                '<span style="font-size:0.60rem;color:rgba(100,116,139,0.48);'
                'font-weight:700;margin-top:1px;flex-shrink:0;">0' + str(i + 1) + '</span>'
                '<span style="font-size:0.76rem;color:rgba(148,163,184,0.62);line-height:1.5;">'
                + notice + '</span></div>'
            )

        st.markdown(
            '<div style="background:linear-gradient(160deg,#0D1221,#080C18);'
            'border:1px solid rgba(255,255,255,0.08);border-radius:16px;'
            'padding:18px 20px 14px;margin-bottom:16px;">'
            '<div style="font-size:0.60rem;color:rgba(100,116,139,0.52);'
            'font-weight:700;text-transform:uppercase;'
            'letter-spacing:1px;margin-bottom:10px;">Notices</div>'
            + notices_html + '</div>',
            unsafe_allow_html=True,
        )

        # Quick metrics row
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("CGPA", str(wd["cgpa"]) + " / 10", "Current sem")
        with m2:
            st.metric("Fee Pending", wd["fee_pending"], "Due " + wd["fee_due_date"])
        with m3:
            st.metric(
                "Attendance", str(att_overall) + "%",
                "Above 75% OK" if att_overall >= 75 else "Below 75% Warning",
            )

    # =========================================================================
    # RIGHT COLUMN — AI CHATBOT
    # =========================================================================
    with right_col:

        ward_first = wd["name"].split()[0]

        st.markdown(
            '<div style="display:flex;align-items:center;gap:12px;'
            'padding-bottom:14px;border-bottom:1px solid rgba(255,255,255,0.07);'
            'margin-bottom:14px;">'
            '<div style="width:36px;height:36px;border-radius:9px;'
            'background:linear-gradient(135deg,#3B82F6,#6D28D9);'
            'display:flex;align-items:center;justify-content:center;font-size:1rem;">'
            '&#129302;</div>'
            '<div>'
            '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;'
            'font-weight:800;font-size:0.95rem;color:#F1F5F9;">AskMNIT AI</div>'
            '<div style="font-size:0.62rem;color:#10B981;font-weight:600;">'
            'Guardian Mode  Focused on ' + wd["name"] + '</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )

        GUARDIAN_PILLS = [
            "Check Ward's Attendance",
            "Pay Semester Fees",
            "Hostel Leave Rules",
            "Contact Warden",
            "Academic Calendar",
        ]

        if not st.session_state.chat_messages:
            st.markdown(
                '<div style="text-align:center;padding:32px 16px 24px;opacity:0.55;">'
                '<div style="font-size:2.2rem;margin-bottom:12px;">&#128106;</div>'
                '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;'
                'font-weight:700;font-size:0.9rem;color:#F1F5F9;margin-bottom:6px;">'
                'Ask me about ' + ward_first + "'s academics</div>"
                '<div style="font-size:0.76rem;color:rgba(241,245,249,0.50);'
                'max-width:300px;margin:0 auto;line-height:1.65;">'
                'Attendance, fees, hostel, exams. I have it all.</div>'
                '</div>',
                unsafe_allow_html=True,
            )

            st.markdown('<div class="pill-zone">', unsafe_allow_html=True)
            pcols = st.columns(len(GUARDIAN_PILLS))
            for i, label in enumerate(GUARDIAN_PILLS):
                with pcols[i]:
                    if st.button(label, key="gpill_" + str(i), use_container_width=True):
                        st.session_state.chat_messages.append({"role": "user", "content": label})
                        st.session_state.pending_ai = True
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        else:
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # AI response handler
        if st.session_state.pending_ai and st.session_state.chat_messages:
            last = st.session_state.chat_messages[-1]["content"]
            with st.chat_message("assistant"):
                if client is None:
                    lower = last.lower()
                    if "attendance" in lower:
                        resp = (
                            wd["name"] + " overall attendance is "
                            + str(att_overall) + "%. Last 7 days: "
                            + wd["att_7d"] + ". "
                            + ("Below 75 percent — contact HOD." if att_overall < 75 else "Above minimum requirement.")
                        )
                    elif "fee" in lower or "pay" in lower:
                        resp = (
                            "Pending for " + wd["fee_semester"] + ": "
                            + wd["fee_pending"] + ", due "
                            + wd["fee_due_date"] + ". Click Pay Now above."
                        )
                    elif "hostel" in lower or "leave" in lower or "warden" in lower:
                        resp = (
                            wd["name"] + " is in " + wd["hostel_block"] + ". "
                            "Warden: " + wd["warden"] + "  " + wd["warden_phone"] + ". "
                            "Hostel leave needs ERP submission 48 hours in advance."
                        )
                    elif "contact" in lower or "hod" in lower:
                        resp = (
                            "Warden: " + wd["warden"] + " at " + wd["warden_phone"] + ". "
                            "For HOD visit MNIT Academic Section Block A."
                        )
                    elif "exam" in lower or "schedule" in lower:
                        resp = "Next exam: " + wd["next_exam"] + ". Full schedule on ERP portal."
                    else:
                        resp = (
                            "I am AskMNIT your guardian assistant for " + wd["name"] + ". "
                            "You asked: " + last + ". "
                            "Add GROQ_API_KEY to .streamlit/secrets.toml for full AI responses."
                        )
                    st.markdown(resp)
                    response_text = resp
                else:
                    # [BACKEND] Live Groq streaming with guardian-specific system prompt
                    system_prompt = (
                        "You are AskMNIT a helpful AI assistant for MNIT Jaipur "
                        "serving a Guardian or Parent. "
                        "Ward: " + wd["name"] + ", " + wd["course"]
                        + ", " + wd["semester"] + ", Roll: " + wd["roll"] + ". "
                        "Attendance: " + str(att_overall) + "%. "
                        "Fee pending: " + wd["fee_pending"]
                        + " due " + wd["fee_due_date"] + ". "
                        "Hostel: " + wd["hostel_block"] + ". "
                        "Warden: " + wd["warden"]
                        + " " + wd["warden_phone"] + ". "
                        "Next exam: " + wd["next_exam"] + ". "
                        "Answer only about this student. Be concise warm and factual."
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
                        response_text = "Error: " + str(e)
                        st.error(response_text)

                st.session_state.chat_messages.append(
                    {"role": "assistant", "content": response_text}
                )
            st.session_state.pending_ai = False
            st.rerun()

        if prompt := st.chat_input(
            "Ask about " + ward_first + " attendance fees hostel",
            key="guardian_chat",
        ):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            st.session_state.pending_ai = True
            st.rerun()

        st.markdown("""
        <p style="text-align:center;font-size:0.61rem;color:rgba(100,116,139,0.40);
                  margin-top:8px;line-height:1.5;">
            AskMNIT can make mistakes. Verify critical info with official college admin.</p>
        """, unsafe_allow_html=True)

    st.stop()


# =============================================================================
# SCREEN 4b — GENERIC DASHBOARD  (student / fresher)
# =============================================================================
role  = st.session_state.user_role
phone = st.session_state.user_phone

ROLE_META = {
    "student": {"icon": "School", "label": "Current Student",    "color": "#10B981", "border": "rgba(16,185,129,0.22)"},
    "fresher": {"icon": "Cap",    "label": "Prospective Student", "color": "#60A5FA", "border": "rgba(59,130,246,0.22)"},
}
rmeta = ROLE_META.get(role, ROLE_META["fresher"])

# Top bar
tb_l, tb_r = st.columns([6, 1])
with tb_l:
    badge_bg = rmeta["border"].replace("0.22", "0.10")
    role_badge_html = (
        '<div style="margin-left:10px;padding:3px 10px;border-radius:99px;'
        'background:' + badge_bg + ';'
        'border:1px solid ' + rmeta["border"] + ';'
        'font-size:0.65rem;font-weight:700;color:' + rmeta["color"] + ';">'
        + rmeta["label"] + '</div>'
    )
    st.markdown(
        '<div style="display:flex;align-items:center;gap:12px;padding-bottom:4px;">'
        '<div style="width:36px;height:36px;'
        'background:linear-gradient(135deg,#3B82F6,#6D28D9);'
        'border-radius:9px;display:flex;align-items:center;'
        'justify-content:center;font-size:0.95rem;">&#127891;</div>'
        '<span style="font-family:\'Plus Jakarta Sans\',sans-serif;'
        'font-weight:800;font-size:0.95rem;color:#F1F5F9;">AskMNIT</span>'
        '<span style="margin-left:8px;font-size:0.58rem;'
        'color:#10B981;font-weight:700;">&#9679; Online</span>'
        + role_badge_html + '</div>',
        unsafe_allow_html=True,
    )
with tb_r:
    st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
    if st.button("Sign Out", use_container_width=True, key="generic_logout"):
        logout()
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# Suggestion pills
PILLS = {
    "student": [
        "Today's Timetable", "View Detailed Attendance",
        "Download PYQs", "Result Dashboard", "ERP Login",
    ],
    "fresher": [
        "Admission Process 2026", "Last Year Cut-offs",
        "Placement Statistics", "Campus Tour and Facilities", "Fee Structure",
    ],
}
current_pills = PILLS.get(role, PILLS["fresher"])

st.markdown(
    '<p style="color:rgba(241,245,249,0.25);font-size:0.60rem;letter-spacing:1.5px;'
    'text-transform:uppercase;margin-bottom:8px;font-weight:700;">Try asking</p>',
    unsafe_allow_html=True,
)

st.markdown('<div class="pill-zone">', unsafe_allow_html=True)
pcols = st.columns(len(current_pills))
for i, label in enumerate(current_pills):
    with pcols[i]:
        if st.button(label, key="pill_" + str(i), use_container_width=True):
            if label == "View Detailed Attendance" and role == "student":
                st.session_state.show_attendance = not st.session_state.show_attendance
                st.rerun()
            else:
                st.session_state.chat_messages.append({"role": "user", "content": label})
                st.session_state.pending_ai = True
                st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# Attendance panel (student only)
if st.session_state.show_attendance and role == "student":
    sdata      = get_student(phone)
    attendance = sdata["attendance"]
    overall    = round(sum(attendance.values()) / len(attendance))

    st.markdown(
        '<div style="background:linear-gradient(160deg,#0D1221,#080C18);'
        'border:1px solid rgba(100,120,200,0.20);border-radius:16px;'
        'padding:20px 24px 14px;margin-bottom:16px;">'
        '<div style="font-weight:800;font-size:1rem;color:#F1F5F9;margin-bottom:4px;">'
        'Subject-wise Attendance</div>'
        '<div style="font-size:0.67rem;color:rgba(148,163,184,0.50);margin-bottom:16px;">'
        'Min required 75 percent  Data synced from ERP</div>',
        unsafe_allow_html=True,
    )
    for subj, pct in attendance.items():
        sc  = att_color(pct)
        stc = att_text_color(pct)
        sbg = att_bg_color(pct)
        sb  = att_badge(pct)
        cn, cp = st.columns([4, 1])
        with cn:
            st.markdown(
                '<div style="font-size:0.82rem;font-weight:600;color:' + stc + ';'
                'margin-bottom:4px;">' + subj +
                '  <span style="font-size:0.60rem;background:' + sbg + ';'
                'color:' + sc + ';padding:1px 7px;border-radius:4px;">'
                + sb + '</span></div>',
                unsafe_allow_html=True,
            )
            st.progress(pct / 100)
        with cp:
            st.markdown(
                '<div style="text-align:right;font-weight:800;font-size:1rem;'
                'color:' + sc + ';padding-top:2px;">' + str(pct) + '%</div>',
                unsafe_allow_html=True,
            )
        st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    oa1, oa2, oa3 = st.columns(3)
    with oa1:
        st.metric("Overall Attendance", str(overall) + "%",
                  "+2% from last month" if overall >= 75 else "Below 75% Warning")
    with oa2:
        low = sum(1 for p in attendance.values() if p < 75)
        st.metric("Subjects Below 75%", str(low),
                  "All clear" if not low else "Need attention")
    with oa3:
        ne = sdata["next_exam"]
        st.metric("Next Exam", ne.split("-")[0].strip(),
                  ne.split("-")[-1].strip() if "-" in ne else "")

    if st.button("Close Attendance Panel", key="close_att"):
        st.session_state.show_attendance = False
        st.rerun()
    st.divider()

# Quick metrics
if role == "student":
    sd = get_student(phone)
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("CGPA", str(sd["cgpa"]) + " / 10", "+0.2 this sem")
    with m2:
        st.metric("Fee Due", sd["fee_due"], "5 days left")
    with m3:
        ne = sd["next_exam"]
        st.metric("Next Exam", ne.split("-")[0].strip(),
                  ne.split("-")[-1].strip() if "-" in ne else "")
elif role == "fresher":
    fd = FRESHER_DATA
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("Avg Package 2025",  fd["placement_avg"],     "+8% YoY")
    with m2: st.metric("Highest Package",   fd["placement_highest"],  "Amazon")
    with m3: st.metric("Placement Rate",    fd["placement_rate"],     "Batch 2025")

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# Chat area
if not st.session_state.chat_messages:
    empty_desc = (
        "Ask me about PYQs timetable results ERP and more."
        if role == "student"
        else "Ask me about MNIT admissions cut-offs placements fees and campus life."
    )
    st.markdown(
        '<div style="text-align:center;padding:40px 20px;opacity:0.55;">'
        '<div style="font-size:2.4rem;margin-bottom:12px;">&#127891;</div>'
        '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;font-weight:700;'
        'font-size:0.95rem;color:#F1F5F9;margin-bottom:6px;">I am AskMNIT</div>'
        '<div style="font-size:0.8rem;color:rgba(241,245,249,0.50);'
        'max-width:360px;margin:0 auto;">' + empty_desc + '</div>'
        '</div>',
        unsafe_allow_html=True,
    )
else:
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Pending AI response
if st.session_state.pending_ai and st.session_state.chat_messages:
    last = st.session_state.chat_messages[-1]["content"]
    with st.chat_message("assistant"):
        if client is None:
            resp = (
                "I am AskMNIT. You asked: " + last + ". "
                "Add GROQ_API_KEY to .streamlit/secrets.toml for live AI responses."
            )
            st.markdown(resp)
            response_text = resp
        else:
            role_ctx = {
                "student": (
                    "The user is a current MNIT Jaipur B.Tech student. "
                    "Help with PYQs timetable attendance results ERP placements."
                ),
                "fresher": (
                    "The user is a prospective student interested in joining MNIT Jaipur. "
                    "Help with JoSAA admissions cut-offs fee structure placements campus life."
                ),
            }
            sp = (
                "You are AskMNIT a helpful AI assistant for MNIT Jaipur. "
                + role_ctx.get(role, "") + " Be concise warm and accurate."
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
                response_text = "Error: " + str(e)
                st.error(response_text)
        st.session_state.chat_messages.append({"role": "assistant", "content": response_text})
    st.session_state.pending_ai = False
    st.rerun()

# Chat input
placeholders = {
    "student":  "Ask about PYQs timetable attendance ERP",
    "fresher":  "Ask about admissions cut-offs placements fees",
}
if prompt := st.chat_input(placeholders.get(role, "Ask me anything"), key="generic_chat"):
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    st.session_state.pending_ai = True
    st.rerun()

st.markdown("""
<p style="text-align:center;font-size:0.62rem;color:rgba(100,116,139,0.42);
          margin-top:8px;line-height:1.5;">
    AskMNIT can make mistakes. Please verify important information with the official admin.
</p>
""", unsafe_allow_html=True)
