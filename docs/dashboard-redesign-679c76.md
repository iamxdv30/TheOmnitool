# Dashboard Redesign: Tools Discovery UI (Next.js + Flask Backend)

Implement a full-stack "Tools Discovery" dashboard with backend-persisted favorites, categories, and usage history—designed for scalability (1M+ users) with mobile-first responsive React components.

---

## Current State Analysis

### Backend Models (Flask)

| Model | Location | Status | Remarks |
|-------|----------|--------|---------|
| **Tool** | `model/tools.py:62-109` | ✅ Has `name`, `description`, `route`, `is_default` — **needs `category`, `icon`** |
| **UsageLog** | `model/tools.py:5-16` | ✅ Ready (`user_id`, `tool_name`, `timestamp`) |
| **ToolAccess** | `model/tools.py:35-59` | ✅ Links users to tools |
| **ToolFavorite** |  | **Does not exist — needs creation** | --> ✅ **[COMPLETED] `model/tools.py:111-126`** |

### Backend API Endpoints

| Endpoint | Status |
|----------|--------|
| `GET /api/v1/tools/` | ✅ Returns all tools with `hasAccess` flag |
| `GET /api/v1/user/tools` | ✅ Returns user's accessible tool names |
| `GET /api/v1/user/usage` | ⚠️ Returns aggregated counts only — **needs recent activity endpoint** |
| `POST/DELETE /api/v1/user/favorites` | ❌ **Does not exist** |

### Frontend (Next.js)

| Component | Location | Status |
|-----------|----------|--------|
| **Dashboard Page** | `frontend/src/app/(dashboard)/dashboard/page.tsx` | Basic grid, no search/filters |
| **Sidebar** | `frontend/src/components/layout/Sidebar.tsx` | ✅ Complete |
| **Card Components** | `frontend/src/components/ui/Card.tsx` | ✅ Multiple variants |
| **Tools API Client** | `frontend/src/lib/api/tools.ts` | ⚠️ Needs favorites/history methods |

---

## Implementation Plan

### Phase 1: Backend — Database Schema Updates

#### 1A. Tool Metadata & Categories
- [X] **Add columns to `Tool` model:**
  - `icon` (String, nullable) — Lucide icon name (e.g., "calculator", "file-text")
  - `display_name` (String, nullable) — Human-readable name
  - `category_id` (Integer, FK) — Reference to `ToolCategory`
  - `is_paid` (Boolean, default=False) — Whether tool requires subscription
  - `required_plan_id` (Integer, FK, nullable) — Minimum plan required (null = free)
- [X] **Create `ToolCategory` model (admin-manageable):**
  ```python
  class ToolCategory(db.Model):
      __tablename__ = "tool_categories"
      id = db.Column(db.Integer, primary_key=True)
      name = db.Column(db.String(50), unique=True, nullable=False)  # "Finance", "Dev"
      slug = db.Column(db.String(50), unique=True, nullable=False)  # "finance", "dev"
      icon = db.Column(db.String(50), nullable=True)  # Optional category icon
      color = db.Column(db.String(20), nullable=True)  # Tailwind class e.g. "text-success"
      display_order = db.Column(db.Integer, default=0)  # For sorting in UI
      is_active = db.Column(db.Boolean, default=True)
      created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
      
      tools = db.relationship("Tool", back_populates="category")
  ```

#### 1B. Subscription System (Future-Ready for Paid Tools)
- [X] **Create `SubscriptionPlan` model (admin-manageable):**
  ```python
  class SubscriptionPlan(db.Model):
      __tablename__ = "subscription_plans"
      id = db.Column(db.Integer, primary_key=True)
      name = db.Column(db.String(50), unique=True, nullable=False)  # "Free", "Basic", "Pro"
      slug = db.Column(db.String(50), unique=True, nullable=False)  # "free", "basic", "pro"
      tier_level = db.Column(db.Integer, nullable=False, default=0)  # 0=Free, 1=Basic, 2=Pro
      price_monthly = db.Column(db.Numeric(10, 2), nullable=True)  # null = free
      price_yearly = db.Column(db.Numeric(10, 2), nullable=True)
      features = db.Column(db.JSON, nullable=True)  # {"max_tools": 5, "priority_support": true}
      is_active = db.Column(db.Boolean, default=True)
      created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
  ```
