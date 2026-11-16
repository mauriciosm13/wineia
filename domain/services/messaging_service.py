from datetime import datetime

from domain.claude_budget import ClaudeBudgetExceededError
from domain.on_demand_entitlements import can_send_on_demand, reset_daily_counter_if_needed

SERVICE_UNAVAILABLE_MESSAGE = (
    "Desculpe, o serviço está temporariamente indisponível. Tente novamente em breve."
)


def process_incoming_message(phone, message, repository, message_sender, ia_service, now=None):
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


def _should_cancel(message):
    normalized_message = str(message or "").strip().lower()
    return normalized_message == "cancelar"


def _normalize_customer(customer):
    if isinstance(customer, list):
        return customer[0] if customer else None

    return customer
