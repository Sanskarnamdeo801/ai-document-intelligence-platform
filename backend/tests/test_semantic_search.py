from unittest.mock import Mock

from app.services.semantic_search import SemanticSearchService


class StubEmbedder:
    def generate_single(self, text: str):
        assert text == "contract terms"
        return [1.0, 0.0]


def test_semantic_search_falls_back_when_pgvector_query_fails(monkeypatch):
    service = SemanticSearchService(embedder=StubEmbedder())

    def raise_pgvector_error(*args, **kwargs):
        raise RuntimeError("pgvector unavailable")

    monkeypatch.setattr(service, "_postgres_search", raise_pgvector_error)
    monkeypatch.setattr(
        service,
        "_fallback_rows",
        lambda db, document_id: [
            {
                "chunk_text": "Contract payment terms",
                "chunk_id": 1,
                "document_id": 10,
                "embedding": [1.0, 0.0],
            },
            {
                "chunk_text": "Employment policy handbook",
                "chunk_id": 2,
                "document_id": 11,
                "embedding": [0.0, 1.0],
            },
        ],
    )

    fake_db = Mock()
    fake_db.bind = Mock()
    fake_db.bind.dialect.name = "postgresql"

    results = service.search_chunks(fake_db, "contract terms", top_k=2)

    assert len(results) == 2
    assert results[0]["chunk_id"] == 1
    assert results[0]["similarity"] >= results[1]["similarity"]
