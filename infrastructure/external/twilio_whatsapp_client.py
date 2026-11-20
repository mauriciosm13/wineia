import os
from base64 import b64encode
from types import SimpleNamespace

from twilio.rest import Client

from core.config import TWILIO_TIMEOUT
from core.utils.load_config import load_config


class TwilioAPIError(Exception):
    pass


def create_twilio_whatsapp_client():
    return SimpleNamespace(send_text=send_text)


def send_text(phone, message):
    configuration = _get_configuration()
    _validate_configuration(configuration)

    client = Client(configuration["account_sid"], configuration["auth_token"])
    return client.messages.create(
        from_=_format_whatsapp_number(configuration["whatsapp_from"]),
        body=message,
        to=_format_whatsapp_number(phone),
    )


def _get_configuration():
    file_config = load_config()
    account_sid = (os.getenv("TWILIO_ACCOUNT_SID") or file_config.get("account_sid") or "").strip()
    auth_token = (os.getenv("TWILIO_AUTH_TOKEN") or file_config.get("auth_token") or "").strip()
    whatsapp_from = (
        os.getenv("TWILIO_WHATSAPP_FROM")
        or file_config.get("numberTwillio")
        or file_config.get("TWILIO_WHATSAPP_FROM")
        or ""
    )
    whatsapp_from = str(whatsapp_from).strip()

    return {
        "account_sid": account_sid,
        "auth_token": auth_token,
        "whatsapp_from": whatsapp_from,
        "timeout": int(os.getenv("TWILIO_TIMEOUT", str(TWILIO_TIMEOUT))),
    }


def _validate_configuration(configuration):
    if not configuration["account_sid"]:
        raise TwilioAPIError("TWILIO_ACCOUNT_SID nao configurado.")

    if not configuration["auth_token"]:
        raise TwilioAPIError("TWILIO_AUTH_TOKEN nao configurado.")

    if not configuration["whatsapp_from"]:
        raise TwilioAPIError("TWILIO_WHATSAPP_FROM nao configurado.")


def _build_messages_url(configuration):
    return (
        "https://api.twilio.com/2010-04-01/Accounts/"
        f"{configuration['account_sid']}/Messages.json"
    )


def _build_headers(configuration):
    auth_value = (
        f"{configuration['account_sid']}:{configuration['auth_token']}".encode("utf-8")
    )
    encoded_auth = b64encode(auth_value).decode("utf-8")

    return {
        "Authorization": f"Basic {encoded_auth}",
    }


def _format_whatsapp_number(phone):
    normalized_phone = str(phone or "").strip()

    if normalized_phone.startswith("whatsapp:"):
        return normalized_phone

    if normalized_phone.startswith("+"):
        return f"whatsapp:{normalized_phone}"

    return f"whatsapp:+{normalized_phone}"
