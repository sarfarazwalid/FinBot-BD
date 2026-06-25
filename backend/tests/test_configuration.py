"""Configuration and integration tests for FinBot BD."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.llm.generator import generate_answer
from app.main import app


_SAMPLE_CHUNK = {
    "text": "You can reset your bKash PIN by dialing *247#.",
    "source": "bkash_faq",
    "score": 0.95,
}


def test_settings_load_openrouter(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings correctly loads OpenRouter environment variables."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
    monkeypatch.setenv("OPENROUTER_MODEL", "test-model")
    monkeypatch.setenv("OPENROUTER_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("LLM_PROVIDER", "openrouter")

    settings = Settings()

    assert settings.openrouter_api_key == "sk-test"
    assert settings.openrouter_model == "test-model"
    assert settings.openrouter_base_url == "https://example.com/v1"
    assert settings.llm_provider == "openrouter"


def test_health_endpoint_provider() -> None:
    """GET /health returns provider=openrouter and correct model."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "openrouter"
    assert data["model"] == Settings().openrouter_model


def test_missing_openrouter_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing OPENROUTER_API_KEY triggers fallback, not a crash."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "")

    import app.llm.generator as gen_mod
    gen_mod._client = None

    with patch.object(gen_mod, "Settings") as mock_settings_cls:
        mock_settings = MagicMock()
        mock_settings.openrouter_api_key = ""
        mock_settings.openrouter_model = "qwen/qwen3-8b:free"
        mock_settings_cls.return_value = mock_settings

        result = generate_answer("test", [_SAMPLE_CHUNK])

    assert "reset" in result["answer"].lower()
    assert result["sources"] == ["bkash_faq"]
    assert result["confidence"] >= 0.0


def test_fallback_mode_enabled() -> None:
    """When OpenRouter fails, fallback synthesizes answer from chunks."""
    with patch("app.llm.generator._get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception(
            "ConnectionError: Unable to reach https://openrouter.ai"
        )

        result = generate_answer("How to reset bKash PIN?", [_SAMPLE_CHUNK])

    assert result["answer"]
    assert result["sources"] == ["bkash_faq"]
    assert 0.0 <= result["confidence"] <= 0.7
    assert "reset" in result["answer"].lower()


def test_openrouter_client_singleton() -> None:
    """_get_client returns the same instance on repeated calls."""
    with patch("app.llm.generator.Settings") as mock_settings_cls:
        mock_settings = MagicMock()
        mock_settings.openrouter_api_key = "sk-test"
        mock_settings.openrouter_base_url = "https://openrouter.ai/api/v1"
        mock_settings_cls.return_value = mock_settings

        import app.llm.generator as gen_mod
        gen_mod._client = None

        from app.llm.generator import _get_client

        client1 = _get_client()
        client2 = _get_client()

    assert client1 is client2
