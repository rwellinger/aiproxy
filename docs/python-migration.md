# Python 3.11 → 3.12 Migration

**Projekt:** aiproxysrv
**Status:** Geplant
**Aufwand:** 2-3 Stunden
**Autor:** Rob
**Datum:** 2025-10-15

---

## Übersicht

### Warum Python 3.12?

**Performance-Verbesserungen:**
- 5-10% schnellere Ausführung durch optimierten Bytecode Compiler
- Bessere Memory-Effizienz bei großen Datenstrukturen
- Schnellere String-Operationen

**Neue Features:**
- Type Parameter Syntax (PEP 695): `def func[T](x: T)` statt `TypeVar`
- `@override` Decorator (PEP 698) für bessere Type Safety
- Verbesserte F-String Syntax mit geschachtelten Ausdrücken
- Buffer Protocol Improvements (PEP 688)

**Wartung & Security:**
- Aktive Sicherheitsupdates bis **Oktober 2028**
- Python 3.11 Support endet Oktober 2027
- Längerer Support-Lifecycle

**Tooling:**
- Bessere Ruff-Performance auf Python 3.12
- Präzisere Error Messages & Tracebacks
- Verbesserte Debugging-Tools

### Risiko-Bewertung

**Kompatibilität: ✅ SEHR GUT**

Alle Dependencies sind Python 3.12 kompatibel:

| Package | Version | Python 3.12 Support |
|---------|---------|---------------------|
| Flask | 3.1.2 | ✅ Ja (ab 3.0+) |
| SQLAlchemy | 2.0.44 | ✅ Ja (ab 2.0+) |
| Pydantic | 2.12.1 | ✅ Ja (ab 2.0+) |
| Celery | 5.5.3 | ✅ Ja (ab 5.3+) |
| Alembic | 1.17.0 | ✅ Ja |
| Redis | 6.4.0 | ✅ Ja |
| psycopg2-binary | 2.9.11 | ✅ Ja |
| Gunicorn | 23.0.0 | ✅ Ja |

**Code-Analyse:**
- Keine deprecated Features im Codebase
- Moderne Type Hints (`str | None` statt `Optional[str]`)
- Keine Breaking Changes erwartet
- Pydantic 2.x Validators vollständig kompatibel

**Hardware:**
- Apple Silicon (M4/M1) - Python 3.12 läuft **nativ auf ARM64**
- Docker Images (`python:3.12-slim`) - Multi-Arch Support ✅

### Aufwand-Schätzung

| Phase | Aufwand |
|-------|---------|
| Development Environment Setup | 30 Min |
| Testing & Validation | 1-2 Std |
| Docker Build & Registry Push | 30 Min |
| Production Deployment | 30 Min |
| **Gesamt** | **2-3 Std** |

---

## Voraussetzungen

### Vor der Migration prüfen

```bash
# 1. Aktuelle Python-Version
python3 --version  # Sollte: Python 3.11.x

# 2. Git Status (clean working directory)
git status

# 3. Docker läuft
docker info

# 4. Alle Tests grün
cd aiproxysrv
ruff check .
ruff format . --check

# 5. Backup der Production-Datenbank
# (siehe Backup-Prozedur in operations/)
```

### Benötigte Tools

- **Miniconda3** (für Conda Environment)
- **Docker/Colima** (für Container Builds)
- **Git** (für Version Control)
- **GitHub CLI** (`gh`) - Optional für Registry Auth

---

## Migration - Schritt für Schritt

### Phase 1: Development Environment (MacBook M4)

#### 1.1 Neues Conda Environment erstellen

```bash
# Altes Environment als Backup behalten
conda create -n mac_ki_service_py312 python=3.12 -y

# Aktivieren
conda activate mac_ki_service_py312

# Python-Version verifizieren
python --version  # Sollte: Python 3.12.x
```

#### 1.2 Dependencies installieren

