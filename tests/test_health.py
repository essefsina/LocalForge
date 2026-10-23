"""Regression test: GET /api/health must not 500.

server.py's health endpoint (and the pull/chat 503 paths) reference
ollama.is_installed() and ollama.DOWNLOAD_URL. When those were missing
from ollama.py, every health check raised AttributeError -> 500, which
also broke the dashboard's Ollama status card. This pins the contract.
"""
from fastapi.testclient import TestClient

from localforge import ollama
from localforge.server import app

client = TestClient(app, raise_server_exceptions=False)


def test_health_returns_200_with_install_state(monkeypatch):
    monkeypatch.setattr(ollama, "is_available", lambda: True)
    monkeypatch.setattr(ollama, "is_installed", lambda: True)
    monkeypatch.setattr(ollama, "server_version", lambda: "0.12.3")
    monkeypatch.setattr(ollama, "api_shape_warnings", lambda: [])
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["ollama"] is True
    assert body["ollama_installed"] is True
    assert body["ollama_version"] == "0.12.3"
    assert body["api_warnings"] == []


def test_health_when_ollama_missing(monkeypatch):
    monkeypatch.setattr(ollama, "is_available", lambda: False)
    monkeypatch.setattr(ollama, "is_installed", lambda: False)
    monkeypatch.setattr(ollama, "server_version", lambda: None)
    monkeypatch.setattr(ollama, "api_shape_warnings", lambda: ["x"])
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["ollama_installed"] is False


def test_is_installed_detects_binary(monkeypatch):
    monkeypatch.setattr(ollama.shutil, "which",
                        lambda name: "/usr/local/bin/ollama" if name == "ollama" else None)
    assert ollama.is_installed() is True
    monkeypatch.setattr(ollama.shutil, "which", lambda name: None)
    assert ollama.is_installed() is False


def test_download_url_points_at_ollama():
    assert ollama.DOWNLOAD_URL.startswith("https://ollama.com/")
