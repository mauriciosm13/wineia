from domain.services.pre_sale_customer_service import PreSaleCustomerService
from tests.fakes.repositories import FakePreSaleCustomerRepository


def test_create_pre_sale_customer_new():
    repo = FakePreSaleCustomerRepository()
    service = PreSaleCustomerService(repo)

    result = service.create_customer(
        "Carla",
        "carla@example.com",
        "+5511777777777",
        {"grape": "malbec"},
    )

    assert result["name"] == "Carla"
    assert result["email"] == "carla@example.com"
    assert result["whatsapp"] == "+5511777777777"
    assert result["preferences"] == {"grape": "malbec"}
    assert repo.save_calls == 1


def test_create_pre_sale_customer_existing_email_returns_copy():
    repo = FakePreSaleCustomerRepository()
    existing = {
        "name": "Diego",
        "email": "diego@example.com",
        "whatsapp": "+5511666666666",
        "preferences": {"style": "tinto"},
    }
    repo.seed(existing)
    service = PreSaleCustomerService(repo)

    result = service.create_customer(
        "Other",
        "diego@example.com",
        "+5511000000000",
        {"grape": "syrah"},
    )

    assert result == existing
    assert result is not existing
    assert repo.save_calls == 0
