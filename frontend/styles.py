DESIGN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    background: #101010 !important;
    color: #f2f2f2 !important;
}
.stApp { background: #101010; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #101010 !important;
    border-right: 1px solid #3d3a39 !important;
}
[data-testid="stSidebar"] * { color: #f2f2f2 !important; }

/* ── Hide default Streamlit chrome ── */
header, footer, #MainMenu { visibility: hidden; }
[data-testid="stHeader"] { background: #101010 !important; }
.block-container { padding-top: 1.5rem !important; }

/* ── Chat messages ── */
div[data-testid="stChatMessage"] {
    background: #1a1a1a !important;
    border: 1px solid #3d3a39 !important;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
}
div[data-testid="stChatMessage"] * { color: #f2f2f2 !important; }

/* ── Chat input ── */
div[data-testid="stChatInput"] {
    background: #1a1a1a !important;
    border-top: 1px solid #3d3a39 !important;
}
div[data-testid="stChatInput"] textarea {
    background: #1a1a1a !important;
    color: #f2f2f2 !important;
    border: 1px solid #3d3a39 !important;
    border-radius: 6px;
    font-family: 'Inter', sans-serif !important;
}

/* ── Text inputs (login) ── */
.stTextInput input {
    background: #1a1a1a !important;
    color: #f2f2f2 !important;
    border: 1px solid #3d3a39 !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    padding: 12px 16px !important;
}
.stTextInput input:focus {
    border-color: #00d992 !important;
    box-shadow: none !important;
}
.stTextInput label { color: #bdbdbd !important; font-size: 14px !important; }

/* ── Primary button (green) ── */
.stButton > button[kind="primary"],
button[data-testid="baseButton-primary"] {
    background: #00d992 !important;
    color: #101010 !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    padding: 12px 16px !important;
    width: 100% !important;
    font-family: 'Inter', sans-serif !important;
    transition: opacity 0.15s ease;
}
.stButton > button[kind="primary"]:hover { opacity: 0.85 !important; }

/* ── Secondary / ghost buttons ── */
.stButton > button {
    background: #101010 !important;
    color: #f2f2f2 !important;
    border: 1px solid #3d3a39 !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    transition: border-color 0.15s ease;
}
.stButton > button:hover {
    border-color: #00d992 !important;
    color: #00d992 !important;
}

/* ── Active session button highlight ── */
button.active-session {
    border-color: #00d992 !important;
    color: #00d992 !important;
}

/* ── Role badge pill ── */
.role-pill {
    display: inline-block;
    background: #101010;
    color: #f2f2f2;
    border: 1px solid #3d3a39;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 600;
    padding: 4px 12px;
    letter-spacing: 0.5px;
}
.role-pill span { color: #00d992; }

/* ── Divider ── */
.green-divider {
    border: none;
    border-top: 1px solid #3d3a39;
    margin: 12px 0;
}

/* ── Sidebar section label ── */
.sidebar-label {
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 2.52px;
    text-transform: uppercase;
    color: #8b949e;
    margin: 16px 0 8px 0;
}

/* ── Error/info text ── */
.err-text { color: #ff4b4b !important; font-size: 13px; }
.mute-text { color: #8b949e; font-size: 13px; }
</style>
"""

ROLES = [
    "C-Level Executives",
    "Finance Manager",
    "Risk Analyst",
    "Compliance Officer",
    "Operations Manager",
    "Data Analyst",
]

BACKEND_URL = "http://localhost:8000"