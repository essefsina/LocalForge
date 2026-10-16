"""Curated model catalog with VRAM requirements and fit recommendations.

VRAM figures are approximate for the default Ollama quantization
(Q4_K_M-ish). They err slightly high so recommendations stay safe.
"""
from __future__ import annotations

from .gpu import GPUInfo

# Leave this fraction of VRAM headroom for the OS, display server, etc.
HEADROOM_FACTOR = 0.85

CATALOG: list[dict] = [
    {
        "id": "gemma3:1b",
        "label": "Gemma 3 1B",
        "params": "1B",
        "vram_mb": 1024,
        "blurb": "Tiny and instant. Great for testing the waters on any GPU.",
        "tags": ["chat", "fast"],
    },
    {
        "id": "qwen2.5:3b",
        "label": "Qwen 2.5 3B",
        "params": "3B",
        "vram_mb": 2048,
        "blurb": "Punchy little all-rounder, surprisingly capable for its size.",
        "tags": ["chat", "fast"],
    },
    {
        "id": "llama3.2:3b",
        "label": "Llama 3.2 3B",
        "params": "3B",
        "vram_mb": 2048,
        "blurb": "Meta's small model. Solid everyday assistant on modest cards.",
        "tags": ["chat", "fast"],
    },
    {
        "id": "gemma3:4b",
        "label": "Gemma 3 4B",
        "params": "4B",
        "vram_mb": 3400,
        "blurb": "Google's efficient mid-size model with strong reasoning.",
        "tags": ["chat"],
    },
    {
        "id": "mistral:7b",
        "label": "Mistral 7B",
        "params": "7B",
        "vram_mb": 4500,
        "blurb": "The classic. Fast, sharp, and a great coding companion.",
        "tags": ["chat", "code"],
    },
    {
        "id": "qwen2.5:7b",
        "label": "Qwen 2.5 7B",
        "params": "7B",
        "vram_mb": 4800,
        "blurb": "Excellent instruction-following and multilingual chops.",
        "tags": ["chat", "code"],
    },
    {
        "id": "llama3.1:8b",
        "label": "Llama 3.1 8B",
        "params": "8B",
        "vram_mb": 5000,
        "blurb": "The community workhorse. Huge ecosystem, great quality.",
        "tags": ["chat", "code"],
    },
    {
        "id": "deepseek-r1:8b",
        "label": "DeepSeek R1 8B",
        "params": "8B",
        "vram_mb": 5300,
        "blurb": "Reasoning model that thinks out loud. Fun to watch work.",
        "tags": ["chat", "reasoning"],
    },
    {
        "id": "gemma3:12b",
        "label": "Gemma 3 12B",
        "params": "12B",
        "vram_mb": 8200,
        "blurb": "A real step up in quality for 12GB+ cards.",
        "tags": ["chat"],
    },
    {
        "id": "phi4:14b",
        "label": "Phi-4 14B",
        "params": "14B",
        "vram_mb": 9200,
        "blurb": "Microsoft's dense model. Near-flagship reasoning, modest VRAM.",
        "tags": ["chat", "reasoning", "code"],
    },
    {
        "id": "qwen2.5:14b",
        "label": "Qwen 2.5 14B",
        "params": "14B",
        "vram_mb": 9200,
        "blurb": "Strong coder and writer for 12GB+ cards.",
        "tags": ["chat", "code"],
    },
    {
        "id": "qwen2.5:32b",
        "label": "Qwen 2.5 32B",
        "params": "32B",
        "vram_mb": 20000,
        "blurb": "Flagship-tier quality. Needs a 24GB card like a 3090/4090.",
        "tags": ["chat", "code"],
    },
    {
        "id": "llama3.3:70b",
        "label": "Llama 3.3 70B",
        "params": "70B",
        "vram_mb": 43000,
        "blurb": "The big one. For 48GB+ workstation cards or multi-GPU rigs.",
        "tags": ["chat", "code", "reasoning"],
    },
]


def _params_to_float(params: str) -> float:
    return float(params.upper().replace("B", ""))


def recommend(gpu: GPUInfo | None) -> dict:
    """Split the catalog into fits / too-big, and pick a top recommendation."""
    budget_mb = int(gpu.vram_total_mb * HEADROOM_FACTOR) if gpu else 0

    fits: list[dict] = []
    too_big: list[dict] = []
    for model in CATALOG:
        entry = dict(model, fits=model["vram_mb"] <= budget_mb)
        (fits if entry["fits"] else too_big).append(entry)

    fits.sort(key=lambda m: _params_to_float(m["params"]))
    too_big.sort(key=lambda m: _params_to_float(m["params"]))

    top_pick = fits[-1]["id"] if fits else None
    fastest = fits[0]["id"] if fits else None

    return {
        "gpu": gpu.to_dict() if gpu else None,
        "budget_mb": budget_mb,
        "top_pick": top_pick,
        "fastest": fastest,
        "fits": fits,
        "too_big": too_big,
    }
