import hashlib
import os
import re
from pathlib import Path

from ..core.config import settings
from ..core.logging_config import logger


class FileStorageService:
    allowed_types = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".txt": "text/plain",
    }

    def __init__(self):
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    def safe_filename(self, filename: str) -> str:
        name = Path(filename or "document").name
        stem = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(name).stem).strip("._") or "document"
        suffix = Path(name).suffix.lower()
        return f"{stem}{suffix}"

    def detect_file_type(self, filename: str) -> str:
        suffix = Path(filename or "").suffix.lower()
        if suffix not in self.allowed_types:
            raise ValueError("Only PDF, DOCX, and TXT files are supported")
        return suffix.lstrip(".")

    def detect_mime_type(self, filename: str, content_type: str | None) -> str:
        suffix = Path(filename or "").suffix.lower()
        default_mime = self.allowed_types.get(suffix)
        return content_type or default_mime or "application/octet-stream"

    def save_uploaded_file(self, content: bytes, filename: str, checksum: str) -> tuple[str, str]:
        safe_name = self.safe_filename(filename)
        target_name = f"{checksum}_{safe_name}"
        file_path = os.path.abspath(os.path.join(settings.UPLOAD_DIR, target_name))
        upload_root = os.path.abspath(settings.UPLOAD_DIR)

        if not file_path.startswith(upload_root):
            raise ValueError("Unsafe upload path resolved")

        if not os.path.exists(file_path):
            with open(file_path, "wb") as file_handle:
                file_handle.write(content)
            logger.info("Saved uploaded file to %s", file_path)

        return file_path, safe_name

    def compute_checksum(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def file_exists(self, file_path: str) -> bool:
        return os.path.exists(file_path)
