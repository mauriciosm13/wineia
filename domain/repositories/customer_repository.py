from abc import ABC, abstractmethod

class CustomerRepository(ABC):

    @abstractmethod
    def save(self, customer):
        pass

    @abstractmethod
    def get_by_phone(self, phone):
        pass

    @abstractmethod
    def update(self, customer):
        pass

    @abstractmethod
    def list_active(self):
        pass

    @abstractmethod
    def list_all(self):
        pass
