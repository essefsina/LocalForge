"""Recommendation-boundary tests — the 0.85 VRAM headroom edge.

recommend() reserves 15% of VRAM for the OS/display, so a model fits only
when its requirement is within int(vram * 0.85). These tests pin the exact
boundary (one MB either side) plus the partition/top-pick invariants,
without needing a GPU or Ollama.
"""

from localforge.gpu import GPUInfo
from localforge.models import CATALOG, HEADROOM_FACTOR, recommend


def _gpu(vram_mb: int) -> GPUInfo:
    return GPUInfo(
        name="Test GPU",
        vram_total_mb=vram_mb,
        vram_used_mb=0,
        utilization_pct=0,
        temperature_c=40,
    )


def _params(model_id: str) -> float:
    return float(next(m for m in CATALOG if m["id"] == model_id)["params"].rstrip("B"))


def test_budget_applies_headroom_factor():
    assert HEADROOM_FACTOR == 0.85
    assert recommend(_gpu(8192))["budget_mb"] == int(8192 * 0.85) == 6963


def test_model_fitting_exactly_at_budget_fits():
    # 1205 MB * 0.85 = 1024.25 -> budget 1024, exactly gemma3:1b's need.
    rec = recommend(_gpu(1205))
    ids = [m["id"] for m in rec["fits"]]
    assert "gemma3:1b" in ids


def test_one_mb_below_budget_does_not_fit():
    # 1204 MB * 0.85 = 1023.4 -> budget 1023, one MB short of gemma3:1b.
    rec = recommend(_gpu(1204))
    ids = [m["id"] for m in rec["fits"]]
    assert "gemma3:1b" not in ids
    assert "gemma3:1b" in [m["id"] for m in rec["too_big"]]


def test_zero_vram_fits_nothing():
    rec = recommend(_gpu(0))
    assert rec["fits"] == []
    assert rec["top_pick"] is None
    assert rec["fastest"] is None


def test_fits_and_too_big_partition_the_catalog():
    rec = recommend(_gpu(8192))
    fit_ids = {m["id"] for m in rec["fits"]}
    big_ids = {m["id"] for m in rec["too_big"]}
    assert fit_ids.isdisjoint(big_ids)
    assert fit_ids | big_ids == {m["id"] for m in CATALOG}


def test_top_pick_is_the_largest_fitting_model():
    rec = recommend(_gpu(8192))
    assert rec["top_pick"] is not None
    assert _params(rec["top_pick"]) == max(_params(m["id"]) for m in rec["fits"])


def test_fastest_is_the_smallest_fitting_model():
    rec = recommend(_gpu(8192))
    assert rec["fastest"] is not None
    assert _params(rec["fastest"]) == min(_params(m["id"]) for m in rec["fits"])


def test_every_fit_entry_is_flagged_fits():
    rec = recommend(_gpu(8192))
    assert all(m["fits"] for m in rec["fits"])
    assert not any(m["fits"] for m in rec["too_big"])
