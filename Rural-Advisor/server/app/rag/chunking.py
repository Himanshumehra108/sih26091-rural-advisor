"""
chunking.py
-----------
Chunk raw documents into overlapping text windows for retrieval.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Chunk:
    text: str
    source: str
    chunk_index: int
    metadata: dict = field(default_factory=dict)

    @property
    def id(self) -> str:
        return f"{self.source}::chunk-{self.chunk_index}"


def _split_into_sentences(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_text(
    text: str,
    source: str,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
) -> list[Chunk]:
    sentences = _split_into_sentences(text)
    if not sentences:
        return []

    chunks: list[Chunk] = []
    current = ""

    for sentence in sentences:
        if current and len(current) + len(sentence) + 1 > chunk_size:
            chunks.append(Chunk(text=current.strip(), source=source, chunk_index=len(chunks)))
            tail = current[-chunk_overlap:] if chunk_overlap > 0 else ""
            current = (tail + " " + sentence).strip()
        else:
            current = (current + " " + sentence).strip()

    if current:
        chunks.append(Chunk(text=current.strip(), source=source, chunk_index=len(chunks)))

    return chunks


def load_and_chunk_directory(
    directory: str | Path,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
    extensions: tuple[str, ...] = (".txt", ".md"),
) -> list[Chunk]:
    directory = Path(directory)
    all_chunks: list[Chunk] = []

    for path in sorted(directory.rglob("*")):
        if path.suffix.lower() not in extensions:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        doc_chunks = chunk_text(
            text,
            source=path.name,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        all_chunks.extend(doc_chunks)

    return all_chunks
