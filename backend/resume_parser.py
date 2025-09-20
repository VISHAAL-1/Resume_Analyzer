# backend/resume_parser.py
import os
import time
from fastapi import UploadFile
import fitz # PyMuPDF
import docx2txt

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_upload_file_tmp(upload_file: UploadFile) -> str:
    contents = await upload_file.read()  # bytes
    ext = os.path.splitext(upload_file.filename)[1].lower()
    ts = int(time.time() * 1000)
    safe_name = f"{ts}_{upload_file.filename.replace(' ', '_')}"
    path = os.path.join(UPLOAD_DIR, safe_name)
    with open(path, "wb") as f:
        f.write(contents)
    return path

async def parse_resume_file(upload_file: UploadFile):
    """
    returns tuple: (plain_text, saved_path)
    """
    saved_path = await save_upload_file_tmp(upload_file)
    text = ""
    if saved_path.lower().endswith(".pdf"):
        with fitz.open(saved_path) as doc:
            pages = []
            for p in doc:
                pages.append(p.get_text())
        text = "\n".join(pages)
    else:
        # docx and many text formats
        try:
            text = docx2txt.process(saved_path)
        except Exception:
            # fallback: read as bytes and decode
            with open(saved_path, "rb") as f:
                try:
                    text = f.read().decode("utf-8", errors="ignore")
                except Exception:
                    text = ""
    return text, saved_path