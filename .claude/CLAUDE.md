# Claude Code Configuration

**Author:** Rob
**Language:** English
**Last Updated:** 2025-10-21

---

# System & Communication

- Never assume agreement; state your own position if needed.  
- Do not use polite forms (“please”, “thank you”, etc.).
- Offer critical viewpoints when relevant, without softening or beautifying.
- Stick to the facts, even if the answer is negative or counterintuitive.
- Call me "Rob"
- Be factual, precise, and to the point
- Follow Clean Code Patterns and standard ICT best practices
- My nativ language is german so if possible give you answers in german. 

## Language Rules

- **Conversation with Claude**: German
- **Code Classes, Functions, Attributes, Variables, Comments**: English only (Python, TypeScript, Scripts, SCSS)
- **UI Texts**: English only (Buttons, Labels, Messages)
- **Documentation**: English only (README, inline docs)
- **Implementation**: Always present analysis, plan & effort estimation first

---

# Project Overview

**Multi-AI Creative Platform** for Image/Song Generation, Chat and Prompt Management.

## Core Features

- **Image Generation**: AI-powered via DALL-E/OpenAI API
- **Song Generation**: AI music via Mureka API (Lyrics/Instrumental, FLAC/MP3, Stems)
- **Lyric Creation**: AI-assisted lyric editor with section detection, cleanup rules, and structure management
- **Lyric Parsing Rules**: Configurable regex-based cleanup (line breaks, smart quotes, etc.) and section detection (Markdown-style labels)
- **Chat**: Ollama (local) & OpenAI (external) integration
- **Prompt Management**: Template system for reusable prompts
- **User Profiles**: Settings, language preferences (EN/DE)

## Tech Stack

**Frontend:** Angular 18, Material Design, SCSS, TypeScript, RxJS, ngx-translate
**Backend:** FastAPI, Python 3 (3.12.12), Celery, SQLAlchemy, Alembic
**Database:** PostgreSQL, Redis
**Deployment:** Docker (Colima), Nginx (Production)
**Hardware:** Apple Silicon (M1/M4)

---

# Environments

## Development

- **MacBook Air M4**, 32GB RAM
- **Docker (Colima)** for PostgreSQL only
- **Redis & Services** run locally via PyCharm (ARM64)
- **Python 3** with Miniconda3 → Conda env `mac_ki_service_py312`

## Production

- **Mac Studio M1 Max**, 32GB RAM
- **Docker (Colima)** for complete stack
- **Ollama** native, accessible via Open WebUI

---

# Architecture

## Directories Overview

### `aiproxysrv` (Python Backend)
Proxy server for external APIs (OpenAI, Mureka, Ollama) + PostgreSQL Access

**Key Paths:**
- `src/api` - FastAPI routes & business logic
- `src/business` - Business logic services
- `src/db` - SQLAlchemy models & connection
- `src/schemas` - Pydantic models
- `src/celery_app` - Async Mureka tasks
- `src/alembic` - Database migrations
- `src/server.py` - Dev server
- `src/wsgi.py` - Prod entry (Gunicorn)
- `src/worker.py` - Celery worker

### `aiwebui` (Angular 18 Frontend)
Material Design UI with SCSS, TypeScript, ngx-translate

**Key Paths:**
- `src/app/pages/` - Feature pages (image-generator, song-generator, song-view, chat, user-profile)
- `src/app/services/` - API calls & business logic
- `src/app/components/` - Shared UI components
- `src/app/models/` - TypeScript interfaces
- `src/app/guards/` - Route protection
- `src/app/interceptors/` - HTTP handling
- `src/assets/i18n/` - Translation files (en.json, de.json)

### `forwardproxy` (Nginx)
Production reverse proxy, `html/` = Angular deployment target

### `aitestmock` (Test API)
Mock API for testing without external API costs

---

# Critical Rules

## ⚠️ API Routing & Security (PRODUCTION-CRITICAL!)

### 1. All API Endpoints MUST use ApiConfigService
- **NEVER** hardcode URLs in Services (no `baseUrl`, no IPs)
- **NEVER** use `environment.apiUrl` directly in Services
- **ALL** endpoints in `aiwebui/src/app/services/config/api-config.service.ts`
- Services inject `ApiConfigService` and use `this.apiConfig.endpoints.*`

