import streamlit as st
import tempfile
import os
from pathlib import Path
import pymupdf4llm
import subprocess

st.set_page_config(page_title="pdf2md", page_icon="📄", layout="wide")

st.title("📄 pdf2md")
st.markdown("**PDF to Markdown** with OCR Support")

# Sidebar
with st.sidebar:
    st.header("Settings")
    include_images = st.checkbox("Extract images", value=True)
    dpi = st.slider("Image DPI", 150, 350, 200)
    use_ocr = st.checkbox("Enable OCR for scanned PDFs", value=True)
    
    if use_ocr:
        st.warning("⚠️ OCR mode is slower and may timeout on large files")

def check_poppler():
    try:
        result = subprocess.run(["pdftoppm", "-v"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

# Check dependencies once
poppler_ok = check_poppler()

uploaded_files = st.file_uploader("Upload PDF(s)", type="pdf", accept_multiple_files=True)

if uploaded_files:
    results = []
    progress_bar = st.progress(0)
    status = st.empty()

    for idx, uploaded_file in enumerate(uploaded_files):
        status.text(f"Processing {uploaded_file.name}...")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name

        try:
            file_progress = st.progress(0, text=f"Converting {uploaded_file.name}")

            if use_ocr and poppler_ok:
                # OCR Mode
                from pdf2image import convert_from_path
                import pytesseract
                
                images = convert_from_path(tmp_path, dpi=dpi)
                text = ""
                for i, img in enumerate(images):
                    text += pytesseract.image_to_string(img) + "\n\n"
                    file_progress.progress(int((i + 1) / len(images) * 100))
                
                md_text = f"# {Path(uploaded_file.name).stem}\n\n{text}"
            else:
                # Normal high-quality mode
                if use_ocr and not poppler_ok:
                    st.warning("Poppler not available → using normal mode")
                md_text = pymupdf4llm.to_markdown(
                    tmp_path,
                    write_images=include_images,
                    dpi=dpi,
                    page_numbers=True
                )
                file_progress.progress(100)

            results.append((uploaded_file.name, md_text))
            os.unlink(tmp_path)

            progress_bar.progress(int((idx + 1) / len(uploaded_files) * 100))

        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    status.success("✅ Conversion completed!")

    for name, md_text in results:
        with st.expander(f"📄 {name}", expanded=True):
            tab1, tab2 = st.tabs(["Preview", "Download"])
            with tab1:
                st.markdown(md_text[:1800] + "\n\n*(truncated preview)*" if len(md_text) > 1800 else md_text)
            with tab2:
                st.download_button(
                    "↓ Download .md",
                    data=md_text,
                    file_name=f"{Path(name).stem}.md",
                    mime="text/markdown",
                    key=name
                )