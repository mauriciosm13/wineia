import json
from domain.services.ia_service import IAService
from infrastructure.repositories.datastore_customer_repository import DatastoreCustomerRepository
from core.utils.twilio_webhook_parser import extract_message, extract_phone
from domain.services.ia_service import IAService
from domain.services.messaging_service import process_incoming_message
from infrastructure.external.twilio_whatsapp_client import create_twilio_whatsapp_client
from infrastructure.repositories.datastore_customer_repository import DatastoreCustomerRepository
from logging import info


repository = DatastoreCustomerRepository()
ia_service = IAService()


def _create_dependencies():
    return {
        "repository": DatastoreCustomerRepository(),
        "messaging_gateway": create_twilio_whatsapp_client(),
        "ia_service": IAService(),
    }

def handle_generate_suggestion(environ, start_response):
    length = int(environ.get("CONTENT_LENGTH", 0))
    body = environ["wsgi.input"].read(length)

    payload = json.loads(body or b"{}")

    phone = payload.get("phone")
    message = str(payload.get("message"))

    if not message:
        start_response("400 Bad Request", [("Content-Type", "application/json")])
        return [b'{"error":"message is required"}']

    customer = None
    if phone:
        customer = repository.get_by_phone(phone)

    response = ia_service.generate_response(customer, message)

    response_body = json.dumps({"reply": response}).encode("utf-8")

    dependencies = _create_dependencies()
    
    dependencies["messaging_gateway"].send_text(phone, response)

    start_response("200 OK", [("Content-Type", "application/json")])
    return [response_body]
