import json
from domain.services.customer_service import CustomerService
from infrastructure.repositories.datastore_customer_repository import DatastoreCustomerRepository

repository = DatastoreCustomerRepository()
service = CustomerService(repository)

def handle_create_customer(environ, start_response):
    length = int(environ.get("CONTENT_LENGTH", 0))
    body = environ["wsgi.input"].read(length)

    payload = json.loads(body)

    phone = payload.get("phone")
    name = payload.get("name")
    status = payload.get("status")
    plan = payload.get("plan")

    if not phone:
        start_response("400 Bad Request", [("Content-Type", "application/json")])
        return [json.dumps({"error": "phone is required"}).encode()]

    customer = service.create_customer(phone, name, status, plan)

    start_response("201 Created", [("Content-Type", "application/json")])
    return [json.dumps(customer, default=str).encode()]