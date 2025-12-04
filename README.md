# thWelly's AI Toolbox

<img src="thwellysAIToolbar.jpg" alt="thWelly's AI Toolbox" width="1024" height="578">

A full-stack platform for AI-powered image and music generation with Python backend (FastAPI) and Angular 20 frontend.

---

## 📁 Repository Structure

**IMPORTANT:** This project is split into two separate repositories:

### 1. **mac_ki_service/** - DEVELOPMENT (this repository)
- **Location:** `/Users/robertw/Workspace/mac_ki_service`
- **Purpose:** Source code, builds, CI/CD, development
- **Contains:** Python/TypeScript/SCSS code, tests, build configs
- **Git:** Active development, commits allowed
- ✅ **Edit code here**

### 2. **thwelly_ki_app/** - PRODUCTION
- **Location:** `/Users/robertw/Workspace/thwelly_ki_app`
- **Purpose:** Production deployment configuration ONLY
- **Contains:** docker-compose.yml, .env (secrets), runtime scripts, data volumes
- **Git:** Separate repository, minimal commits
- ⚠️ **NO source code editing! Only configs/secrets**
- ⚠️ **FINGER WEG VON CODE - Deployment only!**

**Workflow:**
1. **DEV (mac_ki_service):** Code → Commit → CI builds Images → ghcr.io
2. **PROD (thwelly_ki_app):** Update docker-compose.yml versions → `docker compose pull && up -d`

---

## 🎯 Features

- **AI Chat Conversations** - Interactive chat with Ollama LLMs (llama3.2:3b, gpt-oss:20b and others)
  - Integrated chat UI replacing Open WebUI (now part of thWelly Toolbox)
  - Multi-conversation management with persistent history
  - Configurable system context for AI behavior customization
  - Token usage tracking with context window visualization
  - Message formatting with markdown support
- **Lyric Creation Editor** - Professional songwriting tool with AI assistance
  - Interactive section-based editor (Verse, Chorus, Bridge, etc.)
  - Song architecture builder with drag & drop reordering
  - AI-powered lyric improvement, rewriting, and extension
  - Text tools: cleanup, structure application, undo functionality
  - Character counter and section navigation
  - Auto-save integration with song generator
  - **Configurable Lyric Parsing Rules** - Regex-based cleanup and section detection
    - Cleanup rules: Line breaks, smart quotes, trailing spaces, em dashes, etc.
    - Section detection: Markdown-style labels (**Intro**, **Verse1**, **Chorus**, etc.)
    - Database-driven configuration with execution order control
- **Song Sketch Library** - Organize and develop song ideas before generation
  - Create and manage song sketches (title, lyrics, music style prompt, tags)
  - Workflow management (draft, used, archived)
  - Master-detail view with search and filtering
  - AI-powered title generation
  - Direct integration with Song Generator and Lyric Creator
  - Convert sketches to full songs with one click
- **Equipment Management** - Organize music production software and plugins
  - Master-detail gallery with search and filtering
  - Track software licenses (online, iLok, license keys)
  - Secure credential storage (encrypted passwords and license keys)
  - Status tracking (active, trial, expired, archived)
  - Purchase tracking with price and date
  - Duplicate equipment entries for quick setup
  - Tagging system for organization (software/plugin tags)
- **Image Generation** via DALL·E 3 (OpenAI)
  - Fast Enhancement Mode: One-click AI-powered prompt optimization
  - Gallery view with filtering, search, and sorting
  - Detail panel with metadata (original/enhanced/revised prompts)
  - Download and delete functionality
  - Master-detail layout with responsive design
  - **Text Overlay Editor** - Add customizable text to generated images
    - Real-time canvas preview with position markers
    - Title and optional artist text (auto-uppercase)
    - Three font styles: Bold (Anton), Elegant (Playfair Display), Light (Roboto)
    - Advanced positioning: 3x3 grid or custom pixel coordinates
    - Independent color and outline controls for title and artist
    - Composition-based sorting (e.g., album-cover images prioritized)
    - Non-destructive editing: Creates new image records
  - **Usage Cost Tracking** - Real-time OpenAI API cost monitoring
    - TTL-based caching (1h for current month, forever for history)
    - Cost breakdown by model (DALL-E, GPT)
    - Monthly and all-time aggregation
    - Displayed in User Profile
