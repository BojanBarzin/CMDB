import os
import streamlit as st
import streamlit.components.v1 as components


_COMPONENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "barcode_component")
_barcode_component = components.declare_component("fs_live_barcode_scanner", path=_COMPONENT_DIR)


def process_barcode_query_params():
    """Primeni skenirane vrednosti pre crtanja Streamlit widgeta.

    Komponenta vrati skeniranu vrednost u Python, zatim je privremeno čuvamo u
    `<key>__pending_scan`. Na sledećem rerun-u ova funkcija prepisuje vrednost
    u pravi `st.session_state[key]` pre nego što se tekstualno polje nacrta.
    """
    try:
        pending_keys = [k for k in list(st.session_state.keys()) if str(k).endswith("__pending_scan")]
        for pending_key in pending_keys:
            target_key = pending_key.replace("__pending_scan", "")
            value = str(st.session_state.get(pending_key, "")).strip()

            if value:
                st.session_state[target_key] = value

                # Za modul Pretraga: skeniranje odmah pokreće pretragu.
                if target_key.startswith("search_"):
                    st.session_state["search_triggered"] = True
                    if "main_table_key" in st.session_state:
                        st.session_state["main_table_key"] += 1

            del st.session_state[pending_key]
    except Exception:
        pass


def _store_scan_for_next_run(target_key: str, value: str):
    value = str(value or "").strip()
    if not value:
        return

    pending_key = f"{target_key}__pending_scan"
    last_key = f"{target_key}__last_scan"

    # Ne pravimo beskonačan rerun ako je ista vrednost već upisana u isto polje.
    if st.session_state.get(last_key) == value and st.session_state.get(target_key) == value:
        return

    st.session_state[pending_key] = value
    st.session_state[last_key] = value
    st.rerun()


def barcode_scanner(label: str, target_key: str, module_name: str = ""):
    """Jedno kompaktno dugme za live barcode scanner.

    Nema expander-a i nema dodatnog dugmeta 'Pokreni kameru'. Klik na dugme odmah
    otvara kameru. Posle uspešnog čitanja kamera se zatvara i polje se automatski
    popunjava.
    """
    component_key = f"barcode_component_{module_name}_{target_key}".replace(" ", "_").replace("/", "_")

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
    pending_key = f"{key}__pending_scan"
    if pending_key in st.session_state:
        st.session_state[key] = str(st.session_state[pending_key]).strip()
        del st.session_state[pending_key]

    value = st.text_input(label, key=key)
    barcode_scanner(label, key, module_name)
    return value


def barcode_after_field(label: str, key: str, module_name: str = ""):
    pending_key = f"{key}__pending_scan"
    if pending_key in st.session_state:
        st.session_state[key] = str(st.session_state[pending_key]).strip()
        del st.session_state[pending_key]

    barcode_scanner(label, key, module_name)
