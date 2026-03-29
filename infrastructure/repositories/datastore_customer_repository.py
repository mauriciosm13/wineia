from google.cloud import datastore
from google.cloud.datastore.query import PropertyFilter
from infrastructure.datastore.client import client
from domain.models.customer import CustomerStatus
from domain.repositories.customer_repository import CustomerRepository

class DatastoreCustomerRepository(CustomerRepository):

    KIND = "Customer"

    def save(customer):
        key = client.key(DatastoreCustomerRepository.KIND, customer.phone)
        entity = datastore.Entity(key=key)

        entity.update(customer.to_dict())

        client.put(entity)

    def update(customer):
        key = client.key(DatastoreCustomerRepository.KIND, customer["phone"])
        entity = datastore.Entity(key=key)

        entity.update(customer)

        client.put(entity)

    def get_by_phone(phone):
        key = client.key(DatastoreCustomerRepository.KIND, phone)
        entity = client.get(key)

        if not entity:
            return None

        return dict(entity)

    def list_active():
        query = client.query(kind=DatastoreCustomerRepository.KIND)
        query.add_filter(filter=PropertyFilter("status", "=", CustomerStatus.active))

        return list(query.fetch())