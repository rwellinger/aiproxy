# Claude Code Configuration

**Author:** Rob
**Language:** English
**Last Updated:** 2025-10-31

---

# System & Communication

- Never assume agreement; state your own position if needed.
- Do not use polite forms ("please", "thank you", etc.).
- Offer critical viewpoints when relevant, without softening or beautifying.
- Stick to the facts, even if the answer is negative or counterintuitive.
- Call me "Rob"
- Be factual, precise, and to the point
- **CRITICAL:** Follow Clean Code Patterns and standard ICT best practices
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

## Tech Stack

**Frontend:** Angular 18, Material Design, SCSS, TypeScript, RxJS, ngx-translate
**Backend:** FastAPI, Python 3.12.12, Celery, SQLAlchemy, Alembic
**Database:** PostgreSQL, Redis
**Deployment:** Docker (Colima), Nginx (Production)
**Hardware:** Apple Silicon (M1/M4)

## Core Features

- **Image Generation** (DALL-E/OpenAI): Fast Enhancement, Gallery, Detail View
- **Song Generation** (Mureka API): Sketches, Styles, FLAC/MP3/Stems, Playback
- **Lyric Creation**: AI-assisted editor, Lyric Architect, Parsing Rules
- **Chat**: Ollama (local) & OpenAI, Multi-conversation, Streaming, Export
- **Prompt Management**: Templates, Categories, Pre/post-conditions
- **User Profiles**: JWT Auth, Language Preferences (EN/DE)

> **Detaillierte Architektur**: siehe `docs/ARCHITECTURE.md`

---

# Environments

## Development
- **MacBook Air M4**, 32GB RAM
- Docker (Colima) for PostgreSQL only
- Redis & Services run locally via PyCharm (ARM64)
- Python 3 with Miniconda3 → Conda env `mac_ki_service_py312`

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

**External API Docs:**
- **OLLAMA**: https://github.com/ollama/ollama/blob/main/docs/api.md
- **MUREKA**: https://platform.mureka.ai/docs/
- **OpenAI**: https://platform.openai.com/docs/api-reference/introduction

### 3. Ollama + Prompt Template Integration (MANDATORY WORKFLOW!)

**CRITICAL:** This is NOT a direct Ollama proxy - it's a **Template-Driven Generation System**.

**Mandatory Workflow (NO EXCEPTIONS!):**
```
User Input → Load Template from DB → Validate → Unified Endpoint → Response
```

**Rules:**
- **ALL** Ollama calls with templates **MUST** use `/api/v1/ollama/chat/generate-unified`
- **ALL** such operations **MUST** go through `ChatService` in the frontend
- **NEVER** implement direct Ollama API calls in new services
- **NEVER** use templates before they exist in DB (backend has no data!)

**Implementation:**

```typescript
// ✅ CORRECT: Simple case
async myNewFeature(input: string): Promise<string> {
  return this.chatService.validateAndCallUnified('category', 'action', input);
}

// ✅ CORRECT: Complex case (with custom logic)
async myComplexFeature(input: string, customParam: string): Promise<string> {
  // 1. Load template from DB
  const template = await firstValueFrom(
    this.promptConfig.getPromptTemplateAsync('category', 'action')
  );
  if (!template) {
    throw new Error('Template category/action not found in database');
  }

  // 2. Validate required fields
  if (!template.model || template.temperature === null || !template.max_tokens) {
    throw new Error('Template is missing required parameters');
  }

  // 3. Build request (can enhance pre_condition/post_condition here)
  const request: UnifiedChatRequest = {
    pre_condition: template.pre_condition + '\n' + customParam,
    post_condition: template.post_condition || '',
    input_text: input,
    temperature: template.temperature,
    max_tokens: template.max_tokens,
    model: template.model
  };

  // 4. Call unified endpoint
  const data = await firstValueFrom(
    this.http.post<ChatResponse>(
      this.apiConfig.endpoints.ollama.chatGenerateUnified,
      request
    )
  );
  return data.response;
}

// ❌ WRONG: Direct Ollama call (bypasses template system!)
async wrongImplementation(input: string): Promise<string> {
  return this.http.post('http://localhost:11434/api/generate', {
    model: 'llama2',  // ❌ Hardcoded, not from DB template!
    prompt: input     // ❌ No pre/post conditions from template!
  });
}

// ❌ WRONG: Custom endpoint (templates don't exist in DB yet!)
async wrongBackendCall(input: string): Promise<string> {
  return this.http.post('/api/v1/my-custom-ollama-endpoint', {
    prompt: input  // ❌ Backend has no template configuration!
  });
}
```

