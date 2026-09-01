import json
from unittest.mock import MagicMock

import pytest

from domain.models.customer import Customer
from domain.services.customer_service import CustomerService
from tests.fakes.repositories import FakeCustomerRepository


def test_create_customer_new():
    repo = FakeCustomerRepository()
    service = CustomerService(repo)

    result = service.create_customer("+5511999999999", "Ana", "active", "free")

    assert result["phone"] == "+5511999999999"
    assert result["name"] == "Ana"
    assert result["status"] == "active"
    assert result["plan"] == "free"
    assert repo.save_calls == 1


def test_create_customer_existing_phone_skips_save():
    repo = FakeCustomerRepository()
    existing = Customer("+5511888888888", "Bob", "active", "free")
    repo._by_phone[existing.phone] = existing
    service = CustomerService(repo)

    result = service.create_customer("+5511888888888", "Other", "canceled", "premium")

    assert result["phone"] == "+5511888888888"
    assert result["name"] == "Bob"
    assert repo.save_calls == 0


def test_list_customers_returns_all():
    repo = FakeCustomerRepository()
    repo.seed({"phone": "+5511", "name": "Ana", "status": "active", "plan": "free"})
    repo.seed({"phone": "+5522", "name": "Bob", "status": "canceled", "plan": "free"})
    service = CustomerService(repo)

    result = service.list_customers()

    assert len(result) == 2
    phones = {customer["phone"] for customer in result}
    assert phones == {"+5511", "+5522"}


def test_get_customer_found():
    repo = FakeCustomerRepository()
    repo.seed({"phone": "+5511", "name": "Ana", "status": "active", "plan": "free"})
    service = CustomerService(repo)

    result = service.get_customer("+5511")

    assert result["name"] == "Ana"


def test_get_customer_not_found():
    repo = FakeCustomerRepository()
    service = CustomerService(repo)

    assert service.get_customer("+5599") is None


def test_update_customer_changes_fields():
    repo = FakeCustomerRepository()
    repo.seed({"phone": "+5511", "name": "Ana", "status": "active", "plan": "free", "preferences": []})
    service = CustomerService(repo)

    result = service.update_customer("+5511", {"name": "Ana Silva", "plan": "premium"})

    assert result["name"] == "Ana Silva"
    assert result["plan"] == "premium"
    assert repo.update_calls == 1


def test_update_customer_not_found():
    repo = FakeCustomerRepository()
    service = CustomerService(repo)

    assert service.update_customer("+5599", {"name": "Ghost"}) is None


def test_update_customer_rejects_invalid_status():
    repo = FakeCustomerRepository()
    repo.seed({"phone": "+5511", "name": "Ana", "status": "active", "plan": "free"})
    service = CustomerService(repo)

    with pytest.raises(ValueError, match="status must be active or canceled"):
        service.update_customer("+5511", {"status": "paused"})


def test_update_customer_requires_field():
    repo = FakeCustomerRepository()
    repo.seed({"phone": "+5511", "name": "Ana", "status": "active", "plan": "free"})
    service = CustomerService(repo)

    with pytest.raises(ValueError, match="at least one updatable field is required"):
        service.update_customer("+5511", {})


def test_update_customer_validates_preferences():
    repo = FakeCustomerRepository()
    repo.seed({"phone": "+5511", "name": "Ana", "status": "active", "plan": "free", "preferences": []})
    service = CustomerService(repo)

    result = service.update_customer("+5511", {"preferences": ["tinto", "malbec"]})

    assert result["preferences"] == ["tinto", "malbec"]


def test_list_customers_handler():
    from api.handlers import customer_handler

    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    fake_service = MagicMock()
    fake_service.list_customers.return_value = [{"phone": "+5511", "name": "Ana"}]
    customer_handler.service = fake_service

    body = customer_handler.handle_list_customers({"REQUEST_METHOD": "GET"}, start_response)

    assert captured["status"] == "200 OK"
    assert json.loads(body[0]) == [{"phone": "+5511", "name": "Ana"}]


def test_get_customer_handler_not_found():
    from api.handlers import customer_handler

    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    fake_service = MagicMock()
    fake_service.get_customer.return_value = None
    customer_handler.service = fake_service

    customer_handler.handle_get_customer({"REQUEST_METHOD": "GET"}, start_response, "+5599")

    assert captured["status"] == "404 Not Found"
