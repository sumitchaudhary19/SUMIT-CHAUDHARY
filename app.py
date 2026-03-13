# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                AskMNIT  —  Streamlit App  (Final · Copy-Paste Ready)         ║
# ║                                                                              ║
# ║  ROUTING  (driven entirely by st.session_state — no URL changes needed)      ║
# ║                                                                              ║
# ║  Step 1 │ logged_in = False                        → LOGIN screen            ║
# ║  Step 2 │ logged_in = True,  user_role = None      → ROLE SELECTION          ║
# ║  Step 3 │ role = "student",  student_data = None   → COLLEGE ID ENTRY        ║
# ║  Step 4 │ role = "student",  student_data = set    → STUDENT DASHBOARD       ║
# ║  Step 3'│ role = "guardian", ward_data   = None    → WARD ID ENTRY           ║
# ║  Step 4'│ role = "guardian", ward_data   = set     → GUARDIAN DASHBOARD      ║
# ║  Step 3"│ role = "fresher"                         → FRESHER DASHBOARD       ║
# ║                                                                              ║
# ║  UI CONSTRAINTS (strictly enforced):                                         ║
# ║    • No st.sidebar anywhere                                                  ║
# ║    • No navigation tabs                                                      ║
# ║    • No "Welcome" or "Your professional dashboard" text                      ║
# ║    • All HTML built as plain strings before st.markdown() — never            ║
# ║      call Python functions inside f-string {} passed to st.markdown()        ║
# ║      (Streamlit escapes them and renders raw code on screen)                 ║
# ║                                                                              ║
# ║  BACKEND HOOKS: search [BACKEND] to wire real APIs                           ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import streamlit as st
from groq import Groq

# ─────────────────────────────────────────────────────────────────────────────
# 0. PAGE CONFIG  ← must be the very first Streamlit call
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AskMNIT",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"  # hides the expand arrow, no sidebar content used,
)

# ─────────────────────────────────────────────────────────────────────────────
# 1. GROQ CLIENT
#    Add  GROQ_API_KEY = "gsk_..."  to  .streamlit/secrets.toml
# ─────────────────────────────────────────────────────────────────────────────
client = Groq(api_key=st.secrets["GROQ_API_KEY"]) if "GROQ_API_KEY" in st.secrets else None

# ═════════════════════════════════════════════════════════════════════════════
# 2. MOCK DATABASES
# ─────────────────────────────────────────────────────────────────────────────
# STUDENT_DB  — keyed by the student's College ID (roll / enrollment number)
#
# [BACKEND] Replace fetch_student() body with:
#   import requests
#   def fetch_student(college_id):
#       r = requests.get(f"https://erp.mnit.ac.in/api/student/{college_id}",
#                        headers={"Authorization": f"Bearer {st.secrets['ERP_TOKEN']}"})
#       return r.json() if r.ok else None
# ═════════════════════════════════════════════════════════════════════════════

STUDENT_DB = {
    # ── Student 1 ────────────────────────────────────────────────────────────
    "2022UMT1234": {
        "name":       "Sumit Chaudhary",
        "initials":   "SC",
        "course":     "B.Tech Metallurgical Engineering",
        "semester":   "Semester 6",
        "college_id": "2022UMT1234",
        "section":    "Section A",
        "cgpa":       8.4,
        "backlogs":   0,
        "overall_att": 80,
        "att_subjects": {
            "Mineral Processing":           78,
            "Foundry and Casting":          92,
            "Welding Technology":           65,
            "Thermodynamics":               82,
            "Engineering Materials":        74,
            "Economics for Engineers":      85,
        },
        "grades": {
            "Mineral Processing":   "B+",
            "Foundry and Casting":  "A",
            "Welding Technology":   "C+",
            "Thermodynamics":       "B+",
            "Engineering Materials":"B",
            "Economics for Engineers": "A",
        },
        "fee_due":       "Rs. 18,500",
        "fee_due_date":  "17 Mar 2026",
        "fee_semester":  "Semester 6",
        "fee_breakdown": [
            ("Tuition Fee",  "Rs. 10,000"),
            ("Hostel Fee",   "Rs. 5,500"),
            ("Library Fee",  "Rs. 500"),
            ("Sports Fee",   "Rs. 1,000"),
            ("Exam Fee",     "Rs. 1,500"),
        ],
        "next_exam":    "Mineral Processing — 20 Mar 2026",
        "timetable_today": [
            ("08:00", "Thermodynamics",       "LT-3"),
            ("10:00", "Mineral Processing",   "LT-1"),
            ("12:00", "Welding Lab",          "Lab-B2"),
            ("14:00", "Economics Tutorial",   "CR-12"),
        ],
        "notices": [
            "Mid-Sem exams: Mar 20–27 — hall tickets on ERP",
            "Welding Lab assignment due: 18 Mar",
            "Hostel gate extended to 11 PM till exams",
        ],
        "pyq_links": {
            "Mineral Processing":   "https://mnit.ac.in/pyq/mp",
            "Welding Technology":   "https://mnit.ac.in/pyq/weld",
        },
    },

    # ── Student 2 ────────────────────────────────────────────────────────────
    "2023UCS0567": {
        "name":       "Ananya Singh",
        "initials":   "AS",
        "course":     "B.Tech Computer Science and Engineering",
        "semester":   "Semester 4",
        "college_id": "2023UCS0567",
        "section":    "Section B",
        "cgpa":       9.1,
        "backlogs":   0,
        "overall_att": 88,
        "att_subjects": {
            "Data Structures and Algorithms": 90,
            "Operating Systems":              85,
            "Computer Networks":              88,
            "Database Management Systems":    84,
            "Software Engineering":           72,
            "Discrete Mathematics":           91,
        },
        "grades": {
            "Data Structures and Algorithms": "A",
            "Operating Systems":              "A",
            "Computer Networks":              "A",
            "Database Management Systems":    "A",
            "Software Engineering":           "B+",
            "Discrete Mathematics":           "A+",
        },
        "fee_due":       "Rs. 12,000",
        "fee_due_date":  "25 Mar 2026",
        "fee_semester":  "Semester 4",
        "fee_breakdown": [
            ("Tuition Fee",  "Rs. 8,000"),
            ("Library Fee",  "Rs. 500"),
            ("Sports Fee",   "Rs. 1,000"),
            ("Exam Fee",     "Rs. 2,500"),
        ],
        "next_exam":    "Data Structures — 22 Mar 2026",
        "timetable_today": [
            ("09:00", "Operating Systems",              "LT-5"),
            ("11:00", "Data Structures Lab",            "CS-Lab-1"),
            ("14:00", "Software Engineering",           "LT-2"),
            ("16:00", "DBMS Tutorial",                  "CR-8"),
        ],
        "notices": [
            "DSA Project submission: 21 Mar (via ERP portal)",
            "Guest lecture on AI/ML: 19 Mar 3 PM, Seminar Hall",
            "OS Mid-Sem paper pattern changed — check notice board",
        ],
        "pyq_links": {
            "Data Structures and Algorithms": "https://mnit.ac.in/pyq/dsa",
            "Operating Systems":              "https://mnit.ac.in/pyq/os",
        },
    },

    # ── Student 3 ────────────────────────────────────────────────────────────
    "2021UCE0892": {
        "name":       "Rohit Sharma",
        "initials":   "RS",
        "course":     "B.Tech Civil Engineering",
        "semester":   "Semester 8",
        "college_id": "2021UCE0892",
        "section":    "Section A",
        "cgpa":       7.6,
        "backlogs":   1,
        "overall_att": 71,
        "att_subjects": {
            "Structural Analysis":    74,
            "Foundation Engineering": 68,
            "Hydraulics":             72,
            "Transportation Engg.":   65,
            "Project Work":           95,
        },
        "grades": {
            "Structural Analysis":    "B",
            "Foundation Engineering": "C+",
            "Hydraulics":             "B",
            "Transportation Engg.":   "C",
            "Project Work":           "A+",
        },
        "fee_due":       "Rs. 9,500",
        "fee_due_date":  "30 Mar 2026",
        "fee_semester":  "Semester 8",
        "fee_breakdown": [
            ("Tuition Fee",  "Rs. 7,000"),
            ("Library Fee",  "Rs. 500"),
            ("Exam Fee",     "Rs. 2,000"),
        ],
        "next_exam":    "Structural Analysis — 25 Mar 2026",
        "timetable_today": [
            ("08:30", "Structural Analysis",   "LT-4"),
            ("10:30", "Hydraulics Lab",        "CE-Lab"),
            ("14:00", "Project Review",        "Dept. Conf. Room"),
        ],
        "notices": [
            "Final year project viva: Apr 2–5 — confirm slot on ERP",
            "Hydraulics lab report due: 20 Mar",
            "Backlog exam registration open till 18 Mar",
        ],
        "pyq_links": {
            "Structural Analysis":    "https://mnit.ac.in/pyq/sa",
            "Foundation Engineering": "https://mnit.ac.in/pyq/fe",
        },
    },
}

