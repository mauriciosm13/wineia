"""On-demand WhatsApp IA entitlements (T024) — webhook path via messaging_service.

Distinct from scheduled recommendation cadence (T021) and webhook abuse limits (T012).
Tier caps default to ENTRY=2 / SUPERIOR=10; T060 reads ops overrides from core.config.
"""
from datetime import datetime, timezone

import core.config as config
from domain.models.customer import DEFAULT_PLAN_TIER, PlanTier


def on_demand_daily_limit(plan_tier):
    tier = plan_tier if plan_tier in PlanTier.all else DEFAULT_PLAN_TIER
    if tier == PlanTier.superior:
        return config.ON_DEMAND_DAILY_LIMIT_SUPERIOR
    return config.ON_DEMAND_DAILY_LIMIT_ENTRY


def _utc_now(now):
    if now is None:
        return datetime.now(timezone.utc)
    if now.tzinfo is None:
        return now.replace(tzinfo=timezone.utc)
    return now.astimezone(timezone.utc)


def utc_calendar_day_key(now=None):
    return _utc_now(now).date().isoformat()


def reset_daily_counter_if_needed(customer, now=None):
    """Reset `messages_sent_today` when the UTC calendar day changes (read-path reset)."""
    today = utc_calendar_day_key(now)
    if customer.get("daily_reset") != today:
        customer["messages_sent_today"] = 0
        customer["daily_reset"] = today


def can_send_on_demand(customer, now=None):
    reset_daily_counter_if_needed(customer, now)
    if customer.get("status") != "active":
        return False
    sent = int(customer.get("messages_sent_today") or 0)
    return sent < on_demand_daily_limit(customer.get("plan_tier"))
