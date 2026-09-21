#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
source .env

export AWS_DEFAULT_REGION=us-east-1
BUCKET="${BACKUP_BUCKET:-ops-baseline-backups-487054650859}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
FILE="/tmp/${DB_NAME}-${TS}.sql.gz"

docker compose exec -T db pg_dump -U "$DB_USER" --clean --if-exists "$DB_NAME" | gzip > "$FILE"

if [ ! -s "$FILE" ]; then
  echo "Backup file is empty, aborting" >&2
  exit 1
fi

aws s3 cp "$FILE" "s3://${BUCKET}/postgres/$(basename "$FILE")"
rm -f "$FILE"
echo "$(date -u +%FT%TZ) backup OK: postgres/$(basename "$FILE")"
