import json

from core.utils.twilio_webhook_parser import extract_message, extract_phone, get_first_value, parse_webhook_body


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


def test_get_first_value_empty():
    assert get_first_value({"Body": []}, "Body") is None
    assert get_first_value({}, "Body") is None
