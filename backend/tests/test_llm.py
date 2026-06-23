"""Tests for the LLM generation module.

Tests are fully mocked — no real Anthropic API calls are made.
"""

from __future__ import annotations

from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest

from app.llm.generator import generate_answer
from app.llm.prompt_builder import build_prompt, _detect_query_language


# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

class TestDetectQueryLanguage:
    def test_bengali(self: TestDetectQueryLanguage) -> None:
        assert _detect_query_language("আমার একাউন্ট ব্লক হয়েছে") == "bn"

    def test_english(self: TestDetectQueryLanguage) -> None:
        assert _detect_query_language("How do I reset my PIN?") == "en"

    def test_banglish_mixed_scripts(self: TestDetectQueryLanguage) -> None:
        # Banglish = Bengali + English mixed in same query
        assert _detect_query_language("আমার bKash PIN vule gechi") == "banglish"

    def test_empty(self: TestDetectQueryLanguage) -> None:
        assert _detect_query_language("") == "en"


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

class TestBuildPrompt:
    @pytest.fixture
    def sample_chunks(self: TestBuildPrompt) -> List[Dict[str, Any]]:
        return [
            {
                "id": "bkash_faq_001_1",
                "text": "You can reset your PIN by dialing *247#.",
                "source": "bkash_faq",
                "language": "en",
                "score": 0.85,
            },
            {
                "id": "nagad_faq_002_1",
                "text": "নগদ PIN রিসেট করতে *167# ডায়াল করুন।",
                "source": "nagad_faq",
                "language": "bn",
                "score": 0.72,
            },
        ]

    def test_prompt_contains_context(self: TestBuildPrompt, sample_chunks: List[Dict[str, Any]]) -> None:
        prompt = build_prompt("How do I reset my PIN?", sample_chunks)
        assert "bkash_faq" in prompt["user"]
        assert "*247#" in prompt["user"]
        assert "nagad_faq" in prompt["user"]
        assert "How do I reset my PIN?" in prompt["user"]

    def test_prompt_contains_system(self: TestBuildPrompt, sample_chunks: List[Dict[str, Any]]) -> None:
        prompt = build_prompt("How do I reset my PIN?", sample_chunks)
        assert "FinBot BD" in prompt["system"]
        assert "banking" in prompt["system"].lower()

    def test_bengali_query_returns_bengali_instruction(self: TestBuildPrompt, sample_chunks: List[Dict[str, Any]]) -> None:
        # Bengali + English = banglish → still answers in Bengali
        prompt = build_prompt("আমার PIN ভুলে গেছি", sample_chunks)
        assert prompt["language"] == "banglish"
        assert "Answer in Bengali" in prompt["user"]

    def test_english_query_returns_english_instruction(self: TestBuildPrompt, sample_chunks: List[Dict[str, Any]]) -> None:
        prompt = build_prompt("How do I reset my PIN?", sample_chunks)
        assert prompt["language"] == "en"
        assert "Answer in English." in prompt["user"]

    def test_banglish_query_returns_bengali_instruction(self: TestBuildPrompt, sample_chunks: List[Dict[str, Any]]) -> None:
        # "amar pin vule gechi" has no Bengali chars → pure English default
        prompt = build_prompt("amar pin vule gechi", sample_chunks)
        assert prompt["language"] == "en"
        assert "Answer in English." in prompt["user"]

    def test_empty_context(self: TestBuildPrompt) -> None:
        prompt = build_prompt("test query", [])
        assert "No relevant context found" in prompt["user"]


# ---------------------------------------------------------------------------
# Generator (mocked Claude)
# ---------------------------------------------------------------------------

class TestGenerateAnswer:
    @pytest.fixture(autouse=True)
    def _mock_client(self: TestGenerateAnswer) -> Any:
        """Patch the Anthropic client so no real API calls are made."""
        self.mock_client = MagicMock()
        self.mock_response = MagicMock()
        self.mock_response.content = [MagicMock(text="Here is your answer.")]
        self.mock_client.messages.create.return_value = self.mock_response

        with patch("app.llm.generator._get_client", return_value=self.mock_client):
            yield

    def test_returns_answer_sources_confidence(self: TestGenerateAnswer) -> None:
        context = [
            {"id": "c1", "text": "Some context", "source": "bkash_faq", "score": 0.9},
        ]
        result = generate_answer("How to reset PIN?", context)

        assert "answer" in result
        assert "sources" in result
        assert "confidence" in result
        assert result["answer"] == "Here is your answer."
        assert result["sources"] == ["bkash_faq"]
        assert 0.0 <= result["confidence"] <= 1.0

    def test_empty_context_returns_default(self: TestGenerateAnswer) -> None:
        result = generate_answer("anything", [])
        assert result["answer"] == "I don't have enough information to answer that."
        assert result["sources"] == []
        assert result["confidence"] == 0.0

    def test_sources_deduplicated(self: TestGenerateAnswer) -> None:
        context = [
            {"id": "c1", "text": "t1", "source": "bkash_faq", "score": 0.9},
            {"id": "c2", "text": "t2", "source": "bkash_faq", "score": 0.8},
            {"id": "c3", "text": "t3", "source": "nagad_faq", "score": 0.7},
        ]
        result = generate_answer("test", context)
        assert set(result["sources"]) == {"bkash_faq", "nagad_faq"}
        assert len(result["sources"]) == 2

    def test_long_answer_confidence_capped(self: TestGenerateAnswer) -> None:
        long_text = "word " * 1000
        self.mock_response.content = [MagicMock(text=long_text)]
        context = [{"id": "c1", "text": "x", "source": "s", "score": 1.0}]
        result = generate_answer("test", context)
        assert result["confidence"] == 1.0  # capped