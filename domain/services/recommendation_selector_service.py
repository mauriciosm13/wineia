import random


def choose_wine(contents, recents, rng=None):
    if rng is None:
        rng = random

    already_sent = {recent["wine_name"] for recent in recents}

    available = [wine for wine in contents if wine["name"] not in already_sent]

    if not available:
        available = list(contents)

    if not available:
        return None

    never_sent = [w for w in available if not w.get("last_sent")]
    if never_sent:
        return rng.choice(never_sent)
    return min(available, key=lambda w: w["last_sent"])


def select_wine(days_block=7):
    from infrastructure.repositories.datastore_recommendation_repository import DatastoreRecommendationRepository

    contents = DatastoreRecommendationRepository.list_active_contents()
    recents = DatastoreRecommendationRepository.list_recent_history(days=days_block)
    return choose_wine(contents, recents)
