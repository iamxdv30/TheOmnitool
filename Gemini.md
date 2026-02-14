# Gemini.md

This file provides context and guidance for Gemini when working with the "MyTools" (The Omnitool) repository.

## Project Identity
**Name:** MyTools (The Omnitool)
**Type:** Hybrid Web Application (Flask Monolith + Modernizing Next.js Frontend)
**Purpose:** A suite of utility tools (Tax calculators, Character counters, etc.) with role-based access control (RBAC).

## Tech Stack

### Backend (Core)
- **Language:** Python 3.x
- **Framework:** Flask 3.0.3 (App Factory Pattern)
- **ORM:** SQLAlchemy 2.0 (w/ Single Table Inheritance for Users)
- **Migrations:** Flask-Migrate / Alembic
- **Template Engine:** Jinja2 (using `ChoiceLoader`)
- **Testing:** Pytest

### Frontend (Legacy / Current Main)
- **Rendering:** Server-Side Rendered (Jinja2)
- **Styling:** CSS (in `static/css`)
- **Scripting:** Vanilla JS / jQuery (in `static/js`)

### Frontend (Modern / Production Ready)
- **Location:** `frontend/` directory
- **Framework:** Next.js 16 (App Router)
- **Library:** React 19
- **State:** Zustand v5 (with persist middleware)
- **API Client:** Custom fetch wrapper with CSRF & interceptors
- **Styling:** Tailwind CSS v4
- **3D Engine:** React Three Fiber (R3F) + Drei + Rapier (Physics)
- **Testing:** Jest + React Testing Library (31 tests passing)
- **Migration Status:** Phase 5 Complete ✅ (Production Deployment)
- **Deployment:** Dual-stack on single Heroku dyno (Flask + Next.js)

### Database
- **Local (Recommended):** Docker PostgreSQL (`docker-compose up -d postgres`)
  - Provides database parity with staging/production
  - Connection: `postgresql://omnitool:omnitool_dev@localhost:5432/omnitool_dev`
  - Enable with: `USE_DOCKER_DB=true` in `.env`
  - **CRITICAL:** Never set `DATABASE_URL` as system environment variable (overrides `.env`)
  - **Dependency:** Requires `psycopg2-binary==2.9.11` (installed via `pip install psycopg2-binary`)
- **Local (Fallback):** SQLite (`users.db`) - Not recommended due to migration issues
- **Staging/Production:** PostgreSQL (Heroku)
- **Tests:** In-memory SQLite (fast, isolated)
- **Safety:** Automatic backups via `utils/db_safety.py` (SQLite binary or JSON for PostgreSQL)
- **Backup Scripts:** `scripts/export_all_data.py` and `scripts/import_all_data.py`
- **Migration Script:** `scripts/migrate_sqlite_to_postgres.py` (one-time SQLite → PostgreSQL migration)

## Critical Workflows

### 1. Running the Application
*   **Backend (Flask only):**
    ```bash
    python main.py
    ```
*   **Frontend (Next.js dev):**
    ```bash
    cd frontend
    npm run dev
    ```
*   **Full Stack (Local Development):**
    ```bash
    # Terminal 1: Flask backend
    python main.py

    # Terminal 2: Next.js frontend
    cd frontend && npm run dev
    ```
*   **Production (Heroku - dual-stack):**
    ```bash
    ./scripts/start-production.sh
    ```

### 2. Database Management
**CRITICAL:** This project emphasizes database safety. Backups are automatic.

**Docker PostgreSQL Setup (First-Time)**:
```bash
# 1. Install PostgreSQL adapter
pip install psycopg2-binary

# 2. Start Docker PostgreSQL container
.\scripts\docker-db.ps1 start   # Windows
./scripts/docker-db.sh start    # Linux/Mac

# 3. Verify .env configuration
# USE_DOCKER_DB=true
# DATABASE_URL='postgresql://omnitool:omnitool_dev@localhost:5432/omnitool_dev'

# 4. Create schema (empty tables)
python migrate_db.py

# 5. (Optional) Migrate existing SQLite data
python scripts/migrate_sqlite_to_postgres.py --export
python scripts/migrate_sqlite_to_postgres.py --import
python scripts/migrate_sqlite_to_postgres.py --verify
```

