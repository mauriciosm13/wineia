from io import BytesIO
from unittest.mock import MagicMock, patch

from api.handlers.whatsapp_handler import handle_whatsapp_webhook
from api.routes import route_request
from api.webhook_rate_limit import reset_webhook_rate_limiter_for_tests


def _webhook_environ(body: bytes, ip: str = "203.0.113.10") -> dict:
    return {
        "REQUEST_METHOD": "POST",
        "CONTENT_LENGTH": str(len(body)),
        "wsgi.input": BytesIO(body),
        "CONTENT_TYPE": "application/x-www-form-urlencoded",
        "HTTP_X_TWILIO_SIGNATURE": "sig",
        "HTTP_HOST": "example.com",
        "PATH_INFO": "/webhook/whatsapp",
        "wsgi.url_scheme": "https",
        "REMOTE_ADDR": ip,
    }


def setup_function():
    reset_webhook_rate_limiter_for_tests()


def test_route_rejects_webhook_when_ip_over_limit():
    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    environ = {
        "REQUEST_METHOD": "POST",
        "PATH_INFO": "/webhook/whatsapp",
        "REMOTE_ADDR": "198.51.100.1",
    }
    mock_handler = MagicMock()

    with patch("api.webhook_rate_limit.WEBHOOK_RATE_LIMIT_IP_MAX", 1):
        with patch("api.webhook_rate_limit.WEBHOOK_RATE_LIMIT_IP_WINDOW_SECONDS", 60):
            with patch.dict("api.routes.ROUTES", {"/webhook/whatsapp": mock_handler}):
                route_request(environ, start_response)
                body = route_request(environ, start_response)

    assert captured["status"] == "429 Too Many Requests"
    assert body == [b'{"error": "rate_limit_exceeded"}']
    assert mock_handler.call_count == 1


def test_route_allows_webhook_under_ip_limit():
    mock_handler = MagicMock(return_value=[b"ok"])

    def start_response(status, headers):
        pass

    environ = {
        "REQUEST_METHOD": "POST",
        "PATH_INFO": "/webhook/whatsapp",
        "REMOTE_ADDR": "198.51.100.2",
    }

    with patch("api.webhook_rate_limit.WEBHOOK_RATE_LIMIT_IP_MAX", 5):
        with patch("api.webhook_rate_limit.WEBHOOK_RATE_LIMIT_IP_WINDOW_SECONDS", 60):
            with patch.dict("api.routes.ROUTES", {"/webhook/whatsapp": mock_handler}):
                body = route_request(environ, start_response)

    mock_handler.assert_called_once()
    assert body == [b"ok"]


def test_whatsapp_webhook_rejects_phone_over_limit():
    body = b"Body=hello&WaId=5511888"
    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    mock_dependencies = {
        "repository": object(),
        "messaging_gateway": object(),
        "ia_service": object(),
    }

    with patch("api.webhook_rate_limit.WEBHOOK_RATE_LIMIT_PHONE_MAX", 1):
        with patch("api.webhook_rate_limit.WEBHOOK_RATE_LIMIT_PHONE_WINDOW_SECONDS", 60):
            with patch("api.handlers.whatsapp_handler.signature_is_valid", return_value=True):
                with patch("api.handlers.whatsapp_handler.process_incoming_message") as mock_process:
                    with patch(
                        "api.handlers.whatsapp_handler._create_dependencies",
                        return_value=mock_dependencies,
                    ):
                        handle_whatsapp_webhook(_webhook_environ(body), start_response)
                        response_body = handle_whatsapp_webhook(_webhook_environ(body), start_response)

    assert captured["status"] == "429 Too Many Requests"
    assert response_body == [b'{"error": "rate_limit_exceeded"}']
    mock_process.assert_called_once()


def test_whatsapp_webhook_allows_phone_under_limit():
    body = b"Body=hello&WaId=5511777"
    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    mock_dependencies = {
        "repository": object(),
        "messaging_gateway": object(),
        "ia_service": object(),
    }

    with patch("api.webhook_rate_limit.WEBHOOK_RATE_LIMIT_PHONE_MAX", 5):
        with patch("api.webhook_rate_limit.WEBHOOK_RATE_LIMIT_PHONE_WINDOW_SECONDS", 60):
            with patch("api.handlers.whatsapp_handler.signature_is_valid", return_value=True):
                with patch("api.handlers.whatsapp_handler.process_incoming_message") as mock_process:
                    with patch(
                        "api.handlers.whatsapp_handler._create_dependencies",
                        return_value=mock_dependencies,
                    ):
                        response_body = handle_whatsapp_webhook(_webhook_environ(body), start_response)

    assert captured["status"] == "200 OK"
    assert response_body == [b'{"status":"received"}']
    mock_process.assert_called_once()
