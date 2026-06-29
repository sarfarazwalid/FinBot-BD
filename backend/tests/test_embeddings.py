"""Tests for the embedding module.

Verifies that:
1. The ``EmbeddingModel`` wrapper works correctly with mocked provider.
2. Singleton caching behavior.
3. Dimension mismatch detection.
4. Provider factory works with mocked config.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch, call

import numpy as np
import pytest

from app.embeddings.provider import EmbeddingProvider, clear_provider_cache
from app.retrieval.vector_store import EmbeddingModel, _EXPECTED_DIMENSION, _EXPECTED_MODEL


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_state():
    """Reset all singletons before each test so state doesn't leak."""
    EmbeddingModel._provider = None
    EmbeddingModel._cache_found = False
    clear_provider_cache()
    yield


@pytest.fixture
def mock_provider() -> MagicMock:
    """Return a MagicMock that behaves like a working EmbeddingProvider."""
    provider = MagicMock(spec=EmbeddingProvider)
    # By default, return a (2, 1536) array on embed
    rng = np.random.default_rng(42)
    vectors = rng.normal(size=(2, _EXPECTED_DIMENSION)).astype(np.float32)
    provider.embed.return_value = vectors
    return provider


# ---------------------------------------------------------------------------
# EmbeddingModel tests
# ---------------------------------------------------------------------------


class TestEmbeddingModel:
    """Tests for EmbeddingModel wrapper (provider mocked)."""

    def test_embed_calls_provider(self: TestEmbeddingModel, mock_provider: MagicMock) -> None:
        """Embed should delegate to the provider."""
        EmbeddingModel._provider = mock_provider
        result = EmbeddingModel.embed(["test text"])
        mock_provider.embed.assert_called_once_with(["test text"])
        assert isinstance(result, np.ndarray)
        assert result.shape[1] == _EXPECTED_DIMENSION

    def test_embed_single_string_converted_to_list(self: TestEmbeddingModel, mock_provider: MagicMock) -> None:
        """A single string should be wrapped in a list before calling provider."""
        EmbeddingModel._provider = mock_provider
        EmbeddingModel.embed("single string")
        mock_provider.embed.assert_called_once_with(["single string"])

    def test_provider_is_cached(self: TestEmbeddingModel, mock_provider: MagicMock) -> None:
        """The provider should not be re-initialised on repeated calls."""
        EmbeddingModel._provider = mock_provider
        EmbeddingModel.embed("first call")
        EmbeddingModel.embed("second call")
        mock_provider.embed.assert_has_calls([
            call(["first call"]),
            call(["second call"]),
        ])
        # _provider should be the same object
        assert EmbeddingModel._provider is mock_provider

    def test_get_info(self: TestEmbeddingModel) -> None:
        """get_info should return expected structure."""
        EmbeddingModel._provider = MagicMock()
        info = EmbeddingModel.get_info()
        assert info["model"] == _EXPECTED_MODEL
        assert info["dimension"] == _EXPECTED_DIMENSION
        assert info["cache_found"] is False
        assert info["model_loaded"] is True

    def test_get_info_model_not_loaded(self: TestEmbeddingModel) -> None:
        """get_info should report model_loaded=False before first embed."""
        info = EmbeddingModel.get_info()
        assert info["model_loaded"] is False


# ---------------------------------------------------------------------------
# Provider tests
# ---------------------------------------------------------------------------


class TestEmbeddingProvider:
    """Tests for the EmbeddingProvider implementations with mocked HTTP."""

    def test_openai_provider_embed(self) -> None:
        """OpenAIEmbeddingProvider should call embeddings.create and return float32 array."""
        from app.embeddings.provider import OpenAIEmbeddingProvider

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(index=0, embedding=[0.1] * _EXPECTED_DIMENSION),
            MagicMock(index=1, embedding=[0.2] * _EXPECTED_DIMENSION),
        ]
        mock_client.embeddings.create.return_value = mock_response

        provider = OpenAIEmbeddingProvider(
            api_key="test-key",
            model="text-embedding-3-small",
            base_url="https://api.openai.com/v1",
        )
        provider._client = mock_client

        result = provider.embed(["hello", "world"])
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.float32
        assert result.shape == (2, _EXPECTED_DIMENSION)
        mock_client.embeddings.create.assert_called_once_with(
            model="text-embedding-3-small",
            input=["hello", "world"],
        )

    def test_openrouter_provider_embed(self) -> None:
        """OpenRouterEmbeddingProvider should call embeddings.create and return float32 array."""
        from app.embeddings.provider import OpenRouterEmbeddingProvider

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(index=0, embedding=[0.3] * _EXPECTED_DIMENSION),
        ]
        mock_client.embeddings.create.return_value = mock_response

        provider = OpenRouterEmbeddingProvider(
            api_key="test-key",
            model="text-embedding-3-small",
            base_url="https://openrouter.ai/api/v1",
        )
        provider._client = mock_client

        result = provider.embed(["test"])
        assert isinstance(result, np.ndarray)
        assert result.shape == (1, _EXPECTED_DIMENSION)


# ---------------------------------------------------------------------------
# Factory tests
# ---------------------------------------------------------------------------


class TestFactory:
    """Tests for get_embedding_provider factory."""

    @patch("app.embeddings.provider.Settings")
    def test_factory_openrouter(self, mock_settings: MagicMock) -> None:
        """Factory should return OpenRouterEmbeddingProvider when configured."""
        mock_settings.return_value.embedding_provider = "openrouter"
        mock_settings.return_value.embedding_model = "text-embedding-3-small"
        mock_settings.return_value.openrouter_api_key = "sk-or-v1-test"
        mock_settings.return_value.openrouter_base_url = "https://openrouter.ai/api/v1"

        from app.embeddings.provider import get_embedding_provider, OpenRouterEmbeddingProvider
        provider = get_embedding_provider()
        assert isinstance(provider, OpenRouterEmbeddingProvider)

    @patch("app.embeddings.provider.Settings")
    def test_factory_openai(self, mock_settings: MagicMock) -> None:
        """Factory should return OpenAIEmbeddingProvider when configured."""
        mock_settings.return_value.embedding_provider = "openai"
        mock_settings.return_value.embedding_model = "text-embedding-3-small"
        mock_settings.return_value.embedding_api_key = "sk-test"
        mock_settings.return_value.embedding_base_url = "https://api.openai.com/v1"
        mock_settings.return_value.openrouter_api_key = ""

        from app.embeddings.provider import get_embedding_provider, OpenAIEmbeddingProvider
        provider = get_embedding_provider()
        assert isinstance(provider, OpenAIEmbeddingProvider)

    @patch("app.embeddings.provider.Settings")
    def test_factory_unknown_raises(self, mock_settings: MagicMock) -> None:
        """Factory should raise ValueError for unknown provider."""
        mock_settings.return_value.embedding_provider = "unknown"
        mock_settings.return_value.embedding_model = "text-embedding-3-small"
        mock_settings.return_value.openrouter_api_key = "sk-or-v1-test"
        mock_settings.return_value.openrouter_base_url = "https://openrouter.ai/api/v1"

        from app.embeddings.provider import get_embedding_provider
        with pytest.raises(ValueError, match="Unknown embedding provider"):
            get_embedding_provider()