- [X] **Create `UserSubscription` model (payment provider-agnostic):**
  ```python
  class UserSubscription(db.Model):
      __tablename__ = "user_subscriptions"
      id = db.Column(db.Integer, primary_key=True)
      user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
      plan_id = db.Column(db.Integer, db.ForeignKey("subscription_plans.id"), nullable=False)
      status = db.Column(db.String(20), default="active")  # active, cancelled, expired, trial, pending
      billing_cycle_id = db.Column(db.Integer, db.ForeignKey("billing_cycles.id"), nullable=False)
      started_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
      expires_at = db.Column(db.DateTime, nullable=True)  # null = lifetime/free
      cancelled_at = db.Column(db.DateTime, nullable=True)
      
      # Provider-agnostic payment fields (works with ANY payment gateway)
      payment_provider_id = db.Column(db.Integer, db.ForeignKey("payment_providers.id"), nullable=True)
      external_subscription_id = db.Column(db.String(255), nullable=True)  # Provider's subscription ID
      external_customer_id = db.Column(db.String(255), nullable=True)  # Provider's customer ID
      external_transaction_id = db.Column(db.String(255), nullable=True)  # Last payment transaction ID
      currency = db.Column(db.String(3), default="USD")  # ISO currency code
      
      user = db.relationship("User", back_populates="subscriptions")
      plan = db.relationship("SubscriptionPlan")
      billing_cycle_ref = db.relationship("BillingCycle", back_populates="subscriptions")
      payment_provider_ref = db.relationship("PaymentProvider", back_populates="subscriptions")
  ```
- [X] **Create `PaymentProvider` table (admin-manageable):**
  ```python
  class PaymentProvider(db.Model):
      __tablename__ = "payment_providers"
      id = db.Column(db.Integer, primary_key=True)
      code = db.Column(db.String(50), unique=True, nullable=False)
      name = db.Column(db.String(50), unique=True, nullable=False)
      is_active = db.Column(db.Boolean, default=True)
      supported_currencies = db.Column(db.JSON, nullable=True)
  ```
- [X] **Create `BillingCycle` table (long-term manageable):**
  ```python
  class BillingCycle(db.Model):
      __tablename__ = "billing_cycles"
      id = db.Column(db.Integer, primary_key=True)
      code = db.Column(db.String(20), unique=True, nullable=False)  # monthly, yearly, lifetime
      name = db.Column(db.String(50), nullable=False)
      display_order = db.Column(db.Integer, default=0)
      is_active = db.Column(db.Boolean, default=True)
  ```

#### 1C. Favorites
- [X] **Create `ToolFavorite` model:**
  ```python
  class ToolFavorite(db.Model):
      __tablename__ = "tool_favorites"
      id = db.Column(db.Integer, primary_key=True)
      user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
      tool_id = db.Column(db.Integer, db.ForeignKey("tools.id"), nullable=False)
      created_at = db.Column(db.DateTime, default=datetime.utcnow)
      __table_args__ = (db.UniqueConstraint('user_id', 'tool_id', name='uq_user_tool_favorite'),)
  ```

#### 1D. Migration & Seed Data
- [X] **Create and apply migrations:**
  - `flask db migrate -m "Add categories, subscriptions, favorites, tool metadata"`
  - `flask db migrate -m "Add billing_cycles table and billing_cycle_id FK"`
  - `python scripts/migrate_db.py` (schema + tool sync only)
- [X] **Seed subscription plans:**
  ```python
  plans = [
      {"name": "Free", "slug": "free", "tier_level": 0, "price_monthly": None},
      {"name": "Basic", "slug": "basic", "tier_level": 1, "price_monthly": 9.99},
      {"name": "Pro", "slug": "pro", "tier_level": 2, "price_monthly": 29.99},
  ]
  ```
- [X] **Seed categories:**
  ```python
  categories = [
      {"name": "Finance", "slug": "finance", "color": "text-success", "display_order": 1},
      {"name": "Development", "slug": "dev", "color": "text-warning", "display_order": 2},
      {"name": "Writing", "slug": "writing", "color": "text-info", "display_order": 3},
      {"name": "Marketing", "slug": "marketing", "color": "text-accent", "display_order": 4},
  ]
  ```
