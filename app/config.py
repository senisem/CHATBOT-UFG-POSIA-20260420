"""
Configurações da aplicação FastAPI.
Gerencia variáveis de ambiente e definições globais.
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação com validação Pydantic."""
    
    # Informações da API
    app_name: str = "Chatbot OpenAI API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4-mini"
    openai_temperature: float = 0.7
    openai_max_tokens: int | None = None
    openai_timeout: int = 30
    openai_max_retries: int = 3
    
    # Segurança (OWASP)
    secret_key: str  # Para JWT (se usar autenticação no futuro)
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    max_requests_per_minute: int = 60
    max_message_length: int = 10000  # Limite de caracteres por mensagem
    max_messages_per_request: int = 50  # Limite de mensagens por requisição
    
    # CORS
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["POST", "OPTIONS"]
    cors_allow_headers: list[str] = ["Content-Type", "Authorization"]
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        """Configuração de carregamento de variáveis."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def validate_configuration(self) -> None:
        """Valida a configuração na inicialização."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY não configurada")
        
        if not self.secret_key:
            raise ValueError("SECRET_KEY não configurada")
        
        if len(self.openai_api_key) < 20:
            raise ValueError("OPENAI_API_KEY inválida")
        
        if self.openai_temperature < 0.0 or self.openai_temperature > 2.0:
            raise ValueError("OPENAI_TEMPERATURE deve estar entre 0.0 e 2.0")


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna a instância única de Settings (singleton com cache).
    Valida a configuração na primeira chamada.
    """
    settings = Settings()
    settings.validate_configuration()
    return settings
