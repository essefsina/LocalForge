"""Tests for the --host / --port CLI flags.

The bind address the user passes on the command line must reach
uvicorn unchanged, and the defaults must stay 127.0.0.1:8000 so the
dashboard keeps listening on localhost unless asked otherwise.
uvicorn and GPU detection are faked so the tests run anywhere
without hardware or a real server (same approach as
test_cli_verbose.py).
"""
import os
import sys
import types

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import localforge.__main__ as cli


def _uvicorn_kwargs(monkeypatch, argv):
    captured = {}

    fake_uvicorn = types.SimpleNamespace(run=lambda *a, **k: captured.update(kwargs=k))
    # main() does `import uvicorn` and `from .server import app` internally -
    # fake both so the tests need neither installed.
    monkeypatch.setitem(sys.modules, "uvicorn", fake_uvicorn)
    monkeypatch.setitem(sys.modules, "localforge.server",
                        types.SimpleNamespace(app=object()))
    monkeypatch.setattr(cli, "detect_gpus", lambda: [])
    monkeypatch.setattr(sys, "argv", ["localforge"] + argv)
    cli.main()
    return captured["kwargs"]


def test_custom_host_and_port_reach_uvicorn(monkeypatch):
    kwargs = _uvicorn_kwargs(monkeypatch, ["--host", "0.0.0.0", "--port", "9000"])
    assert kwargs["host"] == "0.0.0.0"
    assert kwargs["port"] == 9000


def test_defaults_are_localhost_8000(monkeypatch):
    kwargs = _uvicorn_kwargs(monkeypatch, [])
    assert kwargs["host"] == "127.0.0.1"
    assert kwargs["port"] == 8000


def test_port_only_keeps_default_host(monkeypatch):
    kwargs = _uvicorn_kwargs(monkeypatch, ["--port", "8080"])
    assert kwargs["host"] == "127.0.0.1"
    assert kwargs["port"] == 8080
