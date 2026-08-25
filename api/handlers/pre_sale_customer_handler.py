import json
import re
from domain.services.pre_sale_customer_service import PreSaleCustomerService
from infrastructure.repositories.datastore_pre_sale_customer_repository import DatastorePreSaleCustomerRepository

repository = DatastorePreSaleCustomerRepository()
service = PreSaleCustomerService(repository)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _respond_error(start_response, status, message):
    start_response(status, [("Content-Type", "application/json")])
    return [json.dumps({"error": message}).encode()]


def _validate_required_string(payload, field_name):
    value = payload.get(field_name)

    if value is None:
        return None, f"{field_name} is required"

    if not isinstance(value, str):
        return None, f"{field_name} must be a string"

    value = value.strip()
    if not value:
        return None, f"{field_name} cannot be empty"

    return value, None


def handle_create_pre_sale_customer(environ, start_response):
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

    name, error = _validate_required_string(payload, "name")
    if error:
        return _respond_error(start_response, "400 Bad Request", error)

    email, error = _validate_required_string(payload, "email")
    if error:
        return _respond_error(start_response, "400 Bad Request", error)

    if not EMAIL_REGEX.match(email):
        return _respond_error(start_response, "400 Bad Request", "email must be a valid email")

    whatsapp, error = _validate_required_string(payload, "whatsapp")
    if error:
        return _respond_error(start_response, "400 Bad Request", error)

    preferences = payload.get("preferences")
    if preferences is None:
        return _respond_error(start_response, "400 Bad Request", "preferences is required")

    if not isinstance(preferences, list):
        return _respond_error(start_response, "400 Bad Request", "preferences must be a list")

    if not preferences:
        return _respond_error(start_response, "400 Bad Request", "preferences cannot be empty")

    normalized_preferences = []
    for preference in preferences:
        if not isinstance(preference, str):
            return _respond_error(start_response, "400 Bad Request", "preferences items must be strings")

        normalized_preference = preference.strip()
        if not normalized_preference:
            return _respond_error(start_response, "400 Bad Request", "preferences items cannot be empty")

        normalized_preferences.append(normalized_preference)

    customer = service.create_customer(name, email, whatsapp, normalized_preferences)

    start_response("201 Created", [("Content-Type", "application/json")])
    return [json.dumps(customer, default=str).encode()]
