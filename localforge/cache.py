"""Local snapshot cache for dashboard data.

The /api/recommendations response is written here after every successful
GPU probe. If the probe fails on a later load (nvidia-smi hanging, driver
update mid-session, browser hitting a cold server), the dashboard renders
the cached snapshot with a "cached" badge instead of erroring out.
"""
from __future__ import annotations

import datetime
import json
import os

_CACHE_ENV = "LOCALFORGE_CACHE_DIR"


def cache_path() -> str:
    """JSON file holding the last successful recommendations payload."""
    base = os.environ.get(_CACHE_ENV) or os.path.join(
        os.path.expanduser("~"), ".cache", "localforge"
    )
    return os.path.join(base, "recommendations.json")


def save_recommendations(payload: dict) -> str:
    """Write one recommendations payload to the cache. Returns the path.

    Failures (read-only disk, missing home dir) are silent on purpose:
    the cache is a convenience, never the primary data source.
    """
    path = cache_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "cached_at": datetime.datetime.now(
                        datetime.timezone.utc
                    ).isoformat(timespec="seconds"),
                    "payload": payload,
                },
                f,
            )
    except OSError:
        pass
    return path


def load_cached_recommendations() -> dict | None:
    """Return the cached payload plus its cached_at stamp, or None."""
    try:
        with open(cache_path(), encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or not isinstance(data.get("payload"), dict):
        return None
    return {"cached_at": data.get("cached_at"), **data["payload"]}
