"""
Modelos Pydantic para validação de entrada e saída da API.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class Message(BaseModel):
    """Modelo para uma mensagem individual no formato OpenAI."""
    
    role: str = Field(
        ...,
        description="Papel da mensagem: 'system', 'user' ou 'assistant'"
    )
    content: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Conteúdo da mensagem"
    )
    
    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Valida se o role é um dos permitidos."""
        allowed_roles = ("system", "user", "assistant")
        if v not in allowed_roles:
            raise ValueError(f"Role deve ser um de {allowed_roles}")
        return v
    
    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Valida se o conteúdo não é apenas espaços em branco."""
        if not v.strip():
            raise ValueError("Conteúdo não pode ser apenas espaços em branco")
        return v


class ChatRequest(BaseModel):
    """Modelo para requisição de chat."""
    
    messages: list[Message] = Field(
        ...,
        min_items=1,
        max_items=50,
        description="Lista de mensagens (máximo 50)"
    )
    temperature: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Controla criatividade da resposta (0.0 a 2.0)"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        ge=1,
        le=4096,
        description="Limite de tokens na resposta"
    )
    
    @field_validator("messages")
    @classmethod
    def validate_messages_format(cls, v: list) -> list:
        """Valida se pelo menos uma mensagem é do usuário."""
        if not any(msg.role == "user" for msg in v):
            raise ValueError("Deve haver pelo menos uma mensagem com role='user'")
        return v


class ChatResponse(BaseModel):
    """Modelo para resposta de chat."""
    
    response: str = Field(..., description="Resposta do modelo OpenAI")
    model: str = Field(..., description="Modelo utilizado")
    usage: Optional[dict] = Field(
        default=None,
        description="Informações de uso de tokens"
    )


class ErrorResponse(BaseModel):
    """Modelo para resposta de erro."""
    
    status_code: int = Field(..., description="Código HTTP do erro")
    message: str = Field(..., description="Mensagem de erro legível")
    error_type: str = Field(..., description="Tipo do erro")
    detail: Optional[str] = Field(
        default=None,
        description="Detalhes adicionais do erro"
    )


class HealthResponse(BaseModel):
    """Modelo para resposta de health check."""
    
    status: str = Field(..., description="Status da API")
    version: str = Field(..., description="Versão da API")
    openai_configured: bool = Field(..., description="Se OpenAI está configurado")
