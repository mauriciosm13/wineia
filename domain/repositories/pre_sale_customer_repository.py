from abc import ABC, abstractmethod


class PreSaleCustomerRepository(ABC):

    @abstractmethod
    def save(self, customer):
        pass

    @abstractmethod
    def get_by_email(self, email):
        pass
