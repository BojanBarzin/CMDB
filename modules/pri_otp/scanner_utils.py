import json
import time
import streamlit as st
import streamlit.components.v1 as components


def process_barcode_query_params():
    """Preuzmi vrednost koju html5-qrcode vrati kroz URL i upiši je u session_state PRE crtanja widgeta."""
    try:
        target = st.query_params.get("barcode_target", "")
        value = st.query_params.get("barcode_value", "")
        module = st.query_params.get("module", "")

        if isinstance(target, list):
            target = target[0] if target else ""
        if isinstance(value, list):
            value = value[0] if value else ""
        if isinstance(module, list):
            module = module[0] if module else ""

        target = str(target).strip()
        value = str(value).strip()
        module = str(module).strip()

        if target and value:
            st.session_state[target] = value

            if target.startswith("search_"):
                st.session_state["search_triggered"] = True

            st.query_params.clear()
            if module:
                st.query_params["module"] = module

            st.rerun()
    except Exception:
        pass


def barcode_scanner(label: str, target_key: str, module_name: str = ""):
    """Live barcode scanner preko html5-qrcode.

    Napomena: Streamlit Cloud pokreće components.html u iframe-u. Automatsko menjanje parent URL-a
    često bude blokirano na Android/Chrome zbog browser security pravila. Zato skener nakon čitanja
    prikaže dugme "Upiši u polje" koje korisnik klikne; to je user-gesture i pouzdano upisuje vrednost.
    """
    unique_id = f"scanner_{target_key}_{int(time.time() * 1000)}".replace(" ", "_").replace("/", "_").replace("-", "_")
    target_js = json.dumps(target_key)
    module_js = json.dumps(module_name)
    label_safe = label.replace("<", "&lt;").replace(">", "&gt;")

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
<style>
    body {{
        margin: 0;
        padding: 0;
        font-family: Arial, sans-serif;
        background: transparent;
    }}
    .scan-wrap {{
        background: #ffffff;
        border: 1px solid #d0d0d0;
        border-radius: 12px;
        padding: 10px;
        box-sizing: border-box;
    }}
    .scan-title {{
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 8px;
        color: #111111;
    }}
    .scan-actions {{
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 8px;
    }}
    button, .fill-link {{
        display: inline-block;
        text-decoration: none;
        background: #111111;
        color: white !important;
        border: 1px solid #111111;
        border-radius: 10px;
        padding: 8px 12px;
        font-weight: 700;
        cursor: pointer;
        font-size: 13px;
    }}
    button:hover, .fill-link:hover {{
        background: black;
        color: #FFD700 !important;
        border-color: #FFD700;
    }}
    .fill-link {{
        background: #FFD700;
        color: #111111 !important;
        border-color: #FFD700;
        margin-top: 8px;
    }}
    #reader-{unique_id} {{
        width: 100%;
        max-width: 360px;
        min-height: 0px;
    }}
    .msg {{
        color: #333;
        font-size: 12px;
        margin-top: 6px;
        word-break: break-word;
    }}
    .result-box {{
        display: none;
        margin-top: 10px;
        padding: 10px;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        background: #f7f7f7;
    }}
    .result-value {{
        font-family: Consolas, monospace;
        font-size: 14px;
        font-weight: 700;
        color: #111111;
        word-break: break-all;
        margin-bottom: 6px;
    }}
</style>
</head>
<body>
<div class="scan-wrap">
    <div class="scan-title">📷 Skener za: {label_safe}</div>
    <div class="scan-actions">
        <button type="button" onclick="startScan()">Pokreni kameru</button>
        <button type="button" onclick="stopScan()">Zaustavi</button>
    </div>
    <div id="reader-{unique_id}"></div>
    <div id="msg-{unique_id}" class="msg">Podržava Code128, Code39, EAN i QR.</div>
    <div id="result-{unique_id}" class="result-box">
        <div>Pročitano:</div>
        <div id="value-{unique_id}" class="result-value"></div>
        <a id="fill-{unique_id}" class="fill-link" href="#" target="_top">Upiši u polje</a>
    </div>
</div>
<script>
let html5QrCode_{unique_id} = null;
let running_{unique_id} = false;
let alreadyRead_{unique_id} = false;

function getTopUrl() {{
    try {{
        return window.top.location.href;
    }} catch (e) {{
        return document.referrer || window.location.href;
    }}
}}

