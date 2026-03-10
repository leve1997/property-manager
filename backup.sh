#!/bin/bash
# SQLite backup to DigitalOcean Spaces
# Runs Mon-Fri at 8PM CET (19:00 UTC)
# Cron:  0 19 * * 1-5 /var/www/property-manager/backup.sh >> /var/log/property-manager/backup.log 2>&1

set -e

# Load .env from the same directory as this script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
fi

# Validate required vars
: "${DB_PATH:?DB_PATH not set}"
: "${SPACES_KEY:?SPACES_KEY not set}"
: "${SPACES_SECRET:?SPACES_SECRET not set}"
: "${SPACES_REGION:?SPACES_REGION not set}"
: "${SPACES_BUCKET:?SPACES_BUCKET not set}"

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="/tmp/property-manager-backup-${TIMESTAMP}.db"
S3_ENDPOINT="https://${SPACES_REGION}.digitaloceanspaces.com"
S3_PATH="s3://${SPACES_BUCKET}/backups/property-manager-${TIMESTAMP}.db"

echo "[$(date)] Starting backup..."

# SQLite hot backup — safe to run while app is live (WAL mode)
sqlite3 "$DB_PATH" ".backup '$BACKUP_FILE'"

echo "[$(date)] DB snapshot created: $BACKUP_FILE"

# Upload to Spaces using s3cmd
s3cmd put "$BACKUP_FILE" "$S3_PATH" \
    --access_key="$SPACES_KEY" \
    --secret_key="$SPACES_SECRET" \
    --host="$S3_ENDPOINT" \
    --host-bucket="https://%(bucket)s.${SPACES_REGION}.digitaloceanspaces.com"

echo "[$(date)] Uploaded to $S3_PATH"

# Clean up local temp file
rm "$BACKUP_FILE"

# Delete backups older than 30 days from Spaces
CUTOFF=$(date -d "30 days ago" +"%Y-%m-%d" 2>/dev/null || date -v-30d +"%Y-%m-%d")
echo "[$(date)] Pruning backups older than $CUTOFF..."

s3cmd ls "s3://${SPACES_BUCKET}/backups/" \
    --access_key="$SPACES_KEY" \
    --secret_key="$SPACES_SECRET" \
    --host="$S3_ENDPOINT" \
    --host-bucket="https://%(bucket)s.${SPACES_REGION}.digitaloceanspaces.com" \
    | awk '{print $4}' \
    | while read -r FILE; do
        FILE_DATE=$(echo "$FILE" | grep -oP '\d{4}-\d{2}-\d{2}' | head -1)
        if [[ -n "$FILE_DATE" && "$FILE_DATE" < "$CUTOFF" ]]; then
            s3cmd del "$FILE" \
                --access_key="$SPACES_KEY" \
                --secret_key="$SPACES_SECRET" \
                --host="$S3_ENDPOINT" \
                --host-bucket="https://%(bucket)s.${SPACES_REGION}.digitaloceanspaces.com"
            echo "[$(date)] Deleted old backup: $FILE"
        fi
    done

echo "[$(date)] Backup complete."
