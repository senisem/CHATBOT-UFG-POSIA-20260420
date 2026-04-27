"""
Aplicação FastAPI principal para o Chatbot com integração OpenAI.
Backend que implementa o padrão de arquitetura especificado no diagrama de componentes.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

# Importações locais
from app.config import Settings, get_settings
from app.models import ChatRequest, ChatResponse, ErrorResponse, HealthResponse, Message
from app.security import (
    setup_cors,
    setup_security_middleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    RequestLoggingMiddleware
)

# Importar a função refatorada de OpenAI
from .get_openai_response import (
    get_openai_response,
    OpenAIConfig,
    OpenAIError,
    OpenAIValidationError,
    OpenAIAPIError
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Lifecycle Events
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação.
    - Startup: Validar configuração
    - Shutdown: Limpeza de recursos
    """
    # Startup
    logger.info("🚀 Iniciando Chatbot API")
    settings = get_settings()
    logger.info(f"Versão: {settings.app_version}")
    logger.info(f"Debug: {settings.debug}")
    logger.info(f"Modelo OpenAI: {settings.openai_model}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Encerrando Chatbot API")


# ============================================================================
# Inicialização da Aplicação
# ============================================================================

def create_app() -> FastAPI:
    """
    Factory function para criar a aplicação FastAPI com configurações.
    
    Returns:
        FastAPI: Aplicação configurada
    """
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="API Backend para Chatbot com integração OpenAI",
        debug=settings.debug,
        lifespan=lifespan,
    )
    
    # ========================================================================
    # Configurar CORS e Segurança (OWASP)
    # ========================================================================
    setup_cors(app, settings.allowed_origins)
    setup_security_middleware(app, settings.max_requests_per_minute)
    
    return app


# Criar instância da aplicação
app = create_app()
settings = get_settings()


# ============================================================================
# Exception Handlers (Tratamento de Erros)
# ============================================================================

@app.exception_handler(OpenAIValidationError)
async def openai_validation_error_handler(request, exc: OpenAIValidationError):
    """Handler para erros de validação do OpenAI."""
    logger.warning(f"Erro de validação: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            status_code=400,
            message="Erro de validação na requisição",
            error_type="VALIDATION_ERROR",
            detail=str(exc)
        ).model_dump()
    )


@app.exception_handler(OpenAIAPIError)
async def openai_api_error_handler(request, exc: OpenAIAPIError):
    """Handler para erros da API OpenAI."""
    logger.error(f"Erro da API OpenAI: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=ErrorResponse(
            status_code=503,
            message="Serviço OpenAI indisponível",
            error_type="SERVICE_UNAVAILABLE",
            detail="Não foi possível processar sua requisição. Tente novamente mais tarde."
        ).model_dump()
    )


@app.exception_handler(OpenAIError)
async def openai_error_handler(request, exc: OpenAIError):
    """Handler genérico para erros OpenAI."""
    logger.error(f"Erro OpenAI não esperado: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status_code=500,
            message="Erro interno do servidor",
            error_type="INTERNAL_ERROR",
            detail="Ocorreu um erro inesperado. Contate o administrador."
        ).model_dump()
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc: Exception):
    """Handler genérico para exceções não tratadas."""
    logger.error(f"Erro inesperado: {type(exc).__name__}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status_code=500,
            message="Erro interno do servidor",
            error_type="INTERNAL_ERROR",
            detail="Ocorreu um erro inesperado."
        ).model_dump()
    )


# ============================================================================
# Endpoints da API
# ============================================================================

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health Check",
    description="Verifica se a API está operacional e se OpenAI está configurado"
)
async def health_check() -> HealthResponse:
    """
    Endpoint de health check para monitoramento.
    Valida a conexão e configuração da API.
    """
    try:
        # Verificar se OpenAI está configurado
        openai_configured = bool(settings.openai_api_key)
        
        return HealthResponse(
            status="healthy",
            version=settings.app_version,
            openai_configured=openai_configured
        )
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço indisponível"
        )


@app.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    tags=["Chat"],
    summary="Enviar mensagem para o Chatbot",
    description="Processa uma mensagem de chat e retorna a resposta do modelo OpenAI",
    responses={
        200: {"description": "Resposta obtida com sucesso"},
        400: {"description": "Erro de validação na requisição"},
        429: {"description": "Limite de requisições excedido"},
        503: {"description": "Serviço OpenAI indisponível"}
    }
)
async def chat_endpoint(
    request: ChatRequest,
    settings: Settings = Depends(get_settings)
) -> ChatResponse:
    """
    Endpoint principal do chatbot.
    
    Recebe mensagens formatadas no padrão OpenAI, processa através
    do modelo GPT-4 Mini e retorna a resposta.
    
    Args:
        request: Requisição com lista de mensagens
        settings: Configurações injetadas
        
    Returns:
        ChatResponse: Resposta do modelo com detalhes de uso
        
    Raises:
        HTTPException: Em caso de erro na processamento
    """
    
    try:
        logger.info(
            f"Requisição de chat recebida com {len(request.messages)} mensagens"
        )
        
        # Converter mensagens Pydantic para dicionários
        messages_dict = [msg.model_dump() for msg in request.messages]
        
        # Criar configuração do OpenAI
        openai_config = OpenAIConfig(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=request.temperature or settings.openai_temperature,
            max_tokens=request.max_tokens or settings.openai_max_tokens,
            timeout=settings.openai_timeout,
            max_retries=settings.openai_max_retries
        )
        
        # Chamar função assíncrona de OpenAI
        logger.debug(f"Chamando OpenAI com modelo: {openai_config.model}")
        response_text = await get_openai_response(
            messages=messages_dict,
            config=openai_config
        )
        
        if not response_text:
            logger.error("OpenAI retornou resposta vazia")
            raise OpenAIAPIError("Resposta vazia do modelo")
        
        logger.info("Resposta OpenAI obtida com sucesso")
        
        return ChatResponse(
            response=response_text,
            model=settings.openai_model,
            usage={
                "model": settings.openai_model,
                "timestamp": str(__import__('datetime').datetime.now()),
                "temperature": request.temperature or settings.openai_temperature,
                "max_tokens": request.max_tokens or settings.openai_max_tokens
            }
        )
    
    except OpenAIValidationError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except OpenAIAPIError as e:
        logger.error(f"Erro da API OpenAI: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço OpenAI indisponível"
        )
    
    except Exception as e:
        logger.error(f"Erro inesperado no endpoint /chat: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


# ============================================================================
# Documentação OpenAPI Customizada
# ============================================================================

def custom_openapi():
    """Customiza a documentação OpenAPI."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Chatbot API",
        version="1.0.0",
        description="API Backend para Chatbot com integração OpenAI. "
                   "Implementa padrão de arquitetura C4 com segurança OWASP.",
        routes=app.routes,
    )
    
    # Adicionar informações de segurança
    openapi_schema["info"]["x-security"] = [
        "Rate Limiting: 60 requisições por minuto por IP",
        "Headers de Segurança: XSS, Clickjacking, MIME Sniffing",
        "CORS: Configurado para origens específicas",
        "Logging: Auditoria de todas as requisições"
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# ============================================================================
# Execution
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
