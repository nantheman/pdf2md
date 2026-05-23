# pdf2md

**High-quality PDF → Markdown converter** with web UI + CLI.  
Supports batch processing, image extraction, and OCR fallback for scanned documents.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)

---

## ✨ Features

- **Excellent conversion quality** using `pymupdf4llm`
- **Batch PDF processing** in the web UI
- **OCR fallback** for scanned/image-only PDFs (via Tesseract)
- **Image extraction** (embedded as base64)
- **Beautiful dark-themed Streamlit UI**
- **Full-featured Unix CLI** (`cli.py`)
- Easy deployment on **Streamlit Cloud**, **Railway**, **Fly.io**, or any Docker host

---

## Quick Start

### Web UI (Recommended)

```bash
git clone https://github.com/YOURUSERNAME/pdf2md.git
cd pdf2md
pip install -r requirements.txt
streamlit run app.py

## API Usage (FastAPI)

```bash
uvicorn api:app --reload --port 8000

curl -X POST "http://localhost:8000/convert" \
  -F "file=@document.pdf" \
  -F "images=true" \
  -F "dpi=200" \
  -F "ocr=false" \
  -o output.md