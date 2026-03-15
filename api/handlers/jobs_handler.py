from domain.services.recommendation_service import RecommendationService
from infrastructure.repositories.datastore_customer_repository import DatastoreCustomerRepository
from infrastructure.external.whatsapp_client import WhatsAppClient

repository = DatastoreCustomerRepository()
whatsapp = WhatsAppClient()

service = RecommendationService(repository, whatsapp)

def handle_daily_recommendations(environ, start_response):

    service.send_daily_recommendations()

    start_response("200 OK", [("Content-Type", "application/json")])
    return [b'{"status":"daily job executed"}']