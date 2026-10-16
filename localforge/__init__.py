"""LocalForge: turn your gaming PC into a private AI server."""
from .gpu import detect_gpus, primary_gpu
from .models import recommend

__all__ = ["detect_gpus", "primary_gpu", "recommend"]
__version__ = "0.2.1"
