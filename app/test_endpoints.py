"""
Script para testar os endpoints da API Chatbot
Execute este script enquanto o servidor estiver rodando (uvicorn app.main:app)
"""

import httpx
import asyncio
import json


async def test_health_endpoint():
    """Testa o endpoint /health"""
    print("\n" + "="*60)
    print("🧪 TESTE 1: Health Check")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://127.0.0.1:8000/health")
            print(f"✅ Status Code: {response.status_code}")
            print(f"📦 Resposta:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return True
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False


async def test_chat_endpoint():
    """Testa o endpoint /chat"""
    print("\n" + "="*60)
    print("🧪 TESTE 2: Chat Endpoint")
    print("="*60)
    
    # Preparar mensagens
    messages = [
        {
            "role": "system",
            "content": "Você é um assistente útil que ajuda com informações sobre Resoluções"
        },
        {
            "role": "user",
            "content": "Qual é o propósito da Resolução 175?"
        }
    ]
    
    payload = {
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    print(f"\n📨 Requisição enviada:")
    print(f"   - Número de mensagens: {len(messages)}")
    print(f"   - Última mensagem: {messages[-1]['content'][:50]}...")
    print(f"   - Temperatura: {payload['temperature']}")
    
    async with httpx.AsyncClient(timeout=60) as client:
        try:
            response = await client.post(
                "http://127.0.0.1:8000/chat",
                json=payload
            )
            print(f"\n✅ Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n📦 Resposta:")
                print(f"   - Modelo: {data.get('model')}")
                print(f"   - Resposta (primeiros 200 caracteres):\n")
                print(f"   {data.get('response', '')[:200]}...\n")
                print(f"   - Metadados: {json.dumps(data.get('usage', {}), indent=2, ensure_ascii=False)}")
                return True
            else:
                print(f"❌ Erro HTTP: {response.json()}")
                return False
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False


async def main():
    """Executa todos os testes"""
    print("\n🚀 Iniciando testes da API Chatbot")
    print("🌐 Servidor: http://127.0.0.1:8000")
    
    # Teste 1: Health Check
    health_ok = await test_health_endpoint()
    
    # Teste 2: Chat
    chat_ok = await test_chat_endpoint()
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    print(f"✅ Health Check: {'PASSOU ✓' if health_ok else 'FALHOU ✗'}")
    print(f"✅ Chat Endpoint: {'PASSOU ✓' if chat_ok else 'FALHOU ✗'}")
    
    if health_ok and chat_ok:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique se o servidor está rodando.")


if __name__ == "__main__":
    asyncio.run(main())
