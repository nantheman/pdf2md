import streamlit as st
import tempfile
import os
from pathlib import Path
import pymupdf4llm

st.set_page_config(
    page_title="pdf2md",
    page_icon="📄",
    layout="wide"
)

st.title("📄 pdf2md")
st.markdown("**Clean PDF to Markdown Converter** — Optimized for Streamlit Cloud")

with st.sidebar:
    st.header("Settings")
    include_images = st.checkbox("Extract images as base64", value=True)
    dpi = st.slider("Image DPI", 150, 300, 200)
    
    st.markdown("---")
    st.caption("OCR is disabled for stability on Streamlit Cloud")

st.info("Upload PDFs below. Works best with digital (text-based) PDFs.")

uploaded_files = st.file_uploader(
    "Drop PDF files here",
    type="pdf",
    accept_multiple_files=True
)

if uploaded_files:
    progress_bar = st.progress(0)
    status_text = st.empty()
    results = []

    for idx, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing {uploaded_file.name} ({idx+1}/{len(uploaded_files)})")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name

        try:
            md_text = pymupdf4llm.to_markdown(
                tmp_path,
                write_images=include_images,
                dpi=dpi,
                page_numbers=True
            )

            results.append((uploaded_file.name, md_text))
            os.unlink(tmp_path)

            progress_bar.progress(int((idx + 1) / len(uploaded_files) * 100))

        except Exception as e:
            st.error(f"Failed {uploaded_file.name}: {str(e)}")
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    status_text.success("✅ All files converted!")

    for name, md_text in results:
        with st.expander(f"📄 {name}", expanded=True):
            tab1, tab2 = st.tabs(["Preview", "Download"])
            with tab1:
                st.markdown(md_text[:2000] + "\n\n... (truncated)" if len(md_text) > 2000 else md_text)
            with tab2:
                st.download_button(
                    label="↓ Download .md",
                    data=md_text,
                    file_name=f"{Path(name).stem}.md",
                    mime="text/markdown",
                    key=name
                )