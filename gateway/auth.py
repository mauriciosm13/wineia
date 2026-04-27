from core.config import INTERNAL_API_TOKEN


def validate_bearer(environ):
    expected_token = INTERNAL_API_TOKEN
    if not expected_token:
        return False

    authorization = str(environ.get("HTTP_AUTHORIZATION", "")).strip()
    return authorization == f"Bearer {expected_token}"
