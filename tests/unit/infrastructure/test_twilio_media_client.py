from unittest.mock import MagicMock

import pytest

from infrastructure.external.twilio_media_client import TwilioMediaDownloadError, download_twilio_media


class _FakeResponse:
    def __init__(self, status_code=200, content=b"abc", content_type="image/jpeg", content_length=None):
        self.status_code = status_code
        self.headers = {"Content-Type": content_type}
        if content_length is not None:
            self.headers["Content-Length"] = str(content_length)
        self._content = content
        self.closed = False

    def iter_content(self, chunk_size=65536):
        yield self._content

    def close(self):
        self.closed = True


def test_download_success_with_basic_auth():
    session = MagicMock()
    session.get.return_value = _FakeResponse(content=b"wine-photo", content_type="image/jpeg")

    result = download_twilio_media(
        "https://api.twilio.com/media/abc",
        account_sid="ACxxx",
        auth_token="secret",
        session=session,
    )

    assert result == {
        "content": b"wine-photo",
        "content_type": "image/jpeg",
        "size": 10,
    }
    session.get.assert_called_once()
    kwargs = session.get.call_args.kwargs
    assert kwargs["auth"] == ("ACxxx", "secret")
    assert kwargs["allow_redirects"] is True
    assert kwargs["stream"] is True


def test_download_rejects_missing_url_and_credentials():
    with pytest.raises(TwilioMediaDownloadError):
        download_twilio_media("", account_sid="AC", auth_token="t")
    with pytest.raises(TwilioMediaDownloadError):
        download_twilio_media("https://api.twilio.com/media/abc", account_sid=None, auth_token="t")


def test_download_rejects_http_error_and_oversize():
    session = MagicMock()
    session.get.return_value = _FakeResponse(status_code=401)
    with pytest.raises(TwilioMediaDownloadError):
        download_twilio_media(
            "https://api.twilio.com/media/abc",
            account_sid="AC",
            auth_token="t",
            session=session,
        )

    session.get.return_value = _FakeResponse(
        content=b"x" * 10,
        content_type="image/jpeg",
        content_length=6 * 1024 * 1024,
    )
    with pytest.raises(TwilioMediaDownloadError, match="max size"):
        download_twilio_media(
            "https://api.twilio.com/media/abc",
            account_sid="AC",
            auth_token="t",
            session=session,
        )


def test_download_rejects_disallowed_mime_and_empty_body():
    session = MagicMock()
    session.get.return_value = _FakeResponse(content=b"pdf", content_type="application/pdf")
    with pytest.raises(TwilioMediaDownloadError, match="content type"):
        download_twilio_media(
            "https://api.twilio.com/media/abc",
            account_sid="AC",
            auth_token="t",
            session=session,
        )

    session.get.return_value = _FakeResponse(content=b"", content_type="image/png")
    with pytest.raises(TwilioMediaDownloadError, match="empty"):
        download_twilio_media(
            "https://api.twilio.com/media/abc",
            account_sid="AC",
            auth_token="t",
            session=session,
        )
