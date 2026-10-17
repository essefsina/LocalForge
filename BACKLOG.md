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
        NOTE 2026-10-17: PR could not be opened — PAT lacks Pull-requests
        write (403 "Resource not accessible by personal access token").
        Branch is pushed and reviewable; open the PR from the compare view
        or add the permission to the "Muse Pushes" token.
- [ ] Resume interrupted translation-pack downloads (Range header) instead
      of restarting from zero
- [ ] Display `[auto → en]` nicely when src is "mul" or "auto" in the
      translation result header
- [x] Add `CONTRIBUTING.md` — how to run from source, build the installer,
      APK build notes
      → branch `cron/2026-10-17-contributing`
        (https://github.com/essefsina/DropIt/tree/cron/2026-10-17-contributing).
        NOTE 2026-10-17: PR could not be opened — PAT lacks Pull-requests
        write (403). Branch is pushed and reviewable.
- [ ] Add screenshots to README.md (drop 2-3 into docs/ and link them)
- [ ] Docstrings + type hints pass over dropit_mt.py public functions
- [ ] Handle translation of very long files: stream results per chunk into
      the modal instead of one blocking call
- [ ] Add a "clear translation packs" maintenance button (frees mt_models/)
- [ ] Fix: `showSaved` modal action row on narrow screens (verify .nact
      wraps or scrolls correctly under 360px)
- [ ] Log translation pack size before download; skip with a clear message
      if the disk has insufficient space
- [ ] Add `--version` CLI flag to dropit.py / app.py
- [ ] Rate-limit /api/aitranslate per IP (avoid one phone hammering the PC)

## LocalForge

- [x] Verify `python -m localforge` boots cleanly without a GPU
      (graceful "no NVIDIA GPU" state instead of a traceback)
- [x] Add `tests/test_gpu_parse.py` — unit tests for nvidia-smi output
      parsing (normal, no-GPU, malformed lines)
- [x] Friendly error card when Ollama is not installed (link to
      ollama.com/download instead of a raw connection error)
      → branch `cron/2026-10-17-ollama-card`
        (https://github.com/essefsina/LocalForge/tree/cron/2026-10-17-ollama-card).
        NOTE 2026-10-17: PR could not be opened — PAT lacks Pull-requests
        write (403). Branch is pushed and reviewable.
- [x] Add 5 more curated models to the VRAM-matched catalog with
      verified parameter counts (llama3.2:1b, qwen2.5-coder:7b, qwen3:8b,
      deepseek-r1:14b, gemma3:27b — tags + VRAM figures verified against
      the Ollama library)
      → branch `cron/2026-10-17-model-catalog`
        (https://github.com/essefsina/LocalForge/tree/cron/2026-10-17-model-catalog).
        NOTE 2026-10-17: PR could not be opened — PAT lacks Pull-requests
        write (403). Branch is pushed and reviewable.
- [ ] Add a `--port` CLI flag to the server
- [ ] README: add a features screenshot / demo GIF placeholder section
- [ ] Handle Ollama version drift: check `/api/version` and warn when
      the API shape is unexpected
- [ ] Add `CONTRIBUTING.md`
- [ ] Cache the model catalog locally so the dashboard renders offline
- [ ] Add request logging (uvicorn-style access log) behind a --verbose flag
