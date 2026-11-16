from google.cloud import datastore
from domain.repositories.claude_budget_repository import ClaudeBudgetRepository
from infrastructure.datastore.client import client


class DatastoreClaudeBudgetRepository(ClaudeBudgetRepository):

    KIND = "ClaudeDailyBudget"
    COUNT_PROPERTY = "call_count"

    def get_call_count(self, day_key):
        entity = client.get(client.key(self.KIND, day_key))
        if entity is None:
            return 0
        return int(entity.get(self.COUNT_PROPERTY, 0) or 0)

    def increment_call_count(self, day_key):
        key = client.key(self.KIND, day_key)
        entity = client.get(key)
        if entity is None:
            entity = datastore.Entity(key=key)
            entity[self.COUNT_PROPERTY] = 0
        current = int(entity.get(self.COUNT_PROPERTY, 0) or 0)
        new_count = current + 1
        entity[self.COUNT_PROPERTY] = new_count
        client.put(entity)
        return new_count
