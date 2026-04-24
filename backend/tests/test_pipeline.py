from app.models.document import AiSummary, DocumentChunk, DocumentMetadata, Embedding, UploadedDocument
from app.services.pipeline import ProcessingPipeline


class StubLLMService:
    model = "llama3.2:3b"

    def generate_summary(self, chunks):
        assert chunks
        return "This is a generated summary."

    def extract_metadata(self, chunks):
        assert chunks
        return {
            "title": "Pipeline Test Document",
            "doc_type": "test",
            "parties": ["Alice", "Bob"],
            "effective_date": None,
            "expiration_date": None,
            "tags": ["test", "pipeline"],
            "language": "en",
        }


class StubEmbeddingService:
    def __init__(self):
        self.dimension = 384

    def generate_embeddings(self, texts):
        return [[0.01] * self.dimension for _ in texts]

    def model_name(self):
        return "all-MiniLM-L6-v2"


def test_processing_pipeline_creates_chunks_summary_metadata_and_embeddings(db_session, tmp_path):
    text_path = tmp_path / "pipeline.txt"
    text_path.write_text(
        "This document contains enough text to create chunks. " * 80,
        encoding="utf-8",
    )

    document = UploadedDocument(
        file_name="pipeline.txt",
        safe_file_name="pipeline.txt",
        file_type="txt",
        mime_type="text/plain",
        file_path=str(text_path),
        file_size=text_path.stat().st_size,
        checksum="pipeline-test-checksum",
        created_by="pytest",
        status="uploaded",
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    pipeline = ProcessingPipeline(db_session)
    pipeline.llm_service = StubLLMService()
    pipeline.embedder = StubEmbeddingService()

    pipeline.process_document(document.id)

    db_session.refresh(document)
    assert document.status == "completed"
    assert db_session.query(DocumentChunk).filter(DocumentChunk.document_id == document.id).count() > 0
    assert db_session.query(AiSummary).filter(AiSummary.document_id == document.id).count() == 1
    assert db_session.query(DocumentMetadata).filter(DocumentMetadata.document_id == document.id).count() == 1
    assert db_session.query(Embedding).filter(Embedding.document_id == document.id).count() > 0
