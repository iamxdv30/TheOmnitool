"""
Seed script for Dashboard Redesign Phase 1 data.

This script is intentionally separate from schema migrations.
Run this after migrations are applied.

Usage:
    python scripts/seed_phase1_dashboard_data.py
"""

import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import create_app
from model import (
    db,
    User,
    PaymentProvider,
    SubscriptionPlan,
    BillingCycle,
    UserSubscription,
    ToolCategory,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("seed_phase1_dashboard_data")


PROVIDERS = [
    {
        "code": "stripe",
        "name": "Stripe",
        "supported_currencies": ["USD", "EUR", "GBP", "CAD", "AUD", "JPY"],
    },
    {
        "code": "paypal",
        "name": "PayPal",
        "supported_currencies": ["USD", "EUR", "GBP", "CAD", "AUD"],
    },
    {
        "code": "paddle",
        "name": "Paddle",
        "supported_currencies": ["USD", "EUR", "GBP"],
    },
    {"code": "razorpay", "name": "Razorpay", "supported_currencies": ["INR", "USD"]},
    {"code": "mollie", "name": "Mollie", "supported_currencies": ["EUR"]},
    {
        "code": "manual",
        "name": "Manual / Bank Transfer",
        "supported_currencies": ["USD", "EUR", "GBP"],
    },
    {"code": "paymongo", "name": "PayMongo", "supported_currencies": ["PHP"]},
    {"code": "omise", "name": "Omise", "supported_currencies": ["THB", "JPY", "SGD"]},
    {"code": "xendit", "name": "Xendit", "supported_currencies": ["IDR", "PHP", "MYR"]},
    {"code": "mercadopago", "name": "Mercado Pago", "supported_currencies": ["BRL"]},
    {
        "code": "flutterwave",
        "name": "Flutterwave",
        "supported_currencies": ["NGN", "GHS", "ZAR"],
    },
]

BILLING_CYCLES = [
    {"code": "monthly", "name": "Monthly", "display_order": 1},
    {"code": "yearly", "name": "Yearly", "display_order": 2},
    {"code": "lifetime", "name": "Lifetime", "display_order": 3},
]

PLANS = [
    {
        "name": "Free",
        "slug": "free",
        "tier_level": 0,
        "price_monthly": None,
        "price_yearly": None,
        "features": {"max_tools": None, "priority_support": False},
    },
    {
        "name": "Basic",
        "slug": "basic",
        "tier_level": 1,
        "price_monthly": 9.99,
        "price_yearly": 99.99,
        "features": {"max_tools": 25, "priority_support": False},
    },
    {
        "name": "Pro",
        "slug": "pro",
        "tier_level": 2,
        "price_monthly": 29.99,
        "price_yearly": 299.99,
        "features": {"max_tools": None, "priority_support": True},
    },
]

CATEGORIES = [
    {
        "name": "Finance",
        "slug": "finance",
        "color": "text-success",
        "icon": "coins",
        "display_order": 1,
    },
    {
        "name": "Development",
        "slug": "dev",
        "color": "text-warning",
        "icon": "code",
        "display_order": 2,
    },
    {
        "name": "Writing",
        "slug": "writing",
        "color": "text-info",
        "icon": "pen-line",
        "display_order": 3,
    },
    {
        "name": "Marketing",
        "slug": "marketing",
        "color": "text-accent",
        "icon": "megaphone",
        "display_order": 4,
    },
]


def seed_payment_providers() -> None:
    logger.info("[STEP 3] Seeding payment providers...")
    for provider_data in PROVIDERS:
        existing = PaymentProvider.query.filter_by(code=provider_data["code"]).first()
        if existing:
            logger.info("  Provider exists: %s", provider_data["name"])
            continue

        db.session.add(PaymentProvider(**provider_data))
        logger.info("  Added provider: %s", provider_data["name"])


def seed_plans_and_categories() -> None:
    logger.info("[STEP 4] Seeding subscription plans and tool categories...")

    for plan_data in PLANS:
        existing = SubscriptionPlan.query.filter_by(slug=plan_data["slug"]).first()
        if existing:
            logger.info("  Plan exists: %s", plan_data["name"])
            continue

        db.session.add(SubscriptionPlan(**plan_data))
        logger.info("  Added plan: %s", plan_data["name"])

    for category_data in CATEGORIES:
        existing = ToolCategory.query.filter_by(slug=category_data["slug"]).first()
        if existing:
            logger.info("  Category exists: %s", category_data["name"])
            continue

        db.session.add(ToolCategory(**category_data))
        logger.info("  Added category: %s", category_data["name"])


def seed_billing_cycles() -> None:
    logger.info("[STEP 4] Seeding billing cycles...")

    for billing_cycle_data in BILLING_CYCLES:
        existing = BillingCycle.query.filter_by(code=billing_cycle_data["code"]).first()
        if existing:
            logger.info("  Billing cycle exists: %s", billing_cycle_data["name"])
            continue

        db.session.add(BillingCycle(**billing_cycle_data))
        logger.info("  Added billing cycle: %s", billing_cycle_data["name"])


def assign_all_existing_users_to_pro_plan() -> None:
    logger.info("[STEP 4] Assigning waived-forever Pro access to all existing users...")

    pro_plan = SubscriptionPlan.query.filter_by(slug="pro").first()
    if not pro_plan:
        raise RuntimeError("Pro plan not found. Seed plans before user assignment.")

    lifetime_cycle = BillingCycle.query.filter_by(code="lifetime").first()
    if not lifetime_cycle:
        raise RuntimeError("Lifetime billing cycle not found. Seed billing cycles first.")

    users = User.query.all()
    created_count = 0
    updated_count = 0

    for user in users:
        existing_subscription = UserSubscription.query.filter_by(user_id=user.id).first()

        if existing_subscription:
            if existing_subscription.plan_id != pro_plan.id:
                existing_subscription.plan_id = pro_plan.id
                updated_count += 1
            existing_subscription.status = "active"
            existing_subscription.billing_cycle_id = lifetime_cycle.id
            existing_subscription.expires_at = None
            existing_subscription.cancelled_at = None
            existing_subscription.payment_provider_id = None
            if not existing_subscription.currency:
                existing_subscription.currency = "USD"
            continue

        db.session.add(
            UserSubscription(
                user_id=user.id,
                plan_id=pro_plan.id,
                status="active",
                billing_cycle_id=lifetime_cycle.id,
                currency="USD",
                expires_at=None,
                cancelled_at=None,
                payment_provider_id=None,
            )
        )
        created_count += 1

    logger.info("  Created waived Pro subscriptions for %s user(s)", created_count)
    logger.info("  Updated existing subscriptions to waived Pro for %s user(s)", updated_count)


def run_seed() -> None:
    app = create_app()

    with app.app_context():
        logger.info("Starting Phase 1 seed script...")

        try:
            seed_payment_providers()
            seed_plans_and_categories()
            seed_billing_cycles()
            assign_all_existing_users_to_pro_plan()

            db.session.commit()
            logger.info("✓ Phase 1 seed completed successfully")

        except Exception as exc:
            db.session.rollback()
            logger.error("✗ Phase 1 seed failed: %s", exc)
            raise


if __name__ == "__main__":
    run_seed()
