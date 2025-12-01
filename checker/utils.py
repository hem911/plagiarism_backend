# plagiarism_backend/checker/utils.py
import io
import pdfplumber
from docx import Document
import re

def extract_text_from_pdf(file_obj):
    """
    file_obj: file-like object
    returns: extracted text string
    """
    text_chunks = []
    # pdfplumber requires a file path or file-like; file_obj should be opened in binary mode
    with pdfplumber.open(file_obj) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_chunks.append(page_text)
    return "\n".join(text_chunks)

def extract_text_from_docx(file_obj):
    """
    file_obj: file-like object (BytesIO)
    returns: extracted text string
    """
    # python-docx expects a file path or file-like
    doc = Document(file_obj)
    paragraphs = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
    return "\n".join(paragraphs)

def clean_text(text):
    # simple cleaning
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\s+\n", "\n", text)
    text = text.strip()
    return text

def chunk_text(text, max_words=150):
    """
    Split text into "meaningful" chunks ~ max_words each.
    Attempts to split by paragraphs or sentences, but fallback to sliding window.
    Returns list of chunk strings.
    """
    text = clean_text(text)
    if not text:
        return []
    # Try split by paragraphs
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    for p in paragraphs:
        words = p.split()
        if len(words) <= max_words:
            chunks.append(p)
        else:
            # split paragraph into sentence-like pieces by sentences (.!?)
            sentences = re.split(r'(?<=[\.\?\!])\s+', p)
            cur = []
            cur_len = 0
            for s in sentences:
                s_words = s.split()
                if cur_len + len(s_words) <= max_words:
                    cur.append(s)
                    cur_len += len(s_words)
                else:
                    if cur:
                        chunks.append(" ".join(cur))
                    # start new
                    cur = [s]
                    cur_len = len(s_words)
            if cur:
                chunks.append(" ".join(cur))
    # if still some chunks too big, do fixed-window split
    final_chunks = []
    for c in chunks:
        words = c.split()
        if len(words) <= max_words:
            final_chunks.append(c)
        else:
            for i in range(0, len(words), max_words):
                final_chunks.append(" ".join(words[i:i+max_words]))
    return final_chunks