**Daily Database Operations**:
*   **Apply Migrations:** `flask db upgrade`
*   **Create Migration:** `flask db migrate -m "message"`
*   **Safe Migration Wrapper (Recommended):** `python migrate_db.py` (Performs backup -> migrate -> upgrade)
*   **Restore Backup:** `python restore_backup.py`
*   **Export Data (JSON):** `python scripts/export_all_data.py --output data/backups/backup.json`
*   **Import Data (JSON):** `python scripts/import_all_data.py --source data/backups/backup.json`
*   **Initialize Tools:** `python tool_management.py`
*   **Seed Dashboard Data:** `python scripts/seed_phase1_dashboard_data.py` (categories, plans, billing cycles, providers, Pro subscriptions)

**Migration & Deployment Scripts**:
*   **Sync tool definitions:** `python sync_tools.py`
*   **Export tool access:** `python scripts/export_tool_access.py --env local`
*   **Import tool access:** `python scripts/import_tool_access.py --source data/tool_access_exports/local_tool_access.json --mode merge`
*   **Verify migration:** `python scripts/verify_migration.py --env local`
*   **Emergency rollback:** `python scripts/rollback_migration.py --env staging`
*   **Smoke tests:** `python tests/smoke_tests.py --url <target_url>`

### 3. Testing

**Backend Tests (pytest):**
```bash
pytest                                        # Run all
pytest --cov=. --cov-report=html             # With coverage
pytest tests/test_routes.py                  # Specific file
pytest tests/test_routes.py::test_function   # Specific test
```

**Frontend Tests (Jest):**
```bash
cd frontend
npm test                        # Run all (31 unit tests)
npm test -- --coverage          # With coverage
npm test -- --watch             # Watch mode
npm test -- authStore.test.ts   # Specific file
```

**Smoke Tests:** `python tests/smoke_tests.py --url <target_url>`

**Current Coverage:**
*   Backend: pytest tests for routes, models, services
*   Frontend: 31 unit tests passing (`authStore.test.ts`, `uiStore.test.ts`, `csrf.test.ts`)

**Test Fixtures** (`tests/conftest.py`):
*   `app` - Flask test app with in-memory SQLite
*   `client` - Test client for requests
*   `init_database` - Pre-populated test data
*   `logged_in_user`, `logged_in_admin`, `logged_in_superadmin` - Authenticated sessions
*   Import models via `from model import User, Admin, Tool, ToolCategory, ToolFavorite, SubscriptionPlan, UserSubscription, etc.`
*   CSRF is disabled in test config

## Architecture Summary

### Application Factory Pattern
*   `main.py`: Contains `create_app()` factory function.
*   Blueprints are registered in the factory.
*   Database and migrations initialized via factory.

### Backend (`/`)
*   **Entry Point:** `main.py` (App factory, logging config, security headers, template loader).
*   **Models (`model/`):**
    *   `base.py` - Core database instance (`db`) and Strategy Pattern for password hashing (`PasswordHasher` → `BcryptPasswordHasher`).
    *   `users.py` - Single Table Inheritance (`User` → `Admin` → `SuperAdmin`), polymorphic on `role` column.
    *   `tools.py` - Tool management, access control, categories, and favorites:
        *   `Tool` (with `icon`, `display_name`, `category_id`, `is_paid`, `required_plan_id`)
        *   `ToolAccess` - Junction table for user-tool permissions
        *   `ToolCategory` - Admin-manageable categories (Finance, Dev, Writing, Marketing)
        *   `ToolFavorite` - User-tool favorites with unique constraint
        *   `UsageLog` - Tracks tool usage per user
        *   `EmailTemplate` - User-specific email templates
    *   `subscription.py` - Subscription and payment models (provider-agnostic):
        *   `SubscriptionPlan` - Plan definitions (Free/Basic/Pro) with tier levels
        *   `UserSubscription` - User-plan assignments with status, billing cycle, expiry
        *   `BillingCycle` - Billing periods (monthly/yearly/lifetime)
        *   `PaymentProvider` - Payment gateway registry (Stripe, PayPal, etc.)
    *   `auth.py` - Factory Pattern (`UserFactory.create_user()`) for role-based user creation.
    *   `__init__.py` - Backward compatibility layer, exports all models for easy importing.

*   **Routes (`routes/`):**
    *   **Legacy (Jinja template-rendered):**
        *   `auth_routes.py` - Login, logout, registration, password reset
        *   `user_routes.py` - User dashboard, profile management
        *   `admin_routes.py` - Admin dashboard, user management
        *   `tool_routes.py` - Tool-specific routes (tax calculators, email templates, etc.)
        *   `contact_routes.py` - Contact form with Flask-Mail integration
    *   **Modern API (JSON, for Next.js frontend) — `routes/api/`:**
        *   `__init__.py` - API blueprint (`/api/v1`), response helpers (`api_response`, `api_error`), decorators (`@require_auth`, `@require_verified`, `@require_role`)
        *   `auth_api.py` - `/api/v1/auth/*` — login, logout, register, CSRF, password reset, email verification
        *   `user_api.py` - `/api/v1/user/*` — profile, password, email, tools, usage, favorites, dashboard
        *   `tool_api.py` - `/api/v1/tools/*` — list tools, tax calculator, character counter, email templates CRUD
        *   `schemas.py` - Marshmallow validation schemas for all API inputs

