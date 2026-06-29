"""Tests for the embedding module.

Verifies that:
1. The ``EmbeddingModel`` class loads correctly.
2. Generated embeddings have the expected dimension (384).
3. Embeddings are normalized (unit vectors for cosine similarity).
"""

from __future__ import annotations

import numpy as np
import pytest

from app.retrieval.vector_store import EmbeddingModel, _EXPECTED_DIMENSION, _EXPECTED_MODEL


class TestEmbeddingModel:
    """Integration tests for EmbeddingModel (downloads the model once)."""

    @pytest.fixture(autouse=True)
    def _reset_model(self: TestEmbeddingModel):
        """Reset the singleton before each test so state doesn't leak."""
        EmbeddingModel._model = None
        yield

    # ------------------------------------------------------------------
    # Basic dimension validation
    # ------------------------------------------------------------------

    def test_embed_single_text(self: TestEmbeddingModel) -> None:
        """A single text should produce a 1-D array reshaped to 2-D."""
        vector = EmbeddingModel.embed("amar bKash pin vule gechi")
        assert isinstance(vector, np.ndarray)
        assert vector.shape == (1, _EXPECTED_DIMENSION), (
            f"Expected (1, {_EXPECTED_DIMENSION}), got {vector.shape}"
        )
        assert _EXPECTED_DIMENSION == 384

    def test_embed_multiple_texts(self: TestEmbeddingModel) -> None:
        """Multiple texts should produce a batch of vectors."""
        texts = [
            "amar bKash pin vule gechi",
            "How do I reset my PIN?",
            "আমার একাউন্ট ব্লক হয়েছে",
        ]
        vectors = EmbeddingModel.embed(texts)
        assert isinstance(vectors, np.ndarray)
        assert vectors.shape == (3, _EXPECTED_DIMENSION), (
            f"Expected (3, {_EXPECTED_DIMENSION}), got {vectors.shape}"
        )

    # ------------------------------------------------------------------
    # Normalization check
    # ------------------------------------------------------------------

    def test_embeddings_are_normalized(self: TestEmbeddingModel) -> None:
        """Check that the model outputs L2-normalized vectors (unit length)."""
        vector = EmbeddingModel.embed("amar bKash pin vule gechi")
        norm = np.linalg.norm(vector, axis=1)
        # Allow small floating-point tolerance.
        assert np.allclose(norm, 1.0, atol=1e-5), (
            f"Expected unit vectors, got norms: {norm}"
        )

    # ------------------------------------------------------------------
    # Dimension mismatch detection
    # ------------------------------------------------------------------

    def test_dimension_mismatch_raises(self: TestEmbeddingModel) -> None:
        """If the expected dimension changes, the model should raise."""
        # Temporarily patch the expected dimension constant.
        import app.retrieval.vector_store as vs

        original_dim = vs._EXPECTED_DIMENSION
        original_model = vs._EXPECTED_MODEL
        vs._EXPECTED_DIMENSION = 9999  # wrong dimension
        try:
            with pytest.raises(RuntimeError, match="returned dimension"):
                EmbeddingModel.embed("test")
        finally:
            vs._EXPECTED_DIMENSION = original_dim
            vs._EXPECTED_MODEL = original_model

    # ------------------------------------------------------------------
    # Idempotency / caching
    # ------------------------------------------------------------------

    def test_model_is_cached(self: TestEmbeddingModel) -> None:
        """Loading the model twice should return the same cached instance."""
        EmbeddingModel.embed("first call")
        model_ref = EmbeddingModel._model
        assert model_ref is not None

        EmbeddingModel.embed("second call")
        assert EmbeddingModel._model is model_ref, "Model was reloaded"