### 2. External APIs ONLY via aiproxysrv Proxy
- **ALL** external calls (OpenAI, Mureka, Ollama) **MUST** go through aiproxysrv
- **NEVER** call external APIs directly from Angular (Browser ≠ HTTPS access)
- **Why?** HTTPS/CORS, API Keys in Backend (not Browser), Centralized control

**Example:**
```typescript
// ❌ WRONG
private baseUrl = 'http://localhost:5050/api';

// ✅ CORRECT (Modern inject() style)
private http = inject(HttpClient);
private apiConfig = inject(ApiConfigService);

getData() {
  return this.http.get(this.apiConfig.endpoints.category.action);
}
```

**Doku External API's:**
- **OLLAMA** https://github.com/ollama/ollama/blob/main/docs/api.md
- **MUREKA** https://platform.mureka.ai/docs/
- **OpenAI** https://platform.openai.com/docs/api-reference/introduction

## Angular 18 Modern Patterns

### Always use inject() for DI
- **ALWAYS** use modern `inject()` function instead of constructor injection
- Import `inject` from `@angular/core`
- Pattern: `private service = inject(ServiceName)`
- Avoids ESLint warning `@angular-eslint/prefer-inject`

### Use HttpClient (not fetch)
- Use Angular's `HttpClient` for all HTTP requests
- Enables JWT injection via interceptors

### Always run build + lint
```bash
# From aiwebui directory
npm run build && npm run lint
```

## SCSS Guidelines

### Nesting Rules
- **Max 2 levels** for custom classes
- **Exception:** Angular Material (`mat-*`) may use 3 levels
- Use **BEM** (`.block__element--modifier`) to flatten hierarchy
- No generic selectors (`div > p`, `h2`) - always use classes

**Example:**
```scss
// ❌ BAD: Deep nesting
.player-bar {
  .player-content {
    .song-info { } // 3+ levels!
  }
}

// ✅ GOOD: Flattened with BEM
.player-bar { }
.player-bar__content { }
.player-bar__song-info { }
```

### Cleanup
- Remove unused styles after changes
- No inline styles
- Comply with Stylelint rules
- Prefer utility classes for recurring layouts

## Internationalization (i18n)

**IMPORTANT:** All new components MUST use i18n (ngx-translate)

### Key Structure
Use **feature-grouped hierarchical keys** (max 3 levels):
```json
{
  "featureName": {
    "subsection": {
      "key": "Translated Text"
    }
  }
}
```

### Implementation
```typescript
// Component
@Component({
  standalone: true,
  imports: [CommonModule, TranslateModule, ...]
})

// Template
<h2>{{ 'featureName.subsection.key' | translate }}</h2>

// With parameters
<span>{{ 'chat.warnings.memoryLow' | translate:{percent: 85} }}</span>
```

### Don'ts
- ❌ DON'T hardcode UI text strings
- ❌ DON'T use flat keys (`buttonSave` instead of `common.save`)
- ❌ DON'T forget to update BOTH `en.json` AND `de.json`
- ❌ DON'T nest deeper than 3 levels

### Available Languages
- `en` - English (default)
- `de` - Deutsch (German)

## Python Code Quality & Testing

### Code Quality (Ruff)

**IMPORTANT:** All Python code MUST pass Ruff linting before commits.

#### Setup
```bash
# From aiproxysrv directory
pip install -e ".[dev]"        # Install ruff + pre-commit
pre-commit install             # Enable git hooks (optional)
```

#### Usage
```bash
# From aiproxysrv directory
ruff check .                   # Check all files
ruff check . --fix             # Auto-fix issues
ruff format .                  # Format code (replaces black)
ruff check src/api/routes/     # Check specific directory
```

#### Configuration
- **Location:** `aiproxysrv/pyproject.toml` under `[tool.ruff]`
- **Line length:** 120 characters
- **Rules:** E (pycodestyle), F (pyflakes), I (isort), N (naming), UP (pyupgrade), B (bugbear), C4 (comprehensions), SIM (simplify), ARG (unused-arguments)
- **Auto-fix:** Enabled for all rules
- **Pre-commit:** Automatically runs on `git commit` if installed

