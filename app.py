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

st.title("📄 pdf2md")
st.markdown("**PDF to Markdown** • Batch + Images + OCR • Running on Streamlit Cloud")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    include_images = st.checkbox("Extract images (base64)", value=True)
    dpi = st.slider("Image DPI", 150, 350, 200, step=50)
    
    use_ocr = st.checkbox("OCR for scanned PDFs", value=False,
                         help="Slower. Requires Poppler + Tesseract")
    
    if use_ocr:
        st.info("OCR mode active (uses Tesseract)")

    st.markdown("---")
    st.markdown("**CLI Example**")
    st.code("python cli.py file.pdf --images --ocr", language="bash")

def check_poppler():
    try:
        subprocess.run(["pdftoppm", "-v"], capture_output=True, timeout=3)
        return True
    except:
        return False

# Main uploader
uploaded_files = st.file_uploader("Upload PDF(s)", type="pdf", accept_multiple_files=True)

if uploaded_files:
    results = []
    progress_bar = st.progress(0)
    status = st.empty()

    poppler_available = check_poppler()

    for idx, uploaded_file in enumerate(uploaded_files):
        status.text(f"Processing {uploaded_file.name} ({idx+1}/{len(uploaded_files)})")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name

        try:
            file_progress = st.progress(0, text=f"Converting {uploaded_file.name}")

            if use_ocr and poppler_available:
                images = convert_from_path(tmp_path, dpi=dpi)
                text = ""
                for i, img in enumerate(images):
                    text += pytesseract.image_to_string(img) + "\n\n"
                    file_progress.progress(int((i+1)/len(images)*100))
                md_text = f"# {Path(uploaded_file.name).stem}\n\n{text}"
            else:
                if use_ocr and not poppler_available:
                    st.warning(f"OCR disabled for {uploaded_file.name} (Poppler not available)")
                md_text = pymupdf4llm.to_markdown(
                    tmp_path,
                    write_images=include_images,
                    dpi=dpi,
                    page_numbers=True
                )
                file_progress.progress(100)

            results.append((uploaded_file.name, md_text))
            os.unlink(tmp_path)

            # Overall progress
            progress_bar.progress(int((idx+1)/len(uploaded_files)*100))

        except Exception as e:
            st.error(f"Error with {uploaded_file.name}: {str(e)}")
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    status.success("✅ Conversion complete!")

    # Results
    for name, md in results:
        with st.expander(f"📄 {name}", expanded=False):
            tab1, tab2 = st.tabs(["Preview", "Download"])
            with tab1:
                st.markdown(md[:2000] + "\n\n*(preview truncated)*" if len(md) > 2000 else md)
            with tab2:
                st.download_button(
                    "↓ Download .md",
                    data=md,
                    file_name=f"{Path(name).stem}.md",
                    mime="text/markdown",
                    key=f"dl_{name}"
                )