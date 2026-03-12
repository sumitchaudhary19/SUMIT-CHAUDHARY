# ╔══════════════════════════════════════════════════════════════════════╗
# ║              AskMNIT — Streamlit App  (Final, Copy-Paste Ready)      ║
# ║                                                                      ║
# ║  PAGE ROUTING — 100% driven by st.session_state (no page files)      ║
# ║                                                                      ║
# ║  Step 1 │ logged_in = False                  → LOGIN screen          ║
# ║  Step 2 │ logged_in = True, user_role = None → ROLE SELECT screen    ║
# ║  Step 3 │ role="guardian", ward_data = None  → WARD ID ENTRY screen  ║
# ║  Step 4a│ role="guardian", ward_data set     → GUARDIAN DASHBOARD    ║
# ║  Step 4b│ role="student"                     → STUDENT DASHBOARD     ║
# ║  Step 4c│ role="fresher"                     → FRESHER DASHBOARD     ║
# ║                                                                      ║
# ║  Search "[BACKEND]" for every API / DB wiring point.                 ║
# ╚══════════════════════════════════════════════════════════════════════╝

import streamlit as st
from groq import Groq
import datetime

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  ← must be the very first Streamlit call in the file
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AskMNIT",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# GROQ CLIENT
# Add your key to .streamlit/secrets.toml → GROQ_API_KEY = "gsk_..."
# ─────────────────────────────────────────────────────────────────────────────
_groq_key = st.secrets.get("GROQ_API_KEY", None)
client = Groq(api_key=_groq_key) if _groq_key else None


# ══════════════════════════════════════════════════════════════════════════════
# MOCK DATABASE
# ══════════════════════════════════════════════════════════════════════════════
# Guardian ward data — keyed by the STUDENT'S college roll / enrollment number.
# This is the exact dict that fetch_ward_data(ward_college_id) reads from.
#
# [BACKEND] Replace the entire WARD_DB dict with an API call in fetch_ward_data().

WARD_DB = {
    "2022UMT1234": {
        "name":               "Sumit Chaudhary",
        "avatar_initials":    "SC",
        "course":             "B.Tech Metallurgical Engineering",
        "semester":           "Semester 6",
        "roll":               "2022UMT1234",
        "campus_status":      "On Campus",
        "hostel_block":       "H-7, Room 214",
        "warden":             "Dr. Pradeep Mehta",
        "warden_phone":       "+91-141-2529041",
        "cgpa":               8.4,
        "overall_attendance": 80,
        "attendance_7d":      "Regular",
        "attendance_subjects": {
            "Economics":                            85,
            "Mineral Processing":                   78,
            "Foundry & Casting":                    92,
            "Welding":                              65,   # ⚠ critical
            "Mobility Systems":                     88,
            "Engg. Materials & Metallurgy":         74,   # ⚠ low
        },
        "fee_pending":        "₹18,500",
        "fee_due_date":       "17 Mar 2026",
        "fee_semester":       "Semester 6",
        "fee_breakdown": [
            ("Tuition Fee",  "₹10,000"),
            ("Hostel Fee",   "₹5,500"),
            ("Library Fee",  "₹500"),
            ("Sports Fee",   "₹1,000"),
            ("Exam Fee",     "₹1,500"),
        ],
        "next_exam":          "Mineral Processing — 20 Mar 2026",
        "notices": [
            "Mid-Semester exams: Mar 20–27",
            "Parent-Teacher Meet: Mar 15 (10 AM – 1 PM)",
            "Hostel gate time extended to 11 PM till exams",
        ],
    },
    "2026CS101": {
        "name":               "Rajesh Sharma",
        "avatar_initials":    "RS",
        "course":             "B.Tech Computer Science & Engineering",
        "semester":           "Semester 4",
        "roll":               "2026CS101",
        "campus_status":      "On Campus",
        "hostel_block":       "H-3, Room 112",
        "warden":             "Dr. Sunita Agarwal",
        "warden_phone":       "+91-141-2529055",
        "cgpa":               9.1,
        "overall_attendance": 85,
        "attendance_7d":      "Regular",
        "attendance_subjects": {
            "Data Structures":       88,
            "Operating Systems":     82,
            "Computer Networks":     90,
            "DBMS":                  79,
            "Software Engineering":  72,
        },
        "fee_pending":        "₹15,000",
        "fee_due_date":       "Oct 15, 2026",
        "fee_semester":       "Semester 4",
        "fee_breakdown": [
            ("Tuition Fee",  "₹10,000"),
            ("Hostel Fee",   "₹3,500"),
            ("Library Fee",  "₹500"),
            ("Sports Fee",   "₹1,000"),
        ],
        "next_exam":          "Data Structures — Apr 5, 2026",
        "notices": [
            "Semester 4 results expected May 10",
            "Lab submissions: Mar 25 (hard deadline)",
            "Alumni Mentorship Program: Register by Mar 20",
        ],
    },
    "2025MT089": {
        "name":               "Priya Verma",
        "avatar_initials":    "PV",
        "course":             "B.Tech Metallurgical Engineering",
        "semester":           "Semester 6",
        "roll":               "2025MT089",
        "campus_status":      "On Campus",
        "hostel_block":       "Girls Hostel G-1, Room 204",
        "warden":             "Dr. Meera Joshi",
        "warden_phone":       "+91-141-2529062",
        "cgpa":               7.9,
        "overall_attendance": 68,   # ⚠ below 75
        "attendance_7d":      "2 absences",
        "attendance_subjects": {
            "Mineral Processing":     70,
            "Phase Transformations":  75,
            "Thermodynamics II":      82,
            "Fluid Mechanics":        60,   # ⚠ critical
            "Engineering Economics":  79,
        },
        "fee_pending":        "₹8,500",
        "fee_due_date":       "Apr 20, 2026",
        "fee_semester":       "Semester 6",
        "fee_breakdown": [
            ("Mess Fee",     "₹4,000"),
            ("Library Fee",  "₹500"),
            ("Tuition Fee",  "₹4,000"),
        ],
        "next_exam":          "Mineral Processing — Mar 28, 2026",
        "notices": [
            "Semester 6 results expected May 5",
            "Lab submissions: Apr 18 (hard deadline)",
        ],
    },
}

# Student self-data (for "student" role, keyed by phone)
STUDENT_DB = {
    "9876543210": {
        "name":    "Sumit Chaudhary",
        "roll":    "2022UMT1234",
        "branch":  "B.Tech Metallurgy · Sem 6",
        "cgpa":    8.4,
        "fee_due": "₹18,500 by 17 Mar 2026",
        "next_exam": "Mineral Processing — 20 Mar 2026",
        "attendance": {
            "Economics":                            85,
            "Mineral Processing":                   78,
            "Foundry & Casting":                    92,
            "Welding":                              65,
            "Mobility Systems":                     88,
            "Engg. Materials & Metallurgy":         74,
        },
    },
}

