"""T079 — inbound media ops: routing, failure copy, text-only entitlements."""

from domain.on_demand_entitlements import utc_calendar_day_key
from domain.services.messaging_service import MEDIA_DOWNLOAD_FAILED_MESSAGE, MEDIA_UNSUPPORTED_MESSAGE, process_incoming_message
from tests.fakes.repositories import FakeCustomerRepository
from tests.unit.domain.test_messaging_service import FakeIAService, FakeMessageSender, _active_customer


def _customer_keys(repo, phone):
    return set(repo._by_phone[phone].keys())


def test_media_only_unsupported_mime_portuguese_copy_no_blob_no_ia():
    """Unsupported MIME → Portuguese copy; no download, IA, counter, or blob fields."""
    phone = "+5511999999999"
    today = utc_calendar_day_key()
    repo = FakeCustomerRepository()
    repo.seed(_active_customer(messages_sent_today=0, daily_reset=today))
    sender = FakeMessageSender()
    ia = FakeIAService()
    download_calls = []

    def downloader(url):
        download_calls.append(url)
        return {"content": b"pdf", "content_type": "application/pdf", "size": 3}

    before_keys = _customer_keys(repo, phone)

    result = process_incoming_message(
        phone,
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
    assert sender.sent == [(phone, MEDIA_UNSUPPORTED_MESSAGE)]
    assert "nao suportamos" in MEDIA_UNSUPPORTED_MESSAGE
    assert "JPEG/PNG" in MEDIA_UNSUPPORTED_MESSAGE
    assert download_calls == []
    assert ia.calls == 0
    assert ia.vision_calls == []
    assert repo._by_phone[phone]["messages_sent_today"] == 0
    assert _customer_keys(repo, phone) == before_keys
    assert "media_blob" not in repo._by_phone[phone]
    assert "media_url" not in repo._by_phone[phone]
    assert "media_bytes" not in repo._by_phone[phone]


def test_media_only_download_failure_portuguese_copy_no_counter():
    """Download failure → Portuguese copy; no IA and no entitlement increment."""
    phone = "+5511999999999"
    today = utc_calendar_day_key()
    repo = FakeCustomerRepository()
    repo.seed(_active_customer(messages_sent_today=1, daily_reset=today))
    sender = FakeMessageSender()
    ia = FakeIAService()

    def downloader(url):
        raise RuntimeError("twilio cdn unavailable")

    before_keys = _customer_keys(repo, phone)

    result = process_incoming_message(
        phone,
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
    assert sender.sent == [(phone, MEDIA_DOWNLOAD_FAILED_MESSAGE)]
    assert "baixar sua midia" in MEDIA_DOWNLOAD_FAILED_MESSAGE
    assert ia.calls == 0
    assert ia.vision_calls == []
    assert repo._by_phone[phone]["messages_sent_today"] == 1
    assert _customer_keys(repo, phone) == before_keys
    assert "media_blob" not in repo._by_phone[phone]


def test_text_only_entitlements_unchanged_after_media_failure_paths():
    """Text-only path still increments on success; media fail-closed does not affect quotas."""
    phone = "+5511999999999"
    today = utc_calendar_day_key()
    repo = FakeCustomerRepository()
    repo.seed(_active_customer(messages_sent_today=0, daily_reset=today))
    sender = FakeMessageSender()
    ia = FakeIAService(response="Malbec")

    fail = process_incoming_message(
        phone,
        "",
        repo,
        sender,
        ia,
        inbound_media={
            "num_media": 1,
            "url": "https://api.twilio.com/media/abc",
            "content_type": "application/pdf",
        },
        media_downloader=lambda url: {"content": b"x", "content_type": "application/pdf", "size": 1},
    )
    assert fail == {"status": "media_unsupported"}
    assert repo._by_phone[phone]["messages_sent_today"] == 0

    ok = process_incoming_message(phone, "me indica um vinho", repo, sender, ia)
    assert ok == {"status": "processed", "message": "Malbec"}
    assert ia.calls == 1
    assert repo._by_phone[phone]["messages_sent_today"] == 1
    assert sender.sent[-1] == (phone, "Malbec")
