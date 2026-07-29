"""
Dashboard Redesign API Tests (Phase 2)

Tests for the endpoints added by the dashboard redesign plan:
- GET  /api/v1/user/usage-history
- GET  /api/v1/user/subscription
- GET  /api/v1/user/dashboard (favorites + subscription included)
- GET  /api/v1/tools/categories
- GET  /api/v1/tools/plans
- GET  /api/v1/tools/ (Phase 1 fields + hasAccess fix)
- Favorites endpoints
- Paid tool access control via subscription tier
"""

import pytest
from datetime import datetime, timezone

from model import (
    db, User, Tool, ToolAccess, ToolCategory, ToolFavorite, UsageLog,
    SubscriptionPlan, BillingCycle, UserSubscription
)


@pytest.fixture
def dashboard_data(app, init_database):
    """Seed categories, plans, billing cycles, usage logs, and a paid tool."""
    with app.app_context():
        category = ToolCategory(name="Finance", slug="finance",
                                color="text-success", icon="coins", display_order=1)
        inactive_category = ToolCategory(name="Hidden", slug="hidden", is_active=False)

        free_plan = SubscriptionPlan(name="Free", slug="free", tier_level=0)
        pro_plan = SubscriptionPlan(name="Pro", slug="pro", tier_level=2,
                                    price_monthly=29.99, price_yearly=299.99)

        lifetime = BillingCycle(code="lifetime", name="Lifetime", display_order=3)

        db.session.add_all([category, inactive_category, free_plan, pro_plan, lifetime])
        db.session.commit()

        # Paid tool requiring Pro tier
        paid_tool = Tool(name="Premium Tool", description="Paid tool",
                         route="/premium", is_default=False)
        paid_tool.is_paid = True
        paid_tool.required_plan_id = pro_plan.id
        paid_tool.category_id = category.id
        paid_tool.icon = "bar-chart"
        db.session.add(paid_tool)

        user = User.query.filter_by(username="testuser").first()

        # Usage logs
        for tool_name in ["Test Tool 1", "Test Tool 1", "Test Tool 2"]:
            db.session.add(UsageLog(user_id=user.id, tool_name=tool_name,
                                    timestamp=datetime.now(timezone.utc)))
        db.session.commit()

        yield {
            "pro_plan_id": pro_plan.id,
            "lifetime_id": lifetime.id,
            "paid_tool_id": paid_tool.id,
            "category_id": category.id,
            "user_id": user.id,
        }


def login(client, username="testuser", password="testpass"):
    return client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
        content_type="application/json",
    )


class TestUsageHistoryAPI:
    def test_requires_auth(self, client, init_database):
        response = client.get("/api/v1/user/usage-history")
        assert response.status_code == 401

    def test_returns_recent_entries(self, client, dashboard_data):
        login(client)
        response = client.get("/api/v1/user/usage-history")

        assert response.status_code == 200
        data = response.get_json()["data"]
        assert data["total"] == 3
        assert len(data["history"]) == 3
        assert {"tool_name", "timestamp"} <= set(data["history"][0].keys())

    def test_pagination(self, client, dashboard_data):
        login(client)
        response = client.get("/api/v1/user/usage-history?limit=2&offset=2")

        data = response.get_json()["data"]
        assert data["total"] == 3
        assert len(data["history"]) == 1

    def test_invalid_params(self, client, dashboard_data):
        login(client)
        response = client.get("/api/v1/user/usage-history?limit=abc")
        assert response.status_code == 400


class TestSubscriptionAPI:
    def test_requires_auth(self, client, init_database):
        response = client.get("/api/v1/user/subscription")
        assert response.status_code == 401

    def test_no_subscription_returns_null(self, client, dashboard_data):
        login(client)
        response = client.get("/api/v1/user/subscription")

        assert response.status_code == 200
        assert response.get_json()["data"]["subscription"] is None

    def test_active_subscription(self, app, client, dashboard_data):
        with app.app_context():
            db.session.add(UserSubscription(
                user_id=dashboard_data["user_id"],
                plan_id=dashboard_data["pro_plan_id"],
                billing_cycle_id=dashboard_data["lifetime_id"],
                status="active",
            ))
            db.session.commit()

        login(client)
        response = client.get("/api/v1/user/subscription")

        sub = response.get_json()["data"]["subscription"]
        assert sub["plan"]["name"] == "Pro"
        assert sub["plan"]["tier_level"] == 2
        assert sub["status"] == "active"
        assert sub["billing_cycle"] == "lifetime"
        assert sub["expires_at"] is None

    def test_expired_subscription_ignored(self, app, client, dashboard_data):
        with app.app_context():
            db.session.add(UserSubscription(
                user_id=dashboard_data["user_id"],
                plan_id=dashboard_data["pro_plan_id"],
                billing_cycle_id=dashboard_data["lifetime_id"],
                status="active",
                expires_at=datetime(2020, 1, 1),
            ))
            db.session.commit()

        login(client)
        response = client.get("/api/v1/user/subscription")
        assert response.get_json()["data"]["subscription"] is None


class TestCategoriesAPI:
    def test_requires_auth(self, client, init_database):
        response = client.get("/api/v1/tools/categories")
        assert response.status_code == 401

    def test_lists_active_categories_only(self, client, dashboard_data):
        login(client)
        response = client.get("/api/v1/tools/categories")

        assert response.status_code == 200
        categories = response.get_json()["data"]["categories"]
        slugs = [c["slug"] for c in categories]
        assert "finance" in slugs
        assert "hidden" not in slugs
        finance = next(c for c in categories if c["slug"] == "finance")
        assert finance["color"] == "text-success"
        assert finance["icon"] == "coins"


