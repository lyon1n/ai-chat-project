from backend.chat_service import build_rag_prompt


def test_build_rag_prompt_includes_source_metadata():
    prompt = build_rag_prompt(
        "问题是什么？",
        [
            {
                "content": "答案在这里",
                "metadata": {"source": "manual.pdf", "page": 3},
            }
        ],
    )

    assert "manual.pdf" in prompt
    assert "第 3 页" in prompt
    assert "答案在这里" in prompt
