import json

from core.utils.twilio_webhook_parser import extract_inbound_media, extract_message, extract_phone, get_first_value, has_inbound_media, parse_webhook_body


def test_parse_json_body():
    payload = parse_webhook_body(json.dumps({"Body": ["oi"]}), "application/json")
    assert payload == {"Body": ["oi"]}


def test_parse_empty_json_body():
    assert parse_webhook_body(None, "application/json") == {}


def test_parse_form_body():
    payload = parse_webhook_body("Body=hello&WaId=5511999")
    assert payload["Body"] == ["hello"]
    assert payload["WaId"] == ["5511999"]


def test_extract_phone_from_waid():
    assert extract_phone({"WaId": ["5511999"], "From": ["whatsapp:+5511000"]}) == "5511999"


def test_extract_phone_from_whatsapp_from():
    assert extract_phone({"WaId": [], "From": ["whatsapp:+5511888"]}) == "+5511888"


def test_extract_phone_plain_from():
    assert extract_phone({"From": ["+5511777"]}) == "+5511777"


def test_extract_phone_missing():
    assert extract_phone({}) is None


def test_extract_message():
    assert extract_message({"Body": ["quero vinho"]}) == "quero vinho"


def test_extract_inbound_media_when_present():
    media = extract_inbound_media(
        {
            "NumMedia": ["1"],
            "MediaUrl0": ["https://api.twilio.com/media/abc"],
            "MediaContentType0": ["image/jpeg"],
        }
    )
    assert media == {
        "num_media": 1,
        "url": "https://api.twilio.com/media/abc",
        "content_type": "image/jpeg",
    }
    assert has_inbound_media(media) is True


def test_extract_inbound_media_when_zero_or_missing():
    assert extract_inbound_media({"NumMedia": ["0"]}) is None
    assert extract_inbound_media({}) is None
    assert extract_inbound_media({"NumMedia": ["abc"]}) is None
    assert has_inbound_media(None) is False
    assert has_inbound_media({"num_media": 0}) is False
    assert has_inbound_media({"num_media": "x"}) is False


def test_get_first_value_empty():
    assert get_first_value({"Body": []}, "Body") is None
    assert get_first_value({}, "Body") is None
