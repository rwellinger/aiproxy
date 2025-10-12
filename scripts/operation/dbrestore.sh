#!/usr/bin/env zsh

# -------------------------------------------------------------
# PostgreSQL Database Restore Script
# -------------------------------------------------------------
# Restores a gzipped schema dump to the PostgreSQL database.
# Usage: ./dbrestore.sh <path-to-backup-file.sql.gz>
# -------------------------------------------------------------

# -------------------------------------------------------------
# 1. Parameter-Validierung
# -------------------------------------------------------------
if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <backup-file.sql.gz>"
  echo "Example: $0 ~/backup/20251012_095621_aiproxysrv_schema.sql.gz"
  exit 1
fi

BACKUP_FILE="$1"
CONTAINER_NAME="postgres"

# -------------------------------------------------------------
# 2. Prüfen, ob Backup-File existiert
# -------------------------------------------------------------
if [[ ! -f "$BACKUP_FILE" ]]; then
  echo "Error: Backup file not found: $BACKUP_FILE"
  exit 1
fi

# Prüfen, ob File gzip-komprimiert ist
if [[ "$BACKUP_FILE" != *.sql.gz ]]; then
  echo "Warning: File does not have .sql.gz extension: $BACKUP_FILE"
  echo "Continuing anyway..."
fi

# -------------------------------------------------------------
# 3. .env laden
# -------------------------------------------------------------
if [[ ! -f .env ]]; then
  echo "Error: .env file not found in current directory."
  exit 1
fi

# Nur POSTGRES_* Variablen exportieren
grep '^POSTGRES_' .env |
while IFS= read -r line; do
  [[ -z "$line" || "$line" == \#* ]] && continue
  export "$line"
done

# Source .env um Variablen im aktuellen Shell zu haben
eval "$(grep '^POSTGRES_' .env | grep -v '^#')"

# Prüfen, ob benötigte Variablen gesetzt sind
: "${POSTGRES_USER:?POSTGRES_USER fehlt in .env}"
: "${POSTGRES_DB:?POSTGRES_DB fehlt in .env}"
: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD fehlt in .env}"

# -------------------------------------------------------------
# 4. Sicherheitsabfrage
# -------------------------------------------------------------
echo "=============================================="
echo "  DATABASE RESTORE - DESTRUCTIVE OPERATION"
echo "=============================================="
echo ""
echo "WARNING: This will DROP and recreate the database: $POSTGRES_DB"
echo "         ALL current database content will be LOST!"
echo ""
echo "Backup file: $BACKUP_FILE"
echo "Target database: $POSTGRES_DB"
echo "Target container: $CONTAINER_NAME"
echo ""
echo "NOTE: This script works with FULL backups (schema + data)."
echo "      Schema-only backups will restore structure but no data."
echo ""
read "CONFIRM?Type 'yes' to continue or 'no' to abort: "

if [[ "$CONFIRM" != "yes" ]]; then
  echo "Restore aborted."
  exit 0
fi

# -------------------------------------------------------------
# 5. Temporäres Entpacken
# -------------------------------------------------------------
TEMP_SQL="/tmp/restore_$$.sql"

echo "Decompressing backup file..."
gunzip -c "$BACKUP_FILE" > "$TEMP_SQL"

if [[ ! -f "$TEMP_SQL" ]]; then
  echo "Error: Failed to decompress backup file."
  exit 1
fi

# -------------------------------------------------------------
# 6. Database Drop & Recreate
# -------------------------------------------------------------
echo "Dropping existing database..."
docker exec -i "$CONTAINER_NAME" \
  psql -U "$POSTGRES_USER" -d postgres \
  -c "DROP DATABASE IF EXISTS \"$POSTGRES_DB\";" \
  2>&1

if [[ $? -ne 0 ]]; then
  echo "Error: Failed to drop database."
  rm -f "$TEMP_SQL"
  exit 1
fi

echo "Creating fresh database..."
docker exec -i "$CONTAINER_NAME" \
  psql -U "$POSTGRES_USER" -d postgres \
  -c "CREATE DATABASE \"$POSTGRES_DB\" OWNER \"$POSTGRES_USER\";" \
  2>&1

if [[ $? -ne 0 ]]; then
  echo "Error: Failed to create database."
  rm -f "$TEMP_SQL"
  exit 1
fi

# -------------------------------------------------------------
# 7. Restore SQL Dump
# -------------------------------------------------------------
echo "Restoring database schema..."
docker exec -i "$CONTAINER_NAME" \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
  < "$TEMP_SQL" \
  2>&1

if [[ $? -ne 0 ]]; then
  echo "Error: Failed to restore database."
  rm -f "$TEMP_SQL"
  exit 1
fi

# -------------------------------------------------------------
# 8. Cleanup
# -------------------------------------------------------------
rm -f "$TEMP_SQL"

# -------------------------------------------------------------
# 9. Erfolgsmeldung
# -------------------------------------------------------------
echo ""
echo "=============================================="
echo "  ✓ DATABASE RESTORE COMPLETED"
echo "=============================================="
echo ""
echo "Database: $POSTGRES_DB"
echo "Source: $BACKUP_FILE"
echo ""
echo "IMPORTANT: Verify that your data has been restored correctly."
echo "           Check your application to ensure all records are present."
echo ""
