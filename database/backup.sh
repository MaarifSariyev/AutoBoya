#!/usr/bin/env bash
# PostgreSQL Database Backup Script (Linux / macOS / WSL)
set -e

CONTAINER_NAME=${CONTAINER_NAME:-"paint_postgres"}
DB_USER=${DB_USER:-"paint_user"}
DB_NAME=${DB_NAME:-"paint_db"}
OUTPUT_DIR=${OUTPUT_DIR:-"./backups"}

mkdir -p "$OUTPUT_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="$OUTPUT_DIR/paint_db_backup_$TIMESTAMP.sql"

echo "Creating PostgreSQL backup for '$DB_NAME' from container '$CONTAINER_NAME'..."
docker exec -t "$CONTAINER_NAME" pg_dump -U "$DB_USER" "$DB_NAME" > "$OUTPUT_FILE"

echo "Backup completed successfully: $OUTPUT_FILE"
