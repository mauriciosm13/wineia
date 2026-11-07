from datetime import datetime, timedelta, timezone

from domain.models.customer import CustomerStatus
from domain.services.education_eligibility import is_eligible_for_weekly_education


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
