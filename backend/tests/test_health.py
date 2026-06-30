"""Tests for the health check and root endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestRoot:
    def test_root_returns_200(self: TestRoot) -> None:
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "status" in data
        assert "version" in data
        assert "docs" in data
        assert "openapi" in data
        assert "health" in data
        assert data["docs"] == "/docs"
        assert data["openapi"] == "/openapi.json"
        assert data["health"] == "/health"

    def test_root_status_running(self: TestRoot) -> None:
        response = client.get("/")
        data = response.json()
        assert data["status"] == "running"


class TestHealth:
    def test_health_returns_ok(self: TestHealth) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_health_returns_service(self: TestHealth) -> None:
        response = client.get("/health")
        data = response.json()
        assert data["service"] == "FinBot BD"

    def test_health_returns_version(self: TestHealth) -> None:
        response = client.get("/health")
        data = response.json()
        assert data["version"] == "1.0.0"

    def test_health_structure(self: TestHealth) -> None:
        response = client.get("/health")
        data = response.json()
        required_keys = {"status", "service", "version", "provider", "model"}
        for key in required_keys:
            assert key in data
