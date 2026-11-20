from unittest.mock import MagicMock

import pytest
import requests

from infrastructure.external.grok_stt_client import GrokSTTError, transcribe_audio


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
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    session = MagicMock()
    session.post.return_value = _FakeResponse(payload={"text": "  quero malbec  "})

    text = transcribe_audio(b"ogg-bytes", "audio/ogg", session=session)

    assert text == "quero malbec"
    kwargs = session.post.call_args.kwargs
    assert kwargs["data"] == [
        ("model", "grok-voice-transcribe-2.0"),
        ("language", "pt"),
    ]
    assert kwargs["headers"]["Authorization"] == "Bearer xai-test"
    assert kwargs["files"]["file"][0] == "audio.ogg"
    assert kwargs["files"]["file"][1] == b"ogg-bytes"
    assert session.post.call_args.args[0] == "https://api.x.ai/v1/stt"


def test_transcribe_audio_rejects_incompatible_mime(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    with pytest.raises(GrokSTTError, match="not supported"):
        transcribe_audio(b"amr", "audio/amr")


def test_transcribe_audio_requires_content(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    with pytest.raises(GrokSTTError, match="content is required"):
        transcribe_audio(b"", "audio/ogg")


def test_transcribe_audio_requires_api_key(monkeypatch):
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    monkeypatch.setattr(
        "infrastructure.external.grok_stt_client.load_config",
        lambda: {},
    )
    with pytest.raises(GrokSTTError, match="api key"):
        transcribe_audio(b"ogg", "audio/ogg")


def test_transcribe_audio_http_failure(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    session = MagicMock()
    session.post.return_value = _FakeResponse(status_code=500, payload={"error": "x"})

    with pytest.raises(GrokSTTError, match="HTTP 500"):
        transcribe_audio(b"ogg", "audio/ogg", session=session)


def test_transcribe_audio_request_exception(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    session = MagicMock()
    session.post.side_effect = requests.Timeout("boom")

    with pytest.raises(GrokSTTError, match="request failed"):
        transcribe_audio(b"ogg", "audio/ogg", session=session)


def test_transcribe_audio_empty_transcript(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    session = MagicMock()
    session.post.return_value = _FakeResponse(payload={"text": "  "})

    with pytest.raises(GrokSTTError, match="empty"):
        transcribe_audio(b"ogg", "audio/ogg", session=session)


def test_transcribe_audio_invalid_json(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    session = MagicMock()
    session.post.return_value = _FakeResponse(json_error=True)

    with pytest.raises(GrokSTTError, match="not json"):
        transcribe_audio(b"ogg", "audio/ogg", session=session)


def test_transcribe_audio_config_json_fallback(monkeypatch):
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    monkeypatch.setattr(
        "infrastructure.external.grok_stt_client.load_config",
        lambda: {"XAI_API_KEY": "xai-from-config"},
    )
    session = MagicMock()
    session.post.return_value = _FakeResponse(payload={"text": "ola"})

    text = transcribe_audio(b"ogg", "audio/ogg", session=session)

    assert text == "ola"
    assert session.post.call_args.kwargs["headers"]["Authorization"] == "Bearer xai-from-config"


def test_transcribe_audio_model_override(monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    monkeypatch.setenv("XAI_STT_MODEL", "grok-voice-transcribe-custom")
    session = MagicMock()
    session.post.return_value = _FakeResponse(payload={"text": "ok"})

    transcribe_audio(b"ogg", "audio/ogg", session=session)

    assert session.post.call_args.kwargs["data"][0] == ("model", "grok-voice-transcribe-custom")
