# pdf2md

**High-quality PDF → Markdown converter** with beautiful web UI, batch processing, image extraction, and OCR fallback.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)

---

## ✨ Features

- Excellent conversion quality using **PyMuPDF4LLM**
- **Batch upload** with live progress bars
- **Image extraction** (embedded as base64)
- **OCR fallback** for scanned/image-only PDFs (Tesseract)
- Clean dark-themed Streamlit UI
- Full-featured Unix-style **CLI**
- **FastAPI** endpoint for scripting / integration
- Easy deployment via Docker, Streamlit Cloud, Railway, Fly.io

---

## Quick Start

### 1. Local Development

```bash
git clone https://github.com/YOURUSERNAME/pdf2md.git
cd pdf2md

# Install dependencies
pip install -r requirements.txt

# System dependencies (for OCR)
# Ubuntu/Debian
sudo apt install tesseract-ocr poppler-utils -y

# Run web UI
streamlit run app.py