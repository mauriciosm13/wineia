from google.cloud import datastore
from infrastructure.datastore.client import client
from domain.repositories.waitlist_repository import WaitlistRepository


class DatastoreWaitlistRepository(WaitlistRepository):

    KIND = "WaitlistLead"

    @staticmethod
    def _entity_to_dict(entity):
        if entity is None:
            return None
        return dict(entity)

    @staticmethod
    def get_by_phone(phone):
        key = client.key(DatastoreWaitlistRepository.KIND, phone)
        return DatastoreWaitlistRepository._entity_to_dict(client.get(key))

    @staticmethod
    def save(lead):
        payload = lead.to_dict() if hasattr(lead, "to_dict") else dict(lead)
        key = client.key(DatastoreWaitlistRepository.KIND, payload["phone"])
        entity = datastore.Entity(key=key)
        entity.update(payload)
        client.put(entity)

    @staticmethod
    def update(lead):
        payload = lead.to_dict() if hasattr(lead, "to_dict") else dict(lead)
        key = client.key(DatastoreWaitlistRepository.KIND, payload["phone"])
        entity = datastore.Entity(key=key)
        entity.update(payload)
        client.put(entity)

    @staticmethod
    def list_all():
        query = client.query(kind=DatastoreWaitlistRepository.KIND)
        return [DatastoreWaitlistRepository._entity_to_dict(entity) for entity in query.fetch()]
