import os
import sys
import base64
from urllib.parse import quote
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


def get_query_module():
    try:
        module = st.query_params.get("module", "PRETRAGA")
    except Exception:
        module = "PRETRAGA"

    if isinstance(module, list):
        module = module[0] if module else "PRETRAGA"

    if module not in MODULES:
        module = "PRETRAGA"

    return module


bg_logo = get_base64("assets/fs_logo_white.png")
module = get_query_module()


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

.cmdb-menu {{
    background: rgba(17,17,17,0.97);
    border-left: 10px solid {BRAND_YELLOW};
    border-radius: 18px;
    padding: 20px 28px;
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
    margin-bottom: 16px;
}}

.cmdb-buttons {{
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}}

.cmdb-module-btn,
.cmdb-module-btn:visited {{
    display: inline-block;
    text-decoration: none !important;
    background: {GRAPHITE};
    color: white !important;
    border: 1px solid {BRAND_YELLOW};
    border-radius: 12px;
    padding: 11px 22px;
    font-weight: 900;
    letter-spacing: .2px;
    min-width: 185px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.18);
}}

.cmdb-module-btn:hover {{
    background: black;
    color: {BRAND_YELLOW} !important;
    border: 1px solid {BRAND_YELLOW};
}}

.cmdb-module-btn.active {{
    background: {BRAND_YELLOW};
    color: black !important;
    border: 1px solid {BRAND_YELLOW};
}}

.cmdb-active-module {{
    display: inline-block;
    color: #111111;
    background: {BRAND_YELLOW};
    border-radius: 999px;
    font-weight: 900;
    padding: 5px 14px;
    margin: 0 0 18px 0;
    font-size: 13px;
}}

/* Modul dugmad i sva obična dugmad */
div.stButton > button,
button[kind="secondary"],
[data-testid="stNumberInput"] button,
[data-testid="stNumberInput"] div button {{
    background: {GRAPHITE} !important;
    color: white !important;
    border: 1px solid {GRAPHITE} !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
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
}}

/* Ako neki modul ipak ima radio/checkbox, boja ne sme biti crvena */
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


inject_global_style(module)

buttons_html = ""
for name in MODULES:
    active = " active" if name == module else ""
    buttons_html += f'<a class="cmdb-module-btn{active}" href="?module={quote(name)}" target="_self">{name}</a>'

st.markdown(
    f"""
<div class="cmdb-menu">
    <div class="cmdb-title">CMDB</div>
    <div class="cmdb-subtitle">Izaberi modul za rad</div>
    <div class="cmdb-buttons">{buttons_html}</div>
</div>
<div class="cmdb-active-module">Aktivan modul: {module}</div>
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

# Finalni CSS ide POSLE modula, da modul ne pregazi izgled glavnih dugmadi i širinu UNOS-a.
inject_global_style(module)
