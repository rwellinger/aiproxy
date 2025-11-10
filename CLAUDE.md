# Claude Code Configuration

**Author:** Rob
**Language:** English
**Last Updated:** 2025-11-10

---

# Project Structure (CRITICAL!)

**TWO SEPARATE REPOSITORIES:**

## 1. mac_ki_service/ - DEVELOPMENT (Source Code)
- **Location:** `/Users/robertw/Workspace/mac_ki_service`
- **Purpose:** Source code, builds, CI/CD, development
- ✅ **Edit code here**

## 2. thwelly_ki_app/ - PRODUCTION (Deployment Only)
- **Location:** `/Users/robertw/Workspace/thwelly_ki_app`
- **Purpose:** Production deployment configuration ONLY
- ⚠️ **NO source code editing! Only configs/secrets**
- ⚠️ **FINGER WEG VON CODE - Deployment only!**

**Workflow:**
1. DEV (mac_ki_service): Code → Commit → CI builds Images → ghcr.io
2. PROD (thwelly_ki_app): Update docker-compose.yml versions → `docker compose pull && up -d`

---

# System & Communication

- Call me "Rob"
- Conversation: German
- Code/Comments/Docs: English only
- No polite forms, be factual and direct
- Always present analysis, plan & effort estimation first

---

# Project Overview

**Multi-AI Creative Platform** - Image/Song Generation, Chat, Prompt Management

**Tech Stack:**
- **Frontend:** Angular 18, Material, SCSS, TypeScript, RxJS, ngx-translate
- **Backend:** FastAPI, Python 3.12.12, Celery, SQLAlchemy, Alembic
- **Database:** PostgreSQL, Redis
- **Deployment:** Docker (Colima), Nginx
- **Hardware:** Apple Silicon M4, Conda env `mac_ki_service_py312`

> **Details:** siehe `docs/ARCHITECTURE.md`

---

# Critical Rules

## ⚠️ API Routing & Security (PRODUCTION-CRITICAL!)

### 1. All API Endpoints MUST use ApiConfigService
- **NEVER** hardcode URLs in Services (no `baseUrl`, no IPs)
- **NEVER** use `environment.apiUrl` directly
- **ALL** endpoints in `aiwebui/src/app/services/config/api-config.service.ts`

```typescript
// ❌ WRONG
private baseUrl = 'http://localhost:5050/api';

// ✅ CORRECT
private http = inject(HttpClient);
private apiConfig = inject(ApiConfigService);

getData() {
  return this.http.get(this.apiConfig.endpoints.category.action);
}
```

