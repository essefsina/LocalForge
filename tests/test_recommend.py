"""Recommendation-engine tests — no GPU or Ollama required."""
from localforge.gpu import GPUInfo
from localforge.models import CATALOG, recommend


def _gpu(vram_mb: int) -> GPUInfo:
    return GPUInfo(
        name="Test GPU",
        vram_total_mb=vram_mb,
        vram_used_mb=0,
        utilization_pct=0,
        temperature_c=40,
    )


def test_catalog_has_entries():
    assert len(CATALOG) >= 8


def test_8gb_gpu_gets_mid_size_pick():
    rec = recommend(_gpu(8 * 1024))
    assert rec["fits"], "an 8GB card should fit several models"
    assert rec["top_pick"] is not None
    assert rec["too_big"], "70B must not fit an 8GB card"


def test_no_gpu_means_no_fits():
    rec = recommend(None)
    assert rec["fits"] == []
    assert rec["top_pick"] is None
    assert len(rec["too_big"]) == len(CATALOG)


def test_24gb_gpu_fits_32b():
    rec = recommend(_gpu(24 * 1024))
    ids = [m["id"] for m in rec["fits"]]
    assert "qwen2.5:32b" in ids
    assert "llama3.3:70b" not in ids


def test_progress_pct():
    from localforge.server import _progress_pct

    assert _progress_pct(0, 0) == 0.0
    assert _progress_pct(0, 1000) == 0.0
    assert _progress_pct(500, 1000) == 50.0
    assert _progress_pct(1, 3) == 33.3
