import os

import requests

from core.utils.load_config import load_config
from core.utils.twilio_media import is_stt_compatible_media_content_type, normalize_media_content_type, stt_filename_for_media_content_type

OPENAI_TRANSCRIPTIONS_URL = "https://api.openai.com/v1/audio/transcriptions"
OPENAI_STT_MODEL = "whisper-1"
OPENAI_STT_LANGUAGE = "pt"
OPENAI_STT_TIMEOUT = int(os.getenv("OPENAI_STT_TIMEOUT", "60"))


class OpenAISTTError(Exception):
    pass


def _resolve_api_key(api_key=None):
    if api_key is not None:
        value = str(api_key).strip()
        return value or None

    env_key = str(os.getenv("OPENAI_API_KEY") or "").strip()
    if env_key:
        return env_key

    try:
        config = load_config()
    except (OSError, ValueError, TypeError):
        return None

    if not isinstance(config, dict):
        return None

    fallback = str(config.get("OPENAI_API_KEY") or "").strip()
    return fallback or None


def transcribe_audio(
    content,
    content_type,
    *,
    api_key=None,
    timeout=None,
    session=None,
):
    if not content:
        raise OpenAISTTError("audio content is required")

    normalized_type = normalize_media_content_type(content_type)
    if not is_stt_compatible_media_content_type(normalized_type):
        raise OpenAISTTError("audio content type is not supported for transcription")

    key = _resolve_api_key(api_key)
    if not key:
        raise OpenAISTTError("openai api key is not configured")

    filename = stt_filename_for_media_content_type(normalized_type)
    request_timeout = OPENAI_STT_TIMEOUT if timeout is None else timeout
    http = session if session is not None else requests

    files = {
        "file": (filename, content, normalized_type),
    }
    data = {
        "model": OPENAI_STT_MODEL,
        "language": OPENAI_STT_LANGUAGE,
    }
    headers = {"Authorization": f"Bearer {key}"}

    try:
        response = http.post(
            OPENAI_TRANSCRIPTIONS_URL,
            headers=headers,
            data=data,
            files=files,
            timeout=request_timeout,
        )
    except requests.RequestException as exc:
        raise OpenAISTTError("transcription request failed") from exc

    if response.status_code < 200 or response.status_code >= 300:
        raise OpenAISTTError(f"transcription failed with HTTP {response.status_code}")

    try:
        payload = response.json()
    except ValueError as exc:
        raise OpenAISTTError("transcription response is not json") from exc

    text = ""
    if isinstance(payload, dict):
        text = str(payload.get("text") or "").strip()
    elif isinstance(payload, str):
        text = payload.strip()

    if not text:
        raise OpenAISTTError("transcription is empty")

    return text
