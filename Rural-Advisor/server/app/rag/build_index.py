"""
build_index.py
--------------
Build a Chroma index from source markdown/text documents.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from chunking import load_and_chunk_directory
from vector_store import RagVectorStore


def main():
    parser = argparse.ArgumentParser(description="Chunk documents and build the vector index.")
    parser.add_argument(
        "--documents",
        default=str(Path(__file__).parent / "documents"),
        help="Folder of .txt/.md documents to index",
    )
    parser.add_argument("--chunk-size", type=int, default=800)
    parser.add_argument("--chunk-overlap", type=int, default=120)
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Wipe the existing index before rebuilding",
    )
    args = parser.parse_args()

    print(f"Loading and chunking documents from: {args.documents}")
    chunks = load_and_chunk_directory(
        args.documents,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )
    print(f"Produced {len(chunks)} chunks from the source documents.")

    if not chunks:
        print("No chunks produced -- check that the documents folder has .txt/.md files.")
        return

    store = RagVectorStore()
    if args.reset:
        print("Resetting existing index...")
        store.reset()

    print("Embedding and storing chunks...")
    store.add_chunks(chunks)
    print(f"Done. Index now contains {store.count()} chunks.")


if __name__ == "__main__":
    main()