**Why this matters:**
1. **Templates MUST be in DB first** - backend loads config from `prompt_templates` table
2. **Centralized control** - all Ollama+Template calls go through one validated path
3. **Prevents Junior mistakes** - no ad-hoc Ollama integrations that bypass templates

**See also:**
- `aiwebui/src/app/services/config/chat.service.ts` - Reference implementation
- `aiproxysrv/src/api/routes/chat_routes.py` - Backend unified endpoint

---

### 4. JWT Authentication REQUIRED for ALL Backend APIs
- **ALL** backend endpoints (except login/register/health) **MUST** use `@jwt_required`
- User ID **MUST** be from JWT token via `get_current_user_id()`, **NOT** URL params
- **Why?** Prevents unauthorized access, URL manipulation

**Backend Example:**
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

**Exceptions (no JWT required):**
- `/api/v1/user/login`, `/api/v1/user/create`
- `/api/v1/health`, `/api/v*/celery-health`

**Frontend:** JWT token is **automatically** added via `authInterceptor`

---

## UI Patterns & Component Standards (CRITICAL!)

**MANDATORY:** All new UI components **MUST** follow standardized patterns documented in `docs/UI_PATTERNS.md`.

### Why This Matters

**NEVER** create custom button styles, layouts, or patterns without following the standards:
- ❌ Every new page with different button designs = inconsistent UX
- ❌ Custom styles = maintenance nightmare
- ✅ Reusable mixins = consistent, maintainable UI

### Standard Mixins (MANDATORY)

**ALWAYS use these button mixins** from `src/scss/_mixins.scss`:

```scss
.edit-button {
  @include button-secondary('base');  // Gray button
}

.delete-button {
  @include button-secondary('base');  // Gray button
}

.primary-action-button {
  @include button-primary('base');    // Blue button
}
```

**NEVER write custom button CSS:**
```scss
// ❌ WRONG: Custom styles
.my-button {
  background-color: #5a6268;
  color: white;
  padding: 8px 16px;
}
```

### Reference Implementation

**Equipment Gallery** (`aiwebui/src/app/pages/equipment-gallery/`) is the **current reference** for:
- ✅ Master-Detail Layout
- ✅ Button Standards (with mixins)
- ✅ Detail Actions Pattern
- ✅ Font Awesome Icons (NOT Material Icons)
- ✅ Form Layouts

### Quick Checklist for New Pages

Before implementing a new page:
- [ ] Review `docs/UI_PATTERNS.md` (COMPLETE documentation)
- [ ] Check Equipment Gallery implementation as reference
- [ ] Use `@include button-*` mixins for all buttons
- [ ] Use Font Awesome icons (`<i class="fas fa-*">`)
- [ ] Place actions in `detail-actions` section (NOT in list items)
- [ ] Follow Master-Detail Layout structure

**Full Documentation:** `docs/UI_PATTERNS.md`

---

## Architecture Principles (CRITICAL!)

### 3-Layer Architecture (MANDATORY for all new features)

**Separation of Concerns:**
```
Controller → Orchestrator → Transformer/Normalizer + Repository
(HTTP)       (Coordinates)  (Pure Functions)      (DB CRUD)
```

**Naming Convention (CRITICAL!):**

| File Pattern | Purpose | Testable? | Example |
|--------------|---------|-----------|---------|
| `*_orchestrator.py` | Coordinates services, NO business logic | ❌ No (only calls other services) | `SketchOrchestrator`, `SongOrchestrator` |
| `*_transformer.py` | Pure functions: transformations, mappings | ✅ Yes (100% coverage) | `SongMurekaTransformer`, `ApiCostTransformer` |
| `*_normalizer.py` | Pure functions: string normalization | ✅ Yes (100% coverage) | `SketchNormalizer` |
| `*_auth_service.py` | Pure functions: authentication logic | ✅ Yes (100% coverage) | `UserAuthService` |
| `*_enhancement_service.py` | Pure functions: enhancements | ✅ Yes (100% coverage) | `ImageEnhancementService` |
| `*_service.py` (in `db/`) | CRUD operations only | ❌ No (infrastructure) | `SketchService`, `SongService` |

