# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MyTools (The Omnitool) is a Flask-based web application providing various utility tools (tax calculators, character counter, email templates, etc.) with role-based access control. Current version: 1.4.0

## Development Commands

### Running the Application
```bash
# Local development
python main.py

# Production (via Heroku)
gunicorn main:app
```

### Database Management
```bash
# Run database migrations (WITH AUTOMATIC BACKUP)
python migrate_db.py

# Create a new migration after model changes
flask db migrate -m "migration message"

# Restore database from backup
python restore_backup.py

# Check database health
curl http://localhost:5000/health

# Initialize tools in database
python tool_management.py
```

### Database Safety Features 🛡️

**Automatic Protection:**
- ✅ Pre-migration backups (automatic)
- ✅ Schema validation on startup
- ✅ Health check endpoints
- ✅ Recovery utilities

**Backup Locations:**
- Primary: `zzDumpfiles/SQLite Database Backup/users.db`
- Pre-migration: `zzDumpfiles/SQLite Database Backup/users.db.backup_pre_migration_*`
- Pre-restore: `instance/users.db.before_restore_*`

**Health Check Endpoints:**
```bash
# Comprehensive health check
curl http://localhost:5000/health

# Simple ping
curl http://localhost:5000/health/ping

# Detailed database status
curl http://localhost:5000/health/database
```

**Troubleshooting Database Issues:**

1. **Database not initialized:**
   ```bash
   python migrate_db.py
   ```

2. **Data lost or corrupted:**
   ```bash
   python restore_backup.py
   ```

3. **Check what's wrong:**
   ```bash
   curl http://localhost:5000/health
   # Or check logs: logs/app.log
   ```

4. **Migration failed:**
   - Backup is automatically created before migration
   - Check error message in console
   - Restore from backup if needed
   - Fix migration issue and try again

### Testing

#### Backend Tests (pytest)
```bash
# Run all backend tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_routes.py

# Run specific test
pytest tests/test_routes.py::test_function_name
```

#### Frontend Tests (Jest)
```bash
# Navigate to frontend
cd frontend

# Run all frontend tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch

# Run specific test file
npm test -- authStore.test.ts
```

**Current Test Coverage:**
- Backend: pytest tests for routes, models, services
- Frontend: 31 unit tests passing
  - `authStore.test.ts` - Auth state management
  - `uiStore.test.ts` - UI state (toasts, modals, sidebar)
  - `csrf.test.ts` - CSRF token management

### Migration Scripts

```bash
# Sync tool definitions (add/rename/delete tools)
python sync_tools.py

# Export tool access permissions (after granting/revoking access)
python scripts/export_tool_access.py --env local

# Import tool access permissions (to staging/production)
python scripts/import_tool_access.py --source data/tool_access_exports/local_tool_access.json --mode merge

# Verify migration success
python scripts/verify_migration.py --env local

# Emergency rollback from backup
python scripts/rollback_migration.py --env staging
python scripts/rollback_migration.py --env production --backup b123

# Post-deployment smoke tests
python tests/smoke_tests.py --url https://omnitool-by-xdv-staging.herokuapp.com

# Sync production data to staging (requires Heroku Standard tier)
python scripts/sync_data_prod_to_staging.py
```

**📚 Complete Workflow Guide**: See [docs/DEVELOPMENT_WORKFLOW.md](docs/DEVELOPMENT_WORKFLOW.md) for detailed step-by-step instructions

## Architecture

### Application Factory Pattern
- `main.py`: Contains `create_app()` factory function
- Blueprints are registered in the factory
- Database and migrations initialized via factory

### Model Architecture (Modular Design)
Located in `model/` directory with the following structure:

- **`base.py`**: Core database instance and Strategy Pattern for password hashing
  - `db` - SQLAlchemy instance
  - `PasswordHasher` - Abstract base class (Strategy Pattern)
  - `BcryptPasswordHasher` - Concrete password hasher implementation

- **`users.py`**: User hierarchy using Single Table Inheritance
  - `User` - Base user class with polymorphic identity
  - `Admin` - Extends User with admin capabilities
  - `SuperAdmin` - Extends Admin with full system control
  - Role differentiation via `role` column and `polymorphic_identity`

