from datetime import datetime, timezone

from domain.claude_budget import ClaudeBudgetExceededError
from domain.models.customer import PlanTier
from domain.on_demand_entitlements import utc_calendar_day_key
from domain.services.messaging_service import MEDIA_DOWNLOAD_FAILED_MESSAGE, MEDIA_STT_FAILED_MESSAGE, MEDIA_UNAVAILABLE_MESSAGE, MEDIA_UNSUPPORTED_MESSAGE, MEDIA_VISION_FAILED_MESSAGE, SERVICE_UNAVAILABLE_MESSAGE, process_incoming_message
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
    def __init__(self, response="Recomendacao de vinho", raise_budget=False, raise_vision=False):
        self.response = response
        self.calls = 0
        self.vision_calls = []
        self.raise_budget = raise_budget
        self.raise_vision = raise_vision

    def generate_response(self, customer, message):
        self.calls += 1
        if self.raise_budget:
            raise ClaudeBudgetExceededError("claude daily call budget exceeded")
        return self.response

    def generate_vision_response(self, customer, image_bytes, content_type, caption=None):
        self.vision_calls.append(
            {
                "customer": customer,
                "image_bytes": image_bytes,
                "content_type": content_type,
                "caption": caption,
            }
        )
        if self.raise_budget:
            raise ClaudeBudgetExceededError("claude daily call budget exceeded")
        if self.raise_vision:
            raise RuntimeError("vision failed")
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


def test_media_only_without_downloader_sends_unavailable():
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


def test_media_only_unsupported_mime():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer())
    sender = FakeMessageSender()
    ia = FakeIAService()
    calls = []

    def downloader(url):
        calls.append(url)
        return {"content": b"x", "content_type": "application/pdf", "size": 1}

    result = process_incoming_message(
        "+5511999999999",
        "",
        repo,
        sender,
        ia,
        inbound_media={
            "num_media": 1,
            "url": "https://api.twilio.com/media/abc",
            "content_type": "application/pdf",
        },
        media_downloader=downloader,
    )

    assert result == {"status": "media_unsupported"}
    assert sender.sent == [("+5511999999999", MEDIA_UNSUPPORTED_MESSAGE)]
    assert calls == []
    assert ia.calls == 0


def test_media_only_download_failure():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer())
    sender = FakeMessageSender()
    ia = FakeIAService()

    def downloader(url):
        raise RuntimeError("boom")

    result = process_incoming_message(
        "+5511999999999",
        "",
        repo,
        sender,
        ia,
        inbound_media={
            "num_media": 1,
            "url": "https://api.twilio.com/media/abc",
            "content_type": "image/jpeg",
        },
        media_downloader=downloader,
    )

    assert result == {"status": "media_download_failed"}
    assert sender.sent == [("+5511999999999", MEDIA_DOWNLOAD_FAILED_MESSAGE)]
    assert ia.calls == 0
    assert repo._by_phone["+5511999999999"]["messages_sent_today"] == 0


def test_media_only_image_vision_success_processes_ia_turn():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer(messages_sent_today=0))
    sender = FakeMessageSender()
    ia = FakeIAService(response="Sugestao a partir da foto")
    calls = []

    def downloader(url):
        calls.append(url)
        return {"content": b"jpeg-bytes", "content_type": "image/jpeg", "size": 10}

    result = process_incoming_message(
        "+5511999999999",
        "",
        repo,
        sender,
        ia,
        inbound_media={
            "num_media": 1,
            "url": "https://api.twilio.com/media/abc",
            "content_type": "image/jpeg",
        },
        media_downloader=downloader,
    )

    assert result == {"status": "processed", "message": "Sugestao a partir da foto"}
    assert calls == ["https://api.twilio.com/media/abc"]
    assert ia.calls == 0
    assert len(ia.vision_calls) == 1
    assert ia.vision_calls[0]["image_bytes"] == b"jpeg-bytes"
    assert ia.vision_calls[0]["content_type"] == "image/jpeg"
    assert ia.vision_calls[0]["caption"] is None
    assert sender.sent == [("+5511999999999", "Sugestao a partir da foto")]
    assert repo._by_phone["+5511999999999"]["messages_sent_today"] == 1


