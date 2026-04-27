"""
Script para demonstrar a estrutura e fluxo completo do sistema
(sem necessidade de chave OpenAI válida)
"""

import json
import sys
sys.path.insert(0, r'C:\Users\Win11\OneDrive\Documents\Projetos\chatbot')

from app.models import Message, ChatRequest, ChatResponse, HealthResponse, ErrorResponse
from app.config import get_settings
from .rag_utils import extract_text_from_pdf, split_text_into_chunks, find_relevant_chunks
import os


def test_config():
    """Testa carregamento de configurações"""
    print("\n" + "="*60)
    print("🧪 TESTE 1: Configurações (Config)")
    print("="*60)
    
    try:
        settings = get_settings()
        print(f"✅ Configurações carregadas:")
        print(f"   - App Name: {settings.app_name}")
        print(f"   - Version: {settings.app_version}")
        print(f"   - Debug: {settings.debug}")
        print(f"   - Model: {settings.openai_model}")
        print(f"   - Temperature: {settings.openai_temperature}")
        print(f"   - Max Requests/min: {settings.max_requests_per_minute}")
        print(f"   - API Key configurada: {'✓' if settings.openai_api_key else '✗'}")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_models():
    """Testa validação de modelos Pydantic"""
    print("\n" + "="*60)
    print("🧪 TESTE 2: Validação de Modelos (Models)")
    print("="*60)
    
    try:
        # Testar Message
        msg = Message(role="user", content="Olá!")
        print(f"✅ Message válida criada")
        
        # Testar ChatRequest
        request = ChatRequest(
            messages=[msg],
            temperature=0.7
        )
        print(f"✅ ChatRequest válida criada")
        print(f"   - Mensagens: {len(request.messages)}")
        print(f"   - Temperature: {request.temperature}")
        
        # Testar validações
        try:
            invalid_msg = Message(role="invalid", content="test")
            print(f"❌ Deveria ter falhado - role inválido")
            return False
        except Exception:
            print(f"✅ Validação de role funcionou")
        
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_rag_system():
    """Testa sistema RAG de extração do PDF"""
    print("\n" + "="*60)
    print("🧪 TESTE 3: Sistema RAG (PDF Extraction)")
    print("="*60)
    
    try:
        pdf_path = r'C:\Users\Win11\OneDrive\Documents\Projetos\chatbot\resol175consolid.pdf'
        
        # Verificar se arquivo existe
        if not os.path.exists(pdf_path):
            print(f"❌ Arquivo PDF não encontrado: {pdf_path}")
            return False
        
        print(f"✅ Arquivo PDF encontrado")
        
        # Extrair texto
        text = extract_text_from_pdf(pdf_path)
        print(f"✅ Texto extraído: {len(text)} caracteres")
        print(f"   Primeiros 100 caracteres: {text[:100]}...")
        
        # Dividir em chunks
        chunks = split_text_into_chunks(text, chunk_size=1500, overlap=200)
        print(f"✅ Texto dividido em {len(chunks)} chunks")
        
        # Buscar chunks relevantes
        question = "Resolução 175 CVM"
        relevant = find_relevant_chunks(question, chunks, top_k=3)
        print(f"✅ Chunks relevantes encontrados: {len(relevant)}")
        if relevant:
            print(f"   Primeiro chunk tem {len(relevant[0])} caracteres")
        
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_security():
    """Testa módulo de segurança"""
    print("\n" + "="*60)
    print("🧪 TESTE 4: Segurança (Security)")
    print("="*60)
    
    try:
        from app.security import RateLimitMiddleware, SecurityHeadersMiddleware
        
        print(f"✅ RateLimitMiddleware importado")
        print(f"✅ SecurityHeadersMiddleware importado")
        
        # Verificar middleware
        settings = get_settings()
        rate_limit = RateLimitMiddleware(None, settings.max_requests_per_minute)
        print(f"✅ Rate Limiter criado: {settings.max_requests_per_minute} req/min")
        
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_openai_module():
    """Testa módulo OpenAI sem chamar a API"""
    print("\n" + "="*60)
    print("🧪 TESTE 5: Módulo OpenAI (Structure)")
    print("="*60)
    
    try:
        from get_openai_response import (
            OpenAIConfig, 
            OpenAIError,
            OpenAIValidationError,
            validate_messages
        )
        
        print(f"✅ OpenAIConfig importado")
        print(f"✅ Exceções importadas")
        
        # Testar validação de mensagens
        valid_messages = [
            {"role": "user", "content": "Olá"}
        ]
        validate_messages(valid_messages)
        print(f"✅ Validação de mensagens funciona")
        
        # Testar criação de config
        config = OpenAIConfig(
            api_key="sk-test-key",
            model="gpt-4-mini"
        )
        print(f"✅ OpenAIConfig criado: {config.model}")
        
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa todos os testes de estrutura"""
    print("\n🚀 TESTE COMPLETO DE ESTRUTURA DO SISTEMA CHATBOT")
    print("🔍 Validando: Configurações, Modelos, RAG, Segurança, OpenAI")
    
    results = {
        "Configurações": test_config(),
        "Modelos": test_models(),
        "Sistema RAG": test_rag_system(),
        "Segurança": test_security(),
        "Módulo OpenAI": test_openai_module(),
    }
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    for name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {name}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    print(f"\n📈 Total: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 EXCELENTE! Toda a estrutura do sistema está funcionando!")
        print("\n⚠️ Nota: O erro 404 da OpenAI indica que a chave API pode estar:")
        print("   - Vencida ou inválida")
        print("   - Sem créditos disponíveis")
        print("   - Não autorizada para o modelo gpt-4-mini")
        print("\n💡 Para resolver:")
        print("   1. Acesse https://platform.openai.com/account/api-keys")
        print("   2. Gere uma nova chave API")
        print("   3. Atualize o .env com OPENAI_API_KEY=sua_nova_chave")
        print("   4. Reinicie o servidor")
    else:
        print(f"\n⚠️ {total - passed} teste(s) falharam. Verifique os erros acima.")


if __name__ == "__main__":
    main()
