"""Tests for the background model-pull endpoints.

Covers POST /api/pull (start + duplicate guard), GET /api/pull/status
(progress math + 404), and the _do_pull worker's terminal states.
No Ollama server needed — pull_stream and list_installed are stubbed;
the worker thread is awaited via polling.
"""
import threading
import time

import pytest
from fastapi.testclient import TestClient

from localforge import ollama
from localforge import server
from localforge.server import app

client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture(autouse=True)
def clean_pull_state():
    server._pull_state.clear()
    yield
    server._pull_state.clear()


def _wait_settled(model, timeout=5.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        st = server._pull_state.get(model)
        if st and st["status"] in ("done", "error"):
            return dict(st)
        time.sleep(0.02)
    raise AssertionError("pull for %r never settled: %r"
                         % (model, server._pull_state.get(model)))


def _online(monkeypatch):
    monkeypatch.setattr(ollama, "is_available", lambda: True)


def test_pull_starts_and_tracks_progress(monkeypatch):
    _online(monkeypatch)

    def fake_stream(model):
        yield {"status": "downloading", "total": 100, "completed": 40}
        yield {"status": "success"}

    monkeypatch.setattr(ollama, "pull_stream", fake_stream)
    monkeypatch.setattr(ollama, "list_installed",
                        lambda: [{"name": "qwen3:8b"}])

    r = client.post("/api/pull", json={"model": "qwen3:8b"})
    assert r.status_code == 200
    assert r.json() == {"ok": True, "started": True}

    state = _wait_settled("qwen3:8b")
    assert state["status"] == "done"
    assert state["completed"] == 40
    assert state["total"] == 100

    r = client.get("/api/pull/status", params={"model": "qwen3:8b"})
    assert r.status_code == 200
    assert r.json()["pct"] == 40.0


def test_duplicate_pull_returns_already_running(monkeypatch):
    _online(monkeypatch)
    started = threading.Event()
    release = threading.Event()

    def fake_stream(model):
        started.set()
        assert release.wait(5), "test did not release the fake stream"
        yield {"status": "success"}

    monkeypatch.setattr(ollama, "pull_stream", fake_stream)
    monkeypatch.setattr(ollama, "list_installed", lambda: [{"name": "m"}])

    r1 = client.post("/api/pull", json={"model": "m"})
    assert r1.json()["started"] is True
    assert started.wait(5), "worker thread never started"

    r2 = client.post("/api/pull", json={"model": "m"})
    assert r2.status_code == 200
    assert r2.json() == {"ok": True, "already_running": True}

    release.set()
    assert _wait_settled("m")["status"] == "done"


def test_pull_error_when_stream_raises(monkeypatch):
    _online(monkeypatch)

    def fake_stream(model):
        yield {"status": "downloading", "total": 10, "completed": 5}
        raise RuntimeError("connection dropped")

    monkeypatch.setattr(ollama, "pull_stream", fake_stream)

    client.post("/api/pull", json={"model": "m"})
    state = _wait_settled("m")
    assert state["status"] == "error"
    assert "connection dropped" in state["detail"]


def test_pull_error_when_stream_ends_silently(monkeypatch):
    # A dead stream with the model missing from Ollama must not read
    # as success.
    _online(monkeypatch)
    monkeypatch.setattr(ollama, "pull_stream", lambda model: iter(()))
    monkeypatch.setattr(ollama, "list_installed", lambda: [])

    client.post("/api/pull", json={"model": "m"})
    state = _wait_settled("m")
    assert state["status"] == "error"
    assert "without installing" in state["detail"]


def test_pull_status_404_for_unknown_model():
    r = client.get("/api/pull/status", params={"model": "never-pulled"})
    assert r.status_code == 404


def test_pull_status_progress_math():
    server._pull_state["m"] = {"status": "pulling", "completed": 1,
                               "total": 4, "detail": "downloading"}
    r = client.get("/api/pull/status", params={"model": "m"})
    assert r.json()["pct"] == 25.0

    server._pull_state["m"] = {"status": "pulling", "completed": 0,
                               "total": 0, "detail": "starting"}
    r = client.get("/api/pull/status", params={"model": "m"})
    assert r.json()["pct"] == 0.0
