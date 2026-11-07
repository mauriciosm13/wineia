from datetime import datetime, timedelta, timezone

from domain.models.customer import CustomerStatus

WEEKLY_EDUCATION_COOLDOWN = timedelta(days=7)


def normalize_utc(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def is_eligible_for_weekly_education(customer, now=None):
    if customer.get("status") != CustomerStatus.active:
        return False
    if not customer.get("weekly_education_opt_in"):
        return False
    last = normalize_utc(customer.get("last_weekly_education_at"))
    if last is None:
        return True
    now = normalize_utc(now) if now is not None else datetime.now(timezone.utc)
    return now - last >= WEEKLY_EDUCATION_COOLDOWN
