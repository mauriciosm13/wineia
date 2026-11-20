import base64
import os

import requests

from core.utils.load_config import load_config

XAI_CHAT_COMPLETIONS_URL = "https://api.x.ai/v1/chat/completions"
DEFAULT_GROK_MODEL = "grok-4.7"
GROK_TIMEOUT = int(os.getenv("XAI_API_TIMEOUT", "60"))

_GROK_IMAGE_MEDIA_TYPES = {
    "image/jpeg": "image/jpeg",
    "image/jpg": "image/jpeg",
    "image/png": "image/png",
}


class GrokClientError(Exception):
    pass


class GrokClient:

    def generate(system_prompt, user_prompt=None, images=None, *, api_key=None, model=None, timeout=None, session=None):
        key = _resolve_api_key(api_key)
        if not key:
            raise GrokClientError("xai api key is not configured")

        resolved_model = _resolve_model(model)
        request_timeout = GROK_TIMEOUT if timeout is None else timeout
        http = session if session is not None else requests

        messages = [{"role": "system", "content": "" if system_prompt is None else str(system_prompt)}]
        messages.append(
            {
                "role": "user",
                "content": _build_user_content(user_prompt=user_prompt, images=images),
            }
        )

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": resolved_model,
            "messages": messages,
            "max_tokens": 1000,
        }

        try:
            response = http.post(
                XAI_CHAT_COMPLETIONS_URL,
                headers=headers,
                json=payload,
                timeout=request_timeout,
            )
        except requests.RequestException as exc:
            raise GrokClientError("generation request failed") from exc

        if response.status_code < 200 or response.status_code >= 300:
            raise GrokClientError(f"generation failed with HTTP {response.status_code}")

        try:
            body = response.json()
        except ValueError as exc:
            raise GrokClientError("generation response is not json") from exc

        return _extract_text(body)


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

    for env_name in ("XAI_API_MODEL", "GROK_API_MODEL"):
        env_value = str(os.getenv(env_name) or "").strip()
        if env_value:
            return env_value

    try:
        config = load_config()
    except (OSError, ValueError, TypeError):
        return DEFAULT_GROK_MODEL

    if isinstance(config, dict):
        for key in ("XAI_API_MODEL", "GROK_API_MODEL"):
            config_value = str(config.get(key) or "").strip()
            if config_value:
                return config_value

    return DEFAULT_GROK_MODEL


def _build_user_content(user_prompt=None, images=None):
    blocks = []

    for image in images or []:
        media_type = _normalize_image_media_type((image or {}).get("media_type"))
        data = (image or {}).get("data")
        if not media_type or data is None:
            continue
        if isinstance(data, bytes):
            encoded = base64.b64encode(data).decode("ascii")
        else:
            encoded = str(data)
        if not encoded:
            continue
        blocks.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{media_type};base64,{encoded}",
                },
            }
        )

    text = "" if user_prompt is None else str(user_prompt)
    if text or not blocks:
        blocks.append({"type": "text", "text": text})

    if len(blocks) == 1 and blocks[0].get("type") == "text":
        return blocks[0]["text"]

    return blocks


def _normalize_image_media_type(media_type):
    if media_type is None:
        return None
    normalized = str(media_type).strip().lower().split(";", 1)[0].strip()
    return _GROK_IMAGE_MEDIA_TYPES.get(normalized)


def _extract_text(body):
    if not isinstance(body, dict):
        return ""

    choices = body.get("choices") or []
    if not choices:
        return ""

    first = choices[0] if isinstance(choices[0], dict) else {}
    message = first.get("message") if isinstance(first, dict) else None
    if not isinstance(message, dict):
        return ""

    content = message.get("content")
    if content is None:
        return ""
    return str(content)
