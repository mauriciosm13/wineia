from unittest.mock import MagicMock

from domain.services.ia_service import IAService, create_client_context


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