*   **Service Layer (`services/`):**
    Business logic separated from HTTP concerns. Routes call services; services handle DB queries, validation, and computation.
    *   `base.py` - `ServiceResult[T]` pattern (`.is_success`, `.is_failure`, `.data`, `.error`), `ErrorCode` enum, `BaseService` class
    *   `auth_service.py` - Login, registration, password reset, email verification logic
    *   `user_service.py` - Profile management, dashboard data assembly (`DashboardData`)
    *   `tool_service.py` - Tool access, favorites (CRUD), tax calc, character counter, email templates
    *   `email_service.py` - Flask-Mail email sending
    *   `token_service.py` - Token generation and validation
    *   Services are singletons accessed via `get_*_service()` factory functions (e.g., `get_tool_service()`).

*   **Tool Logic (`Tools/`):** Contains standalone computation modules (e.g., `tax_calculator.py`, `char_counter.py`) and Jinja2 templates. Services import from here; legacy routes call directly.
*   **Templates:** Managed via `ChoiceLoader` searching in `Tools/templates/` then `templates/`.

### Design Patterns in Use
1.  **Factory Pattern** (`model/auth.py`) - `UserFactory.create_user()` centralizes user object creation.
2.  **Strategy Pattern** (`model/base.py`) - `PasswordHasher` abstract class with swappable implementations.
3.  **Single Table Inheritance** (`model/users.py`) - User, Admin, SuperAdmin share `users` table, polymorphic on `role`.
4.  **Service Result Pattern** (`services/base.py`) - All service methods return `ServiceResult[T]`, routes stay thin.

### Frontend (`frontend/`)
*   **Structure:** Next.js App Router (`src/app`) with route groups:
    *   `(public)/` - No auth required (landing, contact)
    *   `(auth)/` - Auth pages (login, register, forgot-password)
    *   `(dashboard)/` - Protected routes (dashboard, profile, tools)
*   **UI Components:** Shadcn-like structure in `src/components/ui`.
*   **View Tunneling:** Uses `<SceneView />` to render 3D R3F content from the DOM into a global shared Canvas.
*   **State Management:**
    *   `authStore.ts` - User authentication (login, logout, session)
    *   `uiStore.ts` - UI state (toasts, modals, sidebar collapse)
    *   `useStore.ts` - Theme persistence (localStorage)
*   **API Layer:**
    *   `lib/api/client.ts` - Base fetch wrapper with interceptors
    *   `lib/api/auth.ts` - Auth endpoint wrappers
    *   `lib/api/csrf.ts` - CSRF token management with caching
    *   `lib/api/tools.ts` - Tools API client (tax calc, email templates)
*   **Route Protection:** `middleware.ts` validates session cookies server-side
*   **Session Polling:** `useSessionPolling.ts` checks auth status every 5 minutes
*   **Health Endpoint:** `src/app/api/health/route.ts` - Checks Flask + Next.js status

## Key Features & Workflows

### Role-Based Access Control
*   **User**: Basic tool access based on ToolAccess permissions.
*   **Admin**: Can manage regular users and grant/revoke tool access.
*   **SuperAdmin**: Can manage all users including admins, change roles.
*   Check access: `User.user_has_tool_access(user_id, tool_name)` or `user.has_tool_access(tool_name)`.

### Tool Access System
Default tools are automatically assigned to new users:
*   Tax Calculator
*   Canada Tax Calculator
*   Character Counter
*   Email Templates

Non-default tools require explicit admin grant.

### Dashboard Redesign (In Progress)
See [docs/dashboard-redesign-679c76.md](docs/dashboard-redesign-679c76.md) for full implementation plan.
*   **Phase 1** (DB Schema): ✅ Complete — categories, subscriptions, favorites, payment providers, billing cycles
*   **Phase 2** (API Endpoints): In progress — 2A Favorites API complete, 2B-2G pending
*   **Phases 3-7** (Frontend): Pending

### User Creation Flow
1.  Use `UserFactory.create_user()` with role parameter.
2.  Password is set automatically within factory.
3.  For new users, call `User.assign_default_tools(user_id)` to grant default tool access.