- **`tools.py`**: Tool management and access control
  - `Tool` - Available tools registry
  - `ToolAccess` - Junction table for user-tool permissions
  - `UsageLog` - Tracks tool usage per user
  - `EmailTemplate` - User-specific email templates

- **`auth.py`**: Factory Pattern for user creation
  - `UserFactory.create_user()` - Creates User/Admin/SuperAdmin based on role parameter

- **`__init__.py`**: Backward compatibility layer - exports all models for easy importing

### Design Patterns in Use

1. **Factory Pattern** (`model/auth.py`)
   - `UserFactory.create_user()` centralizes user object creation
   - Handles role-based instantiation (User/Admin/SuperAdmin)

2. **Strategy Pattern** (`model/base.py`)
   - `PasswordHasher` abstract class with `BcryptPasswordHasher` implementation
   - Allows swapping password hashing algorithms without changing user code

3. **Single Table Inheritance** (`model/users.py`)
   - User, Admin, SuperAdmin share `users` table
   - Polymorphic on `role` column
   - Admins table and super_admins table extend via foreign keys

### Routes Structure
Organized as Flask blueprints in `routes/`:

- `auth_routes.py` - Login, logout, registration, password reset
- `user_routes.py` - User dashboard, profile management
- `admin_routes.py` - Admin dashboard, user management
- `tool_routes.py` - Tool-specific routes (tax calculators, email templates, etc.)
- `contact_routes.py` - Contact form with Flask-Mail integration

### Frontend Architecture (Legacy)
JavaScript organized by purpose in `static/js/`:

- **`modules/`** - Reusable functionality
  - `ui.js` - UI utilities and theme management
  - `forms.js` - Form handling and validation
  - `ajax.js` - AJAX request wrappers

- **`pages/`** - Page-specific logic
  - Each page has its own JS file (e.g., `admin_dashboard.js`, `tax_calculator.js`)

- **`utils/`** - Shared utilities
  - `theme.js` - Dark/light mode toggle
  - `search.js` - Reusable search with pagination
  - `email.js` - Email template functionality
  - `common.js` - Common utilities

### Modern Frontend (Next.js 16 + React Three Fiber)

Located in `frontend/` directory - a high-performance 3D application using the "Solarpunk High-Tech" design system.

**Migration Status:** Phase 3 (Frontend Authentication & State Management) ✅ **COMPLETE**
- See [docs/BACKEND_FRONTEND_INTEGRATION_PLAN.md](docs/BACKEND_FRONTEND_INTEGRATION_PLAN.md) for full migration strategy

#### Tech Stack
| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | Next.js 16 (App Router) | Server Components, Turbopack |
| 3D Engine | React Three Fiber v9 | Declarative Three.js |
| 3D Helpers | @react-three/drei | View tunneling, GLB loading |
| Physics | @react-three/rapier | WASM-based physics |
| State | Zustand (v5) | Auth, UI, theme state management |
| API Client | Custom fetch wrapper | CSRF protection, 401/403 interceptors |
| Styling | Tailwind CSS v4 | Zero-runtime CSS |
| Icons | Lucide React | Tree-shakeable icons |
| Testing | Jest + React Testing Library | 31 unit tests |

#### Development Commands
```bash
# Navigate to frontend
cd frontend

# Development server
npm run dev

# Production build
npm run build

# Start production server
npm start

# Run tests
npm test

# Type checking
npm run lint
```

