from datetime import datetime

class MessagingService:

    DAILY_LIMIT = 2

    def __init__(self, repository, whatsapp):
        self.repository = repository
        self.whatsapp = whatsapp

    def process_incoming_message(self, phone, message):

        customer = self.repository.get_by_phone(phone)

        if not customer:
            return

        if message.lower() == "cancelar":
            customer["status"] = "CANCELED"
            self.repository.update(customer)
            return

    def can_send_message(self, customer):

        if customer["status"] != "ACTIVE":
            return False

        if customer["messages_sent_today"] >= self.DAILY_LIMIT:
            return False

        return True