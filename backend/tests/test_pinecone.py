"""Tests for Pinecone configuration validation and error handling.

Covers:
- _validate_pinecone_config
- get_pinecone_status
- _get_pinecone_index with mocked client
- /debug/pinecone endpoint
- /health pinecone fields
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.retrieval.vector_store import (
    _validate_pinecone_config,
    get_pinecone_status,
    reset_pinecone_connection,
    _EXPECTED_DIMENSION,
    _get_pinecone_index,
)


# ---------------------------------------------------------------------------
# Config validation tests
# ---------------------------------------------------------------------------


class TestValidatePineconeConfig:
    @patch("app.retrieval.vector_store.Settings")
    def test_valid_config(self, mock_settings: MagicMock) -> None:
        mock_settings.return_value.pinecone_api_key = "test-key"
        mock_settings.return_value.pinecone_index_name = "finbot-bd"
        valid, error = _validate_pinecone_config()
        assert valid is True
        assert error is None

    @patch("app.retrieval.vector_store.Settings")
    def test_missing_api_key(self, mock_settings: MagicMock) -> None:
        mock_settings.return_value.pinecone_api_key = ""
        mock_settings.return_value.pinecone_index_name = "finbot-bd"
        valid, error = _validate_pinecone_config()
        assert valid is False
        assert "PINECONE_API_KEY" in (error or "")

    @patch("app.retrieval.vector_store.Settings")
    def test_missing_index_name(self, mock_settings: MagicMock) -> None:
        mock_settings.return_value.pinecone_api_key = "test-key"
        mock_settings.return_value.pinecone_index_name = ""
        valid, error = _validate_pinecone_config()
        assert valid is False
        assert "PINECONE_INDEX_NAME" in (error or "")

    @patch("app.retrieval.vector_store.Settings")
    def test_invalid_index_name_uppercase(self, mock_settings: MagicMock) -> None:
        mock_settings.return_value.pinecone_api_key = "test-key"
        mock_settings.return_value.pinecone_index_name = "FinBotBD"
        valid, error = _validate_pinecone_config()
        assert valid is False
        assert "invalid" in (error or "").lower()

    @patch("app.retrieval.vector_store.Settings")
    def test_invalid_index_name_underscore(self, mock_settings: MagicMock) -> None:
        mock_settings.return_value.pinecone_api_key = "test-key"
        mock_settings.return_value.pinecone_index_name = "finbot_bd"
        valid, error = _validate_pinecone_config()
        assert valid is False
        assert "invalid" in (error or "").lower()


# ---------------------------------------------------------------------------
# get_pinecone_status tests
# -------------------------------------------------------------------------


class TestGetPineconeStatus:
    def setup_method(self) -> None:
        reset_pinecone_connection()

    @patch("app.retrieval.vector_store.Settings")
    @patch("app.retrieval.vector_store._get_pinecone_index")
    def test_status_ok(self, mock_get_index: MagicMock, mock_settings: MagicMock) -> None:
        mock_settings.return_value.pinecone_api_key = "test-key"
        mock_settings.return_value.pinecone_index_name = "finbot-bd"

        mock_index = MagicMock()
        mock_index.describe_index_stats.return_value = {
            "dimension": _EXPECTED_DIMENSION,
            "metric": "cosine",
            "total_vector_count": 1234,
        }
        mock_get_index.return_value = mock_index

        status = get_pinecone_status()
        assert status["authenticated"] is True
        assert status["index_exists"] is True
        assert status["dimension"] == _EXPECTED_DIMENSION
        assert status["vector_count"] == 1234
        assert status["status"] == "ok"

    @patch("app.retrieval.vector_store.Settings")
    def test_status_missing_config(self, mock_settings: MagicMock) -> None:
        mock_settings.return_value.pinecone_api_key = ""
        mock_settings.return_value.pinecone_index_name = "finbot-bd"

        status = get_pinecone_status()
        assert status["authenticated"] is False
        assert status["api_key_present"] is False
        assert "error" in status

    @patch("app.retrieval.vector_store.Settings")
    @patch("app.retrieval.vector_store._get_pinecone_index")
    def test_status_pinecone_error(self, mock_get_index: MagicMock, mock_settings: MagicMock) -> None:
        mock_settings.return_value.pinecone_api_key = "test-key"
        mock_settings.return_value.pinecone_index_name = "finbot-bd"

        mock_get_index.side_effect = RuntimeError("Pinecone auth failed")

        status = get_pinecone_status()
        assert status["authenticated"] is False
        assert status["index_exists"] is False
        assert "auth" in status["error"].lower() or "failed" in status["error"].lower()


# ---------------------------------------------------------------------------
# _get_pinecone_index error handling tests
# ---------------------------------------------------------------------------


class TestGetPineconeIndex:
    def setup_method(self) -> None:
        reset_pinecone_connection()

    @patch("app.retrieval.vector_store.Settings")
    def test_missing_api_key(self, mock_settings: MagicMock) -> None:
        mock_settings.return_value.pinecone_api_key = ""
        mock_settings.return_value.pinecone_index_name = "finbot-bd"

        with pytest.raises(RuntimeError, match="PINECONE_API_KEY"):
            _get_pinecone_index()

    @patch("app.retrieval.vector_store.Settings")
    def test_invalid_index_name(self, mock_settings: MagicMock) -> None:
        mock_settings.return_value.pinecone_api_key = "test-key"
        mock_settings.return_value.pinecone_index_name = "invalid_name"

        with pytest.raises(RuntimeError, match="invalid"):
            _get_pinecone_index()

    @patch("app.retrieval.vector_store.Settings")
    def test_unauthorized_error(self, mock_settings: MagicMock) -> None:
        mock_settings.return_value.pinecone_api_key = "bad-key"
        mock_settings.return_value.pinecone_index_name = "finbot-bd"

        # Patch the pinecone module where it's imported inside _get_pinecone_index
        with patch.dict("sys.modules", {"pinecone": MagicMock(), "pinecone.ServerlessSpec": MagicMock()}):
            mock_pinecone = MagicMock()
            mock_pc = MagicMock()
            mock_pc.list_indexes.side_effect = Exception(
                "UnauthorizedError: [401] Invalid API key"
            )
            mock_pinecone.Pinecone.return_value = mock_pc
            import sys
            sys.modules["pinecone"] = mock_pinecone

            with pytest.raises(RuntimeError, match="authentication failed"):
                _get_pinecone_index()

    @patch("app.retrieval.vector_store.Settings")
    def test_dimension_mismatch(self, mock_settings: MagicMock) -> None:
        mock_settings.return_value.pinecone_api_key = "test-key"
        mock_settings.return_value.pinecone_index_name = "finbot-bd"

        mock_pinecone = MagicMock()
        mock_pc = MagicMock()
        mock_pc.list_indexes.return_value.names.return_value = ["finbot-bd"]
        mock_index = MagicMock()
        mock_index.describe_index_stats.return_value = {
            "dimension": 384,
            "metric": "cosine",
            "total_vector_count": 100,
        }
        mock_pc.Index.return_value = mock_index
        mock_pinecone.Pinecone.return_value = mock_pc

        with patch.dict("sys.modules", {"pinecone": mock_pinecone}):
            with pytest.raises(RuntimeError, match="dimension"):
                _get_pinecone_index()


# ---------------------------------------------------------------------------
# Endpoint tests
# ---------------------------------------------------------------------------


class TestPineconeEndpoints:
    def test_debug_pinecone_endpoint(self) -> None:
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.get("/debug/pinecone")
        assert response.status_code == 200
        data = response.json()
        assert "authenticated" in data
        assert "api_key_present" in data
        assert "index_name" in data
        assert "index_exists" in data

    def test_health_includes_pinecone_fields(self) -> None:
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "pinecone_index" in data
        assert "pinecone_authenticated" in data
        assert "pinecone_connected" in data