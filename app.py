import os
import sys
import base64
import streamlit as st

st.set_page_config(page_title="CMDB", layout="wide")

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


bg_logo = get_base64("assets/fs_logo_white.png")

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
    padding-top: 1.4rem;
}}

.cmdb-menu {{
    background: rgba(17,17,17,0.97);
    border-left: 10px solid {BRAND_YELLOW};
    border-radius: 18px;
    padding: 20px 28px 20px 28px;
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

.cmdb-active-module {{
    display: inline-block;
    color: #111111;
    background: {BRAND_YELLOW};
    border-radius: 999px;
    font-weight: 900;
    padding: 5px 14px;
    margin-top: 10px;
    font-size: 13px;
}}

/* Glavna dugmad za izbor modula + Streamlit dugmad */
div.stButton > button,
button[kind="secondary"] {{
    background: {GRAPHITE} !important;
    color: white !important;
    border: 1px solid {BRAND_YELLOW} !important;
    border-radius: 12px !important;
    padding: 0.58rem 1rem !important;
    font-weight: 900 !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.18) !important;
}}

div.stButton > button:hover,
button[kind="secondary"]:hover {{
    background: black !important;
    color: {BRAND_YELLOW} !important;
    border: 1px solid {BRAND_YELLOW} !important;
}}

div.stButton > button p {{
    color: inherit !important;
    font-weight: 900 !important;
}}

/* Ne koristimo radio za izbor modula. Ako ga Streamlit/tema negde prikaže, ne sme biti crven. */
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

st.markdown(
    """
<div class="cmdb-menu">
    <div class="cmdb-title">CMDB</div>
    <div class="cmdb-subtitle">Izaberi modul za rad</div>
</div>
""",
    unsafe_allow_html=True,
)

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
st.markdown(f'<div class="cmdb-active-module">Aktivan modul: {module}</div>', unsafe_allow_html=True)

# UNOS treba da ostane centralan/uzak kao ranije. Ostali moduli ostaju wide.
if module == "UNOS":
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 980px !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 100% !important;
            padding-left: 2.5rem !important;
            padding-right: 2.5rem !important;
        }
        </style>
        """,
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


module_dir, module_file = MODULES[module]
run_module(module_dir, module_file)