- [X] **Seed billing cycles:**
  ```python
  billing_cycles = [
      {"code": "monthly", "name": "Monthly", "display_order": 1},
      {"code": "yearly", "name": "Yearly", "display_order": 2},
      {"code": "lifetime", "name": "Lifetime", "display_order": 3},
  ]
  ```
- [X] **Assign all existing users (including admins) to waived-forever Pro access**
  - `plan = Pro`
  - `billing_cycle = lifetime`
  - `expires_at = null`
  - `payment_provider_id = null`
  - run via: `python scripts/seed_phase1_dashboard_data.py`

#### 1E. Phase 1 Delivery Notes (Added During Implementation)
- [X] **Separated schema migration from seed data responsibilities:**
  - `scripts/migrate_db.py` now handles schema migration + tool sync only.
  - `scripts/seed_phase1_dashboard_data.py` handles providers, plans, categories, billing cycles, and subscription assignment.
- [X] **Added migration backfill safety for billing cycle refactor:**
  - Migrates legacy `user_subscriptions.billing_cycle` string values into `billing_cycle_id` before dropping old column.
- [X] **Standardized relationship consistency:**
  - `back_populates` pairs are explicitly defined for `UserSubscription` with `User`, `PaymentProvider`, and `BillingCycle`.

### Phase 2: Backend — New API Endpoints

> **Architecture context from Phase 1:**
> - API blueprint at `/api/v1` with sub-blueprints: `auth_api_bp` (`/auth`), `user_api_bp` (`/user`), `tool_api_bp` (`/tools`)
> - Decorators: `@require_auth`, `@require_verified`, `@require_role(*roles)` — defined in `routes/api/__init__.py`
> - Response helpers: `api_response(data)`, `api_error(code, message, status_code)` — defined in `routes/api/__init__.py`
> - Service layer: `ToolService` (`services/tool_service.py`), `UserService` (`services/user_service.py`)
> - All services return `ServiceResult[T]` with `.is_success`, `.is_failure`, `.data`, `.error`
> - Registration via `register_api_routes()` in `routes/api/__init__.py:273-290`
> - Models available: `ToolFavorite` (`model/tools.py:134-142`), `ToolCategory` (`model/tools.py:120-132`), `UserSubscription` (`model/subscription.py:31-52`), `SubscriptionPlan` (`model/subscription.py:5-15`), `UsageLog` (`model/tools.py:7-18`)

#### 2A. Favorites Endpoints (add to `routes/api/user_api.py`)
- [X] **`GET /api/v1/user/favorites`** — List user's favorited tool IDs
  - Uses `@require_auth`
  - Queries `ToolFavorite` by `user_id` (model has `user_id`, `tool_id`, `created_at`)
  - Returns: `{"favorites": [tool_id, ...]}`
- [X] **`POST /api/v1/user/favorites/<int:tool_id>`** — Add favorite
  - Uses `@require_auth`
  - Creates `ToolFavorite(user_id=session['user_id'], tool_id=tool_id)`
  - Respects `UniqueConstraint('user_id', 'tool_id', name='uq_user_tool_favorite')`
  - Returns 201 on success, 409 if already favorited
- [X] **`DELETE /api/v1/user/favorites/<int:tool_id>`** — Remove favorite
  - Uses `@require_auth`
  - Deletes `ToolFavorite` matching `(user_id, tool_id)`
  - Returns 204 on success, 404 if not found
- [X] **Add service methods to `services/tool_service.py`:**
  - `get_user_favorites(user_id) → ServiceResult[List[int]]`
  - `add_favorite(user_id, tool_id) → ServiceResult[bool]`
  - `remove_favorite(user_id, tool_id) → ServiceResult[bool]`

#### 2B. Usage History Endpoint (add to `routes/api/user_api.py`)
- [ ] **`GET /api/v1/user/usage-history`** — Return recent `UsageLog` entries (paginated)
  - Uses `@require_auth`
  - Existing `GET /api/v1/user/usage` only returns aggregated counts (`{tool_name: count}`)
  - New endpoint returns actual log entries: `UsageLog` has `user_id`, `tool_name`, `timestamp`
  - Query params: `?limit=10&offset=0`
  - Returns: `{"history": [{"tool_name": "...", "timestamp": "ISO8601"}, ...], "total": int}`
