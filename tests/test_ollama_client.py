"""Tests for the localforge.ollama HTTP client (is_available,
list_installed, running, chat) — no Ollama server required.

httpx.MockTransport stands in for Ollama: an up server, a down server,
a non-200 server, and an empty model list. server_version() and
api_shape_warnings() already have their own tests in
test_ollama_version.py and are not duplicated here.
"""
from __future__ import annotations

import os
import sys

import httpx
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from localforge import ollama


def _patched(monkeypatch, handler):
    monkeypatch.setattr(ollama, "_client",
                        httpx.Client(transport=httpx.MockTransport(handler)))


def _tags_handler(request):
    if request.url.path == "/api/tags":
        return httpx.Response(200, json={"models": [
            {"name": "llama3.2:1b"}, {"name": "qwen2.5:3b"}]})
    if request.url.path == "/api/ps":
        return httpx.Response(200, json={"models": [
            {"name": "llama3.2:1b"}]})
    if request.url.path == "/api/chat":
        return httpx.Response(200, json={"message": {"content": "hello back"}})
    return httpx.Response(404, json={})


def test_is_available_true_on_200(monkeypatch):
    _patched(monkeypatch, _tags_handler)
    assert ollama.is_available() is True


def test_is_available_false_on_non_200(monkeypatch):
    def handler(request):
        return httpx.Response(500, json={})

    _patched(monkeypatch, handler)
    assert ollama.is_available() is False


def test_is_available_false_when_down(monkeypatch):
    def handler(request):
        raise httpx.ConnectError("nope")

    _patched(monkeypatch, handler)
    assert ollama.is_available() is False


def test_list_installed_returns_model_names(monkeypatch):
    _patched(monkeypatch, _tags_handler)
    models = ollama.list_installed()
    assert [m["name"] for m in models] == ["llama3.2:1b", "qwen2.5:3b"]


def test_running_returns_running_models_only(monkeypatch):
    _patched(monkeypatch, _tags_handler)
    assert [m["name"] for m in ollama.running()] == ["llama3.2:1b"]


def test_empty_model_lists(monkeypatch):
    def handler(request):
        return httpx.Response(200, json={"models": []})

    _patched(monkeypatch, handler)
    assert ollama.list_installed() == []
    assert ollama.running() == []


def test_chat_returns_content(monkeypatch):
    _patched(monkeypatch, _tags_handler)
    reply = ollama.chat("llama3.2:1b",
                        [{"role": "user", "content": "hi"}])
    assert reply == "hello back"


def test_chat_propagates_server_error(monkeypatch):
    def handler(request):
        return httpx.Response(500, json={"error": "boom"})

    _patched(monkeypatch, handler)
    with pytest.raises(httpx.HTTPStatusError):
        ollama.chat("llama3.2:1b", [{"role": "user", "content": "hi"}])
