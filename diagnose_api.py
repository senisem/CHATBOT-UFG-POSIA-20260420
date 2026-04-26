"""
Script de diagnóstico para testar a chave OpenAI API
"""

import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI, APIError

# Carregar variáveis de ambiente
load_dotenv()

async def test_api_key():
    """Testa a chave API da OpenAI"""
    print("\n" + "="*60)
    print("🧪 DIAGNÓSTICO DA CHAVE OPENAI API")
    print("="*60)
    
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4-mini")
    
    if not api_key:
        print("❌ OPENAI_API_KEY não configurada no .env")
        return False
    
    print(f"\n📋 Informações:")
    print(f"   - Chave configurada: {api_key[:20]}...{api_key[-10:]}")
    print(f"   - Modelo: {model}")
    print(f"   - Comprimento da chave: {len(api_key)} caracteres")
    
    # Verificar formato da chave
    if not api_key.startswith("sk-"):
        print(f"❌ Formato de chave inválido (deve começar com 'sk-')")
        return False
    
    print(f"✅ Formato de chave válido")
    
    # Testar conexão
    print(f"\n🔗 Testando conexão com OpenAI...")
    client = AsyncOpenAI(api_key=api_key, timeout=30)
    
    try:
        # Tentar listar modelos (requisição simples)
        print(f"   Listando modelos disponíveis...")
        models = await client.models.list()
        print(f"✅ Conexão bem-sucedida!")
        print(f"   Modelos disponíveis: {len(models.data)} encontrados")
        
        # Procurar pelos modelos mais comuns
        model_names = [m.id for m in models.data[:10]]
        print(f"   Primeiros modelos: {model_names}")
        
        # Verificar se o modelo solicitado existe
        all_models = [m.id for m in models.data]
        if model in all_models:
            print(f"✅ Modelo '{model}' disponível")
        else:
            print(f"⚠️ Modelo '{model}' NÃO encontrado na sua conta")
            print(f"   Modelos disponíveis que contêm 'gpt': {[m for m in all_models if 'gpt' in m][:5]}")
            
            # Sugerir um modelo alternativo
            gpt_models = [m for m in all_models if 'gpt' in m and 'mini' in m]
            if not gpt_models:
                gpt_models = [m for m in all_models if 'gpt' in m][:1]
            
            if gpt_models:
                print(f"\n💡 Sugestão: Use o modelo '{gpt_models[0]}'")
        
        return True
        
    except APIError as e:
        error_code = getattr(e, 'status_code', None)
        print(f"❌ Erro da API OpenAI: {e}")
        print(f"   Status Code: {error_code}")
        
        if error_code == 401:
            print(f"   → Chave API inválida ou expirada")
        elif error_code == 403:
            print(f"   → Acesso negado (verificar permissões da chave)")
        elif error_code == 404:
            print(f"   → Recurso não encontrado (pode ser o modelo)")
        elif error_code == 429:
            print(f"   → Limite de requisições excedido")
        else:
            print(f"   → Erro desconhecido")
        
        return False
        
    except Exception as e:
        print(f"❌ Erro: {type(e).__name__}: {e}")
        return False


async def test_chat_completion():
    """Testa um chat completion simples"""
    print("\n" + "="*60)
    print("💬 TESTE DE CHAT COMPLETION")
    print("="*60)
    
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4-mini")
    
    if not api_key:
        print("❌ Chave não configurada")
        return False
    
    client = AsyncOpenAI(api_key=api_key, timeout=60)
    
    try:
        print(f"📨 Enviando requisição para '{model}'...")
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": "Olá! Teste rápido."}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        print(f"✅ Resposta recebida com sucesso!")
        print(f"   Modelo usado: {response.model}")
        print(f"   Tokens usados: {response.usage.total_tokens}")
        print(f"   Resposta: {response.choices[0].message.content}")
        
        return True
        
    except APIError as e:
        error_code = getattr(e, 'status_code', None)
        print(f"❌ Erro: {e}")
        
        if error_code == 404:
            print(f"💡 Tente mudar o modelo em .env:")
            print(f"   OPENAI_MODEL=gpt-3.5-turbo  (modelo mais econômico)")
            print(f"   ou")
            print(f"   OPENAI_MODEL=gpt-4  (modelo mais poderoso)")
        
        return False


async def main():
    print("\n🚀 INICIANDO DIAGNÓSTICO")
    
    # Teste 1: Validar chave
    key_ok = await test_api_key()
    
    if not key_ok:
        print("\n⚠️ Problema detectado com a chave API")
        return
    
    # Teste 2: Chat completion
    chat_ok = await test_chat_completion()
    
    print("\n" + "="*60)
    print("📊 DIAGNÓSTICO COMPLETO")
    print("="*60)
    
    if key_ok and chat_ok:
        print("✅ TUDO FUNCIONANDO!")
        print("Você pode testar a API completa agora.")
    else:
        print("⚠️ Há problemas a resolver")
        print("\n💡 PRÓXIMOS PASSOS:")
        print("1. Verifique sua conta em https://platform.openai.com")
        print("2. Confirme se tem créditos disponíveis")
        print("3. Tente gerar uma nova chave em https://platform.openai.com/account/api-keys")
        print("4. Atualize o .env com a nova chave")
        print("5. Reinicie o servidor FastAPI")


if __name__ == "__main__":
    asyncio.run(main())