### Session Security
*   Sessions expire on browser close (`SESSION_PERMANENT=False`).
*   30-minute backup timeout.
*   HTTPS-only cookies in production.
*   CSRF protection via `SESSION_COOKIE_SAMESITE='Lax'`.

### Email System
Flask-Mail integration for password reset, email verification, and contact form submissions. Configuration in `routes/contact_routes.py` via `configure_mail()`.

## Environment Configuration

### Local Development
Set in `.env` file:
*   `IS_LOCAL=true` - Enables local development mode
*   `FLASK_ENV=development` - Development environment
*   `SECRET_KEY` - Session secret key
*   `SECURITY_PASSWORD_SALT` - For password reset tokens
*   `TOKEN_SECRET_KEY` - For verification tokens

Database: SQLite (`sqlite:///users.db`) or Docker PostgreSQL (recommended).

### Production (Heroku)
*   `IS_LOCAL=false` or unset
*   `DATABASE_URL` - PostgreSQL connection string (auto-provided by Heroku)
*   HTTPS enforcement and security headers enabled

## Development Conventions

1.  **Imports:** Use absolute imports (e.g., `from model import User`).
2.  **Passwords:** ALWAYS use `user.set_password("...")`.
3.  **Authentication:** Includes reCAPTCHA verification and strict email verification (enforced in `auth_routes.py`).
4.  **Logging:** Centralized in `main.py`. Uses `TimedRotatingFileHandler` (daily, 30-day retention) and a `NoiseFilter` to exclude verbose library logs.
5.  **Security:** Production environment enforces HTTPS and adds HSTS and CSP headers.
6.  **Version:** Tracked in the root `VERSION` file, injected into templates via context processor.

## Common Gotchas
1.  **Circular imports**: Models use local imports within methods to avoid circular dependencies.
2.  **Password handling**: Always use `user.set_password()`, never set `user.password` directly.
3.  **Tool names**: Must match exactly between `Tool.name` and `ToolAccess.tool_name`.
4.  **Role changes**: SuperAdmin can change roles, but this creates new User objects (not in-place updates).
5.  **Template loading**: Both `templates/` and `Tools/templates/` are searched via ChoiceLoader.

## Key Files Map

### Backend
*   `main.py`: App factory, logging, and middleware.
*   `model/users.py`: RBAC and user hierarchy (STI).
*   `model/tools.py`: Tool, ToolAccess, ToolCategory, ToolFavorite, UsageLog, EmailTemplate.
*   `model/subscription.py`: SubscriptionPlan, UserSubscription, BillingCycle, PaymentProvider.
*   `model/auth.py`: UserFactory for role-based user creation.
*   `routes/api/`: JSON API endpoints (auth_api, user_api, tool_api).
*   `services/`: Business logic layer (auth_service, user_service, tool_service, email_service, token_service).
*   `routes/tool_routes.py`: Legacy HTML routes for tools.
*   `Tools/tax_calculator.py`: Core math logic for US, Canada, and VAT calculations.
*   `utils/db_safety.py`: Database validation and backup logic.
*   `.github/workflows/`: CI/CD pipelines for production and staging (dual-stack deployment).
*   `scripts/start-production.sh`: Dual-process startup script (Flask + Next.js).
*   `scripts/seed_phase1_dashboard_data.py`: Seeds categories, plans, billing cycles, providers.

### Frontend (Next.js)
*   `frontend/src/app/(public)/page.tsx`: Landing page.
*   `frontend/src/app/(auth)/login/page.tsx`: Login page with query param handling.
*   `frontend/src/app/(dashboard)/layout.tsx`: Dashboard layout with collapsible sidebar.
*   `frontend/src/app/api/health/route.ts`: Health check endpoint (Flask + Next.js status).
*   `frontend/src/middleware.ts`: Route protection (session validation).
*   `frontend/src/store/authStore.ts`: Authentication state management.
*   `frontend/src/store/uiStore.ts`: UI state (toasts, modals, sidebar).
*   `frontend/src/lib/api/client.ts`: API client with CSRF and interceptors.
*   `frontend/src/lib/api/tools.ts`: Tools API client (tax calc, email templates).
*   `frontend/src/__tests__/`: Jest unit tests (31 passing).

### Documentation
*   `docs/BACKEND_FRONTEND_INTEGRATION_PLAN.md`: Migration strategy (Phase 5 complete)
*   `docs/DATABASE_SAFETY.md`: Database safety system and troubleshooting
*   `docs/DEVELOPMENT_WORKFLOW.md`: Complete dev → staging → production pipeline
*   `docs/QUICK_START.md`: Quick reference for daily workflows
*   `CLAUDE.md`: Context for Claude Code AI agent.
*   `Gemini.md`: Context for Gemini AI agent (this file).
*   `MEMORY.md`: Development learnings and common issues.