- [ ] **Add service method to `services/tool_service.py`:**
  - `get_usage_history(user_id, limit=10, offset=0) → ServiceResult[dict]`

#### 2C. Subscription Read Endpoint (add to `routes/api/user_api.py`)
- [ ] **`GET /api/v1/user/subscription`** — Get user's current subscription status
  - Uses `@require_auth`
  - Queries `UserSubscription` by `user_id` (Phase 1 assigned all users waived-forever Pro)
  - Joins `SubscriptionPlan` for plan details and `BillingCycle` for cycle info
  - Returns:
    ```json
    {
      "subscription": {
        "plan": {"id": 2, "name": "Pro", "slug": "pro", "tier_level": 2},
        "status": "active",
        "billing_cycle": "lifetime",
        "started_at": "ISO8601",
        "expires_at": null
      }
    }
    ```
- [ ] **Add service method to `services/tool_service.py` (or new `services/subscription_service.py`):**
  - `get_user_subscription(user_id) → ServiceResult[dict]`

#### 2D. Tool & Category Endpoints (modify `routes/api/tool_api.py`)
- [ ] **`GET /api/v1/tools/categories`** — List all active categories (for filter pills)
  - Uses `@require_auth`
  - Queries `ToolCategory` where `is_active=True`, ordered by `display_order`
  - Seeded categories (Phase 1): Finance, Development, Writing, Marketing
  - Returns: `{"categories": [{"id": 1, "name": "Finance", "slug": "finance", "color": "text-success", "icon": "coins"}, ...]}`
- [ ] **Update `GET /api/v1/tools/` response** — Include new Phase 1 fields in response
  - Current response (`tool_api.py:114-121`) only returns `id`, `name`, `description`, `route`, `is_default`, `hasAccess`
  - **Add:** `icon`, `display_name`, `is_paid`, `required_plan`, nested `category` object
  - Update `ToolInfo` dataclass (`services/tool_service.py:25-44`) to include:
    - `icon: Optional[str]`
    - `category_id: Optional[int]`
    - `category_name: Optional[str]`
    - `category_slug: Optional[str]`
    - `category_color: Optional[str]`
    - `is_paid: bool`
    - `required_plan_id: Optional[int]`
    - `required_plan_name: Optional[str]`
    - `required_plan_tier: Optional[int]`
  - Update `_tool_to_info()` helper (`services/tool_service.py:629-639`) to populate new fields from `Tool.category` and `Tool.required_plan_id` relationships
  - Update response builder (`tool_api.py:106-122`) to include new fields
- [ ] **Add service method:** `get_categories() → ServiceResult[List[dict]]`

#### 2E. Access Control Updates (modify `services/tool_service.py`)
- [ ] **Extend `check_tool_access()` (`services/tool_service.py:162-198`):**
  ```python
  def check_tool_access(self, user_id, tool_name, user_role=None):
      # 1. Admins/SuperAdmins bypass all checks (existing, line 182)
      # 2. Check explicit ToolAccess record (existing, line 186-188)
      # 3. NEW: If tool.is_paid, check user's subscription tier:
      #    - Query UserSubscription for user_id where status='active'
      #    - Compare plan.tier_level >= tool.required_plan.tier_level
      #    - Tool model has: is_paid (bool), required_plan_id (FK → subscription_plans.id)
      #    - SubscriptionPlan model has: tier_level (int) — 0=Free, 1=Basic, 2=Pro
  ```
- [ ] **Update `check_tool_access()` in `routes/api/tool_api.py:28-55`** to pass subscription context

#### 2F. Subscription Management Endpoints (future — payment integration)
> **Note:** These endpoints are deferred until a payment provider is integrated.
> Phase 1 seeded 11 payment providers in `payment_providers` table and created the
> `PaymentProvider` model (`model/subscription.py:55-65`). The Strategy Pattern
> architecture (`services/payment/base.py` → `PaymentProviderInterface`) should be
> created when the first provider is integrated.

- [ ] **`GET /api/v1/tools/plans`** — List available subscription plans
  - Queries `SubscriptionPlan` where `is_active=True`
  - Seeded plans (Phase 1): Free (tier 0), Basic (tier 1, $9.99/mo), Pro (tier 2, $29.99/mo)
