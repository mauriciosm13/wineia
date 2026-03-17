from domain.models.recommendation_content import RecommendationContent


class RecommendationContentService:

    def __init__(self, repository):
        self.repository = repository

    def create_content(self, name, grape=None, winery=None, country=None, price=None, description=None):
        content = RecommendationContent(
            name=name,
            grape=grape,
            winery=winery,
            country=country,
            price=price,
            description=description,
        )
        self.repository.save_content(content)
        return content.to_dict()
