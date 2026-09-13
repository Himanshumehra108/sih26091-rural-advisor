"""
query.py
--------
Query the local vector index for relevant text chunks.
"""

from __future__ import annotations

import argparse

from vector_store import RagVectorStore


def main():
    parser = argparse.ArgumentParser(description="Query the RAG vector index.")
    parser.add_argument("question", help="Natural-language question to search for")
    parser.add_argument("--top-k", type=int, default=4, help="Number of chunks to retrieve")
    args = parser.parse_args()

    store = RagVectorStore()
    if store.count() == 0:
        print("Index is empty. Run build_index.py first.")
        return

    hits = store.query(args.question, top_k=args.top_k)

    print(f'\nTop {len(hits)} chunks for: "{args.question}"\n' + "-" * 60)
    for rank, hit in enumerate(hits, start=1):
        print(f"\n#{rank}  source={hit['source']}  chunk={hit['chunk_index']}  distance={hit['distance']:.4f}")
        print(hit["text"])


if __name__ == "__main__":
    main()
