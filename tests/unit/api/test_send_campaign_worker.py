import json
from io import BytesIO
from unittest.mock import MagicMock, patch

from api.handlers.worker_handler import handle_send_campaign
from api.routes import ROUTES, route_request


def _start_response_capture(captured):
    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = headers

    return start_response


def test_send_campaign_success_calls_twilio():
    captured = {}
    mock_client = MagicMock()
    payload = {"phone": "+5511999999999", "message": "Campanha teste"}
    body = json.dumps(payload).encode()
    environ = {
        "CONTENT_LENGTH": str(len(body)),
        "wsgi.input": BytesIO(body),
    }

    with patch("api.handlers.worker_handler.client", mock_client):
        response = handle_send_campaign(environ, _start_response_capture(captured))

    assert captured["status"] == "200 OK"
    assert json.loads(response[0].decode()) == {"status": "sent"}
    mock_client.send_text.assert_called_once_with("+5511999999999", "Campanha teste")


def test_send_campaign_missing_phone_returns_400():
    captured = {}
    body = json.dumps({"message": "hello"}).encode()
    environ = {
        "CONTENT_LENGTH": str(len(body)),
        "wsgi.input": BytesIO(body),
    }

    with patch("api.handlers.worker_handler.client", MagicMock()):
        response = handle_send_campaign(environ, _start_response_capture(captured))

    assert captured["status"] == "400 Bad Request"
    assert json.loads(response[0].decode()) == {"error": "phone is required"}


def test_send_campaign_missing_message_returns_400():
    captured = {}
    body = json.dumps({"phone": "+5511"}).encode()
    environ = {
        "CONTENT_LENGTH": str(len(body)),
        "wsgi.input": BytesIO(body),
    }

    with patch("api.handlers.worker_handler.client", MagicMock()):
        response = handle_send_campaign(environ, _start_response_capture(captured))

    assert captured["status"] == "400 Bad Request"
    assert json.loads(response[0].decode()) == {"error": "message is required"}


def test_send_campaign_invalid_json_returns_400():
    captured = {}
    body = b"{not-json"
    environ = {
        "CONTENT_LENGTH": str(len(body)),
        "wsgi.input": BytesIO(body),
    }

    response = handle_send_campaign(environ, _start_response_capture(captured))

    assert captured["status"] == "400 Bad Request"
    assert json.loads(response[0].decode()) == {"error": "Invalid JSON"}


def test_send_campaign_route_registered():
    assert ROUTES["/workers/send-campaign"] is handle_send_campaign


def test_route_request_rejects_send_campaign_without_secret():
    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    environ = {
        "REQUEST_METHOD": "POST",
        "PATH_INFO": "/workers/send-campaign",
    }

    with patch("api.internal_job_auth.JOB_INTERNAL_SECRET", "server-secret"):
        body = route_request(environ, start_response)

    assert captured["status"] == "401 Unauthorized"
    assert body == [b'{"error": "unauthorized"}']
