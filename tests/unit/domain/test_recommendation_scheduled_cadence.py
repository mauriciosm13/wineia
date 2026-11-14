from datetime import datetime, timedelta, timezone

from domain.recommendation_scheduled_cadence import _as_utc, migrate_recommendation_window_from_legacy, record_scheduled_recommendation_send, roll_recommendation_window_if_expired, should_send_scheduled_recommendation
from domain.recommendation_scheduled_cadence import RECOMMENDATION_RETRY_GUARD, RECOMMENDATION_WINDOW_GRACE


def test_as_utc_naive_gets_utc_tz():
    naive = datetime(2026, 1, 1, 12, 0, 0)
    out = _as_utc(naive)
    assert out.tzinfo == timezone.utc


def test_as_utc_aware_converts_to_utc():
    aware = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone(timedelta(hours=-3)))
    out = _as_utc(aware)
    assert out.tzinfo == timezone.utc


def test_roll_recommendation_window_if_expired_resets_count():
    now_utc = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
    customer = {
        "recommendation_window_started_at": now_utc - timedelta(hours=169),
        "recommendation_send_count_7d": 2,
    }
    roll_recommendation_window_if_expired(customer, now_utc)
    assert customer["recommendation_window_started_at"] == now_utc
    assert customer["recommendation_send_count_7d"] == 0


def test_migrate_skips_when_window_start_already_set():
    now_utc = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
    started = now_utc - timedelta(days=2)
    customer = {
        "recommendation_window_started_at": started,
        "last_recommendation_at": now_utc - timedelta(days=1),
    }
    migrate_recommendation_window_from_legacy(customer, now_utc)
    assert customer["recommendation_window_started_at"] == started


def test_record_scheduled_recommendation_send_naive_now_gets_utc_last_at():
    naive_now = datetime(2026, 6, 15, 12, 0, 0)
    customer = {"recommendation_send_count_7d": 0}
    record_scheduled_recommendation_send(customer, naive_now)
    assert customer["last_recommendation_at"].tzinfo == timezone.utc


def test_grace_and_guard_constants():
    assert RECOMMENDATION_WINDOW_GRACE == timedelta(hours=6)
    assert RECOMMENDATION_RETRY_GUARD == timedelta(hours=24)


def test_window_rolls_when_next_thursday_run_starts_earlier_than_window_start():
    start = datetime(2026, 11, 12, 10, 0, 30, tzinfo=timezone.utc)
    now_utc = datetime(2026, 11, 19, 10, 0, 0, tzinfo=timezone.utc)
    customer = {
        "recommendation_window_started_at": start,
        "recommendation_send_count_7d": 2,
        "last_recommendation_at": start + timedelta(days=2),
    }

    assert should_send_scheduled_recommendation(customer, now_utc) is True
    assert customer["recommendation_window_started_at"] == now_utc
    assert customer["recommendation_send_count_7d"] == 0


def test_window_does_not_roll_just_before_grace_boundary():
    start = datetime(2026, 11, 12, 10, 0, 30, tzinfo=timezone.utc)
    now_utc = start + timedelta(hours=161, minutes=59)
    customer = {
        "recommendation_window_started_at": start,
        "recommendation_send_count_7d": 2,
        "last_recommendation_at": start + timedelta(days=2),
    }

    assert should_send_scheduled_recommendation(customer, now_utc) is False
    assert customer["recommendation_window_started_at"] == start
    assert customer["recommendation_send_count_7d"] == 2


def test_retry_five_minutes_after_send_skips_customer():
    sent_at = datetime(2026, 11, 12, 13, 0, 0, tzinfo=timezone.utc)
    customer = {}
    record_scheduled_recommendation_send(customer, sent_at)

    assert should_send_scheduled_recommendation(customer, sent_at + timedelta(minutes=5)) is False
    assert customer["recommendation_send_count_7d"] == 1


def test_saturday_run_48h_after_send_still_sends():
    sent_at = datetime(2026, 11, 12, 13, 0, 0, tzinfo=timezone.utc)
    customer = {}
    record_scheduled_recommendation_send(customer, sent_at)

    assert should_send_scheduled_recommendation(customer, sent_at + timedelta(hours=48)) is True


def test_retry_guard_handles_naive_last_recommendation_at():
    now_utc = datetime(2026, 11, 12, 13, 5, 0, tzinfo=timezone.utc)
    customer = {
        "recommendation_window_started_at": now_utc - timedelta(minutes=5),
        "recommendation_send_count_7d": 1,
        "last_recommendation_at": datetime(2026, 11, 12, 13, 0, 0),
    }

    assert should_send_scheduled_recommendation(customer, now_utc) is False


def _thursday_saturday_slots(weeks):
    first_thursday = datetime(2026, 11, 12, 13, 0, 0, tzinfo=timezone.utc)
    slots = []
    for week in range(weeks):
        thursday = first_thursday + timedelta(weeks=week)
        slots.append(thursday)
        slots.append(thursday + timedelta(days=2))
    return slots


def test_four_weeks_thursday_saturday_runs_send_once_per_slot():
    slots = _thursday_saturday_slots(weeks=4)
    customer = {}
    sends = []

    for n, nominal in enumerate(slots):
        now_utc = nominal - n * timedelta(seconds=60)
        assert should_send_scheduled_recommendation(customer, now_utc) is True, nominal
        record_scheduled_recommendation_send(customer, now_utc)
        sends.append(nominal)

        if nominal.weekday() == 3:
            retry_at = now_utc + timedelta(minutes=5)
            assert should_send_scheduled_recommendation(customer, retry_at) is False, retry_at

    assert len(slots) == 8
    assert sends == slots
