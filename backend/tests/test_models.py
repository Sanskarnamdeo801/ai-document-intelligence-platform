from app.models.document import AiSummary, DocumentChunk, DocumentMetadata, Embedding, PipelineLog, QueryHistory, UploadedDocument


def test_model_imports_and_required_tables_exist():
    assert UploadedDocument.__tablename__ == "uploaded_documents"
    assert DocumentChunk.__tablename__ == "document_chunks"
    assert DocumentMetadata.__tablename__ == "document_metadata"
    assert AiSummary.__tablename__ == "ai_summaries"
    assert Embedding.__tablename__ == "embedding_store"
    assert QueryHistory.__tablename__ == "query_history"
    assert PipelineLog.__tablename__ == "pipeline_logs"
