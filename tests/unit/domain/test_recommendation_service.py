from collections import UserDict
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import domain.services.recommendation_service as recommendation_service
from domain.models.customer import CustomerStatus, PlanTier

DEFAULT_NOW = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)


def _customer(**overrides):
    data = {
        "phone": "+5511999999999",
        "status": CustomerStatus.active,
        "plan_tier": PlanTier.entry,
        "last_recommendation_at": None,
        "recommendation_window_started_at": None,
        "recommendation_send_count_7d": 0,
        "messages_sent_today": 0,
    }
    data.update(overrides)
    return data


def _patch_deps(monkeypatch, customers, wine=None, response="msg da semana"):
    wine = wine or SimpleNamespace(key="wine-key")
    enqueue_send_message = MagicMock()
    update_customer = MagicMock()
    update_content = MagicMock()

    monkeypatch.setattr(
        recommendation_service.DatastoreCustomerRepository,
        "list_active",
        staticmethod(lambda: customers),
    )
    monkeypatch.setattr(recommendation_service, "select_wine", lambda: wine)
    monkeypatch.setattr(
        recommendation_service.ia_service,
        "generate_recommendation",
        lambda wine, preferences=None: response,
    )
    monkeypatch.setattr(
        recommendation_service.DatastoreRecommendationRepository,
        "update_content_last_sent",
        update_content,
    )
    monkeypatch.setattr(recommendation_service, "enqueue_send_message", enqueue_send_message)
    monkeypatch.setattr(
        recommendation_service.DatastoreCustomerRepository,
        "update",
        update_customer,
    )
    return enqueue_send_message, update_customer, update_content


def test_sdd_entry_no_prior_sends_enqueues(monkeypatch):
    """SDD #1: ENTRY, no prior sends — Send."""
    c = _customer()
    enqueue, update_customer, update_content = _patch_deps(monkeypatch, [c])

    recommendation_service.send_recommendations(now_utc=DEFAULT_NOW)

    enqueue.assert_called_once_with("+5511999999999", "msg da semana")
    update_customer.assert_called_once()
    update_content.assert_called_once_with("wine-key")
    assert c["recommendation_send_count_7d"] == 1
    assert c["last_recommendation_at"] is not None


def test_sdd_entry_one_send_three_days_ago_enqueues(monkeypatch):
    """SDD #2: ENTRY, one send 3d ago — Send (second in week)."""
    now_utc = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
    last = now_utc - timedelta(days=3)
    c = _customer(last_recommendation_at=last)
    enqueue, update_customer, _ = _patch_deps(monkeypatch, [c])

    recommendation_service.send_recommendations(now_utc=now_utc)

    enqueue.assert_called_once()
    update_customer.assert_called_once()
    assert c["recommendation_send_count_7d"] == 2


def test_sdd_entry_two_sends_in_168h_skips(monkeypatch):
    """SDD #3: ENTRY, two sends in last 168h — Skip."""
    now_utc = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
    window_start = now_utc - timedelta(hours=1)
    c = _customer(
        recommendation_window_started_at=window_start,
        recommendation_send_count_7d=2,
        last_recommendation_at=now_utc - timedelta(hours=2),
    )
    enqueue, update_customer, update_content = _patch_deps(monkeypatch, [c])

    recommendation_service.send_recommendations(now_utc=now_utc)

    enqueue.assert_not_called()
    update_customer.assert_not_called()
    update_content.assert_called_once_with("wine-key")


def test_sdd_entry_one_send_eight_days_ago_enqueues_after_roll(monkeypatch):
    """SDD #4: ENTRY, one send 8d ago (window rolled) — Send."""
    now_utc = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
    last = now_utc - timedelta(days=8)
    c = _customer(last_recommendation_at=last)
    enqueue, update_customer, _ = _patch_deps(monkeypatch, [c])

    recommendation_service.send_recommendations(now_utc=now_utc)

    enqueue.assert_called_once()
    update_customer.assert_called_once()
    assert c["recommendation_send_count_7d"] == 1


def test_sdd_superior_same_cadence_as_entry(monkeypatch):
    """SDD #5: SUPERIOR — same scheduled cadence as ENTRY."""
    c = _customer(plan_tier=PlanTier.superior)
    enqueue, update_customer, _ = _patch_deps(monkeypatch, [c])

    recommendation_service.send_recommendations(now_utc=DEFAULT_NOW)

    enqueue.assert_called_once_with("+5511999999999", "msg da semana")
    update_customer.assert_called_once()


