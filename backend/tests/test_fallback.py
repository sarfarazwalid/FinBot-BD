"""Tests for the offline fallback answer system.

Verifies that when Gemini is unavailable, FinBot BD still produces a
clean, language-appropriate answer from the retrieved chunks.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.llm.generator import _build_fallback_answer, generate_answer


_SAMPLE_CHUNKS = [
    {
        "text": "You can reset your bKash PIN by dialing *247# and selecting the PIN reset option.",
        "source": "bkash_faq",
        "score": 0.95,
    },
    {
        "text": "You can also reset PIN via bKash app > Settings > Security > Reset PIN.",
        "source": "bkash_faq",
        "score": 0.90,
    },
    {
        "text": "Dial *167#, select forgot PIN, enter registered mobile, verify with OTP.",
        "source": "nagad_faq",
        "score": 0.85,
    },
]

_BENGALI_CHUNK = {
    "text": "আপনার পিন রিসেট করতে *247# ডায়াল করুন এবং পিন রিসেট অপশন নির্বাচন করুন।",
    "source": "bkash_faq",
    "score": 0.92,
}


class TestBuildFallbackAnswer:
    """Unit tests for _build_fallback_answer()."""

    def test_english_query_produces_english_fallback(self):
        """English query should produce an English fallback."""
        result = _build_fallback_answer(_SAMPLE_CHUNKS, "How to reset bKash PIN?")
        assert "bkash_faq" in result["sources"]
        assert "reset" in result["answer"].lower()
        assert "*247#" in result["answer"]
        # No Bengali script
        import re
        assert not re.search(r"[\u0980-\u09FF]", result["answer"])

    def test_bengali_query_produces_bengali_fallback(self):
        """Bengali query should produce a Bengali fallback."""
        chunks = [_BENGALI_CHUNK, _SAMPLE_CHUNKS[0]]
        result = _build_fallback_answer(chunks, "কিভাবে পিন রিসেট করবেন?")
        assert result["answer"]
        assert len(result["answer"]) > 0

    def test_banglish_query_produces_banglish_fallback(self):
        """Banglish query should produce a mixed Banglish fallback."""
        result = _build_fallback_answer(_SAMPLE_CHUNKS, "bKash PIN reset ki vabe korbo?")
        assert result["answer"]
        assert "reset" in result["answer"].lower()

    def test_fallback_removes_duplicates(self):
        """Duplicate chunks should not produce duplicate sentences."""
        chunks = [_SAMPLE_CHUNKS[0], _SAMPLE_CHUNKS[0]]  # same chunk twice
        result = _build_fallback_answer(chunks, "How to reset bKash PIN?")
        # The sentence should appear only once
        assert result["answer"].count("*247#") == 1

    def test_fallback_preserves_source_attribution(self):
        """Fallback should list sources used."""
        result = _build_fallback_answer(_SAMPLE_CHUNKS, "How to reset bKash PIN?")
        assert "bkash_faq" in result["sources"]
        assert "nagad_faq" in result["sources"]

    def test_fallback_confidence_scales_with_chunks(self):
        """More chunks should yield higher (but capped) confidence."""
        result_single = _build_fallback_answer([_SAMPLE_CHUNKS[0]], "reset PIN")
        result_multi = _build_fallback_answer(_SAMPLE_CHUNKS, "reset PIN")
        assert 0.0 <= result_single["confidence"] <= 0.7
        assert 0.0 <= result_multi["confidence"] <= 0.7
        assert result_multi["confidence"] >= result_single["confidence"]

    def test_fallback_empty_chunks(self):
        """Empty chunk list should return default message."""
        result = _build_fallback_answer([], "How to reset PIN?")
        assert "enough information" in result["answer"]
        assert result["sources"] == []
        assert result["confidence"] == 0.0

    def test_fallback_reason_included_when_no_chunks(self):
        """When reason is provided and no chunks available, reason should appear."""
        result = _build_fallback_answer(
            [], "How to reset PIN?", reason="quota_exceeded"
        )
        assert "service temporarily unavailable" in result["answer"].lower()
        assert "enough information" in result["answer"].lower()

    def test_fallback_no_metadata_labels(self):
        """Fallback answer should not contain raw FAQ labels."""
        result = _build_fallback_answer(_SAMPLE_CHUNKS, "How to reset PIN?")
        for label in ["Question:", "Answer:", "Category:", "Language:", "====", "----"]:
            assert label not in result["answer"], f"Found metadata label: {label}"


class TestFallbackIntegration:
    """Integration tests: generate_answer() should use fallback on Gemini errors."""

    @patch("app.llm.generator._get_client")
    def test_quota_exceeded_uses_fallback(self, mock_get_client):
        """429 ResourceExhausted should trigger fallback."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception(
            "429 ResourceExhausted: Quota exceeded"
        )

        result = generate_answer("How to reset bKash PIN?", _SAMPLE_CHUNKS)

        assert "quota" in result["answer"].lower() or "reset" in result["answer"].lower()
        assert result["sources"]
        assert result["confidence"] >= 0.0
        assert "[FALLBACK]" not in result["answer"]  # reason not exposed in answer

    @patch("app.llm.generator._get_client")
    def test_invalid_api_key_uses_fallback(self, mock_get_client):
        """Invalid API key should trigger fallback."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception(
            "401 PermissionDenied: API key invalid"
        )

        result = generate_answer("How to reset bKash PIN?", _SAMPLE_CHUNKS)

        assert result["answer"]
        assert "reset" in result["answer"].lower()
        assert result["sources"]

    @patch("app.llm.generator._get_client")
    def test_timeout_uses_fallback(self, mock_get_client):
        """Timeout should trigger fallback."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception(
            "DeadlineExceeded: Request timed out"
        )

        result = generate_answer("How to check balance?", _SAMPLE_CHUNKS)

        assert result["answer"]
        assert result["sources"]

    @patch("app.llm.generator._get_client")
    def test_empty_response_uses_fallback(self, mock_get_client):
        """Empty Gemini response should trigger fallback."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = ""
        mock_client.models.generate_content.return_value = mock_response

        result = generate_answer("How to reset PIN?", _SAMPLE_CHUNKS)

        assert result["answer"]
        assert result["sources"]
        # Fallback should contain retrieved info since chunks exist
        assert "reset" in result["answer"].lower() or "247" in result["answer"]

    @patch("app.llm.generator._get_client")
    def test_fallback_preserves_language_english(self, mock_get_client):
        """Fallback for English query should not contain Bengali."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("503 Service Unavailable")

        result = generate_answer("How to reset bKash PIN?", _SAMPLE_CHUNKS)
        import re
        assert not re.search(r"[\u0980-\u09FF]", result["answer"])

    @patch("app.llm.generator._get_client")
    def test_fallback_logs_reason(self, mock_get_client, caplog):
        """Fallback should log the reason and chunks used."""
        import logging
        caplog.set_level(logging.INFO)

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception(
            "429 ResourceExhausted: Quota exceeded"
        )

        generate_answer("How to reset bKash PIN?", _SAMPLE_CHUNKS)

        assert any("[FALLBACK]" in record.message for record in caplog.records)
        assert any("chunks_used=" in record.message for record in caplog.records)
        assert any("reason=" in record.message for record in caplog.records)

    def test_no_context_returns_default(self):
        """With no context, fallback should return default message."""
        result = generate_answer("How to reset PIN?", [])
        assert "enough information" in result["answer"]
        assert result["sources"] == []
        assert result["confidence"] == 0.0