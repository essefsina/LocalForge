"""Minimal Ollama HTTP client (http://localhost:11434 by default)."""
from __future__ import annotations

import os

import httpx

BASE_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
TIMEOUT = httpx.Timeout(10.0, read=300.0)

# Bypass proxy env vars: Ollama is always a localhost service, and a
# misconfigured proxy must never break local calls.
_client = httpx.Client(trust_env=False, timeout=TIMEOUT)


def is_available() -> bool:
    """Boolean probe — never raises, even with a broken network/proxy setup."""
    try:
        r = _client.get(f"{BASE_URL}/api/tags", timeout=5.0)
        return r.status_code == 200
    except Exception:  # noqa: BLE001
        return False


def list_installed() -> list[dict]:
    r = _client.get(f"{BASE_URL}/api/tags")
    r.raise_for_status()
    return r.json().get("models", [])


def running() -> list[dict]:
    r = _client.get(f"{BASE_URL}/api/ps")
    r.raise_for_status()
    return r.json().get("models", [])


def pull_stream(model: str):
    """Yield raw status dicts from Ollama as the pull progresses.

    Raises RuntimeError if Ollama reports the pull failed — callers must
    not treat a dead stream as success.

    Typical updates look like:
      {"status": "pulling manifest"}
      {"status": "downloading", "total": 4835941252, "completed": 123456}
      {"status": "verifying sha256 digest"}
      {"status": "success"}
    """
    import json

    with _client.stream("POST", f"{BASE_URL}/api/pull", json={"name": model}) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if line.strip():
                data = json.loads(line)
                if data.get("status") == "error":
                    raise RuntimeError(data.get("error") or "Ollama reported a pull error")
                yield data


def chat(model: str, messages: list[dict]) -> str:
    r = _client.post(
        f"{BASE_URL}/api/chat",
        json={"model": model, "messages": messages, "stream": False},
    )
    r.raise_for_status()
    return r.json()["message"]["content"]
