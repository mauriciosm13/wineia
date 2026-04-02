import json
from infrastructure.external.twilio_whatsapp_client import (
    create_twilio_whatsapp_client,
)


client = create_twilio_whatsapp_client()


def handle_send_message(environ, start_response):

    length = int(environ.get("CONTENT_LENGTH", 0))
    body = environ["wsgi.input"].read(length)

    payload = json.loads(body)

    phone = payload["phone"]
    message = payload["message"]

    client.send_text(phone, message)

    start_response("200 OK", [("Content-Type", "application/json")])

    return [b'{"status":"sent"}']
