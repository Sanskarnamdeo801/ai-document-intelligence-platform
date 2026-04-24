import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from .api.routes_dashboard import router as dashboard_router
from .api.routes_documents import router as documents_router
from .api.routes_processing import router as processing_router
from .api.routes_qa import router as qa_router
from .api.routes_search import router as search_router
from .core.config import settings
from .core.database import get_db, init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    init_db()
    yield


app = FastAPI(title="AI Document Intelligence Platform", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router, prefix="/api/v1", tags=["documents"])
app.include_router(processing_router, prefix="/api/v1", tags=["processing"])
app.include_router(search_router, prefix="/api/v1", tags=["search"])
app.include_router(qa_router, prefix="/api/v1", tags=["qa"])
app.include_router(dashboard_router, prefix="/api/v1", tags=["dashboard"])


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
