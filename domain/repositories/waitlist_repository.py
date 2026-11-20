from abc import ABC, abstractmethod


class WaitlistRepository(ABC):

    @abstractmethod
    def get_by_phone(self, phone):
        pass

    @abstractmethod
    def save(self, lead):
        pass

    @abstractmethod
    def update(self, lead):
        pass

    @abstractmethod
    def list_all(self):
        pass
