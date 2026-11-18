from datetime import datetime

from core.utils.twilio_media import classify_media_content_type, is_allowed_media_content_type, is_stt_compatible_media_content_type
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

MEDIA_STT_FAILED_MESSAGE = (
    "Recebemos seu audio, mas nao conseguimos transcreve-lo agora. "
    "Tente novamente em breve ou envie sua pergunta em texto."
)

MEDIA_VISION_FAILED_MESSAGE = (
    "Recebemos sua foto, mas nao conseguimos analisa-la agora. "
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
    audio_transcriber=None,
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
    media_kind = None
    if has_inbound_media(inbound_media):
        media_kind = classify_media_content_type((inbound_media or {}).get("content_type"))

    if media_kind == "image":
        return _handle_image_media(
            phone=phone,
            customer=customer,
            inbound_media=inbound_media,
            caption=text,
            repository=repository,
            message_sender=message_sender,
            ia_service=ia_service,
            media_downloader=media_downloader,
        )

    if not text and has_inbound_media(inbound_media):
        return _handle_media_only(
            phone=phone,
            customer=customer,
            inbound_media=inbound_media,
            repository=repository,
            message_sender=message_sender,
            ia_service=ia_service,
            media_downloader=media_downloader,
            audio_transcriber=audio_transcriber,
        )

    return _complete_ia_turn(
        phone=phone,
        customer=customer,
        user_message=message,
        repository=repository,
        message_sender=message_sender,
        ia_service=ia_service,
    )


def can_send_message(customer, now=None):
    return can_send_on_demand(customer, now)


def _handle_media_only(
    phone,
    customer,
    inbound_media,
    repository,
    message_sender,
    ia_service,
    media_downloader,
    audio_transcriber,
):
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

    downloaded_type = content_type
    content = None
    if isinstance(downloaded, dict):
        downloaded_type = downloaded.get("content_type") or content_type
        content = downloaded.get("content")

    kind = classify_media_content_type(downloaded_type)
    if kind == "audio":
        return _handle_audio_media(
            phone=phone,
            customer=customer,
            content=content,
            content_type=downloaded_type,
            repository=repository,
            message_sender=message_sender,
            ia_service=ia_service,
            audio_transcriber=audio_transcriber,
        )

    message_sender(phone, MEDIA_UNAVAILABLE_MESSAGE)
    return {"status": "media_unprocessable"}


def _handle_image_media(
    phone,
    customer,
    inbound_media,
    caption,
    repository,
    message_sender,
    ia_service,
    media_downloader,
):
    content_type = (inbound_media or {}).get("content_type")
    media_url = str((inbound_media or {}).get("url") or "").strip()
    if media_downloader is None or not media_url:
        message_sender(phone, MEDIA_UNAVAILABLE_MESSAGE)
        return {"status": "media_unprocessable"}

    try:
        downloaded = media_downloader(media_url)
    except Exception:
        message_sender(phone, MEDIA_DOWNLOAD_FAILED_MESSAGE)
        return {"status": "media_download_failed"}

    downloaded_type = content_type
    content = None
    if isinstance(downloaded, dict):
        downloaded_type = downloaded.get("content_type") or content_type
        content = downloaded.get("content")

    if not content or classify_media_content_type(downloaded_type) != "image":
        message_sender(phone, MEDIA_VISION_FAILED_MESSAGE)
        return {"status": "media_vision_failed"}

    try:
        response_message = ia_service.generate_vision_response(
            customer,
            content,
            downloaded_type,
            caption=caption or None,
        )
    except ClaudeBudgetExceededError:
        message_sender(phone, SERVICE_UNAVAILABLE_MESSAGE)
        return {"status": "budget_exceeded"}
    except Exception:
        message_sender(phone, MEDIA_VISION_FAILED_MESSAGE)
        return {"status": "media_vision_failed"}

    message_sender(phone, response_message)

    customer["messages_sent_today"] = customer.get("messages_sent_today", 0) + 1
    customer["last_message_at"] = datetime.utcnow().isoformat()
    repository.update(customer)

    return {"status": "processed", "message": response_message}


def _handle_audio_media(
    phone,
    customer,
    content,
    content_type,
    repository,
    message_sender,
    ia_service,
    audio_transcriber,
):
    if audio_transcriber is None or not content:
        message_sender(phone, MEDIA_STT_FAILED_MESSAGE)
        return {"status": "media_stt_failed"}

    if not is_stt_compatible_media_content_type(content_type):
        message_sender(phone, MEDIA_STT_FAILED_MESSAGE)
        return {"status": "media_stt_failed"}

    try:
        transcript = audio_transcriber(content, content_type)
    except Exception:
        message_sender(phone, MEDIA_STT_FAILED_MESSAGE)
        return {"status": "media_stt_failed"}

    transcript_text = str(transcript or "").strip()
    if not transcript_text:
        message_sender(phone, MEDIA_STT_FAILED_MESSAGE)
        return {"status": "media_stt_failed"}

    return _complete_ia_turn(
        phone=phone,
        customer=customer,
        user_message=transcript_text,
        repository=repository,
        message_sender=message_sender,
        ia_service=ia_service,
    )


def _complete_ia_turn(phone, customer, user_message, repository, message_sender, ia_service):
    try:
        response_message = ia_service.generate_response(customer, user_message)
    except ClaudeBudgetExceededError:
        message_sender(phone, SERVICE_UNAVAILABLE_MESSAGE)
        return {"status": "budget_exceeded"}

    message_sender(phone, response_message)

    customer["messages_sent_today"] = customer.get("messages_sent_today", 0) + 1
    customer["last_message_at"] = datetime.utcnow().isoformat()
    repository.update(customer)

    return {"status": "processed", "message": response_message}


def _should_cancel(message):
    normalized_message = str(message or "").strip().lower()
    return normalized_message == "cancelar"


def _normalize_customer(customer):
    if isinstance(customer, list):
        return customer[0] if customer else None

    return customer
