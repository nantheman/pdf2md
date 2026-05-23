import streamlit as st
import pymupdf4llm
import tempfile
import os
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

st.set_page_config(page_title="pdf2md", page_icon="📄", layout="wide")

st.title("📄 pdf2md")
st.markdown("**High-quality PDF → Markdown** with batch progress + OCR")

with st.sidebar:
    st.header("Options")
    include_images = st.checkbox("Extract images", value=True)
    dpi = st.slider("Image DPI", 150, 400, 200)
    use_ocr = st.checkbox("OCR fallback (scanned PDFs)", value=False)
    st.markdown("---")
    st.code("python cli.py input.pdf --images --ocr", language="bash")

uploaded_files = st.file_uploader("Drop one or more PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing {uploaded_file.name} ({idx+1}/{len(uploaded_files)})")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name

        try:
            # Per-file sub-progress
            file_progress = st.progress(0, text=f"Converting {uploaded_file.name}")

            if use_ocr:
                images = convert_from_path(tmp_path, dpi=dpi)
                ocr_text = ""
                for i, img in enumerate(images):
                    ocr_text += pytesseract.image_to_string(img) + "\n\n"
                    file_progress.progress((i + 1) / len(images))
                md_text = f"# {uploaded_file.name.replace('.pdf','')}\n\n{ocr_text}"
            else:
                # pymupdf4llm doesn't have native progress, so we simulate
                md_text = pymupdf4llm.to_markdown(
                    tmp_path,
                    write_images=include_images,
                    dpi=dpi,
                    page_numbers=True
                )
                file_progress.progress(100)

            os.unlink(tmp_path)

            results.append((uploaded_file.name, md_text))

            # Update main progress
            overall_progress = int((idx + 1) / len(uploaded_files) * 100)
            progress_bar.progress(overall_progress)

        except Exception as e:
            st.error(f"Failed {uploaded_file.name}: {str(e)}")
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    status_text.text("✅ All files processed!")

    # Display results
    for name, md_text in results:
        st.subheader(name)
        tab1, tab2 = st.tabs(["Preview", "Download"])
        with tab1:
            st.markdown(md_text[:1500] + "\n\n*(truncated)*" if len(md_text) > 1500 else md_text)
        with tab2:
            st.download_button(
                "↓ Download .md",
                data=md_text,
                file_name=f"{Path(name).stem}.md",
                mime="text/markdown",
                key=f"dl_{name}"
            )