class TestPlansAPI:
    def test_requires_auth(self, client, init_database):
        response = client.get("/api/v1/tools/plans")
        assert response.status_code == 401

    def test_lists_plans_ordered_by_tier(self, client, dashboard_data):
        login(client)
        response = client.get("/api/v1/tools/plans")

        plans = response.get_json()["data"]["plans"]
        tiers = [p["tier_level"] for p in plans]
        assert tiers == sorted(tiers)
        pro = next(p for p in plans if p["slug"] == "pro")
        assert pro["price_monthly"] == 29.99


class TestToolsListAPI:
    def test_default_tool_does_not_require_explicit_grant(
        self, app, client, dashboard_data
    ):
        with app.app_context():
            ToolAccess.query.filter_by(
                user_id=dashboard_data["user_id"],
                tool_name="Test Tool 1",
            ).delete()
            db.session.commit()

            from services import get_tool_service

            access_result = get_tool_service().check_tool_access(
                dashboard_data["user_id"], "Test Tool 1"
            )
            assert access_result.is_success
            assert access_result.data is True

        login(client)
        permissions_response = client.get("/api/v1/user/tools")
        tools_response = client.get("/api/v1/tools")

        assert "Test Tool 1" in permissions_response.get_json()["data"]["tools"]
        tools = tools_response.get_json()["data"]["tools"]
        default_tool = next(tool for tool in tools if tool["name"] == "Test Tool 1")
        assert default_tool["hasAccess"] is True

    def test_accepts_slashless_url_without_redirect(self, client, dashboard_data):
        login(client)
        response = client.get("/api/v1/tools")

        assert response.status_code == 200

    def test_includes_phase1_fields_and_access(self, client, dashboard_data):
        login(client)
        response = client.get("/api/v1/tools/")

        tools = {t["name"]: t for t in response.get_json()["data"]["tools"]}

        # Regular user has explicit access to Test Tool 1 only
        assert tools["Test Tool 1"]["hasAccess"] is True
        assert tools["Test Tool 2"]["hasAccess"] is False

        premium = tools["Premium Tool"]
        assert premium["is_paid"] is True
        assert premium["icon"] == "bar-chart"
        assert premium["category"]["slug"] == "finance"
        assert premium["required_plan"]["tier_level"] == 2
        assert premium["hasAccess"] is False

    def test_paid_tool_unlocked_by_subscription(self, app, client, dashboard_data):
        with app.app_context():
            db.session.add(UserSubscription(
                user_id=dashboard_data["user_id"],
                plan_id=dashboard_data["pro_plan_id"],
                billing_cycle_id=dashboard_data["lifetime_id"],
                status="active",
            ))
            db.session.commit()

        login(client)
        response = client.get("/api/v1/tools/")
        tools = {t["name"]: t for t in response.get_json()["data"]["tools"]}
        assert tools["Premium Tool"]["hasAccess"] is True

    def test_admin_has_access_to_all(self, client, dashboard_data):
        login(client, "adminuser", "adminpass")
        response = client.get("/api/v1/tools/")
        tools = response.get_json()["data"]["tools"]
        assert all(t["hasAccess"] for t in tools)


class TestPaidToolAccessControl:
    def test_check_tool_access_with_tier(self, app, dashboard_data):
        from services import get_tool_service

        with app.app_context():
            tool_service = get_tool_service()
            user_id = dashboard_data["user_id"]

            # No subscription: no access to paid tool
            result = tool_service.check_tool_access(user_id, "Premium Tool")
            assert result.is_success and result.data is False

            db.session.add(UserSubscription(
                user_id=user_id,
                plan_id=dashboard_data["pro_plan_id"],
                billing_cycle_id=dashboard_data["lifetime_id"],
                status="active",
            ))
            db.session.commit()

            # Pro subscription meets tier requirement
            result = tool_service.check_tool_access(user_id, "Premium Tool")
            assert result.is_success and result.data is True


class TestFavoritesAPI:
    def test_favorites_flow(self, client, dashboard_data):
        login(client)
        tool_id = dashboard_data["paid_tool_id"]

        # Initially empty
        response = client.get("/api/v1/user/favorites")
        assert response.get_json()["data"]["favorites"] == []

        # Add
        response = client.post(f"/api/v1/user/favorites/{tool_id}")
        assert response.status_code == 201

        # Duplicate rejected
        response = client.post(f"/api/v1/user/favorites/{tool_id}")
        assert response.status_code == 409

        # Listed
        response = client.get("/api/v1/user/favorites")
        assert tool_id in response.get_json()["data"]["favorites"]

        # Remove
        response = client.delete(f"/api/v1/user/favorites/{tool_id}")
        assert response.status_code == 204

        # Remove again → 404
        response = client.delete(f"/api/v1/user/favorites/{tool_id}")
        assert response.status_code == 404

    def test_add_favorite_unknown_tool(self, client, dashboard_data):
        login(client)
        response = client.post("/api/v1/user/favorites/999999")
        assert response.status_code == 404


class TestDashboardAPI:
    def test_dashboard_includes_favorites_and_subscription(self, app, client, dashboard_data):
        with app.app_context():
            db.session.add(ToolFavorite(
                user_id=dashboard_data["user_id"],
                tool_id=dashboard_data["paid_tool_id"],
            ))
            db.session.add(UserSubscription(
                user_id=dashboard_data["user_id"],
                plan_id=dashboard_data["pro_plan_id"],
                billing_cycle_id=dashboard_data["lifetime_id"],
                status="active",
            ))
            db.session.commit()

        login(client)
        response = client.get("/api/v1/user/dashboard")

        data = response.get_json()["data"]
        assert dashboard_data["paid_tool_id"] in data["favorites"]
        assert data["subscription"]["plan"]["slug"] == "pro"
        assert "user" in data and "tools" in data and "usage" in data
