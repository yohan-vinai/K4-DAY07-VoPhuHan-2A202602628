from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start: start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        # TODO: split into sentences, group into chunks
        if not text or not text.strip():
            return []

        sentences = [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])(?:\s+|(?=\n))", text.strip())
            if sentence.strip()
        ]
        return [
            " ".join(sentences[start: start + self.max_sentences_per_chunk])
            for start in range(0, len(sentences), self.max_sentences_per_chunk)
        ]


class HeadingSectionChunker:
    """Split Markdown by heading while retaining the section heading in each chunk.

    A section that exceeds ``chunk_size`` is split recursively, with its heading
    prepended to every resulting chunk so retrieved text remains self-describing.
    """

    HEADING_PATTERN = re.compile(r"^(#{1,6}\s+.+)$", re.MULTILINE)

    def __init__(self, chunk_size: int = 500) -> None:
        self.chunk_size = chunk_size
        self._fallback = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        text = text.strip()
        matches = list(self.HEADING_PATTERN.finditer(text))
        if not matches:
            return self._fallback.chunk(text)

        chunks: list[str] = []
        preamble = text[:matches[0].start()].strip()
        if preamble:
            chunks.extend(self._fallback.chunk(preamble))

        for index, match in enumerate(matches):
            heading = match.group(1).strip()
            section_end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            body = text[match.end():section_end].strip()
            section = f"{heading}\n\n{body}".strip()

            if len(section) <= self.chunk_size:
                chunks.append(section)
                continue

            available_body_size = max(1, self.chunk_size - len(heading) - 2)
            for body_chunk in RecursiveChunker(chunk_size=available_body_size).chunk(body):
                chunks.append(f"{heading}\n\n{body_chunk}".strip())

        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(
            separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        # TODO: implement recursive splitting strategy
        if not text or not text.strip():
            return []
        return [chunk.strip() for chunk in self._split(text.strip(), self.separators) if chunk.strip()]

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        # TODO: recursive helper used by RecursiveChunker.chunk
        if len(current_text) <= self.chunk_size:
            return [current_text]
        if not remaining_separators:
            return [current_text[index: index + self.chunk_size] for index in range(0, len(current_text), self.chunk_size)]

        separator = remaining_separators[0]
        if separator == "":
            return [current_text[index: index + self.chunk_size] for index in range(0, len(current_text), self.chunk_size)]

        parts = current_text.split(separator)
        if len(parts) == 1:
            return self._split(current_text, remaining_separators[1:])

        chunks: list[str] = []
        pending = ""
        for part in parts:
            candidate = part if not pending else pending + separator + part
            if len(candidate) <= self.chunk_size:
                pending = candidate
                continue
            if pending:
                chunks.extend(self._split(pending, remaining_separators[1:]))
            pending = part
        if pending:
            chunks.extend(self._split(pending, remaining_separators[1:]))
        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    # TODO: implement cosine similarity formula
    norm_a = math.sqrt(_dot(vec_a, vec_a))
    norm_b = math.sqrt(_dot(vec_b, vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return _dot(vec_a, vec_b) / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        # TODO: call each chunker, compute stats, return comparison dict
        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=0),
            "by_sentences": SentenceChunker(max_sentences_per_chunk=3),
            "recursive": RecursiveChunker(chunk_size=chunk_size),
        }
        comparison = {}
        for name, chunker in strategies.items():
            chunks = chunker.chunk(text)
            comparison[name] = {
                "chunks": chunks,
                "count": len(chunks),
                "avg_length": sum(map(len, chunks)) / len(chunks) if chunks else 0.0,
            }
        return comparison
