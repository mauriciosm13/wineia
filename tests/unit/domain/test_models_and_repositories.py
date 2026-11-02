from domain.models.customer import Customer, CustomerStatus, DEFAULT_PLAN_TIER, PlanTier, normalize_customer_fields
from domain.models.recommendation_history import RecommendationHistory
from domain.repositories.customer_repository import CustomerRepository
from domain.repositories.pre_sale_customer_repository import PreSaleCustomerRepository
from domain.repositories.recommendation_repository import RecommendationRepository


def test_customer_status_constants():
    assert CustomerStatus.active == "active"
    assert CustomerStatus.canceled == "canceled"


def test_customer_to_dict_includes_counters():
    customer = Customer("+5511", "Ana", CustomerStatus.active, "free")
    payload = customer.to_dict()
    assert payload["messages_sent_today"] == 0
    assert payload["last_message_at"] is None
    assert payload["preferences"] == []


def test_customer_to_dict_includes_preferences():
    customer = Customer("+5511", "Ana", CustomerStatus.active, "free", ["tinto", "malbec"])
    payload = customer.to_dict()
    assert payload["preferences"] == ["tinto", "malbec"]


def test_customer_defaults_plan_tier_and_education_opt_in():
    customer = Customer("+5511", "Ana", CustomerStatus.active, "free")
    payload = customer.to_dict()
    assert payload["plan_tier"] == DEFAULT_PLAN_TIER
    assert payload["plan_tier"] == PlanTier.entry
    assert payload["weekly_education_opt_in"] is False


def test_customer_accepts_superior_tier_and_opt_in():
    customer = Customer(
        "+5511",
        "Ana",
        CustomerStatus.active,
        "premium",
        plan_tier=PlanTier.superior,
        weekly_education_opt_in=True,
    )
    payload = customer.to_dict()
    assert payload["plan_tier"] == PlanTier.superior
    assert payload["weekly_education_opt_in"] is True


def test_normalize_customer_fields_applies_defaults():
    legacy = {"phone": "+5511", "plan": "free", "status": "active"}
    normalize_customer_fields(legacy)
    assert legacy["plan_tier"] == PlanTier.entry
    assert legacy["weekly_education_opt_in"] is False


def test_recommendation_history_to_dict():
    history = RecommendationHistory("+5511", "Malbec Reserva")
    payload = history.to_dict()
    assert payload["phone"] == "+5511"
    assert payload["wine_name"] == "Malbec Reserva"
    assert payload["sent_at"] is not None


def test_repository_interfaces_are_abstract():
    assert CustomerRepository.__abstractmethods__
    assert PreSaleCustomerRepository.__abstractmethods__
    assert RecommendationRepository.__abstractmethods__
