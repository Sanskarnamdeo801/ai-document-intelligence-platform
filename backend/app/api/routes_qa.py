import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.document import DocumentChunk, Embedding, QueryHistory, UploadedDocument
from ..schemas.document import QAQuery, QAResponse, SearchResult
from ..services.llm_service import LLMService
from ..services.semantic_search import SemanticSearchService

router = APIRouter()
search_service = SemanticSearchService()
llm_service = LLMService()


@router.post("/qa", response_model=QAResponse)
def ask_question(query: QAQuery, db: Session = Depends(get_db)):
    started_at = time.perf_counter()
    answer = ""
    search_results = []

    if query.document_id is not None:
        document = db.query(UploadedDocument).filter(UploadedDocument.id == query.document_id).first()
        if document is None:
            raise HTTPException(status_code=404, detail="Document not found")

        if document.status != "completed":
            answer = f"This document is not processed yet. Current status: {document.status}"
        else:
            chunks_count = db.query(DocumentChunk).filter(DocumentChunk.document_id == query.document_id).count()
            embeddings_count = db.query(Embedding).filter(Embedding.document_id == query.document_id).count()
            if chunks_count == 0:
                answer = "No text chunks were extracted from this document."
            elif embeddings_count == 0:
                answer = "This document has chunks but embeddings are missing. Please reprocess it."

    if not answer:
        search_results = search_service.search_chunks(db, query.question, query.document_id, query.top_k)
        if not search_results:
            answer = "No relevant document context was found for this question."
        else:
            context_chunks = [result["chunk_text"] for result in search_results if result.get("chunk_text")]
            if not context_chunks:
                answer = "No relevant document context was found for this question."
            else:
                answer = llm_service.answer_question(query.question, context_chunks)

    response_time_ms = int((time.perf_counter() - started_at) * 1000)

    db.add(
        QueryHistory(
            document_id=query.document_id,
            query_type="qa",
            query_text=query.question,
            answer_text=answer,
            top_k=query.top_k,
            response_time_ms=response_time_ms,
        )
    )
    db.commit()

    return QAResponse(
        answer=answer,
        sources=[SearchResult(**result) for result in search_results],
        response_time_ms=response_time_ms,
    )
