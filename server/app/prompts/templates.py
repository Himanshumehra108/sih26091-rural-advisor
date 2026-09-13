"""
templates.py
------------
Grounded prompt assembly for RAG-backed advisory responses.
"""

from __future__ import annotations

from dataclasses import dataclass


SYSTEM_PROMPT = """You are Rural Advisor, an assistant that answers farmers' \
questions about government schemes, subsidies, and agricultural programs.

Ground rules:
1. Answer ONLY using the information in the "Context" section below. Do \
not use outside knowledge, even if you are confident it is correct.
2. If the context does not contain enough information to answer the \
question, say so plainly -- for example: "I don't have information about \
that in the documents I have access to." Do NOT guess or fill gaps with \
assumptions.
3. When you state a fact, cite which source it came from using the \
bracketed source name given with each context chunk, e.g. [irrigation_subsidy.txt].
4. If different chunks conflict, point out the conflict rather than \
picking one silently.
5. Keep answers concise and practical -- farmers need a clear next step, \
not a wall of text. Use short paragraphs or a short list where it helps.
6. Never invent numbers, deadlines, eligibility criteria, or office names. \
If a specific figure isn't in the context, say it isn't available rather \
than estimating.
"""


NO_CONTEXT_FALLBACK = (
    "I don't have information about that in the documents I have access to. "
    "You may want to check with your local agriculture office directly."
)


@dataclass
class ContextChunk:
    text: str
    source: str
    distance: float


def format_context(chunks: list[ContextChunk]) -> str:
    if not chunks:
        return "(no relevant context was retrieved)"

    blocks = []
    for i, chunk in enumerate(chunks, start=1):
        blocks.append(f"[{chunk.source}]\n{chunk.text}")
    return "\n\n---\n\n".join(blocks)


def build_user_prompt(query: str, chunks: list[ContextChunk]) -> str:
    context_block = format_context(chunks)
    return f"""Context:
{context_block}

Question: {query}

Answer the question using only the context above. If the context doesn't \
answer it, say so instead of guessing."""


def should_use_fallback(chunks: list[ContextChunk], max_distance: float = 1.1) -> bool:
    if not chunks:
        return True
    return chunks[0].distance > max_distance