- [ ] **`POST /api/v1/user/subscription`** — Create/upgrade subscription (requires payment provider)
- [ ] **`DELETE /api/v1/user/subscription`** — Cancel subscription
- [ ] **`POST /api/v1/webhooks/<provider>`** — Webhook endpoints per provider
- [ ] **Create `services/subscription_service.py`** — Subscription management logic
- [ ] **Create `services/payment/` directory** — Payment provider implementations
  - `base.py` — `PaymentProviderInterface` abstract class
  - `stripe_provider.py` — Stripe implementation (first provider)

#### 2G. Phase 2 Delivery Checklist
- [ ] **Update `routes/api/__init__.py:273-290`** — No new sub-blueprints needed (favorites/usage-history/subscription go on existing `user_api_bp`; categories goes on existing `tool_api_bp`)
- [ ] **Update `services/__init__.py`** — Export any new service classes/functions
- [ ] **Add validation schemas** to `routes/api/schemas.py` if needed (e.g., `FavoriteSchema`)
- [ ] **Update `GET /api/v1/user/dashboard`** (`user_api.py:274-308`) — Include favorites and subscription in the combined dashboard response

### Phase 3: Frontend — API Client Updates
- [ ] Add to `frontend/src/lib/api/tools.ts`:
  - `getCategories()` — Fetch dynamic category list
  - `getFavorites()` / `addFavorite(toolId)` / `removeFavorite(toolId)`
  - `getUsageHistory(limit?)`
- [ ] Add to `frontend/src/lib/api/subscription.ts` (new file):
  - `getPlans()` / `getUserSubscription()` / `subscribeToPlan(planId)`
- [ ] Update `ToolInfo` interface with `is_paid`, `required_plan`, nested `category`
- [ ] Create `Category`, `SubscriptionPlan`, `UserSubscription` interfaces

### Phase 4: Frontend — Reusable UI Components
- [ ] **`SearchInput.tsx`** — Debounced search input with icon
- [ ] **`Badge.tsx`** — Category badge component
- [ ] **`CategoryFilter.tsx`** — Filter pills ("All", "Favorites", "Dev", "Finance", etc.)

### Phase 5: Frontend — Dashboard Feature Components
- [ ] **`ToolCard.tsx`** — Enhanced card with favorite toggle, category badge, **paid/locked indicator**
- [ ] **`ToolsGrid.tsx`** — Responsive grid with search/filter logic
- [ ] **`UsageHistory.tsx`** — Recent activity card
- [ ] **`UpgradeBanner.tsx`** — Optional banner prompting upgrade for locked tools

### Phase 6: Frontend — Dashboard Page Refactor
- [ ] Integrate new components into `page.tsx`
- [ ] Add state: `searchQuery`, `activeCategory`, `favorites`
- [ ] Implement filtering logic
- [ ] Fetch favorites and usage history on mount

### Phase 7: Testing
- [ ] Unit tests for new API endpoints (pytest)
- [ ] Frontend component tests (Jest + RTL)
- [ ] Responsive testing: 320px / 768px / 1024px+
- [ ] Theme toggle verification

---

## Design Reference (from image)

| Component | Details |
|-----------|---------|
| **Header** | "Tools Discovery" title, subtitle |
| **Search** | Full-width, placeholder "Search tools..." |
| **Filters** | Pills: All Tools, Favorites, Dev, Finance, Writing |
| **Tool Cards** | Icon, title, description (2 lines), category badge, "Launch →", favorite heart |
| **Grid** | 3 cols desktop, 2 tablet, 1 mobile |
| **Usage Section** | "Usage & History" header, total count, recent activity list |

---

## Files to Create/Modify

### Backend (Flask)

