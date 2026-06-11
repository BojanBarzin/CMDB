import os
import streamlit as st
import streamlit.components.v1 as components


_COMPONENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "barcode_component")
_barcode_component = components.declare_component("fs_live_barcode_scanner", path=_COMPONENT_DIR)


def process_barcode_query_params():
    """Primeni skenirane vrednosti pre crtanja Streamlit widgeta.

    Komponenta vraća događaj skeniranja u obliku {value, scan_id}. Vrednost se
    prvo čuva u `<key>__pending_scan`, pa se na sledećem rerun-u upisuje u pravi
    `st.session_state[key]` pre crtanja tekstualnog polja.
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


def clear_barcode_field(target_key: str):
    """Obriši polje i sve pomoćne scan vrednosti.

    Ovo rešava problem da se poslednji skenirani barkod ponovo vrati u polje
    nakon ručnog brisanja.
    """
    st.session_state[target_key] = ""

    prefixes = [
        f"{target_key}__pending_scan",
        f"{target_key}__last_scan",
        f"{target_key}__processed_scan_id",
    ]
    for k in prefixes:
        if k in st.session_state:
            del st.session_state[k]

    if target_key.startswith("search_"):
        st.session_state["search_triggered"] = False
        if "main_table_key" in st.session_state:
            st.session_state["main_table_key"] += 1


def _store_scan_for_next_run(target_key: str, value: str):
    value = str(value or "").strip()
    if not value:
        return

    pending_key = f"{target_key}__pending_scan"
    st.session_state[pending_key] = value
    st.rerun()


def _extract_scan_event(result):
    """Vrati (value, scan_id) iz rezultata komponente.

    Stara verzija komponente vraćala je običan string. Nova vraća dict sa
    jedinstvenim scan_id, kako se isti barkod ne bi ponovo upisivao posle ručnog
    brisanja polja.
    """
    if isinstance(result, dict):
        value = str(result.get("value", "") or "").strip()
        scan_id = str(result.get("scan_id", "") or "").strip()
        return value, scan_id

    if isinstance(result, str):
        value = result.strip()
        # Fallback za stare komponente: bez event id-a.
        return value, f"legacy::{value}"

    return "", ""


def barcode_scanner(label: str, target_key: str, module_name: str = ""):
    """Jedno kompaktno dugme za live barcode scanner.

    Klik na dugme odmah otvara kameru. Posle uspešnog čitanja kamera se zatvara,
    okvir skenera se skloni i polje se automatski popunjava.
    """
    component_key = f"barcode_component_{module_name}_{target_key}".replace(" ", "_").replace("/", "_")

    scanned_result = _barcode_component(
        label=label,
        target_key=target_key,
        component_key=component_key,
        default=None,
        key=component_key,
    )

    value, scan_id = _extract_scan_event(scanned_result)
    if value and scan_id:
        processed_key = f"{target_key}__processed_scan_id"
        if st.session_state.get(processed_key) != scan_id:
            st.session_state[processed_key] = scan_id
            st.session_state[f"{target_key}__last_scan"] = value
            _store_scan_for_next_run(target_key, value)


def field_has_value(key: str) -> bool:
    return bool(str(st.session_state.get(key, "") or "").strip())


def clear_button_for_field(label: str, key: str):
    st.button(
        "✕ Obriši",
        key=f"clear_{key}",
        help=f"Obriši polje: {label}",
        use_container_width=True,
        on_click=clear_barcode_field,
        args=(key,),
    )


def barcode_text_input(label: str, key: str, module_name: str = ""):
    pending_key = f"{key}__pending_scan"
    if pending_key in st.session_state:
        st.session_state[key] = str(st.session_state[pending_key]).strip()
        del st.session_state[pending_key]

    value = st.text_input(label, key=key)

    # Samo skener dugme. Polje može ručno da se obriše bez posebnog dugmeta.
    barcode_scanner(label, key, module_name)

    return value


def barcode_after_field(label: str, key: str, module_name: str = ""):
    pending_key = f"{key}__pending_scan"
    if pending_key in st.session_state:
        st.session_state[key] = str(st.session_state[pending_key]).strip()
        del st.session_state[pending_key]

    # Samo skener dugme. Polje može ručno da se obriše bez posebnog dugmeta.
    barcode_scanner(label, key, module_name)