#### Directory Structure
```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── (public)/           # Public route group (no auth)
│   │   │   ├── layout.tsx      # Public layout with header
│   │   │   ├── page.tsx        # Landing page
│   │   │   └── contact/        # Contact page
│   │   ├── (auth)/             # Auth route group
│   │   │   ├── login/          # Login page (with query param handling)
│   │   │   ├── register/       # Registration page
│   │   │   ├── forgot-password/
│   │   │   └── reset-password/
│   │   ├── (dashboard)/        # Protected route group
│   │   │   ├── layout.tsx      # Dashboard layout with sidebar
│   │   │   ├── dashboard/      # User dashboard
│   │   │   ├── profile/        # User profile
│   │   │   └── tools/          # Tool pages
│   │   ├── layout.tsx          # Root layout (FOUC fix, Canvas provider)
│   │   ├── not-found.tsx       # Custom 404 page
│   │   └── globals.css         # Sage Tech color system
│   ├── components/
│   │   ├── ui/                 # Atomic UI components
│   │   │   ├── Button.tsx      # Primary, Glow, Outline variants
│   │   │   └── Card.tsx        # Glass, Interactive variants
│   │   ├── canvas/             # 3D components
│   │   │   ├── Canvas.tsx      # Global WebGL context
│   │   │   ├── Scene.tsx       # 3D scene content
│   │   │   └── SceneView.tsx   # View tunneling wrapper
│   │   ├── layout/             # Layout components
│   │   │   ├── Header.tsx      # Navigation header (public only)
│   │   │   ├── Sidebar.tsx     # Collapsible sidebar (dashboard)
│   │   │   ├── ThemeToggle.tsx # Dark/light mode toggle
│   │   │   └── Footer.tsx      # Page footer
│   │   ├── feedback/           # User feedback
│   │   │   └── Toaster.tsx     # Toast notification system
│   │   └── providers/          # React providers
│   │       └── CanvasProvider.tsx  # Dynamic Canvas import
│   ├── store/
│   │   ├── authStore.ts        # Authentication state (Zustand)
│   │   ├── uiStore.ts          # UI state (toasts, modals, sidebar)
│   │   └── useStore.ts         # Theme state with persistence
│   ├── lib/
│   │   ├── api/                # API client layer
│   │   │   ├── client.ts       # Base client with interceptors
│   │   │   ├── auth.ts         # Auth endpoints
│   │   │   ├── csrf.ts         # CSRF token management
│   │   │   └── index.ts        # Centralized exports
│   │   └── utils.ts            # cn() utility for class merging
│   ├── hooks/
│   │   ├── useAuth.ts          # Auth hook (uses authStore)
│   │   ├── useSessionPolling.ts # Session expiration polling
│   │   └── index.ts            # Hook exports
│   ├── middleware.ts           # Route protection
│   └── __tests__/              # Unit tests (31 passing)
│       ├── store/
│       │   ├── authStore.test.ts
│       │   └── uiStore.test.ts
│       └── lib/api/
│           └── csrf.test.ts
├── next.config.ts              # Turbopack + 3D + API rewrites
├── jest.config.js              # Jest configuration
├── jest.setup.js               # Jest setup (next/navigation mocks)
└── package.json                # Dependencies + test scripts
```

#### Design System - "Sage Tech" Dark Mode

