from backend.chunk import split_pages, split_text


def test_split_text_keeps_overlap():
    text = "这是第一句。" * 80
    chunks = split_text(text, chunk_size=120, overlap=20)

    assert len(chunks) > 1
    assert all(chunk.strip() for chunk in chunks)
    assert chunks[1].startswith(chunks[0][-20:].strip()[:5])


def test_split_pages_adds_source_metadata():
    records = split_pages(
        [{"page": 2, "text": "测试内容。" * 20}],
        chunk_size=80,
        overlap=10,
        source="demo.pdf",
    )

    assert records
    assert records[0]["metadata"]["source"] == "demo.pdf"
    assert records[0]["metadata"]["page"] == 2
