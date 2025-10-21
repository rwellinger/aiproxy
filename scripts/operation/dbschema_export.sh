#!/usr/bin/env zsh

# -------------------------------------------------------------
# PostgreSQL Schema Export Script
# -------------------------------------------------------------
# Creates a SCHEMA-ONLY export (no data) of the PostgreSQL database.
# Useful for comparing DB schema with SQLAlchemy models.
# -------------------------------------------------------------

# -------------------------------------------------------------
# 1. Konfiguration
# -------------------------------------------------------------
BACKUP_DIR="$HOME/backup"
CONTAINER_NAME="postgres"          # Name des laufenden Containers
DATESTAMP="$(date +%Y%m%d_%H%M%S)"

# Parse options
OUTPUT_TO_STDOUT=false
while getopts "s" opt; do
  case $opt in
    s) OUTPUT_TO_STDOUT=true ;;
    *) echo "Usage: $0 [-s]  (-s for stdout output)"; exit 1 ;;
  esac
done

# -------------------------------------------------------------
# 2. Sicherstellen, dass .env existiert
# -------------------------------------------------------------
if [[ ! -f .env ]]; then
  echo ".env file not found in current directory."
  exit 1
fi

# -------------------------------------------------------------
# 3. Nur POSTGRES_*‑Variablen exportieren
# -------------------------------------------------------------
grep '^POSTGRES_' .env |
while IFS= read -r line; do
  [[ -z "$line" || "$line" == \#* ]] && continue
  export "$line"
done

# -------------------------------------------------------------
# 4. Prüfen, ob benötigte Variablen gesetzt sind
# -------------------------------------------------------------
: "${POSTGRES_USER:?POSTGRES_USER fehlt in .env}"
: "${POSTGRES_DB:?POSTGRES_DB fehlt in .env}"

# -------------------------------------------------------------
# 5. Schema Export
# -------------------------------------------------------------
if [[ "$OUTPUT_TO_STDOUT" == true ]]; then
  # Direkt nach stdout (für Claude-Analyse)
  docker exec "$CONTAINER_NAME" \
    pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --schema-only
else
  # In Datei schreiben
  mkdir -p "$BACKUP_DIR"
  SCHEMA_FILE="$BACKUP_DIR/${DATESTAMP}_${POSTGRES_DB}_schema.sql"

  echo "Exporting database schema (tables, indexes, constraints)..."
  docker exec "$CONTAINER_NAME" \
    pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --schema-only \
    > "$SCHEMA_FILE"

  # -------------------------------------------------------------
  # 6. Ergebnis melden
  # -------------------------------------------------------------
  if [[ -f "$SCHEMA_FILE" ]]; then
    echo ""
    echo "✓ Schema export completed successfully!"
    echo "  File: $SCHEMA_FILE"
    echo "  Type: SCHEMA ONLY (no data)"
    echo "  Size: $(du -h "$SCHEMA_FILE" | cut -f1)"
    echo ""
    echo "To view schema: cat $SCHEMA_FILE"
    echo "To compare with models: diff $SCHEMA_FILE <expected_schema>"
  else
    echo "Schema export failed."
    exit 1
  fi
fi
