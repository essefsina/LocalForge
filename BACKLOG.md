# GitHub contribution backlog — DropIt + LocalForge

Real, reviewable work items. Each should become ONE focused commit with a
proper message. Mark done with [x]. The daily job takes the top 4 pending
items, alternating repos when possible. Never invent filler.

## DropIt

- [x] Add `tests/test_detect_lang.py` — unit tests for dropit_mt.detect_lang
      (fr/es/de/it/pt/nl/ru/ja/zh/ar/en + None cases)
- [x] Add `tests/test_mt_chunk.py` — unit tests for _PairMT._split chunking
      (long text splits on sentence boundaries, chunks stay under limit)
- [x] Show download progress when fetching a translation pack (bytes
      downloaded / total in the AI modal instead of a frozen "Working…")
      → branch `cron/2026-10-17-dl-progress`
        (https://github.com/essefsina/DropIt/tree/cron/2026-10-17-dl-progress).
        PR: https://github.com/essefsina/DropIt/pull/1 (opened 2026-10-17
        after the "Muse Pushes" token got Pull-requests write).
- [x] Resume interrupted translation-pack downloads (Range header) instead
      of restarting from zero
      → branch `cron/2026-10-18-mt-resume`
        (https://github.com/essefsina/DropIt/tree/cron/2026-10-18-mt-resume).
        PR: https://github.com/essefsina/DropIt/pull/3 (opened 2026-10-18).
- [x] Display `[auto → en]` nicely when src is "mul" or "auto" in the
      translation result header
      → branch `cron/2026-10-18-auto-header`
        (https://github.com/essefsina/DropIt/tree/cron/2026-10-18-auto-header).
        PR: https://github.com/essefsina/DropIt/pull/4 (opened 2026-10-18).
- [x] Add `CONTRIBUTING.md` — how to run from source, build the installer,
      APK build notes
      → branch `cron/2026-10-17-contributing`
        (https://github.com/essefsina/DropIt/tree/cron/2026-10-17-contributing).
        PR: https://github.com/essefsina/DropIt/pull/2 (opened 2026-10-17).
- [ ] Add screenshots to README.md (drop 2-3 into docs/ and link them)
- [x] Docstrings + type hints pass over dropit_mt.py public functions
      → branch `cron/2026-10-19-mt-docs`.
        PR: https://github.com/essefsina/DropIt/pull/5 (opened 2026-10-19).
- [x] Handle translation of very long files: stream results per chunk into
      the modal instead of one blocking call
      → branch `cron/2026-10-23-translate-stream`.
        PR: https://github.com/essefsina/Drop/pull/10 (opened 2026-10-23).
- [x] Add a "clear translation packs" maintenance button (frees mt_models/)
      → branch `cron/2026-10-20-clear-packs`.
        PR: https://github.com/essefsina/DropIt/pull/8 (opened 2026-10-20).
- [x] Fix: `showSaved` modal action row on narrow screens (verify .nact
      wraps or scrolls correctly under 360px)
      → branch `cron/2026-10-23-nact-narrow`.
        PR: https://github.com/essefsina/Drop/pull/11 (opened 2026-10-23).
- [x] Log translation pack size before download; skip with a clear message
      if the disk has insufficient space
      → branch `cron/2026-10-20-disk-check`.
        PR: https://github.com/essefsina/DropIt/pull/7 (opened 2026-10-20).
- [x] Add `--version` CLI flag to dropit.py / app.py
      → branch `cron/2026-10-19-version-flag`.
        PR: https://github.com/essefsina/DropIt/pull/6 (opened 2026-10-19).
- [x] Rate-limit /api/aitranslate per IP (avoid one phone hammering the PC)
      → branch `cron/2026-10-20-rate-limit`.
        PR: https://github.com/essefsina/DropIt/pull/9 (opened 2026-10-20).

## LocalForge

- [x] Verify `python -m localforge` boots cleanly without a GPU
      (graceful "no NVIDIA GPU" state instead of a traceback)
- [x] Add `tests/test_gpu_parse.py` — unit tests for nvidia-smi output
      parsing (normal, no-GPU, malformed lines)
- [x] Friendly error card when Ollama is not installed (link to
      ollama.com/download instead of a raw connection error)
      → branch `cron/2026-10-17-ollama-card`
        (https://github.com/essefsina/LocalForge/tree/cron/2026-10-17-ollama-card).
        PR: https://github.com/essefsina/LocalForge/pull/1 (opened 2026-10-17).
- [x] Add 5 more curated models to the VRAM-matched catalog with
      verified parameter counts (llama3.2:1b, qwen2.5-coder:7b, qwen3:8b,
      deepseek-r1:14b, gemma3:27b — tags + VRAM figures verified against
      the Ollama library)
      → branch `cron/2026-10-17-model-catalog`
        (https://github.com/essefsina/LocalForge/tree/cron/2026-10-17-model-catalog).
        PR: https://github.com/essefsina/LocalForge/pull/2 (opened 2026-10-17;
        branch cleaned of committed .pytest_cache/__pycache__ before opening).
- [x] Add a `--port` CLI flag to the server (already shipped in main —
      no PR needed)
- [x] README: add a features screenshot / demo GIF placeholder section
      → branch `cron/2026-10-20-readme-shots`.
        PR: https://github.com/essefsina/LocalForge/pull/7 (opened 2026-10-20).
- [x] Handle Ollama version drift: check `/api/version` and warn when
      the API shape is unexpected
      → branch `cron/2026-10-18-ollama-version`
        (https://github.com/essefsina/LocalForge/tree/cron/2026-10-18-ollama-version).
        PR: https://github.com/essefsina/LocalForge/pull/3 (opened 2026-10-18).
- [x] Add `CONTRIBUTING.md`
      → branch `cron/2026-10-19-contributing`.
        PR: https://github.com/essefsina/LocalForge/pull/6 (opened 2026-10-19).
- [x] Cache the model catalog locally so the dashboard renders offline
      → branch `cron/2026-10-19-offline-cache`.
        PR: https://github.com/essefsina/LocalForge/pull/5 (opened 2026-10-19).
- [x] Add request logging (uvicorn-style access log) behind a --verbose flag
      → branch `cron/2026-10-18-verbose`
        (https://github.com/essefsina/LocalForge/tree/cron/2026-10-18-verbose).
        PR: https://github.com/essefsina/LocalForge/pull/4 (opened 2026-10-18).
- [x] Fix: `ollama.is_installed()` / `ollama.DOWNLOAD_URL` are referenced by
      server.py (health endpoint, pull/chat 503s) but were never added to
      ollama.py — GET /api/health returns 500 on main (regression from the
      PR #5 merge; the definitions only exist on PR #1's branch)
      → branch `cron/2026-10-23-health-500-fix`.
        PR: https://github.com/essefsina/LocalForge/pull/8 (opened 2026-10-23).
- [x] Add `tests/test_pull_api.py` — pull lifecycle tests: start, duplicate
      POST returns already_running, 404 for unknown model status, progress
      pct math, error when the pull stream raises, error when the stream
      ends without the model being installed
      → branch `cron/2026-10-23-pull-api-tests`.
        PR: https://github.com/essefsina/LocalForge/pull/9 (opened 2026-10-23).

## New items (added 2026-10-25)

## DropIt

- [x] Add `tests/test_version_flag.py` — subprocess tests that
      `dropit.py --version` and `app.py --version` both print
      "DropIt <VERSION>" and exit cleanly
      → branch `cron/2026-10-25-version-flag`.
        PR: https://github.com/essefsina/Drop/pull/12 (opened 2026-10-25).
- [x] Add `tests/test_date_filter.py` — unit tests for
      dropit_ai._parse_date_filter (absolute "oct 2"/"10/2", full month
      names, future-date rollback, "last week"/"yesterday", year-only)
      → branch `cron/2026-10-25-date-filter`.
        PR: https://github.com/essefsina/Drop/pull/13 (opened 2026-10-25).

## LocalForge

- [x] Add `tests/test_recommend_boundary.py` — VRAM headroom boundary
      tests for recommend() (exact-fit MB either side of 0.85 factor,
      partition/top-pick/fastest invariants)
      → branch `cron/2026-10-25-recommend-boundary`.
        PR: https://github.com/essefsina/LocalForge/pull/10 (opened 2026-10-25).
- [x] Add `tests/test_recommendations_api.py` — TestClient tests for
      GET /api/recommendations (live path caches, probe failure serves
      cached snapshot, probe failure without cache is 503)
      → branch `cron/2026-10-25-recommend-api`.
        PR: https://github.com/essefsina/LocalForge/pull/11 (opened 2026-10-25).

## New items (added 2026-10-30)

## DropIt

- [x] Add `tests/test_script_lang.py` — unit tests for
      dropit_mt._script_lang (ja/ko/zh/ar/hi/bn/ru script detection,
      Latin text returns None, below-threshold mixed text returns None,
      empty text returns None)
      → branch `cron/2026-10-30-script-lang`.
        PR: https://github.com/essefsina/Drop/pull/16 (opened 2026-10-30).
- [x] Add `tests/test_extract_text.py` — unit tests for
      dropit_ai.extract_text (plain-text files read fully, unknown
      extensions and missing files return "" without raising, output
      capped at MAX_TEXT_CHARS)
      → branch `cron/2026-10-30-extract-text`.
        PR: https://github.com/essefsina/Drop/pull/17 (opened 2026-10-30).

## LocalForge

- [x] Add `tests/test_gpu_endpoint.py` — TestClient tests for
      GET /api/gpu (no GPU returns empty list and primary None; one
      GPU returns its to_dict fields including derived GB values)
      → branch `cron/2026-10-30-gpu-endpoint`.
        PR: https://github.com/essefsina/LocalForge/pull/14 (opened 2026-10-30).
- [x] Add `tests/test_cli_host_port.py` — CLI tests that --host/--port
      reach uvicorn.run (custom values and 127.0.0.1:8000 defaults)
      → branch `cron/2026-10-30-cli-host-port`.
        PR: https://github.com/essefsina/LocalForge/pull/15 (opened 2026-10-30).
