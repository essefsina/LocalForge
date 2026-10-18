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


def server_version() -> str | None:
    """Ollama server version from GET /api/version, e.g. "0.12.3".

    Returns None when Ollama is unreachable or the response is unexpected.
    Never raises.
    """
    try:
        r = _client.get(f"{BASE_URL}/api/version", timeout=5.0)
        r.raise_for_status()
        data = r.json()
        version = data.get("version") if isinstance(data, dict) else None
        return version if isinstance(version, str) else None
    except Exception:  # noqa: BLE001
        return None


def api_shape_warnings() -> list[str]:
    """Detect Ollama version drift on the endpoints LocalForge parses.

    Probes /api/tags and /api/ps and reports any whose JSON no longer has
    the expected shape (an object with a "models" list). A drift warning
    means the running Ollama server changed its API relative to the
    version this client was written against, so callers should surface it
    instead of silently mis-parsing. Never raises.
    """
    warnings: list[str] = []
    for endpoint in ("/api/tags", "/api/ps"):
        try:
            r = _client.get(f"{BASE_URL}{endpoint}", timeout=5.0)
            r.raise_for_status()
            data = r.json()
        except Exception:  # noqa: BLE001 - probe, not an operation
            warnings.append(
                f"Ollama {endpoint} did not respond — can't verify its API shape")
            continue
        if not isinstance(data, dict) or not isinstance(data.get("models"), list):
            warnings.append(
                f"Ollama {endpoint} returned an unexpected shape "
                f"(expected a JSON object with a 'models' list) — "
                f"the server version may have changed the API")
    return warnings


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
