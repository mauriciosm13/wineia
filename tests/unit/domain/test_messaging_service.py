from datetime import datetime, timezone

from domain.claude_budget import ClaudeBudgetExceededError
from domain.models.customer import PlanTier
from domain.on_demand_entitlements import utc_calendar_day_key
from domain.services.messaging_service import MEDIA_UNAVAILABLE_MESSAGE, SERVICE_UNAVAILABLE_MESSAGE, process_incoming_message
from tests.fakes.repositories import FakeCustomerRepository



class FakeMessageSender:
    def __init__(self, raise_on_send=False):
        self.sent = []
        self.raise_on_send = raise_on_send

    def __call__(self, phone, message):
        if self.raise_on_send:
            raise RuntimeError("enqueue failed")
        self.sent.append((phone, message))


class FakeIAService:
    def __init__(self, response="Recomendacao de vinho", raise_budget=False):
        self.response = response
        self.calls = 0
        self.raise_budget = raise_budget

    def generate_response(self, customer, message):
        self.calls += 1
        if self.raise_budget:
            raise ClaudeBudgetExceededError("claude daily call budget exceeded")
        return self.response


def _active_customer(messages_sent_today=0, plan_tier=PlanTier.entry, daily_reset=None):
    return {
        "phone": "+5511999999999",
        "name": "Ana",
        "status": "active",
        "plan": "free",
        "plan_tier": plan_tier,
        "messages_sent_today": messages_sent_today,
        "daily_reset": daily_reset,
    }


def test_cancelar_sets_canceled_status():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer())
    sender = FakeMessageSender()
    ia = FakeIAService()

    result = process_incoming_message("+5511999999999", "cancelar", repo, sender, ia)

    assert result == {"status": "canceled"}
    assert repo._by_phone["+5511999999999"]["status"] == "canceled"
    assert sender.sent == []
    assert ia.calls == 0


def test_limit_reached_at_two_messages():
    repo = FakeCustomerRepository()
    today = utc_calendar_day_key()
    repo.seed(_active_customer(messages_sent_today=2, daily_reset=today))
    sender = FakeMessageSender()
    ia = FakeIAService()

    result = process_incoming_message("+5511999999999", "oi", repo, sender, ia)

    assert result == {"status": "limit_reached"}
    assert len(sender.sent) == 1
    assert "limite diario" in sender.sent[0][1]
    assert ia.calls == 0
    assert repo._by_phone["+5511999999999"]["messages_sent_today"] == 2


def test_processed_increments_counter():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer(messages_sent_today=0))
    sender = FakeMessageSender()
    ia = FakeIAService(response="Malbec argentino")

    result = process_incoming_message("+5511999999999", "quero vinho", repo, sender, ia)

    assert result == {"status": "processed", "message": "Malbec argentino"}
    assert repo._by_phone["+5511999999999"]["messages_sent_today"] == 1
    assert repo._by_phone["+5511999999999"]["last_message_at"] is not None
    assert sender.sent == [("+5511999999999", "Malbec argentino")]
    assert ia.calls == 1


def test_processed_sender_failure_does_not_increment():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer(messages_sent_today=0))
    sender = FakeMessageSender(raise_on_send=True)
    ia = FakeIAService(response="Malbec argentino")

    try:
        process_incoming_message("+5511999999999", "quero vinho", repo, sender, ia)
        assert False, "expected enqueue failure"
    except RuntimeError:
        pass

    customer = repo._by_phone["+5511999999999"]
    assert customer["messages_sent_today"] == 0
    assert customer.get("last_message_at") is None
    assert ia.calls == 1


def test_unknown_phone_returns_none():
    repo = FakeCustomerRepository()
    sender = FakeMessageSender()
    ia = FakeIAService()

    result = process_incoming_message("+5511000000000", "oi", repo, sender, ia)

    assert result is None
    assert sender.sent == []
    assert ia.calls == 0


def test_normalize_customer_list_uses_first_entry():
    repo = FakeCustomerRepository()
    repo._by_phone["+5511999999999"] = [_active_customer()]
    sender = FakeMessageSender()
    ia = FakeIAService(response="ok")

    result = process_incoming_message("+5511999999999", "oi", repo, sender, ia)

    assert result["status"] == "processed"
    assert ia.calls == 1


def test_normalize_customer_empty_list_returns_none():
    repo = FakeCustomerRepository()
    repo._by_phone["+5511999999999"] = []
    sender = FakeMessageSender()
    ia = FakeIAService()

    result = process_incoming_message("+5511999999999", "oi", repo, sender, ia)

    assert result is None
    assert ia.calls == 0


