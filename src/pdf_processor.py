from pypdf import PdfReader
from io import BytesIO


def extract_resume_text(pdf_bytes: bytes) -> str:
    """Extract text from a PDF resume."""
    pdf_file = BytesIO(pdf_bytes)
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text += page_text + "\n"

    return text.strip()