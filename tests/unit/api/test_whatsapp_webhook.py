from io import BytesIO
from unittest.mock import patch

from api.handlers.whatsapp_handler import handle_whatsapp_webhook


def _webhook_environ(body: bytes, signature: str = "test-signature") -> dict:
    return {
        "REQUEST_METHOD": "POST",
        "CONTENT_LENGTH": str(len(body)),
        "wsgi.input": BytesIO(body),
        "CONTENT_TYPE": "application/x-www-form-urlencoded",
        "HTTP_X_TWILIO_SIGNATURE": signature,
        "HTTP_HOST": "example.com",
        "PATH_INFO": "/webhook/whatsapp",
        "wsgi.url_scheme": "https",
    }


def test_whatsapp_webhook_rejects_invalid_signature():
    body = b"Body=hello&WaId=5511999"
    captured = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = headers

    with patch("api.handlers.whatsapp_handler.signature_is_valid", return_value=False):
        with patch("api.handlers.whatsapp_handler.process_incoming_message") as mock_process:
            with patch("api.handlers.whatsapp_handler._create_dependencies") as mock_deps:
                response_body = handle_whatsapp_webhook(_webhook_environ(body), start_response)

    assert captured["status"] == "403 Forbidden"
    assert captured["headers"] == [("Content-Type", "application/json")]
    assert response_body == [b'{"error":"invalid signature"}']
    mock_process.assert_not_called()
    mock_deps.assert_not_called()


def test_whatsapp_webhook_accepts_valid_signature():
    body = b"Body=hello&WaId=5511999"
    captured = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = headers

    mock_dependencies = {
        "repository": object(),
        "message_sender": object(),
        "ia_service": object(),
    }

    with patch("api.handlers.whatsapp_handler.signature_is_valid", return_value=True):
        with patch("api.handlers.whatsapp_handler.process_incoming_message") as mock_process:
            with patch(
                "api.handlers.whatsapp_handler._create_dependencies",
                return_value=mock_dependencies,
            ):
                response_body = handle_whatsapp_webhook(_webhook_environ(body), start_response)

    assert captured["status"] == "200 OK"
    assert captured["headers"] == [("Content-Type", "application/json")]
    assert response_body == [b'{"status":"received"}']
    mock_process.assert_called_once_with(
        phone="5511999",
        message="hello",
        repository=mock_dependencies["repository"],
        message_sender=mock_dependencies["message_sender"],
        ia_service=mock_dependencies["ia_service"],
    )


def test_whatsapp_webhook_dependencies_use_enqueue_send_message():
    from api.handlers import whatsapp_handler
    from domain.services.recommendation_service import enqueue_send_message

    with patch("api.handlers.whatsapp_handler.DatastoreCustomerRepository"):
        with patch("api.handlers.whatsapp_handler.IAService"):
            deps = whatsapp_handler._create_dependencies()

    assert deps["message_sender"] is enqueue_send_message
    assert "messaging_gateway" not in deps
