#!/usr/bin/env bash
# AgriDecision AI - Disaster Recovery Database Restore Script
# Downloads specified database backup archive from AWS S3 and restores to target PostgreSQL instance.

set -euo pipefail

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <s3_backup_filename>"
    echo "Example: $0 agridecision_full_backup_20260726_120000.sql.gz"
    exit 1
fi

BACKUP_FILENAME="$1"
S3_BUCKET="s3://agridecision-production-db-backups/postgresql"
RESTORE_DIR="/tmp/pg_restore"

mkdir -p "${RESTORE_DIR}"

POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
PGPASSWORD="${POSTGRES_PASSWORD:-SecretPassword123}"
export PGPASSWORD

echo "[INFO] Downloading backup file from AWS S3: ${S3_BUCKET}/${BACKUP_FILENAME}..."
aws s3 cp "${S3_BUCKET}/${BACKUP_FILENAME}" "${RESTORE_DIR}/${BACKUP_FILENAME}"

echo "[INFO] Executing database restore onto ${POSTGRES_HOST}..."
gunzip -c "${RESTORE_DIR}/${BACKUP_FILENAME}" | psql -h "${POSTGRES_HOST}" -U "${POSTGRES_USER}"

rm -rf "${RESTORE_DIR}"
echo "[SUCCESS] Disaster Recovery Database Restoration Completed."
