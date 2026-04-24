import hashlib
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

from ..core.config import settings
from ..core.logging_config import logger


class EmbeddingService:
    _model: SentenceTransformer | None = None
    _model_error: str | None = None

    def __init__(self):
        self.dimension = settings.EMBEDDING_DIMENSION

    @classmethod
    def _load_model(cls) -> SentenceTransformer | None:
        if cls._model is not None:
            return cls._model
        if cls._model_error is not None:
            return None

        try:
            cls._model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info("Loaded embedding model: %s", settings.EMBEDDING_MODEL)
            return cls._model
        except Exception as exc:
            cls._model_error = str(exc)
            logger.warning("Falling back to deterministic embeddings: %s", exc)
            return None

    def generate_embeddings(self, texts: List[str]) -> List[list[float]]:
        if not texts:
            return []

        model = self._load_model()
        if model is not None:
            try:
                embeddings = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
                return [self._validate_embedding(vector) for vector in embeddings]
            except Exception as exc:
                logger.warning("SentenceTransformer encode failed, using fallback embeddings: %s", exc)

        return [self._fallback_embedding(text) for text in texts]

    def generate_single(self, text: str) -> list[float]:
        return self.generate_embeddings([text])[0]

    def model_name(self) -> str:
        return settings.EMBEDDING_MODEL if self._model is not None else "deterministic-fallback"

    def _validate_embedding(self, vector) -> list[float]:
        normalized = np.asarray(vector, dtype=float).flatten().tolist()
        if len(normalized) != self.dimension:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self.dimension}, got {len(normalized)}"
            )
        return normalized

    def _fallback_embedding(self, text: str) -> list[float]:
        vector = np.zeros(self.dimension, dtype=float)
        tokens = text.lower().split() or [text.lower() or "empty"]

        for token_index, token in enumerate(tokens):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            for byte_index, byte in enumerate(digest):
                vector[(token_index * len(digest) + byte_index) % self.dimension] += (byte / 255.0) - 0.5

        norm = np.linalg.norm(vector)
        if norm == 0:
            vector[0] = 1.0
            norm = 1.0

        normalized = (vector / norm).tolist()
        return self._validate_embedding(normalized)
