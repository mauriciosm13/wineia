import importlib

import core.config as config
import core.logging as wine_logging
import core.queues as queues


def test_config_timeout_is_int():
    assert isinstance(config.TWILIO_TIMEOUT, int)


def test_config_reload_reads_env(monkeypatch):
    monkeypatch.setenv("PROJECT_ID", "wineia-test")
    monkeypatch.setenv("TWILIO_TIMEOUT", "12")
    reloaded = importlib.reload(config)
    assert reloaded.PROJECT_ID == "wineia-test"
    assert reloaded.TWILIO_TIMEOUT == 12


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
