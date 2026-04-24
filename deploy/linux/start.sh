#!/bin/bash
set -euo pipefail

cd /opt/app/backend

if [ ! -d "venv" ]; then
    echo "Python virtual environment not found at /opt/app/backend/venv" >&2
    exit 1
fi

mkdir -p /opt/app/uploads /opt/app/logs /opt/app/backups

source venv/bin/activate
exec gunicorn app.main:app -k uvicorn.workers.UvicornWorker --config /opt/app/backend/gunicorn.conf.py
