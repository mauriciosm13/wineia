from unittest.mock import MagicMock, patch

import pytest

from infrastructure.external import twilio_whatsapp_client as twilio_mod


def test_get_configuration_prefers_env_over_file(monkeypatch):
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "ACenv")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "token-env")
    monkeypatch.setenv("TWILIO_WHATSAPP_FROM", "+5511999999999")
    monkeypatch.setattr(
        twilio_mod,
        "load_config",
        lambda: {"account_sid": "ACfile", "auth_token": "token-file", "numberTwillio": "5511888888888"},
    )

    config = twilio_mod._get_configuration()

    assert config["account_sid"] == "ACenv"
    assert config["auth_token"] == "token-env"
    assert config["whatsapp_from"] == "+5511999999999"


def test_get_configuration_falls_back_to_config_json(monkeypatch):
    monkeypatch.delenv("TWILIO_ACCOUNT_SID", raising=False)
    monkeypatch.delenv("TWILIO_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("TWILIO_WHATSAPP_FROM", raising=False)
    monkeypatch.setattr(
        twilio_mod,
        "load_config",
        lambda: {"account_sid": "ACfile", "auth_token": "token-file", "numberTwillio": "5511888888888"},
    )

    config = twilio_mod._get_configuration()

    assert config["account_sid"] == "ACfile"
    assert config["auth_token"] == "token-file"
    assert config["whatsapp_from"] == "5511888888888"


def test_send_text_uses_env_without_config_json(monkeypatch):
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "ACenv")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "token-env")
    monkeypatch.setenv("TWILIO_WHATSAPP_FROM", "+5511999999999")
    monkeypatch.setattr(twilio_mod, "load_config", lambda: {})

    fake_client = MagicMock()
    fake_client.messages.create.return_value = MagicMock(sid="SMxxx")

    with patch.object(twilio_mod, "Client", return_value=fake_client) as client_cls:
        result = twilio_mod.send_text("+5511888777666", "ola")

    client_cls.assert_called_once_with("ACenv", "token-env")
    fake_client.messages.create.assert_called_once_with(
        from_="whatsapp:+5511999999999",
        body="ola",
        to="whatsapp:+5511888777666",
    )
    assert result.sid == "SMxxx"


def test_send_text_raises_when_env_and_file_missing(monkeypatch):
    monkeypatch.delenv("TWILIO_ACCOUNT_SID", raising=False)
    monkeypatch.delenv("TWILIO_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("TWILIO_WHATSAPP_FROM", raising=False)
    monkeypatch.setattr(twilio_mod, "load_config", lambda: {})

    with pytest.raises(twilio_mod.TwilioAPIError, match="TWILIO_ACCOUNT_SID"):
        twilio_mod.send_text("+5511888777666", "ola")


def test_format_whatsapp_number_variants():
    assert twilio_mod._format_whatsapp_number("whatsapp:+5511") == "whatsapp:+5511"
    assert twilio_mod._format_whatsapp_number("+5511") == "whatsapp:+5511"
    assert twilio_mod._format_whatsapp_number("5511") == "whatsapp:+5511"
