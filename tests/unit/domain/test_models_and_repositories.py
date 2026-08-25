from domain.models.customer import Customer, CustomerStatus
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
