import os
import requests
from core.utils.load_config import load_config
from base64 import b64encode
from core.config import TWILIO_TIMEOUT
from types import SimpleNamespace
from twilio.rest import Client


class TwilioAPIError(Exception):
    pass


def create_twilio_whatsapp_client():
    return SimpleNamespace(send_text=send_text)


def send_text(phone, message):
    config = load_config()
    account_sid = config["account_sid"]
    auth_token = config["auth_token"]
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_=f'whatsapp:+{config["numberTwillio"]}',
        body=message,
        to=f'whatsapp:+{phone}'
    )

    return message


def _get_configuration():
    config = load_config()
    return {
        "account_sid": config["account_sid"],
        "auth_token": config["auth_token"],
        "whatsapp_from": os.getenv("TWILIO_WHATSAPP_FROM"),
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

    return f"whatsapp:{normalized_phone}"
