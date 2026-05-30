import pytest
from fastapi import HTTPException

from backend.upload_utils import sanitize_pdf_filename


def test_sanitize_pdf_filename_blocks_path_traversal():
    safe_filename, collection = sanitize_pdf_filename("../合同 2026.pdf")

    assert safe_filename == "合同_2026.pdf"
    assert collection == "合同_2026"


def test_sanitize_pdf_filename_rejects_non_pdf():
    with pytest.raises(HTTPException):
        sanitize_pdf_filename("notes.txt")
