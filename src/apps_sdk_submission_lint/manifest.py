"""Manifest loading helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_manifest(path: str | Path) -> dict[str, Any]:
    """Load a local JSON manifest file."""
    manifest_path = Path(path)
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{manifest_path} is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"{manifest_path} must contain a JSON object")
    return data