def test_media_only_audio_stt_success_processes_ia_turn():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer(messages_sent_today=0))
    sender = FakeMessageSender()
    ia = FakeIAService(response="Sugestao a partir do audio")
    stt_calls = []

    def downloader(url):
        return {"content": b"ogg-bytes", "content_type": "audio/ogg", "size": 9}

    def transcriber(content, content_type):
        stt_calls.append((content, content_type))
        return "  quero um malbec  "

    result = process_incoming_message(
        "+5511999999999",
        "",
        repo,
        sender,
        ia,
        inbound_media={
            "num_media": 1,
            "url": "https://api.twilio.com/media/audio",
            "content_type": "audio/ogg",
        },
        media_downloader=downloader,
        audio_transcriber=transcriber,
    )

    assert result == {"status": "processed", "message": "Sugestao a partir do audio"}
    assert stt_calls == [(b"ogg-bytes", "audio/ogg")]
    assert ia.calls == 1
    assert sender.sent == [("+5511999999999", "Sugestao a partir do audio")]
    assert repo._by_phone["+5511999999999"]["messages_sent_today"] == 1
    assert repo._by_phone["+5511999999999"]["last_message_at"] is not None


def test_media_only_audio_stt_failure_fail_closed():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer())
    sender = FakeMessageSender()
    ia = FakeIAService()

    def downloader(url):
        return {"content": b"ogg-bytes", "content_type": "audio/ogg", "size": 9}

    def transcriber(content, content_type):
        raise RuntimeError("stt down")

    result = process_incoming_message(
        "+5511999999999",
        "",
        repo,
        sender,
        ia,
        inbound_media={
            "num_media": 1,
            "url": "https://api.twilio.com/media/audio",
            "content_type": "audio/ogg",
        },
        media_downloader=downloader,
        audio_transcriber=transcriber,
    )

    assert result == {"status": "media_stt_failed"}
    assert sender.sent == [("+5511999999999", MEDIA_STT_FAILED_MESSAGE)]
    assert ia.calls == 0
    assert repo._by_phone["+5511999999999"]["messages_sent_today"] == 0


def test_media_only_audio_empty_transcript_fail_closed():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer())
    sender = FakeMessageSender()
    ia = FakeIAService()

    def downloader(url):
        return {"content": b"ogg-bytes", "content_type": "audio/ogg", "size": 9}

    def transcriber(content, content_type):
        return "   "

    result = process_incoming_message(
        "+5511999999999",
        "",
        repo,
        sender,
        ia,
        inbound_media={
            "num_media": 1,
            "url": "https://api.twilio.com/media/audio",
            "content_type": "audio/ogg",
        },
        media_downloader=downloader,
        audio_transcriber=transcriber,
    )

    assert result == {"status": "media_stt_failed"}
    assert sender.sent == [("+5511999999999", MEDIA_STT_FAILED_MESSAGE)]
    assert ia.calls == 0


def test_media_only_audio_incompatible_mime_fail_closed():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer())
    sender = FakeMessageSender()
    ia = FakeIAService()
    stt_calls = []

    def downloader(url):
        return {"content": b"amr-bytes", "content_type": "audio/amr", "size": 9}

    def transcriber(content, content_type):
        stt_calls.append((content, content_type))
        return "should not run"

    result = process_incoming_message(
        "+5511999999999",
        "",
        repo,
        sender,
        ia,
        inbound_media={
            "num_media": 1,
            "url": "https://api.twilio.com/media/audio",
            "content_type": "audio/amr",
        },
        media_downloader=downloader,
        audio_transcriber=transcriber,
    )

    assert result == {"status": "media_stt_failed"}
    assert stt_calls == []
    assert sender.sent == [("+5511999999999", MEDIA_STT_FAILED_MESSAGE)]
    assert ia.calls == 0


def test_media_only_audio_missing_transcriber_fail_closed():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer())
    sender = FakeMessageSender()
    ia = FakeIAService()

    def downloader(url):
        return {"content": b"ogg-bytes", "content_type": "audio/ogg", "size": 9}

    result = process_incoming_message(
        "+5511999999999",
        "",
        repo,
        sender,
        ia,
        inbound_media={
            "num_media": 1,
            "url": "https://api.twilio.com/media/audio",
            "content_type": "audio/ogg",
        },
        media_downloader=downloader,
    )

    assert result == {"status": "media_stt_failed"}
    assert sender.sent == [("+5511999999999", MEDIA_STT_FAILED_MESSAGE)]
    assert ia.calls == 0


