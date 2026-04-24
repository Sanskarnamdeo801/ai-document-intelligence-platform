import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import relationship

from ..core.config import settings
from ..core.database import Base


class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(Uuid(as_uuid=True), default=uuid.uuid4, nullable=False, unique=True)
    file_name = Column(String(255), nullable=False)
    safe_file_name = Column(String(255), nullable=False)
    file_type = Column(String(100), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_path = Column(String(1024), nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="uploaded", index=True)
    checksum = Column(String(64), nullable=False, index=True)
    created_by = Column(String(100))
    error_trace = Column(Text)
    upload_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_time = Column(DateTime(timezone=True))

    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="DocumentChunk.chunk_index",
    )
    document_metadata = relationship(
        "DocumentMetadata",
        back_populates="document",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    ai_summary = relationship(
        "AiSummary",
        back_populates="document",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    embeddings = relationship(
        "Embedding",
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    queries = relationship("QueryHistory", back_populates="document")
    logs = relationship(
        "PipelineLog",
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="PipelineLog.created_at",
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("uploaded_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=False)
    page_number = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    document = relationship("UploadedDocument", back_populates="chunks")
    embedding_record = relationship(
        "Embedding",
        back_populates="chunk",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class DocumentMetadata(Base):
    __tablename__ = "document_metadata"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("uploaded_documents.id", ondelete="CASCADE"), nullable=False, unique=True)
    title = Column(String(255), nullable=False, default="")
    doc_type = Column(String(100), nullable=False, default="unknown")
    parties = Column(JSON, nullable=False, default=list)
    effective_date = Column(String(100))
    expiration_date = Column(String(100))
    tags = Column(JSON, nullable=False, default=list)
    language = Column(String(50), nullable=False, default="en")
    extracted_json = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    document = relationship("UploadedDocument", back_populates="document_metadata")


class AiSummary(Base):
    __tablename__ = "ai_summaries"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("uploaded_documents.id", ondelete="CASCADE"), nullable=False, unique=True)
    summary_text = Column(Text, nullable=False)
    summary_type = Column(String(20), nullable=False, default="full")
    model_name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    document = relationship("UploadedDocument", back_populates="ai_summary")


class Embedding(Base):
    __tablename__ = "embedding_store"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("uploaded_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_id = Column(Integer, ForeignKey("document_chunks.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION), nullable=False)
    model_name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    document = relationship("UploadedDocument", back_populates="embeddings")
    chunk = relationship("DocumentChunk", back_populates="embedding_record")


class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("uploaded_documents.id", ondelete="SET NULL"), nullable=True, index=True)
    query_type = Column(String(50), nullable=False)
    query_text = Column(Text, nullable=False)
    answer_text = Column(Text)
    top_k = Column(Integer, nullable=False, default=5)
    response_time_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    document = relationship("UploadedDocument", back_populates="queries")


class PipelineLog(Base):
    __tablename__ = "pipeline_logs"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("uploaded_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    stage = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    message = Column(Text, nullable=False, default="")
    error_trace = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    document = relationship("UploadedDocument", back_populates="logs")
