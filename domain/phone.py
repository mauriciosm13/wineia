import re

_WHATSAPP_PREFIX = "whatsapp:"
_E164_PATTERN = re.compile(r"^\+[1-9]\d{7,14}$")


def normalize_phone(raw):
    """Normalize WhatsApp/phone input to E.164-ish form (+digits).

    Strips whitespace, optional ``whatsapp:`` prefix, and non-digit characters
    except a leading ``+``. Returns ``None`` when the value cannot be normalized.
    """
    if raw is None:
        return None
    if not isinstance(raw, str):
        return None

    value = raw.strip()
    if not value:
        return None

    if value.lower().startswith(_WHATSAPP_PREFIX):
        value = value[len(_WHATSAPP_PREFIX):].strip()

    digits = re.sub(r"\D", "", value)
    if not digits:
        return None

    normalized = f"+{digits}"
    if not _E164_PATTERN.match(normalized):
        return None
    return normalized
