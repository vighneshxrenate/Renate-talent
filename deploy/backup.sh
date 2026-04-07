#!/bin/bash
# deploy/backup.sh — Daily PostgreSQL backup with 7-day rotation
# Runs from cron: 0 2 * * * /usr/local/bin/renate-backup
set -euo pipefail

APP_DIR="/opt/renate-talent"
BACKUP_DIR="/opt/renate-backups"
DATE=$(date +%Y-%m-%d)
KEEP_DAYS=7

mkdir -p "$BACKUP_DIR"
cd "$APP_DIR"

# Dump database from the running container
echo "[$(date)] Starting backup..."
docker compose exec -T db pg_dump \
    -U "${POSTGRES_USER:-renate}" \
    "${POSTGRES_DB:-renate_talent}" \
    | gzip > "$BACKUP_DIR/db-$DATE.sql.gz"

echo "[$(date)] Backup saved: $BACKUP_DIR/db-$DATE.sql.gz ($(du -sh "$BACKUP_DIR/db-$DATE.sql.gz" | cut -f1))"

# Rotate — delete backups older than KEEP_DAYS
find "$BACKUP_DIR" -name "db-*.sql.gz" -mtime "+$KEEP_DAYS" -delete
echo "[$(date)] Rotated backups, keeping last $KEEP_DAYS days"

# Also backup the uploads volume (resumes)
UPLOAD_VOL=$(docker volume inspect renate-talent_uploads -f '{{.Mountpoint}}' 2>/dev/null || true)
if [ -n "$UPLOAD_VOL" ]; then
    tar -czf "$BACKUP_DIR/uploads-$DATE.tar.gz" -C "$UPLOAD_VOL" .
    find "$BACKUP_DIR" -name "uploads-*.tar.gz" -mtime "+$KEEP_DAYS" -delete
    echo "[$(date)] Uploads backed up"
fi

echo "[$(date)] Backup complete"
