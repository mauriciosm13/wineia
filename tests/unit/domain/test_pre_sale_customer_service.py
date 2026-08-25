from domain.services.pre_sale_customer_service import PreSaleCustomerService
from tests.fakes.repositories import FakeCustomerRepository, FakePreSaleCustomerRepository


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


def test_activate_creates_customer_with_preferences():
    pre_sale_repo = FakePreSaleCustomerRepository()
    customer_repo = FakeCustomerRepository()
    pre_sale_repo.seed(
        {
            "name": "Carla",
            "email": "carla@example.com",
            "whatsapp": "+5511777777777",
            "preferences": ["tinto", "malbec"],
        }
    )
    service = PreSaleCustomerService(pre_sale_repo)

    result = service.activate("carla@example.com", customer_repo)

    assert result["phone"] == "+5511777777777"
    assert result["name"] == "Carla"
    assert result["status"] == "active"
    assert result["plan"] == "free"
    assert result["preferences"] == ["tinto", "malbec"]
    assert customer_repo.save_calls == 1


def test_activate_missing_email_returns_none():
    pre_sale_repo = FakePreSaleCustomerRepository()
    customer_repo = FakeCustomerRepository()
    service = PreSaleCustomerService(pre_sale_repo)

    result = service.activate("missing@example.com", customer_repo)

    assert result is None
    assert customer_repo.save_calls == 0


def test_activate_existing_phone_merges_preferences_without_duplicate_save():
    pre_sale_repo = FakePreSaleCustomerRepository()
    customer_repo = FakeCustomerRepository()
    customer_repo.seed(
        {
            "phone": "+5511666666666",
            "name": "Diego",
            "status": "active",
            "plan": "free",
            "preferences": ["branco"],
        }
    )
    pre_sale_repo.seed(
        {
            "name": "Diego",
            "email": "diego@example.com",
            "whatsapp": "+5511666666666",
            "preferences": ["tinto", "branco"],
        }
    )
    service = PreSaleCustomerService(pre_sale_repo)

    result = service.activate("diego@example.com", customer_repo)

    assert result["phone"] == "+5511666666666"
    assert result["preferences"] == ["branco", "tinto"]
    assert customer_repo.save_calls == 0
    assert customer_repo.update_calls == 1


def test_activate_existing_phone_skips_update_when_preferences_unchanged():
    pre_sale_repo = FakePreSaleCustomerRepository()
    customer_repo = FakeCustomerRepository()
    customer_repo.seed(
        {
            "phone": "+5511555555555",
            "name": "Eva",
            "status": "active",
            "plan": "free",
            "preferences": ["tinto"],
        }
    )
    pre_sale_repo.seed(
        {
            "name": "Eva",
            "email": "eva@example.com",
            "whatsapp": "+5511555555555",
            "preferences": ["tinto"],
        }
    )
    service = PreSaleCustomerService(pre_sale_repo)

    result = service.activate("eva@example.com", customer_repo)

    assert result["preferences"] == ["tinto"]
    assert customer_repo.update_calls == 0


def test_activate_accepts_pre_sale_model_and_dict_preferences():
    from domain.models.pre_sale_customer import PreSaleCustomer

    pre_sale_repo = FakePreSaleCustomerRepository()
    customer_repo = FakeCustomerRepository()
    lead = PreSaleCustomer("Lia", "lia@example.com", "+5511444444444", {"style": "leve"})
    pre_sale_repo.get_by_email = lambda email: lead if email == lead.email else None
    service = PreSaleCustomerService(pre_sale_repo)

    result = service.activate("lia@example.com", customer_repo)

    assert result["phone"] == "+5511444444444"
    assert "style: leve" in result["preferences"]


def test_activate_ignores_non_list_scalar_preferences():
    pre_sale_repo = FakePreSaleCustomerRepository()
    customer_repo = FakeCustomerRepository()
    pre_sale_repo.seed(
        {
            "name": "Nico",
            "email": "nico@example.com",
            "whatsapp": "+5511333333333",
            "preferences": 3,
        }
    )
    service = PreSaleCustomerService(pre_sale_repo)

    result = service.activate("nico@example.com", customer_repo)

    assert result["preferences"] == []
