from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.document import PipelineLog, UploadedDocument
from ..schemas.document import ProcessingResponse
from ..services.pipeline import run_document_processing

router = APIRouter()


@router.post("/documents/{document_id}/process", response_model=ProcessingResponse)
def trigger_processing(
    document_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    document = db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.status == "processing":
        raise HTTPException(status_code=400, detail="Document is already processing")

    document.status = "processing"
    document.error_trace = None
    document.processed_time = None
    db.add(
        PipelineLog(
            document_id=document.id,
            stage="processing",
            status="started",
            message="Document reprocessing queued",
        )
    )
    db.commit()

    background_tasks.add_task(run_document_processing, document.id, True)
    return ProcessingResponse(message="Processing started", status="started")
