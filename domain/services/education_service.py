from datetime import datetime

from core.logging import log_info
from domain.claude_budget import ClaudeBudgetExceededError
from domain.services.education_eligibility import is_eligible_for_weekly_education
from domain.services.ia_service import IAService
from domain.services.recommendation_service import enqueue_send_message
from infrastructure.repositories.datastore_customer_repository import DatastoreCustomerRepository

ia_service = IAService()


def send_weekly_education():
    customers = DatastoreCustomerRepository.list_active()
    try:
        message = ia_service.generate_weekly_education()
    except ClaudeBudgetExceededError:
        log_info("send_weekly_education skipped: claude daily call budget exceeded")
        return

    for customer in customers:
        if not is_eligible_for_weekly_education(customer):
            continue

        enqueue_send_message(customer["phone"], message)
        customer["last_weekly_education_at"] = datetime.utcnow()
        DatastoreCustomerRepository.update(customer)
