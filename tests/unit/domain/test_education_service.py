from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import domain.services.education_service as education_service
from domain.models.customer import CustomerStatus


def _customer(**overrides):
    data = {
        "phone": "+5511999999999",
        "status": CustomerStatus.active,
        "weekly_education_opt_in": True,
        "last_weekly_education_at": None,
    }
    data.update(overrides)
    return data


def _patch_deps(monkeypatch, customers, message="dica da semana"):
    enqueue = MagicMock()
    update_customer = MagicMock()

    monkeypatch.setattr(
        education_service.DatastoreCustomerRepository,
        "list_active",
        staticmethod(lambda: customers),
    )
    monkeypatch.setattr(
        education_service.ia_service,
        "generate_weekly_education",
        lambda: message,
    )
    monkeypatch.setattr(education_service, "enqueue_send_message", enqueue)
    monkeypatch.setattr(
        education_service.DatastoreCustomerRepository,
        "update",
        update_customer,
    )
    return enqueue, update_customer


def test_send_weekly_education_skips_without_opt_in(monkeypatch):
    enqueue, update_customer = _patch_deps(
        monkeypatch,
        [_customer(weekly_education_opt_in=False)],
    )

    education_service.send_weekly_education()

    enqueue.assert_not_called()
    update_customer.assert_not_called()


def test_send_weekly_education_skips_inactive(monkeypatch):
    enqueue, update_customer = _patch_deps(
        monkeypatch,
        [_customer(status=CustomerStatus.canceled)],
    )

    education_service.send_weekly_education()

    enqueue.assert_not_called()
    update_customer.assert_not_called()


def test_send_weekly_education_skips_when_sent_within_week(monkeypatch):
    last = datetime.now(timezone.utc) - timedelta(days=2)
    enqueue, update_customer = _patch_deps(
        monkeypatch,
        [_customer(last_weekly_education_at=last)],
    )

    education_service.send_weekly_education()

    enqueue.assert_not_called()
    update_customer.assert_not_called()


def test_send_weekly_education_one_claude_call_fan_out(monkeypatch):
    customers = [
        _customer(phone="+5511111111111"),
        _customer(phone="+5511222222222", weekly_education_opt_in=False),
        _customer(phone="+5511333333333"),
    ]
    enqueue, update_customer = _patch_deps(monkeypatch, customers, message="texto compartilhado")
    generate = MagicMock(return_value="texto compartilhado")
    monkeypatch.setattr(education_service.ia_service, "generate_weekly_education", generate)

    education_service.send_weekly_education()

    generate.assert_called_once()
    assert enqueue.call_count == 2
    enqueue.assert_any_call("+5511111111111", "texto compartilhado")
    enqueue.assert_any_call("+5511333333333", "texto compartilhado")
    assert update_customer.call_count == 2


def test_send_weekly_education_sets_last_sent(monkeypatch):
    customer = _customer()
    last = datetime.now(timezone.utc) - timedelta(days=8)
    customer["last_weekly_education_at"] = last
    enqueue, update_customer = _patch_deps(monkeypatch, [customer])

    education_service.send_weekly_education()

    enqueue.assert_called_once()
    update_customer.assert_called_once()
    assert customer["last_weekly_education_at"] is not None
