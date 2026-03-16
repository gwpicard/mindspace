"""Text chunking for long captures."""

from dataclasses import dataclass

from mindspace.infra.config import get_settings


@dataclass
class Chunk:
    """A chunk of text from a capture."""

    capture_id: str
    chunk_index: int
    text: str

    @property
    def chunk_id(self) -> str:
        return f"{self.capture_id}__chunk_{self.chunk_index}"


class Chunker:
    """Splits text into overlapping chunks for embedding."""

    def __init__(
        self,
        max_tokens: int | None = None,
        overlap_tokens: int | None = None,
    ) -> None:
        settings = get_settings()
        self._max_tokens = max_tokens if max_tokens is not None else settings.chunk_max_tokens
        self._overlap_tokens = overlap_tokens if overlap_tokens is not None else settings.chunk_overlap_tokens

    def chunk(self, text: str, capture_id: str) -> list[Chunk]:
        """Split text into chunks. Short text returns a single chunk."""
        words = text.split()
        if len(words) <= self._max_tokens:
            return [Chunk(capture_id=capture_id, chunk_index=0, text=text)]

        chunks: list[Chunk] = []
        paragraphs = text.split("\n\n")

        # Build chunks by accumulating paragraphs
        current_words: list[str] = []
        chunk_index = 0

        for para in paragraphs:
            para_words = para.split()
            if not para_words:
                continue

            # If adding this paragraph would exceed max, finalize current chunk
            if current_words and len(current_words) + len(para_words) > self._max_tokens:
                chunks.append(Chunk(
                    capture_id=capture_id,
                    chunk_index=chunk_index,
                    text=" ".join(current_words),
                ))
                chunk_index += 1
                # Overlap: keep last N tokens
                if self._overlap_tokens > 0:
                    current_words = current_words[-self._overlap_tokens:]
                else:
                    current_words = []

            current_words.extend(para_words)

            # If a single paragraph exceeds max, split by sentences
            while len(current_words) > self._max_tokens:
                # Find a sentence boundary within max_tokens
                text_so_far = " ".join(current_words[:self._max_tokens])
                split_pos = text_so_far.rfind(". ")
                if split_pos > 0:
                    split_words = text_so_far[: split_pos + 1].split()
                else:
                    split_words = current_words[:self._max_tokens]

                chunks.append(Chunk(
                    capture_id=capture_id,
                    chunk_index=chunk_index,
                    text=" ".join(split_words),
                ))
                chunk_index += 1

                # Within a paragraph, advance fully past split (no overlap here;
                # overlap is applied only at paragraph boundaries)
                current_words = current_words[len(split_words):]

        # Don't forget the last chunk
        if current_words:
            chunks.append(Chunk(
                capture_id=capture_id,
                chunk_index=chunk_index,
                text=" ".join(current_words),
            ))

        return chunks