**Layer Responsibilities:**

**1. Business Layer** (`src/business/`)
- **Orchestrators** (`*_orchestrator.py`): Coordinate services (NOT testable, no business logic)
- **Transformers/Normalizers**: Pure functions (100% unit-testable)
- ✅ Business logic, calculations, transformations (in transformers/normalizers)
- ✅ Pure functions (no DB, no file system)
- ✅ **MUST be unit-testable** without mocks (transformers/normalizers only)
- ❌ NO database queries
- ❌ NO file system operations

**2. Repository Layer** (`src/db/*_service.py`)
- ✅ CRUD operations only
- ✅ SQLAlchemy queries
- ❌ NO business logic
- ❌ NO transformations (use business layer)
- ❌ **NO unit tests** (pure CRUD, not testable without DB)

**3. Controller Layer** (`src/api/controllers/*_controller.py`)
- ✅ HTTP request/response handling
- ✅ Input validation (Pydantic)
- ✅ Call orchestrator or business services
- ❌ NO business logic
- ❌ NO direct DB queries

**Example (Images - CORRECT Pattern):**
```python
# ✅ CORRECT: Separation of Concerns
image_controller.py
  └─> image_orchestrator.py (coordinates services, NOT testable)
       ├─ Calls: image_enhancement_service.py (pure functions, 100% tested)
       ├─ Calls: file_management_service.py (infrastructure)
       └─> image_service.py (DB CRUD only, NO tests)

# Tests:
# - image_enhancement_service.py: 100% coverage (pure functions)
# - image_orchestrator.py: 0% coverage (orchestration, not testable)
# - image_service.py: 0% coverage (CRUD, no tests)
```

**Anti-Pattern (WRONG):**
```python
# ❌ WRONG: Business logic mixed with DB
class SomeService:
    def get_data(self, db: Session):
        result = db.query(...).first()  # DB query

        # ❌ Business logic in DB service!
        return {
            "total": float(result.total),  # Transformation
            "image": costs.get("image", 0)  # Defaults
        }
```

**Refactoring Guide:**

If you find business logic in `src/db/*_service.py`:
1. Create `src/business/*_transformer.py` for transformations
2. Extract pure functions (transformations, defaults, calculations)
3. Write unit tests for business layer
4. Keep DB layer as pure CRUD

**Checklist for NEW Services:**
- [ ] Business logic in `src/business/` (unit-testable)
- [ ] DB operations in `src/db/` (CRUD only, no tests)
- [ ] Controller calls business layer (no direct DB)
- [ ] Unit tests cover business logic (not infrastructure)

### Automated Architecture Validation (CRITICAL!)

**IMPORTANT:** Architecture rules are now **automatically enforced** via linters. Run these checks **BEFORE every commit**!

#### Python Backend (import-linter)

**Validates:**
- ❌ Controllers MUST NOT import DB services directly (use business layer)
- ❌ DB layer MUST NOT import business logic
- ❌ Business layer MUST NOT import SQLAlchemy directly
- ❌ Schemas MUST NOT depend on business/DB layers

**Run validation:**
```bash
# From aiproxysrv/ directory
lint-imports                    # Quick check
make lint-all                   # Ruff + import-linter
```

**Configuration:** `aiproxysrv/.importlinter`

**Common violations:**
```bash
# ERROR: Controllers must go through business layer, not directly to DB
src.api.controllers.foo_controller -> src.db.bar_service

# Fix: Use orchestrator as intermediary
src.api.controllers.foo_controller -> src.business.foo_orchestrator -> src.db.bar_service
```

#### Angular Frontend (dependency-cruiser)

**Validates:**
- ❌ Services MUST NOT depend on Components/Pages
- ❌ Services MUST use ApiConfigService (NOT environment.apiUrl)
- ❌ Models MUST NOT depend on Services/Components
- ❌ Guards/Interceptors MUST NOT depend on Components
- ❌ No circular dependencies

**Run validation:**
```bash
# From aiwebui/ directory
npm run lint:arch               # Architecture only
npm run lint:all                # TypeScript + SCSS + Architecture
```

**Configuration:** `aiwebui/.dependency-cruiser.js`

