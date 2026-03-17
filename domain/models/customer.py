from datetime import datetime


class CustomerStatus:
    active = "active"
    canceled = "canceled"


class Customer:

    def __init__(self, phone, name=None, status=None, plan=None):
        self.phone = phone
        self.name = name
        self.status = status
        self.plan = plan
        self.created_at = datetime.utcnow()
        self.last_message_at = None
        self.last_recommendation_at = None
        self.messages_sent_today = 0
        self.daily_reset = None

    def to_dict(self):
        return {
            "phone": self.phone,
            "name": self.name,
            "plan": self.plan,
            "status": self.status,
            "created_at": self.created_at,
            "last_message_at": self.last_message_at,
            "last_recommendation_at": self.last_recommendation_at,
            "messages_sent_today": self.messages_sent_today,
            "daily_reset": self.daily_reset,
        }