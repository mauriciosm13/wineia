import base64

from anthropic import Anthropic
from core.utils.load_config import load_config

_CLAUDE_IMAGE_MEDIA_TYPES = {
    "image/jpeg": "image/jpeg",
    "image/jpg": "image/jpeg",
    "image/png": "image/png",
}


class ClaudeClient:

    def generate(system_prompt, user_prompt=None, images=None):
        config = load_config()
        api_key = config["ANTHROPIC_API_KEY"]
        model = config["ANTHROPIC_API_MODEL"]

        client = Anthropic(api_key=api_key)

        content = _build_user_content(user_prompt=user_prompt, images=images)

        message = client.messages.create(
                model=model,
                max_tokens=1000,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": content,
                    }
                ],
            )

        contents = getattr(message, "content", None) or []
        for item in contents:
            if getattr(item, "type", None) == "text" and hasattr(item, "text"):
                return item.text or ""

        return ""


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
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": encoded,
                },
            }
        )

    text = "" if user_prompt is None else str(user_prompt)
    if text or not blocks:
        blocks.append(text)

    if len(blocks) == 1 and isinstance(blocks[0], str):
        return blocks[0]

    content = []
    for block in blocks:
        if isinstance(block, str):
            content.append({"type": "text", "text": block})
        else:
            content.append(block)
    return content


def _normalize_image_media_type(media_type):
    if media_type is None:
        return None
    normalized = str(media_type).strip().lower().split(";", 1)[0].strip()
    return _CLAUDE_IMAGE_MEDIA_TYPES.get(normalized)
