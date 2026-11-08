"""On-demand WhatsApp IA entitlements (T024) — webhook path via messaging_service.

Distinct from scheduled recommendation cadence (T021) and webhook abuse limits (T012).
Tier defaults here are the baseline for T060 (finer caps / ops tuning may follow).
"""
from datetime import datetime, timezone

from domain.models.customer import DEFAULT_PLAN_TIER, PlanTier

# MVP tier caps (per UTC calendar day). SUPERIOR: on-demand Gastón per commercial.md.
ON_DEMAND_DAILY_LIMIT_BY_TIER = {
    PlanTier.entry: 2,
    PlanTier.superior: 10,
}


def on_demand_daily_limit(plan_tier):
    tier = plan_tier if plan_tier in PlanTier.all else DEFAULT_PLAN_TIER
    return ON_DEMAND_DAILY_LIMIT_BY_TIER[tier]


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
