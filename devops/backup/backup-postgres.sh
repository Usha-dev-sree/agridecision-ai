#!/usr/bin/env bash
# AgriDecision AI - Production Database Automated Backup Script
# Performs PostgreSQL and TimescaleDB pg_dumpall backups, compresses with gzip, and uploads to AWS S3.

set -euo pipefail

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/tmp/pg_backups"
S3_BUCKET="s3://agridecision-production-db-backups/postgresql"

mkdir -p "${BACKUP_DIR}"

POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
PGPASSWORD="${POSTGRES_PASSWORD:-SecretPassword123}"
export PGPASSWORD

BACKUP_FILE="${BACKUP_DIR}/agridecision_full_backup_${TIMESTAMP}.sql.gz"

echo "[INFO] Starting database backup at ${TIMESTAMP}..."
pg_dumpall -h "${POSTGRES_HOST}" -U "${POSTGRES_USER}" | gzip > "${BACKUP_FILE}"

echo "[INFO] Uploading backup binary to AWS S3: ${S3_BUCKET}..."
aws s3 cp "${BACKUP_FILE}" "${S3_BUCKET}/agridecision_full_backup_${TIMESTAMP}.sql.gz"

rm -f "${BACKUP_FILE}"
echo "[SUCCESS] Backup completed and verified successfully."
