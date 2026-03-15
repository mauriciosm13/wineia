from google.cloud import datastore
from infrastructure.datastore.client import client
from domain.repositories.customer_repository import CustomerRepository

class DatastoreCustomerRepository(CustomerRepository):

    KIND = "Customer"

    def save(self, customer):

        key = client.key(self.KIND, customer.phone)
        entity = datastore.Entity(key=key)

        entity.update(customer.to_dict())

        client.put(entity)

    def update(self, customer):

        key = client.key(self.KIND, customer["phone"])
        entity = datastore.Entity(key=key)

        entity.update(customer)

        client.put(entity)

    def get_by_phone(self, phone):

        key = client.key(self.KIND, phone)
        entity = client.get(key)

        if not entity:
            return None

        return dict(entity)

    def list_active(self):

        query = client.query(kind=self.KIND)
        query.add_filter("status", "=", "ACTIVE")

        return list(query.fetch())