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

### Frontend (Modern / In-Progress)
- **Location:** `frontend/` directory
- **Framework:** Next.js 16 (App Router)
- **Library:** React 19
- **State:** Zustand v5 (with persist middleware)
- **API Client:** Custom fetch wrapper with CSRF & interceptors
- **Styling:** Tailwind CSS v4
- **3D Engine:** React Three Fiber (R3F) + Drei + Rapier (Physics)
- **Testing:** Jest + React Testing Library (31 tests passing)
- **Migration Status:** Phase 3 Complete ✅ (Auth & State Management)

### Database
- **Local:** SQLite (`users.db`)
- **Production:** PostgreSQL (Heroku)
- **Safety:** Built-in automatic backup before migrations via `utils/db_safety.py`.

## Critical Workflows

### 1. Running the Application
*   **Backend (Flask):**
    ```bash
    # Standard entry
    python main.py
    ```
*   **Frontend (Next.js):**
    ```bash
    cd frontend
    npm run dev
    ```

### 2. Database Management
**CRITICAL:** This project emphasizes database safety. Backups are automatic.
*   **Apply Migrations:** `flask db upgrade`
*   **Create Migration:** `flask db migrate -m "message"`
*   **Safe Migration Wrapper (Recommended):** `python migrate_db.py` (Performs backup -> migrate -> upgrade)
*   **Restore Backup:** `python restore_backup.py`

### 3. Testing
*   **Backend Tests:** `pytest` (from root directory)
*   **Frontend Tests:** `npm test` (from `frontend/` directory)
*   **Smoke Tests:** `python tests/smoke_tests.py --url <target_url>`
*   **Current Coverage:** 31 frontend unit tests (auth, UI, CSRF)

## Architecture Summary

### Backend (`/`)
*   **Entry Point:** `main.py` (App factory, logging config, security headers, template loader).
*   **Models (`model/`):**
    *   **Users:** Single Table Inheritance (`User` -> `Admin` -> `SuperAdmin`) in `users.py`.
    *   **Tools:** `Tool` and `ToolAccess` (many-to-many relationship) in `tools.py`.
*   **Routes (`routes/`):** Blueprint-based logic for `auth`, `user`, `admin`, `tool`, `contact`, and `health`.
*   **Tool Logic (`Tools/`):** Contains standalone logic for tools (e.g., `tax_calculator.py`, `char_counter.py`).
*   **Templates:** Managed via `ChoiceLoader` searching in `Tools/templates/` then `templates/`.

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
*   **Route Protection:** `middleware.ts` validates session cookies server-side
*   **Session Polling:** `useSessionPolling.ts` checks auth status every 5 minutes

## Development Conventions

1.  **Imports:** Use absolute imports (e.g., `from model import User`).
2.  **Passwords:** ALWAYS use `user.set_password("...")`.
3.  **Authentication:** Includes reCAPTCHA verification and strict email verification (enforced in `auth_routes.py`).
4.  **Logging:** Centralized in `main.py`. Uses `TimedRotatingFileHandler` (daily, 30-day retention) and a `NoiseFilter` to exclude verbose library logs.
5.  **Security:** Production environment enforces HTTPS and adds HSTS and CSP headers.
6.  **Version:** Tracked in the root `VERSION` file, injected into templates via context processor.

## Key Files Map

### Backend
*   `main.py`: App factory, logging, and middleware.
*   `model/users.py`: RBAC and user hierarchy.
*   `routes/api/`: JSON API endpoints (auth_api, user_api, tool_api)
*   `services/`: Business logic layer (auth_service, user_service, tool_service)
*   `routes/tool_routes.py`: Legacy HTML routes for tools.
*   `Tools/tax_calculator.py`: Core math logic for US, Canada, and VAT calculations.
*   `utils/db_safety.py`: Database validation and backup logic.
*   `.github/workflows/`: CI/CD pipelines for production and staging.

### Frontend (Next.js)
*   `frontend/src/app/(public)/page.tsx`: Landing page.
*   `frontend/src/app/(auth)/login/page.tsx`: Login page with query param handling.
*   `frontend/src/app/(dashboard)/layout.tsx`: Dashboard layout with collapsible sidebar.
*   `frontend/src/middleware.ts`: Route protection (session validation).
*   `frontend/src/store/authStore.ts`: Authentication state management.
*   `frontend/src/store/uiStore.ts`: UI state (toasts, modals, sidebar).
*   `frontend/src/lib/api/client.ts`: API client with CSRF and interceptors.
*   `frontend/src/__tests__/`: Jest unit tests (31 passing).

### Documentation
*   `docs/BACKEND_FRONTEND_INTEGRATION_PLAN.md`: Migration strategy (Phase 3 complete)
*   `CLAUDE.md`: Context for Claude Code AI agent.
*   `Gemini.md`: Context for Gemini AI agent (this file).