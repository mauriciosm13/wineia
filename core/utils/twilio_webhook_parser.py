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


def extract_inbound_media(payload):
    raw_num_media = get_first_value(payload, "NumMedia")
    if raw_num_media is None:
        return None

    try:
        num_media = int(str(raw_num_media).strip())
    except (TypeError, ValueError):
        return None

    if num_media < 1:
        return None

    return {
        "num_media": num_media,
        "url": get_first_value(payload, "MediaUrl0"),
        "content_type": get_first_value(payload, "MediaContentType0"),
    }


def has_inbound_media(media):
    if not isinstance(media, dict):
        return False

    try:
        return int(media.get("num_media", 0)) >= 1
    except (TypeError, ValueError):
        return False


def get_first_value(payload, key):
    values = payload.get(key, [])

    if not values:
        return None

    return values[0]
