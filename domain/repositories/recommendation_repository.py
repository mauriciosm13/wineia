from abc import ABC, abstractmethod


class RecommendationRepository(ABC):

    @abstractmethod
    def save_content(self, content):
        pass

    @abstractmethod
    def list_active_contents(self):
        pass

    @abstractmethod
    def save_history(self, history):
        pass

    @abstractmethod
    def list_recent_history(self, phone, days):
        pass