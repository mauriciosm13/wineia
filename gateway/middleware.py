import json

from gateway.auth import validate_bearer
from gateway.policies import PROTECTED_ROUTES, PUBLIC_ROUTES, TWILIO_WEBHOOK_ROUTES
from gateway.twilio import validate_twilio_request
from core.utils.request import read_request_body


def _json_response(start_response, status, message):
    start_response(status, [("Content-Type", "application/json")])
    return [json.dumps({"error": message}).encode("utf-8")]


def enforce_gateway(environ, start_response):
    path = environ.get("PATH_INFO", "")

    if path in PUBLIC_ROUTES:
        return None

    if path in TWILIO_WEBHOOK_ROUTES:
        raw_body = read_request_body(environ, decode=True)
        if not validate_twilio_request(environ, raw_body):
            return _json_response(start_response, "403 Forbidden", "invalid signature")
        return None

    if path in PROTECTED_ROUTES and not validate_bearer(environ):
        return _json_response(start_response, "401 Unauthorized", "unauthorized")

    return None
