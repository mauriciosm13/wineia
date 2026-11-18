import importlib
from unittest.mock import MagicMock

import core.config as config
import pytest

from domain.claude_budget import ClaudeBudgetExceededError
from domain.services.ia_service import IAService, create_client_context


class FakeClaudeBudgetRepository:
    def __init__(self, count=0):
        self.count = count
        self.increments = 0

    def get_call_count(self, day_key):
        return self.count

    def increment_call_count(self, day_key):
        self.increments += 1
        self.count += 1
        return self.count


def test_create_client_context_unknown_when_missing():
    assert create_client_context(None) == "Cliente desconhecido (nenhum dado cadastrado)."


def test_create_client_context_defaults_for_empty_fields():
    context = create_client_context({"phone": "+5511"})
    assert "Nome: Cliente" in context
    assert "Status: desconhecido" in context
    assert "Plano: desconhecido" in context


def test_create_client_context_uses_customer_fields():
    context = create_client_context({"name": "Ana", "status": "active", "plan": "free"})
    assert "Nome: Ana" in context
    assert "Status: active" in context
    assert "Plano: free" in context


def test_create_client_context_includes_preferences():
    context = create_client_context(
        {"name": "Ana", "status": "active", "plan": "free", "preferences": ["tinto", "malbec"]}
    )
    assert "Preferências: tinto, malbec" in context


def test_create_client_context_omits_empty_preferences():
    context = create_client_context({"name": "Ana", "status": "active", "plan": "free", "preferences": []})
    assert "Preferências:" not in context


def test_generate_response_sanitizes_and_validates(monkeypatch):
    mock_generate = MagicMock(return_value="  Malbec da Patagonia  ")
    monkeypatch.setattr("domain.services.ia_service.ClaudeClient.generate", mock_generate)

    result = IAService().generate_response(
        {"name": "Ana", "status": "active", "plan": "free"},
        "quero um tinto",
    )

    assert result == "Malbec da Patagonia"
    mock_generate.assert_called_once()
    _system, user_prompt = mock_generate.call_args.kwargs["system_prompt"], mock_generate.call_args.kwargs["user_prompt"]
    assert "Gastón" in _system
    assert "quero um tinto" in user_prompt


def test_generate_vision_response_includes_image_and_caption(monkeypatch):
    mock_generate = MagicMock(return_value="  Rotulo identificado  ")
    monkeypatch.setattr("domain.services.ia_service.ClaudeClient.generate", mock_generate)

    result = IAService().generate_vision_response(
        {"name": "Ana", "status": "active", "plan": "free"},
        b"jpeg-bytes",
        "image/jpeg",
        caption="o que e este vinho?",
    )

    assert result == "Rotulo identificado"
    kwargs = mock_generate.call_args.kwargs
    assert "Gastón" in kwargs["system_prompt"]
    assert "o que e este vinho?" in kwargs["user_prompt"]
    assert kwargs["images"] == [{"media_type": "image/jpeg", "data": b"jpeg-bytes"}]


def test_generate_vision_response_default_caption_when_empty(monkeypatch):
    mock_generate = MagicMock(return_value="ok")
    service = IAService(generate=mock_generate)

    service.generate_vision_response(
        {"name": "Ana", "status": "active", "plan": "free"},
        b"png",
        "image/png",
        caption="   ",
    )

    assert "Analise a imagem" in mock_generate.call_args.kwargs["user_prompt"]


def test_generate_vision_response_requires_bytes():
    service = IAService(generate=MagicMock())
    with pytest.raises(ValueError, match="image content"):
        service.generate_vision_response(
            {"name": "Ana"},
            b"",
            "image/jpeg",
        )


def test_generate_vision_response_respects_budget(monkeypatch):
    monkeypatch.setenv("CLAUDE_DAILY_CALL_BUDGET", "1")
    importlib.reload(config)
    mock_generate = MagicMock(return_value="should not run")
    repo = FakeClaudeBudgetRepository(count=1)
    service = IAService(budget_repository=repo, generate=mock_generate)

    with pytest.raises(ClaudeBudgetExceededError):
        service.generate_vision_response(
            {"name": "Ana", "status": "active", "plan": "free"},
            b"jpeg",
            "image/jpeg",
        )

    mock_generate.assert_not_called()
    monkeypatch.delenv("CLAUDE_DAILY_CALL_BUDGET", raising=False)
    importlib.reload(config)


def test_generate_recommendation_uses_wine_fields(monkeypatch):
    mock_generate = MagicMock(return_value="Indicação da semana: Malbec.")
    monkeypatch.setattr("domain.services.ia_service.ClaudeClient.generate", mock_generate)

    result = IAService().generate_recommendation(
        {"name": "Catena Malbec", "grape": "Malbec", "country": "Argentina"}
    )

    assert result == "Indicação da semana: Malbec."
    prompt = mock_generate.call_args.kwargs["system_prompt"]
    assert "Catena Malbec" in prompt
    assert "Malbec" in prompt
    assert "Argentina" in prompt


