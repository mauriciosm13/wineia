import json
from domain.services.ia_service import IAService
from infrastructure.repositories.datastore_customer_repository import DatastoreCustomerRepository


repository = DatastoreCustomerRepository()
ia_service = IAService()


def handle_generate_suggestion(environ, start_response):
    length = int(environ.get("CONTENT_LENGTH", 0))
    body = environ["wsgi.input"].read(length)

    payload = json.loads(body or b"{}")

    phone = payload.get("phone")
    message = payload.get("message")

    if not message:
        start_response("400 Bad Request", [("Content-Type", "application/json")])
        return [b'{"error":"message is required"}']

    customer = None
    if phone:
        customer = repository.get_by_phone(phone)

    response = ia_service.generate_response(customer, message)

    response_body = json.dumps({"reply": response}).encode("utf-8")

    start_response("200 OK", [("Content-Type", "application/json")])
    return [response_body]

