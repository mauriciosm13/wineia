import random
from infrastructure.repositories.datastore_recommendation_repository import DatastoreRecommendationRepository

def select_wine(days_block=7):
    contents = DatastoreRecommendationRepository.list_active_contents()
    recents = DatastoreRecommendationRepository.list_recent_history(days=days_block)

    already_sent = {recent["wine_name"] for recent in recents}

    available = [
        wine for wine in contents
        if wine["name"] not in already_sent
    ]

    if not available:
        available = contents

    return random.choice(available)