#!/usr/bin/env zsh

# -------------------------------------------------------------
# PostgreSQL Full Database Backup Script
# -------------------------------------------------------------
# Creates a FULL backup (schema + data) of the PostgreSQL database.
# WARNING: This creates a complete dump including all table data.
# For schema-only backups, add the -s flag to pg_dump.
# -------------------------------------------------------------

# -------------------------------------------------------------
# 1. Konfiguration
# -------------------------------------------------------------
BACKUP_DIR="$HOME/backup"
CONTAINER_NAME="postgres"          # Name des laufenden Containers
DATESTAMP="$(date +%Y%m%d_%H%M%S)"

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
#  - Zeilen filtern
#  - Leere Zeilen / Kommentare überspringen
#  - Jede Zeile als Variable exportieren
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
: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD fehlt in .env}"

# -------------------------------------------------------------
# 5. Backup‑Verzeichnis anlegen
# -------------------------------------------------------------
mkdir -p "$BACKUP_DIR"

# -------------------------------------------------------------
# 6. Full Dump (Schema + Data) aus Container holen
# -------------------------------------------------------------
DUMP_FILE="$BACKUP_DIR/${DATESTAMP}_${POSTGRES_DB}_full.sql"

echo "Creating full database backup (schema + data)..."
docker exec "$CONTAINER_NAME" \
  pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
  > "$DUMP_FILE"

# -------------------------------------------------------------
# 7. Ergebnis melden
# -------------------------------------------------------------
if [[ -f "$DUMP_FILE" ]]; then
  echo "Full backup created: $DUMP_FILE"
  echo "Compressing backup..."
  gzip "$DUMP_FILE"
  echo ""
  echo "✓ Backup completed successfully!"
  echo "  File: ${DUMP_FILE}.gz"
  echo "  Type: FULL (schema + data)"
  echo ""
else
  echo "Dump fehlgeschlagen."
  exit 1
fi
