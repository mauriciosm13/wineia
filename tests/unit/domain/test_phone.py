from domain.phone import normalize_phone


def test_normalize_phone_e164():
    assert normalize_phone("+5511999999999") == "+5511999999999"


def test_normalize_phone_strips_whatsapp_prefix_and_spaces():
    assert normalize_phone(" whatsapp:+55 11 99999-9999 ") == "+5511999999999"


def test_normalize_phone_digits_only_gets_plus():
    assert normalize_phone("5511987654321") == "+5511987654321"


def test_normalize_phone_rejects_empty_and_invalid():
    assert normalize_phone("") is None
    assert normalize_phone(None) is None
    assert normalize_phone("123") is None
    assert normalize_phone("not-a-phone") is None
    assert normalize_phone(5511999999999) is None
    assert normalize_phone("   ") is None
    assert normalize_phone("+") is None