#### Why Ruff?
- **10-100x faster** than pylint/flake8
- **All-in-one:** Replaces pylint, flake8, black, isort
- **Modern:** Rust-based, industry standard
- **Zero config:** Works out of the box

### Unit Testing (pytest)

**IMPORTANT:** All Python code changes MUST be validated with unit tests before commits.

#### When to Write/Extend Tests
- **New Features:** Write tests for all new functionality
- **Bug Fixes:** Add test case that reproduces the bug, then fix it
- **Refactoring:** Extend existing tests if logic changes
- **API Changes:** Update tests to cover new endpoints or parameters

#### Usage
```bash
# From aiproxysrv directory
pytest                         # Run all tests
pytest -v -s                   # Verbose output with print statements
pytest tests/test_health.py    # Run specific test file
pytest -k "test_name"          # Run tests matching pattern
pytest --cov=src               # Run with coverage report
```

#### Test Organization
- **Location:** `aiproxysrv/tests/`
- **Pattern:** `test_*.py` or `*_test.py`
- **Fixtures:** Use `conftest.py` for shared fixtures (DB session, test client, etc.)

#### Why Unit Tests?
- **Catch regressions** before they reach production
- **Document behavior** through test cases
- **Enable refactoring** with confidence
- **Faster debugging** than manual testing

## General Don'ts

- ❌ NEVER commit `.env` to repo
- ❌ NEVER use emojis (unless explicitly requested)
- ❌ NEVER create unnecessary markdown files
- ❌ NEVER skip linting before commits (run `ruff check . --fix` in aiproxysrv)
- ❌ NEVER skip unit tests before commits (run `pytest` in aiproxysrv)

---

# Development Workflow

## Quick Commands

### Frontend (aiwebui)
**Working Directory:** `aiwebui/`
```bash
npm run dev                    # Development server
npm run build:prod             # Production build → forwardproxy/html/aiwebui
npm run lint                   # ESLint
npm run test                   # Unit tests
```

### Backend (aiproxysrv)
**Working Directory:** `aiproxysrv/`
```bash
# Activate conda environment (if not active)
conda activate mac_ki_service

# Development Server
python src/server.py           # Dev server (PyCharm)

# Database Migrations
# IMPORTANT: alembic.ini is in aiproxysrv/ root, NOT in src/
# Always run from aiproxysrv/ directory!
alembic current                                         # Show current version
alembic upgrade head                                    # Apply migrations
alembic revision --autogenerate -m "message"            # Create migration
alembic history                                         # Show migration history

# Celery Worker
python src/worker.py           # Start worker
celery -A src.worker flower    # Monitor tasks (http://localhost:5555)

# Code Quality & Linting (Ruff)
pip install -e ".[dev]"        # Install dev dependencies (ruff, pre-commit)
ruff check .                   # Run linter
ruff check . --fix             # Auto-fix issues
ruff format .                  # Format code
ruff check src/path/to/file.py # Check specific file

# Pre-commit Hooks (optional, auto-runs ruff on git commit)
pre-commit install             # Install git hooks
pre-commit run --all-files     # Run manually on all files

# Unit Testing (pytest)
pytest                         # Run all tests
pytest -v -s                   # Verbose output with print statements
pytest tests/test_health.py    # Run specific test file
pytest -k "test_name"          # Run tests matching pattern
pytest --cov=src               # Run with coverage report
```

### Database Seeding
**Working Directory:** Project root (`mac_ki_service/`)

**IMPORTANT:** All seed scripts are SQL-based (not Python) for easy deployment in Docker environments.

