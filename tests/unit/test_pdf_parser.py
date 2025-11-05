import pytest
from app.parsing.pdf_parser import parse_pdf_bytes, PDFParseError
import pathlib

TEST_DATA = pathlib.Path(__file__).parent.parent / "data"

def test_parse_valid_pdf():
    path = TEST_DATA / "sample.pdf"
    assert path.exists(), "Place a small sample.pdf at tests/data/sample.pdf"
    with path.open("rb") as f:
        b = f.read()
    parsed = parse_pdf_bytes(b, filename="sample.pdf", document_id="doc1")
    assert parsed.pages > 0
    assert len(parsed.text) > 10

def test_parse_empty_bytes():
    with pytest.raises(PDFParseError):
        parse_pdf_bytes(b"", filename="empty.pdf", document_id="doc2")
