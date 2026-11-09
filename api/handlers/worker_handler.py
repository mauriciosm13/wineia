import json
from infrastructure.external.twilio_whatsapp_client import create_twilio_whatsapp_client


client = create_twilio_whatsapp_client()


def _respond_error(start_response, status, message):
    start_response(status, [("Content-Type", "application/json")])
    return [json.dumps({"error": message}).encode()]


def handle_send_message(environ, start_response):

    length = int(environ.get("CONTENT_LENGTH", 0))
    body = environ["wsgi.input"].read(length)

    payload = json.loads(body)

    phone = payload["phone"]
    message = payload["message"]

    client.send_text(phone, message)

    start_response("200 OK", [("Content-Type", "application/json")])

    return [b'{"status":"sent"}']


def handle_send_campaign(environ, start_response):
    length = int(environ.get("CONTENT_LENGTH", 0) or 0)
    body = environ["wsgi.input"].read(length)

    if not body:
        return _respond_error(start_response, "400 Bad Request", "Body is required")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return _respond_error(start_response, "400 Bad Request", "Invalid JSON")

    phone = payload.get("phone")
    message = payload.get("message")

    if not phone or not isinstance(phone, str):
        return _respond_error(start_response, "400 Bad Request", "phone is required")

    if not message or not isinstance(message, str):
        return _respond_error(start_response, "400 Bad Request", "message is required")

    client.send_text(phone, message)

    start_response("200 OK", [("Content-Type", "application/json")])

    return [b'{"status":"sent"}']
