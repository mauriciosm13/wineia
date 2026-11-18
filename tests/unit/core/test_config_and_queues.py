import importlib

import core.config as config
import core.queues as queues
import pytest


@pytest.fixture(autouse=True)
def _restore_on_demand_limit_defaults(monkeypatch):
    monkeypatch.delenv("ON_DEMAND_DAILY_LIMIT_ENTRY", raising=False)
    monkeypatch.delenv("ON_DEMAND_DAILY_LIMIT_SUPERIOR", raising=False)
    monkeypatch.delenv("CLAUDE_DAILY_CALL_BUDGET", raising=False)
    monkeypatch.delenv("PRIVACY_POLICY_URL", raising=False)
    monkeypatch.delenv("TERMS_OF_SERVICE_URL", raising=False)
    importlib.reload(config)
    yield
    monkeypatch.delenv("ON_DEMAND_DAILY_LIMIT_ENTRY", raising=False)
    monkeypatch.delenv("ON_DEMAND_DAILY_LIMIT_SUPERIOR", raising=False)
    monkeypatch.delenv("CLAUDE_DAILY_CALL_BUDGET", raising=False)
    monkeypatch.delenv("PRIVACY_POLICY_URL", raising=False)
    monkeypatch.delenv("TERMS_OF_SERVICE_URL", raising=False)
    importlib.reload(config)


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


def test_claude_daily_call_budget_default_unlimited(monkeypatch):
    monkeypatch.delenv("CLAUDE_DAILY_CALL_BUDGET", raising=False)
    reloaded = importlib.reload(config)
    assert reloaded.CLAUDE_DAILY_CALL_BUDGET == 0


def test_claude_daily_call_budget_env_override(monkeypatch):
    monkeypatch.setenv("CLAUDE_DAILY_CALL_BUDGET", "100")
    reloaded = importlib.reload(config)
    assert reloaded.CLAUDE_DAILY_CALL_BUDGET == 100


def test_claude_daily_call_budget_zero_allowed(monkeypatch):
    monkeypatch.setenv("CLAUDE_DAILY_CALL_BUDGET", "0")
    reloaded = importlib.reload(config)
    assert reloaded.CLAUDE_DAILY_CALL_BUDGET == 0


def test_claude_daily_call_budget_invalid_fall_back(monkeypatch):
    monkeypatch.setenv("CLAUDE_DAILY_CALL_BUDGET", "abc")
    reloaded = importlib.reload(config)
    assert reloaded.CLAUDE_DAILY_CALL_BUDGET == 0
    monkeypatch.setenv("CLAUDE_DAILY_CALL_BUDGET", "-5")
    reloaded = importlib.reload(config)
    assert reloaded.CLAUDE_DAILY_CALL_BUDGET == 0
    monkeypatch.setenv("CLAUDE_DAILY_CALL_BUDGET", "  ")
    reloaded = importlib.reload(config)
    assert reloaded.CLAUDE_DAILY_CALL_BUDGET == 0




def test_privacy_terms_urls_default_placeholders(monkeypatch):
    monkeypatch.delenv("PRIVACY_POLICY_URL", raising=False)
    monkeypatch.delenv("TERMS_OF_SERVICE_URL", raising=False)
    reloaded = importlib.reload(config)
    assert reloaded.PRIVACY_POLICY_URL == "https://example.com/privacy"
    assert reloaded.TERMS_OF_SERVICE_URL == "https://example.com/terms"


def test_privacy_terms_urls_env_override(monkeypatch):
    monkeypatch.setenv("PRIVACY_POLICY_URL", "https://wineia.app/privacy")
    monkeypatch.setenv("TERMS_OF_SERVICE_URL", "https://wineia.app/terms")
    reloaded = importlib.reload(config)
    assert reloaded.PRIVACY_POLICY_URL == "https://wineia.app/privacy"
    assert reloaded.TERMS_OF_SERVICE_URL == "https://wineia.app/terms"


def test_privacy_terms_urls_whitespace_falls_back(monkeypatch):
    monkeypatch.setenv("PRIVACY_POLICY_URL", "  ")
    monkeypatch.setenv("TERMS_OF_SERVICE_URL", "")
    reloaded = importlib.reload(config)
    assert reloaded.PRIVACY_POLICY_URL == "https://example.com/privacy"
    assert reloaded.TERMS_OF_SERVICE_URL == "https://example.com/terms"


def test_queue_worker_paths_match_routes():
    assert queues.QUEUES["send_message"]["worker_path"] == "/workers/send-message"
    assert queues.QUEUES["send_campaign"]["worker_path"] == "/workers/send-campaign"
    assert queues.QUEUES["send_campaign"]["name"] == "wine-campaigns"


def test_queues_reload_reads_region(monkeypatch):
    monkeypatch.setenv("QUEUE_REGION", "us-east1")
    reloaded = importlib.reload(queues)
    assert reloaded.QUEUE_REGION == "us-east1"