- **Song Generation** via Mureka API (asynchronous with Celery)
- **Song Projects** - Complete project management for music production workflows
  - Hierarchical folder structure (Arrangement, Mixing, Mastering, Stems, References, etc.)
  - S3 cloud storage with batch upload/download
  - File management: Upload, download, delete, mirror sync
  - Asset assignment: Link songs, sketches, and images to project folders
  - Project metadata: Tags, descriptions, cover images, sync status
  - CLI integration for local workflow (clone, mirror, batch operations)
- **PostgreSQL** database for persistent storage
- **Angular 20** frontend with Material Design
- **Redis & Celery** for asynchronous task processing

---

## 📋 System Requirements

- **macOS** (Apple Silicon - M1/M4)
- **Python 3.12+** (with Miniconda3, current: 3.12.12)
- **Node.js & npm** (for Angular 20)
- **Docker** (via Colima for macOS)
- **Git**

---

## Build Status

[![Build Status](https://github.com/rwellinger/thwelly_ai_tools/actions/workflows/release.yml/badge.svg)](https://github.com/rwellinger/thwelly_ai_tools/actions)

- **CI/CD:** GitHub Actions
- **Build Server:** GitHub Hosted Runners
- **Registry:** GitHub Container Registry (GHCR)
- **Architecture:** ARM64 (linux/arm64)

---


## 🔧 Development Workflow

### Start Backend (Development)

```bash
# Terminal 1: Activate Conda environment
conda activate mac_ki_service
cd aiproxysrv

# Development server
python src/server.py
# Running on http://localhost:5050

# Terminal 2: Celery Worker (for song generation)
python src/worker.py
```

### Start Frontend (Development)

```bash
cd aiwebui

# Development server
npm run dev
# Running on http://localhost:4200
```

### Production Build

```bash
# Build frontend
cd aiwebui
npm run build:prod

# Output in: forwardproxy/html/aiwebui/
```

---

## 🚀 Release Management

### Creating a New Release

The release process is automated with scripts that handle versioning, git tagging, and Docker image builds.

#### 1. Create Release (Version + Git Tag)

```bash
# Creates VERSION files, commits, tags, and pushes
./scripts/build/create_release.sh v2.1.6
```

**What this does:**
- ✅ Validates version format (`vX.Y.Z`)
- ✅ Checks git status (clean tree, no unpushed commits)
- ✅ Updates `aiproxysrv/VERSION` and `aiwebui/VERSION`
- ✅ Commits: `"Bump version to vX.Y.Z"`
- ✅ Creates git tag with message
- ✅ Pushes commit and tag to remote

#### 2. Automated Build via GitHub Actions

After pushing the tag, **GitHub Actions automatically builds and pushes** Docker images:

**Workflow:** `.github/workflows/release.yml`

**What happens automatically:**
- ✅ GitHub Actions triggered by tag push
- ✅ Builds 3 Docker images in parallel:
  - `ghcr.io/rwellinger/aiproxysrv-app` (Backend API)
  - `ghcr.io/rwellinger/celery-worker-app` (Async Worker)
  - `ghcr.io/rwellinger/aiwebui-app` (Frontend)
- ✅ Tags: `vX.Y.Z` + `latest`
- ✅ Pushes to GitHub Container Registry (GHCR)
- ✅ ~10-12 minutes build time

**Monitor build status:**
```bash
# Via GitHub UI
https://github.com/rwellinger/thwelly_ai_tools/actions

# Via gh CLI
gh run watch --repo rwellinger/thwelly_ai_tools
```

#### 3. Re-run Failed Builds

If a specific job fails (e.g., frontend build error), you can re-run only that job:

**GitHub UI:**
1. Go to: https://github.com/rwellinger/thwelly_ai_tools/actions
2. Click on the failed run (e.g., "Build & Release #42")
3. You'll see 4 jobs:
   ```
   ✅ build-backend      (aiproxysrv-app)
   ✅ build-worker       (celery-worker-app)
   ❌ build-frontend     (aiwebui-app)        ← Failed!
   ✅ lint-frontend
   ```
4. Click on the failed job (e.g., `build-frontend`)
5. Click **"Re-run job"** (top right)
6. Only that job will rebuild (~5-6 minutes)

**GitHub CLI:**
```bash
# Find the run ID
gh run list --repo rwellinger/thwelly_ai_tools

# Re-run only the failed job
gh run rerun <RUN_ID> --job build-frontend --repo rwellinger/thwelly_ai_tools

# Or re-run all jobs
gh run rerun <RUN_ID> --repo rwellinger/thwelly_ai_tools
```

**Build Jobs:**
- `build-backend` - Backend API (~4-5 min)
- `build-worker` - Celery Worker (~3-4 min)
- `build-frontend` - Angular UI (~5-6 min)
- `lint-frontend` - ESLint check (~1-2 min)

All jobs run in **parallel**. Total time = longest job (~5-6 min).

#### Optional: Manual Build (Fallback)

If GitHub Actions is unavailable, use manual scripts:

```bash
# Build and push backend images (aiproxysrv-app + celery-worker-app)
./scripts/build/build-and-push-aiproxysrv.sh

# Build and push frontend image (aiwebui-app)
./scripts/build/build-and-push-aiwebui.sh

# Force push (skip confirmation)
./scripts/build/build-and-push-aiproxysrv.sh --force
./scripts/build/build-and-push-aiwebui.sh --force
```

### Cleanup Scripts

```bash
# Clean up old git tags
./scripts/build/cleanup-tags.sh

# Clean up old git branches
./scripts/build/cleanup-branchs.sh

# Clean up old Docker images
./scripts/build/cleanup-docker-images.sh

# General git cleanup
./scripts/build/gitcleanup.sh
```

---

## 🗂️ Project Structure

```
mac_ki_service/
├── aiproxysrv/          # Python Backend (FastAPI)
│   ├── src/
│   │   ├── adapters/    # External API Clients (Adapter Pattern)
│   │   │   ├── mureka/        # Mureka API integration
│   │   │   ├── ollama/        # Ollama API integration
│   │   │   └── openai/        # OpenAI API integration
│   │   ├── api/         # API Layer (HTTP & Routing)
│   │   │   ├── controllers/   # HTTP Layer + Pydantic Schemas
│   │   │   └── routes/        # API Endpoints
│   │   ├── business/    # Core Business Logic (3-Layer Architecture)
│   │   │   ├── *_orchestrator.py    # Coordination layer
│   │   │   ├── *_transformer.py     # Pure functions (testable)
│   │   │   ├── *_normalizer.py      # Pure functions (testable)
│   │   │   └── *_service.py         # Pure functions (testable)
│   │   ├── db/          # Repository Layer (CRUD only)
│   │   │   ├── models.py            # SQLAlchemy models
│   │   │   └── *_service.py         # CRUD operations
│   │   ├── schemas/     # Pydantic Data Schemas
│   │   ├── celery_app/  # Async Processing (Mureka)
│   │   ├── config/      # Configuration (reads .env)
│   │   ├── utils/       # Utility Functions
│   │   ├── alembic/     # DB Migrations
│   │   ├── server.py    # Dev server
│   │   ├── worker.py    # Celery worker
│   │   └── wsgi.py      # Prod entry (Gunicorn)
│   ├── docker-compose.yml
│   ├── env_template
│   ├── VERSION          # Version file for releases
│   └── pyproject.toml
│
├── aiwebui/             # Angular 20 Frontend
│   ├── src/app/
│   │   ├── pages/       # Feature pages (17)
│   │   │   ├── ai-chat/               # AI Chat conversations
│   │   │   ├── openai-chat/           # OpenAI GPT chat
│   │   │   ├── lyric-creation/        # Lyric editor with AI tools
│   │   │   ├── lyric-parsing-rules/   # Regex-based lyric cleanup
│   │   │   ├── song-sketch-creator/   # Create/edit song sketches
│   │   │   ├── song-sketch-library/   # Manage song sketches
│   │   │   ├── equipment-gallery/     # Equipment master-detail gallery
│   │   │   ├── equipment-editor/      # Equipment create/edit/duplicate
│   │   │   ├── image-generator/       # Image generation with fast enhancement
│   │   │   ├── image-view/            # Image gallery with master-detail view
│   │   │   ├── text-overlay-editor/   # Add text overlays to images
│   │   │   ├── song-generator/        # Song generation UI
│   │   │   ├── song-view/             # Display of generated songs
│   │   │   ├── song-profile/          # Mureka account information
│   │   │   ├── song-projects/         # Song project management (master-detail)
│   │   │   ├── user-profile/          # User profile and settings
│   │   │   ├── music-style-prompt/    # Music style template management
│   │   │   └── prompt-templates/      # Template management for prompts
│   │   ├── services/    # API Services & Business Logic
│   │   │   ├── business/      # ImageService, ConversationService, SketchService,
│   │   │   │                  # SongService, EquipmentService, SongProjectService
│   │   │   ├── config/        # ChatService, ApiConfigService
│   │   │   └── ui/            # ProgressService, NotificationService
│   │   ├── components/  # Shared components
│   │   │   ├── image-detail-panel/    # Image detail view component
│   │   │   ├── song-detail-panel/     # Song detail view component
│   │   │   ├── lyric-architect-modal/ # Song architecture builder
│   │   │   └── ...
│   │   └── models/      # TypeScript interfaces
│   │       ├── conversation.model.ts
│   │       ├── equipment.model.ts
│   │       ├── image-generation.model.ts
│   │       ├── lyric-architecture.model.ts
│   │       ├── song-project.model.ts
│   │       └── ...
│   ├── package.json
│   └── VERSION          # Version file for releases
│
├── scripts/
│   ├── build/           # Release & Build automation
│   │   ├── create_release.sh           # Create versioned release
│   │   ├── build-and-push-aiproxysrv.sh
│   │   ├── build-and-push-aiwebui.sh
│   │   ├── cleanup-docker-images.sh
│   │   ├── cleanup-tags.sh
│   │   ├── cleanup-branchs.sh
│   │   └── gitcleanup.sh
│   ├── cli/             # CLI Tool
│   │   ├── aiproxy-cli.py          # Main CLI script (1177 lines)
│   │   ├── README.md               # CLI user documentation
│   │   ├── requirements.txt        # Python dependencies (Click, rich, requests)
│   │   └── .aiproxyignore.default  # Default ignore patterns
│   └── db/              # Database seeding (SQL-based)
│       ├── seed_prompts.sql
│       └── seed_lyric_parsing_rules.sql
│
├── forwardproxy/        # Nginx reverse proxy (Production)
│   ├── html/           # Angular build output
│   └── nginx/          # Nginx config
│
├── aitestmock/          # Mock API (Testing)
├── docs/                # Documentation (arc42, patterns, troubleshooting)
└── develop-env/         # Development Docker setup
    └── docker-compose.yml
```

---

## 🛠️ Important Commands

### Release Management

```bash
# Create new release (version + git tag)
./scripts/build/create_release.sh v2.1.6

# Build and push Docker images
./scripts/build/build-and-push-aiproxysrv.sh    # Backend + Worker
./scripts/build/build-and-push-aiwebui.sh       # Frontend

# Force push (skip confirmation)
./scripts/build/build-and-push-aiproxysrv.sh --force
./scripts/build/build-and-push-aiwebui.sh --force

# Cleanup
./scripts/build/cleanup-docker-images.sh
./scripts/build/cleanup-tags.sh
./scripts/build/cleanup-branchs.sh
```

### Backend

```bash
# Development server
python src/server.py

# Celery worker
python src/worker.py

# Database migrations
cd src && alembic upgrade head
cd src && alembic revision --autogenerate -m "description"

# Database seeding (SQL-based, Docker-friendly)
# From project root (mac_ki_service/)
cat scripts/db/seed_prompts.sql | docker exec -i mac_ki_service-postgres-1 psql -U aiuser -d aiproxy
cat scripts/db/seed_lyric_parsing_rules.sql | docker exec -i mac_ki_service-postgres-1 psql -U aiuser -d aiproxy

# Or local PostgreSQL (without Docker)
psql -h localhost -U aiuser -d aiproxy -f scripts/db/seed_prompts.sql
psql -h localhost -U aiuser -d aiproxy -f scripts/db/seed_lyric_parsing_rules.sql

# Code Quality & Linting (Ruff)
ruff check .                   # Run linter
ruff check . --fix             # Auto-fix issues
ruff format .                  # Format code

# Logging (CRITICAL!)
# ALWAYS use: from utils.logger import logger
# NEVER use:  import logging
# Standard Python logger crashes with structured parameters: logger.info("msg", param=value)
# See CLAUDE.md for complete logging guidelines

# Unit Testing (pytest)
pytest                         # Run all tests
pytest -v -s                   # Verbose output with print statements
pytest tests/test_health.py    # Run specific test file
pytest -k "test_name"          # Run tests matching pattern
pytest --cov=src               # Run with coverage report

# Docker (Production)
cd aiproxysrv
docker compose up -d
docker compose logs -f
```

### Frontend

```bash
# Development
npm run dev

# Production build
npm run build:prod

# Linting
npm run lint
npm run lint:fix

# Tests
npm run test
```

---

## 🔐 API Keys & Security

### Required API Keys

1. **OpenAI (DALL·E 3)**
   - https://platform.openai.com/api-keys
   - Cost: ~$0.040-0.080 per image

2. **Mureka (Song Generation)**
   - https://mureka.ai/
   - Cost: Credit-based

3. **JWT Secret**
   ```bash
   openssl rand -base64 32
   ```

> ⚠️ **Important!**
> - Never commit `.env` files to the repository
> - Keep API keys secure
> - In production: Use strong passwords
> - Rotate JWT_SECRET_KEY regularly

---

## 🧪 Testing

### Mock API (aitestmock)

For testing without API costs:

```bash
cd aitestmock
python mock_server.py
# Running on http://localhost:3080
```

**Test scenarios:**
- Image: `prompt="0001"` → Success
- Image: `prompt="0002"` → Error (invalid token)
- Song: `prompt="0001"` → Success
- Song: `prompt="0002"` → Error (invalid token)
- Song: `prompt="30s"` → 30s duration test

---

## 🐛 Troubleshooting

### Docker Issues

```bash
# Check ports
lsof -i :5050  # Backend
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# Docker cleanup
docker system prune -f
docker volume prune -f
```

### Database Connection

```bash
# PostgreSQL status
docker compose ps postgres
docker compose logs postgres

# Connect manually
docker exec -it postgres psql -U aiproxy -d aiproxysrv

# Migration status
alembic current
alembic history
```

### Celery Worker

```bash
# Worker status
celery -A worker inspect active

# Restart worker
pkill -f "celery worker"
python src/worker.py
```

---

## 📚 Architecture

### Backend (aiproxysrv)
- **Framework**: FastAPI (Flask compatibility)
- **Database**: PostgreSQL + SQLAlchemy ORM
- **Async Tasks**: Celery + Redis
- **Migrations**: Alembic

### Frontend (aiwebui)
- **Framework**: Angular 20
- **UI**: Angular Material
- **Styling**: SCSS
- **State**: RxJS

### Production
- **Reverse Proxy**: Nginx
- **Container**: Docker + Colima
- **Orchestration**: Docker Compose

---

## 🖥️ CLI Tool (aiproxy-cli)

**AiProxy CLI** - Command-line tool for managing song projects, uploading files, and syncing with the backend.

### Installation

```bash
# Via Makefile (recommended)
make install-cli              # Install CLI without config
make install-cli-dev          # Install + DEV config (localhost:5050)
make install-cli-prod         # Install + PROD config (macstudio)

# Manual installation
mkdir -p ~/bin
cp scripts/cli/aiproxy-cli.py ~/bin/aiproxy-cli
chmod +x ~/bin/aiproxy-cli
pip install -r scripts/cli/requirements.txt

# Add to PATH (in ~/.zshrc or ~/.bashrc)
export PATH="$HOME/bin:$PATH"
```

### Commands

#### 1. `login` - Authenticate with JWT Token

```bash
aiproxy-cli login [--api-url URL]

# Interactive: Enter email + password
# Stores JWT token in ~/.aiproxy/config.json (0600 permissions)
```

#### 2. `upload` - Upload Files to Project Folder

```bash
aiproxy-cli upload <PROJECT_ID> <FOLDER_ID> [LOCAL_PATH] [--debug]

# Examples:
aiproxy-cli upload 550e8400-... 01-arrangement ~/Music/songs/
aiproxy-cli upload proj-id folder-id . --debug  # Current dir with debug

# Features:
# - Recursive directory scan
# - .aiproxyignore pattern support (global + local)
# - Batch upload (3 files/batch, max 500MB)
# - Progress bar with percentage
# - Preserves directory structure
```

#### 3. `download` - Download Folder Files

```bash
aiproxy-cli download <PROJECT_ID> <FOLDER_ID> [LOCAL_PATH]

# Example:
aiproxy-cli download 550e8400-... 01-arrangement ~/Downloads/

# Features:
# - Reconstructs directory structure (without folder prefix)
# - Streaming download (8KB chunks)
# - Progress bar
```

#### 4. `clone` - Clone Complete Project

```bash
aiproxy-cli clone <PROJECT_ID> [LOCAL_PATH] [-d/--create-dir]

# Examples:
aiproxy-cli clone 550e8400-... ~/Projects/
aiproxy-cli clone proj-id . -d  # Creates subdirectory with project name

# Features:
# - Clones ALL folders + files (including empty folders)
# - Preserves complete S3 directory structure
# - 1:1 replication of project structure
# - Use case: "Create in Web UI → Clone → Ready to work!"
```

#### 5. `mirror` - One-Way Sync (Local → Remote)

```bash
aiproxy-cli mirror <PROJECT_ID> <FOLDER_ID> <LOCAL_PATH> [OPTIONS]

# Options:
#   --dry-run    Preview changes without executing
#   --yes        Skip confirmation (for automation)
#   --debug      Show request/response details

# Examples:
aiproxy-cli mirror proj-id folder-id ~/Music/ --dry-run  # Preview
aiproxy-cli mirror proj-id folder-id ~/Music/ --yes      # Auto-confirm

# Features:
# - SHA256 hash-based comparison
# - Three operations: Upload (new), Update (changed), Delete (remote-only)
# - .aiproxyignore support
# - Interactive confirmation (shows files to delete!)
# - Batch upload + batch delete
```

### .aiproxyignore Patterns

**Global:** `~/.aiproxy/.aiproxyignore`
**Local:** `{upload_dir}/.aiproxyignore` (higher priority)

**Syntax (gitignore-style):**
```
.DS_Store          # Exact match
Icon*              # Wildcard
*.tmp              # File extension
.git/              # Directories (ends with /)
node_modules/
__pycache__/
*.log
```

### Configuration

**File:** `~/.aiproxy/config.json` (0600 permissions)

```json
{
  "api_url": "https://macstudio/aiproxysrv",
  "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "email": "user@example.com",
  "expires_at": "2024-11-03T10:30:00Z",
  "ssl_verify": false
}
```

### Workflow Example

```bash
# 1. Login
aiproxy-cli login

# 2. Clone project from Web UI
aiproxy-cli clone 550e8400-e29b-41d4-a716-446655440000 ~/Projects/ -d
# → Creates ~/Projects/My Song Project/

# 3. Work locally (edit files, add stems, mix, etc.)
# [edit files in ~/Projects/My Song Project/]

# 4. Preview sync changes
aiproxy-cli mirror proj-id 01-arrangement ~/Projects/"My Song Project"/01-arrangement --dry-run

# 5. Sync with server (upload new, update changed, delete remote-only)
aiproxy-cli mirror proj-id 01-arrangement ~/Projects/"My Song Project"/01-arrangement --yes
```

### Technical Details

- **Technology:** Python Click 8.1.0+ CLI framework
- **HTTP Client:** requests 2.31.0+ with SSL self-signed cert support
- **Terminal UI:** rich 13.7.0+ for progress bars and formatting
- **Batch Size:** 3 files per upload (max 500MB Nginx limit)
- **Timeout:** 10 minutes per batch/download
- **Hash Algorithm:** SHA256 for mirror comparison
- **File Permissions:** Config file secured with 0600 (owner-only)

### Security Notes

⚠️ **JWT Token Storage:**
- Token stored in plaintext in `~/.aiproxy/config.json`
- File permissions: 0600 (owner read/write only)
- **NOT** for use on multi-user systems
- **DO NOT** sync `~/.aiproxy/` with cloud services (Dropbox, iCloud)
- Token expiry: 24 hours (re-login required)

### API Endpoints Used

| Command | Backend Endpoint |
|---------|-----------------|
| `login` | `POST /api/v1/user/login` |
| `upload` | `POST /api/v1/song-projects/{id}/folders/{folder_id}/batch-upload` |
| `download` | `GET /api/v1/song-projects/{id}/folders/{folder_id}/files` |
| `clone` | `GET /api/v1/song-projects/{id}/files/all` |
| `mirror` | `POST /api/v1/song-projects/{id}/folders/{folder_id}/mirror`<br>`DELETE /api/v1/song-projects/{id}/files/batch-delete` |

**Documentation:** `scripts/cli/README.md`

---

## 🤝 Contributing

For questions or issues:
1. Create an issue
2. Create a branch: `feature/xyz` or `fix/xyz`
3. Pull request against `main`

---

## 📄 License

Private project - All rights reserved

---

## ⚙️ Environment Variables

Complete list in `aiproxysrv/env_template`:

| Variable | Description | Example |
|----------|-------------|---------|
| `JWT_SECRET_KEY` | JWT Token Secret | `openssl rand -base64 32` |
| `OPENAI_API_KEY` | OpenAI API Key | `sk-...` |
| `MUREKA_API_KEY` | Mureka API Key | `mk_...` |
| `DATABASE_URL` | PostgreSQL Connection | `postgresql://user:pass@localhost:5432/db` |
| `REDIS_URL` | Redis Connection | `redis://localhost:6379` |
| `DEBUG` | Debug Mode | `true` / `false` |

---

## 📞 Support

- **Docs**: See `./docs/README.md` for detailed developer documentation
- **Issues**: GitHub Issues
- **Email**: rob.wellinger@gmail.com

