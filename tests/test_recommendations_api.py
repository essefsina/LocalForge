"""Tests for GET /api/recommendations, including its offline fallback.

The dashboard must still render when the GPU probe throws (hanging
driver, nvidia-smi mid-update): with a cached snapshot it serves that
snapshot flagged cached=True; without one it answers 503 instead of 500.
The GPU probe and cache are monkeypatched so no GPU or Ollama is needed.
"""

from fastapi.testclient import TestClient

import localforge.server as server
from localforge.gpu import GPUInfo

client = TestClient(server.app)


def _gpu(vram_mb: int) -> GPUInfo:
    return GPUInfo(
        name="Test GPU",
        vram_total_mb=vram_mb,
        vram_used_mb=0,
        utilization_pct=0,
        temperature_c=40,
    )


def test_success_returns_live_recommendations_and_caches_them(monkeypatch):
    saved = []
    monkeypatch.setattr(server, "primary_gpu", lambda: _gpu(8192))
    monkeypatch.setattr(server, "save_recommendations", lambda p: saved.append(p))
    resp = client.get("/api/recommendations")
    assert resp.status_code == 200
    data = resp.json()
    assert data["cached"] is False
    assert data["budget_mb"] == int(8192 * 0.85)
    assert data["top_pick"] is not None
    assert data["fits"], "an 8GB card should fit several models"
    assert len(saved) == 1


def test_probe_failure_serves_cached_snapshot(monkeypatch):
    cached = {
        "cached_at": "2026-10-24T00:00:00+00:00",
        "budget_mb": 6963,
        "top_pick": "qwen3:8b",
        "fits": [],
        "too_big": [],
    }
    monkeypatch.setattr(
        server, "primary_gpu", lambda: (_ for _ in ()).throw(RuntimeError("nvidia-smi hung"))
    )
    monkeypatch.setattr(server, "load_cached_recommendations", lambda: cached)
    resp = client.get("/api/recommendations")
    assert resp.status_code == 200
    data = resp.json()
    assert data["cached"] is True
    assert data["cached_at"] == "2026-10-24T00:00:00+00:00"
    assert data["budget_mb"] == 6963
    assert data["top_pick"] == "qwen3:8b"


def test_probe_failure_without_cache_is_503_not_500(monkeypatch):
    monkeypatch.setattr(
        server, "primary_gpu", lambda: (_ for _ in ()).throw(RuntimeError("nvidia-smi hung"))
    )
    monkeypatch.setattr(server, "load_cached_recommendations", lambda: None)
    resp = client.get("/api/recommendations")
    assert resp.status_code == 503
    assert "no cached recommendations" in resp.json()["detail"]
