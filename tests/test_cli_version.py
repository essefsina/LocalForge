"""Tests for the --version (and --help) CLI flags.

argparse handles both before main() ever touches uvicorn or the GPU,
so these run in-process with no server, hardware, or extra deps.
"""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import localforge.__main__ as cli  # noqa: E402
from localforge import __version__  # noqa: E402


def test_version_flag_prints_name_and_version(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["localforge", "--version"])
    with pytest.raises(SystemExit) as excinfo:
        cli.main()
    assert excinfo.value.code == 0
    assert capsys.readouterr().out.strip() == f"localforge {__version__}"


def test_help_flag_exits_cleanly_and_names_the_tool(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["localforge", "--help"])
    with pytest.raises(SystemExit) as excinfo:
        cli.main()
    assert excinfo.value.code == 0
    out = capsys.readouterr().out
    assert "Turn your gaming PC into a private AI server." in out
    assert "--port" in out
    assert "--verbose" in out