# Fresher general data (same for all prospective students)
FRESHER_DATA = {
    "admission_deadline":  "15 June 2026 (JoSAA Round 1)",
    "last_cutoff_general": "CRL Rank ≤ 14,800 (Metallurgy, 2025)",
    "placement_avg":       "₹12.4 LPA",
    "placement_highest":   "₹48 LPA (Amazon)",
    "placement_rate":      "94%",
    "fee_per_sem":         "₹45,000 (approx)",
    "campus_highlights": [
        "350+ acre campus in Jaipur",
        "25+ state-of-the-art labs",
        "NBA & NAAC A+ accredited",
        "Active placement cell — 200+ companies",
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# DATA HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def fetch_ward_data(ward_college_id: str) -> dict | None:
    """
    Core data-fetch for Guardian role.
    Receives wardCollegeId → returns ward dict or None.

    [BACKEND] Replace with a real DB / ERP call:
        import requests
        res = requests.get(
            f"https://erp.mnit.ac.in/api/student/{ward_college_id}",
            headers={"Authorization": f"Bearer {st.secrets['ERP_TOKEN']}"},
            timeout=8,
        )
        return res.json() if res.status_code == 200 else None
    """
    return WARD_DB.get(ward_college_id.strip().upper(), None)


def fetch_student_data(phone: str) -> dict:
    """Returns current-student record by phone; falls back to demo record."""
    return STUDENT_DB.get(phone, list(STUDENT_DB.values())[0])


def att_color(pct: int) -> str:
    """Return hex color string for attendance percentage."""
    if pct < 65:  return "#EF4444"
    if pct < 75:  return "#F59E0B"
    return              "#10B981"


def att_badge(pct: int) -> str:
    if pct < 65:  return "🔴 Critical"
    if pct < 75:  return "🟡 Low"
    return              "🟢 Safe"


def tag_html(label: str, color: str, bg: str) -> str:
    """Render an inline status tag as HTML string."""
    return (
        f'<span style="display:inline-flex;align-items:center;gap:5px;'
        f'padding:3px 10px;border-radius:999px;background:{bg};'
        f'font-size:0.67rem;font-weight:700;color:{color};">'
        f'<span style="width:6px;height:6px;border-radius:50%;'
        f'background:{color};flex-shrink:0;"></span>{label}</span>'
    )


def logout():
    """Reset all session state keys to defaults and go back to login."""
    for k, v in _DEFAULTS.items():
        st.session_state[k] = v
    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE — initialise all keys exactly once on first load
# ══════════════════════════════════════════════════════════════════════════════
# st.session_state survives button clicks and reruns within the same session.
# Keys below are set only when missing — clicks/reruns never reset them.
_DEFAULTS: dict = {
    # ── Auth / routing ────────────────────────────────────────────────────
    "logged_in":          False,   # True after OTP verification
    "user_phone":         "",      # phone number used to sign in
    "user_role":          None,    # "student" | "guardian" | "fresher"
    "user_name":          "",      # display name resolved after login
    "otp_sent":           False,   # True while OTP is awaited
    # ── Guardian-specific ─────────────────────────────────────────────────
    "ward_id":            "",      # wardCollegeId entered by guardian
    "ward_data":          None,    # dict returned by fetch_ward_data()
    "ward_id_error":      "",      # validation / not-found message
    "show_attend_detail": False,   # toggle subject-wise attendance panel
    # ── Chat ──────────────────────────────────────────────────────────────
    "chat_messages":      [],      # [{"role": ..., "content": ...}]
    "pending_ai":         False,   # True while Groq is generating
    # ── Student view ──────────────────────────────────────────────────────
    "show_attendance":    False,   # subject panel for student role
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS  — dark premium theme, no sidebar, no default Streamlit chrome
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
    padding-top: 22px !important;
    padding-bottom: 48px !important;
    max-width: 100% !important;
}

/* ── Hide ALL default Streamlit chrome ── */
header[data-testid="stHeader"],
footer, #MainMenu,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
section[data-testid="stSidebar"] { display: none !important; }

/* ── Text inputs ── */
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 10px !important;
    color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.88rem !important;
    padding: 10px 14px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: rgba(139,92,246,0.50) !important;
}
[data-testid="stTextInput"] label {
    color: rgba(241,245,249,0.58) !important;
    font-size: 0.74rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* ── Buttons — default gradient ── */
.stButton > button {
    background: linear-gradient(135deg,#3B82F6,#6D28D9) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.84rem !important;
    box-shadow: 0 4px 16px rgba(59,130,246,0.24) !important;
    transition: all 0.18s !important;
    padding: 10px 18px !important;
}
.stButton > button:hover {
    opacity: 0.90 !important;
    transform: translateY(-1px) !important;
}

/* ── Ghost button ── */
.ghost-btn .stButton > button {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    color: rgba(241,245,249,0.60) !important;
    box-shadow: none !important;
}
.ghost-btn .stButton > button:hover {
    background: rgba(59,130,246,0.10) !important;
    color: #F1F5F9 !important;
    border-color: rgba(59,130,246,0.30) !important;
}

/* ── Pay Now — amber override ── */
.pay-btn .stButton > button {
    background: linear-gradient(135deg,#D97706,#F59E0B) !important;
    box-shadow: 0 4px 18px rgba(245,158,11,0.30) !important;
}

/* ── Pill buttons ── */
.pill-zone .stButton > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 999px !important;
    color: rgba(241,245,249,0.58) !important;
    font-size: 0.73rem !important;
    font-weight: 500 !important;
    box-shadow: none !important;
    padding: 7px 12px !important;
}
.pill-zone .stButton > button:hover {
    background: rgba(139,92,246,0.14) !important;
    border-color: rgba(139,92,246,0.32) !important;
    color: #CBD5E1 !important;
    transform: translateY(-1px) !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
    padding: 16px !important;
}
[data-testid="stMetricLabel"] {
    color: rgba(241,245,249,0.38) !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stMetricValue"] {
    color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.5rem !important;
}
[data-testid="stMetricDelta"] {
    font-size: 0.68rem !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* ── Progress bars ── */
[data-testid="stProgress"] > div > div { border-radius: 99px !important; }

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    margin-bottom: 4px !important;
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
    font-size: 0.875rem !important;
}
[data-testid="stChatInputSubmitButton"] {
    background: linear-gradient(135deg,#3B82F6,#6D28D9) !important;
    border-radius: 9px !important;
    border: none !important;
}

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.07) !important; }

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.82rem !important;
}

/* ── General text ── */
p, li, span {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
h1, h2, h3 {
    color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 800 !important;
    letter-spacing: -0.5px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar       { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.22); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ████████████████████████████████████████
#  SCREEN 1 — LOGIN
# ████████████████████████████████████████
# Condition: logged_in = False
# After: sets logged_in=True, user_phone, user_name → st.rerun() → Screen 2
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:

    _, col, _ = st.columns([1, 1.5, 1])
    with col:

        # ── Brand mark ──
        st.markdown("""
        <div style="text-align:center;padding:44px 0 28px;">
            <div style="width:58px;height:58px;margin:0 auto 14px;
                        background:linear-gradient(135deg,#3B82F6,#6D28D9);
                        border-radius:15px;display:flex;align-items:center;
                        justify-content:center;font-size:1.7rem;
                        box-shadow:0 8px 28px rgba(59,130,246,0.30);">🎓</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;
                        font-size:1.5rem;font-weight:800;color:#F1F5F9;
                        letter-spacing:-0.6px;">AskMNIT</div>
            <div style="font-size:0.72rem;color:rgba(100,116,139,0.65);margin-top:4px;">
                Your campus AI — powered by LLaMA 3.3 70B
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Card ──
        st.markdown("""
        <div style="background:linear-gradient(160deg,#0C1120,#080D19);
                    border:1px solid rgba(100,120,220,0.16);border-radius:20px;
                    padding:28px 28px 24px;
                    box-shadow:0 24px 80px rgba(0,0,0,0.68);">
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="font-family:'Plus Jakarta Sans',sans-serif;
                    font-size:1.05rem;font-weight:800;color:#F1F5F9;margin-bottom:4px;">
            Sign in to continue
        </div>
        <div style="font-size:0.72rem;color:rgba(148,163,184,0.50);margin-bottom:20px;">
            Enter your registered mobile number.
        </div>
        """, unsafe_allow_html=True)

        phone_val = st.text_input(
            "📱 Mobile Number",
            placeholder="10-digit mobile number",
            max_chars=10,
            key="login_phone_input",
        )

        if not st.session_state.otp_sent:
            if st.button("📨  Send OTP", use_container_width=True, key="btn_send_otp"):
                if len(phone_val) == 10 and phone_val.isdigit():
                    # ── [BACKEND] Send real OTP ──────────────────────────
                    # import requests
                    # requests.post(
                    #     "https://api.your-auth-provider.com/send-otp",
                    #     json={"phone": "+91" + phone_val},
                    #     headers={"x-api-key": st.secrets["OTP_API_KEY"]},
                    # )
                    # ─────────────────────────────────────────────────────
                    st.session_state.otp_sent = True
                    st.rerun()
                else:
                    st.error("Please enter a valid 10-digit mobile number.")

        if st.session_state.otp_sent:
            st.markdown(f"""
            <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.22);
                        border-radius:8px;padding:9px 12px;margin-bottom:12px;
                        font-size:0.72rem;color:#34D399;font-weight:600;">
                ✓ OTP sent to +91 {phone_val}
            </div>
            """, unsafe_allow_html=True)

            otp_val = st.text_input(
                "🔐 Enter OTP",
                placeholder="Enter the 4–6 digit OTP",
                max_chars=6,
                type="password",
                key="login_otp_input",
            )

            c1, c2 = st.columns([2, 1])
            with c1:
                if st.button("✅  Verify & Continue", use_container_width=True, key="btn_verify_otp"):
                    if len(otp_val) >= 4:
                        # ── [BACKEND] Verify OTP ─────────────────────────
                        # result = requests.post(
                        #     "https://api.your-auth-provider.com/verify-otp",
                        #     json={"phone": "+91" + phone_val, "otp": otp_val},
                        # )
                        # if result.status_code != 200:
                        #     st.error("Invalid OTP. Please try again.")
                        #     st.stop()
                        # ─────────────────────────────────────────────────
                        st.session_state.logged_in  = True
                        st.session_state.user_phone = phone_val
                        st.session_state.otp_sent   = False
                        # Resolve display name if phone maps to a student
                        if phone_val in STUDENT_DB:
                            st.session_state.user_name = STUDENT_DB[phone_val]["name"]
                        st.rerun()   # → SCREEN 2
                    else:
                        st.error("Enter a valid OTP (minimum 4 digits).")
            with c2:
                st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
                if st.button("← Change", use_container_width=True, key="btn_change_no"):
                    st.session_state.otp_sent = False
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)  # close card

        st.markdown("""
        <p style="text-align:center;font-size:0.60rem;color:rgba(100,116,139,0.40);
                  margin-top:14px;line-height:1.6;">
            By continuing you agree to MNIT's Terms of Service & Privacy Policy.
        </p>
        """, unsafe_allow_html=True)

    st.stop()   # ← nothing below renders until logged_in = True


# ══════════════════════════════════════════════════════════════════════════════
# ████████████████████████████████████████
#  SCREEN 2 — ROLE SELECTION
# ████████████████████████████████████████
# Condition: logged_in=True, user_role=None
# After: sets user_role → st.rerun()
#   • guardian → Screen 3 (ward ID entry)
#   • student / fresher → Screen 4b / 4c (generic dashboard)
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.user_role is None:

    _, col, _ = st.columns([1, 1.9, 1])
    with col:

        st.markdown(f"""
        <div style="text-align:center;padding:44px 0 30px;">
            <div style="font-family:'Plus Jakarta Sans',sans-serif;
                        font-size:1.4rem;font-weight:800;color:#F1F5F9;
                        letter-spacing:-0.5px;margin-bottom:6px;">
                Tell us who you are
            </div>
            <div style="font-size:0.76rem;color:rgba(148,163,184,0.48);">
                We'll personalise AskMNIT based on your role.
            </div>
        </div>
        """, unsafe_allow_html=True)

        _ROLE_LIST = [
            ("fresher",  "🎓", "Prospective Student",  "Fresher",
             "Looking to apply for admission.",
             "linear-gradient(135deg,#1D4ED8,#3B82F6)", "rgba(59,130,246,0.28)"),
            ("guardian", "👨‍👧", "Guardian / Parent",    "",
             "Here for my ward or child.",
             "linear-gradient(135deg,#7C3AED,#A78BFA)", "rgba(139,92,246,0.28)"),
            ("student",  "🏫", "Current Student",       "",
             "Already enrolled in the college.",
             "linear-gradient(135deg,#065F46,#10B981)", "rgba(16,185,129,0.28)"),
        ]

        for rid, icon, title, badge, desc, grad, glow in _ROLE_LIST:
            badge_html = (
                f'<span style="font-size:0.56rem;padding:2px 7px;'
                f'background:rgba(255,255,255,0.14);border-radius:4px;'
                f'font-weight:700;letter-spacing:0.5px;text-transform:uppercase;'
                f'margin-left:8px;">{badge}</span>'
            ) if badge else ""

            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.025);
                        border:1px solid rgba(255,255,255,0.08);
                        border-radius:14px;padding:16px 18px 8px;margin-bottom:4px;">
                <div style="display:flex;align-items:center;gap:14px;margin-bottom:4px;">
                    <div style="width:46px;height:46px;border-radius:12px;flex-shrink:0;
                                background:{grad};display:flex;align-items:center;
                                justify-content:center;font-size:1.3rem;
                                box-shadow:0 4px 14px {glow};">{icon}</div>
                    <div>
                        <div style="font-family:'Plus Jakarta Sans',sans-serif;
                                    font-weight:700;font-size:0.90rem;color:#F1F5F9;">
                            {title}{badge_html}
                        </div>
                        <div style="font-size:0.72rem;color:rgba(148,163,184,0.52);margin-top:2px;">
                            {desc}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Select — {title}", key=f"role_btn_{rid}", use_container_width=True):
                # ── [BACKEND] Persist role to user profile ───────────────
                # import requests
                # requests.patch(
                #     f"{API_BASE}/user/role",
                #     json={"phone": st.session_state.user_phone, "role": rid},
                #     headers={"Authorization": f"Bearer {st.secrets['API_TOKEN']}"},
                # )
                # ─────────────────────────────────────────────────────────
                st.session_state.user_role     = rid
                st.session_state.chat_messages = []
                st.session_state.ward_id       = ""
                st.session_state.ward_data     = None
                st.session_state.ward_id_error = ""
                st.rerun()

            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    st.stop()   # ← nothing below until role is chosen


# ══════════════════════════════════════════════════════════════════════════════
# ████████████████████████████████████████████████████████████████████████████
#  SCREEN 3 — GUARDIAN: WARD ID ENTRY
# ████████████████████████████████████████████████████████████████████████████
#
# Condition : user_role = "guardian" AND ward_data = None
#
# KEY LOGIC:
#   1. Render mandatory text input for wardCollegeId
#   2. On submit → call fetch_ward_data(wardCollegeId)
#   3. If found  → save to st.session_state.ward_data & st.session_state.ward_id
#      st.rerun() → Screen 4a (Guardian Dashboard)
#   4. If not found → show error, stay on this screen
#
# The guardian CANNOT proceed without a valid ward ID.
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.user_role == "guardian" and st.session_state.ward_data is None:

    _, col, _ = st.columns([1, 1.6, 1])
    with col:

        # ── Header ──
        st.markdown("""
        <div style="text-align:center;padding:44px 0 28px;">
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
            <div style="font-size:0.74rem;color:rgba(148,163,184,0.50);
                        line-height:1.65;max-width:320px;margin:0 auto;">
                Enter your child's enrollment or roll number to link their
                academic data to your account.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Card ──
        st.markdown("""
        <div style="background:linear-gradient(160deg,#0C1120,#080D19);
                    border:1px solid rgba(139,92,246,0.22);border-radius:20px;
                    padding:28px 28px 24px;
                    box-shadow:0 24px 80px rgba(0,0,0,0.68);">
        """, unsafe_allow_html=True)

        # ── Required input field ──
        ward_input = st.text_input(
            "🎓 Ward's College ID / Enrollment Number *",
            placeholder="e.g.  2022UMT1234   or   2026CS101",
            key="ward_id_field",
            help="Roll No. or Enrollment No. printed on your ward's college identity card.",
        )

        # ── Validation / not-found error ──
        if st.session_state.ward_id_error:
            st.markdown(f"""
            <div style="background:rgba(239,68,68,0.08);
                        border:1px solid rgba(239,68,68,0.22);
                        border-radius:8px;padding:10px 14px;margin:8px 0 4px;
                        font-size:0.74rem;color:#FCA5A5;
                        display:flex;gap:8px;align-items:flex-start;line-height:1.5;">
                <span style="flex-shrink:0;margin-top:1px;">⚠</span>
                <span>{st.session_state.ward_id_error}</span>
            </div>
            """, unsafe_allow_html=True)

        # ── Submit button ── (guardian cannot proceed without filling this)
        if st.button("🔍  Link Ward's Account", use_container_width=True, key="btn_link_ward"):
            raw_id = ward_input.strip()

            # Guard 1: empty field
            if not raw_id:
                st.session_state.ward_id_error = (
                    "This field is required. "
                    "Please enter your ward's College ID or Roll Number."
                )
                st.rerun()

            else:
                # ── [BACKEND] CORE DATA FETCH using wardCollegeId ─────────────
                # This fetch is triggered IMMEDIATELY after the guardian submits.
                # Replace fetch_ward_data() with your real API call, e.g.:
                #
                #   import requests
                #   res = requests.get(
                #       f"https://erp.mnit.ac.in/api/student/{raw_id.upper()}",
                #       headers={"Authorization": f"Bearer {st.secrets['ERP_TOKEN']}"},
                #       timeout=8,
                #   )
                #   fetched = res.json() if res.status_code == 200 else None
                #
                # The fetched dict is stored in st.session_state.ward_data.
                # From this point on, the ENTIRE dashboard reads ONLY from
                # st.session_state.ward_data — guaranteeing the guardian sees
                # ONLY their ward's data and nothing else.
                # ─────────────────────────────────────────────────────────────
                fetched = fetch_ward_data(raw_id)

                if fetched is None:
                    # Guard 2: ID not found
                    st.session_state.ward_id_error = (
                        f'No student found for ID "{raw_id.upper()}". '
                        "Please double-check the ID on your ward's identity card. "
                        "Demo IDs you can try: 2022UMT1234 · 2026CS101 · 2025MT089"
                    )
                    st.rerun()

                else:
                    # ── SUCCESS: lock fetched data into session state ──────────
                    # ward_id and ward_data are now the single source of truth.
                    # No further fetches happen during this session — data is
                    # already in st.session_state.ward_data.
                    st.session_state.ward_id       = raw_id.upper()
                    st.session_state.ward_data     = fetched
                    st.session_state.ward_id_error = ""
                    st.session_state.chat_messages = []
                    st.rerun()   # → SCREEN 4a — Guardian Dashboard

        st.markdown("</div>", unsafe_allow_html=True)  # close card

        st.markdown("""
        <p style="text-align:center;font-size:0.63rem;color:rgba(100,116,139,0.42);
                  margin-top:12px;line-height:1.6;">
            Don't know the ID? Check your ward's admit card or contact the Academic Section.
        </p>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("← Change Role", use_container_width=True, key="btn_back_from_ward"):
            st.session_state.user_role     = None
            st.session_state.ward_id_error = ""
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()   # ← nothing below until ward_data is fetched


# ══════════════════════════════════════════════════════════════════════════════
# ████████████████████████████████████████████████████████████████████████████
#  SCREEN 4a — GUARDIAN DASHBOARD
#
#  Data source: EXCLUSIVELY st.session_state.ward_data
#               (fetched using the guardian's wardCollegeId)
#  Layout    : NO sidebar · NO navigation tabs · NO generic headings
#              Two columns: left = data cards │ right = AI chatbot
# ████████████████████████████████████████████████████████████████████████████
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.user_role == "guardian":

    # Convenience alias — all dashboard data comes from this single dict
    wd = st.session_state.ward_data
    att_overall = wd["overall_attendance"]
    att_c       = att_color(att_overall)

    # ── Top bar ────────────────────────────────────────────────────────────
    tb_l, tb_r = st.columns([6, 1])
    with tb_l:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;padding-bottom:4px;">
            <div style="width:36px;height:36px;
                        background:linear-gradient(135deg,#3B82F6,#6D28D9);
                        border-radius:9px;display:flex;align-items:center;
                        justify-content:center;font-size:0.95rem;">🎓</div>
            <div>
                <span style="font-family:'Plus Jakarta Sans',sans-serif;
                             font-weight:800;font-size:1rem;color:#F1F5F9;">AskMNIT</span>
                <span style="margin-left:8px;font-size:0.58rem;color:#10B981;font-weight:700;">
                    ● Online · Guardian Mode
                </span>
            </div>
            <div style="margin-left:6px;padding:3px 11px;
                        background:rgba(139,92,246,0.12);
                        border:1px solid rgba(139,92,246,0.28);
                        border-radius:99px;font-size:0.63rem;font-weight:700;
                        color:#A78BFA;font-family:'Plus Jakarta Sans',sans-serif;">
                👨‍👧 Guardian · {wd['roll']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    with tb_r:
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("🚪 Sign Out", use_container_width=True, key="guardian_logout"):
            logout()
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # ── Two-column layout ────────────────────────────────────────────────
    left_col, right_col = st.columns([1.1, 1], gap="large")

    # ════════════════════════════════════════════
    # LEFT COLUMN — DATA CARDS
    # All data comes from wd (= st.session_state.ward_data)
    # ════════════════════════════════════════════
    with left_col:

        # ─────────────────────────────────────────
        # CARD 1: WARD SUMMARY
        # ─────────────────────────────────────────
        info_grid = "".join([
            f'<div style="background:rgba(255,255,255,0.04);border-radius:10px;padding:10px 12px;">'
            f'<div style="font-size:0.56rem;color:rgba(100,116,139,0.52);font-weight:700;'
            f'text-transform:uppercase;letter-spacing:0.8px;margin-bottom:3px;">{ico} {lbl}</div>'
            f'<div style="font-size:0.74rem;color:#E2E8F0;font-weight:600;line-height:1.4;">{val}</div></div>'
            for ico, lbl, val in [
                ("🏢", "Hostel",   wd["hostel_block"]),
                ("👷", "Warden",   wd["warden"]),
                ("📱", "Contact",  wd["warden_phone"]),
                ("🎓", "Roll No",  wd["roll"]),
            ]
        ])

        st.markdown(f"""
        <div style="background:linear-gradient(160deg,#0D1221,#080C18);
                    border:1px solid rgba(139,92,246,0.20);border-radius:16px;
                    padding:20px 22px 18px;margin-bottom:14px;">

            <div style="display:flex;align-items:flex-start;gap:14px;margin-bottom:16px;">
                <div style="width:54px;height:54px;border-radius:14px;flex-shrink:0;
                            background:linear-gradient(135deg,#7C3AED,#A78BFA);
                            display:flex;align-items:center;justify-content:center;
                            font-size:1.1rem;font-weight:800;color:white;
                            box-shadow:0 4px 16px rgba(139,92,246,0.28);">
                    {wd['avatar_initials']}
                </div>
                <div style="flex:1;min-width:0;">
                    <div style="font-family:'Plus Jakarta Sans',sans-serif;
                                font-weight:800;font-size:1.05rem;color:#F1F5F9;margin-bottom:2px;">
                        {wd['name']}
                    </div>
                    <div style="font-size:0.71rem;color:rgba(148,163,184,0.55);
                                line-height:1.5;margin-bottom:8px;">
                        {wd['course']} · {wd['semester']}
                    </div>
                    {tag_html(wd['campus_status'], '#34D399', 'rgba(16,185,129,0.12)')}
                </div>
            </div>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:9px;
                        border-top:1px solid rgba(255,255,255,0.06);padding-top:14px;">
                {info_grid}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ─────────────────────────────────────────
        # CARD 2: ATTENDANCE
        # ─────────────────────────────────────────
        warn_html = ""
        if att_overall < 75:
            warn_html = (
                '<div style="background:rgba(245,158,11,0.08);'
                'border:1px solid rgba(245,158,11,0.22);border-radius:8px;'
                'padding:8px 12px;margin-bottom:14px;font-size:0.71rem;'
                'color:#FCD34D;line-height:1.5;">'
                '⚠️ Overall attendance is below the 75% threshold. '
                'Exam eligibility may be affected — please contact the HOD.'
                '</div>'
            )

        st.markdown(f"""
        <div style="background:linear-gradient(160deg,#0D1221,#080C18);
                    border:1px solid rgba(255,255,255,0.09);border-radius:16px;
                    padding:20px 22px 18px;margin-bottom:14px;">

            <div style="font-size:0.60rem;color:rgba(100,116,139,0.52);font-weight:700;
                        text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">
                Attendance
            </div>

            <div style="display:flex;align-items:center;
                        justify-content:space-between;margin-bottom:14px;">
                <div>
                    <div style="font-size:2.2rem;font-weight:800;color:{att_c};
                                letter-spacing:-1px;line-height:1;">
                        {att_overall}%
                    </div>
                    <div style="font-size:0.70rem;color:rgba(148,163,184,0.52);margin-top:4px;">
                        Overall · Last 7 days:
                        <span style="color:{att_c};font-weight:700;">{wd['attendance_7d']}</span>
                    </div>
                </div>
                <!-- Circular ring -->
                <div style="width:62px;height:62px;border-radius:50%;flex-shrink:0;
                            background:conic-gradient({att_c} 0% {att_overall}%,
                            rgba(255,255,255,0.07) {att_overall}% 100%);
                            display:flex;align-items:center;justify-content:center;">
                    <div style="width:46px;height:46px;border-radius:50%;
                                background:#0D1221;display:flex;align-items:center;
                                justify-content:center;font-size:0.68rem;
                                font-weight:800;color:{att_c};">
                        {att_overall}%
                    </div>
                </div>
            </div>

            {warn_html}
        </div>
        """, unsafe_allow_html=True)

        # Subject-wise toggle button
        if st.button(
            "📊  View Subject-wise Attendance" if not st.session_state.show_attend_detail
            else "✖  Hide Subject Details",
            key="toggle_attend_detail",
            use_container_width=True,
        ):
            st.session_state.show_attend_detail = not st.session_state.show_attend_detail
            st.rerun()

        # ── Subject-wise attendance panel ─────────────────────────────────
        if st.session_state.show_attend_detail:
            st.markdown("""
            <div style="background:rgba(255,255,255,0.02);
                        border:1px solid rgba(100,120,200,0.16);
                        border-radius:12px;padding:16px 18px 12px;margin-top:10px;
                        margin-bottom:14px;">
                <div style="font-size:0.60rem;color:rgba(100,116,139,0.52);font-weight:700;
                            text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;">
                    Subject-wise · {course}
                </div>
            """.format(course=wd["semester"]), unsafe_allow_html=True)

            for subj, pct in wd["attendance_subjects"].items():
                sc = att_color(pct)
                sb = att_badge(pct)
                col_name, col_pct = st.columns([4, 1])
                with col_name:
                    st.markdown(f"""
                    <div style="font-size:0.79rem;font-weight:600;
                                color:{'#FCA5A5' if pct<65 else '#FCD34D' if pct<75 else '#E2E8F0'};
                                margin-bottom:4px;">
                        {subj}
                        <span style="margin-left:6px;font-size:0.57rem;
                                     background:{'rgba(239,68,68,0.14)' if pct<65 else 'rgba(245,158,11,0.12)' if pct<75 else 'rgba(16,185,129,0.10)'};
                                     color:{sc};padding:1px 6px;border-radius:4px;">{sb}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(pct / 100)
                with col_pct:
                    st.markdown(f"""
                    <div style="text-align:right;font-weight:800;font-size:0.95rem;
                                color:{sc};padding-top:2px;">{pct}%</div>
                    """, unsafe_allow_html=True)
                st.markdown("<div style='height:3px'></div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # ─────────────────────────────────────────
        # CARD 3: FEE & FINANCE
        # ─────────────────────────────────────────
        fee_rows_html = "".join([
            f'<div style="display:flex;justify-content:space-between;'
            f'padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);">'
            f'<span style="font-size:0.77rem;color:rgba(148,163,184,0.52);">{item}</span>'
            f'<span style="font-size:0.77rem;font-weight:700;color:#F1F5F9;">{amt}</span></div>'
            for item, amt in wd["fee_breakdown"]
        ])

        st.markdown(f"""
        <div style="background:linear-gradient(160deg,#0D1221,#080C18);
                    border:1px solid rgba(245,158,11,0.18);border-radius:16px;
                    padding:20px 22px 18px;margin-bottom:14px;">

            <div style="font-size:0.60rem;color:rgba(100,116,139,0.52);font-weight:700;
                        text-transform:uppercase;letter-spacing:1px;margin-bottom:14px;">
                Fee &amp; Finance · {wd['fee_semester']}
            </div>

            <div style="display:flex;align-items:flex-end;
                        justify-content:space-between;margin-bottom:16px;">
                <div>
                    <div style="font-size:0.70rem;color:rgba(148,163,184,0.50);margin-bottom:3px;">
                        Pending Amount
                    </div>
                    <div style="font-size:2rem;font-weight:800;color:#F59E0B;letter-spacing:-1px;">
                        {wd['fee_pending']}
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.58rem;color:rgba(100,116,139,0.48);margin-bottom:2px;">
                        Due Date
                    </div>
                    <div style="font-size:0.88rem;font-weight:700;color:#EF4444;">
                        {wd['fee_due_date']}
                    </div>
                </div>
            </div>

            {fee_rows_html}

            <div style="display:flex;justify-content:space-between;
                        padding:10px 0 0;margin-top:4px;">
                <span style="font-size:0.85rem;font-weight:700;color:#F1F5F9;">Total</span>
                <span style="font-size:0.92rem;font-weight:800;color:#F59E0B;">{wd['fee_pending']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Pay Now — amber button override
        st.markdown('<div class="pay-btn">', unsafe_allow_html=True)
        if st.button("💳  Pay Now →", use_container_width=True, key="guardian_pay"):
            # ── [BACKEND] Redirect to MNIT payment gateway ────────────────
            # st.markdown(f'<meta http-equiv="refresh" content="0; URL={PAY_URL}">', unsafe_allow_html=True)
            # ─────────────────────────────────────────────────────────────
            st.info("🔗 Redirecting to MNIT payment gateway… (wire the real payment URL here)")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # ─────────────────────────────────────────
        # CARD 4: NOTICES
        # ─────────────────────────────────────────
        notices_html = "".join([
            f'<div style="display:flex;gap:10px;padding:9px 12px;'
            f'background:rgba(255,255,255,0.03);border-radius:9px;margin-bottom:6px;">'
            f'<span style="font-size:0.60rem;color:rgba(100,116,139,0.48);'
            f'font-weight:700;margin-top:1px;flex-shrink:0;">0{i+1}</span>'
            f'<span style="font-size:0.76rem;color:rgba(148,163,184,0.62);line-height:1.5;">'
            f'{n}</span></div>'
            for i, n in enumerate(wd["notices"])
        ])

        st.markdown(f"""
        <div style="background:linear-gradient(160deg,#0D1221,#080C18);
                    border:1px solid rgba(255,255,255,0.08);border-radius:16px;
                    padding:18px 20px 14px;margin-bottom:16px;">
            <div style="font-size:0.60rem;color:rgba(100,116,139,0.52);font-weight:700;
                        text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;">
                📌 Notices
            </div>
            {notices_html}
        </div>
        """, unsafe_allow_html=True)

        # ─────────────────────────────────────────
        # QUICK METRICS ROW
        # ─────────────────────────────────────────
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("CGPA", f"{wd['cgpa']} / 10", "Current sem")
        with m2:
            st.metric("Fee Pending", wd["fee_pending"], f"Due {wd['fee_due_date']}")
        with m3:
            st.metric(
                "Attendance", f"{att_overall}%",
                "Above 75% ✓" if att_overall >= 75 else "Below 75% ⚠️",
            )

    # ════════════════════════════════════════════
    # RIGHT COLUMN — AI CHATBOT
    # ════════════════════════════════════════════
    with right_col:

        # Chat header
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;
                    padding-bottom:14px;border-bottom:1px solid rgba(255,255,255,0.07);
                    margin-bottom:14px;">
            <div style="width:36px;height:36px;border-radius:9px;
                        background:linear-gradient(135deg,#3B82F6,#6D28D9);
                        display:flex;align-items:center;justify-content:center;
                        font-size:0.95rem;">🤖</div>
            <div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif;
                            font-weight:800;font-size:0.92rem;color:#F1F5F9;">AskMNIT AI</div>
                <div style="font-size:0.60rem;color:#10B981;font-weight:600;">
                    ● Guardian Mode · Focused on {wd['name']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Guardian suggestion pills ──
        GUARDIAN_PILLS = [
            ("📋", "Check Ward's Attendance"),
            ("💳", "Pay Semester Fees"),
            ("🏢", "Hostel Leave Rules"),
            ("📞", "Contact Warden"),
            ("📅", "Academic Calendar"),
        ]

        if not st.session_state.chat_messages:
            # Empty state
            st.markdown(f"""
            <div style="text-align:center;padding:30px 16px 20px;opacity:0.52;">
                <div style="font-size:2rem;margin-bottom:12px;">👨‍👧</div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;
                            font-size:0.88rem;color:#F1F5F9;margin-bottom:6px;">
                    Ask me about {wd['name'].split()[0]}'s academics
                </div>
                <div style="font-size:0.74rem;color:rgba(241,245,249,0.48);
                            max-width:280px;margin:0 auto;line-height:1.65;">
                    Attendance, fees, hostel, exam schedule — I have it all.
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Suggestion pills — guardian-specific
            st.markdown("""
            <p style='color:rgba(241,245,249,0.25);font-size:0.60rem;letter-spacing:1.2px;
            text-transform:uppercase;margin-bottom:8px;font-weight:700;'>💡 Try asking</p>
            """, unsafe_allow_html=True)

            st.markdown('<div class="pill-zone">', unsafe_allow_html=True)
            pcols = st.columns(len(GUARDIAN_PILLS))
            for i, (emoji, label) in enumerate(GUARDIAN_PILLS):
                with pcols[i]:
                    if st.button(f"{emoji} {label}", key=f"gpill_{i}", use_container_width=True):
                        st.session_state.chat_messages.append({"role": "user", "content": label})
                        st.session_state.pending_ai = True
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        else:
            # Render chat history
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # ── AI response logic ────────────────────────────────────────────
        if st.session_state.pending_ai and st.session_state.chat_messages:
            last_msg = st.session_state.chat_messages[-1]["content"].lower()

            with st.chat_message("assistant"):

                if client is None:
                    # ── [BACKEND] Add GROQ_API_KEY to .streamlit/secrets.toml ──
                    # Smart fallback uses real ward_data for believable answers
                    if "attendance" in last_msg:
                        resp = (
                            f"📊 **{wd['name']}'s Attendance:** Overall **{att_overall}%**. "
                            f"Last 7 days: **{wd['attendance_7d']}**. "
                            + ("⚠️ Below 75% minimum — please contact the HOD." if att_overall < 75
                               else "✅ Above minimum requirement.")
                        )
                    elif "fee" in last_msg or "pay" in last_msg:
                        resp = (
                            f"💳 **Fee Due for {wd['name']}:** {wd['fee_pending']} "
                            f"by **{wd['fee_due_date']}** ({wd['fee_semester']}). "
                            f"Click **Pay Now →** on the Fee card to proceed."
                        )
                    elif "hostel" in last_msg or "leave" in last_msg:
                        resp = (
                            f"🏢 {wd['name']} is in **{wd['hostel_block']}**. "
                            f"Warden: **{wd['warden']}** · {wd['warden_phone']}. "
                            "Hostel leave requires a signed form submitted 48 hrs in advance."
                        )
                    elif "warden" in last_msg or "contact" in last_msg:
                        resp = (
                            f"📞 Warden for {wd['hostel_block']}: "
                            f"**{wd['warden']}** · {wd['warden_phone']}. "
                            "HOD contact is available on the MNIT official website."
                        )
                    elif "calendar" in last_msg or "schedule" in last_msg:
                        resp = (
                            f"📅 Next exam for {wd['name']}: **{wd['next_exam']}**. "
                            "Full academic calendar is available at mnit.ac.in/academic."
                        )
                    else:
                        resp = (
                            f"I'm AskMNIT in Guardian Mode, focused on **{wd['name']}** "
                            f"({wd['roll']}). Add `GROQ_API_KEY` to `.streamlit/secrets.toml` "
                            "to enable live AI responses via LLaMA 3.3 70B."
                        )
                    st.markdown(resp)
                    response_text = resp

                else:
                    # ── [BACKEND] Live Groq call — guardian-specific system prompt ──
                    system_prompt = (
                        f"You are AskMNIT — a helpful AI assistant for MNIT Jaipur. "
                        f"The user is a GUARDIAN of student {wd['name']} (Roll: {wd['roll']}, "
                        f"{wd['course']}, {wd['semester']}). "
                        f"Current attendance: {att_overall}%. Fee pending: {wd['fee_pending']} "
                        f"by {wd['fee_due_date']}. "
                        "Only answer questions relevant to this specific student. "
                        "Be concise, accurate, and empathetic to parents' concerns."
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

        # Chat input box
        if prompt := st.chat_input(
            f"Ask about {wd['name'].split()[0]}'s attendance, fees, hostel…",
            key="guardian_chat_input",
        ):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            st.session_state.pending_ai = True
            st.rerun()

        st.markdown("""
        <p style="text-align:center;font-size:0.60rem;color:rgba(100,116,139,0.38);
                  margin-top:8px;line-height:1.5;">
            AskMNIT can make mistakes. Verify critical info with official college admin.
        </p>
        """, unsafe_allow_html=True)

    st.stop()   # guardian dashboard rendered — nothing below should run


# ══════════════════════════════════════════════════════════════════════════════
# ████████████████████████████████████████████████████████████████████████████
#  SCREEN 4b / 4c — STUDENT & FRESHER DASHBOARDS
#  (role = "student" or "fresher")
# ████████████████████████████████████████████████████████████████████████████
# ══════════════════════════════════════════════════════════════════════════════

role  = st.session_state.user_role
phone = st.session_state.user_phone

ROLE_META = {
    "student":  {"icon": "🏫", "label": "Current Student",    "color": "#10B981", "border": "rgba(16,185,129,0.25)"},
    "fresher":  {"icon": "🎓", "label": "Prospective Student", "color": "#60A5FA", "border": "rgba(59,130,246,0.25)"},
}
rmeta = ROLE_META.get(role, ROLE_META["student"])

PILLS = {
    "student": [
        ("🕐", "Today's Timetable"),
        ("📊", "View Detailed Attendance"),
        ("📝", "Download PYQs"),
        ("🏆", "Result Dashboard"),
        ("🔗", "ERP Login"),
    ],
    "fresher": [
        ("🎓", "Admission Process 2026"),
        ("📊", "Last Year Cut-offs"),
        ("💼", "Placement Statistics"),
        ("🏛️", "Campus Tour & Facilities"),
        ("💰", "Fee Structure"),
    ],
}
current_pills = PILLS.get(role, [])

# ── Top bar ──
tb_l2, tb_r2 = st.columns([6, 1])
with tb_l2:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;padding-bottom:4px;">
        <div style="width:36px;height:36px;
                    background:linear-gradient(135deg,#3B82F6,#6D28D9);
                    border-radius:9px;display:flex;align-items:center;
                    justify-content:center;font-size:0.95rem;">🎓</div>
        <div>
            <span style="font-family:'Plus Jakarta Sans',sans-serif;
                         font-weight:800;font-size:1rem;color:#F1F5F9;">AskMNIT</span>
            <span style="margin-left:8px;font-size:0.58rem;color:#10B981;font-weight:700;">
                ● Online · LLaMA 3.3 70B
            </span>
        </div>
        <div style="margin-left:6px;padding:3px 11px;
                    background:{rmeta['border'].replace('0.25','0.10')};
                    border:1px solid {rmeta['border']};
                    border-radius:99px;font-size:0.63rem;font-weight:700;
                    color:{rmeta['color']};font-family:'Plus Jakarta Sans',sans-serif;">
            {rmeta['icon']} {rmeta['label']}
        </div>
    </div>
    """, unsafe_allow_html=True)
with tb_r2:
    st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
    if st.button("🚪 Sign Out", use_container_width=True, key="generic_logout"):
        logout()
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ── Quick metrics ──
if role == "student":
    sd = fetch_student_data(phone)
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("CGPA",     f"{sd['cgpa']} / 10", "+0.2 this sem")
    with m2: st.metric("Fee Due",  sd["fee_due"],         "")
    with m3:
        ne = sd["next_exam"]
        st.metric("Next Exam", ne.split("—")[0].strip(), ne.split("—")[-1].strip() if "—" in ne else "")

elif role == "fresher":
    fd = FRESHER_DATA
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("Avg Package 2025",  fd["placement_avg"],     "+8% YoY")
    with m2: st.metric("Highest Package",   fd["placement_highest"],  "Amazon 2025")
    with m3: st.metric("Placement Rate",    fd["placement_rate"],     "Batch 2025")

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# ── Suggestion pills ──
st.markdown("""
<p style='color:rgba(241,245,249,0.25);font-size:0.60rem;letter-spacing:1.2px;
text-transform:uppercase;margin-bottom:8px;font-weight:700;'>💡 Try asking</p>
""", unsafe_allow_html=True)

st.markdown('<div class="pill-zone">', unsafe_allow_html=True)
pcols2 = st.columns(len(current_pills))
for i, (emoji, label) in enumerate(current_pills):
    with pcols2[i]:
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

# ── Student attendance panel ──
if st.session_state.show_attendance and role == "student":
    sd2        = fetch_student_data(phone)
    attendance = sd2["attendance"]
    overall_a  = round(sum(attendance.values()) / len(attendance))

    st.markdown("""
    <div style="background:linear-gradient(160deg,#0D1221,#080C18);
                border:1px solid rgba(100,120,200,0.18);border-radius:16px;
                padding:20px 22px 14px;margin-bottom:14px;">
        <div style="font-weight:800;font-size:0.95rem;color:#F1F5F9;margin-bottom:4px;">
            📊 Subject-wise Attendance
        </div>
        <div style="font-size:0.65rem;color:rgba(100,116,139,0.50);margin-bottom:14px;">
            Minimum required: 75% · Data synced from ERP
        </div>
    """, unsafe_allow_html=True)

    for subj, pct in attendance.items():
        sc = att_color(pct)
        sb = att_badge(pct)
        cs, cp = st.columns([4, 1])
        with cs:
            st.markdown(f"""
            <div style="font-size:0.79rem;font-weight:600;
                        color:{'#FCA5A5' if pct<65 else '#FCD34D' if pct<75 else '#E2E8F0'};
                        margin-bottom:4px;">
                {subj}
                <span style="margin-left:6px;font-size:0.57rem;
                             background:{'rgba(239,68,68,0.14)' if pct<65 else 'rgba(245,158,11,0.12)' if pct<75 else 'rgba(16,185,129,0.10)'};
                             color:{sc};padding:1px 6px;border-radius:4px;">{sb}</span>
            </div>
            """, unsafe_allow_html=True)
            st.progress(pct / 100)
        with cp:
            st.markdown(f"""
            <div style="text-align:right;font-weight:800;font-size:0.95rem;
                        color:{sc};padding-top:2px;">{pct}%</div>
            """, unsafe_allow_html=True)
        st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    a1, a2, a3 = st.columns(3)
    with a1: st.metric("Overall Attendance", f"{overall_a}%",
                       "+2% from last month" if overall_a >= 75 else "Below 75% ⚠️")
    with a2:
        low = sum(1 for p in attendance.values() if p < 75)
        st.metric("Subjects Below 75%", str(low), "All clear ✓" if not low else "Need attention")
    with a3:
        ne2 = fetch_student_data(phone)["next_exam"]
        st.metric("Next Exam", ne2.split("—")[0].strip(), ne2.split("—")[-1].strip() if "—" in ne2 else "")

    if st.button("✖ Close Attendance Panel", key="close_att"):
        st.session_state.show_attendance = False
        st.rerun()
    st.divider()

# ── Chat history ──
if not st.session_state.chat_messages:
    st.markdown(f"""
    <div style="text-align:center;padding:38px 20px;opacity:0.50;">
        <div style="font-size:2.2rem;margin-bottom:12px;">{rmeta['icon']}</div>
        <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;
                    font-size:0.92rem;color:#F1F5F9;margin-bottom:6px;">I'm AskMNIT</div>
        <div style="font-size:0.78rem;color:rgba(241,245,249,0.48);
                    max-width:340px;margin:0 auto;line-height:1.65;">
            {"Ask me about PYQs, timetable, results, ERP & more." if role=="student"
             else "Ask me about MNIT admissions, cut-offs, placements, fees & campus life."}
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ── AI response ──
if st.session_state.pending_ai and st.session_state.chat_messages:
    last2 = st.session_state.chat_messages[-1]["content"]
    with st.chat_message("assistant"):
        if client is None:
            resp2 = (
                f"I'm AskMNIT. You asked: **{last2}**. "
                "Add `GROQ_API_KEY` to `.streamlit/secrets.toml` for live AI responses."
            )
            st.markdown(resp2)
            response_text2 = resp2
        else:
            role_ctx = {
                "student": (
                    "The user is a current MNIT Jaipur B.Tech student. "
                    "Help with PYQs, timetable, attendance, results, ERP, placements."
                ),
                "fresher": (
                    "The user is a prospective student interested in joining MNIT Jaipur. "
                    "Help with admissions, JoSAA, cut-offs, fee structure, placement stats, campus life."
                ),
            }
            sp2 = (
                f"You are AskMNIT — a helpful AI assistant for MNIT Jaipur. "
                f"{role_ctx.get(role, '')} Be concise, warm and accurate."
            )
            try:
                stream2 = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": sp2},
                        *[{"role": m["role"], "content": m["content"]}
                          for m in st.session_state.chat_messages],
                    ],
                    model="llama-3.3-70b-versatile",
                    stream=True,
                )
                def _gen2():
                    for chunk in stream2:
                        delta = chunk.choices[0].delta.content
                        if delta:
                            yield delta
                response_text2 = st.write_stream(_gen2())
            except Exception as e:
                response_text2 = f"⚠️ Error: {e}"
                st.error(response_text2)

    st.session_state.chat_messages.append({"role": "assistant", "content": response_text2})
    st.session_state.pending_ai = False
    st.rerun()

# ── Chat input ──
_ph = {
    "student": "Ask about PYQs, timetable, attendance, ERP…",
    "fresher": "Ask about admissions, cut-offs, placements, fees…",
}
if prompt2 := st.chat_input(_ph.get(role, "Ask me anything…"), key="generic_chat"):
    st.session_state.chat_messages.append({"role": "user", "content": prompt2})
    st.session_state.pending_ai = True
    st.rerun()

st.markdown("""
<p style="text-align:center;font-size:0.60rem;color:rgba(100,116,139,0.38);
          margin-top:8px;line-height:1.5;">
    AskMNIT can make mistakes. Please verify important information with the official admin.
</p>
""", unsafe_allow_html=True)
