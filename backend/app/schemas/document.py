from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentBase(BaseModel):
    file_name: str
    safe_file_name: str
    file_type: str
    mime_type: str
    file_size: int
    checksum: str


class Document(DocumentBase):
    id: int
    uuid: UUID
    file_path: str
    status: DocumentStatus
    upload_time: datetime
    processed_time: Optional[datetime] = None
    created_by: Optional[str] = None
    error_trace: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class Chunk(BaseModel):
    id: int
    chunk_index: int
    chunk_text: str
    token_count: int
    page_number: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Metadata(BaseModel):
    title: str
    doc_type: str
    parties: List[str] = Field(default_factory=list)
    effective_date: Optional[str] = None
    expiration_date: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    language: str
    extracted_json: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Summary(BaseModel):
    summary_text: str
    summary_type: str
    model_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class PipelineLogEntry(BaseModel):
    stage: str
    status: str
    message: str
    error_trace: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SearchQuery(BaseModel):
    query: str
    document_id: Optional[int] = None
    top_k: int = 5


class SearchResult(BaseModel):
    chunk_text: str
    chunk_id: int
    document_id: int
    similarity: float


class QAQuery(BaseModel):
    question: str
    document_id: Optional[int] = None
    top_k: int = 3


class QAResponse(BaseModel):
    answer: str
    sources: List[SearchResult]
    response_time_ms: int


class ProcessingResponse(BaseModel):
    message: str
    status: str


class DocumentDebugResponse(BaseModel):
    document_id: int
    file_name: str
    file_path: str
    status: str
    error_trace: Optional[str] = None
    extracted_file_exists: bool
    chunks_count: int
    non_empty_chunks_count: int
    embeddings_count: int
    summary_exists: bool
    metadata_exists: bool
    recent_pipeline_logs: List[PipelineLogEntry]


class DashboardMetrics(BaseModel):
    total_documents: int
    total_chunks: int
    total_queries: int
    completed_documents: int
    failed_documents: int
    processing_documents: int


class RecentActivityItem(BaseModel):
    activity_type: str
    message: str
    created_at: datetime
    document_id: Optional[int] = None
