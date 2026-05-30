import re


_BOUNDARY_RE = re.compile(r"[。！？.!?；;，,\n]")


def _best_boundary(text: str, start: int, end: int) -> int:
    min_end = start + int((end - start) * 0.6)
    window = text[min_end:end]
    matches = list(_BOUNDARY_RE.finditer(window))
    if not matches:
        return end
    return min_end + matches[-1].end()


def split_text(text, chunk_size=800, overlap=100):
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        return []
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            end = _best_boundary(text, start, end)

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break
        start = max(end - overlap, start + 1)

    return chunks


def split_pages(pages, chunk_size=800, overlap=100, source=None):
    records = []
    for page in pages:
        page_number = page.get("page")
        for index, content in enumerate(
            split_text(page.get("text", ""), chunk_size=chunk_size, overlap=overlap)
        ):
            records.append(
                {
                    "content": content,
                    "metadata": {
                        "source": source or "",
                        "page": page_number or 0,
                        "chunk_index": index,
                    },
                }
            )
    return records