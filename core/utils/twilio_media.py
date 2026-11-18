TWILIO_MEDIA_MAX_BYTES_IMAGE = 5 * 1024 * 1024
TWILIO_MEDIA_MAX_BYTES_AUDIO = 16 * 1024 * 1024

TWILIO_MEDIA_IMAGE_MIME_TYPES = frozenset(
    {
        "image/jpeg",
        "image/jpg",
        "image/png",
    }
)

TWILIO_MEDIA_AUDIO_MIME_TYPES = frozenset(
    {
        "audio/ogg",
        "audio/opus",
        "audio/amr",
        "audio/3gpp",
        "audio/aac",
        "audio/mpeg",
        "audio/mp4",
    }
)

TWILIO_MEDIA_ALLOWED_MIME_TYPES = TWILIO_MEDIA_IMAGE_MIME_TYPES | TWILIO_MEDIA_AUDIO_MIME_TYPES


def normalize_media_content_type(content_type):
    if content_type is None:
        return None

    normalized = str(content_type).strip().lower()
    if not normalized:
        return None

    return normalized.split(";", 1)[0].strip()


def classify_media_content_type(content_type):
    normalized = normalize_media_content_type(content_type)
    if normalized in TWILIO_MEDIA_IMAGE_MIME_TYPES:
        return "image"
    if normalized in TWILIO_MEDIA_AUDIO_MIME_TYPES:
        return "audio"
    return None


def is_allowed_media_content_type(content_type):
    return classify_media_content_type(content_type) is not None


def max_bytes_for_media_content_type(content_type):
    kind = classify_media_content_type(content_type)
    if kind == "image":
        return TWILIO_MEDIA_MAX_BYTES_IMAGE
    if kind == "audio":
        return TWILIO_MEDIA_MAX_BYTES_AUDIO
    return None
