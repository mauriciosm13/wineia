from datetime import datetime, timedelta
from domain.services.ia_service import IAService
from domain.models.customer import CustomerStatus
from domain.services.recommendation_selector_service import select_wine
from infrastructure.repositories.datastore_customer_repository import DatastoreCustomerRepository
from infrastructure.repositories.datastore_recommendation_repository import DatastoreRecommendationRepository
from infrastructure.external.twilio_whatsapp_client import send_text
from datetime import datetime, timedelta, timezone

ia_service = IAService()

def send_recommendations():
    customers = DatastoreCustomerRepository.list_active()
    wine = select_wine()

    response = ia_service.generate_recommendation(wine=wine)
    DatastoreRecommendationRepository.update_content_last_sent(wine.key)

    for customer in customers:
        if customer.get("status") != CustomerStatus.active:
            return False

        last = customer.get("last_recommendation_at")

        if last:
            # Normaliza caso `last` venha do banco sem timezone
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            
            if datetime.now(timezone.utc) - last < timedelta(hours=24):
                return False

        # 🔒 regra 3 — limite diário
        if customer.get("messages_sent_today", 0) >= 2:
            return False

        #preferences = DatastoreRecommendationRepository.get(customer["phone"])
        send_text(customer["phone"], response)
        customer["last_recommendation_at"] = datetime.utcnow()
        customer["messages_sent_today"] = customer.get("messages_sent_today", 0) + 1

        DatastoreCustomerRepository.update(customer)
