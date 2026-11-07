"""TestClient tests for POST /api/chat — the dashboard chat endpoint.

Covers the contract the UI depends on: a successful chat returns the
model's reply, a backend failure is a 502 (not a 500 traceback), an
unreachable Ollama is a 503 whose message tells the user exactly what
to do (install vs. start the server), and a malformed request is a
422 from request validation.
"""
from fastapi.testclient import TestClient

from localforge import ollama
from localforge.server import app

client = TestClient(app, raise_server_exceptions=False)

PAYLOAD = {"model": "llama3.2:1b", "messages": [{"role": "user", "content": "hi"}]}


def test_chat_success_returns_reply(monkeypatch):
    monkeypatch.setattr(ollama, "is_available", lambda: True)
    monkeypatch.setattr(ollama, "chat", lambda m, msgs: "hello back")
    r = client.post("/api/chat", json=PAYLOAD)
    assert r.status_code == 200
    assert r.json() == {"reply": "hello back"}


def test_chat_passes_model_and_messages_through(monkeypatch):
    seen = {}

    def fake_chat(model, messages):
        seen["model"] = model
        seen["messages"] = messages
        return "ok"

    monkeypatch.setattr(ollama, "is_available", lambda: True)
    monkeypatch.setattr(ollama, "chat", fake_chat)
    r = client.post("/api/chat", json=PAYLOAD)
    assert r.status_code == 200
    assert seen["model"] == "llama3.2:1b"
    assert seen["messages"] == PAYLOAD["messages"]


def test_chat_failure_is_502(monkeypatch):
    def boom(model, messages):
        raise RuntimeError("connection reset")

    monkeypatch.setattr(ollama, "is_available", lambda: True)
    monkeypatch.setattr(ollama, "chat", boom)
    r = client.post("/api/chat", json=PAYLOAD)
    assert r.status_code == 502
    assert "Chat failed" in r.json()["detail"]


def test_chat_503_when_not_installed_links_download(monkeypatch):
    monkeypatch.setattr(ollama, "is_available", lambda: False)
    monkeypatch.setattr(ollama, "is_installed", lambda: False)
    r = client.post("/api/chat", json=PAYLOAD)
    assert r.status_code == 503
    assert ollama.DOWNLOAD_URL in r.json()["detail"]


def test_chat_503_when_not_running_says_serve(monkeypatch):
    monkeypatch.setattr(ollama, "is_available", lambda: False)
    monkeypatch.setattr(ollama, "is_installed", lambda: True)
    r = client.post("/api/chat", json=PAYLOAD)
    assert r.status_code == 503
    assert "ollama serve" in r.json()["detail"]


def test_chat_missing_model_is_422(monkeypatch):
    monkeypatch.setattr(ollama, "is_available", lambda: True)
    r = client.post("/api/chat", json={"messages": []})
    assert r.status_code == 422


def test_chat_missing_messages_is_422(monkeypatch):
    monkeypatch.setattr(ollama, "is_available", lambda: True)
    r = client.post("/api/chat", json={"model": "llama3.2:1b"})
    assert r.status_code == 422
