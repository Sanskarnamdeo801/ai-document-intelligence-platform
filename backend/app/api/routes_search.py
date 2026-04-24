import time
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.document import QueryHistory
from ..schemas.document import SearchQuery, SearchResult
from ..services.semantic_search import SemanticSearchService

router = APIRouter()
search_service = SemanticSearchService()


@router.post("/search", response_model=List[SearchResult])
def semantic_search(query: SearchQuery, db: Session = Depends(get_db)):
    started_at = time.perf_counter()
    results = search_service.search_chunks(db, query.query, query.document_id, query.top_k)
    response_time_ms = int((time.perf_counter() - started_at) * 1000)

    db.add(
        QueryHistory(
            document_id=query.document_id,
            query_type="semantic_search",
            query_text=query.query,
            answer_text=None,
            top_k=query.top_k,
            response_time_ms=response_time_ms,
        )
    )
    db.commit()

    return [SearchResult(**result) for result in results]
