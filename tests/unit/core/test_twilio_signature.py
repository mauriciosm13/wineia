from core.utils.twilio_signature import form_params_from_body, public_request_url, signature_is_valid


def test_public_request_url_uses_forwarded_proto():
    environ = {
        "HTTP_X_FORWARDED_PROTO": "https,http",
        "HTTP_HOST": "example.com",
        "PATH_INFO": "/webhook/whatsapp",
        "wsgi.url_scheme": "http",
    }
    assert public_request_url(environ) == "https://example.com/webhook/whatsapp"


def test_public_request_url_includes_query_string():
    environ = {
        "HTTP_HOST": "example.com",
        "PATH_INFO": "/webhook/whatsapp",
        "QUERY_STRING": "bodySHA256=abc123",
        "wsgi.url_scheme": "https",
    }
    assert public_request_url(environ) == "https://example.com/webhook/whatsapp?bodySHA256=abc123"


def test_public_request_url_defaults_scheme_to_https():
    environ = {
        "HTTP_HOST": "example.com",
        "PATH_INFO": "/webhook/whatsapp",
    }
    assert public_request_url(environ) == "https://example.com/webhook/whatsapp"


def test_form_params_from_body_json_returns_raw_body():
    raw = '{"Body":"hello"}'
    assert form_params_from_body(raw, "application/json", parsed_payload=None) == raw


def test_form_params_from_body_form_flattens_lists():
    parsed = {"Body": ["hello"], "WaId": ["5511999"]}
    assert form_params_from_body("", "application/x-www-form-urlencoded", parsed_payload=parsed) == {
        "Body": "hello",
        "WaId": "5511999",
    }


def test_signature_is_valid_false_when_token_missing():
    assert signature_is_valid(None, "https://example.com/webhook", {"Body": "hi"}, "sig") is False
    assert signature_is_valid("", "https://example.com/webhook", {"Body": "hi"}, "sig") is False
    assert signature_is_valid("   ", "https://example.com/webhook", {"Body": "hi"}, "sig") is False


def test_signature_is_valid_false_when_signature_missing():
    assert signature_is_valid("token", "https://example.com/webhook", {"Body": "hi"}, None) is False
    assert signature_is_valid("token", "https://example.com/webhook", {"Body": "hi"}, "") is False
    assert signature_is_valid("token", "https://example.com/webhook", {"Body": "hi"}, "   ") is False


def test_signature_is_valid_false_when_url_missing():
    assert signature_is_valid("token", None, {"Body": "hi"}, "sig") is False
    assert signature_is_valid("token", "", {"Body": "hi"}, "sig") is False


def test_signature_is_valid_true_for_computed_form_signature():
    from twilio.request_validator import RequestValidator

    token = "auth-token"
    url = "https://example.com/webhook/whatsapp"
    params = {"Body": "hello", "WaId": "5511999"}
    signature = RequestValidator(token).compute_signature(url, params)
    assert signature_is_valid(token, url, params, signature) is True
