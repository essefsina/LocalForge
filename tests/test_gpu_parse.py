"""nvidia-smi output parsing tests — no GPU required.

Patches localforge.gpu._run_nvidia_smi with canned outputs covering the
normal case, the no-GPU case, and malformed lines.
"""
import localforge.gpu as gpu_mod
from localforge.gpu import GPUInfo, detect_gpus, primary_gpu

TWO_GPUS = (
    "NVIDIA GeForce RTX 4070, 12282, 1042, 12, 51\n"
    "NVIDIA GeForce RTX 3060, 12288, 512, 0, 38\n"
)


def _patch(monkeypatch, raw):
    monkeypatch.setattr(gpu_mod, "_run_nvidia_smi", lambda: raw)


def test_two_gpus_parsed(monkeypatch):
    _patch(monkeypatch, TWO_GPUS)
    gpus = detect_gpus()
    assert len(gpus) == 2
    first, second = gpus
    assert first.name == "NVIDIA GeForce RTX 4070"
    assert first.vram_total_mb == 12282
    assert first.vram_used_mb == 1042
    assert first.utilization_pct == 12
    assert first.temperature_c == 51
    assert second.name == "NVIDIA GeForce RTX 3060"
    assert second.vram_total_mb == 12288


def test_no_smi_means_no_gpus(monkeypatch):
    # nvidia-smi missing from PATH or failing -> None
    _patch(monkeypatch, None)
    assert detect_gpus() == []
    assert primary_gpu() is None


def test_blank_output_means_no_gpus(monkeypatch):
    _patch(monkeypatch, "   \n")
    assert detect_gpus() == []
    assert primary_gpu() is None


def test_malformed_lines_are_skipped(monkeypatch):
    raw = (
        "garbage line with no fields\n"
        "NVIDIA GeForce RTX 4070, 12282, 1042, 12, 51\n"
        "Only, three, fields\n"
        "NVIDIA Weird Card, N/A, 100, 10, 40\n"
        "\n"
    )
    _patch(monkeypatch, raw)
    gpus = detect_gpus()
    assert len(gpus) == 1
    assert gpus[0].name == "NVIDIA GeForce RTX 4070"


def test_primary_gpu_is_first(monkeypatch):
    _patch(monkeypatch, TWO_GPUS)
    p = primary_gpu()
    assert p is not None
    assert p.name == "NVIDIA GeForce RTX 4070"


def test_gpuinfo_derived_properties():
    g = GPUInfo(
        name="Test GPU",
        vram_total_mb=12282,
        vram_used_mb=1042,
        utilization_pct=12,
        temperature_c=51,
    )
    assert g.vram_total_gb == 12.0
    assert g.vram_used_gb == 1.0
    assert g.vram_free_gb == 11.0
    d = g.to_dict()
    assert d["name"] == "Test GPU"
    assert d["vram_total_gb"] == 12.0
    assert d["vram_free_gb"] == 11.0
