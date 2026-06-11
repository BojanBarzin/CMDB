import os
import sys
import base64
import streamlit as st

st.set_page_config(page_title="CMDB", layout="wide")

APP_VERSION = "CMDB spojena app v6 - BUTTON MENU"
BRAND_YELLOW = "#FFD700"
GRAPHITE = "#111111"
LIGHT_GRAY = "#F5F5F5"

MODULES = {
    "PRETRAGA": ("modules/pretraga", "_module_app.py"),
    "UNOS": ("modules/unos", "_module_app.py"),
    "PRI-OTP SA TERENA": ("modules/pri_otp", "_module_app.py"),
}


def get_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""


def init_state():
    if "cmdb_active_module" not in st.session_state:
        st.session_state.cmdb_active_module = "PRETRAGA"

    if st.session_state.cmdb_active_module not in MODULES:
        st.session_state.cmdb_active_module = "PRETRAGA"


bg_logo = get_base64("assets/fs_logo_white.png")
init_state()


def inject_global_style(current_module):
    max_width = "980px" if current_module == "UNOS" else "100%"
    pad_x = "2rem" if current_module == "UNOS" else "2.5rem"

    st.markdown(
        f"""
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
    padding-top: 1.4rem !important;
    max-width: {max_width} !important;
    padding-left: {pad_x} !important;
    padding-right: {pad_x} !important;
}}

.cmdb-shell {{
    background: rgba(17,17,17,0.97);
    border-left: 10px solid {BRAND_YELLOW};
    border-radius: 18px;
    padding: 20px 28px;
    margin-bottom: 16px;
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
    margin-bottom: 8px;
}}

.cmdb-active-module {{
    display: inline-block;
    color: black;
    background: {BRAND_YELLOW};
    border-radius: 999px;
    font-weight: 900;
    padding: 5px 14px;
    margin: 0 0 18px 0;
    font-size: 13px;
}}

.cmdb-version {{
    color: #777;
    font-size: 11px;
    margin-top: -8px;
    margin-bottom: 12px;
}}

/* SVA STREAMLIT DUGMAD */
div.stButton > button,
button[kind="secondary"],
[data-testid="stNumberInput"] button,
[data-testid="stNumberInput"] div button {{
    background: {GRAPHITE} !important;
    color: white !important;
    border: 1px solid {BRAND_YELLOW} !important;
    border-radius: 10px !important;
    font-weight: 800 !important;
}}

div.stButton > button:hover,
button[kind="secondary"]:hover,
[data-testid="stNumberInput"] button:hover,
[data-testid="stNumberInput"] div button:hover {{
    background: black !important;
    color: {BRAND_YELLOW} !important;
    border: 1px solid {BRAND_YELLOW} !important;
}}

div.stButton > button p {{
    color: inherit !important;
    font-weight: 800 !important;
}}

/* Ako neki modul ima radio/checkbox, nikad crveno */
input[type="radio"],
input[type="checkbox"] {{
    accent-color: {BRAND_YELLOW} !important;
}}

.stTextInput input,
.stNumberInput input,
.stDateInput input {{
    background-color: white !important;
    color: black !important;
    border: 1px solid #d0d0d0 !important;
    border-radius: 10px !important;
}}

div[data-baseweb="select"] > div {{
    background-color: white !important;
    color: black !important;
    border-radius: 10px !important;
    border: 1px solid #d0d0d0 !important;
}}

.stDownloadButton > button {{
    background: {BRAND_YELLOW} !important;
    color: black !important;
    border-radius: 10px !important;
    font-weight: 900 !important;
    border: none !important;
}}
</style>
""",
        unsafe_allow_html=True,
    )


def render_header():
    current_module = st.session_state.cmdb_active_module

    st.markdown(
        f"""
<div class="cmdb-shell">
    <div class="cmdb-title">CMDB</div>
    <div class="cmdb-subtitle">Izaberi modul za rad</div>
</div>
<div class="cmdb-version">{APP_VERSION}</div>
""",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("PRETRAGA", use_container_width=True, key="cmdb_btn_pretraga"):
            st.session_state.cmdb_active_module = "PRETRAGA"
            st.rerun()

    with c2:
        if st.button("UNOS", use_container_width=True, key="cmdb_btn_unos"):
            st.session_state.cmdb_active_module = "UNOS"
            st.rerun()

    with c3:
        if st.button("PRI-OTP SA TERENA", use_container_width=True, key="cmdb_btn_pri_otp"):
            st.session_state.cmdb_active_module = "PRI-OTP SA TERENA"
            st.rerun()

    st.markdown(
        f'<div class="cmdb-active-module">Aktivan modul: {current_module}</div>',
        unsafe_allow_html=True,
    )


def run_module(module_dir, module_file):
    root_dir = os.getcwd()
    abs_dir = os.path.join(root_dir, module_dir)
    abs_file = os.path.join(abs_dir, module_file)

    if not os.path.exists(abs_file):
        st.error(f"Nije pronađen modul: {abs_file}")
        return

    old_cwd = os.getcwd()
    old_path = list(sys.path)

    try:
        os.chdir(abs_dir)
        if abs_dir not in sys.path:
            sys.path.insert(0, abs_dir)

        namespace = {
            "__name__": f"cmdb_module_{module_dir.replace('/', '_')}",
            "__file__": abs_file,
        }

        with open(abs_file, "r", encoding="utf-8") as f:
            code = compile(f.read(), abs_file, "exec")

        exec(code, namespace)

    finally:
        os.chdir(old_cwd)
        sys.path = old_path


module = st.session_state.cmdb_active_module
inject_global_style(module)
render_header()

module_dir, module_file = MODULES[module]
run_module(module_dir, module_file)

# CSS opet posle modula, da modul ne pregazi dugmad i širinu.
inject_global_style(st.session_state.cmdb_active_module)
