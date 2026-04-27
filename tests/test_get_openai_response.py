import asyncio

import pytest

from app.get_openai_response import (
    OpenAIConfig,
    OpenAIValidationError,
    OpenAIAPIError,
    validate_messages,
    get_openai_response,
)


class DummyCompletion:
    def __init__(self, content: str):
        self.choices = [type("Choice", (), {"message": type("Message", (), {"content": content})})()]


class DummyClient:
    def __init__(self, *args, **kwargs):
        self.chat = self

    async def create(self, **kwargs):
        return DummyCompletion("resposta simulada")


@pytest.mark.parametrize("message", [None, [], "texto"])
def test_validate_messages_rejects_invalid_list(message):
    with pytest.raises(OpenAIValidationError):
        validate_messages(message)


def test_validate_messages_rejects_invalid_role():
    with pytest.raises(OpenAIValidationError, match="Role 'bot' inválido"):
        validate_messages([{"role": "bot", "content": "teste"}])


def test_validate_messages_rejects_empty_content():
    with pytest.raises(OpenAIValidationError, match="Conteúdo da mensagem 0 vazio ou inválido"):
        validate_messages([{"role": "user", "content": "   "}])


def test_validate_messages_accepts_valid_messages():
    messages = [{"role": "user", "content": "Olá"}, {"role": "assistant", "content": "Oi"}]
    validate_messages(messages)


def test_openai_config_from_env_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        OpenAIConfig.from_env()


def test_get_openai_response_raises_for_invalid_temperature():
    config = OpenAIConfig(api_key="x" * 30, temperature=2.5)
    with pytest.raises(OpenAIValidationError, match="Temperature deve estar entre 0.0 e 2.0"):
        asyncio.run(get_openai_response([{"role": "user", "content": "teste"}], config=config))


@pytest.mark.asyncio
async def test_get_openai_response_inserts_context(monkeypatch):
    async def mock_get_openai_response(messages, config):
        return "resposta simulada"

    async def mock_create(**kwargs):
        return DummyCompletion("resposta simulada")

    class MockAsyncOpenAI:
        def __init__(self, *args, **kwargs):
            self.chat = self
            self.completions = self

        async def create(self, **kwargs):
            return DummyCompletion("resposta simulada")

    monkeypatch.setattr("app.get_openai_response.get_context_for_question", lambda question: "contexto relevante")
    monkeypatch.setattr("app.get_openai_response.AsyncOpenAI", MockAsyncOpenAI)

    messages = [{"role": "user", "content": "Qual é a regra?"}]
    result = await get_openai_response(messages, config=OpenAIConfig(api_key="x" * 30))

    assert result == "resposta simulada"
    assert messages[0]["role"] == "system"
    assert "contexto relevante" in messages[0]["content"]


@pytest.mark.asyncio
async def test_get_openai_response_adds_default_system_message_when_no_context(monkeypatch):
    class MockAsyncOpenAI:
        def __init__(self, *args, **kwargs):
            self.chat = self
            self.completions = self

        async def create(self, **kwargs):
            return DummyCompletion("outro retorno")

    monkeypatch.setattr("app.get_openai_response.get_context_for_question", lambda question: "")
    monkeypatch.setattr("app.get_openai_response.AsyncOpenAI", MockAsyncOpenAI)

    messages = [{"role": "user", "content": "Qual é a regra?"}]
    result = await get_openai_response(messages, config=OpenAIConfig(api_key="x" * 30))

    assert result == "outro retorno"
    assert messages[0]["role"] == "system"
    assert "Use apenas informações da Resolução 175 consolidada" in messages[0]["content"]
