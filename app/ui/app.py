import os

import streamlit as st
import httpx

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="DocIntellect RPA",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main > div { padding: 0 1rem; }
    .doc-card {
        background: #1e1e2e; border: 1px solid #313244;
        border-radius: 12px; padding: 1rem; margin-bottom: 0.75rem;
    }
    .doc-card .name { color: #cdd6f4; font-size: 0.9rem; font-weight: 600; }
    .doc-card .meta { color: #6c7086; font-size: 0.75rem; margin-top: 0.25rem; }
    .status-badge {
        display: inline-block; font-size: 0.65rem; padding: 0.1rem 0.5rem;
        border-radius: 99px; font-weight: 600; margin-top: 0.3rem;
    }
    .badge-completed { background: #a6e3a1; color: #1e1e2e; }
    .badge-processing { background: #f9e2af; color: #1e1e2e; }
    .badge-failed { background: #f38ba8; color: #1e1e2e; }
    .badge-uploaded { background: #94e2d5; color: #1e1e2e; }
    .result-header {
        display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;
        margin-bottom: 1.5rem; padding-bottom: 1rem;
        border-bottom: 1px solid #313244;
    }
    .doc-type-badge {
        background: #89b4fa; color: #1e1e2e;
        font-size: 0.8rem; font-weight: 700; padding: 0.25rem 0.75rem;
        border-radius: 99px; text-transform: uppercase; letter-spacing: 0.5px;
    }
    .conf-bar {
        height: 6px; border-radius: 3px; background: #313244; margin-top: 4px;
    }
    .conf-bar-fill { height: 100%; border-radius: 3px; background: #a6e3a1; }
    .field-card {
        background: #181825; border: 1px solid #313244;
        border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 0.5rem;
        display: flex; justify-content: space-between; align-items: center;
    }
    .field-card .label { color: #a6adc8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; }
    .field-card .value { color: #cdd6f4; font-size: 1rem; font-weight: 600; font-family: monospace; }
    .field-card .conf { font-size: 0.75rem; color: #6c7086; }
    .section-header {
        color: #89b4fa; font-size: 1.1rem; font-weight: 700;
        margin: 1.5rem 0 0.75rem; padding-bottom: 0.25rem;
        border-bottom: 1px solid #313244;
    }
    .kv-grid {
        display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;
        margin-bottom: 1rem;
    }
    .kv-item {
        background: #181825; border: 1px solid #313244;
        border-radius: 8px; padding: 0.5rem 0.75rem;
    }
    .kv-item .k { color: #6c7086; font-size: 0.7rem; text-transform: uppercase; }
    .kv-item .v { color: #cdd6f4; font-size: 0.9rem; font-weight: 600; }
    .review-banner {
        background: #f38ba8; color: #1e1e2e; padding: 0.5rem 1rem;
        border-radius: 8px; font-weight: 600; font-size: 0.85rem; margin-bottom: 1rem;
    }
    .empty-state { text-align: center; padding: 4rem 2rem; color: #6c7086; }
    .empty-state h3 { color: #cdd6f4; margin-bottom: 0.5rem; }
    table.doc-table {
        width: 100%; border-collapse: collapse; margin: 0.5rem 0 1rem;
        font-size: 0.85rem;
    }
    table.doc-table th {
        background: #313244; color: #cdd6f4; font-weight: 600;
        padding: 0.5rem 0.75rem; text-align: left; border: 1px solid #45475a;
    }
    table.doc-table td {
        padding: 0.4rem 0.75rem; border: 1px solid #313244; color: #a6adc8;
    }
    table.doc-table tr:nth-child(even) td { background: #181825; }
    .block-paragraph { color: #cdd6f4; line-height: 1.6; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)


def format_bytes(size: int) -> str:
    for unit in ("B", "KB", "MB"):
        if size < 1024:
            return f"{size:.0f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def render_field_card(field: dict):
    conf = field.get("confidence", 0)
    method = field.get("extraction_method", "ocr").upper()
    st.markdown(f"""
    <div class="field-card">
        <div>
            <div class="label">{field.get("field_name", "")} \u00b7 {method}</div>
            <div class="value">{field.get("field_value", "\u2014")}</div>
        </div>
        <div style="text-align:right;min-width:80px">
            <div class="conf">{conf:.0%}</div>
            <div class="conf-bar"><div class="conf-bar-fill" style="width:{conf*100}%"></div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_table(table: dict):
    headers = table.get("headers", [])
    rows = table.get("rows", [])
    if not headers and not rows:
        return
    html = "<table class='doc-table'><thead><tr>"
    for h in headers:
        html += f"<th>{h}</th>"
    html += "</tr></thead><tbody>"
    for row in rows:
        html += "<tr>"
        for cell in row:
            html += f"<td>{cell}</td>"
        html += "</tr>"
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)


def render_structured(result: dict):
    blocks = result.get("structured_blocks", [])

    if "fields" in result and result["fields"]:
        st.markdown("### Campos extra\u00eddos")
        for field in result["fields"]:
            render_field_card(field)

    if not blocks:
        return

    for block in blocks:
        t = block.get("type", "paragraph")
        content = block.get("content", "")
        meta = block.get("metadata", {})

        if t == "header":
            st.markdown(f"<div class='section-header'>{content}</div>", unsafe_allow_html=True)

        elif t == "key_value":
            col1, col2 = st.columns([1, 1])
            items = [line for line in content.split("\n") if ":" in line or "=" in line]
            for i, item in enumerate(items):
                col = col1 if i % 2 == 0 else col2
                if ":" in item:
                    k, v = item.split(":", 1)
                elif "=" in item:
                    k, v = item.split("=", 1)
                else:
                    continue
                col.markdown(f"""
                <div class="kv-item">
                    <div class="k">{k.strip()}</div>
                    <div class="v">{v.strip()}</div>
                </div>
                """, unsafe_allow_html=True)

        elif t == "table":
            pass

        elif t == "list":
            lines = content.split("\n")
            for line in lines:
                clean = line.lstrip("- *\u2022").strip()
                st.markdown(f"- {clean}")

        else:
            st.markdown(f"<div class='block-paragraph'>{content}</div>", unsafe_allow_html=True)


def render_result(result: dict):
    doc_type = result.get("document_type") or "desconhecido"
    conf = result.get("overall_confidence", 0)
    needs_review = result.get("needs_review", False)

    st.markdown(f"""
    <div class="result-header">
        <span class="doc-type-badge">{doc_type}</span>
        <span style="color:#a6adc8;font-size:0.85rem;">Confian\u00e7a: {conf:.0%}</span>
    </div>
    """, unsafe_allow_html=True)

    if needs_review:
        st.markdown('<div class="review-banner">\u26a0\ufe0f Revis\u00e3o necess\u00e1ria</div>', unsafe_allow_html=True)

    render_structured(result)

    for table in result.get("tables", []):
        render_table(table)

    if result.get("raw_text"):
        with st.expander("Texto bruto"):
            st.text(result["raw_text"])


def render_empty_state():
    st.markdown("""
    <div class="empty-state">
        <h3>Nenhum documento selecionado</h3>
        <p>Fa\u00e7a upload de um documento na barra lateral</p>
    </div>
    """, unsafe_allow_html=True)


if "docs" not in st.session_state:
    st.session_state.docs = {}

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("# DocIntellect")
    st.markdown("RPA \u00b7 OCR \u00b7 NLP")

    st.markdown("### Upload")
    uploaded = st.file_uploader(
        "Arquivo", type=["pdf", "png", "jpg", "jpeg", "tiff", "bmp"],
        label_visibility="collapsed",
    )

    if uploaded:
        key = f"upl_{uploaded.name}_{uploaded.size}"
        if key not in st.session_state:
            st.session_state[key] = True
            with st.spinner("Enviando..."):
                try:
                    r = httpx.post(
                        f"{API_URL}/api/v1/documents/upload",
                        files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type)},
                        timeout=30,
                    )
                    if r.status_code == 201:
                        doc = r.json()
                        doc["status"] = "uploaded"
                        doc["filename"] = uploaded.name
                        st.session_state.docs[doc["id"]] = doc
                        st.session_state.selected = doc["id"]
                        st.success("Enviado!")
                    else:
                        st.error(r.text)
                except httpx.ConnectError:
                    st.error(f"API indisponivel em {API_URL}")

    st.markdown("---")
    st.markdown("### Documentos")

    for doc_id, doc in list(st.session_state.docs.items()):
        is_sel = doc_id == st.session_state.get("selected")
        sel_style = "border-left: 3px solid #89b4fa;" if is_sel else ""

        status = doc.get("status", "uploaded")
        badge_cls = f"badge-{status}"
        labels = {"uploaded": "Recebido", "processing": "Processando", "completed": "Concluido", "failed": "Falha"}

        st.markdown(f"""
        <div class="doc-card" style="{sel_style}">
            <div class="name">{doc.get("filename", "\u2014")}</div>
            <div class="meta">{format_bytes(doc.get("file_size", 0))}</div>
            <span class="status-badge {badge_cls}">{labels.get(status, status)}</span>
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("Selecionar", key=f"sel_{doc_id}", use_container_width=True):
                st.session_state.selected = doc_id
                st.rerun()
        with col_b:
            can_process = doc.get("status") in ("uploaded", "failed")
            if st.button("Processar", key=f"proc_{doc_id}", use_container_width=True, disabled=not can_process):
                doc["status"] = "processing"
                with st.spinner("Processando..."):
                    try:
                        r = httpx.post(f"{API_URL}/api/v1/documents/process/{doc_id}", timeout=120)
                        if r.status_code == 200:
                            doc["result"] = r.json()
                            doc["status"] = "completed"
                        else:
                            doc["status"] = "failed"
                            doc["error"] = r.text
                    except Exception as e:
                        doc["status"] = "failed"
                        doc["error"] = str(e)
                st.rerun()

# ── Main ─────────────────────────────────────────────────
_, main_col, _ = st.columns([1, 3, 1])

with main_col:
    sel_id = st.session_state.get("selected")
    if sel_id and sel_id in st.session_state.docs:
        doc = st.session_state.docs[sel_id]
        if "result" in doc:
            render_result(doc["result"])
        elif doc.get("status") == "processing":
            st.info("Processando documento...")
        elif doc.get("status") == "failed":
            st.error(f"Falha: {doc.get('error', 'erro desconhecido')}")
        else:
            st.info("Clique em **Processar** na barra lateral.")
    else:
        render_empty_state()
