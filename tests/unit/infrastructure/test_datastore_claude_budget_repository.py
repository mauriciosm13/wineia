from unittest.mock import MagicMock

import infrastructure.repositories.datastore_claude_budget_repository as module
from infrastructure.repositories.datastore_claude_budget_repository import DatastoreClaudeBudgetRepository


class _FakeEntity(dict):
    def __init__(self, key=None, **kwargs):
        super().__init__(**kwargs)
        self.key = key


def test_get_call_count_returns_zero_when_missing(monkeypatch):
    client = MagicMock()
    client.key.return_value = "key-2026-11-16"
    client.get.return_value = None
    monkeypatch.setattr(module, "client", client)
    monkeypatch.setattr(module, "datastore", MagicMock())

    repo = DatastoreClaudeBudgetRepository()
    assert repo.get_call_count("2026-11-16") == 0
    client.key.assert_called_once_with(DatastoreClaudeBudgetRepository.KIND, "2026-11-16")


def test_get_call_count_reads_property(monkeypatch):
    client = MagicMock()
    client.key.return_value = "key"
    client.get.return_value = _FakeEntity(call_count=3)
    monkeypatch.setattr(module, "client", client)

    repo = DatastoreClaudeBudgetRepository()
    assert repo.get_call_count("2026-11-16") == 3


def test_increment_call_count_creates_entity(monkeypatch):
    client = MagicMock()
    key = object()
    client.key.return_value = key
    client.get.return_value = None
    fake_datastore = MagicMock()
    entity = _FakeEntity(key=key)
    fake_datastore.Entity.return_value = entity
    monkeypatch.setattr(module, "client", client)
    monkeypatch.setattr(module, "datastore", fake_datastore)

    repo = DatastoreClaudeBudgetRepository()
    assert repo.increment_call_count("2026-11-16") == 1
    assert entity["call_count"] == 1
    client.put.assert_called_once_with(entity)


def test_increment_call_count_updates_existing(monkeypatch):
    client = MagicMock()
    key = object()
    client.key.return_value = key
    entity = _FakeEntity(key=key, call_count=4)
    client.get.return_value = entity
    monkeypatch.setattr(module, "client", client)
    monkeypatch.setattr(module, "datastore", MagicMock())

    repo = DatastoreClaudeBudgetRepository()
    assert repo.increment_call_count("2026-11-16") == 5
    assert entity["call_count"] == 5
    client.put.assert_called_once_with(entity)
