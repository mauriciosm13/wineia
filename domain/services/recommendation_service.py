from datetime import datetime, timedelta, timezone

from domain.models.customer import CustomerStatus
from domain.services.ia_service import IAService
from domain.services.recommendation_selector_service import select_wine
from infrastructure.repositories.datastore_customer_repository import DatastoreCustomerRepository
from infrastructure.repositories.datastore_recommendation_repository import DatastoreRecommendationRepository

ia_service = IAService()


def enqueue_send_message(phone, message):
    from infrastructure.queue.cloud_tasks_client import CloudTasksClient

    CloudTasksClient().enqueue("send_message", {"phone": phone, "message": message})


def send_recommendations():
    customers = DatastoreCustomerRepository.list_active()
    wine = select_wine()

    DatastoreRecommendationRepository.update_content_last_sent(wine.key)

    for customer in customers:
        if customer.get("status") != CustomerStatus.active:
            continue

        last = customer.get("last_recommendation_at")

        if last:
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)

            if datetime.now(timezone.utc) - last < timedelta(hours=24):
                continue

        if customer.get("messages_sent_today", 0) >= 2:
            continue

        response = ia_service.generate_recommendation(
            wine=wine,
            preferences=customer.get("preferences"),
        )
        enqueue_send_message(customer["phone"], response)
        customer["last_recommendation_at"] = datetime.utcnow()
        customer["messages_sent_today"] = customer.get("messages_sent_today", 0) + 1

        DatastoreCustomerRepository.update(customer)