```bash
cd /Users/robertw/Workspace/mac_ki_service/aiproxysrv

# Basis-Dependencies
pip install --upgrade pip
pip install -e .

# Dev-Dependencies (Ruff, Pre-commit)
pip install -e ".[dev]"

# Installations-Check
pip list | grep -E "Flask|SQLAlchemy|celery|pydantic"
```

#### 1.3 Ruff Konfiguration aktualisieren

```bash
# Datei: aiproxysrv/pyproject.toml
# Zeile 51 ändern:
# target-version = "py311" → target-version = "py312"
```

**Manuelle Änderung:**
```toml
[tool.ruff]
# Python version target
target-version = "py312"  # ← ÄNDERN
```

#### 1.4 Code-Qualität testen

```bash
cd aiproxysrv

# Linting
ruff check .

# Auto-Fix (falls nötig)
ruff check . --fix

# Formatierung
ruff format .

# Alle Checks grün? → Weiter zu 1.5
```

#### 1.5 Funktions-Tests

```bash
# PostgreSQL starten (Docker)
cd /Users/robertw/Workspace/mac_ki_service/aiproxysrv
docker compose up postgres -d

# Datenbank-Migrationen
cd src
alembic upgrade head
cd ..

# Dev-Server starten (PyCharm oder Terminal)
python src/server.py

# In anderem Terminal: Health-Check
curl http://localhost:5050/api/v1/health
# Erwartete Antwort: {"status": "healthy"}

# Celery Worker testen
python src/worker.py
# Worker sollte starten ohne Errors
```

#### 1.6 Integrations-Tests

```bash
# Image-Generation Test (mit aitestmock)
curl -X POST http://localhost:5050/api/images/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "0001", "model": "dall-e-3"}'

# Chat Test (Ollama - falls lokal läuft)
curl -X POST http://localhost:5050/api/chat/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.2:3b", "prompt": "Hello"}'

# Alle Tests erfolgreich? → Phase 2
```

---

### Phase 2: Docker Images (Build & Registry)

#### 2.1 Dockerfile aktualisieren

```bash
# Datei: aiproxysrv/Dockerfile
# Zeile 1 ändern:
# FROM python:3.11-slim AS base → FROM python:3.12-slim AS base
```

**Manuelle Änderung:**
```dockerfile
FROM python:3.12-slim AS base  # ← ÄNDERN
```

#### 2.2 Lokalen Test-Build

```bash
cd /Users/robertw/Workspace/mac_ki_service/aiproxysrv

# App-Image bauen
docker build -f Dockerfile --target app -t aiproxysrv-app:test .

# Worker-Image bauen
docker build -f Dockerfile --target worker -t celery-worker-app:test .

# Verifizieren
docker images | grep test
```

#### 2.3 Test-Container starten

```bash
# Test mit lokalem Image
docker run --rm -it \
  -e DATABASE_URL="postgresql://aiuser:password@host.docker.internal:5432/aiproxy" \
  -p 5050:5050 \
  aiproxysrv-app:test

# In anderem Terminal testen
curl http://localhost:5050/api/v1/health

# Container stoppen: Ctrl+C
```

#### 2.4 Version bumpen

```bash
# Neue Version festlegen (z.B. v2.2.0 für Python 3.12)
cd /Users/robertw/Workspace/mac_ki_service
./scripts/build/setVersion.sh 2.2.0

# Version in pyproject.toml prüfen
grep "^version" aiproxysrv/pyproject.toml
# Sollte: version = "2.2.0"
```

#### 2.5 Images bauen & pushen

```bash
cd /Users/robertw/Workspace/mac_ki_service

# Build & Push zu GitHub Container Registry
./scripts/build/build-and-push-aiproxysrv.sh v2.2.0

# Script baut:
# - ghcr.io/rwellinger/aiproxysrv-app:v2.2.0
# - ghcr.io/rwellinger/aiproxysrv-app:latest
# - ghcr.io/rwellinger/celery-worker-app:v2.2.0
# - ghcr.io/rwellinger/celery-worker-app:latest
```