## Common Issues & Troubleshooting

### Issue 1: "No module named 'psycopg2'"
**Symptom:** Migration fails with `ModuleNotFoundError: No module named 'psycopg2'`

**Cause:** PostgreSQL adapter not installed.

**Solution:**
```bash
pip install psycopg2-binary
```

**Note:** This package is already in `requirements.txt` as `psycopg2-binary==2.9.11`.

---

### Issue 2: Malformed DATABASE_URL (e.g., "172530@localhost")
**Symptom:**
- Error: `could not translate host name "172530@localhost" to address`
- Connection string shows: `postgresql://postgres:iamxdv@172530@localhost/omnitool`
- Expected format: `postgresql://omnitool:omnitool_dev@localhost:5432/omnitool_dev`

**Cause:** System environment variables overriding `.env` file.

**Diagnosis:**
```bash
python -c "import os; print(os.environ.get('DATABASE_URL', 'NOT SET'))"
```

**Solution:**
1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Advanced tab → Environment Variables
3. Delete `DATABASE_URL` and `DATABASE_URL_LOCAL` from User variables
4. **Restart VSCode completely** (restarting terminal is NOT enough)
5. Verify: `echo $DATABASE_URL` should be empty

**Temporary Workaround:**
```bash
export DATABASE_URL='postgresql://omnitool:omnitool_dev@localhost:5432/omnitool_dev'
python migrate_db.py
```

**Root Cause:** Python's `python-dotenv` library doesn't override existing environment variables. System environment variables always take precedence over `.env` file.

---

### Issue 3: Docker PostgreSQL Not Accessible
**Symptom:** `could not connect to server` or `Connection refused`

**Diagnosis:**
```bash
# Check container status
docker ps --filter "name=omnitool-postgres"

# Verify PostgreSQL is ready
docker exec omnitool-postgres pg_isready -U omnitool -d omnitool_dev
```

**Solutions:**
```bash
# Start container if not running
.\scripts\docker-db.ps1 start   # Windows
./scripts/docker-db.sh start    # Linux/Mac

# Check logs
docker logs omnitool-postgres

# Reset if corrupted (WARNING: destroys data)
.\scripts\docker-db.ps1 reset
python migrate_db.py
```

---

### Issue 4: "Schema invalid - missing tables"
**Symptom:** Application warns about missing database tables on startup.

**Solution:**
```bash
python migrate_db.py
```

This creates all required tables via Alembic migrations.

---

## Database Migrations

Using Flask-Migrate (Alembic):
1.  Make model changes in `model/` files.
2.  Generate migration: `flask db migrate -m "description"`
3.  Review migration in `migrations/versions/`
4.  Apply: `flask db upgrade`

### Production Migration Safety

The CI/CD pipeline (`.github/workflows/deploy.yml`) implements automatic rollback on migration failure:
1.  **Backup Phase**: Full PostgreSQL backup created before any changes.
2.  **Migration Phase**: `flask db upgrade` runs with error tracking.
3.  **Success Path**: Migration verified, data counts reported to Discord.
4.  **Failure Path**: Automatic rollback from backup dump file (zero manual intervention).

**Key Safety Features**:
*   Migrations only ADD columns with defaults (never delete data).
*   Full database dump (`.dump`) used for rollback, not CSV.
*   Automatic restoration triggered immediately on failure.
*   Backup artifacts retained for 30 days.
*   Users experience zero downtime during rollback.

## Production Deployment (Heroku)

### Dual-Stack Architecture
The application runs Flask (Gunicorn) and Next.js on a single Heroku dyno:
- **Flask:** Background process on port 5000 (internal)
- **Next.js:** Foreground process on `$PORT` (Heroku-assigned)
- **Proxy:** Next.js rewrites `/api/*` to Flask backend

### Health Check Endpoints
```bash
# Flask health
curl https://your-app.herokuapp.com/health/ping

# Next.js + Flask combined health
curl https://your-app.herokuapp.com/api/health
```

### Buildpacks (Order Matters)
```bash
heroku buildpacks:add heroku/python   # First
heroku buildpacks:add heroku/nodejs   # Second
```

### Required Environment Variables
```bash
FLASK_API_URL=http://127.0.0.1:5000
NEXT_PUBLIC_APP_URL=https://your-app.herokuapp.com
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_SAMESITE=Lax
SESSION_COOKIE_HTTPONLY=true
```