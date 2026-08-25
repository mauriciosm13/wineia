from google.cloud import datastore
from google.cloud.datastore.query import PropertyFilter
from infrastructure.datastore.client import client
from domain.repositories.pre_sale_customer_repository import PreSaleCustomerRepository


class DatastorePreSaleCustomerRepository(PreSaleCustomerRepository):

    KIND = "PreSaleCustomer"

    @staticmethod
    def save(customer):
        key = client.key(DatastorePreSaleCustomerRepository.KIND, customer.email)
        entity = datastore.Entity(key=key)

        entity.update(customer.to_dict())

        client.put(entity)

    @staticmethod
    def get_by_email(email):
        query = client.query(kind=DatastorePreSaleCustomerRepository.KIND)
        query.add_filter(filter=PropertyFilter("email", "=", email))

        return next(query.fetch(), None)
