import importlib

import core.config as config
import core.logging as wine_logging
import core.queues as queues
import pytest


@pytest.fixture(autouse=True)
def _restore_on_demand_limit_defaults(monkeypatch):
    monkeypatch.delenv("ON_DEMAND_DAILY_LIMIT_ENTRY", raising=False)
    monkeypatch.delenv("ON_DEMAND_DAILY_LIMIT_SUPERIOR", raising=False)
    importlib.reload(config)
    yield
    monkeypatch.delenv("ON_DEMAND_DAILY_LIMIT_ENTRY", raising=False)
    monkeypatch.delenv("ON_DEMAND_DAILY_LIMIT_SUPERIOR", raising=False)
    importlib.reload(config)


def test_config_timeout_is_int():
    assert isinstance(config.TWILIO_TIMEOUT, int)


def test_config_reload_reads_env(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "wineia-test")
    monkeypatch.setenv("TWILIO_TIMEOUT", "12")
    reloaded = importlib.reload(config)
    assert reloaded.PROJECT_ID == "wineia-test"
    assert reloaded.TWILIO_TIMEOUT == 12


def test_on_demand_daily_limits_default_when_unset(monkeypatch):
    monkeypatch.delenv("ON_DEMAND_DAILY_LIMIT_ENTRY", raising=False)
    monkeypatch.delenv("ON_DEMAND_DAILY_LIMIT_SUPERIOR", raising=False)
    reloaded = importlib.reload(config)
    assert reloaded.ON_DEMAND_DAILY_LIMIT_ENTRY == 2
    assert reloaded.ON_DEMAND_DAILY_LIMIT_SUPERIOR == 10


def test_on_demand_daily_limits_env_override(monkeypatch):
    monkeypatch.setenv("ON_DEMAND_DAILY_LIMIT_ENTRY", "5")
    monkeypatch.setenv("ON_DEMAND_DAILY_LIMIT_SUPERIOR", "20")
    reloaded = importlib.reload(config)
    assert reloaded.ON_DEMAND_DAILY_LIMIT_ENTRY == 5
    assert reloaded.ON_DEMAND_DAILY_LIMIT_SUPERIOR == 20


def test_on_demand_daily_limits_zero_allowed(monkeypatch):
    monkeypatch.setenv("ON_DEMAND_DAILY_LIMIT_ENTRY", "0")
    monkeypatch.setenv("ON_DEMAND_DAILY_LIMIT_SUPERIOR", "0")
    reloaded = importlib.reload(config)
    assert reloaded.ON_DEMAND_DAILY_LIMIT_ENTRY == 0
    assert reloaded.ON_DEMAND_DAILY_LIMIT_SUPERIOR == 0


def test_on_demand_daily_limits_invalid_fall_back(monkeypatch):
    monkeypatch.setenv("ON_DEMAND_DAILY_LIMIT_ENTRY", "abc")
    monkeypatch.setenv("ON_DEMAND_DAILY_LIMIT_SUPERIOR", "-3")
    reloaded = importlib.reload(config)
    assert reloaded.ON_DEMAND_DAILY_LIMIT_ENTRY == 2
    assert reloaded.ON_DEMAND_DAILY_LIMIT_SUPERIOR == 10
    monkeypatch.setenv("ON_DEMAND_DAILY_LIMIT_ENTRY", "  ")
    monkeypatch.setenv("ON_DEMAND_DAILY_LIMIT_SUPERIOR", "")
    reloaded = importlib.reload(config)
    assert reloaded.ON_DEMAND_DAILY_LIMIT_ENTRY == 2
    assert reloaded.ON_DEMAND_DAILY_LIMIT_SUPERIOR == 10


def test_logger_name():
    assert wine_logging.logger.name == "wine-concierge"


def test_queue_catalog():
    assert queues.QUEUE_REGION == "southamerica-east1" or queues.QUEUE_REGION
    assert queues.QUEUES["send_message"]["worker_path"] == "/workers/send-message"
    assert queues.QUEUES["send_campaign"]["name"] == "wine-campaigns"


def test_queues_reload_reads_region(monkeypatch):
    monkeypatch.setenv("QUEUE_REGION", "us-east1")
    reloaded = importlib.reload(queues)
    assert reloaded.QUEUE_REGION == "us-east1"
