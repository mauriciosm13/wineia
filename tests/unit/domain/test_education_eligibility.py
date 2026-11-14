from datetime import datetime, timedelta, timezone

from domain.models.customer import CustomerStatus
from domain.services.education_eligibility import WEEKLY_EDUCATION_GRACE, is_eligible_for_weekly_education


def _customer(**overrides):
    data = {
        "phone": "+5511999999999",
        "status": CustomerStatus.active,
        "weekly_education_opt_in": True,
        "last_weekly_education_at": None,
    }
    data.update(overrides)
    return data


def test_eligible_when_active_opt_in_and_never_sent():
    assert is_eligible_for_weekly_education(_customer()) is True


def test_skips_when_not_opt_in():
    assert is_eligible_for_weekly_education(_customer(weekly_education_opt_in=False)) is False


def test_skips_when_not_active():
    assert is_eligible_for_weekly_education(_customer(status=CustomerStatus.canceled)) is False


def test_skips_when_sent_within_rolling_week():
    now = datetime.now(timezone.utc)
    last = now - timedelta(days=3)
    assert is_eligible_for_weekly_education(_customer(last_weekly_education_at=last), now=now) is False


def test_eligible_when_sent_more_than_seven_days_ago():
    now = datetime.now(timezone.utc)
    last = now - timedelta(days=7, hours=1)
    assert is_eligible_for_weekly_education(_customer(last_weekly_education_at=last), now=now) is True


def test_cadence_normalizes_naive_last_sent():
    now = datetime.now(timezone.utc)
    last = datetime.utcnow() - timedelta(days=2)
    assert is_eligible_for_weekly_education(_customer(last_weekly_education_at=last), now=now) is False


def test_weekly_education_grace_is_six_hours():
    assert WEEKLY_EDUCATION_GRACE == timedelta(hours=6)


def test_eligible_when_next_monday_run_starts_before_last_stamp():
    last = datetime(2026, 11, 9, 15, 0, 20, tzinfo=timezone.utc)
    now = datetime(2026, 11, 16, 15, 0, 5, tzinfo=timezone.utc)
    assert is_eligible_for_weekly_education(_customer(last_weekly_education_at=last), now=now) is True


def test_not_eligible_just_before_grace_boundary():
    last = datetime(2026, 11, 9, 15, 0, 20, tzinfo=timezone.utc)
    now = last + timedelta(days=6, hours=17, minutes=59)
    assert is_eligible_for_weekly_education(_customer(last_weekly_education_at=last), now=now) is False
