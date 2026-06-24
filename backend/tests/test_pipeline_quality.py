"""Quality tests for the answer generation pipeline.

Verifies that generated answers never contain raw FAQ metadata labels.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.llm.generator import generate_answer


_FORBIDDEN = ["Question:", "Answer:", "Category:", "Language:", "====", "----"]

_SAMPLE_CHUNKS = [
    {
        "text": """==================================================

Question:
How to reset bKash PIN?

Answer:
You can reset your bKash PIN by dialing *247# and selecting the PIN reset option.

Category:
Security

Language:
en

==================================================""",
        "source": "bkash_faq",
        "score": 0.95,
    },
    {
        "text": """==================================================

Question:
Nagad PIN reset

Answer:
Dial *167#, select forgot PIN, enter registered mobile, verify with OTP.

Category:
Security

Language:
en

==================================================""",
        "source": "nagad_faq",
        "score": 0.90,
    },
]


class TestAnswerQuality:
    def test_answer_has_no_faq_labels(self: TestAnswerQuality) -> None:
        result = generate_answer("pin reset", _SAMPLE_CHUNKS)
        answer = result["answer"]
        for label in _FORBIDDEN:
            assert label not in answer, f"Answer contains forbidden label: {label}"

    def test_answer_has_sources(self: TestAnswerQuality) -> None:
        result = generate_answer("pin reset", _SAMPLE_CHUNKS)
        assert "bkash_faq" in result["sources"] or "nagad_faq" in result["sources"]

    def test_answer_has_confidence(self: TestAnswerQuality) -> None:
        result = generate_answer("pin reset", _SAMPLE_CHUNKS)
        assert isinstance(result["confidence"], float)
        assert 0.0 <= result["confidence"] <= 1.0

    def test_empty_context_returns_default(self: TestAnswerQuality) -> None:
        result = generate_answer("pin reset", [])
        assert "enough information" in result["answer"]
        assert result["sources"] == []
        assert result["confidence"] == 0.0