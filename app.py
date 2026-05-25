import streamlit as st
import tempfile
import os
from pathlib import Path
import pymupdf4llm
from pdf2image import convert_from_path
import pytesseract
import subprocess
from PIL import Image

# ====================== CONFIG ======================
st.set_page_config(
    page_title="pdf2md",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📄 pdf2md")
st.markdown("**Professional PDF to Markdown Converter** — Batch • Images • OCR Fallback")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("⚙️ Conversion Settings")
    
    include_images = st.checkbox("Extract images as base64", value=True, 
                                help="Embeds images directly in the markdown")
    
    dpi = st.slider("Image quality (DPI)", min_value=150, max_value=400, 
                   value=200, step=50)
    
    use_ocr = st.checkbox("Enable OCR fallback for scanned PDFs", value=False,
                         help="Slower but necessary for image-only PDFs")
    
    st.markdown("---")
    st.markdown("**Unix CLI**")
    st.code("python cli.py input.pdf --images --ocr --dpi 300", language="bash")
    
    st.markdown("---")
    st.info("Poppler + Tesseract required for OCR mode")

# ====================== UTILITY FUNCTIONS ======================
def check_poppler():
    """Check if poppler-utils is installed"""
    try:
        result = subprocess.run(["pdftoppm", "-v"], capture_output=True, text=True, timeout=3)
        return True
    except FileNotFoundError:
        return False
    except:
        return False

# ====================== MAIN APP ======================
uploaded_files = st.file_uploader(
    "Drop one or more PDF files here",
    type="pdf",
    accept_multiple_files=True,
    help="You can select multiple files at once"
)

if uploaded_files:
    if use_ocr and not check_poppler():
        st.error("❌ **OCR mode is enabled but Poppler is not installed.**")
        st.warning("OCR requires `poppler-utils`. Use Docker deployment or disable OCR.")
        use_ocr = False  # Force disable

    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, uploaded_file in enumerate(uploaded_files):
        file_name = uploaded_file.name
        status_text.text(f"Processing: {file_name} ({idx+1}/{len(uploaded_files)})")

        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_path = tmp_file.name

        try:
            file_progress = st.progress(0, text=f"Converting {file_name}")

            if use_ocr:
                # OCR Mode
                images = convert_from_path(tmp_path, dpi=dpi)
                ocr_text = ""
                
                for i, img in enumerate(images):
                    ocr_text += pytesseract.image_to_string(img) + "\n\n"
                    progress_pct = int((i + 1) / len(images) * 100)
                    file_progress.progress(progress_pct)
                
                md_text = f"# {Path(file_name).stem}\n\n{ocr_text}"
                
            else:
                # High-quality PyMuPDF4LLM mode
                md_text = pymupdf4llm.to_markdown(
                    tmp_path,
                    write_images=include_images,
                    dpi=dpi,
                    page_numbers=True
                )
                file_progress.progress(100)

            results.append((file_name, md_text))
            os.unlink(tmp_path)

            # Update overall progress
            overall_progress = int((idx + 1) / len(uploaded_files) * 100)
            progress_bar.progress(overall_progress)

        except Exception as e:
            st.error(f"Failed to process **{file_name}**: {str(e)}")
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    status_text.success(f"✅ All {len(uploaded_files)} files processed successfully!")

    # ====================== RESULTS SECTION ======================
    st.markdown("---")
    st.subheader("Conversion Results")

    for file_name, md_text in results:
        with st.expander(f"📄 {file_name}", expanded=True):
            tab1, tab2 = st.tabs(["📝 Preview", "📥 Download"])

            with tab1:
                preview_length = 1500
                preview = md_text[:preview_length] + "\n\n*(...truncated preview...)*" if len(md_text) > preview_length else md_text
                st.markdown(preview)

            with tab2:
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.download_button(
                        label="↓ Download Markdown",
                        data=md_text,
                        file_name=f"{Path(file_name).stem}.md",
                        mime="text/markdown",
                        key=f"download_{file_name}"
                    )
                with col2:
                    if st.button("📋 Copy to Clipboard", key=f"copy_{file_name}"):
                        st.code(md_text[:2000] + "..." if len(md_text) > 2000 else md_text)
                        st.toast("✅ Copied to clipboard!", icon="📋")

else:
    st.info("👆 Upload PDFs to begin conversion")
    st.markdown("""
    ### Supported Features:
    - Excellent layout preservation (headings, tables, lists)
    - Image extraction
    - OCR for scanned documents
    - Batch processing with live progress
    """)