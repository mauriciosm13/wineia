from datetime import datetime


class PreSaleCustomer:

    def __init__(
        self,
        name,
        email,
        whatsapp,
        preferences,
        privacy_terms_version=None,
        privacy_terms_accepted_at=None,
    ):
        self.name = name
        self.email = email
        self.whatsapp = whatsapp
        self.preferences = preferences
        self.created_at = datetime.utcnow()
        self.privacy_terms_version = privacy_terms_version
        self.privacy_terms_accepted_at = privacy_terms_accepted_at

    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "whatsapp": self.whatsapp,
            "preferences": self.preferences,
            "created_at": self.created_at,
            "privacy_terms_version": self.privacy_terms_version,
            "privacy_terms_accepted_at": self.privacy_terms_accepted_at,
        }
