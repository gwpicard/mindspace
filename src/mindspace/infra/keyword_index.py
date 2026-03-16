"""BM25 keyword index for hybrid search."""

import json
import re
from pathlib import Path

from mindspace.infra.paths import derived_dir


CORPUS_FILE = "bm25_corpus.json"


class KeywordIndex:
    """In-memory BM25 index over chunk texts, persisted to JSON."""

    def __init__(self) -> None:
        self._corpus_path = derived_dir() / CORPUS_FILE
        self._chunk_ids: list[str] = []
        self._tokenized_corpus: list[list[str]] = []
        self._bm25 = None

    def _tokenize(self, text: str) -> list[str]:
        """Simple whitespace + lowercase tokenization."""
        text = text.lower()
        tokens = re.findall(r"\b\w+\b", text)
        return tokens

    def build(self, chunk_ids: list[str], texts: list[str]) -> None:
        """Build index from scratch."""
        from rank_bm25 import BM25Okapi

        self._chunk_ids = chunk_ids
        self._tokenized_corpus = [self._tokenize(t) for t in texts]
        if self._tokenized_corpus:
            self._bm25 = BM25Okapi(self._tokenized_corpus)
        else:
            self._bm25 = None

    def add(self, chunk_id: str, text: str) -> None:
        """Add a single document. Rebuilds BM25 (cheap for small corpora)."""
        self._chunk_ids.append(chunk_id)
        self._tokenized_corpus.append(self._tokenize(text))
        from rank_bm25 import BM25Okapi

        if self._tokenized_corpus:
            self._bm25 = BM25Okapi(self._tokenized_corpus)

    def search(self, query: str, n_results: int = 10) -> list[tuple[str, float]]:
        """Search and return (chunk_id, score) pairs, sorted by score desc."""
        if not self._bm25 or not self._chunk_ids:
            return []
        tokenized_query = self._tokenize(query)
        if not tokenized_query:
            return []
        scores = self._bm25.get_scores(tokenized_query)
        scored = [(self._chunk_ids[i], float(scores[i])) for i in range(len(self._chunk_ids))]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:n_results]

    def save(self) -> None:
        """Persist corpus to JSON."""
        data = {
            "chunk_ids": self._chunk_ids,
            "texts": [" ".join(tokens) for tokens in self._tokenized_corpus],
        }
        self._corpus_path.parent.mkdir(parents=True, exist_ok=True)
        self._corpus_path.write_text(json.dumps(data, ensure_ascii=False))

    def load(self) -> bool:
        """Load corpus from JSON. Returns True if loaded successfully."""
        if not self._corpus_path.exists():
            return False
        data = json.loads(self._corpus_path.read_text())
        self.build(data["chunk_ids"], data["texts"])
        return True

    def clear(self) -> None:
        """Clear the index and remove persisted file."""
        self._chunk_ids = []
        self._tokenized_corpus = []
        self._bm25 = None
        if self._corpus_path.exists():
            self._corpus_path.unlink()
