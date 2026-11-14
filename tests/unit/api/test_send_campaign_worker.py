import json
from io import BytesIO
from unittest.mock import patch

from api.handlers.worker_handler import handle_send_campaign
from api.routes import ROUTES, route_request


def _campaign_environ(secret=None, phone="+5511999990000", message="Campaign copy"):
    raw = json.dumps({"phone": phone, "message": message}).encode()
    environ = {
        "REQUEST_METHOD": "POST",
        "PATH_INFO": "/workers/send-campaign",
        "CONTENT_LENGTH": str(len(raw)),
        "wsgi.input": BytesIO(raw),
    }
    if secret is not None:
        environ["HTTP_X_JOB_INTERNAL_SECRET"] = secret
    return environ


def test_routes_maps_send_campaign_to_handler():
    assert ROUTES["/workers/send-campaign"] is handle_send_campaign


def test_send_campaign_missing_secret_returns_401_and_does_not_send():
    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    with patch("api.internal_job_auth.JOB_INTERNAL_SECRET", "server-secret"):
        with patch("api.handlers.worker_handler.client.send_text") as send_text:
            body = route_request(_campaign_environ(), start_response)

    assert captured["status"] == "401 Unauthorized"
    assert body == [b'{"error": "unauthorized"}']
    send_text.assert_not_called()


def test_send_campaign_wrong_secret_returns_401_and_does_not_send():
    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    with patch("api.internal_job_auth.JOB_INTERNAL_SECRET", "server-secret"):
        with patch("api.handlers.worker_handler.client.send_text") as send_text:
            body = route_request(_campaign_environ(secret="wrong-secret"), start_response)

    assert captured["status"] == "401 Unauthorized"
    assert body == [b'{"error": "unauthorized"}']
    send_text.assert_not_called()


def test_send_campaign_matching_secret_sends_text():
    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    phone = "+5511988887777"
    message = "Weekly campaign"
    with patch("api.internal_job_auth.JOB_INTERNAL_SECRET", "server-secret"):
        with patch("api.handlers.worker_handler.client.send_text") as send_text:
            body = route_request(_campaign_environ(secret="server-secret", phone=phone, message=message), start_response)

    assert captured["status"] != "404 Not Found"
    assert captured["status"] == "200 OK"
    send_text.assert_called_once_with(phone, message)
    assert body == [b'{"status":"sent"}']