**Colors (Tailwind classes):**
- `primary` / `primary-hover` / `primary-glow`: Sage green (#588157)
- `secondary` / `secondary-hover`: Tech mint (#9CDFB9)
- `accent` / `accent-hover`: Deep teal (#577A81)
- `surface-900` / `surface-800` / `surface-700`: Tinted dark backgrounds
- `text-high` / `text-muted`: Text colors
- `success` / `warning` / `danger` / `info`: State colors

**Typography:**
- Display font (headers): Space Grotesk via `font-display`
- Body font (UI): Inter via `font-body`

**Glassmorphism:**
- `.glass`: Standard glass effect
- `.glass-strong`: Higher opacity glass
- `.glow-primary` / `.glow-secondary`: Glow effects

#### View Tunneling Architecture (3D)

The 3D system uses "View Tunneling" for DOM/WebGL integration:

1. **Global Canvas**: Single `<Canvas>` at root layout
2. **View Components**: Render 3D into specific DOM positions
3. **Benefits**: Perfect scroll sync, correct z-indexing, single WebGL context

```tsx
// Place 3D content anywhere in HTML flow
import { SceneView } from "@/components/canvas";

<div className="relative h-[400px]">
  <SceneView className="absolute inset-0" />
  <div className="relative z-10">Overlay content</div>
</div>
```

#### Performance Features

- **Dynamic imports**: Canvas/3D components loaded with `ssr: false`
- **Performance monitor**: Auto-adjusts DPR based on FPS
- **On-demand rendering**: `frameloop="demand"` for static scenes
- **Optimized imports**: Lucide and drei tree-shaking
- **Theme persistence**: Zustand persist middleware prevents re-initialization
- **FOUC prevention**: Blocking script in root layout applies theme before render

#### Authentication & Security

**Session Management:**
- HttpOnly cookies for session storage (Flask backend)
- CSRF token injection on all mutating requests (POST/PUT/PATCH/DELETE)
- Automatic token caching and refresh
- 5-minute session polling to detect expiration

**Route Protection:**
- Next.js middleware validates session cookie
- Public routes: `/login`, `/register`, `/forgot-password`, `/reset-password`
- Protected routes: `/dashboard`, `/profile`, `/tools/*`, `/admin/*`
- 401 → Redirect to `/login?session_expired=true`
- 403 AUTH_UNVERIFIED → Redirect to `/verify-email-pending`

**API Client Features:**
- Automatic CSRF token injection via request interceptor
- Response interceptors for 401/403 handling
- Centralized error handling with toast notifications
- Token refresh on 403 CSRF mismatch

**State Management:**
```typescript
// authStore: User authentication state
{
  user: UserProfile | null,
  isAuthenticated: boolean,
  isLoading: boolean,
  permissions: string[],
  login(credentials) → Promise<void>,
  logout() → Promise<void>,
  checkAuth() → Promise<void>
}

// uiStore: UI state (toasts, modals, sidebar)
{
  toasts: Toast[],
  isSidebarCollapsed: boolean,
  isLoading: boolean,
  showToast(toast) → void,
  removeToast(id) → void,
  toggleSidebar() → void
}

// useStore: Theme persistence
{
  theme: 'light' | 'dark',
  toggleTheme() → void
}
```

### Templates
Jinja2 templates in two locations (ChoiceLoader setup):
- `templates/` - Main application templates
- `Tools/templates/` - Tool-specific templates

Template inheritance based on `base.html` with flash message support via `_flash_messages.html`.

## Environment Configuration

### Local Development
Set in `.env` file:
- `IS_LOCAL=true` - Enables local development mode
- `FLASK_ENV=development` - Development environment
- `SECRET_KEY` - Session secret key
- `SECURITY_PASSWORD_SALT` - For password reset tokens
- `TOKEN_SECRET_KEY` - For verification tokens

Database: SQLite (`sqlite:///users.db`)

### Production (Heroku)
- `IS_LOCAL=false` or unset
- `DATABASE_URL` - PostgreSQL connection string (auto-provided by Heroku)
- HTTPS enforcement and security headers enabled

## Key Features & Workflows

### Role-Based Access Control
- **User**: Basic tool access based on ToolAccess permissions
- **Admin**: Can manage regular users and grant/revoke tool access
- **SuperAdmin**: Can manage all users including admins, change roles

Check access: `User.user_has_tool_access(user_id, tool_name)` or `user.has_tool_access(tool_name)`

### Tool Access System
Default tools are automatically assigned to new users:
- Tax Calculator
- Canada Tax Calculator
- Character Counter
- Email Templates

Non-default tools require explicit admin grant.

### User Creation Flow
1. Use `UserFactory.create_user()` with role parameter
2. Password is set automatically within factory
3. For new users, call `User.assign_default_tools(user_id)` to grant default tool access

### Session Security
- Sessions expire on browser close (`SESSION_PERMANENT=False`)
- 30-minute backup timeout
- HTTPS-only cookies in production
- CSRF protection via `SESSION_COOKIE_SAMESITE='Lax'`

### Email System
Flask-Mail integration for:
- Password reset emails
- Email verification
- Contact form submissions

Configuration in `routes/contact_routes.py` via `configure_mail()`

## Testing

Test fixtures in `tests/conftest.py`:
- `app` - Flask test app with in-memory SQLite
- `client` - Test client for requests
- `init_database` - Pre-populated test data
- `logged_in_user`, `logged_in_admin`, `logged_in_superadmin` - Authenticated sessions

When writing tests:
- Use in-memory SQLite for speed
- Import models via `from model import User, Admin, Tool, etc.`
- CSRF is disabled in test config

## Database Migrations

Using Flask-Migrate (Alembic):
1. Make model changes in `model/` files
2. Generate migration: `flask db migrate -m "description"`
3. Review migration in `migrations/versions/`
4. Apply: `flask db upgrade`

### Production Migration Safety

The CI/CD pipeline (`.github/workflows/deploy.yml`) implements automatic rollback on migration failure:

1. **Backup Phase**: Full PostgreSQL backup created before any changes
2. **Migration Phase**: `flask db upgrade` runs with error tracking
3. **Success Path**: Migration verified, data counts reported to Discord
4. **Failure Path**: Automatic rollback from backup dump file
   - Zero manual intervention required
   - Database restored to pre-migration state
   - Discord notifications at every step

**Key Safety Features**:
- Migrations only ADD columns with defaults (never delete data)
- Full database dump (.dump) used for rollback, not CSV
- Automatic restoration triggered immediately on failure
- Backup artifacts retained for 30 days
- Users experience zero downtime during rollback

## Common Gotchas

1. **Circular imports**: Models use local imports within methods to avoid circular dependencies
2. **Password handling**: Always use `user.set_password()`, never set `user.password` directly
3. **Tool names**: Must match exactly between `Tool.name` and `ToolAccess.tool_name`
4. **Role changes**: SuperAdmin can change roles, but this creates new User objects (not in-place updates)
5. **Template loading**: Both `templates/` and `Tools/templates/` are searched via ChoiceLoader

# Agent Context & Tooling

## MCP Rule** The Model Context Protocol server responsible for persistent long-term context is named **knowledge graph memory server (kgm)**.
**Usage Rule:** Always refer to the tool by its full name: **knowledge graph memory server (kgm)**.

## MCP Server Usage Guidelines

Use MCP servers strategically and only when they add clear value to the task. Follow these rules:

### 1. **Knowledge Graph Memory Server (kgm)**
- **When to use:** Store important facts, preferences, decisions, or context the user wants remembered across conversations
- **When NOT to use:** For temporary information, current conversation context, or general knowledge queries
- **Examples:** User preferences, project details, personal information, ongoing work context

### 2. **Context7**
- **When to use:** For accessing real-time data, external APIs, or specialized context not available through standard tools
- **When NOT to use:** If web_search or other built-in tools can accomplish the task
- **Examples:** Specialized API integrations, real-time data feeds

### 3. **Playwright**
- **When to use:** Browser automation tasks, testing web applications, scraping dynamic content, or interacting with web pages programmatically
- **When NOT to use:** Simple web fetching (use web_fetch instead), or when manual instructions suffice
- **Examples:** Form submissions, clicking through multi-step processes, testing UI flows

### 4. **Sequential Thinking**
- **When to use:** Complex multi-step reasoning, mathematical proofs, logic puzzles, or when explicit step-by-step analysis improves accuracy
- **When NOT to use:** Simple questions, casual conversation, or when normal reasoning suffices
- **Examples:** Complex algorithm design, detailed problem decomposition, systematic analysis

### 5. **Sentry**
- **When to use:** Debugging application errors, monitoring issues, or analyzing error logs from Sentry projects
- **When NOT to use:** General debugging not related to Sentry-monitored applications
- **Examples:** Investigating production errors, analyzing error patterns

### 6. **Apidog Project**
- **When to use:** Working with APIs documented in Apidog project #1089534, testing API endpoints, or generating API-related code
- **When NOT to use:** For APIs not in this specific project or general API documentation
- **Examples:** Testing endpoints, generating API client code, understanding API specifications

### 7. **GitHub**
- **When to use:** Searching repositories, reading code, creating issues, managing pull requests, or accessing GitHub-hosted content
- **When NOT to use:** For non-GitHub code repositories or when web_search/web_fetch would suffice
- **Examples:** Code analysis, repository exploration, GitHub workflow automation

## General Principles

1. **Default to built-in tools first** - Use web_search, web_fetch, or repl before reaching for specialized MCP servers
2. **One task, one server** - Don't use multiple servers when one will do
3. **Justify usage** - If using an MCP server, it should solve a problem that built-in tools cannot
4. **User context matters** - If the user explicitly mentions a tool or workflow (e.g., "save this to memory", "test this in a browser"), use the appropriate MCP server
5. **Efficient selection** - Choose the most direct path to the solution

## Priority Order

When multiple tools could work:
1. Built-in Claude tools (web_search, web_fetch, repl, artifacts)
2. Lightweight MCP servers (kgm for memory, GitHub for code)
3. Heavy automation tools (Playwright, Sequential Thinking) - only when clearly beneficial
