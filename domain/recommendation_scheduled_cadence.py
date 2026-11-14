"""Scheduled recommendation cadence for ENTRY/SUPERIOR (T021, SDD Option B).

Uses a tumbling 168h window: `recommendation_window_started_at` plus
`recommendation_send_count_7d`, with `last_recommendation_at` for ops/debug.

Legacy Datastore rows may only have `last_recommendation_at`. On first evaluation
after deploy we seed window fields from it when that timestamp falls inside the
last 168h (count 1, window_start = last send) to avoid an extra send; otherwise
we start a fresh window with count 0.

The window rolls 6h early (`RECOMMENDATION_WINDOW_GRACE`) so a weekly run that
starts slightly earlier than last week still opens a new window. A customer whose
`last_recommendation_at` is within `RECOMMENDATION_RETRY_GUARD` is skipped so a
retried scheduler run never sends twice in the same slot.

Scheduled sends do not increment `messages_sent_today` (on-demand / webhook cap).
"""
from datetime import timedelta, timezone

from domain.models.customer import PlanTier

ROLLING_RECOMMENDATION_WINDOW = timedelta(hours=168)
RECOMMENDATION_WINDOW_GRACE = timedelta(hours=6)
RECOMMENDATION_RETRY_GUARD = timedelta(hours=24)


def _as_utc(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def migrate_recommendation_window_from_legacy(customer, now_utc):
    """Seed `recommendation_*` fields when missing, using `last_recommendation_at` if present."""
    if customer.get("recommendation_window_started_at") is not None:
        return
    last = _as_utc(customer.get("last_recommendation_at"))
    if last is None:
        return
    if now_utc - last < ROLLING_RECOMMENDATION_WINDOW:
        customer["recommendation_window_started_at"] = last
        customer["recommendation_send_count_7d"] = 1
    else:
        customer["recommendation_window_started_at"] = now_utc
        customer["recommendation_send_count_7d"] = 0


def roll_recommendation_window_if_expired(customer, now_utc):
    """Reset tumbling window when the current period is older than 168h minus the grace."""
    start = _as_utc(customer.get("recommendation_window_started_at"))
    if start is None:
        return
    if now_utc - start >= ROLLING_RECOMMENDATION_WINDOW - RECOMMENDATION_WINDOW_GRACE:
        customer["recommendation_window_started_at"] = now_utc
        customer["recommendation_send_count_7d"] = 0


def tier_gets_scheduled_recommendations(plan_tier):
    return plan_tier in (PlanTier.entry, PlanTier.superior)


def should_send_scheduled_recommendation(customer, now_utc):
    """Return True if ENTRY/SUPERIOR cadence allows another scheduled send."""
    migrate_recommendation_window_from_legacy(customer, now_utc)
    roll_recommendation_window_if_expired(customer, now_utc)
    last = _as_utc(customer.get("last_recommendation_at"))
    if last is not None and now_utc - last < RECOMMENDATION_RETRY_GUARD:
        return False
    count = int(customer.get("recommendation_send_count_7d") or 0)
    return count < 2


def record_scheduled_recommendation_send(customer, now_utc):
    """Persist state after a scheduled recommendation is enqueued."""
    start = customer.get("recommendation_window_started_at")
    count = int(customer.get("recommendation_send_count_7d") or 0)
    if start is None:
        customer["recommendation_window_started_at"] = now_utc
        customer["recommendation_send_count_7d"] = 1
    else:
        customer["recommendation_send_count_7d"] = count + 1
    if now_utc.tzinfo is None:
        customer["last_recommendation_at"] = now_utc.replace(tzinfo=timezone.utc)
    else:
        customer["last_recommendation_at"] = now_utc.astimezone(timezone.utc)
