"""Tests for context chunk sanitization."""

from __future__ import annotations

from app.ingestion.cleaner import sanitize_chunk_text, sanitize_context


_RAW_CHUNK = """==================================================

Question:
How to reset bKash PIN?

Answer:
You can reset your bKash PIN by dialing *247# and selecting the PIN reset option.

Category:
Security

Language:
en

=================================================="""


class TestSanitizeChunkText:
    def test_removes_question_label(self: TestSanitizeChunkText) -> None:
        result = sanitize_chunk_text(_RAW_CHUNK)
        assert "Question:" not in result

    def test_removes_answer_label(self: TestSanitizeChunkText) -> None:
        result = sanitize_chunk_text(_RAW_CHUNK)
        assert "Answer:" not in result

    def test_removes_category_label(self: TestSanitizeChunkText) -> None:
        result = sanitize_chunk_text(_RAW_CHUNK)
        assert "Category:" not in result

    def test_removes_language_label(self: TestSanitizeChunkText) -> None:
        result = sanitize_chunk_text(_RAW_CHUNK)
        assert "Language:" not in result

    def test_removes_separators(self: TestSanitizeChunkText) -> None:
        result = sanitize_chunk_text(_RAW_CHUNK)
        assert "====" not in result
        assert "----" not in result

    def test_preserves_answer_content(self: TestSanitizeChunkText) -> None:
        result = sanitize_chunk_text(_RAW_CHUNK)
        assert "reset your bKash PIN" in result
        assert "*247#" in result

    def test_no_faq_labels_in_result(self: TestSanitizeChunkText) -> None:
        result = sanitize_chunk_text(_RAW_CHUNK)
        forbidden = ["Question:", "Answer:", "Category:", "Language:"]
        for label in forbidden:
            assert label not in result, f"Found '{label}' in sanitized output"

    def test_handles_empty_string(self: TestSanitizeChunkText) -> None:
        assert sanitize_chunk_text("") == ""

    def test_handles_plain_text(self: TestSanitizeChunkText) -> None:
        text = "Just a plain sentence."
        assert sanitize_chunk_text(text) == text


class TestSanitizeContext:
    def test_sanitizes_multiple_chunks(self: TestSanitizeContext) -> None:
        chunks = [
            {"text": _RAW_CHUNK, "source": "bkash_faq", "score": 0.9},
            {"text": _RAW_CHUNK, "source": "nagad_faq", "score": 0.8},
        ]
        result = sanitize_context(chunks)
        assert len(result) == 2
        for item in result:
            assert "Question:" not in item["text"]
            assert "Answer:" not in item["text"]
            assert "Category:" not in item["text"]
            assert "Language:" not in item["text"]
            assert "====" not in item["text"]
            # Original metadata fields are preserved
            assert item["source"] in ("bkash_faq", "nagad_faq")
            assert item["score"] in (0.9, 0.8)