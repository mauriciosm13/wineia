from datetime import datetime


class RecommendationHistory:

    def __init__(self, phone, wine_name):
        self.phone = phone
        self.wine_name = wine_name
        self.sent_at = datetime.utcnow()

    def to_dict(self):
        return {
            "phone": self.phone,
            "wine_name": self.wine_name,
            "sent_at": self.sent_at,
        }
