#!/bin/bash
set -euo pipefail

LOG_DIR="/opt/app/logs"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

mkdir -p "$LOG_DIR"

shopt -s nullglob
for log_file in "$LOG_DIR"/*.log; do
    rotated_file="${log_file}.${TIMESTAMP}"
    cp "$log_file" "$rotated_file"
    : > "$log_file"
    gzip -f "$rotated_file"
done
shopt -u nullglob

find "$LOG_DIR" -type f -name "*.gz" -mtime +14 -delete
