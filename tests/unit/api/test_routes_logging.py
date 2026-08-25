import logging

from api.routes import route_request
from core.logging import log_request


def test_unknown_path_logs_request_and_returns_404(caplog):
    captured = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = headers

    environ = {"REQUEST_METHOD": "GET", "PATH_INFO": "/unknown"}

    with caplog.at_level(logging.INFO, logger="wine-concierge"):
        body = route_request(environ, start_response)

    assert captured["status"] == "404 Not Found"
    assert body == [b"Not Found"]
    assert any(
        "request method=GET path=/unknown" in record.message
        for record in caplog.records
    )


def test_log_request_includes_status(caplog):
    with caplog.at_level(logging.INFO, logger="wine-concierge"):
        log_request("POST", "/health", status="200")

    assert any("status=200" in record.message for record in caplog.records)
