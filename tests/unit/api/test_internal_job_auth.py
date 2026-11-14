from unittest.mock import MagicMock, patch
from api.internal_job_auth import internal_job_request_is_authorized, path_requires_internal_job_auth
from api.routes import route_request


def test_path_requires_internal_job_auth():
    assert path_requires_internal_job_auth("/jobs/send-recommendations") is True
    assert path_requires_internal_job_auth("/workers/send-message") is True
    assert path_requires_internal_job_auth("/workers/send-campaign") is True
    assert path_requires_internal_job_auth("/health") is False
    assert path_requires_internal_job_auth("/webhook/whatsapp") is False


def test_internal_job_request_is_authorized_accepts_valid_secret():
    environ = {"HTTP_X_JOB_INTERNAL_SECRET": "expected-secret"}
    with patch("api.internal_job_auth.JOB_INTERNAL_SECRET", "expected-secret"):
        assert internal_job_request_is_authorized(environ) is True


def test_internal_job_request_is_authorized_rejects_wrong_secret():
    environ = {"HTTP_X_JOB_INTERNAL_SECRET": "wrong"}
    with patch("api.internal_job_auth.JOB_INTERNAL_SECRET", "expected-secret"):
        assert internal_job_request_is_authorized(environ) is False


def test_internal_job_request_is_authorized_rejects_missing_header():
    with patch("api.internal_job_auth.JOB_INTERNAL_SECRET", "expected-secret"):
        assert internal_job_request_is_authorized({}) is False


def test_internal_job_request_is_authorized_rejects_when_secret_not_configured():
    environ = {"HTTP_X_JOB_INTERNAL_SECRET": "anything"}
    with patch("api.internal_job_auth.JOB_INTERNAL_SECRET", None):
        assert internal_job_request_is_authorized(environ) is False


def test_route_request_rejects_job_without_secret():
    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    environ = {
        "REQUEST_METHOD": "POST",
        "PATH_INFO": "/jobs/send-recommendations",
    }

    with patch("api.internal_job_auth.JOB_INTERNAL_SECRET", "server-secret"):
        body = route_request(environ, start_response)

    assert captured["status"] == "401 Unauthorized"
    assert body == [b'{"error": "unauthorized"}']


def test_route_request_rejects_job_with_wrong_secret():
    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    environ = {
        "REQUEST_METHOD": "POST",
        "PATH_INFO": "/jobs/send-recommendations",
        "HTTP_X_JOB_INTERNAL_SECRET": "bad",
    }

    mock_handler = MagicMock()

    with patch("api.internal_job_auth.JOB_INTERNAL_SECRET", "server-secret"):
        with patch.dict("api.routes.ROUTES", {"/jobs/send-recommendations": mock_handler}):
            body = route_request(environ, start_response)

    assert captured["status"] == "401 Unauthorized"
    assert body == [b'{"error": "unauthorized"}']
    mock_handler.assert_not_called()


def test_route_request_accepts_worker_with_valid_secret():
    mock_handler = MagicMock(return_value=[b"ok"])

    def start_response(status, headers):
        pass

    environ = {
        "REQUEST_METHOD": "POST",
        "PATH_INFO": "/workers/send-message",
        "HTTP_X_JOB_INTERNAL_SECRET": "server-secret",
    }

    with patch("api.internal_job_auth.JOB_INTERNAL_SECRET", "server-secret"):
        with patch.dict("api.routes.ROUTES", {"/workers/send-message": mock_handler}):
            body = route_request(environ, start_response)

    mock_handler.assert_called_once()
    assert body == [b"ok"]
