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
    send_text = MagicMock()
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
        lambda wine: response,
    )
    monkeypatch.setattr(
        recommendation_service.DatastoreRecommendationRepository,
        "update_content_last_sent",
        update_content,
    )
    monkeypatch.setattr(recommendation_service, "send_text", send_text)
    monkeypatch.setattr(
        recommendation_service.DatastoreCustomerRepository,
        "update",
        update_customer,
    )
    return send_text, update_customer, update_content


def test_send_recommendations_skips_inactive_customer(monkeypatch):
    send_text, update_customer, _ = _patch_deps(
        monkeypatch,
        [_customer(status="canceled")],
    )

    result = recommendation_service.send_recommendations()

    assert result is False
    send_text.assert_not_called()
    update_customer.assert_not_called()


def test_send_recommendations_skips_when_sent_within_24h(monkeypatch):
    last = datetime.now(timezone.utc) - timedelta(hours=2)
    send_text, _, _ = _patch_deps(monkeypatch, [_customer(last_recommendation_at=last)])

    assert recommendation_service.send_recommendations() is False
    send_text.assert_not_called()


def test_send_recommendations_normalizes_naive_last_sent(monkeypatch):
    last = datetime.utcnow() - timedelta(hours=1)
    send_text, _, _ = _patch_deps(monkeypatch, [_customer(last_recommendation_at=last)])

    assert recommendation_service.send_recommendations() is False
    send_text.assert_not_called()


def test_send_recommendations_skips_daily_limit(monkeypatch):
    send_text, _, _ = _patch_deps(monkeypatch, [_customer(messages_sent_today=2)])

    assert recommendation_service.send_recommendations() is False
    send_text.assert_not_called()


def test_send_recommendations_sends_when_last_sent_older_than_24h(monkeypatch):
    last = datetime.now(timezone.utc) - timedelta(hours=25)
    customer = _customer(last_recommendation_at=last)
    send_text, update_customer, _ = _patch_deps(monkeypatch, [customer])

    recommendation_service.send_recommendations()

    send_text.assert_called_once()
    update_customer.assert_called_once()
    customer = _customer()
    send_text, update_customer, update_content = _patch_deps(monkeypatch, [customer])

    recommendation_service.send_recommendations()

    send_text.assert_called_once_with("+5511999999999", "msg da semana")
    update_content.assert_called_once_with("wine-key")
    update_customer.assert_called_once()
    assert customer["messages_sent_today"] == 1
    assert customer["last_recommendation_at"] is not None
