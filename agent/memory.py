"""
Long-term conversational memory using ChromaDB and sentence embeddings.
Provides RAG capabilities for context-aware responses.
"""

import logging
import time
from typing import Optional
from dataclasses import dataclass, field

import chromadb

from config.config import MEMORY_DIR, MEMORY_COLLECTION, MEMORY_TOP_K

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """A single memory record to be stored."""

    user_message: str
    assistant_response: str
    sentiment_label: str
    sentiment_score: float
    emotion: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class RetrievedMemory:
    """A memory retrieved via similarity search."""

    user_message: str
    assistant_response: str
    sentiment_label: str
    emotion: str
    distance: float
    timestamp: float


class ConversationMemory:
    """ChromaDB-backed long-term conversation memory with RAG retrieval."""

    def __init__(
        self,
        persist_dir: str = str(MEMORY_DIR),
        collection_name: str = MEMORY_COLLECTION,
    ):
        self._client = chromadb.PersistentClient(path=persist_dir)
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            "Memory initialized: %d entries in '%s'.",
            self._collection.count(),
            collection_name,
        )

    def store(self, entry: MemoryEntry) -> None:
        """Store a conversation turn in memory."""
        doc_id = f"msg_{int(entry.timestamp * 1000)}"
        document = f"User: {entry.user_message}\nAssistant: {entry.assistant_response}"
        metadata = {
            "user_message": entry.user_message[:500],
            "assistant_response": entry.assistant_response[:500],
            "sentiment_label": entry.sentiment_label,
            "sentiment_score": entry.sentiment_score,
            "emotion": entry.emotion,
            "timestamp": entry.timestamp,
        }
        self._collection.add(
            ids=[doc_id],
            documents=[document],
            metadatas=[metadata],
        )
        logger.debug("Stored memory: %s", doc_id)

    def retrieve(self, query: str, top_k: int = MEMORY_TOP_K) -> list[RetrievedMemory]:
        """Retrieve the most relevant past conversations for a query."""
        if self._collection.count() == 0:
            return []

        effective_k = min(top_k, self._collection.count())
        results = self._collection.query(
            query_texts=[query],
            n_results=effective_k,
        )

        memories = []
        if results and results["metadatas"]:
            for meta, dist in zip(results["metadatas"][0], results["distances"][0]):
                memories.append(
                    RetrievedMemory(
                        user_message=meta.get("user_message", ""),
                        assistant_response=meta.get("assistant_response", ""),
                        sentiment_label=meta.get("sentiment_label", "neutral"),
                        emotion=meta.get("emotion", "neutral"),
                        distance=dist,
                        timestamp=meta.get("timestamp", 0),
                    )
                )
        return memories

    @property
    def count(self) -> int:
        """Total number of stored memories."""
        return self._collection.count()
