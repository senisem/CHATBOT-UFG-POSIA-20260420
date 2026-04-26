import os
import asyncio
import logging
from typing import Optional
from dataclasses import dataclass
from openai import AsyncOpenAI, APIError, APIConnectionError, RateLimitError, APIStatusError

# Importar utilitários RAG
from rag_utils import get_context_for_question

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class OpenAIConfig:
    """Configuração segura para cliente OpenAI."""
    api_key: str
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout: int = 30
    max_retries: int = 3
    
    @staticmethod
    def from_env() -> "OpenAIConfig":
        """Carrega configuração a partir de variáveis de ambiente."""
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            logger.error("OPENAI_API_KEY não configurada")
            raise ValueError("Variável de ambiente OPENAI_API_KEY é obrigatória")
        
        if len(api_key) < 20:
            logger.error("OPENAI_API_KEY inválida (comprimento insuficiente)")
            raise ValueError("Chave API inválida")
        
        return OpenAIConfig(
            api_key=api_key,
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "50000")) or None,
            timeout=int(os.getenv("OPENAI_TIMEOUT", "30")),
            max_retries=int(os.getenv("OPENAI_MAX_RETRIES", "3"))
        )


class OpenAIError(Exception):
    """Exceção base para erros do OpenAI."""
    pass


class OpenAIValidationError(OpenAIError):
    """Erro de validação de entrada."""
    pass


class OpenAIAPIError(OpenAIError):
    """Erro da API OpenAI."""
    pass


def validate_messages(messages: list[dict]) -> None:
    """
    Valida o formato das mensagens.
    
    Args:
        messages: Lista de mensagens a validar
        
    Raises:
        OpenAIValidationError: Se as mensagens forem inválidas
    """
    if not isinstance(messages, list) or not messages:
        raise OpenAIValidationError("Mensagens devem ser uma lista não vazia")
    
    for i, msg in enumerate(messages):
        if not isinstance(msg, dict):
            raise OpenAIValidationError(f"Mensagem {i} não é um dicionário")
        
        if "role" not in msg or "content" not in msg:
            raise OpenAIValidationError(
                f"Mensagem {i} não tem 'role' ou 'content'"
            )
        
        if msg["role"] not in ("system", "user", "assistant"):
            raise OpenAIValidationError(
                f"Role '{msg['role']}' inválido na mensagem {i}"
            )
        
        if not isinstance(msg["content"], str) or not msg["content"].strip():
            raise OpenAIValidationError(
                f"Conteúdo da mensagem {i} vazio ou inválido"
            )


