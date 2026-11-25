"""Load config.json, falling back to sensible defaults."""
from __future__ import annotations

import json
from pathlib import Path

DEFAULTS = {
    "library": "~/tilawah-library",
    "reciters": ["alafasy", "husary", "minshawi"],
    "start_surah": 1,
    "volume": 60,
    "max_volume": 85,
    "pins": {},
    "cards": {},
    "routines": [],
    "quiet_hours": None,
    "timezone": "Europe/London",
}


def load(path: str | Path | None) -> dict:
    cfg = dict(DEFAULTS)
    if path and Path(path).exists():
        cfg.update(json.loads(Path(path).read_text(encoding="utf-8")))
    return cfg
