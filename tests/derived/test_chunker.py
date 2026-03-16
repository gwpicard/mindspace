"""Tests for text chunking."""

from mindspace.derived.chunker import Chunk, Chunker


def test_short_text_single_chunk(tmp_data_dir):
    chunker = Chunker(max_tokens=500, overlap_tokens=50)
    chunks = chunker.chunk("This is a short text.", "cap_001")
    assert len(chunks) == 1
    assert chunks[0].text == "This is a short text."
    assert chunks[0].chunk_id == "cap_001__chunk_0"
    assert chunks[0].capture_id == "cap_001"
    assert chunks[0].chunk_index == 0


def test_long_text_multiple_chunks(tmp_data_dir):
    chunker = Chunker(max_tokens=10, overlap_tokens=2)
    # 30 words -> should create multiple chunks
    words = [f"word{i}" for i in range(30)]
    text = " ".join(words)
    chunks = chunker.chunk(text, "cap_002")
    assert len(chunks) > 1
    # All chunks should have the correct capture_id
    for c in chunks:
        assert c.capture_id == "cap_002"
    # Chunk IDs should be sequential
    for i, c in enumerate(chunks):
        assert c.chunk_index == i
        assert c.chunk_id == f"cap_002__chunk_{i}"


def test_paragraph_boundaries(tmp_data_dir):
    chunker = Chunker(max_tokens=10, overlap_tokens=0)
    # Two paragraphs, each under the limit
    text = "One two three four five.\n\nSix seven eight nine ten."
    chunks = chunker.chunk(text, "cap_003")
    assert len(chunks) == 1  # Total 10 words, fits in one chunk


def test_paragraph_split(tmp_data_dir):
    chunker = Chunker(max_tokens=6, overlap_tokens=0)
    text = "One two three four five.\n\nSix seven eight nine ten."
    chunks = chunker.chunk(text, "cap_004")
    assert len(chunks) == 2


def test_chunk_dataclass():
    chunk = Chunk(capture_id="abc", chunk_index=3, text="hello")
    assert chunk.chunk_id == "abc__chunk_3"


def test_overlap_preserved(tmp_data_dir):
    chunker = Chunker(max_tokens=5, overlap_tokens=2)
    # Three paragraphs of 3 words each — overlap applies at paragraph boundaries
    text = "Alpha beta gamma.\n\nDelta epsilon zeta.\n\nEta theta iota."
    chunks = chunker.chunk(text, "cap_005")
    assert len(chunks) >= 2
    # After first paragraph chunk, overlap should carry last 2 words into next chunk
    first_words = chunks[0].text.split()
    second_words = chunks[1].text.split()
    overlap = first_words[-2:]
    assert second_words[:2] == overlap
