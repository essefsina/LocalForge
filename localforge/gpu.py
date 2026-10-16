"""GPU detection via nvidia-smi.

Gracefully degrades when no NVIDIA GPU (or no nvidia-smi) is present,
so the dashboard still runs on machines without a discrete GPU.
"""
from __future__ import annotations

import shutil
import subprocess
from dataclasses import asdict, dataclass


@dataclass
class GPUInfo:
    name: str
    vram_total_mb: int
    vram_used_mb: int
    utilization_pct: int
    temperature_c: int

    @property
    def vram_total_gb(self) -> float:
        return round(self.vram_total_mb / 1024, 1)

    @property
    def vram_used_gb(self) -> float:
        return round(self.vram_used_mb / 1024, 1)

    @property
    def vram_free_gb(self) -> float:
        return round((self.vram_total_mb - self.vram_used_mb) / 1024, 1)

    def to_dict(self) -> dict:
        d = asdict(self)
        d.update(
            vram_total_gb=self.vram_total_gb,
            vram_used_gb=self.vram_used_gb,
            vram_free_gb=self.vram_free_gb,
        )
        return d


def _run_nvidia_smi() -> str | None:
    if not shutil.which("nvidia-smi"):
        return None
    try:
        out = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.used,utilization.gpu,temperature.gpu",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if out.returncode != 0:
            return None
        return out.stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return None


def detect_gpus() -> list[GPUInfo]:
    """Return one GPUInfo per NVIDIA GPU, or an empty list if none found."""
    raw = _run_nvidia_smi()
    if not raw:
        return []
    gpus: list[GPUInfo] = []
    for line in raw.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 5:
            continue
        try:
            gpus.append(
                GPUInfo(
                    name=parts[0],
                    vram_total_mb=int(parts[1]),
                    vram_used_mb=int(parts[2]),
                    utilization_pct=int(parts[3]),
                    temperature_c=int(parts[4]),
                )
            )
        except ValueError:
            continue
    return gpus


def primary_gpu() -> GPUInfo | None:
    """The first detected GPU, or None when no NVIDIA GPU is present."""
    gpus = detect_gpus()
    return gpus[0] if gpus else None
