"""Tests for the --verbose CLI flag.

Asserts the flag (and the quiet default) is wired through to uvicorn as
INFO log level + access log. uvicorn and GPU detection are faked so the
tests run anywhere without hardware or deps.
"""
from __future__ import annotations

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


def test_verbose_enables_access_log_and_info_level(monkeypatch, capsys):
    kwargs = _uvicorn_kwargs(monkeypatch, ["--verbose"])
    assert kwargs["access_log"] is True
    assert kwargs["log_level"] == "info"


def test_default_is_quiet(monkeypatch, capsys):
    kwargs = _uvicorn_kwargs(monkeypatch, [])
    assert kwargs["access_log"] is False
    assert kwargs["log_level"] == "warning"
