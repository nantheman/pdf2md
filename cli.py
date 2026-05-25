#!/usr/bin/env python3
import argparse
import pymupdf4llm
import sys
import tempfile
import os
from pdf2image import convert_from_path
import pytesseract

def main():
    parser = argparse.ArgumentParser(description="pdf2md - PDF to Markdown converter")
    parser.add_argument("input", help="Input PDF file")
    parser.add_argument("-o", "--output", help="Output markdown file")
    parser.add_argument("--images", action="store_true", help="Extract images")
    parser.add_argument("--dpi", type=int, default=200, help="Image DPI")
    parser.add_argument("--ocr", action="store_true", help="Use OCR fallback")
    args = parser.parse_args()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        with open(args.input, "rb") as f:
            tmp.write(f.read())
        tmp_path = tmp.name

    try:
        if args.ocr:
            images = convert_from_path(tmp_path, dpi=args.dpi)
            text = ""
            for img in images:
                text += pytesseract.image_to_string(img) + "\n\n"
            md_text = f"# {os.path.basename(args.input).replace('.pdf','')}\n\n{text}"
        else:
            md_text = pymupdf4llm.to_markdown(
                tmp_path, write_images=args.images, dpi=args.dpi
            )

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(md_text)
            print(f"✅ Saved to {args.output}", file=sys.stderr)
        else:
            print(md_text)

    finally:
        os.unlink(tmp_path)

if __name__ == "__main__":
    main()