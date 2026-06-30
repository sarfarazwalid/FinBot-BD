"""Tests for CORS configuration and preflight handling."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestCorsPreflight:
    def test_options_chat_returns_200(self: TestCorsPreflight) -> None:
        """OPTIONS preflight for /api/v1/chat must return 200."""
        response = client.options(
            "/api/v1/chat",
            headers={
                "Origin": "https://fin-bot-bd.vercel.app",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        assert response.status_code == 200

    def test_options_chat_contains_cors_headers(self: TestCorsPreflight) -> None:
        """OPTIONS response must include CORS headers."""
        response = client.options(
            "/api/v1/chat",
            headers={
                "Origin": "https://fin-bot-bd.vercel.app",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        assert response.status_code == 200
        # FastAPI/CORSMiddleware sets these on the response
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers

    def test_options_chat_allows_vercel_origin(self: TestCorsPreflight) -> None:
        """Vercel origin must be allowed."""
        response = client.options(
            "/api/v1/chat",
            headers={
                "Origin": "https://fin-bot-bd.vercel.app",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.status_code == 200
        allow_origin = response.headers.get("access-control-allow-origin", "")
        assert "https://fin-bot-bd.vercel.app" in allow_origin

    def test_options_chat_allows_localhost(self: TestCorsPreflight) -> None:
        """localhost:3000 must still be allowed for development."""
        response = client.options(
            "/api/v1/chat",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.status_code == 200
        allow_origin = response.headers.get("access-control-allow-origin", "")
        assert "http://localhost:3000" in allow_origin


class TestDebugCors:
    def test_debug_cors_returns_config(self: TestDebugCors) -> None:
        response = client.get("/debug/cors")
        assert response.status_code == 200
        data = response.json()
        assert "allowed_origins" in data
        assert "allow_credentials" in data
        assert "allow_methods" in data
        assert "allow_headers" in data
        assert data["allow_credentials"] is True
        assert data["allow_methods"] == ["*"]
        assert data["allow_headers"] == ["*"]

    def test_debug_cors_includes_vercel(self: TestDebugCors) -> None:
        response = client.get("/debug/cors")
        data = response.json()
        assert "https://fin-bot-bd.vercel.app" in data["allowed_origins"]

    def test_debug_cors_includes_localhost(self: TestDebugCors) -> None:
        response = client.get("/debug/cors")
        data = response.json()
        assert "http://localhost:3000" in data["allowed_origins"]
        assert "http://localhost:3001" in data["allowed_origins"]