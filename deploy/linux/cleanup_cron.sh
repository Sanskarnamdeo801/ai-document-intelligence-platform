#!/bin/bash
set -euo pipefail

APP_DIR="/opt/app"
API_BASE="${API_BASE:-http://127.0.0.1:8000/api/v1}"
ENV_FILE="$APP_DIR/backend/.env"

if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

DB_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/document_intelligence_db}"
DB_URL="${DB_URL/postgresql+psycopg2:/postgresql:}"

find /tmp -maxdepth 1 -type d -name "ai-document-platform*" -mtime +7 -exec rm -rf {} +
find "$APP_DIR/uploads" -type f -name "*.tmp" -mtime +2 -delete
find "$APP_DIR/logs" -type f -name "*.tmp" -mtime +2 -delete

if command -v psql >/dev/null 2>&1 && command -v curl >/dev/null 2>&1; then
    psql "$DB_URL" -Atc "SELECT id FROM uploaded_documents WHERE status = 'failed' ORDER BY upload_time DESC LIMIT 10" | \
    while IFS= read -r document_id; do
        if [ -n "$document_id" ]; then
            curl -fsS -X POST "$API_BASE/documents/$document_id/process" >/dev/null || true
        fi
    done
fi
