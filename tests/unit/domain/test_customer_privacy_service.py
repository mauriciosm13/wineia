from domain.services.customer_privacy_service import REDACTED, CustomerPrivacyService
from tests.fakes.repositories import FakeCustomerRepository, FakePreSaleCustomerRepository


def _privacy_service():
    customer_repo = FakeCustomerRepository()
    pre_sale_repo = FakePreSaleCustomerRepository()
    return CustomerPrivacyService(customer_repo, pre_sale_repo), customer_repo, pre_sale_repo


def test_export_customer_missing_returns_none():
    service, _, _ = _privacy_service()

    assert service.export_customer("+5511999999999") is None


def test_export_customer_without_pre_sale():
    service, customer_repo, _ = _privacy_service()
    customer_repo.seed(
        {
            "phone": "+5511999999999",
            "name": "Ana",
            "status": "active",
            "plan": "free",
            "plan_tier": "ENTRY",
            "weekly_education_opt_in": True,
            "preferences": ["tinto"],
            "privacy_terms_version": "2026-11-18",
            "privacy_terms_accepted_at": "2026-11-18T12:00:00Z",
            "messages_sent_today": 1,
            "recommendation_send_count_7d": 2,
        }
    )

    payload = service.export_customer("+5511999999999")

    assert payload["phone"] == "+5511999999999"
    assert payload["name"] == "Ana"
    assert payload["preferences"] == ["tinto"]
    assert payload["plan_tier"] == "ENTRY"
    assert payload["privacy_terms_version"] == "2026-11-18"
    assert payload["messages_sent_today"] == 1
    assert payload["recommendation_send_count_7d"] == 2
    assert payload["pre_sale"] is None
    assert "api_key" not in payload
    assert "secret" not in payload


def test_export_customer_includes_pre_sale_by_whatsapp():
    service, customer_repo, pre_sale_repo = _privacy_service()
    customer_repo.seed(
        {
            "phone": "+5511888777666",
            "name": "Bruno",
            "status": "active",
            "plan": "free",
            "preferences": [],
        }
    )
    pre_sale_repo.seed(
        {
            "name": "Bruno Lead",
            "email": "bruno@example.com",
            "whatsapp": "+5511888777666",
            "preferences": ["branco"],
            "privacy_terms_version": "2026-11-18",
            "privacy_terms_accepted_at": "2026-11-18T10:00:00Z",
            "created_at": "2026-11-01T00:00:00Z",
        }
    )

    payload = service.export_customer("+5511888777666")

    assert payload["pre_sale"]["email"] == "bruno@example.com"
    assert payload["pre_sale"]["whatsapp"] == "+5511888777666"
    assert payload["pre_sale"]["name"] == "Bruno Lead"
    assert payload["pre_sale"]["preferences"] == ["branco"]


def test_erase_customer_missing_returns_none():
    service, _, _ = _privacy_service()

    assert service.erase_customer("+5511000000000") is None


def test_erase_customer_anonymizes_without_pre_sale():
    service, customer_repo, pre_sale_repo = _privacy_service()
    customer_repo.seed(
        {
            "phone": "+5511555555555",
            "name": "Carla",
            "status": "active",
            "plan": "free",
            "plan_tier": "SUPERIOR",
            "weekly_education_opt_in": True,
            "preferences": ["rosé"],
            "privacy_terms_version": "2026-11-18",
            "privacy_terms_accepted_at": "2026-11-18T12:00:00Z",
            "messages_sent_today": 3,
        }
    )

    result = service.erase_customer("+5511555555555")

    assert result["erased"] is True
    assert result["pre_sale_deleted"] is False
    assert result["name"] == REDACTED
    assert result["preferences"] == []
    assert result["status"] == "canceled"
    assert result["weekly_education_opt_in"] is False
    assert result["privacy_terms_version"] is None
    assert result["privacy_terms_accepted_at"] is None
    assert result["phone"] == "+5511555555555"
    assert result["plan_tier"] == "SUPERIOR"
    assert result["messages_sent_today"] == 3
    assert customer_repo.update_calls == 1
    assert pre_sale_repo.delete_calls == 0

    stored = customer_repo.get_by_phone("+5511555555555")
    assert stored["name"] == REDACTED
    assert stored["status"] == "canceled"


def test_erase_customer_deletes_linked_pre_sale():
    service, customer_repo, pre_sale_repo = _privacy_service()
    customer_repo.seed(
        {
            "phone": "+5511444333222",
            "name": "Diego",
            "status": "active",
            "plan": "free",
            "preferences": ["tinto"],
        }
    )
    pre_sale_repo.seed(
        {
            "name": "Diego Lead",
            "email": "diego@example.com",
            "whatsapp": "+5511444333222",
            "preferences": ["tinto"],
        }
    )

    result = service.erase_customer("+5511444333222")

    assert result["erased"] is True
    assert result["pre_sale_deleted"] is True
    assert pre_sale_repo.delete_calls == 1
    assert pre_sale_repo.get_by_whatsapp("+5511444333222") is None
    assert pre_sale_repo.get_by_email("diego@example.com") is None


def test_fake_pre_sale_get_by_whatsapp_and_delete():
    repo = FakePreSaleCustomerRepository()
    repo.seed(
        {
            "name": "Eva",
            "email": "eva@example.com",
            "whatsapp": "+5511222333444",
            "preferences": [],
        }
    )

    assert repo.get_by_whatsapp("+5511222333444")["email"] == "eva@example.com"
    assert repo.get_by_whatsapp("+5511000000000") is None

    repo.delete("eva@example.com")
    assert repo.delete_calls == 1
    assert repo.get_by_whatsapp("+5511222333444") is None

def test_export_accepts_customer_and_pre_sale_models():
    from domain.models.customer import Customer
    from domain.models.pre_sale_customer import PreSaleCustomer

    service, customer_repo, pre_sale_repo = _privacy_service()
    customer_repo.save(Customer("+5511666777888", "Fernanda", "active", "free"))
    pre_sale_repo.save(
        PreSaleCustomer(
            "Fernanda Lead",
            "fernanda@example.com",
            "+5511666777888",
            ["branco"],
            privacy_terms_version="2026-11-18",
            privacy_terms_accepted_at="2026-11-18T09:00:00Z",
        )
    )
    # Store model object (not dict) so export exercises to_dict branches
    pre_sale_repo._by_email["fernanda@example.com"] = PreSaleCustomer(
        "Fernanda Lead",
        "fernanda@example.com",
        "+5511666777888",
        ["branco"],
        privacy_terms_version="2026-11-18",
        privacy_terms_accepted_at="2026-11-18T09:00:00Z",
    )

    payload = service.export_customer("+5511666777888")

    assert payload["name"] == "Fernanda"
    assert payload["pre_sale"]["email"] == "fernanda@example.com"
    assert payload["pre_sale"]["name"] == "Fernanda Lead"
