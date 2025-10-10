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
- **Image Generation** via DALL·E 3 (OpenAI)
- **Song Generation** via Mureka API (asynchronous with Celery)
- **PostgreSQL** database for persistent storage
- **Angular 18** frontend with Material Design
- **Redis & Celery** for asynchronous task processing

---

## 📋 System Requirements

- **macOS** (Apple Silicon - M1/M4)
- **Python 3.11+** (with Miniconda3)
- **Node.js & npm** (for Angular 18)
- **Docker** (via Colima for macOS)
- **Git**

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

#### 2. Build & Push Docker Images

After creating the release, build and push Docker images:

```bash
# Build and push backend images (aiproxysrv-app + celery-worker-app)
./scripts/build/build-and-push-aiproxysrv.sh

# Build and push frontend image (aiwebui-app)
./scripts/build/build-and-push-aiwebui.sh
```

**What these do:**
- ✅ Read version from VERSION files automatically
- ✅ Build Docker images with correct tags (`vX.Y.Z` + `latest`)
- ✅ Check if version already exists in registry
- ✅ Push to GitHub Container Registry (`ghcr.io/rwellinger/*`)
- ✅ Support `--force` flag to skip confirmation

**Available Docker Images:**
- `ghcr.io/rwellinger/aiproxysrv-app:vX.Y.Z` (Backend API)
- `ghcr.io/rwellinger/celery-worker-app:vX.Y.Z` (Async Worker)
- `ghcr.io/rwellinger/aiwebui-app:vX.Y.Z` (Frontend)

#### Optional: Force Push (Overwrite Existing Tags)

```bash
# Build and push with force (skip confirmation)
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
│   │   │   ├── ai-chat/          # AI Chat conversations
│   │   │   ├── image-generator/  # Image generation UI
│   │   │   ├── song-generator/   # Song generation UI
│   │   │   └── ...
│   │   ├── services/    # API services
│   │   │   ├── business/         # Conversation management
│   │   │   └── config/           # Chat & API config
│   │   ├── components/  # Shared components
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

