from google.cloud import datastore
from google.cloud.datastore.query import PropertyFilter
from infrastructure.datastore.client import client
from domain.models.customer import CustomerStatus
from domain.repositories.customer_repository import CustomerRepository

class DatastoreCustomerRepository(CustomerRepository):

    KIND = "Customer"

    @staticmethod
    def save(customer):
        key = client.key(DatastoreCustomerRepository.KIND, customer.phone)
        entity = datastore.Entity(key=key)

        entity.update(customer.to_dict())

        client.put(entity)

    @staticmethod
    def update(customer):
        key = client.key(DatastoreCustomerRepository.KIND, customer["phone"])
        entity = datastore.Entity(key=key)

        entity.update(customer)

        client.put(entity)

    @staticmethod
    def get_by_key(key):
        return client.get(key)

    @staticmethod
    def list_active():
        query = client.query(kind=DatastoreCustomerRepository.KIND)
        query.add_filter(filter=PropertyFilter("status", "=", CustomerStatus.active))

        return list(query.fetch())
    
    @staticmethod
    def get_by_phone(phone):
        query = client.query(kind=DatastoreCustomerRepository.KIND)
        query.add_filter(filter=PropertyFilter("phone", "=", phone))

        return next(query.fetch(), None)
