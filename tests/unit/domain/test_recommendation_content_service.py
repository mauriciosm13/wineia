from domain.services.recommendation_content_service import RecommendationContentService
from tests.fakes.repositories import FakeRecommendationContentRepository


def test_create_content_saves_and_returns_dict():
    repo = FakeRecommendationContentRepository()
    service = RecommendationContentService(repo)

    result = service.create_content(
        name="Reserva Malbec",
        grape="Malbec",
        winery="Trapiche",
        country="Argentina",
        price=89.90,
        description="Encorpado",
    )

    assert repo.save_content_calls == 1
    saved = repo.saved[0]
    assert saved.name == "Reserva Malbec"
    assert saved.grape == "Malbec"
    assert saved.winery == "Trapiche"

    expected_keys = {
        "name",
        "grape",
        "country",
        "price",
        "description",
        "winery",
        "active",
        "created_at",
        "last_sent",
    }
    assert set(result.keys()) == expected_keys
    assert result["name"] == "Reserva Malbec"
    assert result["active"] is True
