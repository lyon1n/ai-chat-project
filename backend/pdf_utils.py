from pypdf import PdfReader


def read_pdf_pages(file_path):
    reader = PdfReader(file_path)
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append({"page": page_number, "text": text})

    return pages


def read_pdf(file_path):
    return "\n\n".join(page["text"] for page in read_pdf_pages(file_path))