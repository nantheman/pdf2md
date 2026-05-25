# ================================================
# pdf2md - Production Docker Image
# ================================================

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py cli.py api.py ./

# Expose ports for Streamlit and FastAPI
EXPOSE 8501 8000

# Health check
HEALTHCHECK CMD pdftoppm -v || exit 1

# Default command: Run Streamlit
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.enableCORS=false"]