**Authentifizierung (falls nötig):**
```bash
# GitHub Token generieren (Settings → Developer Settings → PAT)
echo $GITHUB_TOKEN | docker login ghcr.io -u rwellinger --password-stdin
```

#### 2.6 Registry verifizieren

```bash
# Images in Registry prüfen
docker manifest inspect ghcr.io/rwellinger/aiproxysrv-app:v2.2.0

# Erwartete Architekturen: linux/amd64, linux/arm64
```

---

### Phase 3: Production Deployment (Mac Studio M1)

#### 3.1 Git Commit & Push

```bash
cd /Users/robertw/Workspace/mac_ki_service

# Änderungen committen
git add aiproxysrv/Dockerfile aiproxysrv/pyproject.toml docs/python-migration.md
git commit -m "Migrate aiproxysrv to Python 3.12

- Update Dockerfile base image to python:3.12-slim
- Update Ruff target-version to py312
- Bump version to v2.2.0
- Add migration documentation

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin main
```

#### 3.2 Production Server: docker-compose.yml updaten

**Auf Mac Studio M1:**

```bash
# SSH zum Production Server (oder direkt am Mac Studio)
cd /path/to/mac_ki_service/aiproxysrv

# Backup der aktuellen docker-compose.yml
cp docker-compose.yml docker-compose.yml.backup

# docker-compose.yml editieren
# Zeilen 39 + 69: Image-Tags ändern
```

**Änderungen:**
```yaml
# Zeile 39 (Celery Worker)
image: ghcr.io/rwellinger/celery-worker-app:v2.2.0  # ← v2.1.16 → v2.2.0

# Zeile 69 (Aiproxy App)
image: ghcr.io/rwellinger/aiproxysrv-app:v2.2.0  # ← v2.1.16 → v2.2.0
```

#### 3.3 Rolling Update (Zero-Downtime)

```bash
cd /path/to/mac_ki_service/aiproxysrv

# Neue Images pullen
docker compose pull

# Services neu starten (einer nach dem anderen)
docker compose up -d celery-worker
docker compose up -d aiproxy-app

# Status prüfen
docker compose ps
docker compose logs -f --tail=50
```

#### 3.4 Health Checks

```bash
# App Health
curl http://localhost:5050/api/v1/health

# Celery Worker Status
docker compose exec celery-worker celery -A celery_app.celery_config:celery_app inspect ping

# PostgreSQL Connection
docker compose exec aiproxy-app python -c "from db.database import engine; print(engine.connect())"

# Logs auf Errors prüfen
docker compose logs --tail=100 | grep -i error
```

#### 3.5 Smoke Tests

```bash
# 1. Image-Generation testen
curl -X POST http://localhost:5050/api/images/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"prompt": "A sunset over mountains", "model": "dall-e-3"}'

# 2. Song-Generation testen (Async Job)
curl -X POST http://localhost:5050/api/songs/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"title": "Test Song", "lyrics": "Test lyrics..."}'

# 3. Chat testen
curl -X POST http://localhost:5050/api/chat/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-oss:20b", "prompt": "Hello World"}'

# 4. Account Status (Mureka API)
curl http://localhost:5050/api/account/status
```

#### 3.6 Monitoring (24h)

```bash
# Logs überwachen
docker compose logs -f

# Celery Tasks überwachen
# Flower UI: http://localhost:5555 (falls aktiviert)

# CPU/Memory Usage
docker stats

# Fehlerhafte Requests
docker compose logs | grep "500\|error\|exception" | tail -20
```

---

### Phase 4: Cleanup & Finalisierung

#### 4.1 Altes Conda Environment entfernen (Optional)

```bash
# Nach 1-2 Wochen erfolgreicher Production-Nutzung
conda env remove -n mac_ki_service

# Neues Environment als Standard setzen
conda activate mac_ki_service_py312

# In ~/.zshrc oder ~/.bashrc:
# conda activate mac_ki_service_py312
```

