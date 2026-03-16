"""Data directory resolution and creation."""

from pathlib import Path

from mindspace.infra.config import get_settings


def data_root() -> Path:
    """Return the root data directory."""
    return Path(get_settings().data_dir).resolve()


def raw_dir() -> Path:
    """Directory for raw capture JSON files."""
    return data_root() / "raw"


def derived_dir() -> Path:
    """Directory for derived data (embeddings, registry)."""
    return data_root() / "derived"


def chroma_dir() -> Path:
    """Directory for ChromaDB persistent storage."""
    return derived_dir() / "chroma"


def index_path() -> Path:
    """Path to the JSONL index of all captures."""
    return data_root() / "index.jsonl"


def eval_dir() -> Path:
    """Directory for evaluation data (golden dataset, history)."""
    return data_root() / "eval"


def golden_path() -> Path:
    """Path to the golden evaluation dataset."""
    return eval_dir() / "golden.json"


def eval_history_path() -> Path:
    """Path to the JSONL evaluation history."""
    return eval_dir() / "history.jsonl"


def ensure_dirs() -> None:
    """Create all required data directories."""
    raw_dir().mkdir(parents=True, exist_ok=True)
    derived_dir().mkdir(parents=True, exist_ok=True)
    chroma_dir().mkdir(parents=True, exist_ok=True)
    eval_dir().mkdir(parents=True, exist_ok=True)
