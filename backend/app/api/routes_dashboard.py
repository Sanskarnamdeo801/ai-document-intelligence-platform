from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.document import DocumentChunk, PipelineLog, QueryHistory, UploadedDocument
from ..schemas.document import DashboardMetrics, RecentActivityItem

router = APIRouter()


@router.get("/dashboard/metrics", response_model=DashboardMetrics)
def get_metrics(db: Session = Depends(get_db)):
    return DashboardMetrics(
        total_documents=db.query(func.count(UploadedDocument.id)).scalar() or 0,
        total_chunks=db.query(func.count(DocumentChunk.id)).scalar() or 0,
        total_queries=db.query(func.count(QueryHistory.id)).scalar() or 0,
        completed_documents=(
            db.query(func.count(UploadedDocument.id))
            .filter(UploadedDocument.status == "completed")
            .scalar()
            or 0
        ),
        failed_documents=(
            db.query(func.count(UploadedDocument.id))
            .filter(UploadedDocument.status == "failed")
            .scalar()
            or 0
        ),
        processing_documents=(
            db.query(func.count(UploadedDocument.id))
            .filter(UploadedDocument.status == "processing")
            .scalar()
            or 0
        ),
    )


@router.get("/dashboard/recent-activity", response_model=List[RecentActivityItem])
def get_recent_activity(db: Session = Depends(get_db), limit: int = 20):
    document_items = [
        RecentActivityItem(
            activity_type="upload",
            message=f"Uploaded {document.file_name}",
            created_at=document.upload_time,
            document_id=document.id,
        )
        for document in db.query(UploadedDocument).order_by(UploadedDocument.upload_time.desc()).limit(limit).all()
    ]

    log_items = [
        RecentActivityItem(
            activity_type="pipeline",
            message=f"{log.stage}: {log.status} - {log.message}",
            created_at=log.created_at,
            document_id=log.document_id,
        )
        for log in db.query(PipelineLog).order_by(PipelineLog.created_at.desc()).limit(limit).all()
    ]

    query_items = [
        RecentActivityItem(
            activity_type=query.query_type,
            message=query.query_text,
            created_at=query.created_at,
            document_id=query.document_id,
        )
        for query in db.query(QueryHistory).order_by(QueryHistory.created_at.desc()).limit(limit).all()
    ]

    recent_items = sorted(
        document_items + log_items + query_items,
        key=lambda item: item.created_at,
        reverse=True,
    )
    return recent_items[:limit]
