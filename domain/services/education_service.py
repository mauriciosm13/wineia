from datetime import datetime

from domain.services.education_eligibility import is_eligible_for_weekly_education
from domain.services.ia_service import IAService
from domain.services.recommendation_service import enqueue_send_message
from infrastructure.repositories.datastore_customer_repository import DatastoreCustomerRepository

ia_service = IAService()


def send_weekly_education():
    customers = DatastoreCustomerRepository.list_active()
    message = ia_service.generate_weekly_education()

    for customer in customers:
        if not is_eligible_for_weekly_education(customer):
            continue

        enqueue_send_message(customer["phone"], message)
        customer["last_weekly_education_at"] = datetime.utcnow()
        DatastoreCustomerRepository.update(customer)
