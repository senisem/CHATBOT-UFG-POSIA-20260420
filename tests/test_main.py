import importlib
import os

import pytest
from fastapi.testclient import TestClient


def setup_test_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x" * 30)
    monkeypatch.setenv("SECRET_KEY", "secret-key-value")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4-mini")
    monkeypatch.setenv("OPENAI_TEMPERATURE", "0.7")
    monkeypatch.setenv("OPENAI_MAX_TOKENS", "0")
    monkeypatch.setenv("OPENAI_TIMEOUT", "30")
    monkeypatch.setenv("OPENAI_MAX_RETRIES", "3")


def test_health_check_endpoint_returns_healthy(monkeypatch):
    setup_test_env(monkeypatch)

    import app.config as config_mod
    config_mod.get_settings.cache_clear()
    import app.main as main
    importlib.reload(config_mod)
    importlib.reload(main)

    client = TestClient(main.app)
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["openai_configured"] is True


def test_custom_openapi_contains_security_metadata(monkeypatch):
    setup_test_env(monkeypatch)

    import app.config as config_mod
    config_mod.get_settings.cache_clear()
    import app.main as main
    importlib.reload(config_mod)
    importlib.reload(main)

    schema = main.app.openapi()
    assert "x-security" in schema["info"]
    assert any("Rate Limiting" in item for item in schema["info"]["x-security"])


def test_chat_endpoint_uses_mocked_openai(monkeypatch):
    setup_test_env(monkeypatch)

    import app.config as config_mod
    config_mod.get_settings.cache_clear()
    import app.main as main
    importlib.reload(config_mod)
    importlib.reload(main)

    async def fake_get_openai_response(messages, config):
        return "resposta do teste"

    monkeypatch.setattr(main, "get_openai_response", fake_get_openai_response)

    client = TestClient(main.app)
    response = client.post(
        "/chat",
        json={"messages": [{"role": "user", "content": "Olá"}]},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["response"] == "resposta do teste"
    assert payload["model"] == "gpt-4-mini"
