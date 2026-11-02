"""Unit tests for GPUInfo's derived GB properties and to_dict().

The dashboard shows GB, but nvidia-smi reports MB — these tests pin
the conversion (rounded to one decimal) and the invariant the UI
relies on: free = total - used, in both MB and GB.
"""
from localforge.gpu import GPUInfo


def _gpu(total_mb, used_mb):
    return GPUInfo(
        name="RTX 4070",
        vram_total_mb=total_mb,
        vram_used_mb=used_mb,
        utilization_pct=10,
        temperature_c=55,
    )


def test_gb_conversion_rounds_to_one_decimal():
    g = _gpu(24576, 1024)
    assert g.vram_total_gb == 24.0
    assert g.vram_used_gb == 1.0
    assert g.vram_free_gb == 23.0


def test_half_gigabyte_values():
    g = _gpu(1536, 512)
    assert g.vram_total_gb == 1.5
    assert g.vram_used_gb == 0.5
    assert g.vram_free_gb == 1.0


def test_free_is_total_minus_used():
    g = _gpu(8192, 100)
    # 8092 MB -> 7.9 GB, not 8.1: free is derived from the MB figures.
    assert g.vram_free_gb == 7.9
    assert g.vram_free_gb == round((8192 - 100) / 1024, 1)


def test_zero_usage():
    g = _gpu(12288, 0)
    assert g.vram_used_gb == 0.0
    assert g.vram_free_gb == 12.0


def test_to_dict_carries_raw_and_derived_fields():
    d = _gpu(24576, 1024).to_dict()
    assert d["name"] == "RTX 4070"
    assert d["vram_total_mb"] == 24576
    assert d["vram_used_mb"] == 1024
    assert d["utilization_pct"] == 10
    assert d["temperature_c"] == 55
    assert d["vram_total_gb"] == 24.0
    assert d["vram_used_gb"] == 1.0
    assert d["vram_free_gb"] == 23.0
