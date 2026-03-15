from datetime import datetime

class RecommendationService:

    def __init__(self, repository, whatsapp):
        self.repository = repository
        self.whatsapp = whatsapp

    def send_daily_recommendations(self):

        customers = self.repository.list_active()

        for customer in customers:

            message = "🍷 Vinho do dia: Experimente um Malbec argentino com carnes grelhadas."

            self.whatsapp.send_text(customer["phone"], message)