def test_generate_recommendation_includes_preferences_instruction(monkeypatch):
    mock_generate = MagicMock(return_value="Indicação da semana: Malbec.")
    monkeypatch.setattr("domain.services.ia_service.ClaudeClient.generate", mock_generate)

    result = IAService().generate_recommendation(
        {"name": "Catena Malbec", "grape": "Malbec", "country": "Argentina"},
        preferences=["tinto", "seco"],
    )

    assert result == "Indicação da semana: Malbec."
    prompt = mock_generate.call_args.kwargs["system_prompt"]
    assert "PREFERÊNCIAS DO CLIENTE" in prompt
    assert "tinto, seco" in prompt
    assert "EXCLUSIVAMENTE o vinho da semana" in prompt


def test_generate_recommendation_skips_blank_preferences(monkeypatch):
    mock_generate = MagicMock(return_value="ok")
    monkeypatch.setattr("domain.services.ia_service.ClaudeClient.generate", mock_generate)

    IAService().generate_recommendation(
        {"name": "A", "grape": "B", "country": "C"},
        preferences=["  ", 1],
    )

    prompt = mock_generate.call_args.kwargs["system_prompt"]
    assert "PREFERÊNCIAS DO CLIENTE" not in prompt


def test_generate_weekly_education_validates_and_uses_didactic_prompt(monkeypatch):
    mock_generate = MagicMock(return_value="  Dica da semana: taninos.  ")
    monkeypatch.setattr("domain.services.ia_service.ClaudeClient.generate", mock_generate)

    result = IAService().generate_weekly_education()

    assert result == "Dica da semana: taninos."
    mock_generate.assert_called_once()
    prompt = mock_generate.call_args.kwargs["system_prompt"]
    assert "Gastón" in prompt
    assert "didática" in prompt or "educativa" in prompt
    assert "NÃO cite preço" in prompt


def test_generate_with_budget_exceeded_skips_claude(monkeypatch):
    monkeypatch.setenv("CLAUDE_DAILY_CALL_BUDGET", "1")
    importlib.reload(config)
    mock_generate = MagicMock(return_value="should not run")
    repo = FakeClaudeBudgetRepository(count=1)
    service = IAService(budget_repository=repo, generate=mock_generate)

    with pytest.raises(ClaudeBudgetExceededError):
        service.generate_weekly_education()

    mock_generate.assert_not_called()
    assert repo.increments == 0
    monkeypatch.delenv("CLAUDE_DAILY_CALL_BUDGET", raising=False)
    importlib.reload(config)


def test_generate_with_budget_increments_after_success(monkeypatch):
    monkeypatch.setenv("CLAUDE_DAILY_CALL_BUDGET", "5")
    importlib.reload(config)
    mock_generate = MagicMock(return_value="  ok  ")
    repo = FakeClaudeBudgetRepository(count=0)
    service = IAService(budget_repository=repo, generate=mock_generate)

    result = service.generate_weekly_education()

    assert result == "ok"
    mock_generate.assert_called_once()
    assert repo.increments == 1
    monkeypatch.delenv("CLAUDE_DAILY_CALL_BUDGET", raising=False)
    importlib.reload(config)


def test_generate_with_budget_zero_does_not_touch_repository(monkeypatch):
    monkeypatch.setenv("CLAUDE_DAILY_CALL_BUDGET", "0")
    importlib.reload(config)
    mock_generate = MagicMock(return_value="ok")
    repo = FakeClaudeBudgetRepository(count=0)
    service = IAService(budget_repository=repo, generate=mock_generate)

    service.generate_weekly_education()

    mock_generate.assert_called_once()
    assert repo.increments == 0
    monkeypatch.delenv("CLAUDE_DAILY_CALL_BUDGET", raising=False)
    importlib.reload(config)


def test_generate_with_budget_uses_lazy_default_repository(monkeypatch):
    monkeypatch.setenv("CLAUDE_DAILY_CALL_BUDGET", "3")
    importlib.reload(config)
    mock_generate = MagicMock(return_value="ok")
    repo = FakeClaudeBudgetRepository(count=0)
    monkeypatch.setattr(
        "domain.services.ia_service._default_budget_repository",
        lambda: repo,
    )
    service = IAService(generate=mock_generate)

    result = service.generate_recommendation(
        {"name": "A", "grape": "B", "country": "C"},
    )

    assert result == "ok"
    mock_generate.assert_called_once()
    assert repo.increments == 1
    monkeypatch.delenv("CLAUDE_DAILY_CALL_BUDGET", raising=False)
    importlib.reload(config)
