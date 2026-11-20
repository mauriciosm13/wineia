import json
from io import BytesIO
from unittest.mock import patch

from api.handlers import waitlist_handler
from domain.services.waitlist_service import WaitlistValidationError
from tests.fakes.repositories import FakeWaitlistRepository
from domain.services.waitlist_service import WaitlistService


def _environ(method, payload=None):
    raw = b"" if payload is None else json.dumps(payload).encode()
    return {
        "REQUEST_METHOD": method,
        "CONTENT_LENGTH": str(len(raw)),
        "wsgi.input": BytesIO(raw),
        "PATH_INFO": "/waitlist",
    }


def test_handler_create_returns_201(monkeypatch):
    repo = FakeWaitlistRepository()
    service = WaitlistService(repo)
    monkeypatch.setattr(waitlist_handler, "service", service)
    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    body = waitlist_handler.handle_waitlist_request(
        _environ(
            "POST",
            {
                "phone": "+5511987654321",
                "name": "Carla",
                "email": "Carla@Example.com",
                "birth_date": "1992-03-04",
            },
        ),
        start_response,
    )

    payload = json.loads(body[0].decode())
    assert captured["status"] == "201 Created"
    assert payload["phone"] == "+5511987654321"
    assert payload["email"] == "carla@example.com"
    assert "privacy_terms_notice" in payload


def test_handler_update_returns_200(monkeypatch):
    repo = FakeWaitlistRepository()
    repo.seed(
        {
            "phone": "+5511987654321",
            "name": "Old",
            "email": "old@example.com",
            "birth_date": "1992-03-04",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        }
    )
    monkeypatch.setattr(waitlist_handler, "service", WaitlistService(repo))
    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    body = waitlist_handler.handle_waitlist_request(
        _environ(
            "POST",
            {
                "phone": "+5511987654321",
                "name": "Nova",
                "email": "nova@example.com",
                "birth_date": "1992-03-04",
            },
        ),
        start_response,
    )

    payload = json.loads(body[0].decode())
    assert captured["status"] == "200 OK"
    assert payload["name"] == "Nova"


def test_handler_rejects_underage_portuguese(monkeypatch):
    monkeypatch.setattr(waitlist_handler, "service", WaitlistService(FakeWaitlistRepository()))
    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    body = waitlist_handler.handle_waitlist_request(
        _environ(
            "POST",
            {
                "phone": "+5511987654321",
                "name": "Minor",
                "email": "minor@example.com",
                "birth_date": "2015-01-01",
            },
        ),
        start_response,
    )

    payload = json.loads(body[0].decode())
    assert captured["status"] == "400 Bad Request"
    assert "pelo menos" in payload["error"]


def test_handler_list_returns_leads(monkeypatch):
    repo = FakeWaitlistRepository()
    repo.seed(
        {
            "phone": "+5511111111111",
            "name": "A",
            "email": "a@example.com",
            "birth_date": "1990-01-01",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        }
    )
    monkeypatch.setattr(waitlist_handler, "service", WaitlistService(repo))
    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    body = waitlist_handler.handle_waitlist_request(_environ("GET"), start_response)
    payload = json.loads(body[0].decode())
    assert captured["status"] == "200 OK"
    assert payload["count"] == 1
    assert payload["leads"][0]["phone"] == "+5511111111111"


def test_handler_maps_validation_error(monkeypatch):
    class BoomService:
        def upsert_lead(self, *args, **kwargs):
            raise WaitlistValidationError("phone deve ser um número WhatsApp válido (formato E.164)")

    monkeypatch.setattr(waitlist_handler, "service", BoomService())
    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    with patch.object(waitlist_handler, "service", BoomService()):
        body = waitlist_handler.handle_waitlist_request(
            _environ("POST", {"phone": "x", "name": "A", "email": "a@b.com", "birth_date": "1990-01-01"}),
            start_response,
        )

    assert captured["status"] == "400 Bad Request"
    assert b"phone" in body[0]
