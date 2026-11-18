import base64
from unittest.mock import MagicMock

from infrastructure.external.claude_client import ClaudeClient, _build_user_content


def test_build_user_content_text_only_returns_string():
    assert _build_user_content(user_prompt="ola") == "ola"
    assert _build_user_content(user_prompt=None, images=None) == ""


def test_build_user_content_with_image_blocks():
    content = _build_user_content(
        user_prompt="descreva",
        images=[{"media_type": "image/jpg", "data": b"abc"}],
    )

    assert isinstance(content, list)
    assert content[0]["type"] == "image"
    assert content[0]["source"]["media_type"] == "image/jpeg"
    assert content[0]["source"]["data"] == base64.b64encode(b"abc").decode("ascii")
    assert content[1] == {"type": "text", "text": "descreva"}


def test_generate_text_only_preserves_string_content(monkeypatch):
    fake_message = MagicMock()
    fake_block = MagicMock()
    fake_block.type = "text"
    fake_block.text = "resposta"
    fake_message.content = [fake_block]

    fake_client = MagicMock()
    fake_client.messages.create.return_value = fake_message
    monkeypatch.setattr(
        "infrastructure.external.claude_client.load_config",
        lambda: {"ANTHROPIC_API_KEY": "k", "ANTHROPIC_API_MODEL": "m"},
    )
    monkeypatch.setattr(
        "infrastructure.external.claude_client.Anthropic",
        lambda api_key: fake_client,
    )

    result = ClaudeClient.generate(system_prompt="sys", user_prompt="oi")

    assert result == "resposta"
    kwargs = fake_client.messages.create.call_args.kwargs
    assert kwargs["messages"][0]["content"] == "oi"


def test_generate_with_images_sends_multimodal_content(monkeypatch):
    fake_message = MagicMock()
    fake_block = MagicMock()
    fake_block.type = "text"
    fake_block.text = "foto ok"
    fake_message.content = [fake_block]

    fake_client = MagicMock()
    fake_client.messages.create.return_value = fake_message
    monkeypatch.setattr(
        "infrastructure.external.claude_client.load_config",
        lambda: {"ANTHROPIC_API_KEY": "k", "ANTHROPIC_API_MODEL": "m"},
    )
    monkeypatch.setattr(
        "infrastructure.external.claude_client.Anthropic",
        lambda api_key: fake_client,
    )

    result = ClaudeClient.generate(
        system_prompt="sys",
        user_prompt="legenda",
        images=[{"media_type": "image/png", "data": b"png"}],
    )

    assert result == "foto ok"
    content = fake_client.messages.create.call_args.kwargs["messages"][0]["content"]
    assert content[0]["type"] == "image"
    assert content[0]["source"]["media_type"] == "image/png"
    assert content[1]["text"] == "legenda"