def test_sdd_inactive_skips(monkeypatch):
    """SDD #6: Inactive / canceled — Skip."""
    c = _customer(status=CustomerStatus.canceled)
    enqueue, update_customer, update_content = _patch_deps(monkeypatch, [c])

    recommendation_service.send_recommendations(now_utc=DEFAULT_NOW)

    enqueue.assert_not_called()
    update_customer.assert_not_called()
    update_content.assert_called_once_with("wine-key")


def test_sdd_messages_sent_today_two_still_sends_when_cadence_allows(monkeypatch):
    """SDD #7: messages_sent_today == 2 but cadence allows — Still send."""
    c = _customer(messages_sent_today=2)
    enqueue, update_customer, _ = _patch_deps(monkeypatch, [c])

    recommendation_service.send_recommendations(now_utc=DEFAULT_NOW)

    enqueue.assert_called_once()
    update_customer.assert_called_once()
    assert c["messages_sent_today"] == 2


def test_sdd_unknown_tier_skips(monkeypatch):
    """SDD #8: Unknown tier — Skip."""
    c = _customer(plan_tier="PREMIUM")
    enqueue, update_customer, update_content = _patch_deps(monkeypatch, [c])

    recommendation_service.send_recommendations(now_utc=DEFAULT_NOW)

    enqueue.assert_not_called()
    update_customer.assert_not_called()
    update_content.assert_called_once_with("wine-key")


def test_send_recommendations_one_claude_call_and_same_body_per_eligible(monkeypatch):
    """T023: one generate_recommendation per job; same body enqueued for each eligible customer."""
    c1 = _customer(phone="+5511111111111")
    c2 = _customer(phone="+5511222222222")
    c3 = _customer(
        phone="+5511333333333",
        recommendation_send_count_7d=2,
        recommendation_window_started_at=DEFAULT_NOW,
        last_recommendation_at=DEFAULT_NOW,
    )
    enqueue, update_customer, _ = _patch_deps(monkeypatch, [c1, c2, c3])
    gen = MagicMock(return_value="shared broadcast body")
    monkeypatch.setattr(recommendation_service.ia_service, "generate_recommendation", gen)

    recommendation_service.send_recommendations(now_utc=DEFAULT_NOW)

    gen.assert_called_once()
    assert enqueue.call_count == 2
    enqueue.assert_any_call("+5511111111111", "shared broadcast body")
    enqueue.assert_any_call("+5511222222222", "shared broadcast body")
    assert update_customer.call_count == 2


def test_send_recommendations_skips_inactive_and_enqueues_for_eligible(monkeypatch):
    canceled = _customer(status=CustomerStatus.canceled, phone="+5511888888888")
    active = _customer(phone="+5511999999999")
    enqueue, update_customer, update_content = _patch_deps(
        monkeypatch,
        [canceled, active],
    )

    recommendation_service.send_recommendations(now_utc=DEFAULT_NOW)

    enqueue.assert_called_once_with("+5511999999999", "msg da semana")
    update_customer.assert_called_once()
    update_content.assert_called_once_with("wine-key")


def test_send_recommendations_does_not_use_send_text(monkeypatch):
    customer = _customer()
    _patch_deps(monkeypatch, [customer])
    send_text = MagicMock()
    monkeypatch.setattr(recommendation_service, "send_text", send_text, raising=False)

    recommendation_service.send_recommendations(now_utc=DEFAULT_NOW)

    send_text.assert_not_called()


def test_send_recommendations_normalizes_userdict_customer_row(monkeypatch):
    row = UserDict(_customer())
    enqueue, update_customer, _ = _patch_deps(monkeypatch, [row])

    recommendation_service.send_recommendations(now_utc=DEFAULT_NOW)

    enqueue.assert_called_once()
    update_customer.assert_called_once()


def test_enqueue_send_message_uses_cloud_tasks_client(monkeypatch):
    mock_client = MagicMock()
    monkeypatch.setattr(
        "infrastructure.queue.cloud_tasks_client.CloudTasksClient",
        lambda: mock_client,
    )

    recommendation_service.enqueue_send_message("+5511", "ola")

    mock_client.enqueue.assert_called_once_with(
        "send_message",
        {"phone": "+5511", "message": "ola"},
    )
