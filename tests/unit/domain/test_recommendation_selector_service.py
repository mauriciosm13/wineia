from domain.services.recommendation_selector_service import choose_wine, select_wine


class FirstItemRng:
    def choice(self, seq):
        return seq[0]


def test_choose_wine_prefers_never_sent():
    contents = [
        {"name": "A", "last_sent": "2026-01-01"},
        {"name": "B", "last_sent": None},
    ]
    chosen = choose_wine(contents, recents=[], rng=FirstItemRng())
    assert chosen["name"] == "B"


def test_choose_wine_skips_recent_history():
    contents = [
        {"name": "A", "last_sent": "2026-01-02"},
        {"name": "B", "last_sent": "2026-01-01"},
    ]
    chosen = choose_wine(contents, recents=[{"wine_name": "A"}])
    assert chosen["name"] == "B"


def test_choose_wine_falls_back_when_all_recent():
    contents = [
        {"name": "A", "last_sent": "2026-01-02"},
        {"name": "B", "last_sent": "2026-01-01"},
    ]
    chosen = choose_wine(
        contents,
        recents=[{"wine_name": "A"}, {"wine_name": "B"}],
    )
    assert chosen["name"] == "B"


def test_choose_wine_empty_catalog_returns_none():
    assert choose_wine([], recents=[]) is None


def test_select_wine_uses_repository(monkeypatch):
    contents = [{"name": "Solo", "last_sent": None}]
    recents = []

    class FakeRepo:
        @staticmethod
        def list_active_contents():
            return contents

        @staticmethod
        def list_recent_history(days):
            assert days == 7
            return recents

    monkeypatch.setattr(
        "infrastructure.repositories.datastore_recommendation_repository.DatastoreRecommendationRepository",
        FakeRepo,
    )

    assert select_wine()["name"] == "Solo"