function buildTargetUrl(value) {{
    const target = {target_js};
    const moduleName = {module_js};
    const topUrl = getTopUrl();
    const hashSplit = topUrl.split('#');
    const beforeHash = hashSplit[0];
    const hash = hashSplit.length > 1 ? '#' + hashSplit.slice(1).join('#') : '';
    const parts = beforeHash.split('?');
    const base = parts[0];
    const params = new URLSearchParams(parts.length > 1 ? parts.slice(1).join('?') : '');

    if (moduleName) params.set('module', moduleName);
    params.set('barcode_target', target);
    params.set('barcode_value', value);
    params.set('barcode_nonce', Date.now().toString());

    return base + '?' + params.toString() + hash;
}}

function showFillButton(value) {{
    const url = buildTargetUrl(value);
    document.getElementById('value-{unique_id}').innerText = value;
    const link = document.getElementById('fill-{unique_id}');
    link.href = url;
    document.getElementById('result-{unique_id}').style.display = 'block';
    document.getElementById('msg-{unique_id}').innerText = 'Barkod je pročitan. Klikni "Upiši u polje".';
}}

function tryAutoRedirect(value) {{
    // Pokušaj automatski, ali na Android/Chrome unutar iframe-a često bude blokirano.
    // Zato dugme ostaje vidljivo kao siguran fallback.
    const url = buildTargetUrl(value);
    try {{
        window.top.location.assign(url);
    }} catch (e) {{
        try {{ window.parent.location.assign(url); }} catch (e2) {{}}
    }}
}}

function onScanSuccess(decodedText, decodedResult) {{
    const clean = (decodedText || '').trim();
    if (!clean || alreadyRead_{unique_id}) return;

    alreadyRead_{unique_id} = true;
    document.getElementById('msg-{unique_id}').innerText = 'Pročitano: ' + clean;
    stopScan().then(() => {{
        showFillButton(clean);
        setTimeout(() => tryAutoRedirect(clean), 150);
    }});
}}

function startScan() {{
    if (running_{unique_id}) return;
    alreadyRead_{unique_id} = false;
    document.getElementById('result-{unique_id}').style.display = 'none';
    const readerId = 'reader-{unique_id}';
    html5QrCode_{unique_id} = new Html5Qrcode(readerId, false);
    const config = {{
        fps: 12,
        qrbox: {{ width: 260, height: 120 }},
        aspectRatio: 1.777,
        formatsToSupport: [
            Html5QrcodeSupportedFormats.CODE_128,
            Html5QrcodeSupportedFormats.CODE_39,
            Html5QrcodeSupportedFormats.EAN_13,
            Html5QrcodeSupportedFormats.EAN_8,
            Html5QrcodeSupportedFormats.QR_CODE
        ]
    }};

    Html5Qrcode.getCameras().then(cameras => {{
        if (!cameras || cameras.length === 0) {{
            document.getElementById('msg-{unique_id}').innerText = 'Kamera nije pronađena.';
            return;
        }}
        let cameraId = cameras[0].id;
        for (const cam of cameras) {{
            const label = (cam.label || '').toLowerCase();
            if (label.includes('back') || label.includes('rear') || label.includes('environment')) {{
                cameraId = cam.id;
                break;
            }}
        }}
        html5QrCode_{unique_id}.start(cameraId, config, onScanSuccess, () => {{}})
            .then(() => {{
                running_{unique_id} = true;
                document.getElementById('msg-{unique_id}').innerText = 'Kamera je aktivna. Uperi u barkod.';
            }})
            .catch(err => {{
                document.getElementById('msg-{unique_id}').innerText = 'Ne mogu da otvorim kameru: ' + err;
            }});
    }}).catch(err => {{
        document.getElementById('msg-{unique_id}').innerText = 'Greška pri čitanju kamera: ' + err;
    }});
}}

async function stopScan() {{
    if (html5QrCode_{unique_id} && running_{unique_id}) {{
        try {{
            await html5QrCode_{unique_id}.stop();
            await html5QrCode_{unique_id}.clear();
        }} catch(e) {{}}
        running_{unique_id} = false;
    }}
}}
</script>
</body>
</html>
"""

    with st.expander(f"📷 Skeniraj {label}", expanded=False):
        components.html(html, height=430, scrolling=False)

def barcode_text_input(label: str, key: str, module_name: str = ""):
    value = st.text_input(label, key=key)
    barcode_scanner(label, key, module_name)
    return value


def barcode_after_field(label: str, key: str, module_name: str = ""):
    barcode_scanner(label, key, module_name)
