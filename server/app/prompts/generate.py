"""
generate.py
-----------
Wires retrieval and prompt engineering together for advisory queries.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "rag"))

from vector_store import RagVectorStore  # noqa: E402
from templates import (  # noqa: E402
    SYSTEM_PROMPT,
    NO_CONTEXT_FALLBACK,
    ContextChunk,
    build_user_prompt,
    should_use_fallback,
)


def retrieve_context(query: str, top_k: int = 4) -> list[ContextChunk]:
    store = RagVectorStore()
    if store.count() == 0:
        raise RuntimeError("The vector index is empty. Run rag/build_index.py first.")
    hits = store.query(query, top_k=top_k)
    return [ContextChunk(text=h["text"], source=h["source"], distance=h["distance"]) for h in hits]


def call_claude(system_prompt: str, user_prompt: str) -> str:
    try:
        import anthropic
    except ImportError as e:
        raise RuntimeError("The 'anthropic' package isn't installed. Run: pip install anthropic") from e

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


def main():
    parser = argparse.ArgumentParser(description="Retrieve context and build/run a grounded RAG prompt.")
    parser.add_argument("question", help="The farmer's question")
    parser.add_argument("--top-k", type=int, default=4, help="Number of chunks to retrieve")
    parser.add_argument(
        "--max-distance",
        type=float,
        default=1.1,
        help="Cosine-distance cutoff for the 'no relevant context' fallback",
    )
    parser.add_argument(
        "--call",
        action="store_true",
        help="Actually call Claude with the prompt (requires ANTHROPIC_API_KEY).",
    )
    args = parser.parse_args()

    chunks = retrieve_context(args.question, top_k=args.top_k)

    print("Retrieved chunks:")
    for c in chunks:
        print(f"  - [{c.source}] distance={c.distance:.4f}")
    print()

    if should_use_fallback(chunks, max_distance=args.max_distance):
        print("No sufficiently relevant context found -- using fallback instead of calling the LLM.\n")
        print(NO_CONTEXT_FALLBACK)
        return

    user_prompt = build_user_prompt(args.question, chunks)

    if not args.call:
        print("=" * 60)
        print("SYSTEM PROMPT")
        print("=" * 60)
        print(SYSTEM_PROMPT)
        print("=" * 60)
        print("USER PROMPT (context + question)")
        print("=" * 60)
        print(user_prompt)
        print("\n(Pass --call to actually send this to Claude and print the answer.)")
        return

    print("Calling Claude...\n")
    answer = call_claude(SYSTEM_PROMPT, user_prompt)
    print("=" * 60)
    print("ANSWER")
    print("=" * 60)
    print(answer)


if __name__ == "__main__":
    main()
