from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import PlainTextResponse
import tempfile
import os
import pymupdf4llm
from pdf2image import convert_from_path
import pytesseract

app = FastAPI(title="pdf2md API")

@app.post("/convert")
async def convert_pdf(
    file: UploadFile = File(...),
    images: bool = Form(True),
    dpi: int = Form(200),
    ocr: bool = Form(False)
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        if ocr:
            images_list = convert_from_path(tmp_path, dpi=dpi)
            text = ""
            for img in images_list:
                text += pytesseract.image_to_string(img) + "\n\n"
            md_text = f"# {file.filename.replace('.pdf','')}\n\n{text}"
        else:
            md_text = pymupdf4llm.to_markdown(
                tmp_path, write_images=images, dpi=dpi
            )

        return PlainTextResponse(md_text, media_type="text/markdown")

    finally:
        os.unlink(tmp_path)


# Run with: uvicorn api:app --reload