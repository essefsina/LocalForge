"""Tests for GET /api/gpu — the dashboard's GPU readout.

With no NVIDIA GPU the endpoint reports an empty list and a null
primary instead of erroring, matching the dashboard's CPU-only mode.
With a GPU present it surfaces the GPUInfo dict, including the
derived GB values the frontend displays.
"""
from fastapi.testclient import TestClient

import localforge.server as server
from localforge.gpu import GPUInfo

client = TestClient(server.app)


def _gpu() -> GPUInfo:
    return GPUInfo(
        name="Test GPU",
        vram_total_mb=8192,
        vram_used_mb=1024,
        utilization_pct=10,
        temperature_c=40,
    )


def test_no_gpu_returns_empty_list_and_null_primary(monkeypatch):
    monkeypatch.setattr(server, "detect_gpus", lambda: [])
    monkeypatch.setattr(server, "primary_gpu", lambda: None)
    resp = client.get("/api/gpu")
    assert resp.status_code == 200
    assert resp.json() == {"gpus": [], "primary": None}


def test_one_gpu_returns_its_dict_in_both_fields(monkeypatch):
    gpu = _gpu()
    monkeypatch.setattr(server, "detect_gpus", lambda: [gpu])
    monkeypatch.setattr(server, "primary_gpu", lambda: gpu)
    resp = client.get("/api/gpu")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["gpus"]) == 1
    assert data["primary"] == data["gpus"][0]
    entry = data["gpus"][0]
    assert entry["name"] == "Test GPU"
    assert entry["vram_total_mb"] == 8192
    assert entry["vram_used_mb"] == 1024
    assert entry["vram_total_gb"] == 8.0
    assert entry["vram_used_gb"] == 1.0
    assert entry["vram_free_gb"] == 7.0
    assert entry["utilization_pct"] == 10
    assert entry["temperature_c"] == 40
