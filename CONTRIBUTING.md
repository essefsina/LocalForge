# Contributing to LocalForge

Thanks for stopping by! LocalForge is a small, focused project — the whole backend is five Python files and the dashboard is one dependency-free HTML page. If you can read a Flask-style route, you can contribute here.

## Getting set up

```bash
git clone https://github.com/essefsina/LocalForge.git
cd LocalForge
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install pytest                                   # test runner
```

Launch the dashboard:

```bash
python -m localforge            # http://127.0.0.1:8000
python -m localforge --port 9000 --verbose
```

You don't need an NVIDIA GPU or Ollama installed to develop — the dashboard degrades gracefully ("CPU-only mode") when they're missing, and the test suite doesn't touch either.

## Project layout

| Path | What it is |
|---|---|
| `localforge/gpu.py` | GPU detection via `nvidia-smi`; degrades to "no GPU" without raising |
| `localforge/models.py` | Curated model catalog (VRAM figures, tags) + the fit/recommendation logic |
| `localforge/ollama.py` | Thin Ollama API client (pull, list, chat, version checks) |
| `localforge/server.py` | FastAPI backend: JSON API + serves the dashboard |
| `localforge/cache.py` | Local snapshot cache for `/api/recommendations` (offline fallback) |
| `localforge/static/index.html` | The whole dashboard — single HTML file, no build step |
| `tests/` | pytest suite, one file per module |

## Code style

- Type hints on all public functions (`from __future__ import annotations` is already at the top of every module).
- Docstrings on anything non-obvious; keep them short and honest about failure modes.
- Stdlib + FastAPI/httpx/pydantic only — don't add a dependency without opening an issue first.

## Tests

```bash
python -m pytest tests/          # full suite
python -m pytest tests/test_cache.py -q   # one file
```

New behavior gets a test. The suite runs with **no GPU and no Ollama** — anything that calls either must be monkeypatched or structured so it degrades (see `gpu.detect_gpus()` and the server's cached-recommendations fallback for the pattern to follow).

## Sending a PR

1. Fork the repo, create a branch (`git checkout -b my-feature`).
2. Make the change, add/extend tests, run the full suite.
3. Write a PR title that says what it does ("Cache /api/recommendations so the dashboard renders offline"), and in the body say **what changed, why, and how you validated it** (which tests, what you clicked through).
4. Keep PRs small and focused — one behavior per PR merges faster.

## Good first issues

- Add a model to the catalog in `localforge/models.py` (verify the Ollama tag and VRAM figure against ollama.com/library first).
- Add AMD (ROCm) or Apple Silicon detection alongside `nvidia-smi`.
- Improve the dashboard UI (it's plain HTML/CSS/JS — no framework to learn).

Questions? Open an issue — the fastest way to get a helpful answer is a short repro and what you expected.