**Common violations:**
```bash
# ERROR: Services must use ApiConfigService, NOT environment.apiUrl
src/app/services/foo.service.ts -> environments/environment

# Fix: Inject ApiConfigService
private apiConfig = inject(ApiConfigService);
this.http.get(this.apiConfig.endpoints.category.action);
```

**Integration Tips for Claude Code:**
- When asked to "run lint", **ALWAYS include architecture checks** (`lint:all`, `make lint-all`)
- **Violations appear in lint output** - no manual review needed
- Fix violations **before marking tasks as completed**
- Architecture errors are **build blockers** (treat like ESLint errors)

---

## Angular 18 Modern Patterns

### Always use inject() for DI
- **ALWAYS** use `inject()` function instead of constructor injection
- Pattern: `private service = inject(ServiceName)`
- Avoids ESLint warning `@angular-eslint/prefer-inject`

### Use HttpClient (not fetch)
- Use Angular's `HttpClient` for all HTTP requests
- Enables JWT injection via interceptors

### Always run build + lint
**CRITICAL:** Always use `lint:all` to check BOTH TypeScript AND SCSS!

```bash
# From aiwebui directory
npm run build && npm run lint:all
```

**Available lint commands:**
- `npm run lint:all` - TypeScript + SCSS + Architecture (use this after changes!)
- `npm run lint` - TypeScript only (ESLint)
- `npm run lint:scss` - SCSS only (Stylelint)
- `npm run lint:arch` - Architecture validation only (dependency-cruiser)
- `npm run lint:scss:fix` - Auto-fix SCSS issues

---

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

### SCSS Architecture for NEW Components (CRITICAL!)

**New components (with `_NEW_` or `-new-` in filename) have STRICT rules enforced by Stylelint:**

**Rules:**
1. **BEM for custom elements** - Max 2 levels
   - `.feature__element`, `.feature__element--modifier`

2. **Material overrides** - Max 3 levels, ONLY for `mat-*`
   - `.feature mat-card mat-card-content { }` ✅

3. **NO custom nesting over 2 levels**
   - Use flat BEM classes instead of nesting

**Example:**
```scss
// ✅ CORRECT: BEM with max 2 levels
.product-list { }
.product-list__item { }
.product-list__item--active { }

// ✅ CORRECT: Material override max 3
.product-list {
  mat-card {                    // +1
    mat-card-content {          // +2
      padding: 1rem;            // Styling (no +3!)
    }
  }
}

// ❌ BUILD FAILS: Custom nesting over 2
.product-list {
  .content {
    .item {                     // ❌ ERROR: 3 custom levels
      .child { }
    }
  }
}
```

**Naming convention for strict rules:**
- `product-list-new.component.scss` ✅ Strict
- `_NEW_customer.component.scss` ✅ Strict
- `payment.component.scss` ⚠️ Warnings only

**Old components** are ignored by Stylelint to avoid breaking changes.

---

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

---

## Python Code Quality & Testing

### Logging (Loguru)
**IMPORTANT:** All backend code MUST use structured logging with context.

#### Rules
- **ALWAYS** use `logger` from `utils.logger`, **NEVER** `print()`
- **ALWAYS** use `from utils.logger import logger`, **NEVER** `import logging`
- **ALWAYS** provide context via extra fields (NOT in the message string)
- **ALWAYS** use human-readable messages (NOT `snake_case`)

**CRITICAL:** Using `import logging` instead of `from utils.logger import logger` will cause crashes when using structured logging parameters (e.g., `logger.info("Message", param=value)`). Standard Python logger does NOT support named parameters!

#### Patterns

```python
# ✅ CORRECT: Use Loguru logger from utils
from utils.logger import logger

logger.debug("Sketch retrieved", sketch_id=sketch_id, workflow=workflow, user_id=user_id)
logger.info("Song updated", song_id=song_id, fields_updated=list(update_data.keys()))
logger.warning("Template not found", category=category, action=action)
logger.error("Database error", error=str(e), error_type=type(e).__name__, sketch_id=sketch_id)

# ❌ WRONG: Standard Python logging (CRASHES with structured parameters!)
import logging
logger = logging.getLogger(__name__)
logger.info("Processing", task_id=task_id)  # TypeError: info() got unexpected keyword argument 'task_id'

# ❌ WRONG: Snake-case messages (unreadable)
logger.debug("sketch_retrieved_by_id", sketch_id=sketch_id)
logger.info("song_updated", song_id=song_id)

# ❌ WRONG: Context in message string (not parseable)
logger.debug(f"Sketch retrieved: {sketch_id}")
logger.info(f"Song updated with fields: {update_data.keys()}")

# ❌ WRONG: Using print()
print(f"Processing sketch {sketch_id}")
```

