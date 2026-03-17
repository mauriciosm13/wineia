from datetime import datetime, timedelta
from google.cloud import datastore
from google.cloud.datastore.query import PropertyFilter
from infrastructure.datastore.client import client
from domain.repositories.recommendation_repository import RecommendationRepository


class DatastoreRecommendationRepository(RecommendationRepository):

    CONTENT_KIND = "RecommendationContent"
    HISTORY_KIND = "RecommendationHistory"

    @staticmethod
    def save_content(content):
        key = client.key(DatastoreRecommendationRepository.CONTENT_KIND)
        entity = datastore.Entity(key=key)
        entity.update(content.to_dict())
        client.put(entity)

    @staticmethod
    def list_active_contents():
        query = client.query(kind=DatastoreRecommendationRepository.CONTENT_KIND)
        query.add_filter(filter=PropertyFilter("active", "=", True))

        return list(query.fetch())

    @staticmethod
    def save_history(history):
        key = client.key(DatastoreRecommendationRepository.HISTORY_KIND)

        entity = datastore.Entity(key=key)
        entity.update(history)

        client.put(entity)
    
    @staticmethod
    def list_recent_history(days):
        query = client.query(kind=DatastoreRecommendationRepository.HISTORY_KIND)
        results = list(query.fetch())

        cutoff = datetime.utcnow() - timedelta(days=days)

        return [
            result for result in results
            if result.get("sent_at") and result["sent_at"] >= cutoff
        ]