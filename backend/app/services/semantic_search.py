from math import sqrt
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from ..core.logging_config import logger
from ..models.document import DocumentChunk, Embedding
from .embedding_service import EmbeddingService


class SemanticSearchService:
    def __init__(self, embedder: EmbeddingService | None = None):
        self.embedder = embedder or EmbeddingService()

    def search_chunks(
        self,
        db: Session,
        query: str,
        document_id: int | None = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        query_embedding = self.embedder.generate_single(query)

        try:
            if db.bind is not None and db.bind.dialect.name == "postgresql":
                return self._postgres_search(db, query_embedding, document_id, top_k)
        except Exception as exc:
            logger.warning("pgvector semantic search failed, falling back to Python similarity: %s", exc)

        rows = self._fallback_rows(db, document_id)
        return self._fallback_search(rows, query_embedding, top_k)

    def _postgres_search(
        self,
        db: Session,
        query_embedding: List[float],
        document_id: int | None,
        top_k: int,
    ) -> List[Dict[str, Any]]:
        distance_expr = Embedding.embedding.cosine_distance(query_embedding)
        query = (
            db.query(
                DocumentChunk.chunk_text.label("chunk_text"),
                DocumentChunk.id.label("chunk_id"),
                Embedding.document_id.label("document_id"),
                (1 - distance_expr).label("similarity"),
            )
            .join(Embedding, Embedding.chunk_id == DocumentChunk.id)
        )
        if document_id is not None:
            query = query.filter(Embedding.document_id == document_id)

        rows = query.order_by(distance_expr).limit(top_k).all()
        return [
            {
                "chunk_text": row.chunk_text,
                "chunk_id": row.chunk_id,
                "document_id": row.document_id,
                "similarity": max(0.0, float(row.similarity)),
            }
            for row in rows
        ]

    def _fallback_rows(self, db: Session, document_id: int | None) -> List[Dict[str, Any]]:
        query = (
            db.query(
                DocumentChunk.chunk_text.label("chunk_text"),
                DocumentChunk.id.label("chunk_id"),
                Embedding.document_id.label("document_id"),
                Embedding.embedding.label("embedding"),
            )
            .join(Embedding, Embedding.chunk_id == DocumentChunk.id)
        )
        if document_id is not None:
            query = query.filter(Embedding.document_id == document_id)
        return [
            {
                "chunk_text": row.chunk_text,
                "chunk_id": row.chunk_id,
                "document_id": row.document_id,
                "embedding": self._coerce_embedding(row.embedding),
            }
            for row in query.all()
        ]

    def _fallback_search(
        self,
        rows: List[Dict[str, Any]],
        query_embedding: List[float],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for row in rows:
            similarity = self._cosine_similarity(query_embedding, row.get("embedding") or [])
            results.append(
                {
                    "chunk_text": row["chunk_text"],
                    "chunk_id": row["chunk_id"],
                    "document_id": row["document_id"],
                    "similarity": similarity,
                }
            )

        results.sort(key=lambda item: item["similarity"], reverse=True)
        return results[:top_k]

    def _coerce_embedding(self, embedding: Any) -> List[float]:
        if embedding is None:
            return []
        if isinstance(embedding, list):
            return [float(value) for value in embedding]
        if isinstance(embedding, tuple):
            return [float(value) for value in embedding]
        if hasattr(embedding, "tolist"):
            return [float(value) for value in embedding.tolist()]

        text_value = str(embedding).strip()
        if text_value.startswith("[") and text_value.endswith("]"):
            raw_values = text_value[1:-1].split(",")
            return [float(value.strip()) for value in raw_values if value.strip()]
        return []

    def _cosine_similarity(self, left: List[float], right: List[float]) -> float:
        if not left or not right or len(left) != len(right):
            return 0.0

        numerator = sum(a * b for a, b in zip(left, right))
        left_norm = sqrt(sum(a * a for a in left))
        right_norm = sqrt(sum(b * b for b in right))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return max(0.0, numerator / (left_norm * right_norm))
