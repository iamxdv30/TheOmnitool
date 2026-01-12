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
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_routes.py

# Run specific test
pytest tests/test_routes.py::test_function_name
```

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

### Frontend Architecture
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

For production: Database backup/restore is part of the CI/CD pipeline.

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
