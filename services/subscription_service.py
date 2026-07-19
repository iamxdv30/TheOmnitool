"""
Subscription Service Module

Handles subscription-related business logic:
- Reading a user's current subscription (plan, billing cycle, status)
- Listing available subscription plans
- Resolving the active subscription tier for access control

Payment provider integration (create/upgrade/cancel, webhooks) is deferred
until a provider is integrated — see docs/dashboard-redesign-679c76.md §2F.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from model import SubscriptionPlan, UserSubscription
from .base import BaseService, ServiceResult, ErrorCode

logger = logging.getLogger(__name__)


def _is_expired(expires_at: Optional[datetime]) -> bool:
    """Check whether an expiry datetime has passed (null = never expires)."""
    if expires_at is None:
        return False
    now = datetime.now(timezone.utc)
    # SQLite returns naive datetimes; compare in the same "flavor"
    if expires_at.tzinfo is None:
        now = now.replace(tzinfo=None)
    return expires_at <= now


class SubscriptionService(BaseService):
    """Service for subscription read operations."""

    def get_user_subscription(self, user_id: int) -> ServiceResult[Optional[Dict[str, Any]]]:
        """
        Get the user's current active subscription with plan and billing cycle.

        Returns:
            ServiceResult with subscription dict, or None if the user has no
            active subscription.
        """
        try:
            subscription = self._get_active_subscription(user_id)
            if subscription is None:
                return ServiceResult.success(None)

            plan = subscription.plan
            cycle = subscription.billing_cycle_ref

            return ServiceResult.success({
                "plan": {
                    "id": plan.id,
                    "name": plan.name,
                    "slug": plan.slug,
                    "tier_level": plan.tier_level,
                } if plan else None,
                "status": subscription.status,
                "billing_cycle": cycle.code if cycle else None,
                "started_at": subscription.started_at.isoformat() if subscription.started_at else None,
                "expires_at": subscription.expires_at.isoformat() if subscription.expires_at else None,
            })

        except Exception as e:
            self._log_error("get_user_subscription", e, user_id=user_id)
            return ServiceResult.failure(
                ErrorCode.DATABASE_ERROR,
                "Failed to retrieve subscription."
            )

    def get_plans(self) -> ServiceResult[List[Dict[str, Any]]]:
        """
        List all active subscription plans ordered by tier level.

        Returns:
            ServiceResult with list of plan dicts
        """
        try:
            plans = (
                SubscriptionPlan.query
                .filter_by(is_active=True)
                .order_by(SubscriptionPlan.tier_level.asc())
                .all()
            )
            plan_list = [{
                "id": p.id,
                "name": p.name,
                "slug": p.slug,
                "tier_level": p.tier_level,
                "price_monthly": float(p.price_monthly) if p.price_monthly is not None else None,
                "price_yearly": float(p.price_yearly) if p.price_yearly is not None else None,
                "features": p.features,
            } for p in plans]

            return ServiceResult.success(plan_list)

        except Exception as e:
            self._log_error("get_plans", e)
            return ServiceResult.failure(
                ErrorCode.DATABASE_ERROR,
                "Failed to retrieve subscription plans."
            )

    def get_active_tier(self, user_id: int) -> Optional[int]:
        """
        Get the tier level of the user's active subscription.

        Returns:
            The plan's tier_level, or None if no active subscription.
            Never raises — access-control callers treat failures as "no tier".
        """
        try:
            subscription = self._get_active_subscription(user_id)
            if subscription and subscription.plan:
                return subscription.plan.tier_level
            return None
        except Exception as e:
            self._log_error("get_active_tier", e, user_id=user_id)
            return None

    def _get_active_subscription(self, user_id: int) -> Optional[UserSubscription]:
        """Get the highest-tier active, non-expired subscription for a user."""
        subscriptions = (
            UserSubscription.query
            .filter_by(user_id=user_id, status="active")
            .join(SubscriptionPlan, UserSubscription.plan_id == SubscriptionPlan.id)
            .order_by(SubscriptionPlan.tier_level.desc())
            .all()
        )
        for subscription in subscriptions:
            if not _is_expired(subscription.expires_at):
                return subscription
        return None


# Singleton instance
_subscription_service: Optional[SubscriptionService] = None


def get_subscription_service() -> SubscriptionService:
    """Get the singleton SubscriptionService instance."""
    global _subscription_service
    if _subscription_service is None:
        _subscription_service = SubscriptionService()
    return _subscription_service
