from core.utils.twilio_webhook_parser import extract_message, extract_phone, parse_webhook_body
from domain.services.ia_service import IAService
from domain.services.messaging_service import process_incoming_message
from infrastructure.external.twilio_whatsapp_client import create_twilio_whatsapp_client
from infrastructure.repositories.datastore_customer_repository import DatastoreCustomerRepository
from logging import info
from core.utils.request import read_request_body


def _create_dependencies():
    return {
        "repository": DatastoreCustomerRepository(),
        "messaging_gateway": create_twilio_whatsapp_client(),
        "ia_service": IAService(),
    }


def handle_whatsapp_webhook(environ, start_response):
    body = read_request_body(environ, decode=True)
    content_type = environ.get("CONTENT_TYPE")
    payload = parse_webhook_body(body, content_type=content_type)

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
