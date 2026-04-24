import os
import shutil
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient


TEST_ROOT = Path(__file__).resolve().parent
TEST_UPLOAD_DIR = TEST_ROOT / "test_uploads"
TEST_LOG_DIR = TEST_ROOT / "test_logs"
TEST_DB_PATH = TEST_ROOT / "test_document_intelligence.db"
BACKEND_ROOT = TEST_ROOT.parent

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("DATABASE_URL", f"sqlite:///{TEST_DB_PATH}")
os.environ.setdefault("UPLOAD_DIR", str(TEST_UPLOAD_DIR))
os.environ.setdefault("LOG_DIR", str(TEST_LOG_DIR))
os.environ.setdefault("OLLAMA_HOST", "http://localhost:11434")
os.environ.setdefault("OLLAMA_MODEL", "llama3.2:3b")

from app.core.database import Base, SessionLocal, engine, init_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    TEST_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    TEST_LOG_DIR.mkdir(parents=True, exist_ok=True)
    init_db()
    yield
    Base.metadata.drop_all(bind=engine)
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    shutil.rmtree(TEST_UPLOAD_DIR, ignore_errors=True)
    shutil.rmtree(TEST_LOG_DIR, ignore_errors=True)


@pytest.fixture(autouse=True)
def clean_database():
    with engine.begin() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())
    yield


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
