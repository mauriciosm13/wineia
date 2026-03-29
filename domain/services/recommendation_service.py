from datetime import datetime, timedelta
from domain.services.ia_service import IAService
from domain.models.customer import CustomerStatus
from domain.services.recommendation_selector_service import select_wine
from infrastructure.repositories.datastore_customer_repository import DatastoreCustomerRepository
from infrastructure.repositories.datastore_recommendation_repository import DatastoreRecommendationRepository

ia_service = IAService()

def send_recommendations():
    customers = DatastoreCustomerRepository.list_active()
    wine = select_wine()
    
    response = ia_service.generate_recommendation(wine=wine)
    print(response)


    for customer in customers:
        if customer.get("status") != CustomerStatus.active:
            return False

        last = customer.get("last_recommendation_at")

        if last:
            if datetime.utcnow() - last < timedelta(hours=24):
                return False

        # 🔒 regra 3 — limite diário
        if customer.get("messages_sent_today", 0) >= 2:
            return False

        #preferences = DatastoreRecommendationRepository.get(customer["phone"])

        DatastoreCustomerRepository.update(customer)