# WARD_DB — keyed by ward's college ID (for guardian role)
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
            "Mineral Processing":          78,
            "Foundry and Casting":         92,
            "Welding Technology":          65,
            "Thermodynamics":              82,
            "Engineering Materials":       74,
            "Economics for Engineers":     85,
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
        "next_exam": "Mineral Processing — 20 Mar 2026",
        "notices": [
            "Mid-Sem exams: Mar 20–27",
            "Parent-Teacher Meet: Mar 15 (10 AM – 1 PM)",
            "Hostel gate extended to 11 PM till exams",
        ],
    },
    "2023UCS0567": {
        "name":          "Ananya Singh",
        "initials":      "AS",
        "course":        "B.Tech Computer Science and Engineering",
        "semester":      "Semester 4",
        "roll":          "2023UCS0567",
        "campus_status": "On Campus",
        "hostel_block":  "Girls Hostel G-2, Room 108",
        "warden":        "Dr. Priya Nair",
        "warden_phone":  "+91-141-2529070",
        "cgpa":          9.1,
        "overall_att":   88,
        "att_7d":        "Regular",
        "att_subjects": {
            "Data Structures and Algorithms": 90,
            "Operating Systems":              85,
            "Computer Networks":              88,
            "Database Management Systems":    84,
            "Software Engineering":           72,
        },
        "fee_pending":  "Rs. 12,000",
        "fee_due_date": "25 Mar 2026",
        "fee_semester": "Semester 4",
        "fee_breakdown": [
            ("Tuition Fee",  "Rs. 8,000"),
            ("Library Fee",  "Rs. 500"),
            ("Sports Fee",   "Rs. 1,000"),
            ("Exam Fee",     "Rs. 2,500"),
        ],
        "next_exam": "Data Structures — 22 Mar 2026",
        "notices": [
            "DSA Project submission: 21 Mar",
            "Guest lecture on AI: 19 Mar 3 PM",
        ],
    },
}

FRESHER_DATA = {
    "placement_avg":     "Rs. 12.4 LPA",
    "placement_highest": "Rs. 48 LPA  (Amazon)",
    "placement_rate":    "94%",
    "admission_deadline": "15 Jun 2026  (JoSAA Round 1)",
    "cutoff_general":    "CRL Rank ≤ 14,800  (Metallurgy 2025)",
    "fee_per_sem":       "Rs. 45,000  (approx)",
}


# ─────────────────────────────────────────────────────────────────────────────
# 3. PURE HELPER FUNCTIONS  (return plain values — no HTML)
# ─────────────────────────────────────────────────────────────────────────────
def fetch_student(college_id: str):
    """Primary fetch for Student role.  Returns dict or None."""
    return STUDENT_DB.get(college_id.strip().upper())

def fetch_ward(ward_id: str):
    """Primary fetch for Guardian role.  Returns dict or None."""
    return WARD_DB.get(ward_id.strip().upper())

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

def grade_color(grade: str) -> str:
    if grade.startswith("A"):
        return "#10B981"
    elif grade.startswith("B"):
        return "#60A5FA"
    elif grade.startswith("C"):
        return "#F59E0B"
    return "#EF4444"


# ─────────────────────────────────────────────────────────────────────────────
# 4. SESSION STATE — initialise all keys once on first load
# ─────────────────────────────────────────────────────────────────────────────
_DEFAULTS: dict = {
    # Routing
    "logged_in":       False,
    "user_phone":      "",
    "user_role":       None,
    "otp_sent":        False,

    # Student-specific
    "student_id":      "",
    "student_data":    None,
    "student_id_error": "",
    "show_timetable":  False,
    "show_pyq":        False,
    "show_att_detail": False,   # shared with guardian

    # Guardian-specific
    "ward_id":         "",
    "ward_data":       None,
    "ward_id_error":   "",
    "show_ward_att":   False,

    # Chat
    "chat_messages":   [],
    "pending_ai":      False,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

def _logout():
    for k, v in _DEFAULTS.items():
        st.session_state[k] = v
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# 5. GLOBAL CSS — dark premium theme, Plus Jakarta Sans
#    No sidebar styles needed — sidebar is fully hidden.
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
    padding-bottom: 52px !important;
    max-width: 100% !important;
}
/* Hide everything we don't need */
header[data-testid="stHeader"], footer, #MainMenu,
[data-testid="stToolbar"], [data-testid="stDecoration"],
section[data-testid="stSidebar"] { display: none !important; }

/* ── Text inputs ── */
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 10px !important;
    color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 11px 14px !important;
}
[data-testid="stTextInput"] label {
    color: rgba(241,245,249,0.55) !important;
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: rgba(59,130,246,0.55) !important;
    box-shadow: 0 0 0 2px rgba(59,130,246,0.15) !important;
}

/* ── Default button — blue-purple gradient ── */
.stButton > button {
    background: linear-gradient(135deg, #3B82F6, #6D28D9) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    padding: 10px 20px !important;
    box-shadow: 0 4px 16px rgba(59,130,246,0.25) !important;
    transition: all 0.18s ease !important;
    letter-spacing: 0.2px !important;
}
.stButton > button:hover {
    opacity: 0.90 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(59,130,246,0.35) !important;
}
.stButton > button:active { transform: scale(0.98) !important; }

/* ── Ghost button ── */
.ghost-btn .stButton > button {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    color: rgba(241,245,249,0.55) !important;
    box-shadow: none !important;
}
.ghost-btn .stButton > button:hover {
    background: rgba(59,130,246,0.10) !important;
    color: #F1F5F9 !important;
    border-color: rgba(59,130,246,0.28) !important;
}

/* ── Pill / suggestion buttons ── */
.pill-zone .stButton > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 999px !important;
    color: rgba(241,245,249,0.60) !important;
    font-size: 0.73rem !important;
    font-weight: 500 !important;
    box-shadow: none !important;
    padding: 7px 14px !important;
}
.pill-zone .stButton > button:hover {
    background: rgba(99,102,241,0.14) !important;
    border-color: rgba(99,102,241,0.35) !important;
    color: #C7D2FE !important;
    transform: translateY(-1px) !important;
}

