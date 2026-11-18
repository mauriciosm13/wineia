from unittest.mock import MagicMock

import pytest
import requests

from infrastructure.external.openai_stt_client import OpenAISTTError, transcribe_audio


class _FakeResponse:
    def __init__(self, status_code=200, payload=None, text="", json_error=False):
        self.status_code = status_code
        self._payload = payload
        self.text = text
        self._json_error = json_error

    def json(self):
        if self._json_error:
            raise ValueError("bad json")
        return self._payload


def test_transcribe_audio_success(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    session = MagicMock()
    session.post.return_value = _FakeResponse(payload={"text": "  quero malbec  "})

    text = transcribe_audio(b"ogg-bytes", "audio/ogg", session=session)

    assert text == "quero malbec"
    kwargs = session.post.call_args.kwargs
    assert kwargs["data"]["model"] == "whisper-1"
    assert kwargs["data"]["language"] == "pt"
    assert kwargs["headers"]["Authorization"] == "Bearer sk-test"
    assert kwargs["files"]["file"][0] == "audio.ogg"
    assert kwargs["files"]["file"][1] == b"ogg-bytes"


def test_transcribe_audio_rejects_incompatible_mime(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    with pytest.raises(OpenAISTTError, match="not supported"):
        transcribe_audio(b"amr", "audio/amr")


def test_transcribe_audio_requires_content(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    with pytest.raises(OpenAISTTError, match="content is required"):
        transcribe_audio(b"", "audio/ogg")


def test_transcribe_audio_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(
        "infrastructure.external.openai_stt_client.load_config",
        lambda: {},
    )
    with pytest.raises(OpenAISTTError, match="api key"):
        transcribe_audio(b"ogg", "audio/ogg")


def test_transcribe_audio_http_failure(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    session = MagicMock()
    session.post.return_value = _FakeResponse(status_code=500, payload={"error": "x"})

    with pytest.raises(OpenAISTTError, match="HTTP 500"):
        transcribe_audio(b"ogg", "audio/ogg", session=session)


def test_transcribe_audio_request_exception(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    session = MagicMock()
    session.post.side_effect = requests.Timeout("boom")

    with pytest.raises(OpenAISTTError, match="request failed"):
        transcribe_audio(b"ogg", "audio/ogg", session=session)


def test_transcribe_audio_empty_transcript(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    session = MagicMock()
    session.post.return_value = _FakeResponse(payload={"text": "  "})

    with pytest.raises(OpenAISTTError, match="empty"):
        transcribe_audio(b"ogg", "audio/ogg", session=session)


def test_transcribe_audio_invalid_json(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    session = MagicMock()
    session.post.return_value = _FakeResponse(json_error=True)

    with pytest.raises(OpenAISTTError, match="not json"):
        transcribe_audio(b"ogg", "audio/ogg", session=session)


def test_transcribe_audio_config_json_fallback(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(
        "infrastructure.external.openai_stt_client.load_config",
        lambda: {"OPENAI_API_KEY": "sk-from-config"},
    )
    session = MagicMock()
    session.post.return_value = _FakeResponse(payload={"text": "ola"})

    text = transcribe_audio(b"ogg", "audio/ogg", session=session)

    assert text == "ola"
    assert session.post.call_args.kwargs["headers"]["Authorization"] == "Bearer sk-from-config"
