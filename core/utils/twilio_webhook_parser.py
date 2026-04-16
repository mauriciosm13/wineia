import json
from urllib.parse import parse_qs


def parse_webhook_body(raw_body, content_type=None):
    normalized_content_type = str(content_type or "").lower()

    if "application/json" in normalized_content_type:
        return json.loads(raw_body or "{}")

    return parse_qs(raw_body)


def extract_phone(payload):
    whatsapp_number = get_first_value(payload, "WaId")

    if whatsapp_number:
        return whatsapp_number

    sender = get_first_value(payload, "From")
    if sender and sender.startswith("whatsapp:"):
        return sender.replace("whatsapp:", "", 1)

    return sender


def extract_message(payload):
    return get_first_value(payload, "Body")


def get_first_value(payload, key):
    values = payload.get(key, [])

    if not values:
        return None

    return values[0]
