import os

import requests

from core.utils.load_config import load_config
from core.utils.twilio_media import is_stt_compatible_media_content_type, normalize_media_content_type, stt_filename_for_media_content_type

XAI_STT_URL = "https://api.x.ai/v1/stt"
DEFAULT_GROK_STT_MODEL = "grok-voice-transcribe-2.0"
GROK_STT_LANGUAGE = "pt"
GROK_STT_TIMEOUT = int(os.getenv("XAI_STT_TIMEOUT", os.getenv("XAI_API_TIMEOUT", "60")))


class GrokSTTError(Exception):
    pass


def _resolve_api_key(api_key=None):
    if api_key is not None:
        value = str(api_key).strip()
        return value or None

    env_key = str(os.getenv("XAI_API_KEY") or "").strip()
    if env_key:
        return env_key

    try:
        config = load_config()
    except (OSError, ValueError, TypeError):
        return None

    if not isinstance(config, dict):
        return None

    fallback = str(config.get("XAI_API_KEY") or "").strip()
    return fallback or None


def _resolve_model(model=None):
    if model is not None:
        value = str(model).strip()
        if value:
            return value

    for env_name in ("XAI_STT_MODEL", "GROK_STT_MODEL"):
        env_value = str(os.getenv(env_name) or "").strip()
        if env_value:
            return env_value

    try:
        config = load_config()
    except (OSError, ValueError, TypeError):
        return DEFAULT_GROK_STT_MODEL

    if isinstance(config, dict):
        for key in ("XAI_STT_MODEL", "GROK_STT_MODEL"):
            config_value = str(config.get(key) or "").strip()
            if config_value:
                return config_value

    return DEFAULT_GROK_STT_MODEL


def transcribe_audio(
    content,
    content_type,
    *,
    api_key=None,
    model=None,
    language=None,
    timeout=None,
    session=None,
):
    if not content:
        raise GrokSTTError("audio content is required")

    normalized_type = normalize_media_content_type(content_type)
    if not is_stt_compatible_media_content_type(normalized_type):
        raise GrokSTTError("audio content type is not supported for transcription")

    key = _resolve_api_key(api_key)
    if not key:
        raise GrokSTTError("xai api key is not configured")

    filename = stt_filename_for_media_content_type(normalized_type)
    request_timeout = GROK_STT_TIMEOUT if timeout is None else timeout
    resolved_model = _resolve_model(model)
    resolved_language = GROK_STT_LANGUAGE if language is None else str(language).strip() or GROK_STT_LANGUAGE
    http = session if session is not None else requests

    # xAI requires non-file fields before `file` in the multipart body.
    data = [
        ("model", resolved_model),
        ("language", resolved_language),
    ]
    files = {
        "file": (filename, content, normalized_type),
    }
    headers = {"Authorization": f"Bearer {key}"}

    try:
        response = http.post(
            XAI_STT_URL,
            headers=headers,
            data=data,
            files=files,
            timeout=request_timeout,
        )
    except requests.RequestException as exc:
        raise GrokSTTError("transcription request failed") from exc

    if response.status_code < 200 or response.status_code >= 300:
        raise GrokSTTError(f"transcription failed with HTTP {response.status_code}")

    try:
        payload = response.json()
    except ValueError as exc:
        raise GrokSTTError("transcription response is not json") from exc

    text = ""
    if isinstance(payload, dict):
        text = str(payload.get("text") or "").strip()
    elif isinstance(payload, str):
        text = payload.strip()

    if not text:
        raise GrokSTTError("transcription is empty")

    return text
