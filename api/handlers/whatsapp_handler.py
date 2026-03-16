import json
from domain.services.ia_service import IAService
from domain.services.messaging_service import MessagingService
from infrastructure.external.whatsapp_client import WhatsAppClient
from infrastructure.repositories.datastore_customer_repository import DatastoreCustomerRepository

repository = DatastoreCustomerRepository()
whatsapp_client = WhatsAppClient()
ia_service = IAService()
service = MessagingService()


def handle_whatsapp_webhook(environ, start_response):

    length = int(environ.get("CONTENT_LENGTH", 0))
    body = environ["wsgi.input"].read(length)

    payload = json.loads(body)

    phone = payload.get("from")
    message = payload.get("message")

    service.process_incoming_message(phone, message)

    start_response("200 OK", [("Content-Type", "application/json")])
    return [b'{"status":"received"}']