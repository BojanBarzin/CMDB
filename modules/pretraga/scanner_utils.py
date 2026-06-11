import os
import time
import streamlit as st
import streamlit.components.v1 as components


_COMPONENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "barcode_component")
_barcode_component = components.declare_component("fs_live_barcode_scanner", path=_COMPONENT_DIR)


def process_barcode_query_params():
    """Primeni skenirane vrednosti pre crtanja Streamlit widgeta.

    Ime je zadržano zbog postojećih import-a u modulima. Više ne koristimo URL query parametre,
    već custom Streamlit komponentu koja vraća vrednost u Python, pa se ona prvo smešta u
    `<key>__pending`, a na sledećem rerun-u ovde prepisuje u pravo polje.
    """
    try:
        pending_keys = [k for k in list(st.session_state.keys()) if str(k).endswith("__pending_scan")]
        for pending_key in pending_keys:
            target_key = pending_key.replace("__pending_scan", "")
            value = str(st.session_state.get(pending_key, "")).strip()

            if value:
                st.session_state[target_key] = value

                if target_key.startswith("search_"):
                    st.session_state["search_triggered"] = True

            del st.session_state[pending_key]
    except Exception:
        pass


def _store_scan_for_next_run(target_key: str, value: str):
    value = str(value or "").strip()
    if not value:
        return

    pending_key = f"{target_key}__pending_scan"
    last_key = f"{target_key}__last_scan"

    # Ako komponenta vrati istu vrednost više puta u istom ciklusu, ne pravimo beskonačan rerun.
    if st.session_state.get(last_key) == value and st.session_state.get(target_key) == value:
        return

    st.session_state[pending_key] = value
    st.session_state[last_key] = value
    st.rerun()


def barcode_scanner(label: str, target_key: str, module_name: str = ""):
    """Live barcode scanner preko html5-qrcode custom komponente.

    Ovo nije `components.html` workaround. Komponenta direktno vraća skeniranu vrednost u Python
    preko Streamlit component protocol-a, pa se polje automatski popunjava bez dugmeta 'Upiši'.
    """
    component_key = f"barcode_component_{module_name}_{target_key}".replace(" ", "_").replace("/", "_")

    with st.expander(f"📷 Skeniraj {label}", expanded=False):
        scanned_value = _barcode_component(
            label=label,
            target_key=target_key,
            component_key=component_key,
            default="",
            key=component_key,
        )

        if scanned_value:
            _store_scan_for_next_run(target_key, scanned_value)


def barcode_text_input(label: str, key: str, module_name: str = ""):
    # Pending vrednosti se inače obrađuju na početku modula, ali ovo ostaje kao dodatna zaštita.
    pending_key = f"{key}__pending_scan"
    if pending_key in st.session_state:
        st.session_state[key] = str(st.session_state[pending_key]).strip()
        del st.session_state[pending_key]

    value = st.text_input(label, key=key)
    barcode_scanner(label, key, module_name)
    return value


def barcode_after_field(label: str, key: str, module_name: str = ""):
    barcode_scanner(label, key, module_name)
