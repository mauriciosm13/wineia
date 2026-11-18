from unittest.mock import MagicMock

from api import routes
from api.handlers import customer_handler

_OPERATOR_SECRET = "test-operator-secret"


def _environ(method, path, **extra):
    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "HTTP_X_JOB_INTERNAL_SECRET": _OPERATOR_SECRET,
    }
    environ.update(extra)
    return environ


def test_route_list_customers_dispatches_get(monkeypatch):
    handler = MagicMock(return_value=[b"ok"])
    monkeypatch.setattr(customer_handler, "handle_list_customers", handler)
    monkeypatch.setattr("api.internal_job_auth.JOB_INTERNAL_SECRET", _OPERATOR_SECRET)

    def start_response(status, headers):
        pass

    body = routes.route_request(_environ("GET", "/customers"), start_response)

    handler.assert_called_once()
    assert body == [b"ok"]


def test_route_create_customer_dispatches_post(monkeypatch):
    handler = MagicMock(return_value=[b"created"])
    monkeypatch.setattr(customer_handler, "handle_create_customer", handler)
    monkeypatch.setattr("api.internal_job_auth.JOB_INTERNAL_SECRET", _OPERATOR_SECRET)

    def start_response(status, headers):
        pass

    environ = _environ("POST", "/customers", CONTENT_LENGTH="0")
    environ["wsgi.input"] = MagicMock()
    body = routes.route_request(environ, start_response)

    handler.assert_called_once()
    assert body == [b"created"]


def test_route_get_customer_by_phone(monkeypatch):
    handler = MagicMock(return_value=[b"customer"])
    monkeypatch.setattr(customer_handler, "handle_get_customer", handler)
    monkeypatch.setattr("api.internal_job_auth.JOB_INTERNAL_SECRET", _OPERATOR_SECRET)

    def start_response(status, headers):
        pass

    body = routes.route_request(_environ("GET", "/customers/%2B5511999999999"), start_response)

    handler.assert_called_once()
    assert handler.call_args[0][2] == "+5511999999999"
    assert body == [b"customer"]


def test_route_update_customer_by_phone(monkeypatch):
    handler = MagicMock(return_value=[b"updated"])
    monkeypatch.setattr(customer_handler, "handle_update_customer", handler)
    monkeypatch.setattr("api.internal_job_auth.JOB_INTERNAL_SECRET", _OPERATOR_SECRET)

    def start_response(status, headers):
        pass

    body = routes.route_request(_environ("PATCH", "/customers/+5511999999999"), start_response)

    handler.assert_called_once()
    assert handler.call_args[0][2] == "+5511999999999"
    assert body == [b"updated"]


def test_route_pre_sale_dispatches_to_pre_sale_handler(monkeypatch):
    handler = MagicMock(return_value=[b"pre-sale"])
    monkeypatch.setattr(customer_handler, "handle_create_pre_sale_customer", handler)
    monkeypatch.setattr("api.internal_job_auth.JOB_INTERNAL_SECRET", _OPERATOR_SECRET)

    def start_response(status, headers):
        pass

    body = routes.route_request(_environ("POST", "/customers/pre-sale"), start_response)

    handler.assert_called_once()
    assert body == [b"pre-sale"]


def test_route_export_customer_by_phone(monkeypatch):
    handler = MagicMock(return_value=[b"export"])
    monkeypatch.setattr(customer_handler, "handle_export_customer", handler)
    monkeypatch.setattr("api.internal_job_auth.JOB_INTERNAL_SECRET", _OPERATOR_SECRET)

    def start_response(status, headers):
        pass

    body = routes.route_request(_environ("GET", "/customers/%2B5511999999999/export"), start_response)

    handler.assert_called_once()
    assert handler.call_args[0][2] == "+5511999999999"
    assert body == [b"export"]


def test_route_erase_customer_by_phone(monkeypatch):
    handler = MagicMock(return_value=[b"erased"])
    monkeypatch.setattr(customer_handler, "handle_erase_customer", handler)
    monkeypatch.setattr("api.internal_job_auth.JOB_INTERNAL_SECRET", _OPERATOR_SECRET)

    def start_response(status, headers):
        pass

    body = routes.route_request(_environ("POST", "/customers/+5511999999999/erase"), start_response)

    handler.assert_called_once()
    assert handler.call_args[0][2] == "+5511999999999"
    assert body == [b"erased"]
