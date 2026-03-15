import os
import requests

class WhatsAppClient:

    def __init__(self):
        self.token = os.getenv("WHATSAPP_TOKEN")
        self.phone_id = os.getenv("WHATSAPP_PHONE_ID")

    def send_text(self, phone, message):

        url = f"https://graph.facebook.com/v19.0/{self.phone_id}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "text",
            "text": {"body": message}
        }

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        requests.post(url, json=payload, headers=headers)