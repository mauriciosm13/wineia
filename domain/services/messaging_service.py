from datetime import datetime

from core.utils.twilio_media import is_allowed_media_content_type
from core.utils.twilio_webhook_parser import has_inbound_media
from domain.claude_budget import ClaudeBudgetExceededError
from domain.on_demand_entitlements import can_send_on_demand, reset_daily_counter_if_needed

SERVICE_UNAVAILABLE_MESSAGE = (
    "Desculpe, o serviço está temporariamente indisponível. Tente novamente em breve."
)

MEDIA_UNAVAILABLE_MESSAGE = (
    "Recebemos sua midia, mas ainda nao conseguimos processa-la. "
    "Envie sua pergunta em texto por enquanto."
)

MEDIA_UNSUPPORTED_MESSAGE = (
    "Recebemos um arquivo que ainda nao suportamos. "
    "Envie uma foto (JPEG/PNG), um audio, ou sua pergunta em texto."
)

MEDIA_DOWNLOAD_FAILED_MESSAGE = (
    "Nao conseguimos baixar sua midia agora. "
    "Tente novamente em breve ou envie sua pergunta em texto."
)


def process_incoming_message(
    phone,
    message,
    repository,
    message_sender,
    ia_service,
    now=None,
    inbound_media=None,
    media_downloader=None,
):
    customer = _normalize_customer(repository.get_by_phone(phone))

    if not customer:
        return None

    if _should_cancel(message):
        customer["status"] = "canceled"
        repository.update(customer)
        return {"status": "canceled"}

    reset_daily_counter_if_needed(customer, now)

    if not can_send_message(customer, now):
        warning_message = (
            "Voce atingiu o limite diario de mensagens gratuitas. "
            "Tente novamente amanha ou atualize seu plano."
        )
        message_sender(phone, warning_message)
        return {"status": "limit_reached"}

    text = str(message or "").strip()
    if not text and has_inbound_media(inbound_media):
        return _handle_media_only(
            phone=phone,
            inbound_media=inbound_media,
            message_sender=message_sender,
            media_downloader=media_downloader,
        )

    try:
        response_message = ia_service.generate_response(customer, message)
    except ClaudeBudgetExceededError:
        message_sender(phone, SERVICE_UNAVAILABLE_MESSAGE)
        return {"status": "budget_exceeded"}

    message_sender(phone, response_message)

    customer["messages_sent_today"] = customer.get("messages_sent_today", 0) + 1
    customer["last_message_at"] = datetime.utcnow().isoformat()
    repository.update(customer)

    return {"status": "processed", "message": response_message}


def can_send_message(customer, now=None):
    return can_send_on_demand(customer, now)


def _handle_media_only(phone, inbound_media, message_sender, media_downloader):
    content_type = (inbound_media or {}).get("content_type")
    if not is_allowed_media_content_type(content_type):
        message_sender(phone, MEDIA_UNSUPPORTED_MESSAGE)
        return {"status": "media_unsupported"}

    media_url = str((inbound_media or {}).get("url") or "").strip()
    if media_downloader is None or not media_url:
        message_sender(phone, MEDIA_UNAVAILABLE_MESSAGE)
        return {"status": "media_unprocessable"}

    try:
        downloaded = media_downloader(media_url)
    except Exception:
        message_sender(phone, MEDIA_DOWNLOAD_FAILED_MESSAGE)
        return {"status": "media_download_failed"}

    size = None
    downloaded_type = content_type
    if isinstance(downloaded, dict):
        size = downloaded.get("size")
        downloaded_type = downloaded.get("content_type") or content_type

    message_sender(phone, MEDIA_UNAVAILABLE_MESSAGE)
    result = {"status": "media_downloaded", "content_type": downloaded_type}
    if size is not None:
        result["size"] = size
    return result


def _should_cancel(message):
    normalized_message = str(message or "").strip().lower()
    return normalized_message == "cancelar"


def _normalize_customer(customer):
    if isinstance(customer, list):
        return customer[0] if customer else None

    return customer