#### Log Levels
- **DEBUG:** Development details with all context fields (visible only in dev)
- **INFO:** Production events, message only (no context fields shown)
- **WARNING:** Unexpected conditions, message only
- **ERROR:** Failures with full context (multi-line format with error details)

#### Output Examples

**Development (LOG_LEVEL=DEBUG):**
```
DEBUG | Prompt template loaded category=image action=enhance model=llama3.2:3b temperature=0.7 max_tokens=500 version=1.0
DEBUG | Sketch retrieved sketch_id=395efa8b workflow=draft user_id=1
INFO  | Sketch updated
```

**Production (LOG_LEVEL=WARNING):**
```
WARNING | Template not found
ERROR   | Database error
  └─ Type: OperationalError
  └─ Error: connection timeout
  └─ sketch_id: 395efa8b
```

---

### Ruff (Linting & Formatting)
**IMPORTANT:** All Python code MUST pass Ruff before commits.

**CRITICAL: ALWAYS use `make` commands (NOT direct `ruff` calls)!**
- ✅ `make` validates Conda environment first (prevents errors)
- ✅ Runs architecture validation (`import-linter`) automatically
- ❌ Direct `ruff` calls skip environment checks and architecture validation

```bash
# From aiproxysrv directory
make lint-all                  # ✅ PREFERRED: Ruff + import-linter + Conda check
make format                    # ✅ PREFERRED: Format with environment check
make test                      # ✅ PREFERRED: pytest with environment check
make install-dev               # Install ruff + pre-commit

# ❌ DON'T use direct commands (skip environment + architecture validation):
# ruff check .
# ruff check . --fix
# ruff format .
```

**Available Makefile targets:**

**Code Quality:**
- `make check-conda` - Verify `mac_ki_service_py312` environment is active
- `make lint-ruff` - Ruff linter only (with Conda check)
- `make lint-imports` - Architecture validation only (with Conda check)
- `make lint-all` - All linters (Ruff + import-linter, with Conda check)
- `make format` - Auto-fix and format code (with Conda check)
- `make test` - Run pytest (with Conda check)
- `make install-dev` - Install development dependencies

**Database Migrations:**
- `make db-current` - Show current migration version
- `make db-upgrade` - Upgrade database to latest version
- `make db-downgrade` - Downgrade database by 1 revision
- `make db-revision` - Create new migration (prompts for message)
- `make db-history` - Show migration history
- `make db-heads` - Show head revisions

### pytest (Unit Testing)
**CRITICAL: Only test business logic, NEVER infrastructure!**

```bash
# From aiproxysrv directory
pytest                         # Run all tests
pytest -v -s                   # Verbose output
pytest tests/test_health.py    # Run specific file
pytest -k "test_name"          # Run tests matching pattern
pytest --cov=src               # Coverage report
```

**What to Test (CRITICAL RULES):**

❌ **DO NOT write tests for:**
- **Database services** (`src/db/*_service.py`) - Pure CRUD operations, no business logic
- **File system operations** - Infrastructure, not logic
- **External API clients** - Mock hell, no value
- **SQLAlchemy mocks** - Testing mock setup, not real behavior
- **Controllers with only DB calls** - Integration tests, not unit tests

✅ **DO write tests for:**
- **Business logic services** (`src/business/*_service.py`) - Pure functions, calculations
- **Validation logic** - HTTP status codes, error messages
- **Utilities** - String manipulation, data transformations, calculations
- **Complex algorithms** - Anything with conditional logic

**Example:**
```python
# ❌ BAD: Testing DB service (no business logic, only CRUD)
class TestApiCostService:
    def test_get_cached_month(self, mock_db_session):
        # Testing SQLAlchemy mock setup = USELESS!
        # If DB schema changes, test breaks but gives no safety
        mock_db_session.query().filter().first()

# ✅ GOOD: Testing business logic (pure function)
class TestImageEnhancementService:
    def test_hex_to_rgb_conversion(self):
        # Real logic, no infrastructure
        assert hex_to_rgb("#FF5733") == (255, 87, 51)
```