def test_media_only_audio_budget_exceeded_after_stt():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer(messages_sent_today=0))
    sender = FakeMessageSender()
    ia = FakeIAService(raise_budget=True)

    def downloader(url):
        return {"content": b"ogg-bytes", "content_type": "audio/ogg", "size": 9}

    def transcriber(content, content_type):
        return "quero vinho"

    result = process_incoming_message(
        "+5511999999999",
        "",
        repo,
        sender,
        ia,
        inbound_media={
            "num_media": 1,
            "url": "https://api.twilio.com/media/audio",
            "content_type": "audio/ogg",
        },
        media_downloader=downloader,
        audio_transcriber=transcriber,
    )

    assert result == {"status": "budget_exceeded"}
    assert sender.sent == [("+5511999999999", SERVICE_UNAVAILABLE_MESSAGE)]
    assert ia.calls == 1
    assert repo._by_phone["+5511999999999"]["messages_sent_today"] == 0


def test_image_with_caption_uses_vision_path():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer(messages_sent_today=0))
    sender = FakeMessageSender()
    ia = FakeIAService(response="ok com legenda")
    inbound_media = {
        "num_media": 1,
        "url": "https://api.twilio.com/media/abc",
        "content_type": "image/jpeg",
    }

    def downloader(url):
        return {"content": b"jpeg-bytes", "content_type": "image/jpeg", "size": 10}

    result = process_incoming_message(
        "+5511999999999",
        "o que e este vinho?",
        repo,
        sender,
        ia,
        inbound_media=inbound_media,
        media_downloader=downloader,
    )

    assert result["status"] == "processed"
    assert ia.calls == 0
    assert len(ia.vision_calls) == 1
    assert ia.vision_calls[0]["caption"] == "o que e este vinho?"
    assert sender.sent == [("+5511999999999", "ok com legenda")]
    assert repo._by_phone["+5511999999999"]["messages_sent_today"] == 1


def test_media_only_image_vision_failure_fail_closed():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer())
    sender = FakeMessageSender()
    ia = FakeIAService(raise_vision=True)

    def downloader(url):
        return {"content": b"jpeg-bytes", "content_type": "image/jpeg", "size": 10}

    result = process_incoming_message(
        "+5511999999999",
        "",
        repo,
        sender,
        ia,
        inbound_media={
            "num_media": 1,
            "url": "https://api.twilio.com/media/abc",
            "content_type": "image/jpeg",
        },
        media_downloader=downloader,
    )

    assert result == {"status": "media_vision_failed"}
    assert sender.sent == [("+5511999999999", MEDIA_VISION_FAILED_MESSAGE)]
    assert repo._by_phone["+5511999999999"]["messages_sent_today"] == 0


def test_media_only_image_vision_budget_exceeded():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer(messages_sent_today=0))
    sender = FakeMessageSender()
    ia = FakeIAService(raise_budget=True)

    def downloader(url):
        return {"content": b"jpeg-bytes", "content_type": "image/jpeg", "size": 10}

    result = process_incoming_message(
        "+5511999999999",
        "",
        repo,
        sender,
        ia,
        inbound_media={
            "num_media": 1,
            "url": "https://api.twilio.com/media/abc",
            "content_type": "image/jpeg",
        },
        media_downloader=downloader,
    )

    assert result == {"status": "budget_exceeded"}
    assert sender.sent == [("+5511999999999", SERVICE_UNAVAILABLE_MESSAGE)]
    assert repo._by_phone["+5511999999999"]["messages_sent_today"] == 0


def test_media_only_image_empty_bytes_fail_closed():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer())
    sender = FakeMessageSender()
    ia = FakeIAService()

    def downloader(url):
        return {"content": b"", "content_type": "image/jpeg", "size": 0}

    result = process_incoming_message(
        "+5511999999999",
        "",
        repo,
        sender,
        ia,
        inbound_media={
            "num_media": 1,
            "url": "https://api.twilio.com/media/abc",
            "content_type": "image/jpeg",
        },
        media_downloader=downloader,
    )

    assert result == {"status": "media_vision_failed"}
    assert sender.sent == [("+5511999999999", MEDIA_VISION_FAILED_MESSAGE)]
    assert ia.vision_calls == []


def test_media_only_audio_without_downloader_unavailable():
    repo = FakeCustomerRepository()
    repo.seed(_active_customer())
    sender = FakeMessageSender()
    ia = FakeIAService()

    result = process_incoming_message(
        "+5511999999999",
        "",
        repo,
        sender,
        ia,
        inbound_media={
            "num_media": 1,
            "url": "https://api.twilio.com/media/audio",
            "content_type": "audio/ogg",
        },
    )

    assert result == {"status": "media_unprocessable"}
    assert sender.sent == [("+5511999999999", MEDIA_UNAVAILABLE_MESSAGE)]
    assert ia.calls == 0


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
