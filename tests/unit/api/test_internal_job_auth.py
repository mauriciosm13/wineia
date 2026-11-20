from unittest.mock import MagicMock, patch
from api.internal_job_auth import internal_job_request_is_authorized, path_requires_internal_job_auth
from api.routes import route_request


def test_path_requires_internal_job_auth():
    assert path_requires_internal_job_auth("/jobs/send-recommendations") is True
    assert path_requires_internal_job_auth("/workers/send-message") is True
    assert path_requires_internal_job_auth("/workers/send-campaign") is True
    assert path_requires_internal_job_auth("/customers") is True
    assert path_requires_internal_job_auth("/customers/+5511999999999") is True
    assert path_requires_internal_job_auth("/customers/+5511999999999/export") is True
    assert path_requires_internal_job_auth("/customers/pre-sale") is True
    assert path_requires_internal_job_auth("/ia/suggestions") is True
    assert path_requires_internal_job_auth("/recommendation-contents") is True
    assert path_requires_internal_job_auth("/waitlist", "GET") is True
    assert path_requires_internal_job_auth("/waitlist", "POST") is False
    assert path_requires_internal_job_auth("/waitlist") is False
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


def test_route_request_rejects_customers_without_secret():
    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    environ = {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": "/customers",
    }
    mock_handler = MagicMock()

    with patch("api.internal_job_auth.JOB_INTERNAL_SECRET", "server-secret"):
        with patch("api.routes.handle_customer_request", mock_handler):
            body = route_request(environ, start_response)

    assert captured["status"] == "401 Unauthorized"
    assert body == [b'{"error": "unauthorized"}']
    mock_handler.assert_not_called()


def test_route_request_rejects_customers_when_secret_unset():
    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    environ = {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": "/customers/+5511999999999/export",
        "HTTP_X_JOB_INTERNAL_SECRET": "anything",
    }
    mock_handler = MagicMock()

    with patch("api.internal_job_auth.JOB_INTERNAL_SECRET", None):
        with patch("api.routes.handle_customer_request", mock_handler):
            body = route_request(environ, start_response)

    assert captured["status"] == "401 Unauthorized"
    assert body == [b'{"error": "unauthorized"}']
    mock_handler.assert_not_called()


def test_route_request_accepts_customers_with_valid_secret():
    mock_handler = MagicMock(return_value=[b"ok"])

    def start_response(status, headers):
        pass

    environ = {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": "/customers",
        "HTTP_X_JOB_INTERNAL_SECRET": "server-secret",
    }

    with patch("api.internal_job_auth.JOB_INTERNAL_SECRET", "server-secret"):
        with patch("api.routes.handle_customer_request", mock_handler):
            body = route_request(environ, start_response)

    mock_handler.assert_called_once()
    assert body == [b"ok"]


def test_route_request_rejects_ia_suggestions_without_secret():
    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    environ = {
        "REQUEST_METHOD": "POST",
        "PATH_INFO": "/ia/suggestions",
    }
    mock_handler = MagicMock()

    with patch("api.internal_job_auth.JOB_INTERNAL_SECRET", "server-secret"):
        with patch.dict("api.routes.ROUTES", {"/ia/suggestions": mock_handler}):
            body = route_request(environ, start_response)

    assert captured["status"] == "401 Unauthorized"
    assert body == [b'{"error": "unauthorized"}']
    mock_handler.assert_not_called()


def test_route_request_accepts_ia_suggestions_with_valid_secret():
    mock_handler = MagicMock(return_value=[b"ok"])

    def start_response(status, headers):
        pass

    environ = {
        "REQUEST_METHOD": "POST",
        "PATH_INFO": "/ia/suggestions",
        "HTTP_X_JOB_INTERNAL_SECRET": "server-secret",
    }

    with patch("api.internal_job_auth.JOB_INTERNAL_SECRET", "server-secret"):
        with patch.dict("api.routes.ROUTES", {"/ia/suggestions": mock_handler}):
            body = route_request(environ, start_response)

    mock_handler.assert_called_once()
    assert body == [b"ok"]


def test_route_request_rejects_recommendation_contents_without_secret():
    captured = {}

    def start_response(status, headers):
        captured["status"] = status

    environ = {
        "REQUEST_METHOD": "POST",
        "PATH_INFO": "/recommendation-contents",
        "HTTP_X_JOB_INTERNAL_SECRET": "wrong",
    }
    mock_handler = MagicMock()

    with patch("api.internal_job_auth.JOB_INTERNAL_SECRET", "server-secret"):
        with patch.dict("api.routes.ROUTES", {"/recommendation-contents": mock_handler}):
            body = route_request(environ, start_response)

    assert captured["status"] == "401 Unauthorized"
    assert body == [b'{"error": "unauthorized"}']
    mock_handler.assert_not_called()


def test_route_request_accepts_recommendation_contents_with_valid_secret():
    mock_handler = MagicMock(return_value=[b"ok"])

    def start_response(status, headers):
        pass

    environ = {
        "REQUEST_METHOD": "POST",
        "PATH_INFO": "/recommendation-contents",
        "HTTP_X_JOB_INTERNAL_SECRET": "server-secret",
    }

    with patch("api.internal_job_auth.JOB_INTERNAL_SECRET", "server-secret"):
        with patch.dict("api.routes.ROUTES", {"/recommendation-contents": mock_handler}):
            body = route_request(environ, start_response)

    mock_handler.assert_called_once()
    assert body == [b"ok"]


def test_route_request_health_does_not_require_secret():
    mock_handler = MagicMock(return_value=[b"ok"])

    def start_response(status, headers):
        pass

    environ = {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": "/health",
    }

    with patch("api.internal_job_auth.JOB_INTERNAL_SECRET", None):
        with patch.dict("api.routes.ROUTES", {"/health": mock_handler}):
            body = route_request(environ, start_response)

    mock_handler.assert_called_once()
    assert body == [b"ok"]


def test_route_request_webhook_does_not_require_secret():
    mock_handler = MagicMock(return_value=[b"ok"])

    def start_response(status, headers):
        pass

    environ = {
        "REQUEST_METHOD": "POST",
        "PATH_INFO": "/webhook/whatsapp",
    }

    with patch("api.internal_job_auth.JOB_INTERNAL_SECRET", "server-secret"):
        with patch("api.routes.webhook_ip_rate_limit_allows", return_value=True):
            with patch.dict("api.routes.ROUTES", {"/webhook/whatsapp": mock_handler}):
                body = route_request(environ, start_response)

    mock_handler.assert_called_once()
    assert body == [b"ok"]
