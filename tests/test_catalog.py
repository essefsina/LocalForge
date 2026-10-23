"""Catalog integrity tests — the 5 curated additions and their VRAM math.

No GPU or Ollama required.
"""
from localforge.gpu import GPUInfo
from localforge.models import CATALOG, _params_to_float, recommend

NEW_MODELS = {
    "llama3.2:1b": ("1B", 1400),
    "qwen2.5-coder:7b": ("7B", 5000),
    "qwen3:8b": ("8B", 5600),
    "deepseek-r1:14b": ("14B", 9400),
    "gemma3:27b": ("27B", 18500),
}

REQUIRED_KEYS = {"id", "label", "params", "vram_mb", "blurb", "tags"}


def _by_id(model_id):
    return next(m for m in CATALOG if m["id"] == model_id)


def test_new_models_present_with_verified_params():
    for model_id, (params, vram_mb) in NEW_MODELS.items():
        m = _by_id(model_id)
        assert REQUIRED_KEYS <= set(m), f"{model_id} missing keys"
        assert m["params"] == params, f"{model_id} param count wrong"
        assert m["vram_mb"] == vram_mb, f"{model_id} VRAM figure wrong"
        assert m["label"] and m["blurb"] and m["tags"]


def test_params_parse_for_sorting():
    for m in CATALOG:
        assert _params_to_float(m["params"]) > 0, m["id"]


def test_vram_ordering_sane():
    ordered = ["llama3.2:1b", "qwen2.5-coder:7b", "qwen3:8b",
               "deepseek-r1:14b", "gemma3:27b"]
    vrams = [_by_id(mid)["vram_mb"] for mid in ordered]
    assert vrams == sorted(vrams), "VRAM figures must grow with model size"


def _gpu(vram_mb):
    return GPUInfo(name="Test GPU", vram_total_mb=vram_mb, vram_used_mb=0,
                   utilization_pct=0, temperature_c=40)


def test_24gb_gpu_fits_gemma3_27b():
    rec = recommend(_gpu(24 * 1024))
    assert "gemma3:27b" in [m["id"] for m in rec["fits"]]


def test_8gb_gpu_excludes_14b_reasoners():
    rec = recommend(_gpu(8 * 1024))
    fits = {m["id"] for m in rec["fits"]}
    assert "deepseek-r1:14b" not in fits
    assert "qwen3:8b" in fits
    assert "qwen2.5-coder:7b" in fits
