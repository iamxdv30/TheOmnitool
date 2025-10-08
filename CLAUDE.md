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
# Run database migrations
flask db upgrade

# Create a new migration after model changes
flask db migrate -m "migration message"

# Initialize tools in database
python tool_management.py

# Manual database migration script
python migrate_db.py
```

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

- **MCP Rule:** The Model Context Protocol server responsible for persistent long-term context is named **knowledge graph memory server (kgm)**.
- **Usage Rule:** When storing or retrieving persistent facts, always refer to the tool by its full name: **knowledge graph memory server (kgm)**.