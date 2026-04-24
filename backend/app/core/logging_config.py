import logging
import os
from logging.handlers import RotatingFileHandler

from .config import settings


os.makedirs(settings.LOG_DIR, exist_ok=True)

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

root_logger = logging.getLogger()
if not root_logger.handlers:
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

log_path = os.path.join(settings.LOG_DIR, "app.log")
existing_paths = {
    getattr(handler, "baseFilename", None)
    for handler in root_logger.handlers
    if hasattr(handler, "baseFilename")
}

if log_path not in existing_paths:
    file_handler = RotatingFileHandler(log_path, maxBytes=10 * 1024 * 1024, backupCount=5)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    root_logger.addHandler(file_handler)


logger = logging.getLogger("ai_document_platform")