### 2. External APIs ONLY via aiproxysrv Proxy (CRITICAL!)
- **ALL** external calls (OpenAI, Mureka, Ollama, **S3/MinIO**) **MUST** go through aiproxysrv
- **NEVER** call external APIs directly from Angular
- **NEVER** use S3 presigned URLs in Angular (Browser can't access internal MinIO!)
- **Why?** HTTPS/CORS, API Keys in Backend (not Browser), Centralized control, Internal services not accessible from Browser

**CRITICAL - S3/MinIO:**
- Browser **CANNOT** access internal MinIO (https://minio:9000/...)
- **ALWAYS** use Backend proxy routes (e.g., `/api/v1/images/{id}`, `/api/v1/releases/{id}/cover`)
- See "Pre-Implementation Checkliste" below for S3 resource handling

**External API Docs:**
- **OLLAMA**: https://github.com/ollama/ollama/blob/main/docs/api.md
- **MUREKA**: https://platform.mureka.ai/docs/
- **OpenAI**: https://platform.openai.com/docs/api-reference/introduction

### 3. Ollama + Prompt Template Integration (MANDATORY WORKFLOW!)

**CRITICAL:** This is NOT a direct Ollama proxy - it's a **Template-Driven Generation System**.

**Mandatory Workflow:**
```
User Input → Load Template from DB → Validate → Unified Endpoint → Response
```

**Rules:**
- **ALL** Ollama+Template calls **MUST** use `/api/v1/ollama/chat/generate-unified`
- **ALL** operations **MUST** go through `ChatService` in frontend
- **NEVER** implement direct Ollama API calls
- **NEVER** use templates before they exist in DB

```typescript
// ✅ CORRECT: Simple case
async myNewFeature(input: string): Promise<string> {
  return this.chatService.validateAndCallUnified('category', 'action', input);
}

// ❌ WRONG: Direct Ollama call (bypasses template system!)
async wrongImplementation(input: string): Promise<string> {
  return this.http.post('http://localhost:11434/api/generate', {
    model: 'llama2',  // ❌ Hardcoded, not from DB!
    prompt: input
  });
}
```

**See:** `aiwebui/src/app/services/config/chat.service.ts` (Reference implementation)

---

### 4. JWT Authentication REQUIRED
- **ALL** backend endpoints (except login/register/health) **MUST** use `@jwt_required`
- User ID **MUST** be from JWT token via `get_current_user_id()`, **NOT** URL params

```python
# ✅ CORRECT
@api_user_v1.route("/profile", methods=["GET"])
@jwt_required
def get_user_profile():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    return user_controller.get_user_profile(str(user_id))
```

---

### 5. Pre-Implementation Checkliste (MANDATORY for External Resources!)

**CRITICAL:** Before implementing ANY feature that returns external resources (files, images, URLs):

#### Step 1: Pattern Search (MANDATORY!)
```
1. Does a similar feature exist? (Images, Files, etc.)
   → grep -r "serve.*s3\|proxy.*resource" src/

2. Found existing pattern?
   → COPY the pattern 1:1
   → DO NOT reinvent the wheel
```

#### Step 2: Backend Proxy Pattern (MANDATORY!)
```
✅ CORRECT:
Frontend → /api/v1/resource/{id} → Backend loads from S3 → Binary Response

❌ WRONG:
Frontend ← MinIO presigned URL (https://minio:9000/...) ← Backend
          └─ Browser CAN'T access internal MinIO!
```

#### Reference Implementations
```
✅ Image S3 Proxy:
   - Route: api/routes/image_routes.py → serve_s3_image()
   - Service: adapters/s3/s3_proxy_service.py → serve_resource()

✅ Song Release Cover Proxy:
   - Route: api/routes/song_release_routes.py → serve_cover()
   - Service: adapters/s3/s3_proxy_service.py → serve_resource()
```

**WHY:** Browser CAN'T access internal services, Backend proxy = centralized security

---

## UI Patterns & Component Standards (CRITICAL!)

**MANDATORY:** All new UI components **MUST** follow `docs/UI_PATTERNS.md`

### Standard Mixins (MANDATORY)

```scss
// ✅ ALWAYS use these mixins from src/scss/_mixins.scss
.edit-button { @include button-secondary('base'); }
.delete-button { @include button-secondary('base'); }
.primary-action-button { @include button-primary('base'); }

// ❌ NEVER write custom button CSS
.my-button {
  background-color: #5a6268;  // ❌ WRONG
}
```

### Reference Implementation
**Equipment Gallery** (`aiwebui/src/app/pages/equipment-gallery/`) - Master-Detail Layout, Button Standards, Font Awesome Icons

**Checklist for New Pages:**
- [ ] Review `docs/UI_PATTERNS.md`
- [ ] Check Equipment Gallery as reference
- [ ] Use `@include button-*` mixins
- [ ] Use Font Awesome icons (`<i class="fas fa-*">`)
- [ ] Place actions in `detail-actions` section

---

## Architecture Principles (CRITICAL!)

### 3-Layer Architecture (MANDATORY)

**Separation of Concerns:**
```
Controller → Orchestrator → Transformer/Normalizer + Repository
(HTTP)       (Coordinates)  (Pure Functions)      (DB CRUD)
```

**Naming Convention (CRITICAL!):**

| File Pattern | Purpose | Testable? | Example |
|--------------|---------|-----------|---------|
| `*_orchestrator.py` | Coordinates services, NO business logic | ❌ No | `SketchOrchestrator` |
| `*_transformer.py` | Pure functions: transformations, mappings | ✅ Yes (100% coverage) | `SongMurekaTransformer` |
| `*_normalizer.py` | Pure functions: string normalization | ✅ Yes (100% coverage) | `SketchNormalizer` |
| `*_service.py` (in `db/`) | CRUD operations only | ❌ No (infrastructure) | `SketchService` |

**Layer Responsibilities:**

**1. Business Layer** (`src/business/`)
- **Orchestrators**: Coordinate services (NOT testable, no business logic)
- **Transformers/Normalizers**: Pure functions (100% unit-testable)
- ✅ Business logic in transformers/normalizers
- ❌ NO database queries
- ❌ NO file system operations

**2. Repository Layer** (`src/db/*_service.py`)
- ✅ CRUD operations only
- ❌ NO business logic
- ❌ NO transformations
- ❌ **NO unit tests** (infrastructure)

**3. Controller Layer** (`src/api/controllers/*_controller.py`)
- ✅ HTTP request/response, call orchestrator
- ❌ NO business logic
- ❌ NO direct DB queries

**Example:**
```python
# ✅ CORRECT
image_controller.py
  └─> image_orchestrator.py (coordinates, NOT testable)
       ├─ Calls: image_enhancement_service.py (pure functions, 100% tested)
       └─> image_service.py (DB CRUD, NO tests)

# ❌ WRONG: Business logic in DB service
class SomeService:
    def get_data(self, db: Session):
        result = db.query(...).first()
        return {"total": float(result.total)}  # ❌ Transformation in DB layer!
```

**Checklist:**
- [ ] Business logic in `src/business/` (unit-testable)
- [ ] DB operations in `src/db/` (CRUD only, no tests)
- [ ] Controller calls business layer (no direct DB)

---

### Automated Architecture Validation (CRITICAL!)

**IMPORTANT:** Architecture rules are **automatically enforced** via linters!

#### Python Backend (import-linter)

**Validates:**
- ❌ Controllers MUST NOT import DB services directly
- ❌ DB layer MUST NOT import business logic
- ❌ Business layer MUST NOT import SQLAlchemy directly

```bash
# From aiproxysrv/
make lint-all                   # Ruff + import-linter
```

**Common violations:**
```bash
# ERROR: Controllers must go through business layer
src.api.controllers.foo_controller -> src.db.bar_service

# Fix: Use orchestrator
src.api.controllers.foo_controller -> src.business.foo_orchestrator -> src.db.bar_service
```

#### Angular Frontend (dependency-cruiser)

**Validates:**
- ❌ Services MUST NOT depend on Components/Pages
- ❌ Services MUST use ApiConfigService (NOT environment.apiUrl)
- ❌ No circular dependencies

```bash
# From aiwebui/
npm run lint:arch               # Architecture only
make lint-all                   # TypeScript + SCSS + Architecture
```

**Common violations:**
```bash
# ERROR: Services must use ApiConfigService
src/app/services/foo.service.ts -> environments/environment

# Fix: Inject ApiConfigService
private apiConfig = inject(ApiConfigService);
this.http.get(this.apiConfig.endpoints.category.action);
```

**Integration:**
- Architecture errors are **build blockers** (treat like ESLint errors)
- Fix violations **before marking tasks completed**

---

## Angular 18 Modern Patterns

### Always use inject() for DI
```typescript
// ✅ CORRECT
private http = inject(HttpClient);
private apiConfig = inject(ApiConfigService);

// ❌ WRONG: Constructor injection
constructor(private http: HttpClient) {}
```

### Always run lint + build
```bash
# From aiwebui/
make lint-all && make build-dev  # Development
make build-prod                   # Production (runs lint-all + test automatically)
```

**Available commands:**
- `make lint-all` - TypeScript + SCSS + Architecture
- `make lint-fix` - Auto-fix issues
- `make build-prod` - Production build with ALL pre-checks
- `make test` - Run unit tests

---

## TypeScript Unit Testing

**IMPORTANT:** All new services with business logic MUST have unit tests.

### What to Test

✅ **DO write tests for:**
- Business Services (`services/business/*.service.ts`) - Pure functions, transformations
- Utility Services (`services/utils/*.service.ts`) - String manipulation, calculations
- Pure functions - No HTTP calls, DOM manipulation

❌ **DO NOT write tests for:**
- HTTP Services - Services that only make API calls
- Config Services - Services that only read configuration
- Angular Components - Use manual testing

### Test Location (CRITICAL!)

Test files MUST be co-located with service:
```
✅ CORRECT:
src/app/services/business/
  ├── chat-export.service.ts
  └── chat-export.service.spec.ts       // ✅ Same directory

❌ WRONG:
src/app/services/
  ├── song.service.spec.ts              // ❌ Wrong location!
  └── business/song.service.ts
```

### Running Tests

```bash
# From aiwebui/
make test                      # Run all tests (single run)
make test-watch               # Watch mode (development)
make test-coverage            # With coverage report
```

---

## SCSS Guidelines

### Nesting Rules (CRITICAL!)
- **Max 2 levels** for custom classes
- **Exception:** Angular Material (`mat-*`) may use 3 levels
- Use **BEM** (`.block__element--modifier`)

```scss
// ❌ BAD: Deep nesting
.player-bar {
  .player-content {
    .song-info { } // 3+ levels!
  }
}

// ✅ GOOD: BEM
.player-bar { }
.player-bar__content { }
.player-bar__song-info { }
```

### NEW Components (Strict Rules)
Components with `_NEW_` or `-new-` in filename have STRICT Stylelint enforcement:
- BEM max 2 levels for custom elements
- Material overrides max 3 levels (only for `mat-*`)

---

## Internationalization (i18n)

**MANDATORY:** All new components use ngx-translate

```typescript
// Template
<h2>{{ 'featureName.subsection.key' | translate }}</h2>

// With parameters
<span>{{ 'chat.warnings.memoryLow' | translate:{percent: 85} }}</span>
```

**Key Structure:** Max 3 levels, feature-grouped
```json
{
  "featureName": {
    "subsection": {
      "key": "Translated Text"
    }
  }
}
```

**Don'ts:**
- ❌ Hardcode UI text
- ❌ Use flat keys
- ❌ Update only one language file

---

## Python Code Quality

### Logging (Loguru)

```python
# ✅ CORRECT
from utils.logger import logger

logger.debug("Sketch retrieved", sketch_id=sketch_id, user_id=user_id)
logger.error("Database error", error=str(e), sketch_id=sketch_id)

# ❌ WRONG: Standard logging (CRASHES!)
import logging
logger = logging.getLogger(__name__)
logger.info("Processing", task_id=task_id)  # TypeError!

# ❌ WRONG: Context in message string
logger.debug(f"Sketch retrieved: {sketch_id}")
```

**CRITICAL:** Using `import logging` causes crashes with structured parameters!

### Ruff + pytest

```bash
# From aiproxysrv/
make lint-all                  # Ruff + import-linter + Conda check
make format                    # Auto-fix and format
make test                      # pytest
```

**What to Test:**

❌ **DO NOT test:**
- Database services (`src/db/*_service.py`) - Pure CRUD, no logic
- File system operations
- SQLAlchemy mocks

✅ **DO test:**
- Business services (`src/business/*_service.py`) - Pure functions
- Validation logic
- Complex algorithms

---

# Development Workflow

## Quick Commands

### Frontend (aiwebui)

**CRITICAL: ALWAYS use `make` (NOT direct `npm` for production)!**

```bash
# Code Quality
make lint-all                  # TypeScript + SCSS + Architecture
make lint-fix                  # Auto-fix issues

# Build (CRITICAL: use make!)
make build-prod                # Production with ALL pre-checks
make build-dev                 # Development

# Development
make dev                       # Dev server
make test                      # Unit tests
make test-watch               # Tests in watch mode
```

### Backend (aiproxysrv)

```bash
# Activate conda environment
conda activate mac_ki_service_py312

# Development Server
python src/server.py

# Database Migrations (ALWAYS use make!)
make db-current                # Show current version
make db-upgrade                # Apply migrations
make db-revision               # Create new migration

# Celery Worker
python src/worker.py

# Code Quality (ALWAYS use make!)
make lint-all                  # Ruff + import-linter
make format                    # Auto-fix and format
make test                      # pytest
```

### Database Seeding

```bash
# From project root (mac_ki_service/)
cat scripts/db/seed_prompts.sql | docker exec -i postgres psql -U aiproxy -d aiproxysrv
cat scripts/db/seed_prompts_image_fast.sql | docker exec -i postgres psql -U aiproxy -d aiproxysrv
cat scripts/db/seed_lyric_parsing_rules.sql | docker exec -i postgres psql -U aiproxy -d aiproxysrv
```

**DB Credentials:** Service: `postgres`, DB: `aiproxysrv`, User: `aiproxy`, Password: `aiproxy123`

### Docker

```bash
docker compose up postgres     # Development (PostgreSQL only)
docker compose logs -f         # View logs
```

---

## Common Pitfalls

### Frontend
1. Forgetting i18n - Hardcoding text instead of `{{ 'key' | translate }}`
2. Constructor DI - Use `inject()` instead
3. Hardcoded URLs - Not using `ApiConfigService`
4. Deep SCSS nesting - Beyond 2-3 levels

### Backend
1. Missing migrations - Run `make db-upgrade` first
2. Celery not running - Async tasks fail silently
3. Missing JWT protection - Unprotected endpoints
4. Architecture violations - Business logic in DB layer

### Both
1. Ignoring linter warnings
2. Not testing language switch
3. Committing `.env`
4. Skipping builds/tests before commits

---

## General Don'ts

- ❌ NEVER commit `.env` to repo
- ❌ NEVER use emojis (unless requested)
- ❌ NEVER create unnecessary docs
- ❌ NEVER skip linting/tests before commits

---

# Additional Documentation

- **UI Patterns**: `docs/UI_PATTERNS.md` **(CRITICAL - Read before new pages!)**
- **Architecture**: `docs/ARCHITECTURE.md` → `docs/arch42/README.md`
- **Code Patterns**: `docs/CODE_PATTERNS.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`
- **CI/CD**: `docs/CI_CD.md`