def test_cancel_treats_none_message_as_not_cancel():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer())
    sender = FakeMessageSender()
    ia = FakeIAService(response="ok")

    result = process_incoming_message("+5511999999999", None, repo, sender, ia)

    assert result["status"] == "processed"


def test_superior_continues_past_entry_cap_of_two():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer(messages_sent_today=2, plan_tier=PlanTier.superior, daily_reset="2026-11-08"))
    sender = FakeMessageSender()
    ia = FakeIAService(response="Resposta superior")
    now = datetime(2026, 11, 8, 15, 0, tzinfo=timezone.utc)

    result = process_incoming_message("+5511999999999", "oi", repo, sender, ia, now=now)

    assert result["status"] == "processed"
    assert repo._by_phone["+5511999999999"]["messages_sent_today"] == 3


def test_daily_reset_on_inbound_clears_stale_counter():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer(messages_sent_today=2, daily_reset="2026-11-07"))
    sender = FakeMessageSender()
    ia = FakeIAService()
    now = datetime(2026, 11, 8, 9, 0, tzinfo=timezone.utc)

    result = process_incoming_message("+5511999999999", "oi", repo, sender, ia, now=now)

    assert result["status"] == "processed"
    assert repo._by_phone["+5511999999999"]["messages_sent_today"] == 1
    assert repo._by_phone["+5511999999999"]["daily_reset"] == "2026-11-08"


def test_inactive_customer_cannot_send():
    repo = FakeCustomerRepository()
    customer = _active_customer()
    customer["status"] = "canceled"
    repo.seed(customer)
    sender = FakeMessageSender()
    ia = FakeIAService()

    result = process_incoming_message("+5511999999999", "oi", repo, sender, ia)

    assert result == {"status": "limit_reached"}
    assert len(sender.sent) == 1
    assert ia.calls == 0


def test_budget_exceeded_sends_unavailable_without_incrementing():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer(messages_sent_today=0))
    sender = FakeMessageSender()
    ia = FakeIAService(raise_budget=True)

    result = process_incoming_message("+5511999999999", "oi", repo, sender, ia)

    assert result == {"status": "budget_exceeded"}
    assert sender.sent == [("+5511999999999", SERVICE_UNAVAILABLE_MESSAGE)]
    assert ia.calls == 1
    assert repo._by_phone["+5511999999999"]["messages_sent_today"] == 0
    assert repo._by_phone["+5511999999999"].get("last_message_at") is None


def test_media_only_sends_unavailable_without_ia_or_increment():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer(messages_sent_today=0))
    sender = FakeMessageSender()
    ia = FakeIAService()
    inbound_media = {
        "num_media": 1,
        "url": "https://api.twilio.com/media/abc",
        "content_type": "image/jpeg",
    }

    result = process_incoming_message(
        "+5511999999999",
        "",
        repo,
        sender,
        ia,
        inbound_media=inbound_media,
    )

    assert result == {"status": "media_unprocessable"}
    assert sender.sent == [("+5511999999999", MEDIA_UNAVAILABLE_MESSAGE)]
    assert ia.calls == 0
    assert repo._by_phone["+5511999999999"]["messages_sent_today"] == 0


def test_text_with_media_still_uses_ia_path():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer(messages_sent_today=0))
    sender = FakeMessageSender()
    ia = FakeIAService(response="ok com midia")
    inbound_media = {
        "num_media": 1,
        "url": "https://api.twilio.com/media/abc",
        "content_type": "image/jpeg",
    }

    result = process_incoming_message(
        "+5511999999999",
        "o que e este vinho?",
        repo,
        sender,
        ia,
        inbound_media=inbound_media,
    )

    assert result["status"] == "processed"
    assert ia.calls == 1
    assert sender.sent == [("+5511999999999", "ok com midia")]
    assert repo._by_phone["+5511999999999"]["messages_sent_today"] == 1


def test_cancelar_with_media_still_cancels():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer())
    sender = FakeMessageSender()
    ia = FakeIAService()
    inbound_media = {"num_media": 1, "url": "https://x", "content_type": "audio/ogg"}

    result = process_incoming_message(
        "+5511999999999",
        "cancelar",
        repo,
        sender,
        ia,
        inbound_media=inbound_media,
    )

    assert result == {"status": "canceled"}
    assert repo._by_phone["+5511999999999"]["status"] == "canceled"
    assert sender.sent == []
    assert ia.calls == 0
