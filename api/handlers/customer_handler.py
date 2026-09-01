import json
from urllib.parse import unquote

from api.handlers.pre_sale_customer_handler import handle_activate_pre_sale_customer, handle_create_pre_sale_customer
from domain.services.customer_service import CustomerService
from infrastructure.repositories.datastore_customer_repository import DatastoreCustomerRepository

repository = DatastoreCustomerRepository()
service = CustomerService(repository)


def _respond_error(start_response, status, message):
    start_response(status, [("Content-Type", "application/json")])
    return [json.dumps({"error": message}).encode()]


def _respond_json(start_response, status, payload):
    start_response(status, [("Content-Type", "application/json")])
    return [json.dumps(payload, default=str).encode()]


def handle_customer_request(environ, start_response):
    path = environ.get("PATH_INFO", "")
    method = environ.get("REQUEST_METHOD", "")

    if path == "/customers":
        if method == "GET":
            return handle_list_customers(environ, start_response)
        if method == "POST":
            return handle_create_customer(environ, start_response)
        return _respond_error(start_response, "405 Method Not Allowed", "Method not allowed")

    if path == "/customers/pre-sale":
        return handle_create_pre_sale_customer(environ, start_response)

    if path == "/customers/pre-sale/activate":
        return handle_activate_pre_sale_customer(environ, start_response)

    prefix = "/customers/"
    if path.startswith(prefix):
        phone = unquote(path[len(prefix):])
        if phone and "/" not in phone:
            if method == "GET":
                return handle_get_customer(environ, start_response, phone)
            if method == "PATCH":
                return handle_update_customer(environ, start_response, phone)
            return _respond_error(start_response, "405 Method Not Allowed", "Method not allowed")

    start_response("404 Not Found", [("Content-Type", "text/plain")])
    return [b"Not Found"]


def handle_create_customer(environ, start_response):
    if environ.get("REQUEST_METHOD") != "POST":
        return _respond_error(start_response, "405 Method Not Allowed", "Method not allowed")

    length = int(environ.get("CONTENT_LENGTH", 0))
    body = environ["wsgi.input"].read(length)

    if not body:
        return _respond_error(start_response, "400 Bad Request", "Body is required")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return _respond_error(start_response, "400 Bad Request", "Invalid JSON")

    phone = payload.get("phone")
    name = payload.get("name")
    status = payload.get("status")
    plan = payload.get("plan")

    if not phone:
        return _respond_error(start_response, "400 Bad Request", "phone is required")

    customer = service.create_customer(phone, name, status, plan)

    return _respond_json(start_response, "201 Created", customer)


def handle_list_customers(environ, start_response):
    if environ.get("REQUEST_METHOD") != "GET":
        return _respond_error(start_response, "405 Method Not Allowed", "Method not allowed")

    customers = service.list_customers()

    return _respond_json(start_response, "200 OK", customers)


def handle_get_customer(environ, start_response, phone):
    if environ.get("REQUEST_METHOD") != "GET":
        return _respond_error(start_response, "405 Method Not Allowed", "Method not allowed")

    customer = service.get_customer(phone)
    if customer is None:
        return _respond_error(start_response, "404 Not Found", "Customer not found")

    return _respond_json(start_response, "200 OK", customer)


def handle_update_customer(environ, start_response, phone):
    if environ.get("REQUEST_METHOD") != "PATCH":
        return _respond_error(start_response, "405 Method Not Allowed", "Method not allowed")

    length = int(environ.get("CONTENT_LENGTH", 0))
    body = environ["wsgi.input"].read(length)

    if not body:
        return _respond_error(start_response, "400 Bad Request", "Body is required")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return _respond_error(start_response, "400 Bad Request", "Invalid JSON")

    try:
        customer = service.update_customer(phone, payload)
    except ValueError as error:
        return _respond_error(start_response, "400 Bad Request", str(error))

    if customer is None:
        return _respond_error(start_response, "404 Not Found", "Customer not found")

    return _respond_json(start_response, "200 OK", customer)
