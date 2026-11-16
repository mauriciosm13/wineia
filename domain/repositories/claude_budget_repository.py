from abc import ABC, abstractmethod


class ClaudeBudgetRepository(ABC):

    @abstractmethod
    def get_call_count(self, day_key):
        pass

    @abstractmethod
    def increment_call_count(self, day_key):
        pass
