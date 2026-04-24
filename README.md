# AI Document Intelligence Platform

FastAPI backend + React frontend for document upload, extraction, chunking, summarization, metadata extraction, semantic search, and Q&A. The project uses PostgreSQL with `pgvector`, Ollama for local LLM generation, and `sentence-transformers` for embeddings.

## Stack

- Backend: FastAPI, SQLAlchemy, pytest
- Frontend: React + Vite
- Database: PostgreSQL
- Vector store: pgvector
- LLM: Ollama (`llama3.2:3b`)
- Embeddings: `sentence-transformers` (`all-MiniLM-L6-v2`, dimension `384`)
- Deployment: gunicorn, nginx, systemd, cron, shell scripts
- CI/CD: GitHub Actions

## Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Example `.env`:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/document_intelligence_db
UPLOAD_DIR=./uploads
LOG_DIR=./logs
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
MAX_UPLOAD_SIZE_MB=50
```

Run the backend:

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Build the frontend:

```bash
cd frontend
npm run build
```

## PostgreSQL + pgvector Setup

Create the database:

```bash
createdb document_intelligence_db
psql document_intelligence_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

Initialize schema with SQL:

```bash
psql document_intelligence_db -f backend/sql/init_db.sql
```

Or rely on SQLAlchemy demo initialization:

```bash
cd backend
source venv/bin/activate
python -c "from app.core.database import init_db; init_db()"
```

### pgAdmin SQL commands

```sql
CREATE DATABASE document_intelligence_db;
\c document_intelligence_db;
CREATE EXTENSION IF NOT EXISTS vector;
\i /absolute/path/to/backend/sql/init_db.sql
```

## Ollama Setup

Install Ollama, start it, then pull the required models:

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

The backend uses:

- `OLLAMA_MODEL=llama3.2:3b`
- `OLLAMA_HOST=http://localhost:11434`

Embeddings are generated locally with `sentence-transformers`. If the embedding model cannot be loaded, the service falls back to deterministic local vectors so tests and offline environments still run.

## Processing Flow

```text
upload -> extraction -> cleaning -> chunking -> summary -> metadata -> embeddings -> completed
```

Artifacts written by the pipeline:

- `uploaded_documents`
- `document_chunks`
- `ai_summaries`
- `document_metadata`
- `embedding_store`
- `pipeline_logs`
- `query_history`

## API Endpoints

- `GET /health`
- `GET /health/db`
- `POST /api/v1/documents/upload`
- `GET /api/v1/documents`
- `GET /api/v1/documents/{document_id}`
- `POST /api/v1/documents/{document_id}/process`
- `GET /api/v1/documents/{document_id}/summary`
- `GET /api/v1/documents/{document_id}/metadata`
- `GET /api/v1/documents/{document_id}/chunks`
- `GET /api/v1/documents/{document_id}/logs`
- `POST /api/v1/search`
- `POST /api/v1/qa`
- `GET /api/v1/dashboard/metrics`
- `GET /api/v1/dashboard/recent-activity`

## Testing

Run backend tests:

```bash
cd backend
source venv/bin/activate
pytest tests/
```

The test suite covers:

- health endpoints
- upload validation and deduplication
- chunker
- cleaner
- model imports
- semantic search fallback behavior

Ollama is not required for the tests. LLM calls are not exercised in the suite.

## Linux Deployment

Prepare directories:

```bash
chmod +x deploy/linux/*.sh
sudo ./deploy/linux/setup_env.sh
```

Backend service:

```bash
sudo cp deploy/linux/app.service /etc/systemd/system/app.service
sudo systemctl daemon-reload
sudo systemctl enable app
sudo systemctl start app
```

Nginx:

```bash
sudo cp deploy/linux/nginx.conf /etc/nginx/sites-available/app
sudo ln -sf /etc/nginx/sites-available/app /etc/nginx/sites-enabled/app
sudo nginx -t
sudo systemctl reload nginx
```

Suggested cron jobs:

```bash
0 1 * * * /opt/app/deploy/linux/rotate_logs.sh
0 2 * * * /opt/app/deploy/linux/backup_export.sh
0 3 * * 0 /opt/app/deploy/linux/cleanup_cron.sh
```

Managed directories:

- `/opt/app/uploads`
- `/opt/app/logs`
- `/opt/app/backups`

## Local Commands Summary

Backend:

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm run dev
```

Manual processing example:

```bash
curl -F "file=@/path/to/document.pdf" -F "created_by=local-user" http://127.0.0.1:8000/api/v1/documents/upload
curl -X POST http://127.0.0.1:8000/api/v1/documents/1/process
curl -X POST http://127.0.0.1:8000/api/v1/search -H "Content-Type: application/json" -d '{"query":"termination clause","top_k":5}'
curl -X POST http://127.0.0.1:8000/api/v1/qa -H "Content-Type: application/json" -d '{"question":"What is the renewal term?","top_k":3}'
```

## GitHub Actions

`.github/workflows/ci.yml` runs two jobs:

- Backend CI: starts PostgreSQL with pgvector, enables the `vector` extension, installs Python dependencies, and runs `pytest`.
- Frontend CI: installs Node dependencies and builds the React app.