/* ── Pay / action button overrides ── */
.pay-btn .stButton > button {
    background: linear-gradient(135deg, #D97706, #F59E0B) !important;
    box-shadow: 0 4px 18px rgba(245,158,11,0.30) !important;
}

/* ── st.metric cards ── */
[data-testid="stMetric"] {
    background: linear-gradient(160deg, #0D1221, #080C18) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
    padding: 16px 18px !important;
}
[data-testid="stMetricLabel"] {
    color: rgba(241,245,249,0.40) !important;
    font-size: 0.66rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.9px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stMetricValue"] {
    color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.4rem !important;
}
[data-testid="stMetricDelta"] { font-family: 'Plus Jakarta Sans', sans-serif !important; }

/* ── Progress bars ── */
[data-testid="stProgress"] > div > div {
    border-radius: 99px !important;
}

/* ── Chat ── */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stChatInput"] > div {
    background: rgba(10,14,26,0.96) !important;
    border: 1px solid rgba(80,90,160,0.35) !important;
    border-radius: 14px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.88rem !important;
}
[data-testid="stChatInput"] button[data-testid="stChatInputSubmitButton"] {
    background: linear-gradient(135deg, #3B82F6, #6D28D9) !important;
    border-radius: 9px !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    margin-bottom: 6px !important;
}
summary {
    color: #E2E8F0 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.86rem !important;
}

/* ── Misc text ── */
[data-testid="stMarkdown"] p, [data-testid="stMarkdown"] li {
    color: rgba(241,245,249,0.70) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
h1, h2, h3 {
    color: #F1F5F9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 800 !important;
    letter-spacing: -0.4px !important;
}
hr { border-color: rgba(255,255,255,0.07) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.25); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# ████  SCREEN 1 — LOGIN  ████
# ═════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:

    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        # Brand
        st.markdown("""
        <div style="text-align:center;padding:44px 0 28px;">
            <div style="width:60px;height:60px;margin:0 auto 14px;
                        background:linear-gradient(135deg,#3B82F6,#6D28D9);
                        border-radius:15px;display:flex;align-items:center;
                        justify-content:center;font-size:1.8rem;
                        box-shadow:0 8px 28px rgba(59,130,246,0.32);">&#127891;</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.55rem;
                        font-weight:800;color:#F1F5F9;letter-spacing:-0.7px;">AskMNIT</div>
            <div style="font-size:0.72rem;color:rgba(100,116,139,0.65);margin-top:5px;">
                Campus Intelligence &nbsp;&#183;&nbsp; LLaMA 3.3 70B
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Card shell
        st.markdown("""
        <div style="background:linear-gradient(160deg,#0C1120,#080D19);
                    border:1px solid rgba(100,120,220,0.16);border-radius:22px;
                    padding:26px 28px 14px;
                    box-shadow:0 28px 90px rgba(0,0,0,0.72);">
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.05rem;
                        font-weight:800;color:#F1F5F9;margin-bottom:4px;">
                Sign in to continue
            </div>
            <div style="font-size:0.73rem;color:rgba(148,163,184,0.50);margin-bottom:20px;">
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
                placeholder="4–6 digit OTP",
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
                  margin-top:16px;line-height:1.6;padding-bottom:6px;">
            By continuing you agree to MNIT's Terms of Service and Privacy Policy.
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
        <div style="text-align:center;padding:40px 0 30px;">
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.45rem;
                        font-weight:800;color:#F1F5F9;letter-spacing:-0.5px;margin-bottom:6px;">
                Tell us who you are
            </div>
            <div style="font-size:0.77rem;color:rgba(148,163,184,0.50);">
                AskMNIT will personalise itself based on your role.
            </div>
        </div>
        """, unsafe_allow_html=True)

        ROLES = [
            ("student",  "Current Student",     "",
             "Already enrolled at MNIT Jaipur.",
             "linear-gradient(135deg,#065F46,#10B981)", "rgba(16,185,129,0.28)"),
            ("guardian", "Guardian or Parent",  "",
             "Here for my ward or child.",
             "linear-gradient(135deg,#7C3AED,#A78BFA)", "rgba(139,92,246,0.28)"),
            ("fresher",  "Prospective Student", "Fresher",
             "Looking to apply for admission.",
             "linear-gradient(135deg,#1D4ED8,#3B82F6)", "rgba(59,130,246,0.28)"),
        ]

        for rid, title, badge, desc, grad, glow in ROLES:
            badge_html = ""
            if badge:
                badge_html = (
                    '<span style="font-size:0.57rem;padding:2px 7px;'
                    'background:rgba(255,255,255,0.14);border-radius:4px;'
                    'font-weight:700;letter-spacing:0.5px;text-transform:uppercase;'
                    'margin-left:8px;">' + badge + '</span>'
                )

            st.markdown(
                '<div style="background:rgba(255,255,255,0.025);'
                'border:1px solid rgba(255,255,255,0.08);'
                'border-radius:14px;padding:15px 18px 9px;margin-bottom:4px;">'
                '<div style="display:flex;align-items:center;gap:14px;">'
                '<div style="width:46px;height:46px;border-radius:12px;'
                'background:' + grad + ';display:flex;align-items:center;'
                'justify-content:center;font-size:1.3rem;flex-shrink:0;'
                'box-shadow:0 4px 14px ' + glow + ';">&#127891;</div>'
                '<div>'
                '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;'
                'font-weight:700;font-size:0.92rem;color:#F1F5F9;">'
                + title + badge_html + '</div>'
                '<div style="font-size:0.73rem;color:rgba(148,163,184,0.55);margin-top:2px;">'
                + desc + '</div>'
                '</div></div></div>',
                unsafe_allow_html=True,
            )

            if st.button("Select  " + title, key="role_" + rid, use_container_width=True):
                # [BACKEND] Persist role to your DB here
                st.session_state.user_role      = rid
                st.session_state.chat_messages  = []
                st.session_state.student_data   = None
                st.session_state.student_id_error = ""
                st.session_state.ward_data      = None
                st.session_state.ward_id_error  = ""
                st.rerun()

            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    st.stop()


# ═════════════════════════════════════════════════════════════════════════════
# ████  SCREEN 3 — STUDENT COLLEGE ID ENTRY  ████
# Condition: role = "student"  AND  student_data is None
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.user_role == "student" and st.session_state.student_data is None:

    _, col, _ = st.columns([1, 1.6, 1])
    with col:
        st.markdown("""
        <div style="text-align:center;padding:40px 0 28px;">
            <div style="width:60px;height:60px;margin:0 auto 16px;
                        background:linear-gradient(135deg,#065F46,#10B981);
                        border-radius:16px;display:flex;align-items:center;
                        justify-content:center;font-size:1.75rem;
                        box-shadow:0 8px 28px rgba(16,185,129,0.30);">&#127979;</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.25rem;
                        font-weight:800;color:#F1F5F9;letter-spacing:-0.4px;margin-bottom:6px;">
                Enter your College ID
            </div>
            <div style="font-size:0.76rem;color:rgba(148,163,184,0.52);
                        line-height:1.65;max-width:320px;margin:0 auto;">
                Enter your roll number or enrollment number to load
                your personal academic dashboard.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Card shell
        st.markdown("""
        <div style="background:linear-gradient(160deg,#0C1120,#080D19);
                    border:1px solid rgba(16,185,129,0.20);border-radius:22px;
                    padding:24px 28px 10px;
                    box-shadow:0 28px 90px rgba(0,0,0,0.72);">
        """, unsafe_allow_html=True)

        college_id_input = st.text_input(
            "College ID / Enrollment Number  (required)",
            placeholder="e.g. 2022UMT1234  or  2023UCS0567",
            key="student_id_input",
        )

        # Show error from previous failed attempt
        if st.session_state.student_id_error:
            err_box = (
                '<div style="background:rgba(239,68,68,0.08);'
                'border:1px solid rgba(239,68,68,0.25);border-radius:9px;'
                'padding:10px 14px;margin:8px 0;'
                'font-size:0.74rem;color:#FCA5A5;line-height:1.5;">'
                + st.session_state.student_id_error + '</div>'
            )
            st.markdown(err_box, unsafe_allow_html=True)

        if st.button("Load My Dashboard", use_container_width=True, key="btn_student_login"):
            raw = college_id_input.strip()
            if not raw:
                st.session_state.student_id_error = (
                    "This field is required. Please enter your College ID."
                )
                st.rerun()
            else:
                # ── CORE FETCH — college_id is the primary key ────────────
                # [BACKEND] Replace with real API call:
                #   r = requests.get(f"{ERP_URL}/api/student/{raw}",
                #                    headers={"Authorization": f"Bearer {TOKEN}"})
                #   fetched = r.json() if r.ok else None
                fetched = fetch_student(raw)

                if fetched is None:
                    st.session_state.student_id_error = (
                        'College ID "' + raw.upper() + '" not found in records. '
                        "Demo IDs: 2022UMT1234  |  2023UCS0567  |  2021UCE0892"
                    )
                    st.rerun()
                else:
                    # Save fetched data into session state.
                    # From this point the entire student dashboard reads
                    # ONLY from st.session_state.student_data.
                    st.session_state.student_id       = raw.upper()
                    st.session_state.student_data     = fetched
                    st.session_state.student_id_error = ""
                    st.session_state.chat_messages    = []
                    st.rerun()   # → STUDENT DASHBOARD

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <p style="text-align:center;font-size:0.65rem;color:rgba(100,116,139,0.45);
                  margin-top:12px;line-height:1.6;">
            Your College ID is printed on your MNIT identity card.
        </p>
        """, unsafe_allow_html=True)

        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("Change Role", use_container_width=True, key="btn_student_back"):
            st.session_state.user_role        = None
            st.session_state.student_id_error = ""
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()


# ═════════════════════════════════════════════════════════════════════════════
# ████  SCREEN 4 — STUDENT DASHBOARD  ████
#
#  All data comes from  sd = st.session_state.student_data
#  That dict was fetched using the student's College ID.
#
#  Layout: two columns — left (data cards) | right (AI chatbot)
#  No sidebar · No tabs · No greeting headings
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.user_role == "student" and st.session_state.student_data is not None:

    sd          = st.session_state.student_data  # single source of truth
    att_overall = sd["overall_att"]
    att_c       = att_color(att_overall)

    # ── Top bar ───────────────────────────────────────────────────────────────
    tb_l, tb_r = st.columns([6, 1])
    with tb_l:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:12px;padding-bottom:4px;">'
            '<div style="width:36px;height:36px;'
            'background:linear-gradient(135deg,#3B82F6,#6D28D9);'
            'border-radius:9px;display:flex;align-items:center;'
            'justify-content:center;font-size:0.95rem;">&#127891;</div>'
            '<span style="font-family:\'Plus Jakarta Sans\',sans-serif;'
            'font-weight:800;font-size:1rem;color:#F1F5F9;">AskMNIT</span>'
            '<span style="margin-left:8px;font-size:0.58rem;'
            'color:#10B981;font-weight:700;">&#9679; Online</span>'
            '<div style="margin-left:8px;padding:3px 11px;'
            'background:rgba(16,185,129,0.10);'
            'border:1px solid rgba(16,185,129,0.25);border-radius:99px;'
            'font-size:0.63rem;font-weight:700;color:#34D399;">'
            'Student  ' + sd["college_id"] + '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with tb_r:
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True, key="student_logout"):
            _logout()
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    left_col, right_col = st.columns([1.1, 1], gap="large")

    # ═════════════════════════════════════════════
    # LEFT COLUMN — DATA CARDS
    # ALL HTML is pre-built as plain strings before
    # st.markdown() — never call functions in { }
    # ═════════════════════════════════════════════
    with left_col:

        # ── CARD 1: STUDENT PROFILE ──────────────────────────────────────────
        # Build backlog tag
        if sd["backlogs"] == 0:
            backlog_tag = (
                '<span style="display:inline-flex;align-items:center;gap:5px;'
                'padding:3px 10px;border-radius:999px;background:rgba(16,185,129,0.12);'
                'font-size:0.65rem;font-weight:700;color:#34D399;">'
                '<span style="width:5px;height:5px;border-radius:50%;'
                'background:#34D399;display:inline-block;"></span>'
                'No Backlogs</span>'
            )
        else:
            backlog_tag = (
                '<span style="display:inline-flex;align-items:center;gap:5px;'
                'padding:3px 10px;border-radius:999px;background:rgba(239,68,68,0.12);'
                'font-size:0.65rem;font-weight:700;color:#FCA5A5;">'
                '<span style="width:5px;height:5px;border-radius:50%;'
                'background:#EF4444;display:inline-block;"></span>'
                + str(sd["backlogs"]) + ' Backlog</span>'
            )

        # Info tiles
        info_grid = ""
        for lbl, val in [
            ("Course",   sd["course"]),
            ("Semester", sd["semester"]),
            ("Section",  sd["section"]),
            ("Roll No",  sd["college_id"]),
        ]:
            info_grid += (
                '<div style="background:rgba(255,255,255,0.04);'
                'border-radius:10px;padding:10px 12px;">'
                '<div style="font-size:0.56rem;color:rgba(100,116,139,0.52);'
                'font-weight:700;text-transform:uppercase;'
                'letter-spacing:0.8px;margin-bottom:3px;">' + lbl + '</div>'
                '<div style="font-size:0.73rem;color:#E2E8F0;'
                'font-weight:600;line-height:1.4;">' + val + '</div>'
                '</div>'
            )

        st.markdown(
            '<div style="background:linear-gradient(160deg,#0D1221,#080C18);'
            'border:1px solid rgba(16,185,129,0.18);border-radius:16px;'
            'padding:20px 22px 18px;margin-bottom:14px;">'

            '<div style="display:flex;align-items:flex-start;gap:14px;margin-bottom:16px;">'
            '<div style="width:54px;height:54px;border-radius:14px;flex-shrink:0;'
            'background:linear-gradient(135deg,#065F46,#10B981);'
            'display:flex;align-items:center;justify-content:center;'
            'font-size:1.1rem;font-weight:800;color:white;'
            'box-shadow:0 4px 16px rgba(16,185,129,0.28);">'
            + sd["initials"] + '</div>'
            '<div style="flex:1;min-width:0;">'
            '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;'
            'font-weight:800;font-size:1.05rem;color:#F1F5F9;margin-bottom:2px;">'
            + sd["name"] + '</div>'
            '<div style="font-size:0.70rem;color:rgba(148,163,184,0.55);'
            'margin-bottom:8px;">' + sd["course"] + '</div>'
            + backlog_tag +
            '</div></div>'

            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:9px;'
            'border-top:1px solid rgba(255,255,255,0.06);padding-top:14px;">'
            + info_grid +
            '</div></div>',
            unsafe_allow_html=True,
        )

        # ── CARD 2: ATTENDANCE ───────────────────────────────────────────────
        warn_html = ""
        if att_overall < 75:
            warn_html = (
                '<div style="background:rgba(245,158,11,0.08);'
                'border:1px solid rgba(245,158,11,0.22);border-radius:8px;'
                'padding:8px 12px;margin-bottom:12px;font-size:0.71rem;'
                'color:#FCD34D;line-height:1.5;">'
                'Overall attendance below 75% — exam eligibility may be affected.'
                '</div>'
            )

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
            'justify-content:space-between;margin-bottom:12px;">'
            '<div>'
            '<div style="font-size:2.2rem;font-weight:800;color:' + att_c + ';'
            'letter-spacing:-1px;line-height:1;">' + str(att_overall) + '%</div>'
            '<div style="font-size:0.70rem;color:rgba(148,163,184,0.52);margin-top:4px;">'
            'Overall this semester</div>'
            '</div>'
            + ring_html +
            '</div>'
            + warn_html +
            '</div>',
            unsafe_allow_html=True,
        )

        # Subject-wise attendance expander
        with st.expander("View Subject-wise Attendance", expanded=False):
            st.markdown(
                '<div style="font-size:0.60rem;color:rgba(100,116,139,0.50);'
                'font-weight:700;text-transform:uppercase;letter-spacing:1px;'
                'margin-bottom:10px;padding-top:4px;">'
                'Subject  |  Attendance  |  Grade</div>',
                unsafe_allow_html=True,
            )
            for subj, pct in sd["att_subjects"].items():
                sc  = att_color(pct)
                stc = att_text_color(pct)
                sbg = att_bg_color(pct)
                sb  = att_badge(pct)
                grade = sd["grades"].get(subj, "—")
                gc    = grade_color(grade)
                col_s, col_p, col_g = st.columns([5, 2, 1])
                with col_s:
                    st.markdown(
                        '<div style="font-size:0.78rem;font-weight:600;color:' + stc + ';'
                        'margin-bottom:3px;">' + subj +
                        '  <span style="font-size:0.56rem;background:' + sbg + ';'
                        'color:' + sc + ';padding:1px 6px;border-radius:4px;">'
                        + sb + '</span></div>',
                        unsafe_allow_html=True,
                    )
                    st.progress(pct / 100)
                with col_p:
                    st.markdown(
                        '<div style="text-align:right;font-weight:800;font-size:0.92rem;'
                        'color:' + sc + ';padding-top:2px;">' + str(pct) + '%</div>',
                        unsafe_allow_html=True,
                    )
                with col_g:
                    st.markdown(
                        '<div style="text-align:center;font-weight:800;font-size:0.88rem;'
                        'color:' + gc + ';padding-top:2px;'
                        'background:rgba(255,255,255,0.04);border-radius:6px;">'
                        + grade + '</div>',
                        unsafe_allow_html=True,
                    )
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            st.markdown(
                '<p style="font-size:0.62rem;color:rgba(100,116,139,0.45);'
                'text-align:center;margin-top:8px;">'
                'Min required: 75%  ·  Data synced from ERP</p>',
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # ── CARD 3: FEE STATUS ───────────────────────────────────────────────
        fee_rows = ""
        for item, amt in sd["fee_breakdown"]:
            fee_rows += (
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
            'Fee Status  —  ' + sd["fee_semester"] + '</div>'
            '<div style="display:flex;align-items:flex-end;'
            'justify-content:space-between;margin-bottom:16px;">'
            '<div>'
            '<div style="font-size:0.70rem;color:rgba(148,163,184,0.50);margin-bottom:3px;">'
            'Amount Due</div>'
            '<div style="font-size:2rem;font-weight:800;color:#F59E0B;letter-spacing:-1px;">'
            + sd["fee_due"] + '</div>'
            '</div>'
            '<div style="text-align:right;">'
            '<div style="font-size:0.58rem;color:rgba(100,116,139,0.48);margin-bottom:2px;">'
            'Due Date</div>'
            '<div style="font-size:0.88rem;font-weight:700;color:#EF4444;">'
            + sd["fee_due_date"] + '</div>'
            '</div></div>'
            + fee_rows +
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="pay-btn">', unsafe_allow_html=True)
        if st.button("Pay Fees Now", use_container_width=True, key="student_pay"):
            # [BACKEND] Redirect to MNIT payment gateway
            st.info("Redirecting to payment gateway — wire the real URL here.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # ── CARD 4: TODAY'S TIMETABLE ────────────────────────────────────────
        tt_rows = ""
        for time, subj, room in sd["timetable_today"]:
            tt_rows += (
                '<div style="display:flex;align-items:center;gap:12px;'
                'padding:9px 0;border-bottom:1px solid rgba(255,255,255,0.05);">'
                '<div style="font-size:0.68rem;font-weight:700;color:rgba(99,102,241,0.80);'
                'min-width:42px;">' + time + '</div>'
                '<div style="flex:1;">'
                '<div style="font-size:0.78rem;font-weight:600;color:#E2E8F0;">'
                + subj + '</div>'
                '<div style="font-size:0.62rem;color:rgba(100,116,139,0.55);margin-top:1px;">'
                + room + '</div>'
                '</div></div>'
            )

        st.markdown(
            '<div style="background:linear-gradient(160deg,#0D1221,#080C18);'
            'border:1px solid rgba(99,102,241,0.18);border-radius:16px;'
            'padding:18px 20px 14px;margin-bottom:14px;">'
            '<div style="font-size:0.60rem;color:rgba(100,116,139,0.52);'
            'font-weight:700;text-transform:uppercase;'
            'letter-spacing:1px;margin-bottom:10px;">Today\'s Timetable</div>'
            + tt_rows +
            '</div>',
            unsafe_allow_html=True,
        )

        # ── CARD 5: NOTICES ──────────────────────────────────────────────────
        notices_html = ""
        for i, notice in enumerate(sd["notices"]):
            notices_html += (
                '<div style="display:flex;gap:10px;padding:9px 12px;'
                'background:rgba(255,255,255,0.03);border-radius:9px;margin-bottom:6px;">'
                '<span style="font-size:0.60rem;color:rgba(100,116,139,0.48);'
                'font-weight:700;flex-shrink:0;margin-top:1px;">0'
                + str(i + 1) + '</span>'
                '<span style="font-size:0.76rem;color:rgba(148,163,184,0.65);line-height:1.5;">'
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

        # Quick metric row
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("CGPA", str(sd["cgpa"]) + " / 10", "Current sem")
        with m2:
            st.metric("Fee Due", sd["fee_due"], "By " + sd["fee_due_date"])
        with m3:
            ne = sd["next_exam"]
            label, delta = (ne.split("—")[0].strip(), ne.split("—")[-1].strip()) if "—" in ne else (ne, "")
            st.metric("Next Exam", label, delta)

    # ═══════════════════════════════════════════
    # RIGHT COLUMN — AI CHATBOT
    # ═══════════════════════════════════════════
    with right_col:

        first_name = sd["name"].split()[0]

        # Chat header
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
            'Student Mode  —  ' + sd["course"].split()[0] + ' ' + sd["semester"] + '</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )

        STUDENT_PILLS = [
            "View Attendance",
            "Download PYQs",
            "Today's Timetable",
            "Fee Status",
            "Exam Schedule",
        ]

        if not st.session_state.chat_messages:
            st.markdown(
                '<div style="text-align:center;padding:28px 16px 20px;opacity:0.55;">'
                '<div style="font-size:2.2rem;margin-bottom:10px;">&#127979;</div>'
                '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;'
                'font-weight:700;font-size:0.9rem;color:#F1F5F9;margin-bottom:6px;">'
                "Hey " + first_name + ", what can I help you with?</div>"
                '<div style="font-size:0.75rem;color:rgba(241,245,249,0.50);'
                'max-width:280px;margin:0 auto;line-height:1.65;">'
                'Ask me about your subjects, attendance, fees, PYQs or exam schedule.</div>'
                '</div>',
                unsafe_allow_html=True,
            )

            st.markdown('<div class="pill-zone">', unsafe_allow_html=True)
            pill_cols = st.columns(len(STUDENT_PILLS))
            for i, label in enumerate(STUDENT_PILLS):
                with pill_cols[i]:
                    if st.button(label, key="spill_" + str(i), use_container_width=True):
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
                        low_subs = [s for s, p in sd["att_subjects"].items() if p < 75]
                        resp = (
                            "**" + sd["name"] + "'s Overall Attendance: " + str(att_overall) + "%**\n\n"
                            + ("⚠️ Subjects below 75%: " + ", ".join(low_subs) + "." if low_subs
                               else "✅ All subjects above 75% threshold.")
                        )
                    elif "pyq" in lower or "question" in lower or "previous" in lower:
                        pyq_text = "\n".join([
                            "- **" + s + "**: " + link
                            for s, link in sd.get("pyq_links", {}).items()
                        ])
                        resp = (
                            "**Previous Year Question Papers for " + sd["name"] + ":**\n\n"
                            + (pyq_text if pyq_text else "PYQ links will be added soon. Check ERP portal.")
                        )
                    elif "timetable" in lower or "schedule" in lower or "class" in lower:
                        tt_text = "\n".join([
                            "- **" + t + "** — " + s + " (" + r + ")"
                            for t, s, r in sd["timetable_today"]
                        ])
                        resp = "**Today's Classes for " + sd["name"] + ":**\n\n" + tt_text
                    elif "fee" in lower or "pay" in lower or "due" in lower:
                        resp = (
                            "**Fee Status — " + sd["fee_semester"] + ":**\n\n"
                            "Amount due: **" + sd["fee_due"] + "**\n"
                            "Due date: **" + sd["fee_due_date"] + "**\n\n"
                            "Click 'Pay Fees Now' on the left panel to proceed."
                        )
                    elif "exam" in lower or "next" in lower:
                        resp = "**Next Exam:** " + sd["next_exam"]
                    elif "cgpa" in lower or "grade" in lower or "result" in lower:
                        grade_lines = "\n".join([
                            "- " + s + ": **" + g + "**"
                            for s, g in sd["grades"].items()
                        ])
                        resp = (
                            "**Current CGPA: " + str(sd["cgpa"]) + " / 10**\n\n"
                            "**Subject Grades:**\n" + grade_lines
                        )
                    else:
                        resp = (
                            "I'm AskMNIT — your personal campus assistant. "
                            "You asked: *" + last + "*\n\n"
                            "Add `GROQ_API_KEY` to `.streamlit/secrets.toml` for full AI responses. "
                            "I can help with attendance, PYQs, timetable, fees, and exam schedules."
                        )
                    st.markdown(resp)
                    response_text = resp
                else:
                    # [BACKEND] Live Groq streaming — student-specific system prompt
                    system_prompt = (
                        "You are AskMNIT — a helpful, friendly AI assistant for MNIT Jaipur students. "
                        "Current student context:\n"
                        "Name: " + sd["name"] + "\n"
                        "Course: " + sd["course"] + ", " + sd["semester"] + "\n"
                        "College ID: " + sd["college_id"] + "\n"
                        "CGPA: " + str(sd["cgpa"]) + "\n"
                        "Overall Attendance: " + str(att_overall) + "%\n"
                        "Subjects: " + ", ".join(sd["att_subjects"].keys()) + "\n"
                        "Next Exam: " + sd["next_exam"] + "\n"
                        "Fee Due: " + sd["fee_due"] + " by " + sd["fee_due_date"] + "\n\n"
                        "Answer questions about this student's academics, attendance, fees, "
                        "exam schedule, PYQs, and hostel. Be concise, warm, and accurate."
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
                        def _stream_student():
                            for chunk in stream:
                                delta = chunk.choices[0].delta.content
                                if delta:
                                    yield delta
                        response_text = st.write_stream(_stream_student())
                    except Exception as e:
                        response_text = "Error: " + str(e)
                        st.error(response_text)

                st.session_state.chat_messages.append(
                    {"role": "assistant", "content": response_text}
                )
            st.session_state.pending_ai = False
            st.rerun()

        if prompt := st.chat_input(
            "Ask about " + first_name + "'s attendance, PYQs, fees, timetable...",
            key="student_chat",
        ):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            st.session_state.pending_ai = True
            st.rerun()

        st.markdown("""
        <p style="text-align:center;font-size:0.61rem;color:rgba(100,116,139,0.38);
                  margin-top:8px;line-height:1.5;">
            AskMNIT can make mistakes. Verify critical info with official admin or ERP.
        </p>
        """, unsafe_allow_html=True)

    st.stop()


# ═════════════════════════════════════════════════════════════════════════════
# ████  SCREEN 3' — GUARDIAN WARD ID ENTRY  ████
# Condition: role = "guardian"  AND  ward_data is None
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.user_role == "guardian" and st.session_state.ward_data is None:

    _, col, _ = st.columns([1, 1.6, 1])
    with col:
        st.markdown("""
        <div style="text-align:center;padding:40px 0 28px;">
            <div style="width:60px;height:60px;margin:0 auto 16px;
                        background:linear-gradient(135deg,#7C3AED,#A78BFA);
                        border-radius:16px;display:flex;align-items:center;
                        justify-content:center;font-size:1.75rem;
                        box-shadow:0 8px 28px rgba(139,92,246,0.30);">&#128106;</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.2rem;
                        font-weight:800;color:#F1F5F9;letter-spacing:-0.4px;margin-bottom:6px;">
                Enter Ward's College ID
            </div>
            <div style="font-size:0.76rem;color:rgba(148,163,184,0.52);
                        line-height:1.65;max-width:320px;margin:0 auto;">
                Enter your child's roll number or enrollment number to link
                their academic data to your account.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:linear-gradient(160deg,#0C1120,#080D19);
                    border:1px solid rgba(139,92,246,0.20);border-radius:22px;
                    padding:24px 28px 10px;box-shadow:0 28px 90px rgba(0,0,0,0.72);">
        """, unsafe_allow_html=True)

        ward_input = st.text_input(
            "Ward's College ID / Enrollment Number  (required)",
            placeholder="e.g. 2022UMT1234  or  2023UCS0567",
            key="ward_id_field",
        )

        if st.session_state.ward_id_error:
            st.markdown(
                '<div style="background:rgba(239,68,68,0.08);'
                'border:1px solid rgba(239,68,68,0.25);border-radius:9px;'
                'padding:10px 14px;margin:8px 0;'
                'font-size:0.74rem;color:#FCA5A5;line-height:1.5;">'
                + st.session_state.ward_id_error + '</div>',
                unsafe_allow_html=True,
            )

        if st.button("Link Ward Account", use_container_width=True, key="btn_link_ward"):
            raw = ward_input.strip()
            if not raw:
                st.session_state.ward_id_error = (
                    "This field is required. Please enter your ward's College ID."
                )
                st.rerun()
            else:
                # [BACKEND] Replace with real API call
                fetched = fetch_ward(raw)
                if fetched is None:
                    st.session_state.ward_id_error = (
                        'ID "' + raw.upper() + '" not found in college records. '
                        "Demo IDs: 2022UMT1234  |  2023UCS0567"
                    )
                    st.rerun()
                else:
                    st.session_state.ward_id       = raw.upper()
                    st.session_state.ward_data     = fetched
                    st.session_state.ward_id_error = ""
                    st.session_state.chat_messages = []
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <p style="text-align:center;font-size:0.65rem;color:rgba(100,116,139,0.45);
                  margin-top:12px;line-height:1.6;">
            Check the admit card or contact the Academic Section for the ID.
        </p>
        """, unsafe_allow_html=True)

        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("Change Role", use_container_width=True, key="btn_guardian_back"):
            st.session_state.user_role     = None
            st.session_state.ward_id_error = ""
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()


# ═════════════════════════════════════════════════════════════════════════════
# ████  SCREEN 4' — GUARDIAN DASHBOARD  ████
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.user_role == "guardian" and st.session_state.ward_data is not None:

    wd          = st.session_state.ward_data
    att_overall = wd["overall_att"]
    att_c       = att_color(att_overall)

    # Top bar
    tb_l, tb_r = st.columns([6, 1])
    with tb_l:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:12px;padding-bottom:4px;">'
            '<div style="width:36px;height:36px;'
            'background:linear-gradient(135deg,#3B82F6,#6D28D9);'
            'border-radius:9px;display:flex;align-items:center;'
            'justify-content:center;font-size:0.95rem;">&#127891;</div>'
            '<span style="font-family:\'Plus Jakarta Sans\',sans-serif;'
            'font-weight:800;font-size:1rem;color:#F1F5F9;">AskMNIT</span>'
            '<span style="margin-left:8px;font-size:0.58rem;'
            'color:#10B981;font-weight:700;">&#9679; Online</span>'
            '<div style="margin-left:8px;padding:3px 11px;'
            'background:rgba(139,92,246,0.10);'
            'border:1px solid rgba(139,92,246,0.28);border-radius:99px;'
            'font-size:0.63rem;font-weight:700;color:#A78BFA;">'
            'Guardian  ' + wd["roll"] + '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with tb_r:
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True, key="guardian_logout"):
            _logout()
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    left_col, right_col = st.columns([1.1, 1], gap="large")

    with left_col:

        # Ward summary card
        status_tag = (
            '<span style="display:inline-flex;align-items:center;gap:5px;'
            'padding:3px 10px;border-radius:999px;background:rgba(16,185,129,0.12);'
            'font-size:0.65rem;font-weight:700;color:#34D399;">'
            '<span style="width:5px;height:5px;border-radius:50%;'
            'background:#34D399;display:inline-block;"></span>'
            + wd["campus_status"] + '</span>'
        )

        info_grid = ""
        for lbl, val in [
            ("Hostel",  wd["hostel_block"]),
            ("Warden",  wd["warden"]),
            ("Contact", wd["warden_phone"]),
            ("Roll No", wd["roll"]),
        ]:
            info_grid += (
                '<div style="background:rgba(255,255,255,0.04);'
                'border-radius:10px;padding:10px 12px;">'
                '<div style="font-size:0.56rem;color:rgba(100,116,139,0.52);'
                'font-weight:700;text-transform:uppercase;'
                'letter-spacing:0.8px;margin-bottom:3px;">' + lbl + '</div>'
                '<div style="font-size:0.73rem;color:#E2E8F0;'
                'font-weight:600;line-height:1.4;">' + val + '</div></div>'
            )

        st.markdown(
            '<div style="background:linear-gradient(160deg,#0D1221,#080C18);'
            'border:1px solid rgba(139,92,246,0.18);border-radius:16px;'
            'padding:20px 22px 18px;margin-bottom:14px;">'
            '<div style="display:flex;align-items:flex-start;gap:14px;margin-bottom:16px;">'
            '<div style="width:54px;height:54px;border-radius:14px;flex-shrink:0;'
            'background:linear-gradient(135deg,#7C3AED,#A78BFA);'
            'display:flex;align-items:center;justify-content:center;'
            'font-size:1.1rem;font-weight:800;color:white;'
            'box-shadow:0 4px 16px rgba(139,92,246,0.25);">'
            + wd["initials"] + '</div>'
            '<div style="flex:1;min-width:0;">'
            '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;'
            'font-weight:800;font-size:1.05rem;color:#F1F5F9;margin-bottom:2px;">'
            + wd["name"] + '</div>'
            '<div style="font-size:0.70rem;color:rgba(148,163,184,0.55);margin-bottom:8px;">'
            + wd["course"] + '  —  ' + wd["semester"] + '</div>'
            + status_tag + '</div></div>'
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:9px;'
            'border-top:1px solid rgba(255,255,255,0.06);padding-top:14px;">'
            + info_grid + '</div></div>',
            unsafe_allow_html=True,
        )

        # Attendance card
        warn_html = ""
        if att_overall < 75:
            warn_html = (
                '<div style="background:rgba(245,158,11,0.08);'
                'border:1px solid rgba(245,158,11,0.22);border-radius:8px;'
                'padding:8px 12px;margin-bottom:12px;font-size:0.71rem;'
                'color:#FCD34D;line-height:1.5;">'
                'Below 75% threshold — exam eligibility may be affected.'
                '</div>'
            )

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
            'justify-content:space-between;margin-bottom:12px;">'
            '<div>'
            '<div style="font-size:2.2rem;font-weight:800;color:' + att_c + ';'
            'letter-spacing:-1px;line-height:1;">' + str(att_overall) + '%</div>'
            '<div style="font-size:0.70rem;color:rgba(148,163,184,0.52);margin-top:4px;">'
            'Overall  —  Last 7 days: '
            '<span style="color:' + att_c + ';font-weight:700;">' + wd["att_7d"] + '</span>'
            '</div></div>'
            + ring_html + '</div>' + warn_html + '</div>',
            unsafe_allow_html=True,
        )

        with st.expander("View Subject-wise Attendance", expanded=False):
            for subj, pct in wd["att_subjects"].items():
                sc  = att_color(pct)
                stc = att_text_color(pct)
                sbg = att_bg_color(pct)
                sb  = att_badge(pct)
                cn, cp = st.columns([4, 1])
                with cn:
                    st.markdown(
                        '<div style="font-size:0.78rem;font-weight:600;color:' + stc + ';'
                        'margin-bottom:3px;">' + subj +
                        '  <span style="font-size:0.56rem;background:' + sbg + ';'
                        'color:' + sc + ';padding:1px 6px;border-radius:4px;">'
                        + sb + '</span></div>',
                        unsafe_allow_html=True,
                    )
                    st.progress(pct / 100)
                with cp:
                    st.markdown(
                        '<div style="text-align:right;font-weight:800;font-size:0.92rem;'
                        'color:' + sc + ';padding-top:2px;">' + str(pct) + '%</div>',
                        unsafe_allow_html=True,
                    )
                st.markdown("<div style='height:3px'></div>", unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # Fee card
        fee_rows = ""
        for item, amt in wd["fee_breakdown"]:
            fee_rows += (
                '<div style="display:flex;justify-content:space-between;'
                'padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);">'
                '<span style="font-size:0.77rem;color:rgba(148,163,184,0.52);">' + item + '</span>'
                '<span style="font-size:0.77rem;font-weight:700;color:#F1F5F9;">' + amt + '</span>'
                '</div>'
            )

        st.markdown(
            '<div style="background:linear-gradient(160deg,#0D1221,#080C18);'
            'border:1px solid rgba(245,158,11,0.18);border-radius:16px;'
            'padding:20px 22px 18px;margin-bottom:14px;">'
            '<div style="font-size:0.60rem;color:rgba(100,116,139,0.52);'
            'font-weight:700;text-transform:uppercase;'
            'letter-spacing:1px;margin-bottom:14px;">'
            'Fee Status  —  ' + wd["fee_semester"] + '</div>'
            '<div style="display:flex;align-items:flex-end;'
            'justify-content:space-between;margin-bottom:16px;">'
            '<div>'
            '<div style="font-size:0.70rem;color:rgba(148,163,184,0.50);margin-bottom:3px;">'
            'Pending Amount</div>'
            '<div style="font-size:2rem;font-weight:800;color:#F59E0B;letter-spacing:-1px;">'
            + wd["fee_pending"] + '</div></div>'
            '<div style="text-align:right;">'
            '<div style="font-size:0.58rem;color:rgba(100,116,139,0.48);margin-bottom:2px;">'
            'Due Date</div>'
            '<div style="font-size:0.88rem;font-weight:700;color:#EF4444;">'
            + wd["fee_due_date"] + '</div></div></div>'
            + fee_rows + '</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="pay-btn">', unsafe_allow_html=True)
        if st.button("Pay Now", use_container_width=True, key="guardian_pay"):
            st.info("Redirecting to MNIT payment gateway — wire the real URL here.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # Notices
        notices_html = ""
        for i, n in enumerate(wd["notices"]):
            notices_html += (
                '<div style="display:flex;gap:10px;padding:9px 12px;'
                'background:rgba(255,255,255,0.03);border-radius:9px;margin-bottom:6px;">'
                '<span style="font-size:0.60rem;color:rgba(100,116,139,0.48);'
                'font-weight:700;flex-shrink:0;">0' + str(i + 1) + '</span>'
                '<span style="font-size:0.76rem;color:rgba(148,163,184,0.65);line-height:1.5;">'
                + n + '</span></div>'
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

        m1, m2, m3 = st.columns(3)
        with m1: st.metric("CGPA", str(wd["cgpa"]) + " / 10", "Current sem")
        with m2: st.metric("Fee Pending", wd["fee_pending"], "Due " + wd["fee_due_date"])
        with m3: st.metric("Attendance", str(att_overall) + "%",
                           "Above 75%" if att_overall >= 75 else "Below 75% Warning")

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
            'Guardian Mode  —  ' + wd["name"] + '</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )

        GUARDIAN_PILLS = [
            "Ward's Attendance",
            "Pay Semester Fees",
            "Hostel Leave Rules",
            "Contact Warden",
            "Academic Calendar",
        ]

        if not st.session_state.chat_messages:
            st.markdown(
                '<div style="text-align:center;padding:28px 16px 20px;opacity:0.55;">'
                '<div style="font-size:2.2rem;margin-bottom:10px;">&#128106;</div>'
                '<div style="font-family:\'Plus Jakarta Sans\',sans-serif;'
                'font-weight:700;font-size:0.9rem;color:#F1F5F9;margin-bottom:6px;">'
                'Ask me about ' + ward_first + "'s academics</div>"
                '<div style="font-size:0.75rem;color:rgba(241,245,249,0.50);'
                'max-width:280px;margin:0 auto;line-height:1.65;">'
                'Attendance, fees, hostel, exams — all here.</div></div>',
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

        if st.session_state.pending_ai and st.session_state.chat_messages:
            last = st.session_state.chat_messages[-1]["content"]
            with st.chat_message("assistant"):
                if client is None:
                    lower = last.lower()
                    if "attendance" in lower:
                        resp = (
                            "**" + wd["name"] + "'s Overall Attendance: " + str(att_overall) + "%**\n"
                            "Last 7 days: " + wd["att_7d"] + ". "
                            + ("⚠️ Below 75% — contact HOD." if att_overall < 75 else "✅ Above minimum.")
                        )
                    elif "fee" in lower or "pay" in lower:
                        resp = (
                            "Pending for " + wd["fee_semester"] + ": **" + wd["fee_pending"]
                            + "**, due **" + wd["fee_due_date"] + "**."
                        )
                    elif "hostel" in lower or "warden" in lower or "leave" in lower:
                        resp = (
                            wd["name"] + " is in **" + wd["hostel_block"] + "**. "
                            "Warden: **" + wd["warden"] + "** — " + wd["warden_phone"] + "."
                        )
                    elif "contact" in lower or "hod" in lower:
                        resp = "Warden: **" + wd["warden"] + "** at " + wd["warden_phone"] + "."
                    elif "exam" in lower:
                        resp = "Next exam: **" + wd["next_exam"] + "**. Full schedule on ERP."
                    else:
                        resp = (
                            "I'm AskMNIT — your guardian assistant for **" + wd["name"] + "**. "
                            "Add `GROQ_API_KEY` to `.streamlit/secrets.toml` for full AI."
                        )
                    st.markdown(resp)
                    response_text = resp
                else:
                    sp = (
                        "You are AskMNIT — helpful AI for MNIT Jaipur, serving a Guardian. "
                        "Ward: " + wd["name"] + ", " + wd["course"] + ", " + wd["semester"]
                        + ". Attendance: " + str(att_overall) + "%. "
                        "Fee: " + wd["fee_pending"] + " due " + wd["fee_due_date"] + ". "
                        "Hostel: " + wd["hostel_block"] + ". Warden: " + wd["warden"]
                        + " " + wd["warden_phone"] + ". "
                        "Answer only about this student. Be concise and warm."
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
                        def _stream_guardian():
                            for chunk in stream:
                                delta = chunk.choices[0].delta.content
                                if delta:
                                    yield delta
                        response_text = st.write_stream(_stream_guardian())
                    except Exception as e:
                        response_text = "Error: " + str(e)
                        st.error(response_text)
                st.session_state.chat_messages.append(
                    {"role": "assistant", "content": response_text}
                )
            st.session_state.pending_ai = False
            st.rerun()

        if prompt := st.chat_input(
            "Ask about " + ward_first + "'s attendance, fees, hostel...",
            key="guardian_chat",
        ):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            st.session_state.pending_ai = True
            st.rerun()

        st.markdown("""
        <p style="text-align:center;font-size:0.61rem;color:rgba(100,116,139,0.38);
                  margin-top:8px;line-height:1.5;">
            AskMNIT can make mistakes. Verify critical info with official admin.
        </p>
        """, unsafe_allow_html=True)

    st.stop()


# ═════════════════════════════════════════════════════════════════════════════
# ████  SCREEN 3" — FRESHER DASHBOARD  ████
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.user_role == "fresher":

    # Top bar
    tb_l, tb_r = st.columns([6, 1])
    with tb_l:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:12px;padding-bottom:4px;">'
            '<div style="width:36px;height:36px;'
            'background:linear-gradient(135deg,#3B82F6,#6D28D9);'
            'border-radius:9px;display:flex;align-items:center;'
            'justify-content:center;font-size:0.95rem;">&#127891;</div>'
            '<span style="font-family:\'Plus Jakarta Sans\',sans-serif;'
            'font-weight:800;font-size:1rem;color:#F1F5F9;">AskMNIT</span>'
            '<span style="margin-left:8px;font-size:0.58rem;'
            'color:#10B981;font-weight:700;">&#9679; Online</span>'
            '<div style="margin-left:8px;padding:3px 11px;'
            'background:rgba(59,130,246,0.10);'
            'border:1px solid rgba(59,130,246,0.28);border-radius:99px;'
            'font-size:0.63rem;font-weight:700;color:#93C5FD;">'
            'Prospective Student</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with tb_r:
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True, key="fresher_logout"):
            _logout()
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    fd = FRESHER_DATA

    # Quick metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Avg Package 2025",  fd["placement_avg"],     "+8% YoY")
    with m2: st.metric("Highest Package",   fd["placement_highest"],  "Amazon 2025")
    with m3: st.metric("Placement Rate",    fd["placement_rate"],     "Batch 2025")
    with m4: st.metric("Fee Per Semester",  fd["fee_per_sem"],        "All inclusive")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    FRESHER_PILLS = [
        "Admission Process 2026",
        "Last Year Cut-offs",
        "Placement Statistics",
        "Campus Life and Hostels",
        "Fee Structure",
        "How to Apply via JoSAA",
    ]

    st.markdown(
        '<p style="color:rgba(241,245,249,0.28);font-size:0.60rem;'
        'letter-spacing:1.5px;text-transform:uppercase;'
        'margin-bottom:8px;font-weight:700;">Ask about MNIT</p>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="pill-zone">', unsafe_allow_html=True)
    pcols = st.columns(len(FRESHER_PILLS))
    for i, label in enumerate(FRESHER_PILLS):
        with pcols[i]:
            if st.button(label, key="fpill_" + str(i), use_container_width=True):
                st.session_state.chat_messages.append({"role": "user", "content": label})
                st.session_state.pending_ai = True
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    if not st.session_state.chat_messages:
        st.markdown("""
        <div style="text-align:center;padding:40px 20px;opacity:0.55;">
            <div style="font-size:2.4rem;margin-bottom:12px;">&#127891;</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;
                        font-size:0.95rem;color:#F1F5F9;margin-bottom:6px;">I'm AskMNIT</div>
            <div style="font-size:0.8rem;color:rgba(241,245,249,0.50);
                        max-width:380px;margin:0 auto;line-height:1.65;">
                Ask me about MNIT admissions, JoSAA cut-offs, placement stats,
                campus life, fee structure, and more.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if st.session_state.pending_ai and st.session_state.chat_messages:
        last = st.session_state.chat_messages[-1]["content"]
        with st.chat_message("assistant"):
            if client is None:
                resp = (
                    "You asked: *" + last + "*\n\n"
                    "Add `GROQ_API_KEY` to `.streamlit/secrets.toml` for full AI responses. "
                    "I can help with JoSAA admissions, cut-offs, fee structure, and placements."
                )
                st.markdown(resp)
                response_text = resp
            else:
                sp = (
                    "You are AskMNIT — a helpful AI for MNIT Jaipur. "
                    "The user is a prospective student exploring MNIT. "
                    "Help with JoSAA, admissions, cut-offs, fee structure (" + fd["fee_per_sem"] + " per sem), "
                    "placement stats (avg " + fd["placement_avg"] + ", highest "
                    + fd["placement_highest"] + ", rate " + fd["placement_rate"] + "), "
                    "campus life, hostels, and branches. Be warm, concise, and accurate."
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
                    def _stream_fresher():
                        for chunk in stream:
                            delta = chunk.choices[0].delta.content
                            if delta:
                                yield delta
                    response_text = st.write_stream(_stream_fresher())
                except Exception as e:
                    response_text = "Error: " + str(e)
                    st.error(response_text)
            st.session_state.chat_messages.append(
                {"role": "assistant", "content": response_text}
            )
        st.session_state.pending_ai = False
        st.rerun()

    if prompt := st.chat_input(
        "Ask about MNIT admissions, placements, cut-offs, campus life...",
        key="fresher_chat",
    ):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        st.session_state.pending_ai = True
        st.rerun()

    st.markdown("""
    <p style="text-align:center;font-size:0.62rem;color:rgba(100,116,139,0.40);
              margin-top:8px;line-height:1.5;">
        AskMNIT can make mistakes. Verify important info with official MNIT sources.
    </p>
    """, unsafe_allow_html=True)
