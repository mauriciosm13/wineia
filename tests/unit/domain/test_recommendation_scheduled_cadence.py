from datetime import datetime, timedelta, timezone

from domain.recommendation_scheduled_cadence import _as_utc, migrate_recommendation_window_from_legacy, record_scheduled_recommendation_send, roll_recommendation_window_if_expired


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
