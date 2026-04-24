from datetime import datetime, timezone
import traceback

from sqlalchemy.orm import Session

from ..core.logging_config import logger
from ..models.document import AiSummary, DocumentChunk, DocumentMetadata, Embedding, PipelineLog, UploadedDocument
from ..core.database import SessionLocal
from .chunker import TextChunker
from .cleaner import TextCleaner
from .embedding_service import EmbeddingService
from .llm_service import LLMService
from .text_extractor import TextExtractor


class ProcessingPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.text_extractor = TextExtractor()
        self.cleaner = TextCleaner()
        self.chunker = TextChunker()
        self.embedder = EmbeddingService()
        self.llm_service = LLMService()

    def process_document(self, document_id: int, reset_outputs: bool = True) -> None:
        document = self.db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()
        if document is None:
            raise ValueError("Document not found")

        current_stage = "processing"

        try:
            document.status = "processing"
            document.error_trace = None
            document.processed_time = None
            self.db.commit()
            self._log_stage(document_id, "processing", "started", "Processing pipeline started")

            if reset_outputs:
                self._delete_existing_outputs(document_id)

            current_stage = "extraction"
            self._log_stage(document_id, "extraction", "started", "Extracting text from uploaded file")
            pages = self.text_extractor.extract(document.file_path, document.file_type or document.mime_type)
            extracted_text = "\n\n".join(text for text, _ in pages if text and text.strip()).strip()
            extracted_length = len(extracted_text)
            logger.info("Document %s extraction completed with %s characters", document_id, extracted_length)
            if not extracted_text:
                raise ValueError("No text extracted from document")
            self._log_stage(
                document_id,
                "extraction",
                "completed",
                f"Extracted {len(pages)} page groups with {extracted_length} characters",
            )

            current_stage = "cleaning"
            self._log_stage(document_id, "cleaning", "started", "Cleaning extracted text")
            cleaned_pages = self.cleaner.clean_pages(pages)
            cleaned_text = "\n\n".join(text for text, _ in cleaned_pages if text and text.strip()).strip()
            cleaned_length = len(cleaned_text)
            logger.info("Document %s cleaning completed with %s characters", document_id, cleaned_length)
            if not cleaned_text:
                raise ValueError("No readable content remained after cleaning")
            self._log_stage(
                document_id,
                "cleaning",
                "completed",
                f"Cleaned text length is {cleaned_length} characters across {len(cleaned_pages)} page groups",
            )

            current_stage = "chunking"
            self._log_stage(document_id, "chunking", "started", "Creating text chunks")
            chunk_rows = []
            for chunk_text, chunk_index, token_count, page_number in self.chunker.chunk_pages(cleaned_pages):
                if not chunk_text.strip():
                    continue
                chunk_rows.append(
                    DocumentChunk(
                        document_id=document_id,
                        chunk_index=chunk_index,
                        chunk_text=chunk_text,
                        token_count=token_count,
                        page_number=page_number,
                    )
                )
            if not chunk_rows:
                raise ValueError("No chunks were created from cleaned text")
            self.db.add_all(chunk_rows)
            self.db.commit()
            logger.info("Document %s chunking completed with %s chunks", document_id, len(chunk_rows))
            self._log_stage(document_id, "chunking", "completed", f"Created {len(chunk_rows)} chunks")

            persisted_chunks = (
                self.db.query(DocumentChunk)
                .filter(DocumentChunk.document_id == document_id)
                .order_by(DocumentChunk.chunk_index.asc())
                .all()
            )
            chunk_texts = [chunk.chunk_text for chunk in persisted_chunks if chunk.chunk_text and chunk.chunk_text.strip()]
            if not chunk_texts:
                raise ValueError("Chunk persistence failed because all chunk text is empty")

            current_stage = "summary"
            self._log_stage(document_id, "summary", "started", "Generating document summary")
            summary_text = self.llm_service.generate_summary(chunk_texts).strip()
            if not summary_text:
                raise ValueError("Summary generation produced empty output")
            self.db.add(
                AiSummary(
                    document_id=document_id,
                    summary_text=summary_text,
                    summary_type="full",
                    model_name=self.llm_service.model,
                )
            )
            self.db.commit()
            logger.info("Document %s summary saved", document_id)
            self._log_stage(document_id, "summary", "completed", "Summary saved")

            current_stage = "metadata"
            self._log_stage(document_id, "metadata", "started", "Extracting structured metadata")
            metadata = self.llm_service.extract_metadata(chunk_texts)
            self.db.add(
                DocumentMetadata(
                    document_id=document_id,
                    title=metadata["title"],
                    doc_type=metadata["doc_type"],
                    parties=metadata["parties"],
                    effective_date=metadata.get("effective_date"),
                    expiration_date=metadata.get("expiration_date"),
                    tags=metadata["tags"],
                    language=metadata["language"],
                    extracted_json=metadata,
                )
            )
            self.db.commit()
            logger.info("Document %s metadata saved", document_id)
            self._log_stage(document_id, "metadata", "completed", "Metadata saved")

            current_stage = "embeddings"
            self._log_stage(document_id, "embeddings", "started", "Generating embeddings for chunks")
            embeddings = self.embedder.generate_embeddings(chunk_texts)
            if len(embeddings) != len(persisted_chunks):
                raise ValueError(
                    f"Embedding count mismatch: expected {len(persisted_chunks)}, got {len(embeddings)}"
                )
            for chunk, vector in zip(persisted_chunks, embeddings):
                self.db.add(
                    Embedding(
                        document_id=document_id,
                        chunk_id=chunk.id,
                        embedding=list(vector),
                        model_name=self.embedder.model_name(),
                    )
                )
            self.db.commit()
            logger.info("Document %s embeddings saved count=%s", document_id, len(embeddings))
            self._log_stage(document_id, "embeddings", "completed", f"Saved {len(embeddings)} embeddings")

            summary_exists = self.db.query(AiSummary).filter(AiSummary.document_id == document_id).count() > 0
            metadata_exists = self.db.query(DocumentMetadata).filter(DocumentMetadata.document_id == document_id).count() > 0
            chunk_count = self.db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).count()
            embedding_count = self.db.query(Embedding).filter(Embedding.document_id == document_id).count()

            if not (chunk_count > 0 and summary_exists and metadata_exists and embedding_count > 0):
                raise ValueError("Processing outputs are incomplete; document cannot be marked completed")

            document.status = "completed"
            document.error_trace = None
            document.processed_time = datetime.now(timezone.utc)
            self.db.commit()
            logger.info("Document %s completed successfully", document_id)
            self._log_stage(document_id, "completed", "completed", "Document processing finished")
        except Exception as exc:
            full_trace = traceback.format_exc()
            logger.exception("Processing failed for document %s", document_id)
            document.status = "failed"
            document.error_trace = str(exc) if str(exc) else "Processing failed"
            self.db.commit()
            self._log_stage(document_id, current_stage, "failed", str(exc), error_trace=full_trace)
            raise

    def _delete_existing_outputs(self, document_id: int) -> None:
        self.db.query(Embedding).filter(Embedding.document_id == document_id).delete(synchronize_session=False)
        self.db.query(AiSummary).filter(AiSummary.document_id == document_id).delete(synchronize_session=False)
        self.db.query(DocumentMetadata).filter(DocumentMetadata.document_id == document_id).delete(synchronize_session=False)
        self.db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete(synchronize_session=False)
        self.db.commit()

    def _log_stage(
        self,
        document_id: int,
        stage: str,
        status: str,
        message: str,
        error_trace: str | None = None,
    ) -> None:
        self.db.add(
            PipelineLog(
                document_id=document_id,
                stage=stage,
                status=status,
                message=message,
                error_trace=error_trace,
            )
        )
        self.db.commit()
        logger.info("Document %s stage=%s status=%s message=%s", document_id, stage, status, message)


def run_document_processing(document_id: int, reset_outputs: bool = True) -> None:
    db = SessionLocal()
    try:
        ProcessingPipeline(db).process_document(document_id, reset_outputs=reset_outputs)
    finally:
        db.close()
