"""Tests for Ollama presence detection and the friendly error paths.

No Ollama binary or server needed — everything is monkeypatched.
"""
from fastapi.testclient import TestClient

from localforge import ollama
from localforge.server import app

client = TestClient(app, raise_server_exceptions=False)


def test_is_installed_true(monkeypatch):
    monkeypatch.setattr(ollama.shutil, "which", lambda name: "/usr/local/bin/ollama")
    assert ollama.is_installed() is True


def test_is_installed_false(monkeypatch):
    monkeypatch.setattr(ollama.shutil, "which", lambda name: None)
    assert ollama.is_installed() is False


def test_health_reports_install_state(monkeypatch):
    monkeypatch.setattr(ollama, "is_available", lambda: False)
    monkeypatch.setattr(ollama, "is_installed", lambda: False)
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["ollama"] is False
    assert body["ollama_installed"] is False


def test_health_healthy_shape(monkeypatch):
    monkeypatch.setattr(ollama, "is_available", lambda: True)
    monkeypatch.setattr(ollama, "is_installed", lambda: True)
    body = client.get("/api/health").json()
    assert body == {"ok": True, "ollama": True, "ollama_installed": True}


def test_pull_503_when_not_installed_links_download(monkeypatch):
    monkeypatch.setattr(ollama, "is_available", lambda: False)
    monkeypatch.setattr(ollama, "is_installed", lambda: False)
    r = client.post("/api/pull", json={"model": "llama3.2:3b"})
    assert r.status_code == 503
    assert "ollama.com/download" in r.json()["detail"]


def test_pull_503_when_not_running_says_serve(monkeypatch):
    monkeypatch.setattr(ollama, "is_available", lambda: False)
    monkeypatch.setattr(ollama, "is_installed", lambda: True)
    r = client.post("/api/pull", json={"model": "llama3.2:3b"})
    assert r.status_code == 503
    detail = r.json()["detail"]
    assert "ollama serve" in detail
    assert "ollama.com/download" not in detail


def test_chat_503_when_not_installed_links_download(monkeypatch):
    monkeypatch.setattr(ollama, "is_available", lambda: False)
    monkeypatch.setattr(ollama, "is_installed", lambda: False)
    r = client.post("/api/chat", json={"model": "x", "messages": []})
    assert r.status_code == 503
    assert "ollama.com/download" in r.json()["detail"]
