#!/bin/sh
set -e

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/renate_talent_${TIMESTAMP}.sql.gz"
KEEP_DAYS=7

echo "[$(date)] Starting database backup..."

pg_dump --clean --if-exists --no-owner | gzip > "${BACKUP_FILE}"

echo "[$(date)] Backup created: ${BACKUP_FILE}"

# Remove backups older than KEEP_DAYS
find "${BACKUP_DIR}" -name "renate_talent_*.sql.gz" -mtime +${KEEP_DAYS} -delete

REMAINING=$(find "${BACKUP_DIR}" -name "renate_talent_*.sql.gz" | wc -l)
echo "[$(date)] Backup complete. ${REMAINING} backup(s) retained."
