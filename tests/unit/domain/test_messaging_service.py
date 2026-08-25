from domain.services.messaging_service import process_incoming_message
from tests.fakes.repositories import FakeCustomerRepository


class FakeMessagingGateway:
    def __init__(self):
        self.sent = []

    def send_text(self, phone, message):
        self.sent.append((phone, message))


class FakeIAService:
    def __init__(self, response="Recomendacao de vinho"):
        self.response = response
        self.calls = 0

    def generate_response(self, customer, message):
        self.calls += 1
        return self.response


def _active_customer(messages_sent_today=0):
    return {
        "phone": "+5511999999999",
        "name": "Ana",
        "status": "active",
        "plan": "free",
        "messages_sent_today": messages_sent_today,
    }


def test_cancelar_sets_canceled_status():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer())
    gateway = FakeMessagingGateway()
    ia = FakeIAService()

    result = process_incoming_message("+5511999999999", "cancelar", repo, gateway, ia)

    assert result == {"status": "canceled"}
    assert repo._by_phone["+5511999999999"]["status"] == "canceled"
    assert gateway.sent == []
    assert ia.calls == 0


def test_limit_reached_at_two_messages():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer(messages_sent_today=2))
    gateway = FakeMessagingGateway()
    ia = FakeIAService()

    result = process_incoming_message("+5511999999999", "oi", repo, gateway, ia)

    assert result == {"status": "limit_reached"}
    assert len(gateway.sent) == 1
    assert ia.calls == 0


def test_processed_increments_counter():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer(messages_sent_today=0))
    gateway = FakeMessagingGateway()
    ia = FakeIAService(response="Malbec argentino")

    result = process_incoming_message("+5511999999999", "quero vinho", repo, gateway, ia)

    assert result == {"status": "processed", "message": "Malbec argentino"}
    assert repo._by_phone["+5511999999999"]["messages_sent_today"] == 1
    assert repo._by_phone["+5511999999999"]["last_message_at"] is not None
    assert gateway.sent == [("+5511999999999", "Malbec argentino")]
    assert ia.calls == 1


def test_unknown_phone_returns_none():
    repo = FakeCustomerRepository()
    gateway = FakeMessagingGateway()
    ia = FakeIAService()

    result = process_incoming_message("+5511000000000", "oi", repo, gateway, ia)

    assert result is None
    assert gateway.sent == []
    assert ia.calls == 0


def test_normalize_customer_list_uses_first_entry():
    repo = FakeCustomerRepository()
    repo._by_phone["+5511999999999"] = [_active_customer()]
    gateway = FakeMessagingGateway()
    ia = FakeIAService(response="ok")

    result = process_incoming_message("+5511999999999", "oi", repo, gateway, ia)

    assert result["status"] == "processed"
    assert ia.calls == 1


def test_normalize_customer_empty_list_returns_none():
    repo = FakeCustomerRepository()
    repo._by_phone["+5511999999999"] = []
    gateway = FakeMessagingGateway()
    ia = FakeIAService()

    result = process_incoming_message("+5511999999999", "oi", repo, gateway, ia)

    assert result is None
    assert ia.calls == 0


def test_cancel_treats_none_message_as_not_cancel():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer())
    gateway = FakeMessagingGateway()
    ia = FakeIAService(response="ok")

    result = process_incoming_message("+5511999999999", None, repo, gateway, ia)

    assert result["status"] == "processed"


def test_inactive_customer_cannot_send():
    repo = FakeCustomerRepository()
    customer = _active_customer()
    customer["status"] = "canceled"
    repo.seed(customer)
    gateway = FakeMessagingGateway()
    ia = FakeIAService()

    result = process_incoming_message("+5511999999999", "oi", repo, gateway, ia)

    assert result == {"status": "limit_reached"}
    assert len(gateway.sent) == 1
    assert ia.calls == 0
