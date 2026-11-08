from datetime import datetime, timezone

from domain.models.customer import CustomerStatus, normalize_customer_fields
from domain.recommendation_scheduled_cadence import record_scheduled_recommendation_send, should_send_scheduled_recommendation, tier_gets_scheduled_recommendations
from domain.services.ia_service import IAService
from domain.services.recommendation_selector_service import select_wine
from infrastructure.repositories.datastore_customer_repository import DatastoreCustomerRepository
from infrastructure.repositories.datastore_recommendation_repository import DatastoreRecommendationRepository

ia_service = IAService()


def enqueue_send_message(phone, message):
    from infrastructure.queue.cloud_tasks_client import CloudTasksClient

    CloudTasksClient().enqueue("send_message", {"phone": phone, "message": message})


def send_recommendations(now_utc=None):
    """Enqueue scheduled recommendations. Pass `now_utc` in tests for deterministic time."""
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)

    customers = DatastoreCustomerRepository.list_active()
    wine = select_wine()

    DatastoreRecommendationRepository.update_content_last_sent(wine.key)
    message = ia_service.generate_recommendation(wine=wine)

    for record in customers:
        if not isinstance(record, dict):
            customer = dict(record)
        else:
            customer = record

        normalize_customer_fields(customer)

        if customer.get("status") != CustomerStatus.active:
            continue

        plan_tier = customer.get("plan_tier")
        if not tier_gets_scheduled_recommendations(plan_tier):
            continue

        if not should_send_scheduled_recommendation(customer, now_utc):
            continue

        enqueue_send_message(customer["phone"], message)
        record_scheduled_recommendation_send(customer, now_utc)

        DatastoreCustomerRepository.update(customer)
