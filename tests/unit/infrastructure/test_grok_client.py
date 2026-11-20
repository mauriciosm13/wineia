import base64
from unittest.mock import MagicMock

import pytest
import requests

from infrastructure.external.grok_client import GrokClient, GrokClientError, _build_user_content


class _FakeResponse:
    def __init__(self, status_code=200, payload=None, json_error=False):
        self.status_code = status_code
        self._payload = payload
        self._json_error = json_error

    def json(self):
        if self._json_error:
            raise ValueError("bad json")
        return self._payload


def test_build_user_content_text_only_returns_string():
    assert _build_user_content(user_prompt="ola") == "ola"
    assert _build_user_content(user_prompt=None, images=None) == ""


def test_build_user_content_with_image_blocks():
    content = _build_user_content(
        user_prompt="descreva",
        images=[{"media_type": "image/jpg", "data": b"abc"}],
    )

    assert isinstance(content, list)
    assert content[0]["type"] == "image_url"
    encoded = base64.b64encode(b"abc").decode("ascii")
    assert content[0]["image_url"]["url"] == f"data:image/jpeg;base64,{encoded}"
    assert content[1] == {"type": "text", "text": "descreva"}


def test_generate_text_only(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    monkeypatch.delenv("XAI_API_MODEL", raising=False)
    monkeypatch.delenv("GROK_API_MODEL", raising=False)
    session = MagicMock()
    session.post.return_value = _FakeResponse(
        payload={"choices": [{"message": {"content": "  resposta  "}}]},
    )

    result = GrokClient.generate(system_prompt="sys", user_prompt="oi", session=session)

    assert result == "  resposta  "
    kwargs = session.post.call_args.kwargs
    assert kwargs["headers"]["Authorization"] == "Bearer xai-test"
    assert kwargs["json"]["model"] == "grok-4.7"
    assert kwargs["json"]["messages"][0] == {"role": "system", "content": "sys"}
    assert kwargs["json"]["messages"][1]["content"] == "oi"


def test_generate_with_images(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    session = MagicMock()
    session.post.return_value = _FakeResponse(
        payload={"choices": [{"message": {"content": "foto ok"}}]},
    )

    result = GrokClient.generate(
        system_prompt="sys",
        user_prompt="legenda",
        images=[{"media_type": "image/png", "data": b"png"}],
        session=session,
    )

    assert result == "foto ok"
    content = session.post.call_args.kwargs["json"]["messages"][1]["content"]
    assert content[0]["type"] == "image_url"
    assert content[0]["image_url"]["url"].startswith("data:image/png;base64,")
    assert content[1]["text"] == "legenda"


def test_generate_uses_env_model_override(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    monkeypatch.setenv("XAI_API_MODEL", "grok-custom")
    session = MagicMock()
    session.post.return_value = _FakeResponse(
        payload={"choices": [{"message": {"content": "ok"}}]},
    )

    GrokClient.generate(system_prompt="sys", user_prompt="oi", session=session)

    assert session.post.call_args.kwargs["json"]["model"] == "grok-custom"


def test_generate_requires_api_key(monkeypatch):
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    monkeypatch.setattr(
        "infrastructure.external.grok_client.load_config",
        lambda: {},
    )
    with pytest.raises(GrokClientError, match="api key"):
        GrokClient.generate(system_prompt="sys", user_prompt="oi")


def test_generate_config_json_fallback(monkeypatch):
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    monkeypatch.delenv("XAI_API_MODEL", raising=False)
    monkeypatch.delenv("GROK_API_MODEL", raising=False)
    monkeypatch.setattr(
        "infrastructure.external.grok_client.load_config",
        lambda: {"XAI_API_KEY": "from-config", "XAI_API_MODEL": "grok-from-config"},
    )
    session = MagicMock()
    session.post.return_value = _FakeResponse(
        payload={"choices": [{"message": {"content": "ola"}}]},
    )

    result = GrokClient.generate(system_prompt="sys", user_prompt="oi", session=session)

    assert result == "ola"
    assert session.post.call_args.kwargs["headers"]["Authorization"] == "Bearer from-config"
    assert session.post.call_args.kwargs["json"]["model"] == "grok-from-config"


def test_generate_http_failure(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    session = MagicMock()
    session.post.return_value = _FakeResponse(status_code=500, payload={"error": "x"})

    with pytest.raises(GrokClientError, match="HTTP 500"):
        GrokClient.generate(system_prompt="sys", user_prompt="oi", session=session)


def test_generate_request_exception(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    session = MagicMock()
    session.post.side_effect = requests.Timeout("boom")

    with pytest.raises(GrokClientError, match="request failed"):
        GrokClient.generate(system_prompt="sys", user_prompt="oi", session=session)


def test_generate_invalid_json(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    session = MagicMock()
    session.post.return_value = _FakeResponse(json_error=True)

    with pytest.raises(GrokClientError, match="not json"):
        GrokClient.generate(system_prompt="sys", user_prompt="oi", session=session)


def test_generate_empty_choices_returns_empty_string(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    session = MagicMock()
    session.post.return_value = _FakeResponse(payload={"choices": []})

    assert GrokClient.generate(system_prompt="sys", user_prompt="oi", session=session) == ""
