# thWelly's AI Toolbox

<img src="thwellysAIToolbar.jpg" alt="thWelly's AI Toolbox" width="1024" height="578">

A full-stack platform for AI-powered image and music generation with Python backend (FastAPI) and Angular 18 frontend.

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
- **PostgreSQL** database for persistent storage
- **Angular 18** frontend with Material Design
- **Redis & Celery** for asynchronous task processing

---

## 📋 System Requirements

- **macOS** (Apple Silicon - M1/M4)
- **Python 3.12+** (with Miniconda3, current: 3.12.12)
- **Node.js & npm** (for Angular 18)
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
│   │   ├── api/         # API routes & business logic
│   │   ├── db/          # Database models & migrations
│   │   ├── celery_app/  # Async worker (Mureka)
│   │   ├── schemas/     # Pydantic models
│   │   ├── server.py    # Dev server
│   │   └── worker.py    # Celery worker
│   ├── docker-compose.yml
│   ├── env_template
│   ├── VERSION          # Version file for releases
│   └── pyproject.toml
│
├── aiwebui/             # Angular 18 Frontend
│   ├── src/app/
│   │   ├── pages/       # Feature pages
│   │   │   ├── ai-chat/               # AI Chat conversations
│   │   │   ├── lyric-creation/        # Lyric editor with AI tools
│   │   │   ├── song-sketch-creator/   # Create/edit song sketches
│   │   │   ├── song-sketch-library/   # Manage song sketches
│   │   │   ├── image-generator/       # Image generation with fast enhancement
│   │   │   ├── image-view/            # Image gallery with master-detail view
│   │   │   ├── text-overlay-editor/   # Add text overlays to images
│   │   │   ├── song-generator/        # Song generation UI
│   │   │   └── ...
│   │   ├── services/    # API services
│   │   │   ├── business/         # Image, Conversation, Sketch & Song services
│   │   │   └── config/           # Chat & API config
│   │   ├── components/  # Shared components
│   │   │   ├── image-detail-panel/    # Image detail view component
│   │   │   └── ...
│   │   └── models/      # TypeScript interfaces
│   ├── package.json
│   └── VERSION          # Version file for releases
│
├── scripts/build/       # Release & Build automation
│   ├── create_release.sh           # Create versioned release
│   ├── build-and-push-aiproxysrv.sh
│   ├── build-and-push-aiwebui.sh
│   ├── cleanup-docker-images.sh
│   ├── cleanup-tags.sh
│   ├── cleanup-branchs.sh
│   └── gitcleanup.sh
│
├── forwardproxy/        # Nginx reverse proxy (Production)
│   ├── html/           # Angular build output
│   └── nginx/          # Nginx config
│
├── aitestmock/          # Mock API (Testing)
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
- **Framework**: Angular 18
- **UI**: Angular Material
- **Styling**: SCSS
- **State**: RxJS

### Production
- **Reverse Proxy**: Nginx
- **Container**: Docker + Colima
- **Orchestration**: Docker Compose

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