#### 4.2 Git Tag erstellen

```bash
git tag -a v2.2.0 -m "Python 3.12 Migration

- Migrated from Python 3.11 to 3.12
- Updated all Docker images
- Performance improvements: 5-10% faster
- Security: Extended support until Oct 2028"

git push origin v2.2.0
```

#### 4.3 Dokumentation updaten

```bash
# CLAUDE.md aktualisieren (falls Python-Version erwähnt)
# README.md aktualisieren (falls Python-Version dokumentiert)
# Deployment-Checkliste aktualisieren
```

---

## Testing-Checkliste

Nach jeder Phase durchführen:

### Development Tests

- [ ] `ruff check .` - Keine Errors
- [ ] `ruff format . --check` - Code formatiert
- [ ] `python src/server.py` - Server startet
- [ ] `python src/worker.py` - Worker startet
- [ ] `alembic upgrade head` - Migrations laufen
- [ ] Health Endpoint erreichbar (`/api/v1/health`)
- [ ] PostgreSQL Connection funktioniert
- [ ] Redis Connection funktioniert

### Integration Tests

- [ ] Image-Generation (OpenAI/aitestmock)
- [ ] Song-Generation (Mureka/aitestmock)
- [ ] Chat (Ollama/OpenAI)
- [ ] Prompt Templates CRUD
- [ ] User Authentication
- [ ] Celery Async Jobs
- [ ] File Downloads (FLAC/MP3/Stems)

### Docker Tests

- [ ] `docker build` erfolgreich (beide Targets)
- [ ] Container startet ohne Errors
- [ ] Health Checks grün
- [ ] Volumes gemountet
- [ ] Environment Variables gesetzt
- [ ] Netzwerk-Kommunikation (postgres/redis)

### Production Tests

- [ ] Services starten (`docker compose up -d`)
- [ ] Health Checks grün (alle Services)
- [ ] Keine Error-Logs
- [ ] API Endpoints erreichbar
- [ ] Frontend kann auf Backend zugreifen
- [ ] Celery Tasks werden verarbeitet
- [ ] 24h Monitoring unauffällig

---

## Rollback-Plan

Falls kritische Probleme auftreten:

### Development Rollback

```bash
# Zurück zu Python 3.11 Environment
conda activate mac_ki_service  # Altes Environment

# Dockerfile zurücksetzen
git checkout HEAD~1 -- aiproxysrv/Dockerfile aiproxysrv/pyproject.toml

# Server neu starten
python src/server.py
```

### Production Rollback

```bash
cd /path/to/mac_ki_service/aiproxysrv

# Alte docker-compose.yml wiederherstellen
cp docker-compose.yml.backup docker-compose.yml

# Alte Images verwenden
docker compose pull
docker compose up -d

# Health Check
curl http://localhost:5050/api/v1/health
```

### Registry Rollback

```bash
# Falls neue Images Probleme machen:
# docker-compose.yml auf vorherige Version setzen

services:
  celery-worker:
    image: ghcr.io/rwellinger/celery-worker-app:v2.1.16  # Alte Version

  aiproxy-app:
    image: ghcr.io/rwellinger/aiproxysrv-app:v2.1.16  # Alte Version
```

**Wichtig:** Alte Images bleiben im Registry verfügbar (solange nicht manuell gelöscht)!

---

## Troubleshooting

### Problem: Import-Fehler nach Migration

**Symptom:**
```
ModuleNotFoundError: No module named 'xyz'
```

**Lösung:**
```bash
# Dependencies neu installieren
pip install --upgrade pip
pip install -e ".[dev]" --force-reinstall
```

---

### Problem: Ruff findet neue Errors

**Symptom:**
```
error: F821 [*] Undefined name `TypeVar`
```

