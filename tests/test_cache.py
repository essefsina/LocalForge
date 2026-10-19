"""Tests for localforge.cache — the recommendations snapshot cache."""
from __future__ import annotations

import json
import os

import pytest

from localforge import cache


@pytest.fixture
def cache_dir(tmp_path, monkeypatch):
    d = str(tmp_path / "lfcache")
    monkeypatch.setenv("LOCALFORGE_CACHE_DIR", d)
    return d


def test_round_trip(cache_dir):
    payload = {"budget_mb": 8500, "top_pick": "gemma3:12b", "fits": [], "too_big": []}
    path = cache.save_recommendations(payload)
    assert path == os.path.join(cache_dir, "recommendations.json")
    loaded = cache.load_cached_recommendations()
    assert loaded["budget_mb"] == 8500
    assert loaded["top_pick"] == "gemma3:12b"
    assert loaded["cached_at"]  # stamp travels with the payload


def test_missing_cache_returns_none(cache_dir):
    assert cache.load_cached_recommendations() is None


def test_corrupt_cache_returns_none(cache_dir):
    path = cache.cache_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("{not json")
    assert cache.load_cached_recommendations() is None


def test_wrong_shape_returns_none(cache_dir):
    path = cache.cache_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"cached_at": "x", "payload": ["not", "a", "dict"]}, f)
    assert cache.load_cached_recommendations() is None


def test_save_failure_is_silent(tmp_path, monkeypatch):
    # Point the cache at a path we cannot create; saving must not raise.
    ro = tmp_path / "ro"
    ro.mkdir()
    monkeypatch.setenv("LOCALFORGE_CACHE_DIR", str(ro / "x" / "y"))
    monkeypatch.setattr(os, "makedirs", lambda *a, **k: (_ for _ in ()).throw(OSError("nope")))
    cache.save_recommendations({"a": 1})  # no raise
