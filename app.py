
import os
import sys
import base64
import streamlit as st

st.set_page_config(page_title="CMDB", layout="wide")

BRAND_YELLOW = "#FFD700"
GRAPHITE = "#111111"
LIGHT_GRAY = "#F5F5F5"

def get_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

bg_logo = get_base64("assets/fs_logo_white.png")

st.markdown(f"""
<style>
html, body, [class*="css"] {{
    font-family: 'Nunito Sans', 'Segoe UI', sans-serif;
}}

.stApp {{
    background-color: {LIGHT_GRAY};
    overflow-x: hidden;
}}

.stApp::before {{
    content: "";
    position: fixed;
    inset: -300px;
    background-image: url("data:image/png;base64,{bg_logo}");
    background-size: 340px;
    background-repeat: repeat;
    background-position: 0 0;
    opacity: 0.045;
    transform: rotate(-18deg);
    z-index: 0;
    pointer-events: none;
    animation: bgMove 55s linear infinite;
}}

@keyframes bgMove {{
    from {{ background-position: 0 0; }}
    to {{ background-position: 900px 900px; }}
}}

.block-container {{
    position: relative;
    z-index: 1;
}}

.cmdb-menu {{
    background: rgba(17,17,17,0.96);
    border-left: 10px solid {BRAND_YELLOW};
    border-radius: 18px;
    padding: 20px 28px 14px 28px;
    margin-bottom: 20px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.18);
}}

.cmdb-title {{
    color: white;
    font-size: 34px;
    font-weight: 900;
    margin: 0 0 4px 0;
}}

.cmdb-subtitle {{
    color: #d9d9d9;
    font-size: 15px;
    margin-bottom: 14px;
}}

/* Dugmad za izbor modula */
    div.stButton > button,
    button[kind="secondary"] {{
        background: #111111 !important;
        color: white !important;
        border: 1px solid #FFD700 !important;
        border-radius: 12px !important;
        padding: 0.55rem 1rem !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.20) !important;
    }}

    div.stButton > button:hover,
    button[kind="secondary"]:hover {{
        background: black !important;
        color: #FFD700 !important;
        border: 1px solid #FFD700 !important;
    }}

    div.stButton > button p {{
        color: inherit !important;
        font-weight: 800 !important;
    }}

    input[type="radio"],
    input[type="checkbox"] {{
        accent-color: #FFD700 !important;
    }}
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="cmdb-menu">
    <div class="cmdb-title">CMDB</div>
    <div class="cmdb-subtitle">Izaberi modul za rad</div>
</div>
""", unsafe_allow_html=True)

if "cmdb_main_module" not in st.session_state:
    st.session_state.cmdb_main_module = "PRETRAGA"

menu_cols = st.columns(3)
with menu_cols[0]:
    if st.button("PRETRAGA", use_container_width=True, key="btn_pretraga"):
        st.session_state.cmdb_main_module = "PRETRAGA"
with menu_cols[1]:
    if st.button("UNOS", use_container_width=True, key="btn_unos"):
        st.session_state.cmdb_main_module = "UNOS"
with menu_cols[2]:
    if st.button("PRI-OTP SA TERENA", use_container_width=True, key="btn_pri_otp"):
        st.session_state.cmdb_main_module = "PRI-OTP SA TERENA"

module = st.session_state.cmdb_main_module
st.caption(f"Aktivan modul: {module}")

MODULES = {
    "PRETRAGA": ("modules/pretraga", "_module_app.py"),
    "UNOS": ("modules/unos", "_module_app.py"),
    "PRI-OTP SA TERENA": ("modules/pri_otp", "_module_app.py"),
}

def run_module(module_dir, module_file):
    root_dir = os.getcwd()
    abs_dir = os.path.join(root_dir, module_dir)
    abs_file = os.path.join(abs_dir, module_file)

    if not os.path.exists(abs_file):
        st.error(f"Nije pronađen modul: {abs_file}")
        return

    # Da bi postojeći kodovi ostali isti, svaki modul se izvršava iz svog foldera.
    old_cwd = os.getcwd()
    old_path = list(sys.path)

    try:
        os.chdir(abs_dir)
        if abs_dir not in sys.path:
            sys.path.insert(0, abs_dir)

        namespace = {
            "__name__": f"cmdb_module_{module_file}",
            "__file__": abs_file,
        }

        with open(abs_file, "r", encoding="utf-8") as f:
            code = compile(f.read(), abs_file, "exec")

        exec(code, namespace)

    finally:
        os.chdir(old_cwd)
        sys.path = old_path

module_dir, module_file = MODULES[module]
run_module(module_dir, module_file)