**Lösung:**
Python 3.12 bevorzugt neue Type Parameter Syntax. Optional modernisieren:

```python
# Alt (3.10+)
from typing import TypeVar
T = TypeVar('T')
def func(x: T) -> T: ...

# Neu (3.12+)
def func[T](x: T) -> T: ...
```

**Oder:** Alten Code behalten (funktioniert auch in 3.12).

---

### Problem: Docker Build schlägt fehl

**Symptom:**
```
failed to solve: python:3.12-slim: not found
```

**Lösung:**
```bash
# Docker Cache leeren
docker builder prune -af

# Erneuter Build
docker build --no-cache -f Dockerfile --target app -t test .
```

---

### Problem: Celery Worker startet nicht

**Symptom:**
```
[ERROR/MainProcess] consumer: Cannot connect to redis://redis:6379
```

**Lösung:**
```bash
# Redis Status prüfen
docker compose ps redis
docker compose logs redis

# Redis neu starten
docker compose restart redis

# Worker neu starten
docker compose restart celery-worker
```

---

### Problem: Performance schlechter als erwartet

**Symptom:**
Requests langsamer als mit Python 3.11.

**Lösung:**
```bash
# 1. Gunicorn Worker-Anzahl prüfen
docker compose exec aiproxy-app ps aux | grep gunicorn
# Sollte: 4 Worker (wie in Dockerfile CMD definiert)

# 2. CPU/Memory Usage
docker stats

# 3. Profiling aktivieren (temporär)
# In src/server.py: Flask Debug Mode für Profiling

# 4. Python 3.12 JIT testen (optional, experimentell)
# Umgebungsvariable: PYTHON_JIT=1
```

---

### Problem: Pydantic Validators funktionieren nicht

**Symptom:**
```
AttributeError: 'ChatRequest' object has no attribute 'validate_model'
```

**Lösung:**
Pydantic 2.x Syntax verwenden (bereits im Projekt):

```python
# Korrekt (Pydantic 2.x):
from pydantic import BaseModel, field_validator

class ChatRequest(BaseModel):
    @field_validator("model")
    def validate_model(cls, v):
        ...
```

---

## Cheat Sheet

### Conda Environments

```bash
# Liste aller Environments
conda env list

# Aktivieren
conda activate mac_ki_service_py312

# Deaktivieren
conda deactivate

# Löschen
conda env remove -n ENV_NAME
```

### Docker Commands

```bash
# Images neu bauen (ohne Cache)
docker compose build --no-cache

# Services neu starten
docker compose restart SERVICE_NAME

# Logs live verfolgen
docker compose logs -f --tail=100

# In Container-Shell
docker compose exec aiproxy-app bash

# Container-Status
docker compose ps
docker stats
```

### Ruff

```bash
# Check + Auto-Fix
ruff check . --fix

# Nur Check (kein Fix)
ruff check .

# Formatierung
ruff format .

# Spezifische Datei
ruff check src/api/routes/chat_routes.py
```

### Alembic

```bash
cd aiproxysrv/src

# Aktuelle DB-Version
alembic current

# Migrations anwenden
alembic upgrade head

# Migration erstellen
alembic revision --autogenerate -m "message"

# Zurück zu vorheriger Version
alembic downgrade -1
```

---

## Referenzen

- **Python 3.12 Release Notes:** https://docs.python.org/3.12/whatsnew/3.12.html
- **Pydantic 2.x Migration:** https://docs.pydantic.dev/latest/migration/
- **SQLAlchemy 2.0 Migration:** https://docs.sqlalchemy.org/en/20/changelog/migration_20.html
- **Docker Official Images:** https://hub.docker.com/_/python
- **Ruff Documentation:** https://docs.astral.sh/ruff/

---

## Changelog

| Datum | Version | Änderung |
|-------|---------|----------|
| 2025-10-15 | 1.0 | Initiale Dokumentation erstellt |

---

**Ende der Migrations-Dokumentation**
