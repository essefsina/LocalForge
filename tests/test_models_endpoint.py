"""Tests for GET /api/models — the dashboard's installed/running list.

The endpoint must not leak a raw Ollama connection error: when Ollama
is down it answers with empty lists and ollama_up False, and when it
is up it reports exactly the names Ollama returned. Ollama is
monkeypatched, so no server or GPU is needed.
"""
from fastapi.testclient import TestClient

import localforge.server as server

client = TestClient(server.app)


def _patch_ollama(monkeypatch, up, installed, running):
    monkeypatch.setattr(server.ollama, "is_available", lambda: up)
    monkeypatch.setattr(server.ollama, "list_installed", installed)
    monkeypatch.setattr(server.ollama, "running", running)


def test_ollama_up_reports_installed_and_running(monkeypatch):
    _patch_ollama(
        monkeypatch, True,
        lambda: [{"name": "llama3.2:1b"}, {"name": "qwen2.5:3b"}],
        lambda: [{"name": "llama3.2:1b"}],
    )
    resp = client.get("/api/models")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ollama_up"] is True
    assert data["installed"] == ["llama3.2:1b", "qwen2.5:3b"]
    assert data["running"] == ["llama3.2:1b"]


def test_ollama_down_reports_empty_lists(monkeypatch):
    def _boom():
        raise AssertionError("must not be called when Ollama is down")

    _patch_ollama(monkeypatch, False, _boom, _boom)
    resp = client.get("/api/models")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ollama_up"] is False
    assert data["installed"] == []
    assert data["running"] == []


def test_ollama_up_with_no_models(monkeypatch):
    _patch_ollama(monkeypatch, True, lambda: [], lambda: [])
    resp = client.get("/api/models")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ollama_up"] is True
    assert data["installed"] == []
    assert data["running"] == []
