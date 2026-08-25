from datetime import datetime


class PreSaleCustomer:

    def __init__(self, name, email, whatsapp, preferences):
        self.name = name
        self.email = email
        self.whatsapp = whatsapp
        self.preferences = preferences
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "whatsapp": self.whatsapp,
            "preferences": self.preferences,
            "created_at": self.created_at,
        }
