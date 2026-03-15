"""Tracks what has been derived per capture."""

import json
from pathlib import Path

from mindspace.infra.paths import derived_dir


REGISTRY_FILE = "registry.json"


class DerivationRegistry:
    """Records which derivations have been applied to which captures."""

    def __init__(self) -> None:
        self._path = derived_dir() / REGISTRY_FILE
        self._data: dict[str, dict] = self._load()

    def _load(self) -> dict:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2))

    def mark_embedded(self, capture_id: str) -> None:
        """Mark a capture as having been embedded."""
        if capture_id not in self._data:
            self._data[capture_id] = {}
        self._data[capture_id]["embedded"] = True
        self._save()

    def is_embedded(self, capture_id: str) -> bool:
        """Check if a capture has been embedded."""
        return self._data.get(capture_id, {}).get("embedded", False)

    def clear(self) -> None:
        """Clear all derivation records."""
        self._data = {}
        self._save()

    def count_embedded(self) -> int:
        """Count how many captures have been embedded."""
        return sum(1 for v in self._data.values() if v.get("embedded"))
