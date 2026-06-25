"""Tests for OpenRouter LLM integration.

Mocks the OpenAI client (configured for OpenRouter) to verify:
- Successful chat completion response
- Invalid API key
- Timeout errors
- Model not found / unavailable
- Empty response handling
- Response schema (answer, sources, confidence)
- Fallback generation on any failure
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.llm.generator import _build_fallback_answer, generate_answer


_SAMPLE_CHUNK = {
    "text": "You can reset your bKash PIN by dialing *247#.",
    "source": "bkash_faq",
    "score": 0.95,
}


def _make_openrouter_response(text: str):
    """Build a mock OpenAI-style chat completion response."""
    choice = MagicMock()
    choice.message.content = text
    choice.finish_reason = "stop"

    response = MagicMock()
    response.choices = [choice]
    response.usage = MagicMock(total_tokens=123)
    return response


class TestOpenRouterSuccess:
    """Test normal OpenRouter response flow."""

    @patch("app.llm.generator._get_client")
    def test_basic_response(self, mock_get_client):
        """OpenRouter returns a normal completion."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.chat.completions.create.return_value = _make_openrouter_response(
            "Dial *247# to reset your bKash PIN."
        )

        result = generate_answer("How to reset bKash PIN?", [_SAMPLE_CHUNK])

        assert result["answer"] == "Dial *247# to reset your bKash PIN."
        assert result["sources"] == ["bkash_faq"]
        assert 0.0 <= result["confidence"] <= 1.0
        assert isinstance(result["confidence"], float)

    @patch("app.llm.generator._get_client")
    def test_response_with_multiple_chunks(self, mock_get_client):
        """OpenRouter synthesizes multiple chunks."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        chunks = [
            _SAMPLE_CHUNK,
            {
                "text": "You can also reset PIN via bKash app > Settings > Security.",
                "source": "bkash_faq",
                "score": 0.90,
            },
        ]
        mock_client.chat.completions.create.return_value = _make_openrouter_response(
            "To reset your bKash PIN:\n"
            "1. Dial *247# and select PIN reset, OR\n"
            "2. Use the bKash app: Settings > Security > Reset PIN."
        )

        result = generate_answer("How to reset bKash PIN?", chunks)

        assert "reset" in result["answer"].lower()
        assert "bkash_faq" in result["sources"]

    @patch("app.llm.generator._get_client")
    def test_logs_provider_and_model(self, mock_get_client, caplog):
        """Request should log provider=openrouter and model name."""
        import logging
        caplog.set_level(logging.INFO)

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.chat.completions.create.return_value = _make_openrouter_response("Hello")

        generate_answer("test", [_SAMPLE_CHUNK])

        assert any("provider=openrouter" in m for m in caplog.messages)
        assert any("model=" in m for m in caplog.messages)


class TestOpenRouterErrorHandling:
    """Test graceful degradation on OpenRouter API errors."""

    @patch("app.llm.generator._get_client")
    def test_invalid_api_key(self, mock_get_client):
        """Invalid API key triggers fallback with chunk content."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception(
            "401 PermissionDenied: API key invalid"
        )

        result = generate_answer("How to reset bKash PIN?", [_SAMPLE_CHUNK])

        assert "reset" in result["answer"].lower()
        assert result["sources"] == ["bkash_faq"]
        assert result["confidence"] >= 0.0

    @patch("app.llm.generator._get_client")
    def test_quota_exceeded(self, mock_get_client):
        """429 quota exceeded triggers fallback."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception(
            "429 Too Many Requests: Rate limit exceeded"
        )

        result = generate_answer("How to reset bKash PIN?", [_SAMPLE_CHUNK])

        assert "reset" in result["answer"].lower()
        assert result["sources"]

    @patch("app.llm.generator._get_client")
    def test_timeout(self, mock_get_client):
        """Timeout triggers fallback."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception(
            "DeadlineExceeded: Request timed out"
        )

        result = generate_answer("How to check balance?", [_SAMPLE_CHUNK])

        assert result["answer"]
        assert result["sources"]

    @patch("app.llm.generator._get_client")
    def test_model_unavailable(self, mock_get_client):
        """Model not found triggers fallback."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception(
            "404 Not Found: Model qwen/qwen3-8b:free is unavailable"
        )

        result = generate_answer("How to reset PIN?", [_SAMPLE_CHUNK])

        assert result["answer"]
        assert result["sources"]

    @patch("app.llm.generator._get_client")
    def test_empty_response_triggers_fallback(self, mock_get_client):
        """Empty content triggers fallback."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.chat.completions.create.return_value = _make_openrouter_response("")

        result = generate_answer("How to reset PIN?", [_SAMPLE_CHUNK])

        assert "reset" in result["answer"].lower()
        assert result["sources"]

    @patch("app.llm.generator._get_client")
    def test_connection_failure(self, mock_get_client):
        """Connection error triggers fallback."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception(
            "ConnectionError: Unable to reach https://openrouter.ai"
        )

        result = generate_answer("Hello", [_SAMPLE_CHUNK])

        assert result["answer"]
        assert result["sources"]


class TestOpenRouterMissingApiKey:
    """Test behavior when OPENROUTER_API_KEY is not configured."""

    @patch("app.llm.generator.Settings")
    def test_missing_api_key_returns_fallback(self, mock_settings):
        """Missing API key falls back instead of crashing."""
        mock_settings.return_value.openrouter_api_key = ""
        mock_settings.return_value.openrouter_model = "qwen/qwen3-8b:free"

        import app.llm.generator as gen_mod
        gen_mod._client = None

        result = generate_answer("test", [_SAMPLE_CHUNK])
        # Fallback uses chunk content
        assert "reset" in result["answer"].lower()
        assert result["sources"] == ["bkash_faq"]


class TestOpenRouterResponseFormat:
    """Verify response schema and logging."""

    @patch("app.llm.generator._get_client")
    def test_response_schema(self, mock_get_client):
        """Response must have answer, sources, confidence."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.chat.completions.create.return_value = _make_openrouter_response(
            "Answer from OpenRouter."
        )

        result = generate_answer("Hello", [_SAMPLE_CHUNK])

        assert "answer" in result
        assert "sources" in result
        assert "confidence" in result
        assert isinstance(result["answer"], str)
        assert isinstance(result["sources"], list)
        assert isinstance(result["confidence"], float)

    @patch("app.llm.generator._get_client")
    def test_empty_context_returns_default(self, mock_get_client):
        """Empty context returns default without calling OpenRouter."""
        result = generate_answer("Hello", [])

        assert "enough information" in result["answer"]
        assert result["sources"] == []
        assert result["confidence"] == 0.0
        mock_get_client.assert_not_called()

    @patch("app.llm.generator._get_client")
    def test_fallback_logs_fields(self, mock_get_client, caplog):
        """Fallback should log [LLM] latency, [FALLBACK] reason/chunks_used."""
        import logging
        caplog.set_level(logging.INFO)

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception(
            "429 Too Many Requests"
        )

        generate_answer("How to reset PIN?", [_SAMPLE_CHUNK])

        assert any("[FALLBACK]" in m for m in caplog.messages)
        assert any("reason=" in m for m in caplog.messages)
        assert any("chunks_used=" in m for m in caplog.messages)
        assert any("[LLM] latency=" in m for m in caplog.messages)