async def get_openai_response(
    messages: list[dict],
    config: Optional[OpenAIConfig] = None
) -> Optional[str]:
    """
    Envia mensagens ao modelo GPT-4 Mini com retry automático.
    
    Args:
        messages: Lista de mensagens no formato OpenAI
                 [{"role": "user", "content": "..."}, ...]
        config: Configuração do cliente (carregada do env se não fornecida)
    
    Returns:
        String com a resposta do modelo ou None em caso de erro irreversível
        
    Raises:
        OpenAIValidationError: Se as mensagens forem inválidas
        OpenAIAPIError: Se houver erro na API após retries
    """
    # Validar entrada
    try:
        validate_messages(messages)
    except OpenAIValidationError as e:
        logger.error(f"Validação de mensagens falhou: {e}")
        raise
    
    # Carregar configuração
    if config is None:
        config = OpenAIConfig.from_env()
    
    # Validar parâmetros
    if not 0.0 <= config.temperature <= 2.0:
        raise OpenAIValidationError(
            f"Temperature deve estar entre 0.0 e 2.0, recebido {config.temperature}"
        )
    
   
    # ============================================================================
    # Integração RAG: Adicionar contexto do PDF
    # ============================================================================
    
    # Extrair a última mensagem do usuário para obter contexto
    user_messages = [msg for msg in messages if msg.get("role") == "user"]
    if user_messages:
        last_user_message = user_messages[-1]["content"]
        logger.debug(f"Obtendo contexto RAG para pergunta: {last_user_message[:100]}...")
        
        try:
            rag_context = get_context_for_question(last_user_message)
            if rag_context:
                # Criar system message com contexto do PDF
                system_message = {
                    "role": "system",
                    "content": f"Você é um assistente especializado em legislação CVM, especificamente na Resolução 175 consolidada.\n\nUse APENAS o seguinte contexto da Resolução 175 consolidada para responder às perguntas do usuário. Não use conhecimento externo ou generalizações:\n\n---\n{rag_context}\n---\n\nSe a pergunta não puder ser respondida com base neste contexto, informe que não possui informações suficientes sobre o assunto na Resolução 175."
                }
                
                # Inserir system message no início da lista de mensagens
                messages.insert(0, system_message)
                logger.info(f"Contexto RAG adicionado: {len(rag_context)} caracteres")
            else:
                logger.warning("Nenhum contexto relevante encontrado no PDF")
                # Mesmo sem contexto, adicionar instrução básica
                system_message = {
                    "role": "system", 
                    "content": "Você é um assistente especializado em legislação CVM. Use apenas informações da Resolução 175 consolidada para responder."
                }
                messages.insert(0, system_message)
                
        except Exception as e:
            logger.error(f"Erro ao obter contexto RAG: {e}")
            # Continuar sem contexto em caso de erro
            system_message = {
                "role": "system",
                "content": "Você é um assistente especializado em legislação CVM. Responda baseado na Resolução 175 consolidada."
            }
            messages.insert(0, system_message)

    client = AsyncOpenAI(
        api_key=config.api_key,
        timeout=config.timeout
    )

 
 #   client = AsyncOpenAI(
 #      api_key=config.api_key,
 #        timeout=config.timeout
 #   )

    # Retry loop com backoff exponencial
    for tentativa in range(config.max_retries):
        try:
            logger.debug(f"Requisição OpenAI - Tentativa {tentativa + 1}/{config.max_retries}")
            
            response = await client.chat.completions.create(
                model=config.model,
                messages=messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
            
            conteudo = response.choices[0].message.content
            logger.info("Resposta OpenAI obtida com sucesso")
            return conteudo
        
        except RateLimitError as e:
            espera = 2 ** tentativa  # Backoff exponencial: 1s, 2s, 4s
            
            if tentativa < config.max_retries - 1:
                logger.warning(
                    f"Rate limit excedido. Aguardando {espera}s antes de retry..."
                )
                await asyncio.sleep(espera)
            else:
                logger.error("Rate limit excedido. Máximo de retries atingido.")
                raise OpenAIAPIError(
                    "Limite de requisições excedido. Tente novamente mais tarde."
                ) from e
        
        except APIConnectionError as e:
            if tentativa < config.max_retries - 1:
                espera = 2 ** tentativa
                logger.warning(
                    f"Conexão falhou. Aguardando {espera}s antes de retry..."
                )
                await asyncio.sleep(espera)
            else:
                logger.error("Falha de conexão persistente com a API")
                raise OpenAIAPIError(
                    "Impossível conectar à API OpenAI."
                ) from e
        
        except APIStatusError as e:
            # Erros de status não recuperáveis
            logger.error(f"Erro HTTP da API: {e.status_code}")
            raise OpenAIAPIError(
                f"Erro da API OpenAI: Status {e.status_code}"
            ) from e
        
        except APIError as e:
            # Erro genérico da API
            logger.error(f"Erro da API OpenAI: {type(e).__name__}")
            raise OpenAIAPIError(
                "Erro na requisição para a API OpenAI."
            ) from e
        
        except Exception as e:
            # Erro inesperado
            logger.error(f"Erro inesperado: {type(e).__name__}")
            raise OpenAIAPIError(
                "Erro inesperado ao processar requisição."
            ) from e


# Exemplo de uso:
if __name__ == "__main__":
    async def main():
        try:
            config = OpenAIConfig.from_env()
            
            messages = [
                {
                    "role": "system",
                    "content": "Você é um assistente útil especializado em responder dúvidas."
                },
                {
                    "role": "user",
                    "content": "Explique brevemente o que é machine learning."
                }
            ]
            
            resposta = await get_openai_response(messages, config)
            
            if resposta:
                print(f"\n✓ Resposta:\n{resposta}")
            
        except OpenAIValidationError as e:
            print(f"❌ Erro de validação: {e}")
        except OpenAIAPIError as e:
            print(f"❌ Erro da API: {e}")
        except ValueError as e:
            print(f"❌ Erro de configuração: {e}")
    
    asyncio.run(main())