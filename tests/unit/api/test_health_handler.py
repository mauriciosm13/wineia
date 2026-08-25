from api.handlers.health_handler import handle_health


def test_health_returns_ok_json():
    captured = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = headers

    body = handle_health({}, start_response)

    assert captured["status"] == "200 OK"
    assert captured["headers"] == [("Content-Type", "application/json")]
    assert body == [b'{"status": "ok"}']
