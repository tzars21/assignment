from typing import Tuple
from pypdf import PdfReader
from pydantic import BaseModel
import io

class ParsedDocument(BaseModel):
    document_id: str
    filename: str
    pages: int
    text: str

class PDFParseError(Exception):
    pass

def parse_pdf_bytes(file_bytes: bytes, filename: str, document_id: str) -> ParsedDocument:
    if not file_bytes:
        raise PDFParseError("Empty file")
    try:
        stream = io.BytesIO(file_bytes)
        reader = PdfReader(stream)
        if reader.pages is None or len(reader.pages) == 0:
            raise PDFParseError("PDF has no pages")

        text_chunks = []
        for page in reader.pages:
            try:
                text_chunks.append(page.extract_text() or "")
            except Exception:
                text_chunks.append("")

        full_text = "\n".join(text_chunks).strip()
        if not full_text:
            raise PDFParseError("No extractable text in PDF")

        return ParsedDocument(
            document_id=document_id,
            filename=filename,
            pages=len(reader.pages),
            text=full_text,
        )
    except Exception as e:
        raise PDFParseError(f"Failed to parse PDF: {e}") from e