```bash
# Seed Prompt Templates
cat scripts/db/seed_prompts.sql | docker exec -i postgres psql -U aiproxy -d aiproxysrv

# Seed Image Fast Enhancement Template
cat scripts/db/seed_prompts_image_fast.sql | docker exec -i postgres psql -U aiproxy -d aiproxysrv

# Seed Lyric Parsing Rules
cat scripts/db/seed_lyric_parsing_rules.sql | docker exec -i postgres psql -U aiproxy -d aiproxysrv

# Local PostgreSQL (without Docker)
psql -h localhost -U aiproxy -d aiproxysrv -f scripts/db/seed_prompts.sql
psql -h localhost -U aiproxy -d aiproxysrv -f scripts/db/seed_prompts_image_fast.sql
psql -h localhost -U aiproxy -d aiproxysrv -f scripts/db/seed_lyric_parsing_rules.sql
```

**DB Credentials** (from `aiproxysrv/.env_postgres`):
- **Service Name**: `postgres` (Docker Compose service)
- **Database**: `aiproxysrv`
- **User**: `aiproxy`
- **Password**: `aiproxy123`

**Why SQL instead of Python?**
- ✅ No Python environment dependencies
- ✅ Easy to run in Docker containers (Production)
- ✅ Fast execution, no DB connection overhead
- ✅ Version-controlled, idempotent (UPSERT logic)
- ✅ No need to worry about `.env` configurations

### Docker
**Working Directory:** Project root (`mac_ki_service/`)
```bash
# Development (PostgreSQL only)
docker compose up postgres

# Production (Full stack)
docker compose up -d
docker compose logs -f

# Check running containers
docker compose ps
```

## Testing Strategy

### Mock API (aitestmock)
Testing without external API costs:
- Image: `"0001"` → OK, `"0002"` → Error
- Song: `"0001"` → OK, `"0002"` → Error, `"30s"` → 30s delay

### Frontend Testing
**Working Directory:** `aiwebui/`
```bash
npm run test -- --watch       # Unit tests
npm run e2e                   # E2E tests
```

### Backend Testing
**Working Directory:** `aiproxysrv/`
```bash
pytest                        # Run all tests
pytest -v -s                  # Verbose output
```

## Deployment Checklist

**Before Production Deploy:**
1. ✅ Run `npm run build:prod` (from `aiwebui/`)
2. ✅ Run `npm run lint` (from `aiwebui/`, no errors)
3. ✅ Run `ruff check . --fix && ruff format .` (from `aiproxysrv/`, no errors)
4. ✅ Run `pytest` (from `aiproxysrv/`, all tests pass)
5. ✅ Test language switch (EN ↔ DE)
6. ✅ Verify all API endpoints use `ApiConfigService`
7. ✅ Check no hardcoded URLs in frontend
8. ✅ Verify `.env` not committed
9. ✅ **Database Migrations** (from `aiproxysrv/`):
   - `alembic current` - Check current version
   - `alembic upgrade head` - Apply pending migrations
10. ✅ **Schema Comparison** (PyCharm Database Tool):
    - Compare DEV ↔ PROD structures
    - Red/Green = critical differences (fix before deploy!)
    - Blue = harmless (operator classes, extensions)
    - No structural differences = ready to deploy
11. ✅ Test with aitestmock first
12. ✅ Check Docker containers start (`docker compose up -d` from root)
13. ✅ Verify Nginx routing (forwardproxy)

**After Production Deploy:**
1. ✅ Run `alembic upgrade head` on PROD (if new migrations)
2. ✅ Verify schema with PyCharm Compare (should be identical)
3. ✅ Run seed scripts if needed (from project root):
   ```bash
   cat scripts/db/seed_prompts.sql | docker exec -i mac_ki_service-postgres-1 psql -U aiuser -d aiproxy
   cat scripts/db/seed_lyric_parsing_rules.sql | docker exec -i mac_ki_service-postgres-1 psql -U aiuser -d aiproxy
   ```

---

# Code Patterns

## Angular Component (Modern inject() style)

```typescript
@Component({
  standalone: true,
  imports: [CommonModule, TranslateModule, MaterialModules]
})
export class ExampleComponent implements OnInit, OnDestroy {
  // Properties
  public items: Item[] = [];
  public loading = false;

  // Modern DI with inject()
  private destroy$ = new Subject<void>();
  private service = inject(ExampleService);
  private snackBar = inject(MatSnackBar);

  ngOnInit(): void {
    this.loadData();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private loadData(): void {
    this.service.getData()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (data) => this.items = data,
        error: (error) => this.handleError(error)
      });
  }
}
```

