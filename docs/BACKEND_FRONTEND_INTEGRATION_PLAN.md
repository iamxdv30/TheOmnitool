# Backend-Frontend Integration Plan

This document outlines the comprehensive strategy for integrating the existing Flask backend (Monolith) with the new Next.js 16 frontend. The goal is to transition from a server-side rendered (Jinja2) application to a modern Single Page Application (SPA) architecture while maintaining backward compatibility and strict security standards.

---

## Table of Contents

    1. [Architecture Overview](#1-architecture-overview)
  [X]  2. [Phase 1: Backend Refactoring (Service Layer)](#2-phase-1-backend-refactoring-the-service-layer) ✅ **COMPLETE**
  [X]  3. [Phase 2: API Definition](#3-phase-2-api-definition) ✅ **COMPLETE**
  [X]  4. [Phase 3: Frontend Authentication & State](#4-phase-3-frontend-authentication--state-management) ✅ **COMPLETE**
  [X]  5. [Phase 4: Tool Migration Strategy](#5-phase-4-tool-migration-strategy) ✅ **COMPLETE**
  [X]  6. [Phase 5: Production Deployment](#6-phase-5-production-deployment-heroku) ✅ **COMPLETE**
  [X]  7. [Security Configuration](#7-security-configuration) ✅ **COMPLETE**
  [X]  8. [Testing Strategy](#8-testing-strategy) ✅ **COMPLETE**
  [X]  9. [Implementation Checklist](#9-implementation-checklist) ✅ **COMPLETE**
  [X]  10. [CI/CD Workflow Updates](#10-cicd-workflow-updates) ✅ **COMPLETE**
  [X]  11. [Migration Risks & Mitigations](#11-migration-risks--mitigations) ✅ **COMPLETE**
  [X]  12. [Success Criteria](#12-success-criteria) ✅ **COMPLETE**

---

## 1. Architecture Overview

We will adopt a **Hybrid "Strangler Fig" Architecture** during the transition phase.

| Component | Role | Technology |
|-----------|------|------------|
| **Backend** | Source of Truth for data, auth, and legacy logic | Flask (evolving to headless API) |
| **Frontend** | Modern UI (SPA) | Next.js 16 + React |
| **Database** | Shared data store | PostgreSQL (prod) / SQLite (dev) |
| **Proxy** | Route `/api/*` to Flask | Next.js rewrites (dev) / Heroku routing (prod) |

### 1.1 Data Flow

```
┌─────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Browser   │ ───▶ │   Next.js SSR   │ ───▶ │   Flask API     │
│  (React SPA)│      │   (Port 3000)   │      │   (Port 5000)   │
└─────────────┘      └─────────────────┘      └─────────────────┘
      │                      │                        │
      │  1. Request /dashboard                        │
      │ ─────────────────────▶                        │
      │  2. Serve React shell                         │
      │ ◀─────────────────────                        │
      │                                               │
      │  3. Fetch /api/v1/user/profile               │
      │ ───────────────────────────────────────────▶ │
      │  4. Validate HttpOnly cookie + Return JSON   │
      │ ◀─────────────────────────────────────────── │
```

### 1.2 Environment Configuration

| Variable | Development | Production |
|----------|-------------|------------|
| `FLASK_API_URL` | `http://localhost:5000` | `http://127.0.0.1:5000` (internal) |
| `NEXT_PUBLIC_APP_URL` | `http://localhost:3000` | `https://omnitool-by-xdv.herokuapp.com` |
| `SESSION_COOKIE_DOMAIN` | `localhost` | `.herokuapp.com` |
| `SESSION_COOKIE_SECURE` | `False` | `True` |
| `CORS_ORIGINS` | `http://localhost:3000` | (same-origin, no CORS needed) |

---

## 2. Phase 1: Backend Refactoring (The Service Layer)

To support both Legacy (HTML) routes and New (JSON) API routes without duplicating code, we must extract business logic into a **Service Layer**.

### 2.1 Directory Structure
```
/
├── routes/                 # Controllers
│   ├── api/                # NEW: JSON Endpoints
│   │   ├── __init__.py
│   │   ├── auth_api.py
│   │   └── user_api.py
│   ├── auth_routes.py      # Legacy: HTML Endpoints
│   └── ...
├── services/               # NEW: Business Logic (Pure Python)
│   ├── __init__.py
│   ├── auth_service.py     # Authentication logic (Login, Register, Verify)
│   ├── user_service.py     # User management
│   └── tool_service.py     # Tax calc, char counter logic
└── model/                  # Database Models
```

### 2.2 Refactoring Pattern
1.  **Identify Logic:** Logic like password verification, ReCAPTCHA validation, and email verification checks currently inside `auth_routes.py` will move to `services/auth_service.py`.
2.  **Refactor Routes:** Both legacy and API routes will call these shared services.

---

## 3. Phase 2: API Definition

### 3.1 Response Envelope Standard

All API responses follow this structure:

```json
// Success
{
  "success": true,
  "data": { ... }
}

// Error
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message"
  }
}
```

### 3.2 HTTP Status Code Conventions

| Status | Usage |
|--------|-------|
| `200` | Successful GET, PUT, PATCH |
| `201` | Successful POST (resource created) |
| `204` | Successful DELETE (no content) |
| `400` | Validation error, malformed request |
| `401` | Not authenticated (session expired/missing) |
| `403` | Authenticated but forbidden (unverified, no permission) |
| `404` | Resource not found |
| `429` | Rate limited |
| `500` | Server error |

### 3.3 Error Codes

| Code | HTTP Status | Meaning |
|------|-------------|---------|
| `AUTH_REQUIRED` | 401 | No valid session |
| `AUTH_UNVERIFIED` | 403 | Email not verified |
| `AUTH_INVALID_CREDENTIALS` | 401 | Wrong username/password |
| `AUTH_RATE_LIMITED` | 429 | Too many login attempts |
| `PERMISSION_DENIED` | 403 | No access to resource |
| `VALIDATION_ERROR` | 400 | Invalid input data |
| `RECAPTCHA_FAILED` | 400 | ReCAPTCHA verification failed |
| `TOKEN_EXPIRED` | 400 | Password reset/verification token expired |
| `RESOURCE_NOT_FOUND` | 404 | Requested item doesn't exist |

### 3.4 Authentication Endpoints (`/api/v1/auth`)

| Endpoint | Method | Body Params | Description |
|----------|--------|-------------|-------------|
| `/login` | POST | `username`, `password`, `recaptcha_token` | Authenticates user. Returns `403 AUTH_UNVERIFIED` if email not verified. |
| `/logout` | POST | - | Clears session cookie. |
| `/register` | POST | `username`, `email`, `password`, `recaptcha_token` | Creates user, sends verification email. |
| `/status` | GET | - | Returns `{ isAuthenticated, user: UserProfile \| null }` |
| `/csrf` | GET | - | Returns `{ csrfToken: string }` for header injection. |
| `/forgot-password` | POST | `email`, `recaptcha_token` | Sends password reset email. |
| `/reset-password` | POST | `token`, `new_password` | Resets password using token from email. |
| `/resend-verification` | POST | `email`, `recaptcha_token` | Resends verification email. |

### 3.5 User Endpoints (`/api/v1/user`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/profile` | GET | Returns current user's profile and settings. |
| `/profile` | PATCH | Updates profile (name, email). Requires re-verification if email changed. |
| `/password` | PUT | Changes password. Requires current password. |
| `/tools` | GET | Returns list of tools user has access to. |
| `/usage` | GET | Returns user's tool usage statistics. |

### 3.6 Tool Endpoints (`/api/v1/tools`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Lists all available tools (with access flags). |
| `/tax-calculator` | POST | Executes tax calculation. Body: `{ income, filingStatus, ... }` |
| `/character-counter` | POST | Counts characters/words. Body: `{ text }` |
| `/email-templates` | GET | Lists user's email templates. |
| `/email-templates` | POST | Creates new template. |
| `/email-templates/:id` | PUT | Updates template. |
| `/email-templates/:id` | DELETE | Deletes template. |

### 3.7 Admin Endpoints (`/api/v1/admin`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/users` | GET | Lists all users (paginated). Query: `?page=1&per_page=20&search=` |
| `/users/:id` | GET | Get user details. |
| `/users/:id` | PATCH | Update user (role, verified status). |
| `/users/:id` | DELETE | Delete user. |
| `/users/:id/tools` | GET | Get user's tool access. |
| `/users/:id/tools` | PUT | Update user's tool access. Body: `{ tool_ids: [] }` |
| `/stats` | GET | Dashboard statistics. |

---

## 4. Phase 3: Frontend Authentication & State Management

### 4.1 State Management (Zustand)

```typescript
// src/store/authStore.ts
interface AuthState {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  permissions: string[];  // Tool access list

  // Actions
  login: (credentials: LoginPayload) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  setUser: (user: UserProfile | null) => void;
}
```

### 4.2 API Client Architecture

```typescript
// src/lib/api/client.ts
const apiClient = {
  // Base configuration
  baseURL: '/api/v1',

  // Interceptors
  requestInterceptor: async (config) => {
    // Inject CSRF token for mutating requests
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(config.method)) {
      const csrfToken = await getCsrfToken();
      config.headers['X-CSRFToken'] = csrfToken;
    }
    return config;
  },

  responseInterceptor: async (response) => {
    // Handle 401: Redirect to login
    if (response.status === 401) {
      authStore.getState().setUser(null);
      redirect('/login?session_expired=true');
    }

    // Handle 403 AUTH_UNVERIFIED: Redirect to verification page
    if (response.status === 403) {
      const data = await response.json();
      if (data.error?.code === 'AUTH_UNVERIFIED') {
        redirect('/verify-email-pending');
      }
    }

    return response;
  }
};
```

### 4.3 Route Protection (Next.js Middleware)

```typescript
// src/middleware.ts
export function middleware(request: NextRequest) {
  const sessionCookie = request.cookies.get('session');
  const path = request.nextUrl.pathname;

  // Public routes (no auth required)
  const publicRoutes = ['/login', '/register', '/forgot-password', '/reset-password'];

  // Admin-only routes
  const adminRoutes = ['/admin'];

  if (!sessionCookie && !publicRoutes.some(r => path.startsWith(r))) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Note: Role-based access checked client-side after /auth/status
  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|api).*)']
};
```

### 4.4 The "Strict Auth" Workflow

#### A. Login Flow

```
┌──────────┐     ┌──────────┐     ┌─────────┐
│  Login   │────▶│  Flask   │────▶│ Check   │
│   Form   │     │   API    │     │ Status  │
└──────────┘     └──────────┘     └─────────┘
      │                │               │
      │ 1. Submit      │               │
      │ credentials    │               │
      │ + reCAPTCHA    │               │
      │                ▼               │
      │         ┌──────────────┐       │
      │         │ Set HttpOnly │       │
      │         │    Cookie    │       │
      │         └──────────────┘       │
      │                │               │
      │                ▼               │
      │         ┌──────────────┐       │
      │         │   200 OK     │       │
      │         │ + user data  │       │
      │         └──────────────┘       │
      │                │               │
      ▼                ▼               ▼
┌──────────────────────────────────────────┐
│  Update Zustand store → Redirect to /    │
└──────────────────────────────────────────┘
```

#### B. Unverified User Handling

1. User logs in with valid credentials
2. Flask returns `403` with `error.code = "AUTH_UNVERIFIED"`
3. Frontend redirects to `/verify-email-pending`
4. User can request resend verification from that page

#### C. Hybrid Email Verification

1. User clicks verification link in email → Flask endpoint
2. Flask verifies token and **sets session cookie** (auto-login)
3. Flask redirects browser to Next.js `/dashboard?verified=true`
4. Next.js calls `/api/v1/auth/status`, gets authenticated user
5. Show success toast "Email verified successfully!"

#### D. Password Reset Flow

1. User submits email on `/forgot-password`
2. Flask sends reset email with token
3. User clicks link → Next.js `/reset-password?token=xxx`
4. User submits new password → Flask validates token and updates
5. Redirect to `/login?password_reset=true`

### 4.5 CSRF Protection

```typescript
// CSRF token management
let csrfToken: string | null = null;

async function getCsrfToken(): Promise<string> {
  if (!csrfToken) {
    const response = await fetch('/api/v1/auth/csrf');
    const data = await response.json();
    csrfToken = data.data.csrfToken;
  }
  return csrfToken;
}

// Clear on logout
function clearCsrfToken() {
  csrfToken = null;
}
```

### 4.6 Session Expiration Handling

- Flask session timeout: 30 minutes of inactivity
- Frontend periodically calls `/auth/status` (every 5 minutes) to detect expiration
- On 401 response, clear local state and redirect to login with message

---

## 5. Phase 4: Tool Migration Strategy

Tools will be migrated one by one to isolate complexity.
1.  **Extract Logic:** Move logic to `services/tool_service.py`.
2.  **Create API:** Implement JSON endpoint in `routes/api/tool_api.py`.
3.  **Build Frontend:** Create Next.js page (e.g., `src/app/tools/tax-calculator`).

---

## 6. Phase 5: Production Deployment (Heroku)

We will use a **Single Dyno** ("All-in-One") approach.

### 6.1 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Heroku Dyno                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                 Process Manager                        │  │
│  │  (npm start with concurrently or custom script)       │  │
│  └───────────────────────────────────────────────────────┘  │
│           │                              │                  │
│           ▼                              ▼                  │
│  ┌─────────────────┐          ┌─────────────────────────┐  │
│  │   Next.js       │          │   Flask (Gunicorn)      │  │
│  │   Port: $PORT   │ ──────▶  │   Port: 5000 (internal) │  │
│  │   (Primary)     │  proxy   │   (Background)          │  │
│  └─────────────────┘          └─────────────────────────┘  │
│                                         │                   │
│                                         ▼                   │
│                               ┌─────────────────────────┐  │
│                               │   PostgreSQL            │  │
│                               │   (Heroku Postgres)     │  │
│                               └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Procfile Configuration

```procfile
# Option A: Using concurrently (npm package)
web: npm run start:prod

# package.json script
# "start:prod": "concurrently \"gunicorn -b 127.0.0.1:5000 main:app\" \"next start -p $PORT\""
```

```procfile
# Option B: Using bash script
web: ./scripts/start-production.sh
```

```bash
#!/bin/bash
# scripts/start-production.sh

# Start Flask in background
gunicorn -b 127.0.0.1:5000 -w 2 main:app &
FLASK_PID=$!

# Wait for Flask to be ready
until curl -s http://127.0.0.1:5000/health/ping > /dev/null; do
  echo "Waiting for Flask..."
  sleep 1
done

echo "Flask ready on port 5000"

# Start Next.js in foreground
cd frontend && npm start -- -p $PORT

# Cleanup on exit
trap "kill $FLASK_PID" EXIT
```

### 6.3 Buildpacks

```
# .buildpacks or Heroku dashboard
1. heroku/python      # First: Install Python + pip dependencies
2. heroku/nodejs      # Second: Install Node.js + npm dependencies, build Next.js
```

### 6.4 Next.js Proxy Configuration

```typescript
// frontend/next.config.ts
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.FLASK_API_URL
          ? `${process.env.FLASK_API_URL}/api/:path*`
          : 'http://127.0.0.1:5000/api/:path*'
      },
      // Legacy routes fallback (during transition)
      {
        source: '/legacy/:path*',
        destination: 'http://127.0.0.1:5000/:path*'
      }
    ];
  }
};
```

### 6.5 Health Checks

```typescript
// Flask: Already exists at /health, /health/ping, /health/database

// Next.js: Add health endpoint
// frontend/src/app/api/health/route.ts
export async function GET() {
  const flaskHealth = await fetch('http://127.0.0.1:5000/health/ping')
    .then(() => 'up')
    .catch(() => 'down');

  return Response.json({
    status: flaskHealth === 'up' ? 'healthy' : 'degraded',
    services: {
      nextjs: 'up',
      flask: flaskHealth
    }
  });
}
```

### 6.6 Environment Variables (Heroku)

```bash
# Required
DATABASE_URL          # Auto-set by Heroku Postgres
SECRET_KEY            # Flask session secret
SECURITY_PASSWORD_SALT
TOKEN_SECRET_KEY
RECAPTCHA_SITE_KEY
RECAPTCHA_SECRET_KEY

# New for frontend
FLASK_API_URL=http://127.0.0.1:5000
NEXT_PUBLIC_APP_URL=https://omnitool-by-xdv.herokuapp.com

# Session cookies
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_SAMESITE=Lax
```

---

## 7. Security Configuration

### 7.1 Session Cookie Settings

```python
# Flask config for production
SESSION_COOKIE_SECURE = True       # HTTPS only
SESSION_COOKIE_HTTPONLY = True     # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'    # CSRF protection
SESSION_COOKIE_NAME = 'omnitool_session'
SESSION_COOKIE_DOMAIN = None       # Same domain only
PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
```

### 7.2 CORS Configuration (Development Only)

```python
# Only needed for local dev where Next.js and Flask on different ports
from flask_cors import CORS

if app.config['IS_LOCAL']:
    CORS(app,
         origins=['http://localhost:3000'],
         supports_credentials=True,  # Allow cookies
         expose_headers=['X-CSRFToken'])
```

### 7.3 CSRF Token Flow

```
1. Frontend loads → GET /api/v1/auth/csrf
2. Flask generates token, stores in session, returns in JSON
3. Frontend caches token, includes in X-CSRFToken header
4. Flask validates header matches session token
5. On logout, token is invalidated
```

### 7.4 Rate Limiting

```python
# Flask-Limiter for API endpoints
from flask_limiter import Limiter

limiter = Limiter(key_func=get_remote_address)

@api_bp.route('/auth/login', methods=['POST'])
@limiter.limit("5 per minute")  # Prevent brute force
def login():
    ...

@api_bp.route('/auth/forgot-password', methods=['POST'])
@limiter.limit("3 per hour")  # Prevent email spam
def forgot_password():
    ...
```

### 7.5 Input Validation

All API endpoints must validate input using a schema library:

```python
# Using marshmallow or pydantic
from marshmallow import Schema, fields, validate

class LoginSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    password = fields.Str(required=True, validate=validate.Length(min=8))
    recaptcha_token = fields.Str(required=True)
```

---

## 8. Testing Strategy

### 8.1 Testing Pyramid

```
        ┌───────────┐
        │   E2E     │  ← Playwright: Critical user journeys
        │  (Few)    │
        ├───────────┤
        │Integration│  ← pytest + Next.js: API contracts, auth flows
        │ (Some)    │
        ├───────────┤
        │   Unit    │  ← pytest + Jest: Services, components, stores
        │  (Many)   │
        └───────────┘
```

### 8.2 Backend Testing (pytest)

```python
# tests/api/test_auth_api.py
def test_login_success(client, test_user):
    response = client.post('/api/v1/auth/login', json={
        'username': 'testuser',
        'password': 'password123',
        'recaptcha_token': 'test_token'
    })
    assert response.status_code == 200
    assert response.json['success'] is True
    assert 'session' in response.headers.get('Set-Cookie', '')

def test_login_unverified_returns_403(client, unverified_user):
    response = client.post('/api/v1/auth/login', json={...})
    assert response.status_code == 403
    assert response.json['error']['code'] == 'AUTH_UNVERIFIED'
```

### 8.3 Frontend Testing (Jest + React Testing Library)

```typescript
// src/__tests__/store/authStore.test.ts
describe('authStore', () => {
  it('should redirect to verify-email-pending on AUTH_UNVERIFIED', async () => {
    mockFetch.mockResolvedValueOnce({
      status: 403,
      json: () => Promise.resolve({
        error: { code: 'AUTH_UNVERIFIED' }
      })
    });

    await authStore.getState().login(credentials);
    expect(mockRouter.push).toHaveBeenCalledWith('/verify-email-pending');
  });
});
```

### 8.4 API Contract Testing

```typescript
// Ensure frontend and backend agree on API shape
// tests/contracts/auth.contract.test.ts

const AuthStatusSchema = z.object({
  success: z.literal(true),
  data: z.object({
    isAuthenticated: z.boolean(),
    user: UserProfileSchema.nullable()
  })
});

test('GET /auth/status matches contract', async () => {
  const response = await fetch('/api/v1/auth/status');
  const data = await response.json();
  expect(() => AuthStatusSchema.parse(data)).not.toThrow();
});
```

### 8.5 E2E Testing (Playwright)

```typescript
// e2e/auth.spec.ts
test('unverified user sees verification page', async ({ page }) => {
  // Register new user
  await page.goto('/register');
  await page.fill('[name=email]', 'test@example.com');
  // ... fill other fields
  await page.click('button[type=submit]');

  // Should redirect to verification pending
  await expect(page).toHaveURL('/verify-email-pending');
  await expect(page.locator('h1')).toContainText('Check Your Email');
});

test('full login to dashboard flow', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[name=username]', 'verified_user');
  await page.fill('[name=password]', 'password123');
  await page.click('button[type=submit]');

  await expect(page).toHaveURL('/dashboard');
  await expect(page.locator('[data-testid=user-menu]')).toBeVisible();
});
```

### 8.6 Smoke Tests (Post-Deployment)

```bash
# Run after each deployment
python tests/smoke_tests.py --url https://omnitool-by-xdv.herokuapp.com

# Checks:
# - /health returns 200
# - /api/v1/auth/status returns valid JSON
# - Login page loads
# - Static assets load
```

---

## 9. Implementation Checklist

### 9.1 Phase 1: Backend Service Layer

- [x] Create `services/` package structure
  - [x] `services/__init__.py`
  - [x] `services/auth_service.py`
  - [x] `services/user_service.py`
  - [x] `services/tool_service.py`
- [x] Extract business logic from routes to services
  - [x] Password verification logic
  - [x] ReCAPTCHA validation
  - [x] Email verification checks
  - [x] User creation/registration
- [x] Add unit tests for services

### 9.2 Phase 2: API Endpoints

- [x] Create API blueprint structure
  - [x] `routes/api/__init__.py`
  - [x] `routes/api/auth_api.py`
  - [x] `routes/api/user_api.py`
  - [x] `routes/api/tool_api.py`
  - [ ] `routes/api/admin_api.py`
- [x] Register API blueprint in `main.py`
- [x] Implement authentication endpoints
  - [x] POST `/api/v1/auth/login`
  - [x] POST `/api/v1/auth/logout`
  - [x] POST `/api/v1/auth/register`
  - [x] GET `/api/v1/auth/status`
  - [x] GET `/api/v1/auth/csrf`
  - [x] POST `/api/v1/auth/forgot-password`
  - [x] POST `/api/v1/auth/reset-password`
  - [x] POST `/api/v1/auth/resend-verification`
- [x] Implement user endpoints
  - [x] GET/PATCH `/api/v1/user/profile`
  - [x] PUT `/api/v1/user/password`
  - [x] GET `/api/v1/user/tools`
- [x] Add input validation schemas (marshmallow/pydantic)
- [ ] Add rate limiting to sensitive endpoints
- [x] Write API integration tests

### 9.3 Phase 3: Frontend Authentication ✅ **COMPLETE**

- [x] Setup Zustand store
  - [x] `src/store/authStore.ts`
  - [x] `src/store/uiStore.ts` (toasts, modals, sidebar state)
  - [x] Theme persistence with Zustand persist middleware
- [x] Create API client
  - [x] `src/lib/api/client.ts` (base client)
  - [x] `src/lib/api/auth.ts` (auth endpoints)
  - [x] `src/lib/api/csrf.ts` (CSRF token management with caching)
  - [x] `src/lib/api/index.ts` (centralized exports)
  - [x] 401/403 interceptors with automatic redirects
- [x] Implement Next.js middleware for route protection
- [x] Create auth pages
  - [x] `/login` (with session_expired, password_reset, verified params)
  - [x] `/register`
  - [x] `/forgot-password`
  - [x] `/reset-password`
  - [x] `/verify-email-pending`
- [x] Configure Next.js rewrites for `/api/*`
- [x] Add session expiration polling (`useSessionPolling.ts`)
- [x] Write frontend unit tests (31 passing tests)
  - [x] `__tests__/store/authStore.test.ts`
  - [x] `__tests__/store/uiStore.test.ts`
  - [x] `__tests__/lib/api/csrf.test.ts`

**Additional UX/DX Improvements:**
- [x] Fixed Flash of Unstyled Content (FOUC) with blocking theme script
- [x] Dynamic ReCAPTCHA theming
- [x] Layout restructuring (removed duplicate header, fixed vertical lines)
- [x] Collapsible sidebar with toggle state
- [x] Custom 404 page
- [x] Responsive dashboard layout

### 9.4 Phase 4: Tool Migration ✅ **COMPLETE**

**Infrastructure:**
- [x] Created `useToolAccess` hook for permission-based access control
- [x] Created `frontend/src/lib/api/tools.ts` - Tools API client with typed methods
- [x] Added `TOOL_NAMES` constants for type-safe tool references

**Tool Status:**

- [x] **Character Counter** (Client-side - no API needed)
  - [x] Backend: `services/tool_service.py` - `count_characters()` method exists
  - [x] Backend: `POST /api/v1/tools/character-counter` endpoint exists
  - [x] Frontend: `src/app/(dashboard)/tools/char-counter/page.tsx` - Pure client-side implementation (faster UX)
  - Note: Kept client-side for real-time counting; API available if needed

- [x] **Unix Timestamp Converter** (Client-side - no API needed)
  - [x] Frontend: `src/app/(dashboard)/tools/unix-timestamp/page.tsx` - Pure client-side implementation
  - Note: No backend logic needed; JavaScript handles timestamp conversion

- [x] **Unified Tax Calculator** (Connected to API)
  - [x] Backend: `services/tool_service.py` - `calculate_tax()` method
  - [x] Backend: `POST /api/v1/tools/tax-calculator` endpoint
  - [x] Frontend: Connected to API via `toolsApi.calculateTax()`
  - [x] Frontend: Added `useToolAccess` for permission checking
  - [x] Frontend: Added loading states and error handling

- [x] **Email Templates** (Connected to API)
  - [x] Backend: Full CRUD in `services/tool_service.py`
  - [x] Backend: RESTful endpoints in `routes/api/tool_api.py`
  - [x] Frontend: `src/app/(dashboard)/tools/email-templates/page.tsx`
  - [x] Frontend: Fixed API client import (`api` → `apiClient`)

### 9.5 Phase 5: Production Deployment ✅ **COMPLETE**

- [x] Create production startup script
  - [x] `scripts/start-production.sh` - Dual-process startup with 60s timeout
  - [x] Flask health check before Next.js start
- [x] Update `Procfile` - Points to `./scripts/start-production.sh`
- [x] Configure Heroku buildpacks (python + nodejs) - Added to CI/CD workflows
- [x] Set environment variables on Heroku - `FLASK_API_URL`, `NEXT_PUBLIC_APP_URL`, session cookies
- [x] Add health check endpoint to Next.js - `frontend/src/app/api/health/route.ts`
- [x] Update CI/CD pipeline for dual-stack deployment
  - [x] Staging workflow (`deploy.yml`) - Node.js setup, frontend tests, buildpacks
  - [x] Production workflow (`deploy_production.yml`) - Mirrored staging + health verification
- [x] Run smoke tests post-deployment - Enhanced for Flask + Next.js health checks

### 9.6 Security Hardening

- [ ] Configure CORS for development
- [ ] Verify session cookie settings in production
- [ ] Add rate limiting to all auth endpoints
- [ ] Audit input validation coverage
- [ ] Test CSRF protection E2E

### 9.7 Testing & Quality

- [x] Backend API tests (pytest)
- [x] Frontend component tests (Jest)
- [ ] API contract tests (Zod schemas)
- [ ] E2E auth flow tests (Playwright)
- [ ] Update smoke test suite
- [ ] Document rollback procedures

---

## 10. CI/CD Workflow Updates

### 10.1 Current State Analysis

**Current Workflows (Python-Only):**
- `deploy.yml` → Staging deployment (`omnitool-by-xdv-staging`)
- `deploy_production.yml` → Production deployment (`omnitool-by-xdv`)
- Both use only Python/Flask with Gunicorn

**Missing for Frontend Integration:**
| Component | Current | Required |
|-----------|---------|----------|
| Buildpacks | `heroku/python` only | `heroku/python` + `heroku/nodejs` |
| Procfile | `gunicorn main:app` | Dual-process (Flask + Next.js) |
| Build Steps | None for frontend | `npm install && npm run build` |
| Env Vars | Flask only | + `FLASK_API_URL`, `NEXT_PUBLIC_APP_URL` |
| Smoke Tests | Flask endpoints only | + Next.js health + frontend routes |
| Health Checks | `/health` (Flask) | + Next.js health endpoint |

### 10.2 Updated Workflow: Staging (`deploy.yml`)

```yaml
# New/modified steps for staging deployment

jobs:
  test:
    # ... existing Python tests ...

    # ADD: Frontend tests
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json

    - name: Install Frontend Dependencies
      run: |
        cd frontend
        npm ci

    - name: Run Frontend Tests
      run: |
        cd frontend
        npm run lint
        npm test -- --passWithNoTests

    - name: Build Frontend
      run: |
        cd frontend
        npm run build

  deploy-to-staging:
    # ... existing steps ...

    # ADD: Configure Heroku Buildpacks
    - name: Configure Buildpacks
      env:
        HEROKU_API_KEY: ${{ secrets.HEROKU_API_KEY }}
      run: |
        echo "Configuring buildpacks for dual-stack deployment..."
        heroku buildpacks:clear -a omnitool-by-xdv-staging
        heroku buildpacks:add heroku/python -a omnitool-by-xdv-staging
        heroku buildpacks:add heroku/nodejs -a omnitool-by-xdv-staging
        echo "✅ Buildpacks configured: python + nodejs"

    # ADD: Frontend environment variables
    - name: Update Heroku Config
      run: |
        # ... existing vars ...

        # NEW: Frontend integration vars
        heroku config:set FLASK_API_URL="http://127.0.0.1:5000" -a omnitool-by-xdv-staging
        heroku config:set NEXT_PUBLIC_APP_URL="https://omnitool-by-xdv-staging-bc1844b846d6.herokuapp.com" -a omnitool-by-xdv-staging

        # Session cookie settings
        heroku config:set SESSION_COOKIE_SECURE="true" -a omnitool-by-xdv-staging
        heroku config:set SESSION_COOKIE_SAMESITE="Lax" -a omnitool-by-xdv-staging
        heroku config:set SESSION_COOKIE_HTTPONLY="true" -a omnitool-by-xdv-staging

    # MODIFY: Enhanced smoke tests
    - name: Run Staging Smoke Tests
      env:
        STAGING_URL: https://omnitool-by-xdv-staging-bc1844b846d6.herokuapp.com
      run: |
        echo "=========================================="
        echo "🧪 RUNNING STAGING SMOKE TESTS"
        echo "=========================================="

        # Flask health check
        curl -f $STAGING_URL/health/ping || {
          echo "❌ Flask health check failed"
          exit 1
        }
        echo "✅ Flask is healthy"

        # NEW: Next.js health check
        curl -f $STAGING_URL/api/health || {
          echo "❌ Next.js health check failed"
          exit 1
        }
        echo "✅ Next.js is healthy"

        # NEW: Frontend page loads
        curl -f -s -o /dev/null -w "%{http_code}" $STAGING_URL/login | grep -q "200" || {
          echo "❌ Frontend login page failed to load"
          exit 1
        }
        echo "✅ Frontend pages loading"

        # Existing Python smoke tests
        python tests/smoke_tests.py --url $STAGING_URL

        echo "=========================================="
```

### 10.3 Updated Workflow: Production (`deploy_production.yml`)

```yaml
# Mirror staging changes + additional safety

  deploy-to-production:
    # ... existing steps ...

    # ADD: Same buildpack configuration
    - name: Configure Buildpacks
      env:
        HEROKU_API_KEY: ${{ secrets.HEROKU_API_KEY }}
      run: |
        heroku buildpacks:clear -a omnitool-by-xdv
        heroku buildpacks:add heroku/python -a omnitool-by-xdv
        heroku buildpacks:add heroku/nodejs -a omnitool-by-xdv

    # ADD: Frontend environment variables
    - name: Update Heroku Config (Production)
      run: |
        # ... existing vars ...

        # NEW: Frontend integration vars
        heroku config:set FLASK_API_URL="http://127.0.0.1:5000" -a omnitool-by-xdv
        heroku config:set NEXT_PUBLIC_APP_URL="https://omnitool-by-xdv-85a1bde25ad1.herokuapp.com" -a omnitool-by-xdv

        # Session cookie settings (CRITICAL for production)
        heroku config:set SESSION_COOKIE_SECURE="true" -a omnitool-by-xdv
        heroku config:set SESSION_COOKIE_SAMESITE="Lax" -a omnitool-by-xdv
        heroku config:set SESSION_COOKIE_HTTPONLY="true" -a omnitool-by-xdv

    # ADD: Wait for Next.js startup
    - name: Verify Dual-Stack Health
      env:
        HEROKU_API_KEY: ${{ secrets.HEROKU_API_KEY }}
        PRODUCTION_URL: https://omnitool-by-xdv-85a1bde25ad1.herokuapp.com
      run: |
        echo "Waiting for both services to be healthy..."
        MAX_RETRIES=30
        RETRY_COUNT=0

        while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
          # Check Flask
          FLASK_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $PRODUCTION_URL/health/ping)

          # Check Next.js
          NEXTJS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $PRODUCTION_URL/api/health)

          if [ "$FLASK_STATUS" = "200" ] && [ "$NEXTJS_STATUS" = "200" ]; then
            echo "✅ Both Flask and Next.js are healthy"
            exit 0
          fi

          RETRY_COUNT=$((RETRY_COUNT + 1))
          echo "Attempt $RETRY_COUNT/$MAX_RETRIES - Flask: $FLASK_STATUS, Next.js: $NEXTJS_STATUS"
          sleep 5
        done

        echo "❌ Services failed to become healthy within timeout"
        exit 1
```

### 10.4 Procfile Changes

```procfile
# BEFORE (current - Flask only)
web: gunicorn main:app

# AFTER (dual-stack)
web: ./scripts/start-production.sh
```

### 10.5 New Files Required

**`frontend/package.json`** - Add scripts:
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest"
  },
  "engines": {
    "node": "20.x"
  }
}
```

**`scripts/start-production.sh`**:
```bash
#!/bin/bash
set -e

echo "Starting dual-stack server..."

# Start Flask in background
gunicorn -b 127.0.0.1:5000 -w 2 --timeout 120 main:app &
FLASK_PID=$!

# Wait for Flask to be ready
echo "Waiting for Flask to start..."
until curl -s http://127.0.0.1:5000/health/ping > /dev/null 2>&1; do
  if ! kill -0 $FLASK_PID 2>/dev/null; then
    echo "❌ Flask process died unexpectedly"
    exit 1
  fi
  sleep 1
done
echo "✅ Flask ready on port 5000"

# Start Next.js in foreground (PORT is set by Heroku)
cd frontend && npm start -- -p $PORT

# Cleanup on exit
trap "kill $FLASK_PID 2>/dev/null" EXIT
```

### 10.6 Staging vs Production Parity

| Setting | Staging | Production |
|---------|---------|------------|
| App Name | `omnitool-by-xdv-staging` | `omnitool-by-xdv` |
| Database | Heroku Postgres (separate) | Heroku Postgres (separate) |
| `FLASK_ENV` | `staging` | `production` |
| `NEXT_PUBLIC_APP_URL` | `https://omnitool-by-xdv-staging-bc1844b846d6.herokuapp.com` | `https://omnitool-by-xdv-85a1bde25ad1.herokuapp.com` |
| Session Cookie Secure | `true` | `true` |
| Buildpacks | python + nodejs | python + nodejs |
| Procfile | `./scripts/start-production.sh` | `./scripts/start-production.sh` |

### 10.7 Rollback Strategy (Dual-Stack)

If deployment fails with the new dual-stack setup:

```bash
# 1. Immediate rollback to Python-only (if Next.js is broken)
heroku buildpacks:clear -a omnitool-by-xdv
heroku buildpacks:add heroku/python -a omnitool-by-xdv

# Revert Procfile to Flask-only
git checkout HEAD~1 -- Procfile
git push heroku main --force

# 2. Database rollback (if migration broke data)
python scripts/rollback_migration.py --env production

# 3. Full rollback to previous release
heroku rollback -a omnitool-by-xdv
```

### 10.8 Implementation Checklist - CI/CD ✅ **COMPLETE**

- [x] **Staging Workflow (`deploy.yml`)**
  - [x] Add Node.js setup step
  - [x] Add frontend test step (lint + Jest)
  - [x] Add frontend build step
  - [x] Configure buildpacks step (python + nodejs)
  - [x] Add frontend environment variables
  - [x] Update smoke tests for dual-stack
- [x] **Production Workflow (`deploy_production.yml`)**
  - [x] Mirror all staging changes
  - [x] Add dual-stack health verification (30 retries, 5s interval)
  - [x] Update rollback documentation
- [x] **Supporting Files**
  - [x] Create `scripts/start-production.sh`
  - [x] Update `Procfile`
  - [x] Ensure `frontend/package.json` has correct `engines.node: "20.x"`
- [ ] **Testing** (pending first deployment)
  - [ ] Deploy to staging first
  - [ ] Verify Flask API works through Next.js proxy
  - [ ] Verify session cookies work cross-stack
  - [ ] Test login/logout flow end-to-end
  - [ ] Confirm health checks pass

---

## 11. Migration Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **SQLite/PostgreSQL behavior differences** | Migrations work locally but fail in staging/production | **SOLVED**: Use Docker PostgreSQL locally (`USE_DOCKER_DB=true`) |
| **Dev database wiped after deployment** | Loss of test data, restore overhead | Use `scripts/export_all_data.py` before push; import after |
| **Docker not installed locally** | Cannot start local PostgreSQL | Provide SQLite fallback (`USE_DOCKER_DB=false`) with warning |
| **Docker PostgreSQL data loss on reset** | Dev data destroyed | Always run `export_all_data.py` before `docker-db reset` |
| Session cookie not shared between Flask/Next.js | Auth breaks | Use same domain, test cookie flow in staging first |
| CSRF token mismatch | All POST requests fail | Implement token refresh on 403 |
| Flask process dies in single dyno | API unavailable | Health check loop, auto-restart in startup script |
| Database connection pool exhaustion | Errors under load | Configure SQLAlchemy pool size, add connection timeout |
| ReCAPTCHA token expiration | Registration fails | Refresh token before submit if > 2min old |
| Heroku buildpack order wrong | Build fails | Document order: Python first, then Node.js |
| Next.js build fails in CI | Staging deploy blocked | Run `npm run build` locally before pushing |
| Memory exceeded on single dyno | App crashes | Monitor memory usage, consider upgrading dyno size |
| Staging/Production env mismatch | Works in staging, fails in prod | Use parity table (10.6), sync all config vars |
| Frontend routes conflict with Flask | 404 errors | Use `/api/*` prefix for all Flask routes |
| Legacy users bookmarked old URLs | Broken links | Add Next.js redirects for legacy routes |

### 11.1 Database Environment Parity

**Problem Solved**: SQLite (dev) and PostgreSQL (staging/prod) have different behaviors, causing migrations to work locally but fail in production.

**Solution**: Docker PostgreSQL for local development provides database parity across all environments.

```bash
# Start Docker PostgreSQL
.\scripts\docker-db.ps1 start   # Windows
./scripts/docker-db.sh start    # Linux/Mac

# Application automatically uses PostgreSQL when USE_DOCKER_DB=true
```

**Backup Workflow**:
```bash
# Before any risky operation
python scripts/export_all_data.py --output data/backups/my_backup.json

# After Docker reset or migration issue
python scripts/import_all_data.py --source data/backups/my_backup.json
```

---

## 12. Success Criteria

Before considering each phase complete:

**Phase 1-2 (Backend):** ✅ **CORE COMPLETE**
- [x] All API endpoints return proper JSON envelope
- [x] Existing HTML routes still work (backward compatibility)
- [ ] API tests pass with 90%+ coverage on services
- [ ] Rate limiting (future feature - requires payment integration)
- [ ] Admin API (`routes/api/admin_api.py`) (future feature)

**Phase 3 (Frontend Auth):** ✅ **COMPLETE**
- [x] User can register, verify email, login, logout
- [x] Unverified users blocked with proper message
- [x] Session expiration handled gracefully
- [x] 31 unit tests passing for auth and UI stores
- [x] Theme persistence works across page reloads
- [x] Responsive layouts for mobile/desktop

**Phase 4 (Tools):** ✅ **COMPLETE**
- [x] Tax Calculator connected to backend API with `toolsApi.calculateTax()`
- [x] Email Templates connected to backend API (CRUD operations)
- [x] Character Counter and Unix Timestamp kept client-side (better UX, no API needed)
- [x] `useToolAccess` hook provides permission-based access control
- [x] `toolsApi` client provides typed API methods for all tool endpoints

**Phase 5 (Production):** ✅ **INFRASTRUCTURE COMPLETE**
- [x] Single dyno starts both Flask and Next.js (`scripts/start-production.sh`)
- [x] Health check endpoints created (`/health/ping`, `/api/health`)
- [x] CI/CD pipelines updated for dual-stack deployment
- [x] Docker PostgreSQL for local development (database parity)
- [x] Comprehensive backup/restore scripts (`export_all_data.py`, `import_all_data.py`)
- [ ] Response times acceptable (< 500ms P95) - pending production load testing