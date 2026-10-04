#!/usr/bin/env bash
# PostgreSQL Database Restore Script (Linux / macOS / WSL)
set -e

BACKUP_FILE=$1
if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: ./restore.sh <path_to_backup_file.sql>"
    exit 1
fi

CONTAINER_NAME=${CONTAINER_NAME:-"paint_postgres"}
DB_USER=${DB_USER:-"paint_user"}
DB_NAME=${DB_NAME:-"paint_db"}

echo "Restoring database '$DB_NAME' from '$BACKUP_FILE'..."
cat "$BACKUP_FILE" | docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME"

echo "Database restore completed successfully!"
