from datetime import datetime

from domain.on_demand_entitlements import can_send_on_demand, reset_daily_counter_if_needed


def process_incoming_message(phone, message, repository, messaging_gateway, ia_service, now=None):
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
        messaging_gateway.send_text(phone, warning_message)
        return {"status": "limit_reached"}

    response_message = ia_service.generate_response(customer, message)
    messaging_gateway.send_text(phone, response_message)

    customer["messages_sent_today"] = customer.get("messages_sent_today", 0) + 1
    customer["last_message_at"] = datetime.utcnow().isoformat()
    repository.update(customer)

    return {"status": "processed", "message": response_message}


def can_send_message(customer, now=None):
    return can_send_on_demand(customer, now)


def _should_cancel(message):
    normalized_message = str(message or "").strip().lower()
    return normalized_message == "cancelar"


def _normalize_customer(customer):
    if isinstance(customer, list):
        return customer[0] if customer else None

    return customer
