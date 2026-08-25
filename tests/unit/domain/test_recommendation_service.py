from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import domain.services.recommendation_service as recommendation_service
from domain.models.customer import CustomerStatus


def _customer(**overrides):
    data = {
        "phone": "+5511999999999",
        "status": CustomerStatus.active,
        "last_recommendation_at": None,
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


def test_send_recommendations_skips_inactive_customer(monkeypatch):
    enqueue, update_customer, update_content = _patch_deps(
        monkeypatch,
        [_customer(status=CustomerStatus.canceled)],
    )

    recommendation_service.send_recommendations()

    enqueue.assert_not_called()
    update_customer.assert_not_called()
    update_content.assert_called_once_with("wine-key")


def test_send_recommendations_skips_inactive_and_enqueues_for_eligible(monkeypatch):
    canceled = _customer(status=CustomerStatus.canceled, phone="+5511888888888")
    active = _customer(phone="+5511999999999")
    enqueue, update_customer, update_content = _patch_deps(
        monkeypatch,
        [canceled, active],
    )

    recommendation_service.send_recommendations()

    enqueue.assert_called_once_with("+5511999999999", "msg da semana")
    update_customer.assert_called_once()
    update_content.assert_called_once_with("wine-key")


def test_send_recommendations_skips_when_sent_within_24h(monkeypatch):
    last = datetime.now(timezone.utc) - timedelta(hours=2)
    enqueue, _, update_content = _patch_deps(
        monkeypatch,
        [_customer(last_recommendation_at=last)],
    )

    recommendation_service.send_recommendations()

    enqueue.assert_not_called()
    update_content.assert_called_once_with("wine-key")


def test_send_recommendations_normalizes_naive_last_sent(monkeypatch):
    last = datetime.utcnow() - timedelta(hours=1)
    enqueue, _, _ = _patch_deps(monkeypatch, [_customer(last_recommendation_at=last)])

    recommendation_service.send_recommendations()

    enqueue.assert_not_called()


def test_send_recommendations_skips_daily_limit(monkeypatch):
    enqueue, _, _ = _patch_deps(monkeypatch, [_customer(messages_sent_today=2)])

    recommendation_service.send_recommendations()

    enqueue.assert_not_called()


def test_send_recommendations_enqueues_for_eligible_customer(monkeypatch):
    last = datetime.now(timezone.utc) - timedelta(hours=25)
    customer = _customer(last_recommendation_at=last)
    enqueue, update_customer, update_content = _patch_deps(monkeypatch, [customer])

    recommendation_service.send_recommendations()

    enqueue.assert_called_once_with("+5511999999999", "msg da semana")
    update_content.assert_called_once_with("wine-key")
    update_customer.assert_called_once()
    assert customer["messages_sent_today"] == 1
    assert customer["last_recommendation_at"] is not None


def test_send_recommendations_does_not_use_send_text(monkeypatch):
    customer = _customer()
    _patch_deps(monkeypatch, [customer])
    send_text = MagicMock()
    monkeypatch.setattr(recommendation_service, "send_text", send_text, raising=False)

    recommendation_service.send_recommendations()

    send_text.assert_not_called()


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