| File | Action |
|------|--------|
| `model/tools.py` | **Modify** — Add `icon`, `display_name`, `category_id`, `is_paid`, `required_plan_id` to `Tool`; Create `ToolCategory`, `ToolFavorite` |
| `model/subscription.py` | **Create/Modify** — `SubscriptionPlan`, `UserSubscription`, `PaymentProvider`, `BillingCycle` models |
| `model/__init__.py` | **Modify** — Export `ToolCategory`, `ToolFavorite`, `SubscriptionPlan`, `UserSubscription`, `PaymentProvider`, `BillingCycle` |
| `scripts/migrate_db.py` | **Modify** — Keep schema migration + tool sync only (no business/data seed steps) |
| `scripts/seed_phase1_dashboard_data.py` | **Create** — Seed providers, plans, categories, billing cycles; assign waived-forever Pro to existing users |
| `routes/api/user_api.py` | **Modify** — Add favorites, usage-history, subscription endpoints |
| `routes/api/tool_api.py` | **Modify** — Add `/categories`, `/plans` endpoints; Update access control for paid tools |
| `services/tool_service.py` | **Modify** — Add favorites, history, subscription service methods |
| `services/subscription_service.py` | **Create** — Subscription management logic |
| `services/payment/` | **Create** — Payment provider directory |
| `services/payment/base.py` | **Create** — `PaymentProviderInterface` abstract class |
| `services/payment/stripe_provider.py` | **Create** — Stripe implementation (initial) |
| `services/payment/paypal_provider.py` | **Create** — PayPal implementation (optional) |
| `migrations/versions/xxx_add_tool_metadata.py` | **Create** (auto-generated) |

### Frontend (Next.js)

| File | Action |
|------|--------|
| `frontend/src/lib/api/tools.ts` | **Modify** — Add `getCategories()`, favorites, history methods |
| `frontend/src/lib/api/subscription.ts` | **Create** — Subscription API client |
| `frontend/src/types/index.ts` | **Modify** — Update `ToolInfo` interface |
| `frontend/src/components/ui/SearchInput.tsx` | **Create** |
| `frontend/src/components/ui/Badge.tsx` | **Create** |
| `frontend/src/components/ui/index.ts` | **Modify** — Add exports |
| `frontend/src/components/features/dashboard/ToolCard.tsx` | **Create** |
| `frontend/src/components/features/dashboard/CategoryFilter.tsx` | **Create** |
| `frontend/src/components/features/dashboard/ToolsGrid.tsx` | **Create** |
| `frontend/src/components/features/dashboard/UsageHistory.tsx` | **Create** |
| `frontend/src/components/features/dashboard/index.ts` | **Create** |
| `frontend/src/app/(dashboard)/dashboard/page.tsx` | **Modify** |

---

## Recommendations & Gap Analysis

### 1. Favorites — Backend vs localStorage

| Approach | Pros | Cons |
|----------|------|------|
| **Backend (Recommended)** | Persists across devices, survives cache clear, analytics-ready, scales to 1M users | Requires API calls, slight latency |
| localStorage | Fast, no backend changes | Lost on device change, no cross-device sync, no analytics |

**Recommendation:** Use backend with proper indexing on `(user_id)` for O(1) lookups.

### 2. Categories — Separate Table (Future-Ready)

| Approach | Pros | Cons |
|----------|------|------|
| Column on Tool | Simple queries | Not expandable without code changes |
| **Separate ToolCategory table (Chosen)** | Admin-manageable, expandable, supports color/icon per category, sortable | One extra join |

**Benefits of `ToolCategory` table:**
- Admins can add/rename/reorder categories without code deployment
- Each category can have its own color and icon
- `display_order` allows custom sorting in filter pills
- `is_active` allows soft-delete without breaking existing tool references
- Future-ready for many-to-many if needed (add junction table later)

### 3. Subscriptions — Separate Tables (Future-Ready for Payments)

| Approach | Pros | Cons |
|----------|------|------|
| Column on User (`tier`) | Simplest | No history, no billing integration |
| **Separate SubscriptionPlan + UserSubscription (Chosen)** | Payment-ready, history tracking, expiry support, Stripe-compatible | More tables |

**Benefits of separate subscription tables:**
- `SubscriptionPlan`: Admins can add/modify plans without code changes (Free, Basic, Pro, Enterprise)
- `UserSubscription`: Tracks status, expiry, billing cycle — essential for paid subscriptions
- `payment_provider`: Stores which provider processed the payment (provider-agnostic)
- `tier_level`: Integer comparison for access control (`user.tier_level >= tool.required_plan.tier_level`)
- Supports trial periods, cancellation dates, subscription history

### 3a. Global Payment Provider Support

