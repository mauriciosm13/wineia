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
        "media_downloader": object(),
        "audio_transcriber": object(),
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
        inbound_media=None,
        media_downloader=mock_dependencies["media_downloader"],
        audio_transcriber=mock_dependencies["audio_transcriber"],
    )


def test_whatsapp_webhook_routes_media_only_to_domain():
    body = (
        b"Body=&WaId=5511999&NumMedia=1"
        b"&MediaUrl0=https%3A%2F%2Fapi.twilio.com%2Fmedia%2Fabc"
        b"&MediaContentType0=image%2Fjpeg"
    )
    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    mock_dependencies = {
        "repository": object(),
        "message_sender": object(),
        "ia_service": object(),
        "media_downloader": object(),
        "audio_transcriber": object(),
    }

    with patch("api.handlers.whatsapp_handler.signature_is_valid", return_value=True):
        with patch("api.handlers.whatsapp_handler.process_incoming_message") as mock_process:
            with patch(
                "api.handlers.whatsapp_handler._create_dependencies",
                return_value=mock_dependencies,
            ):
                response_body = handle_whatsapp_webhook(_webhook_environ(body), start_response)

    assert captured["status"] == "200 OK"
    assert response_body == [b'{"status":"received"}']
    mock_process.assert_called_once_with(
        phone="5511999",
        message=None,
        repository=mock_dependencies["repository"],
        message_sender=mock_dependencies["message_sender"],
        ia_service=mock_dependencies["ia_service"],
        inbound_media={
            "num_media": 1,
            "url": "https://api.twilio.com/media/abc",
            "content_type": "image/jpeg",
        },
        media_downloader=mock_dependencies["media_downloader"],
        audio_transcriber=mock_dependencies["audio_transcriber"],
    )


def test_whatsapp_webhook_skips_empty_body_without_media():
    body = b"Body=&WaId=5511999&NumMedia=0"
    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    with patch("api.handlers.whatsapp_handler.signature_is_valid", return_value=True):
        with patch("api.handlers.whatsapp_handler.process_incoming_message") as mock_process:
            with patch("api.handlers.whatsapp_handler._create_dependencies") as mock_deps:
                response_body = handle_whatsapp_webhook(_webhook_environ(body), start_response)

    assert captured["status"] == "200 OK"
    assert response_body == [b'{"status":"received"}']
    mock_process.assert_not_called()
    mock_deps.assert_called_once()


def test_whatsapp_webhook_dependencies_use_enqueue_send_message():
    from api.handlers import whatsapp_handler
    from domain.services.recommendation_service import enqueue_send_message
    from infrastructure.external.grok_stt_client import transcribe_audio
    from infrastructure.external.twilio_media_client import download_twilio_media

    with patch("api.handlers.whatsapp_handler.DatastoreCustomerRepository"):
        with patch("api.handlers.whatsapp_handler.IAService"):
            deps = whatsapp_handler._create_dependencies()

    assert deps["message_sender"] is enqueue_send_message
    assert deps["media_downloader"] is download_twilio_media
    assert deps["audio_transcriber"] is transcribe_audio
    assert "messaging_gateway" not in deps
