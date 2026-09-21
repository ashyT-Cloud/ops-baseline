#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
source .env

export AWS_DEFAULT_REGION=us-east-1
BUCKET="${BACKUP_BUCKET:-ops-baseline-backups-487054650859}"
KEY="${1:-$(aws s3 ls "s3://${BUCKET}/postgres/" | sort | tail -n 1 | awk '{print $4}')}"
[ -n "$KEY" ] || { echo "No backup found" >&2; exit 1; }
KEY="${KEY#postgres/}"

echo "Restoring postgres/${KEY} ..."
aws s3 cp "s3://${BUCKET}/postgres/${KEY}" - | gunzip | docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1
echo "Restore complete"
