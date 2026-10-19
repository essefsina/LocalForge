"""FastAPI backend serving the LocalForge dashboard and JSON API."""
from __future__ import annotations

import os
import threading

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import ollama
from .cache import load_cached_recommendations, save_recommendations
from .gpu import detect_gpus, primary_gpu
from .models import recommend

app = FastAPI(title="LocalForge", version="0.2.0")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# --- background pull tracking -------------------------------------------
# Maps model id -> {"status": "pulling"|"done"|"error",
#                   "completed": bytes, "total": bytes, "detail": str}
_pull_state: dict[str, dict] = {}
_pull_lock = threading.Lock()


def _do_pull(model: str) -> None:
    with _pull_lock:
        state = _pull_state.setdefault(
            model,
            {"status": "pulling", "completed": 0, "total": 0, "detail": "starting"},
        )
    try:
        for update in ollama.pull_stream(model):
            status = update.get("status", "")
            with _pull_lock:
                state["detail"] = status.replace("_", " ")
                if update.get("total"):
                    state["completed"] = update.get("completed", 0)
                    state["total"] = update["total"]
                if status == "success":
                    state["status"] = "done"
        with _pull_lock:
            if state["status"] == "pulling":
                state["status"] = "done"
    except Exception as exc:  # noqa: BLE001
        with _pull_lock:
            state["status"] = "error"
            state["detail"] = str(exc)
        return

    # The stream ended — but only trust it if the model actually landed
    # in Ollama. A silent/early end of stream is not a success.
    try:
        installed = [m["name"] for m in ollama.list_installed()]
    except Exception:  # noqa: BLE001
        installed = []
    if model not in installed:
        with _pull_lock:
            state["status"] = "error"
            state["detail"] = (
                "Ollama finished without installing the model. "
                "Check disk space and connection, then try again."
            )


class PullRequest(BaseModel):
    model: str


class ChatRequest(BaseModel):
    model: str
    messages: list[dict]


@app.get("/api/health")
def health() -> dict:
    return {
        "ok": True,
        "ollama": ollama.is_available(),
        "ollama_installed": ollama.is_installed(),
        "ollama_version": ollama.server_version(),
        # Empty list = every endpoint still matches the API shape this
        # client was written against; non-empty = version drift.
        "api_warnings": ollama.api_shape_warnings(),
    }


def _ollama_unavailable() -> HTTPException:
    """503 with guidance matched to the actual problem.

    "Not installed" points at the download page; "not running" points at
    `ollama serve`. Callers should raise this instead of surfacing a raw
    connection error.
    """
    if not ollama.is_installed():
        return HTTPException(
            503,
            f"Ollama isn't installed. Download it from {ollama.DOWNLOAD_URL}, "
            "then run `ollama serve`.",
        )
    return HTTPException(503, "Ollama is not running. Start it first: `ollama serve`")


@app.get("/api/gpu")
def gpu() -> dict:
    gpus = detect_gpus()
    return {"gpus": [g.to_dict() for g in gpus], "primary": primary_gpu().to_dict() if gpus else None}


@app.get("/api/recommendations")
def recommendations() -> dict:
    """Live VRAM-matched catalog, falling back to the cached snapshot.

    The fresh payload is cached after every success. When the GPU probe
    throws (hanging driver, missing nvidia-smi mid-update), the dashboard
    still renders from the last known-good snapshot instead of showing
    an error card.
    """
    try:
        data = recommend(primary_gpu())
    except Exception as exc:  # noqa: BLE001 - GPU probe must never 500 the dashboard
        cached = load_cached_recommendations()
        if cached is None:
            raise HTTPException(
                503,
                f"GPU probe failed and no cached recommendations available: {exc}",
            ) from exc
        return {"cached": True, **cached}
    save_recommendations(data)
    return {"cached": False, **data}


@app.get("/api/models")
def models() -> dict:
    installed = []
    if ollama.is_available():
        installed = [m["name"] for m in ollama.list_installed()]
    running = []
    if ollama.is_available():
        running = [m["name"] for m in ollama.running()]
    return {"installed": installed, "running": running, "ollama_up": ollama.is_available()}


@app.post("/api/pull")
def pull(req: PullRequest) -> dict:
    """Start pulling a model in the background; poll /api/pull/status."""
    if not ollama.is_available():
        raise _ollama_unavailable()
    with _pull_lock:
        existing = _pull_state.get(req.model)
        if existing and existing["status"] == "pulling":
            return {"ok": True, "already_running": True}
        _pull_state[req.model] = {
            "status": "pulling",
            "completed": 0,
            "total": 0,
            "detail": "starting",
        }
    threading.Thread(target=_do_pull, args=(req.model,), daemon=True).start()
    return {"ok": True, "started": True}


def _progress_pct(completed: int, total: int) -> float:
    return round(completed / total * 100, 1) if total else 0.0


@app.get("/api/pull/status")
def pull_status(model: str) -> dict:
    with _pull_lock:
        state = _pull_state.get(model)
        if not state:
            raise HTTPException(404, "no pull in progress for this model")
        state = dict(state)
    state["pct"] = _progress_pct(state.get("completed", 0), state.get("total") or 0)
    return state


@app.post("/api/chat")
def chat(req: ChatRequest) -> dict:
    if not ollama.is_available():
        raise _ollama_unavailable()
    try:
        reply = ollama.chat(req.model, req.messages)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, f"Chat failed: {exc}") from exc
    return {"reply": reply}


if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))
