# 🔥 LocalForge

**Turn your gaming PC into a private AI server.**

Half the people with an RTX card have no idea they're sitting on a machine that can run ChatGPT-tier models — privately, offline, for free. LocalForge detects your GPU, tells you exactly which open models fit in your VRAM, pulls them with one click, and gives you a slick dashboard to chat with them. Nothing leaves your PC. 🔒

## ✨ What it does

- 🎮 **Auto-detects your GPU** — VRAM, utilization, temperature, live
- 🧠 **Smart model recommendations** — curated catalog matched to *your* VRAM budget, with a "best pick" callout
- ⬇️ **One-click model pulls** — powered by [Ollama](https://ollama.com), no terminal needed, with a live progress bar
- 💬 **Built-in chat playground** — talk to any installed model right in the dashboard
- 🔌 **OpenAI-compatible endpoint** — every model is also served at `http://localhost:11434/v1`, so any AI app can use it

## 🚀 Quickstart

**1. Install Ollama** (the engine that runs the models):

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh
# Windows: download from https://ollama.com/download
```

**2. Install LocalForge:**

```bash
git clone https://github.com/essefsina/LocalForge.git
cd localforge
pip install -r requirements.txt
```

**3. Launch:**

```bash
python -m localforge
```

Open **http://127.0.0.1:8000** → pick your model → start chatting. That's it.

## 🖥️ How it works

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  nvidia-smi  │─────▶│  LocalForge  │─────▶│   Ollama    │
│ GPU detect   │      │  dashboard   │      │ model engine│
└─────────────┘      │  :8000       │      │  :11434     │
                     └──────────────┘      └─────────────┘
```

LocalForge reads your GPU via `nvidia-smi`, filters a hand-tuned model catalog against 85% of your VRAM (leaving headroom for your OS/display), and drives Ollama's API for pulling, listing, and chatting. The whole UI is a single dependency-free HTML page.

## 📸 Screenshots & demo

> 🚧 Captures coming — placeholders below. Drop PNGs in [`docs/screenshots/`](docs/screenshots/) and update the links.

| Dashboard | Model recommendations | Chat playground |
|---|---|---|
| ![Dashboard placeholder](docs/screenshots/dashboard.png) | ![Recommendations placeholder](docs/screenshots/recommendations.png) | ![Chat placeholder](docs/screenshots/chat.png) |

<!-- Demo GIF: record one pull + chat round-trip, save as docs/screenshots/demo.gif, then:
![LocalForge demo](docs/screenshots/demo.gif)
-->

## 🗺️ Roadmap

- [ ] VRAM usage graph over time + per-model benchmarks on *your* hardware
- [ ] One-click GGUF import for models outside Ollama's library
- [ ] Multi-GPU / split-loading recommendations
- [ ] AMD (ROCm) and Apple Silicon (MLX) detection
- [ ] Team mode: share your local server on your LAN with access keys
- [ ] Docker Compose one-liner

## 🤝 Contributing

PRs welcome! Good first issues: add a model to the catalog (`localforge/models.py`), improve the dashboard UI, or add AMD/Apple Silicon detection. Run tests with:

```bash
python -m pytest tests/
```

## 📄 License

MIT — do whatever you want with it.
