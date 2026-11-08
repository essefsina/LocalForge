"""Tests for ollama.pull_stream() itself.

test_pull_api.py stubs pull_stream at the server boundary; these tests
exercise the real generator against a fake Ollama server built with
httpx.MockTransport: NDJSON status lines, blank lines, error statuses,
and non-200 responses. No Ollama server needed.
"""
from __future__ import annotations

import json
import os
import sys

import httpx
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from localforge import ollama  # noqa: E402


def _patched(monkeypatch, handler):
    monkeypatch.setattr(ollama, "_client",
                        httpx.Client(transport=httpx.MockTransport(handler)))


def _ndjson(*events):
    return ("\n".join(json.dumps(e) for e in events) + "\n").encode()


def test_yields_status_dicts_in_order(monkeypatch):
    events = [
        {"status": "pulling manifest"},
        {"status": "downloading", "total": 1000, "completed": 400},
        {"status": "downloading", "total": 1000, "completed": 1000},
        {"status": "verifying sha256 digest"},
        {"status": "success"},
    ]

    def handler(request):
        assert request.url.path == "/api/pull"
        assert json.loads(request.content) == {"name": "qwen3:8b"}
        return httpx.Response(200, content=_ndjson(*events))

    _patched(monkeypatch, handler)
    assert list(ollama.pull_stream("qwen3:8b")) == events


def test_blank_lines_are_skipped(monkeypatch):
    body = b'{"status": "pulling manifest"}\n\n\n{"status": "success"}\n'

    def handler(request):
        return httpx.Response(200, content=body)

    _patched(monkeypatch, handler)
    assert list(ollama.pull_stream("llama3.2:1b")) == [
        {"status": "pulling manifest"},
        {"status": "success"},
    ]


def test_empty_stream_yields_nothing(monkeypatch):
    def handler(request):
        return httpx.Response(200, content=b"")

    _patched(monkeypatch, handler)
    assert list(ollama.pull_stream("llama3.2:1b")) == []


def test_error_status_raises_with_server_message(monkeypatch):
    def handler(request):
        return httpx.Response(200, content=_ndjson(
            {"status": "pulling manifest"},
            {"status": "error", "error": "model not found"},
        ))

    _patched(monkeypatch, handler)
    with pytest.raises(RuntimeError, match="model not found"):
        list(ollama.pull_stream("nope:1b"))


def test_error_status_without_message_gets_default(monkeypatch):
    def handler(request):
        return httpx.Response(200, content=_ndjson(
            {"status": "error"},
        ))

    _patched(monkeypatch, handler)
    with pytest.raises(RuntimeError, match="Ollama reported a pull error"):
        list(ollama.pull_stream("nope:1b"))


def test_non_200_response_raises(monkeypatch):
    def handler(request):
        return httpx.Response(404, json={"error": "not found"})

    _patched(monkeypatch, handler)
    with pytest.raises(httpx.HTTPStatusError):
        list(ollama.pull_stream("nope:1b"))
