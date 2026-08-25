from core.config import TWILIO_AUTH_TOKEN
from core.utils.twilio_signature import form_params_from_body, public_request_url, signature_is_valid
from core.utils.twilio_webhook_parser import extract_message, extract_phone, parse_webhook_body
from domain.services.ia_service import IAService
from domain.services.messaging_service import process_incoming_message
from infrastructure.external.twilio_whatsapp_client import create_twilio_whatsapp_client
from infrastructure.repositories.datastore_customer_repository import DatastoreCustomerRepository


def _create_dependencies():
    return {
        "repository": DatastoreCustomerRepository(),
        "messaging_gateway": create_twilio_whatsapp_client(),
        "ia_service": IAService(),
    }


def handle_whatsapp_webhook(environ, start_response):
    length = int(environ.get("CONTENT_LENGTH", 0))
    raw_body = environ["wsgi.input"].read(length).decode("utf-8")
    content_type = environ.get("CONTENT_TYPE")
    signature = environ.get("HTTP_X_TWILIO_SIGNATURE", "")

    request_url = public_request_url(environ)
    params_or_body = form_params_from_body(raw_body, content_type, parsed_payload=None)

    if not signature_is_valid(TWILIO_AUTH_TOKEN, request_url, params_or_body, signature):
        start_response("403 Forbidden", [("Content-Type", "application/json")])
        return [b'{"error":"invalid signature"}']

    payload = parse_webhook_body(raw_body, content_type=content_type)

    phone = extract_phone(payload)
    message = extract_message(payload)
    dependencies = _create_dependencies()

    if phone and message:
        process_incoming_message(
            phone=phone,
            message=message,
            repository=dependencies["repository"],
            messaging_gateway=dependencies["messaging_gateway"],
            ia_service=dependencies["ia_service"],
        )

    start_response("200 OK", [("Content-Type", "application/json")])
    return [b'{"status":"received"}']
