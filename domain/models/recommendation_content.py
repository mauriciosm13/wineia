from datetime import datetime


class RecommendationContent:

    def __init__(self, name, grape=None, country=None, price=None, description=None, winery=None):
        self.name = name
        self.grape = grape
        self.country = country
        self.price = price
        self.description = description
        self.winery = winery
        self.active = True
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "name": self.name,
            "grape": self.grape,
            "country": self.country,
            "price": self.price,
            "description": self.description,
            "winery": self.winery,
            "active": self.active,
            "created_at": self.created_at,
        }