**When to Write Tests:**
- **New Features**: Write tests for business logic only
- **Bug Fixes**: Add test case that reproduces the bug (if logic-related)
- **Refactoring**: Extend existing tests if logic changes

---

## General Don'ts

- ❌ NEVER commit `.env` to repo
- ❌ NEVER use emojis (unless explicitly requested)
- ❌ NEVER create unnecessary markdown files
- ❌ NEVER skip linting before commits
- ❌ NEVER skip unit tests before commits

---

# Development Workflow

## Quick Commands

### Frontend (aiwebui)
```bash
npm run dev                    # Development server
npm run build:prod             # Production build → forwardproxy/html/aiwebui
npm run lint:all               # TypeScript + SCSS (use this!)
npm run lint                   # TypeScript only (ESLint)
npm run lint:scss              # SCSS only (Stylelint)
npm run test                   # Unit tests
```

### Backend (aiproxysrv)
```bash
# Activate conda environment
conda activate mac_ki_service_py312

# Development Server
python src/server.py

# Database Migrations (ALWAYS use make!)
make db-current                # Show current version
make db-upgrade                # Apply all pending migrations
make db-downgrade              # Rollback 1 revision
make db-revision               # Create new migration (prompts for message)
make db-history                # Show migration history
make db-heads                  # Show head revisions

# Celery Worker
python src/worker.py
celery -A src.worker flower    # Monitor (http://localhost:5555)

# Code Quality (ALWAYS use make!)
make lint-all                  # ✅ Ruff + import-linter + Conda check
make format                    # ✅ Auto-fix and format with checks
make test                      # ✅ pytest with Conda check
make check-conda               # Verify correct environment

# ❌ DON'T use: ruff check . --fix && ruff format .
# ❌ DON'T use: pytest -v -s
# ❌ DON'T use: alembic upgrade head (use make db-upgrade)
```

### Database Seeding
```bash
# From project root (mac_ki_service/)
# IMPORTANT: All seed scripts are SQL-based (not Python) for Docker compatibility

# Seed Prompt Templates
cat scripts/db/seed_prompts.sql | docker exec -i postgres psql -U aiproxy -d aiproxysrv

# Seed Image Fast Enhancement Template
cat scripts/db/seed_prompts_image_fast.sql | docker exec -i postgres psql -U aiproxy -d aiproxysrv

# Seed Lyric Parsing Rules
cat scripts/db/seed_lyric_parsing_rules.sql | docker exec -i postgres psql -U aiproxy -d aiproxysrv

# Local PostgreSQL (without Docker)
psql -h localhost -U aiproxy -d aiproxysrv -f scripts/db/seed_prompts.sql
```

**DB Credentials** (from `aiproxysrv/.env_postgres`):
- **Service**: `postgres`, **DB**: `aiproxysrv`, **User**: `aiproxy`, **Password**: `aiproxy123`

### Docker
```bash
# From project root
docker compose up postgres     # Development (PostgreSQL only)
docker compose logs -f         # View logs
docker compose ps              # Check containers
```

---

## Testing Strategy

### Mock API (aitestmock)
Testing without external API costs:
- Image: `"0001"` → OK, `"0002"` → Error
- Song: `"0001"` → OK, `"0002"` → Error, `"30s"` → 30s delay

### Frontend Testing
```bash
# From aiwebui/
npm run test -- --watch       # Unit tests
npm run e2e                   # E2E tests
```

---

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
5. **Missing JWT protection**: Unprotected API endpoints
6. **Architecture violations**: Business logic in DB layer (Code Review catches this)

### Both
1. **Ignoring linter warnings**: ESLint/Stylelint/Ruff errors
2. **Not testing language switch**: Only testing in one language
3. **Committing `.env`**: Security breach!
4. **Skipping builds/tests**: Not running validation before commits

---

# Additional Documentation

- **UI Patterns**: `docs/UI_PATTERNS.md` **(CRITICAL - Read before creating new pages!)**
- **Architecture Details**: `docs/ARCHITECTURE.md` → Links to `docs/arch42/README.md` (arc42 template with diagrams, DB schema, API endpoints)
- **Code Patterns**: `docs/CODE_PATTERNS.md` (Complete code examples)
- **Troubleshooting**: `docs/TROUBLESHOOTING.md` (Debug commands, common issues)
- **CI/CD**: `docs/CI_CD.md` (GitHub Actions, build pipeline)
