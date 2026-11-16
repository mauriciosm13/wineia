from datetime import datetime, timezone

import pytest

from domain.claude_budget import ClaudeBudgetExceededError, ensure_within_budget, record_successful_call, utc_day_key


class FakeClaudeBudgetRepository:
    def __init__(self, counts=None):
        self.counts = dict(counts or {})
        self.get_calls = []
        self.increment_calls = []

    def get_call_count(self, day_key):
        self.get_calls.append(day_key)
        return self.counts.get(day_key, 0)

    def increment_call_count(self, day_key):
        self.increment_calls.append(day_key)
        self.counts[day_key] = self.counts.get(day_key, 0) + 1
        return self.counts[day_key]


def test_utc_day_key_formats_utc_calendar_day():
    now = datetime(2026, 11, 16, 23, 30, tzinfo=timezone.utc)
    assert utc_day_key(now) == "2026-11-16"


def test_utc_day_key_normalizes_naive_as_utc():
    now = datetime(2026, 11, 16, 1, 0, 0)
    assert utc_day_key(now) == "2026-11-16"


def test_ensure_within_budget_unlimited_skips_repository():
    repo = FakeClaudeBudgetRepository(counts={"2026-11-16": 999})
    ensure_within_budget(repo, 0, now=datetime(2026, 11, 16, tzinfo=timezone.utc))
    ensure_within_budget(repo, None, now=datetime(2026, 11, 16, tzinfo=timezone.utc))
    assert repo.get_calls == []


def test_ensure_within_budget_allows_when_under_cap():
    repo = FakeClaudeBudgetRepository(counts={"2026-11-16": 2})
    ensure_within_budget(repo, 5, now=datetime(2026, 11, 16, 12, tzinfo=timezone.utc))
    assert repo.get_calls == ["2026-11-16"]


def test_ensure_within_budget_raises_when_at_or_over_cap():
    repo = FakeClaudeBudgetRepository(counts={"2026-11-16": 5})
    with pytest.raises(ClaudeBudgetExceededError, match="claude daily call budget exceeded"):
        ensure_within_budget(repo, 5, now=datetime(2026, 11, 16, 12, tzinfo=timezone.utc))


def test_record_successful_call_increments_for_utc_day():
    repo = FakeClaudeBudgetRepository()
    new_count = record_successful_call(repo, now=datetime(2026, 11, 16, 8, tzinfo=timezone.utc))
    assert new_count == 1
    assert repo.counts["2026-11-16"] == 1
    assert repo.increment_calls == ["2026-11-16"]
