#!/bin/bash
set -euo pipefail

APP_DIR="/opt/app"
BACKUP_DIR="$APP_DIR/backups"
ENV_FILE="$APP_DIR/backend/.env"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

DB_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/document_intelligence_db}"
DB_URL="${DB_URL/postgresql+psycopg2:/postgresql:}"

mkdir -p "$BACKUP_DIR"

pg_dump "$DB_URL" | gzip > "$BACKUP_DIR/db_${TIMESTAMP}.sql.gz"

find "$APP_DIR/uploads" -type f -mtime -30 -print0 | \
tar --null -czf "$BACKUP_DIR/uploads_${TIMESTAMP}.tar.gz" --files-from -

find "$BACKUP_DIR" -type f -name "*.gz" -mtime +7 -delete

echo "Backup completed: $TIMESTAMP"
