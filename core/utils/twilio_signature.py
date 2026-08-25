from urllib.parse import parse_qs

from twilio.request_validator import RequestValidator


def public_request_url(environ):
    forwarded_proto = environ.get("HTTP_X_FORWARDED_PROTO", "")
    if forwarded_proto:
        scheme = forwarded_proto.split(",")[0].strip()
    else:
        scheme = environ.get("wsgi.url_scheme") or "https"

    host = environ.get("HTTP_HOST", "")
    path = environ.get("PATH_INFO", "")
    query = environ.get("QUERY_STRING", "")

    url = f"{scheme}://{host}{path}"
    if query:
        url = f"{url}?{query}"
    return url


def form_params_from_body(raw_body, content_type, parsed_payload):
    normalized_content_type = str(content_type or "").lower()

    if "application/json" in normalized_content_type:
        return raw_body or ""

    payload = parsed_payload if parsed_payload is not None else parse_qs(raw_body or "")
    return {key: values[0] if values else "" for key, values in payload.items()}


def signature_is_valid(auth_token, url, params_or_body, signature):
    if not auth_token or not str(auth_token).strip():
        return False
    if not url or not str(url).strip():
        return False
    if not signature or not str(signature).strip():
        return False

    validator = RequestValidator(auth_token)
    return validator.validate(url, params_or_body, signature)