| Region | Recommended Providers |
|--------|----------------------|
| **Global** | Stripe, PayPal, Paddle |
| **EU** | Mollie (iDEAL, SEPA, Bancontact), Stripe |
| **Asia (India)** | Razorpay, Stripe |
| **Asia (SEA)** | Omise, Xendit, PayMongo |
| **Latin America** | MercadoPago, Stripe |
| **Africa** | Flutterwave, Paystack |
| **Manual** | Bank transfer with admin verification |

**Architecture Pattern: Strategy Pattern for Payment Providers**
```python
# services/payment/base.py
class PaymentProviderInterface(ABC):
    @abstractmethod
    def create_subscription(self, user, plan, currency): pass
    
    @abstractmethod
    def cancel_subscription(self, subscription_id): pass
    
    @abstractmethod
    def verify_webhook(self, payload, signature): pass

# services/payment/stripe_provider.py
class StripeProvider(PaymentProviderInterface): ...

# services/payment/paypal_provider.py  
class PayPalProvider(PaymentProviderInterface): ...

# Factory to get the right provider
def get_payment_provider(provider_name: str) -> PaymentProviderInterface:
    providers = {
        "stripe": StripeProvider,
        "paypal": PayPalProvider,
        # Add more as needed
    }
    return providers[provider_name]()
```

### 4. Usage History — Existing UsageLog

The `UsageLog` model is already perfect. Current `/user/usage` endpoint returns aggregated counts—we just need a new endpoint that returns the actual log entries with timestamps for "recent activity" display.

### 5. Database Indexing for Scale

```python
# Add to ToolFavorite for 1M user performance
__table_args__ = (
    db.Index('ix_tool_favorites_user_id', 'user_id'),
    db.UniqueConstraint('user_id', 'tool_id', name='uq_user_tool_favorite'),
)
```

---

## Initial Seed Data

### Categories (`tool_categories` table)

| name | slug | color | icon | display_order |
|------|------|-------|------|---------------|
| Finance | finance | text-success | `coins` | 1 |
| Development | dev | text-warning | `code` | 2 |
| Writing | writing | text-info | `pen-line` | 3 |
| Marketing | marketing | text-accent | `megaphone` | 4 |

### Subscription Plans (`subscription_plans` table)

| name | slug | tier_level | price_monthly | price_yearly |
|------|------|------------|---------------|--------------|
| Free | free | 0 | null | null |
| Basic | basic | 1 | 9.99 | 99.99 |
| Pro | pro | 2 | 29.99 | 299.99 |

### Tools → Category + Plan Mapping

| Tool Name | Category | Tool Icon | is_paid | required_plan |
|-----------|----------|-----------|---------|---------------|
| Tax Calculator | Finance | `calculator` | false | null (Free) |
| Character Counter | Writing | `file-text` | false | null (Free) |
| Unix Timestamp | Development | `clock` | false | null (Free) |
| Email Templates | Marketing | `mail` | false | null (Free) |
| *(future paid tool)* | *(category)* | *(icon)* | **true** | Basic (tier 1) |

---

## API Response Examples

### `GET /api/v1/categories`
```json
{
  "categories": [
    {"id": 1, "name": "Finance", "slug": "finance", "color": "text-success", "icon": "coins"},
    {"id": 2, "name": "Development", "slug": "dev", "color": "text-warning", "icon": "code"},
    ...
  ]
}
```

### `GET /api/v1/tools/` (updated response)
```json
{
  "tools": [
    {
      "id": 1,
      "name": "tax-calculator",
      "display_name": "Tax Calculator",
      "description": "Calculate taxes for US, Canada, and VAT",
      "icon": "calculator",
      "category": {"id": 1, "name": "Finance", "slug": "finance", "color": "text-success"},
      "is_paid": false,
      "required_plan": null,
      "hasAccess": true
    },
    {
      "id": 5,
      "name": "advanced-analytics",
      "display_name": "Advanced Analytics",
      "description": "Premium analytics dashboard",
      "icon": "bar-chart",
      "category": {"id": 2, "name": "Development", "slug": "dev", "color": "text-warning"},
      "is_paid": true,
      "required_plan": {"id": 2, "name": "Pro", "tier_level": 2},
      "hasAccess": false
    }
  ]
}
```

### `GET /api/v1/user/subscription`
```json
{
  "subscription": {
    "plan": {"id": 1, "name": "Free", "tier_level": 0},
    "status": "active",
    "expires_at": null
  }
}
```
