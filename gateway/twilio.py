from urllib.parse import parse_qs
from core.config import TWILIO_AUTH_TOKEN
from twilio.request_validator import RequestValidator


def _build_request_url(environ):
    scheme = environ.get("HTTP_X_FORWARDED_PROTO") or environ.get("wsgi.url_scheme", "https")
    host = environ.get("HTTP_HOST", "")
    path = environ.get("PATH_INFO", "")
    query_string = environ.get("QUERY_STRING", "")

    url = f"{scheme}://{host}{path}"
    if query_string:
        url = f"{url}?{query_string}"

    return url


def validate_twilio_request(environ, raw_body):
    if not TWILIO_AUTH_TOKEN:
        return False

    signature = environ.get("HTTP_X_TWILIO_SIGNATURE", "")
    if not signature:
        return False

    content_type = str(environ.get("CONTENT_TYPE", "")).lower()
    params = None

    if "application/x-www-form-urlencoded" in content_type:
        params = {key: values[0] for key, values in parse_qs(raw_body, keep_blank_values=True).items()}

    validator = RequestValidator(TWILIO_AUTH_TOKEN)
    return validator.validate(_build_request_url(environ), params, signature)
