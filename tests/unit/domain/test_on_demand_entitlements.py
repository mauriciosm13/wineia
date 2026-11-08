from datetime import datetime, timezone

from domain.models.customer import PlanTier
from domain.on_demand_entitlements import can_send_on_demand, on_demand_daily_limit, reset_daily_counter_if_needed, utc_calendar_day_key


def _customer(plan_tier=PlanTier.entry, messages_sent_today=0, daily_reset=None, status="active"):
    return {
        "phone": "+5511",
        "status": status,
        "plan_tier": plan_tier,
        "messages_sent_today": messages_sent_today,
        "daily_reset": daily_reset,
    }


def test_on_demand_daily_limit_by_tier():
    assert on_demand_daily_limit(PlanTier.entry) == 2
    assert on_demand_daily_limit(PlanTier.superior) == 10
    assert on_demand_daily_limit(None) == 2
    assert on_demand_daily_limit("UNKNOWN") == 2


def test_reset_daily_counter_when_day_changes():
    customer = _customer(messages_sent_today=2, daily_reset="2026-11-07")
    now = datetime(2026, 11, 8, 12, 0, tzinfo=timezone.utc)
    reset_daily_counter_if_needed(customer, now)
    assert customer["messages_sent_today"] == 0
    assert customer["daily_reset"] == "2026-11-08"


def test_reset_daily_counter_skips_when_same_day():
    today = utc_calendar_day_key(datetime(2026, 11, 8, 8, 0, tzinfo=timezone.utc))
    customer = _customer(messages_sent_today=1, daily_reset=today)
    reset_daily_counter_if_needed(customer, datetime(2026, 11, 8, 20, 0, tzinfo=timezone.utc))
    assert customer["messages_sent_today"] == 1


def test_can_send_entry_blocked_at_two():
    today = utc_calendar_day_key()
    customer = _customer(messages_sent_today=2, daily_reset=today)
    assert can_send_on_demand(customer) is False


def test_can_send_superior_allows_two_messages_same_day():
    today = utc_calendar_day_key()
    customer = _customer(plan_tier=PlanTier.superior, messages_sent_today=2, daily_reset=today)
    assert can_send_on_demand(customer) is True


def test_can_send_superior_blocked_at_ten():
    today = utc_calendar_day_key()
    customer = _customer(plan_tier=PlanTier.superior, messages_sent_today=10, daily_reset=today)
    assert can_send_on_demand(customer) is False


def test_reset_accepts_naive_utc_datetime():
    customer = _customer(messages_sent_today=5, daily_reset="2026-11-07")
    reset_daily_counter_if_needed(customer, datetime(2026, 11, 8, 6, 0))
    assert customer["daily_reset"] == "2026-11-08"
    assert customer["messages_sent_today"] == 0


def test_inactive_customer_cannot_send():
    today = utc_calendar_day_key()
    customer = _customer(messages_sent_today=0, daily_reset=today, status="canceled")
    assert can_send_on_demand(customer) is False
