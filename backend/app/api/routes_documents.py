from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import desc
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.database import get_db
from ..models.document import AiSummary, DocumentChunk, DocumentMetadata, Embedding, PipelineLog, UploadedDocument
from ..schemas.document import Chunk, Document, DocumentDebugResponse, Metadata, PipelineLogEntry, Summary
from ..services.file_storage import FileStorageService
from ..services.pipeline import run_document_processing

router = APIRouter()


@router.post("/documents/upload", response_model=Document)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    created_by: str = Form("anonymous"),
    db: Session = Depends(get_db),
):
    file_storage = FileStorageService()

    try:
        file_type = file_storage.detect_file_type(file.filename or "")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if file.content_type and file.content_type not in file_storage.allowed_types.values():
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are allowed")

    content = file.file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Uploaded file exceeds the configured size limit")

    checksum = file_storage.compute_checksum(content)
    existing_document = (
        db.query(UploadedDocument)
        .filter(UploadedDocument.checksum == checksum)
        .order_by(desc(UploadedDocument.upload_time))
        .first()
    )
    if existing_document:
        return existing_document

    file_path, safe_file_name = file_storage.save_uploaded_file(content, file.filename or "document", checksum)

    document = UploadedDocument(
        file_name=file.filename or safe_file_name,
        safe_file_name=safe_file_name,
        file_type=file_type,
        mime_type=file_storage.detect_mime_type(file.filename or safe_file_name, file.content_type),
        file_path=file_path,
        file_size=len(content),
        checksum=checksum,
        created_by=created_by,
        status="uploaded",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    db.add(
        PipelineLog(
            document_id=document.id,
            stage="upload",
            status="completed",
            message=f"Uploaded file {document.safe_file_name}",
        )
    )
    document.status = "processing"
    db.commit()

    background_tasks.add_task(run_document_processing, document.id, True)
    return document


@router.get("/documents", response_model=List[Document])
def list_documents(db: Session = Depends(get_db), limit: int = 50, skip: int = 0):
    return (
        db.query(UploadedDocument)
        .order_by(desc(UploadedDocument.upload_time))
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/documents/{document_id}", response_model=Document)
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.get("/documents/{document_id}/summary", response_model=Summary)
def get_document_summary(document_id: int, db: Session = Depends(get_db)):
    summary = db.query(AiSummary).filter(AiSummary.document_id == document_id).first()
    if summary is None:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary


@router.get("/documents/{document_id}/metadata", response_model=Metadata)
def get_document_metadata(document_id: int, db: Session = Depends(get_db)):
    metadata = db.query(DocumentMetadata).filter(DocumentMetadata.document_id == document_id).first()
    if metadata is None:
        raise HTTPException(status_code=404, detail="Metadata not found")
    return metadata


@router.get("/documents/{document_id}/chunks", response_model=List[Chunk])
def get_document_chunks(document_id: int, db: Session = Depends(get_db)):
    return (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index.asc())
        .all()
    )


@router.get("/documents/{document_id}/logs", response_model=List[PipelineLogEntry])
def get_document_logs(document_id: int, db: Session = Depends(get_db)):
    return (
        db.query(PipelineLog)
        .filter(PipelineLog.document_id == document_id)
        .order_by(PipelineLog.created_at.asc(), PipelineLog.id.asc())
        .all()
    )


@router.get("/documents/{document_id}/debug", response_model=DocumentDebugResponse)
def get_document_debug(document_id: int, db: Session = Depends(get_db)):
    document = db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    file_storage = FileStorageService()
    chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).all()
    non_empty_chunks_count = sum(1 for chunk in chunks if chunk.chunk_text and chunk.chunk_text.strip())
    embeddings_count = db.query(Embedding).filter(Embedding.document_id == document_id).count()
    summary_exists = db.query(AiSummary).filter(AiSummary.document_id == document_id).count() > 0
    metadata_exists = db.query(DocumentMetadata).filter(DocumentMetadata.document_id == document_id).count() > 0
    recent_logs = (
        db.query(PipelineLog)
        .filter(PipelineLog.document_id == document_id)
        .order_by(PipelineLog.created_at.desc(), PipelineLog.id.desc())
        .limit(10)
        .all()
    )

    return DocumentDebugResponse(
        document_id=document.id,
        file_name=document.file_name,
        file_path=document.file_path,
        status=document.status,
        error_trace=document.error_trace,
        extracted_file_exists=file_storage.file_exists(document.file_path),
        chunks_count=len(chunks),
        non_empty_chunks_count=non_empty_chunks_count,
        embeddings_count=embeddings_count,
        summary_exists=summary_exists,
        metadata_exists=metadata_exists,
        recent_pipeline_logs=list(reversed(recent_logs)),
    )
