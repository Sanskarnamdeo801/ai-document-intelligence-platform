#!/bin/bash
set -euo pipefail

APP_DIR="/opt/app"

mkdir -p "$APP_DIR/uploads" "$APP_DIR/logs" "$APP_DIR/backups"
mkdir -p "$APP_DIR/backend" "$APP_DIR/frontend/dist"

chown -R www-data:www-data "$APP_DIR"
chmod 755 "$APP_DIR"
chmod 775 "$APP_DIR/uploads" "$APP_DIR/logs" "$APP_DIR/backups"

echo "Prepared directories:"
echo "  $APP_DIR/uploads"
echo "  $APP_DIR/logs"
echo "  $APP_DIR/backups"
