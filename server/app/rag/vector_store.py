"""
vector_store.py
---------------
Persistent vector store backed by Chroma for advisory
 document retrieval.
"""


from __future__ import annotations

from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

from chunking import Chunk

DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_COLLECTION_NAME = "rural_advisor_docs"
DEFAULT_PERSIST_DIR = str(Path(__file__).parent / "chroma_db")


class RagVectorStore:
    def __init__(
        self,
        persist_dir: str = DEFAULT_PERSIST_DIR,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        model_name: str = DEFAULT_MODEL_NAME,
    ):
        self._embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=model_name
        )

        self._client = chromadb.PersistentClient(path=persist_dir)
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            embedding_function=self._embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, chunks: list[Chunk], batch_size: int = 64) -> None:
        if not chunks:
            return

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            self._collection.upsert(
                ids=[c.id for c in batch],
                documents=[c.text for c in batch],
                metadatas=[{"source": c.source, "chunk_index": c.chunk_index, **c.metadata} for c in batch],
            )

    def query(self, query_text: str, top_k: int = 4) -> list[dict]:
        results = self._collection.query(
            query_texts=[query_text],
            n_results=top_k,
        )

        hits = []
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        dists = results["distances"][0]

        for text, meta, distance in zip(docs, metas, dists):
            hits.append(
                {
                    "text": text,
                    "source": meta.get("source"),
                    "chunk_index": meta.get("chunk_index"),
                    "distance": distance,
                }
            )
        return hits

    def count(self) -> int:
        return self._collection.count()

    def reset(self) -> None:
        self._client.delete_collection(self._collection.name)
        self._collection = self._client.get_or_create_collection(
            name=self._collection.name,
            embedding_function=self._embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )
