import requests

from core.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_TIMEOUT
from core.utils.twilio_media import is_allowed_media_content_type, max_bytes_for_media_content_type, normalize_media_content_type


class TwilioMediaDownloadError(Exception):
    pass


def download_twilio_media(
    url,
    *,
    account_sid=None,
    auth_token=None,
    timeout=None,
    declared_content_type=None,
    session=None,
):
    media_url = str(url or "").strip()
    if not media_url:
        raise TwilioMediaDownloadError("media url is required")

    sid = account_sid if account_sid is not None else TWILIO_ACCOUNT_SID
    token = auth_token if auth_token is not None else TWILIO_AUTH_TOKEN
    if not sid or not token:
        raise TwilioMediaDownloadError("twilio credentials are not configured")

    request_timeout = TWILIO_TIMEOUT if timeout is None else timeout
    http = session if session is not None else requests

    try:
        response = http.get(
            media_url,
            auth=(sid, token),
            timeout=request_timeout,
            stream=True,
            allow_redirects=True,
        )
    except requests.RequestException as exc:
        raise TwilioMediaDownloadError("media download request failed") from exc

    if response.status_code < 200 or response.status_code >= 300:
        raise TwilioMediaDownloadError(f"media download failed with HTTP {response.status_code}")

    content_type = normalize_media_content_type(
        response.headers.get("Content-Type") or declared_content_type
    )
    if not is_allowed_media_content_type(content_type):
        raise TwilioMediaDownloadError("media content type is not allowed")

    max_bytes = max_bytes_for_media_content_type(content_type)
    content_length = response.headers.get("Content-Length")
    if content_length is not None:
        try:
            if int(content_length) > max_bytes:
                raise TwilioMediaDownloadError("media exceeds max size")
        except (TypeError, ValueError):
            pass

    chunks = []
    total = 0
    try:
        for chunk in response.iter_content(chunk_size=64 * 1024):
            if not chunk:
                continue
            total += len(chunk)
            if total > max_bytes:
                raise TwilioMediaDownloadError("media exceeds max size")
            chunks.append(chunk)
    finally:
        response.close()

    if total == 0:
        raise TwilioMediaDownloadError("media body is empty")

    return {
        "content": b"".join(chunks),
        "content_type": content_type,
        "size": total,
    }
