import importlib
import os

import pytest
from fastapi import FastAPI

from app.config import Settings
from app.models import ChatRequest, Message
from app.security import (
    validate_bearer_token,
    setup_cors,
    setup_security_middleware,
)


def test_settings_validate_configuration_accepts_valid_values(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x" * 30)
    monkeypatch.setenv("SECRET_KEY", "my-secret-key")
    monkeypatch.setenv("OPENAI_TEMPERATURE", "0.5")
    monkeypatch.setenv("OPENAI_MAX_TOKENS", "0")

    settings = Settings()
    settings.validate_configuration()

    assert settings.openai_api_key == "x" * 30
    assert settings.secret_key == "my-secret-key"
    assert settings.openai_temperature == 0.5


def test_get_settings_caches_instance(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "y" * 30)
    monkeypatch.setenv("SECRET_KEY", "another-secret")
    monkeypatch.setenv("OPENAI_MAX_TOKENS", "0")

    import app.config as config_mod
    config_mod.get_settings.cache_clear()

    first = config_mod.get_settings()
    second = config_mod.get_settings()

    assert first is second
    assert first.openai_api_key == "y" * 30


def test_message_validator_rejects_invalid_role():
    with pytest.raises(ValueError, match="Role deve ser um de"):
        Message(role="bot", content="texto válido")


def test_message_validator_rejects_blank_content():
    with pytest.raises(ValueError, match="Conteúdo não pode ser apenas espaços em branco"):
        Message(role="user", content="   ")


def test_chat_request_requires_user_role():
    with pytest.raises(ValueError, match="Deve haver pelo menos uma mensagem com role='user'"):
        ChatRequest(messages=[Message(role="system", content="teste")])


def test_validate_bearer_token_accepts_valid_bearer():
    assert validate_bearer_token("Bearer token123", "secret") is True


def test_validate_bearer_token_rejects_wrong_scheme():
    assert validate_bearer_token("Basic token123", "secret") is False


def test_validate_bearer_token_rejects_missing_token():
    assert validate_bearer_token("Bearer ", "secret") is False


def test_setup_cors_adds_cors_middleware():
    app = FastAPI()
    setup_cors(app, ["http://localhost:3000"])

    assert any(m.cls.__name__ == "CORSMiddleware" for m in app.user_middleware)


def test_setup_security_middleware_adds_middlewares():
    app = FastAPI()
    setup_security_middleware(app, requests_per_minute=5)

    middleware_names = [m.cls.__name__ for m in app.user_middleware]
    assert "SecurityHeadersMiddleware" in middleware_names
    assert "RequestLoggingMiddleware" in middleware_names
    assert "RateLimitMiddleware" in middleware_names
