from app.services.embedding_service import EmbeddingService


def test_embedding_fallback_dimension_is_384(monkeypatch):
    monkeypatch.setattr(EmbeddingService, "_load_model", classmethod(lambda cls: None))
    service = EmbeddingService()

    embedding = service.generate_single("Sample text for embedding")

    assert len(embedding) == 384
