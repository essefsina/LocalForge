"""Tests for ollama.server_version() and ollama.api_shape_warnings().

Simulates an Ollama server with httpx.MockTransport: a matching server,
a drifted API shape, and a dead server.
"""
from __future__ import annotations

import os
import sys

import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from localforge import ollama


def _patched(monkeypatch, handler):
    monkeypatch.setattr(ollama, "_client",
                        httpx.Client(transport=httpx.MockTransport(handler)))


def test_server_version(monkeypatch):
    def handler(request):
        assert request.url.path == "/api/version"
        return httpx.Response(200, json={"version": "0.12.3"})

    _patched(monkeypatch, handler)
    assert ollama.server_version() == "0.12.3"


def test_server_version_none_when_unreachable(monkeypatch):
    def handler(request):
        raise httpx.ConnectError("nope")

    _patched(monkeypatch, handler)
    assert ollama.server_version() is None


def test_server_version_none_on_unexpected_shape(monkeypatch):
    def handler(request):
        return httpx.Response(200, json=["not", "an", "object"])

    _patched(monkeypatch, handler)
    assert ollama.server_version() is None


def test_no_warnings_when_shape_matches(monkeypatch):
    def handler(request):
        return httpx.Response(200, json={"models": [{"name": "llama3.2:1b"}]})

    _patched(monkeypatch, handler)
    assert ollama.api_shape_warnings() == []


def test_warns_when_tags_shape_drifts(monkeypatch):
    def handler(request):
        if request.url.path == "/api/tags":
            return httpx.Response(200, json={"data": []})  # drifted shape
        return httpx.Response(200, json={"models": []})

    _patched(monkeypatch, handler)
    warnings = ollama.api_shape_warnings()
    assert len(warnings) == 1
    assert "/api/tags" in warnings[0]


def test_warns_for_both_endpoints_when_ollama_down(monkeypatch):
    def handler(request):
        raise httpx.ConnectError("nope")

    _patched(monkeypatch, handler)
    warnings = ollama.api_shape_warnings()
    assert len(warnings) == 2
    assert any("/api/tags" in w for w in warnings)
    assert any("/api/ps" in w for w in warnings)
