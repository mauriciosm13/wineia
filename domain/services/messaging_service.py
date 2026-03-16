from datetime import datetime


class MessagingService:

    DAILY_LIMIT = 2

    def process_incoming_message(self, phone, message):

        customer = self.repository.get_by_phone(phone)

        if not customer:
            return

        if message.lower() == "cancelar":
            customer["status"] = "CANCELED"
            self.repository.update(customer)
            return

        if not self.can_send_message(customer):
            self.whatsapp.send_text(
                phone,
                "Você atingiu o limite diário de mensagens gratuitas. "
                "Tente novamente amanhã ou atualize seu plano."
            )
            return

        resposta = self.ia_service.generea(customer, message)

        self.whatsapp.send_text(phone, resposta)

        customer["messages_sent_today"] = customer.get("messages_sent_today", 0) + 1
        customer["last_message_at"] = datetime.utcnow().isoformat()
        self.repository.update(customer)

    def can_send_message(self, customer):

        if customer["status"] != "ACTIVE":
            return False

        if customer.get("messages_sent_today", 0) >= self.DAILY_LIMIT:
            return False

        return True