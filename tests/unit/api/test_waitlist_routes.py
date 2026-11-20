import json
from io import BytesIO
from unittest.mock import MagicMock, patch

from api.routes import route_request
from api.waitlist_rate_limit import reset_waitlist_rate_limiter_for_tests


_OPERATOR_SECRET = "waitlist-operator-secret"


def setup_function():
    reset_waitlist_rate_limiter_for_tests()


def _environ(method, path, body=None, ip="203.0.113.50", secret=None):
    raw = b"" if body is None else body
    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "CONTENT_LENGTH": str(len(raw)),
        "wsgi.input": BytesIO(raw),
        "REMOTE_ADDR": ip,
    }
    if secret is not None:
        environ["HTTP_X_JOB_INTERNAL_SECRET"] = secret
    return environ


def test_post_waitlist_is_public_and_creates(monkeypatch):
    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    payload = {
        "phone": "+5511987654321",
        "name": "Beatriz",
        "email": "beatriz@example.com",
        "birth_date": "1995-06-15",
    }
    lead = {
        **payload,
        "email": "beatriz@example.com",
        "created_at": "2026-11-20T12:00:00Z",
        "updated_at": "2026-11-20T12:00:00Z",
        "privacy_terms_notice": "notice",
    }
    mock_handler = MagicMock(
        return_value=[json.dumps(lead).encode()]
    )

    with patch.dict("api.routes.ROUTES", {"/waitlist": mock_handler}):
        # Ensure router does not require secret for POST
        monkeypatch.setattr("api.internal_job_auth.JOB_INTERNAL_SECRET", _OPERATOR_SECRET)
        body = route_request(
            _environ("POST", "/waitlist", json.dumps(payload).encode()),
            start_response,
        )

    mock_handler.assert_called_once()
    assert body == [json.dumps(lead).encode()]


def test_post_waitlist_rate_limited():
    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    mock_handler = MagicMock()
    environ = _environ("POST", "/waitlist", b'{"phone":"+5511999999999"}', ip="198.51.100.9")

    with patch("api.waitlist_rate_limit.WAITLIST_RATE_LIMIT_IP_MAX", 1):
        with patch("api.waitlist_rate_limit.WAITLIST_RATE_LIMIT_IP_WINDOW_SECONDS", 60):
            with patch.dict("api.routes.ROUTES", {"/waitlist": mock_handler}):
                route_request(environ, start_response)
                body = route_request(environ, start_response)

    assert captured["status"] == "429 Too Many Requests"
    assert body == [b'{"error": "rate_limit_exceeded"}']
    assert mock_handler.call_count == 1


def test_get_waitlist_requires_job_secret(monkeypatch):
    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    mock_handler = MagicMock()
    monkeypatch.setattr("api.internal_job_auth.JOB_INTERNAL_SECRET", _OPERATOR_SECRET)

    with patch.dict("api.routes.ROUTES", {"/waitlist": mock_handler}):
        body = route_request(_environ("GET", "/waitlist"), start_response)

    assert captured["status"] == "401 Unauthorized"
    assert body == [b'{"error": "unauthorized"}']
    mock_handler.assert_not_called()


def test_get_waitlist_authorized_reaches_handler(monkeypatch):
    mock_handler = MagicMock(return_value=[b'{"leads":[],"count":0}'])

    def start_response(status, headers):
        pass

    monkeypatch.setattr("api.internal_job_auth.JOB_INTERNAL_SECRET", _OPERATOR_SECRET)

    with patch.dict("api.routes.ROUTES", {"/waitlist": mock_handler}):
        body = route_request(
            _environ("GET", "/waitlist", secret=_OPERATOR_SECRET),
            start_response,
        )

    mock_handler.assert_called_once()
    assert body == [b'{"leads":[],"count":0}']
