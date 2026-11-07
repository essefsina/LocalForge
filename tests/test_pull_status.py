"""TestClient tests for GET /api/pull/status — the dashboard's view
into a background model pull.

Covers the contract the UI polls on: a model with no pull at all is a
404 (not an empty progress bar), a pull in flight reports its status
plus a percentage derived from completed/total, a zero total is 0.0
rather than a division error, and a finished pull keeps its final
state instead of disappearing.
"""
import pytest
from fastapi.testclient import TestClient

from localforge.server import _pull_state, app

client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture(autouse=True)
def _clean_pull_state():
    _pull_state.clear()
    yield
    _pull_state.clear()


def _seed(model, **state):
    _pull_state[model] = state


def test_unknown_model_is_404():
    r = client.get("/api/pull/status", params={"model": "llama3.2:1b"})
    assert r.status_code == 404
    assert "no pull" in r.json()["detail"]


def test_pulling_state_reports_pct():
    _seed("qwen3:8b", status="pulling", completed=250, total=1000,
          detail="pulling manifest")
    r = client.get("/api/pull/status", params={"model": "qwen3:8b"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "pulling"
    assert body["pct"] == 25.0
    assert body["completed"] == 250
    assert body["total"] == 1000
    assert body["detail"] == "pulling manifest"


def test_zero_total_is_zero_pct_not_an_error():
    _seed("gemma3:4b", status="pulling", completed=0, total=0,
          detail="starting")
    r = client.get("/api/pull/status", params={"model": "gemma3:4b"})
    assert r.status_code == 200
    assert r.json()["pct"] == 0.0


def test_done_state_reports_full_pct():
    _seed("llama3.2:1b", status="done", completed=4700000000,
          total=4700000000, detail="success")
    r = client.get("/api/pull/status", params={"model": "llama3.2:1b"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "done"
    assert body["pct"] == 100.0


def test_error_state_keeps_its_detail():
    _seed("deepseek-r1:14b", status="error", completed=100, total=1000,
          detail="connection reset by peer")
    r = client.get("/api/pull/status", params={"model": "deepseek-r1:14b"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "error"
    assert body["detail"] == "connection reset by peer"
    assert body["pct"] == 10.0
