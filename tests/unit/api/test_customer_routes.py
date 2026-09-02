from unittest.mock import MagicMock

from api import routes
from api.handlers import customer_handler


def test_route_list_customers_dispatches_get(monkeypatch):
    handler = MagicMock(return_value=[b"ok"])
    monkeypatch.setattr(customer_handler, "handle_list_customers", handler)

    def start_response(status, headers):
        pass

    environ = {"REQUEST_METHOD": "GET", "PATH_INFO": "/customers"}
    body = routes.route_request(environ, start_response)

    handler.assert_called_once_with(environ, start_response)
    assert body == [b"ok"]


def test_route_create_customer_dispatches_post(monkeypatch):
    handler = MagicMock(return_value=[b"created"])
    monkeypatch.setattr(customer_handler, "handle_create_customer", handler)

    def start_response(status, headers):
        pass

    environ = {"REQUEST_METHOD": "POST", "PATH_INFO": "/customers", "CONTENT_LENGTH": "0", "wsgi.input": MagicMock()}
    body = routes.route_request(environ, start_response)

    handler.assert_called_once()
    assert body == [b"created"]


def test_route_get_customer_by_phone(monkeypatch):
    handler = MagicMock(return_value=[b"customer"])
    monkeypatch.setattr(customer_handler, "handle_get_customer", handler)

    def start_response(status, headers):
        pass

    environ = {"REQUEST_METHOD": "GET", "PATH_INFO": "/customers/%2B5511999999999"}
    body = routes.route_request(environ, start_response)

    handler.assert_called_once()
    assert handler.call_args[0][2] == "+5511999999999"
    assert body == [b"customer"]


def test_route_update_customer_by_phone(monkeypatch):
    handler = MagicMock(return_value=[b"updated"])
    monkeypatch.setattr(customer_handler, "handle_update_customer", handler)

    def start_response(status, headers):
        pass

    environ = {"REQUEST_METHOD": "PATCH", "PATH_INFO": "/customers/+5511999999999"}
    body = routes.route_request(environ, start_response)

    handler.assert_called_once()
    assert handler.call_args[0][2] == "+5511999999999"
    assert body == [b"updated"]


def test_route_pre_sale_dispatches_to_pre_sale_handler(monkeypatch):
    handler = MagicMock(return_value=[b"pre-sale"])
    monkeypatch.setattr(customer_handler, "handle_create_pre_sale_customer", handler)

    def start_response(status, headers):
        pass

    environ = {"REQUEST_METHOD": "POST", "PATH_INFO": "/customers/pre-sale"}
    body = routes.route_request(environ, start_response)

    handler.assert_called_once()
    assert body == [b"pre-sale"]
