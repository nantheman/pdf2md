import streamlit as st
import tempfile
import os
from pathlib import Path
import pymupdf4llm
from pdf2image import convert_from_path
import pytesseract
import subprocess

st.set_page_config(
    page_title="pdf2md",
    page_icon="📄",
    layout="wide"
)

# ====================== SIDEBAR NAVIGATION ======================
page = st.sidebar.selectbox(
    "Navigation",
    ["Converter", "About"]
)

# ====================== ABOUT PAGE ======================
if page == "About":
    st.title("About pdf2md")
    st.markdown("**High-quality PDF to Markdown Converter** — Local Desktop Edition")
    
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            readme_content = f.read()
        st.markdown(readme_content)
    except FileNotFoundError:
        st.error("README.md file not found.")
        st.markdown("""
        ### pdf2md
        
        High-quality PDF → Markdown converter with OCR support.
        
        **Features:**
        - Excellent layout preservation
        - Image extraction
        - OCR for scanned PDFs
        - Local Streamlit UI + CLI
        """)

# ====================== CONVERTER PAGE ======================
else:
    st.title("📄 pdf2md")
    st.markdown("**Local Desktop Version** — High Quality + OCR Support")

    # Sidebar settings
    with st.sidebar:
        st.header("⚙️ Settings")
        include_images = st.checkbox("Extract images as base64", value=True)
        dpi = st.slider("Image DPI", 150, 400, 220)
        use_ocr = st.checkbox("Use OCR for scanned PDFs", value=False)
        
        st.markdown("---")
        st.caption("Run CLI: `python cli.py file.pdf --ocr`")

    def check_poppler():
        try:
            subprocess.run(["pdftoppm", "-v"], capture_output=True, timeout=3)
            return True
        except:
            return False

    poppler_ok = check_poppler()

    uploaded_files = st.file_uploader(
        "Drop one or more PDF files here",
        type="pdf",
        accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            with st.spinner(f"Processing {uploaded_file.name}..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getbuffer())
                    tmp_path = tmp.name

                try:
                    if use_ocr and poppler_ok:
                        images = convert_from_path(tmp_path, dpi=dpi)
                        text = ""
                        progress = st.progress(0)
                        for i, img in enumerate(images):
                            text += pytesseract.image_to_string(img) + "\n\n"
                            progress.progress((i + 1) / len(images))
                        md_text = f"# {Path(uploaded_file.name).stem}\n\n{text}"
                    else:
                        md_text = pymupdf4llm.to_markdown(
                            tmp_path,
                            write_images=include_images,
                            dpi=dpi,
                            page_numbers=True
                        )

                    os.unlink(tmp_path)

                    st.subheader(uploaded_file.name)
                    tab1, tab2 = st.tabs(["📝 Preview", "📥 Download"])
                    with tab1:
                        st.markdown(md_text[:2000] + "\n\n... (truncated)" if len(md_text) > 2000 else md_text)
                    with tab2:
                        st.download_button(
                            label="↓ Download .md",
                            data=md_text,
                            file_name=f"{Path(uploaded_file.name).stem}.md",
                            mime="text/markdown",
                            key=uploaded_file.name
                        )

                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)