import os

import docx
import fitz
import textract
from bs4 import BeautifulSoup


# Parse PDF files
def parse_pdf(file_bytes) -> str:
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        text = "\n".join(page.get_text() for page in doc)
    return text


# Parse DOCX files
def parse_docx(file_bytes) -> str:
    with open("temp.docx", "wb") as f:
        f.write(file_bytes)
    doc = docx.Document("temp.docx")
    text = "\n".join([p.text for p in doc.paragraphs])
    os.remove("temp.docx")
    return text


# Parse DOC files
def parse_doc(file_bytes) -> str:
    with open("temp.doc", "wb") as f:
        f.write(file_bytes)
    try:
        text = textract.process("temp.doc").decode("utf-8")
        return text
    finally:
        os.remove("temp.doc")


# Parse TXT files
def parse_txt(file_bytes) -> str:
    return file_bytes.decode("utf-8")


def parse_html(file_bytes) -> str:
    try:
        html = file_bytes.decode("utf-8", errors="ignore")
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator="\n", strip=True)
    except Exception as e:
        raise RuntimeError(f"Failed to parse HTML file: {e}")
