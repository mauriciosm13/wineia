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

    assert result is existing
    assert repo.save_calls == 0
