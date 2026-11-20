import json
from domain.services.waitlist_service import WaitlistService, WaitlistValidationError
from infrastructure.repositories.datastore_waitlist_repository import DatastoreWaitlistRepository

repository = DatastoreWaitlistRepository()
service = WaitlistService(repository)


def _respond_json(start_response, status, payload):
    start_response(status, [("Content-Type", "application/json")])
    return [json.dumps(payload, default=str).encode()]


def _respond_error(start_response, status, message):
    return _respond_json(start_response, status, {"error": message})


def handle_waitlist_request(environ, start_response):
    method = environ.get("REQUEST_METHOD", "")

    if method == "POST":
        return handle_create_waitlist_lead(environ, start_response)

    if method == "GET":
        return handle_list_waitlist_leads(environ, start_response)

    return _respond_error(start_response, "405 Method Not Allowed", "Method not allowed")


def handle_create_waitlist_lead(environ, start_response):
    length = int(environ.get("CONTENT_LENGTH") or 0)
    body = environ["wsgi.input"].read(length) if length else b""

    if not body:
        return _respond_error(start_response, "400 Bad Request", "Body é obrigatório")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return _respond_error(start_response, "400 Bad Request", "JSON inválido")

    if not isinstance(payload, dict):
        return _respond_error(start_response, "400 Bad Request", "JSON inválido")

    try:
        lead, created = service.upsert_lead(
            payload.get("phone"),
            payload.get("name"),
            payload.get("email"),
            payload.get("birth_date"),
        )
    except WaitlistValidationError as exc:
        return _respond_error(start_response, "400 Bad Request", str(exc))

    status = "201 Created" if created else "200 OK"
    return _respond_json(start_response, status, lead)


def handle_list_waitlist_leads(environ, start_response):
    leads = service.list_leads()
    return _respond_json(start_response, "200 OK", {"leads": leads, "count": len(leads)})
