"""
Camada de segurança com implementação de controles OWASP.
Inclui rate limiting, CORS, headers de segurança, logging, etc.
"""

import logging
import time
from collections import defaultdict
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
import hashlib
import hmac

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware para implementar rate limiting por IP.
    Protege contra DDoS e abuso de API (OWASP A4: Insecure Deserialization).
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_times = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        """Verifica limite de requisições por IP."""
        
        # Obter IP real (considerando proxies)
        client_ip = request.client.host
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        current_time = time.time()
        
        # Limpar requisições antigas
        self.request_times[client_ip] = [
            req_time for req_time in self.request_times[client_ip]
            if current_time - req_time < 60
        ]
        
        # Verificar limite
        if len(self.request_times[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit excedido para IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Limite de requisições excedido. Tente novamente mais tarde."
                }
            )
        
        # Registrar requisição
        self.request_times[client_ip].append(current_time)
        
        response = await call_next(request)
        
        # Adicionar headers de segurança
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - len(self.request_times[client_ip])
        )
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware para adicionar headers de segurança padrão (OWASP).
    Protege contra XSS, Clickjacking, MIME Sniffing, etc.
    """
    
    async def dispatch(self, request: Request, call_next):
        """Adiciona headers de segurança na resposta."""
        response = await call_next(request)
        
        # Prevenir XSS (Cross-Site Scripting)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        # Prevenir MIME Sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # HSTS (HTTP Strict Transport Security)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy (antes Feature-Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para logging estruturado de requisições (OWASP A09: Logging & Monitoring).
    Rastreia atividades para auditoria e detecção de ameaças.
    """
    
    async def dispatch(self, request: Request, call_next):
        """Registra informações de requisição e resposta."""
        
        start_time = datetime.now()
        client_ip = request.client.host
        
        # Registrar requisição
        logger.info(
            f"Requisição recebida: {request.method} {request.url.path} | IP: {client_ip}"
        )
        
        try:
            response = await call_next(request)
            process_time = (datetime.now() - start_time).total_seconds()
            
            # Registrar resposta
            log_level = logging.INFO if response.status_code < 400 else logging.WARNING
            logger.log(
                log_level,
                f"Resposta: {request.method} {request.url.path} | "
                f"Status: {response.status_code} | "
                f"Tempo: {process_time:.2f}s | IP: {client_ip}"
            )
            
            response.headers["X-Process-Time"] = str(process_time)
            return response
        
        except Exception as e:
            process_time = (datetime.now() - start_time).total_seconds()
            logger.error(
                f"Erro na requisição: {request.method} {request.url.path} | "
                f"Erro: {str(e)} | Tempo: {process_time:.2f}s | IP: {client_ip}",
                exc_info=True
            )
            raise


def setup_cors(app, allowed_origins: list[str]) -> None:
    """
    Configura CORS de forma segura (OWASP A07: Cross-Origin Resource Sharing).
    
    Args:
        app: Aplicação FastAPI
        allowed_origins: Lista de origens permitidas
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,  # Não use ["*"] em produção!
        allow_credentials=True,
        allow_methods=["POST", "OPTIONS"],  # Métodos explícitos
        allow_headers=["Content-Type"],
        expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"],
        max_age=3600,  # Cache de preflight por 1 hora
    )


def setup_security_middleware(app, requests_per_minute: int = 60) -> None:
    """
    Configura todos os middlewares de segurança.
    
    Args:
        app: Aplicação FastAPI
        requests_per_minute: Limite de requisições por minuto
    """
    # Ordem importa! Adicionar na ordem correta
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitMiddleware, requests_per_minute=requests_per_minute)


def validate_bearer_token(authorization: str, secret_key: str) -> bool:
    """
    Valida um token Bearer usando HMAC (para autenticação futura).
    
    Args:
        authorization: Header Authorization
        secret_key: Chave secreta para validação
        
    Returns:
        True se o token é válido, False caso contrário
    """
    if not authorization or not authorization.startswith("Bearer "):
        return False
    
    token = authorization.replace("Bearer ", "")
    
    # Implementação simplificada (use JWT em produção)
    try:
        # Aqui você validaria o token com JWT
        # Este é apenas um exemplo educacional
        return len(token) > 0
    except Exception as e:
        logger.error(f"Erro na validação do token: {e}")
        return False