## Angular Service (Modern inject() style)

```typescript
@Injectable({ providedIn: 'root' })
export class ExampleService {
  private http = inject(HttpClient);
  private apiConfig = inject(ApiConfigService);

  public getData(): Observable<Item[]> {
    return this.http.get<ApiResponse<Item[]>>(
      this.apiConfig.endpoints.category.list()
    ).pipe(
      map(response => response.data),
      catchError(error => throwError(() => error))
    );
  }
}
```

## Python FastAPI Route

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..schemas.song import SongCreate, SongResponse

router = APIRouter(prefix="/api/songs", tags=["songs"])

@router.get("/", response_model=List[SongResponse])
async def list_songs(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    songs = db.query(Song).offset(skip).limit(limit).all()
    return songs
```

---

# Troubleshooting

## CSS Layout Issues (Horizontal Scrollbar)

**Quick Fix:**
```javascript
// Browser Console: Find overflowing elements
document.querySelectorAll('*').forEach(el => {
    if (el.scrollWidth > el.clientWidth) {
        console.log('Overflow:', el.tagName, el.className);
    }
});
```

**Common Causes:**
- Tables without `table-layout: fixed` + `width: 100%`
- Flex containers without `min-width: 0`
- Browser cache (Hard Refresh: `Cmd+Shift+R`)

## Backend Issues

**PostgreSQL:**
```bash
# From project root
docker compose ps postgres
docker compose logs postgres
docker exec -it mac_ki_service-postgres-1 psql -U aiuser -d aiproxy
```

**Celery Worker:**
```bash
# From aiproxysrv directory
celery -A src.worker inspect active
pkill -f "celery worker" && python src/worker.py
```

**API Testing:**
```bash
# From anywhere
curl http://localhost:5050/api/health
curl http://localhost:5050/api/account/status
```

## Docker Issues

**Container won't start:**
```bash
# From project root
docker compose logs [service-name]
docker compose build --no-cache [service-name]
docker system prune -f
```

**Port conflicts:**
```bash
# From anywhere
lsof -i :5050  # Backend
lsof -i :4200  # Frontend dev
lsof -i :5432  # PostgreSQL
```

---

# Quick Reference

## Database Tables

- `songs` - Generated songs (title, lyrics, status, job_id, flac_url, mp3_url, stems_url)
- `song_choices` - Individual song variations from MUREKA (mp3_url, flac_url, stem_url, duration, rating)
- `images` - Generated images (title, prompt, status, job_id, url)
- `prompt_templates` - Reusable AI prompts (category, action, pre_condition, post_condition, model)
- `lyric_parsing_rules` - Configurable regex rules for lyric cleanup and section detection (pattern, replacement, rule_type, order)
- `users` - User accounts & settings (email, password_hash, is_active)
- `conversations` - Chat conversations (title, model, provider, token_count)
- `messages` - Individual chat messages (role, content, token_count)
- `messages_archive` - Archived messages from compression

## Key API Endpoints

```
POST /api/images/generate      # Generate image
GET  /api/images               # List images
POST /api/songs/generate       # Generate song
GET  /api/songs                # List songs
GET  /api/songs/{id}/flac      # Download FLAC
POST /api/songs/{id}/stems     # Generate stems
GET  /api/prompts              # List prompt templates
GET  /api/account/status       # Mureka account status
```

## Common Pitfalls

### Frontend
1. **Forgetting i18n**: Hardcoding UI text instead of `{{ 'key' | translate }}`
2. **Constructor DI**: Using constructor injection instead of `inject()`
3. **Hardcoded URLs**: Not using `ApiConfigService`
4. **Deep SCSS nesting**: Going beyond 2-3 levels
5. **Missing cleanup**: Not unsubscribing with `takeUntil(destroy$)`

### Backend
1. **Missing migrations**: Running code before `alembic upgrade head`
2. **Celery not running**: Async tasks fail silently
3. **DB connection leaks**: Not closing sessions properly
4. **Missing error handling**: No try/catch in routes

### Both
1. **Ignoring linter warnings**: ESLint/Stylelint errors
2. **Not testing language switch**: Only testing in one language
3. **Committing `.env`**: Security breach!
4. **Skipping builds**: Not running `npm run build` before testing

---

# AI-Context Keywords

**Tech Stack:** Angular 18, FastAPI, PostgreSQL, Redis, Celery, SQLAlchemy, Alembic, Docker, Nginx, SCSS, TypeScript, RxJS, ngx-translate

**Domain:** Image Generation (DALL-E/OpenAI), Song Generation (Mureka), Chat (Ollama/OpenAI), Prompt Management, User Profiles, Media Management

**Patterns:** Master-Detail Views, Service Layer, Shared Components, Guards, Interceptors, Async Jobs, Job Tracking, File Handling, Error Handling

**Layout:** CSS Grid, Flexbox, Responsive Design, Material Design, Overflow Prevention

**Performance:** Lazy Loading, OnPush Strategy, Memory Management (takeUntil), Bundle Optimization, Redis Caching

**Security:** CORS, Token Management, Input Validation, Environment Variables, Proxy Pattern

**Workflow:** Hot Reload, Build Pipeline, Linting, Type Checking, DB Migrations, Docker Compose

---

# CI/CD - GitHub Actions

## Setup

- **Platform:** GitHub Actions (hosted)
- **Trigger:** Git tag push (`v*.*.*`)
- **Workflow:** `.github/workflows/release.yml`
- **Registry:** GitHub Container Registry (GHCR)
- **Architecture:** ARM64 only (linux/arm64)

## Build Triggers

### Automatic
- **Tag Push:** `v*.*.*` → Full build & push to GHCR
- Triggered by: `./scripts/build/create_release.sh v2.2.6`

### Manual
- GitHub UI: Actions → "Build & Release" → "Run workflow"
- Or: Re-run failed builds

## Pipeline Steps

1. **Checkout:** Clone repository
2. **QEMU Setup:** Enable ARM64 emulation
3. **Buildx:** Multi-platform Docker builds
4. **Login GHCR:** Automatic via `GITHUB_TOKEN`
5. **Build Images:** Parallel builds with layer caching
   - `aiproxysrv-app` (backend)
   - `celery-worker-app` (worker)
   - `aiwebui-app` (frontend)
6. **Lint:** ESLint on Angular code (parallel job)

## Build Time

- **Expected:** ~10-12 minutes
- **First build:** ~15 minutes (no cache)
- **Subsequent:** ~8-10 minutes (with cache)

## Secrets

**Automatically available (no configuration needed):**
- `GITHUB_TOKEN` - Auto-generated for GHCR push access

## Cost

**Free Tier:**
- 2000 minutes/month for private repos
- Linux runners: 1x multiplier
- ~10-12 min/build = **~166 builds/month free**

## Monitoring

**Build Status:**
```bash
# Via GitHub UI
https://github.com/rwellinger/thwelly_ai_tools/actions

# Via gh CLI
gh run list --repo rwellinger/thwelly_ai_tools
gh run watch --repo rwellinger/thwelly_ai_tools

# Badge in README
[![Build Status](https://github.com/rwellinger/thwelly_ai_tools/actions/workflows/release.yml/badge.svg)](https://github.com/rwellinger/thwelly_ai_tools/actions)
```

## Troubleshooting

### Build schlägt fehl

```bash
# Check logs in GitHub UI
https://github.com/rwellinger/thwelly_ai_tools/actions

# Or via CLI
gh run view --repo rwellinger/thwelly_ai_tools

# Re-run failed build
gh run rerun <RUN_ID> --repo rwellinger/thwelly_ai_tools
```

### Images nicht in GHCR

```bash
# Check GHCR packages
https://github.com/rwellinger?tab=packages

# Verify GITHUB_TOKEN permissions
# Actions → Workflow → Settings → Permissions
# Ensure "Read and write permissions" for packages
```

### Fallback: Manuelle Builds

```bash
# Falls GitHub Actions nicht verfügbar
./scripts/build/build-and-push-aiproxysrv.sh v2.2.6
./scripts/build/build-and-push-aiwebui.sh v2.2.6
```

## Workflow File Location

`.github/workflows/release.yml`
