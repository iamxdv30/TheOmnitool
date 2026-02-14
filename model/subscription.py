from datetime import datetime, timezone
from .base import db


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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class BillingCycle(db.Model):
    __tablename__ = "billing_cycles"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)  # monthly, yearly, lifetime
    name = db.Column(db.String(50), nullable=False)
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    subscriptions = db.relationship("UserSubscription", back_populates="billing_cycle_ref")


class UserSubscription(db.Model):
    __tablename__ = "user_subscriptions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("subscription_plans.id"), nullable=False)
    status = db.Column(db.String(20), default="active")  # active, cancelled, expired, trial, pending
    billing_cycle_id = db.Column(db.Integer, db.ForeignKey("billing_cycles.id"), nullable=False)
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=True)  # null = lifetime/free
    cancelled_at = db.Column(db.DateTime, nullable=True)

    # Provider-agnostic payment fields
    payment_provider_id = db.Column(db.Integer, db.ForeignKey("payment_providers.id"), nullable=True)
    external_subscription_id = db.Column(db.String(255), nullable=True)  # Provider's subscription ID
    external_customer_id = db.Column(db.String(255), nullable=True)  # Provider's customer ID
    external_transaction_id = db.Column(db.String(255), nullable=True)  # Provider's transaction ID
    currency = db.Column(db.String(3), nullable=True)  # "USD", "EUR", "GBP", etc.

    user = db.relationship("User", back_populates="subscriptions")
    plan = db.relationship("SubscriptionPlan")
    billing_cycle_ref = db.relationship("BillingCycle", back_populates="subscriptions")
    payment_provider_ref = db.relationship("PaymentProvider", back_populates="subscriptions")


class PaymentProvider(db.Model):
    __tablename__ = "payment_providers"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)  # "stripe", "paypal", "manual"
    name = db.Column(db.String(50), unique=True, nullable=False)  # "Stripe", "PayPal", "Manual"
    is_active = db.Column(db.Boolean, default=True)
    supported_currencies = db.Column(db.JSON, nullable=True)  # {"USD", "EUR", "GBP"}
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    subscriptions = db.relationship("UserSubscription", back_populates="payment_provider_ref")