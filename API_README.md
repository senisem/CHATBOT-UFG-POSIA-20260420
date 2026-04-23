# Chatbot API - Backend FastAPI

API backend para um chatbot com integração OpenAI, implementada com **FastAPI** e segurança baseada em **OWASP**.

## 🏗️ Arquitetura

A API segue a arquitetura C4 especificada no `diagrama_componentes.puml`:

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Streamlit/Gradio)             │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/JSON
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                            │
│  ┌─────────────┐  ┌──────────┐  ┌────────────────────────┐  │
│  │ Controller  │→ │ Service  │→ │ Repository (RAG/PDF)  │  │
│  └─────────────┘  └──────────┘  └────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
   OpenAI API      Arquivo PDF      Cache/DB
```

## 🔒 Segurança (OWASP)

- **A01 - Broken Access Control**: Rate limiting por IP (60 req/min)
- **A03 - Injection**: Validação Pydantic em todas as entradas
- **A04 - Insecure Deserialization**: Serialização segura com Pydantic
- **A07 - CORS**: Configuração restritiva de CORS
- **A09 - Logging & Monitoring**: Logging estruturado de todas as requisições
- **Headers de Segurança**: XSS Protection, Clickjacking Prevention, MIME Sniffing
- **Variáveis de Ambiente**: Chaves API isoladas em .env

## 📋 Estrutura de Arquivos

```
chatbot/
├── app/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # FastAPI application
│   ├── config.py             # Configuration management
│   ├── models.py             # Pydantic models
│   ├── security.py           # OWASP security middleware
│   └── __pycache__/
├── .env.example              # Example environment variables
├── requirements.txt          # Python dependencies
├── get_openai_response.py    # OpenAI integration
├── diagrama_componentes.puml # Architecture diagram
└── README.md                 # This file
```

## 🚀 Getting Started

### Pré-requisitos

- Python 3.9+
- pip ou poetry
- Chave API OpenAI

### 1. Clone ou configure o projeto

```bash
cd chatbot
```

### 2. Crie um ambiente virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite .env com suas configurações
# Pelo menos defina: OPENAI_API_KEY
```

**Variáveis obrigatórias:**
```env
OPENAI_API_KEY=sk-...
SECRET_KEY=sua-chave-secreta-aqui
```

### 5. Execute a API

```bash
# Desenvolvimento com hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Produção
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

A API estará disponível em: `http://localhost:8000`

## 📚 Documentação Interativa

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API Endpoints

### 1. Health Check

```bash
GET /health
```

**Resposta (200):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "openai_configured": true
}
```

### 2. Chat Endpoint

```bash
POST /chat
Content-Type: application/json

{
  "messages": [
    {
      "role": "system",
      "content": "Você é um assistente útil especializado em legislação."
    },
    {
      "role": "user",
      "content": "Qual é a CVM 175?"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 500
}
```

**Resposta (200):**
```json
{
  "response": "CVM 175 é uma instrução da Comissão de Valores Mobiliários...",
  "model": "gpt-4-mini",
  "usage": {
    "model": "gpt-4-mini",
    "timestamp": "2026-04-22T10:30:00",
    "temperature": 0.7,
    "max_tokens": 500
  }
}
```

**Erro Rate Limit (429):**
```json
{
  "detail": "Limite de requisições excedido. Tente novamente mais tarde."
}
```

## 🛡️ Tratamento de Erros

A API implementa tratamento robusto de erros:

| Status | Erro | Cenário |
|--------|------|---------|
| 400 | Bad Request | Mensagens inválidas, parâmetros fora do range |
| 429 | Too Many Requests | Rate limit excedido |
| 503 | Service Unavailable | OpenAI indisponível, conexão falhou |
| 500 | Internal Server Error | Erro inesperado |

## 🔐 Middleware de Segurança

### RateLimitMiddleware
- Limita requisições por IP
- Configurável via `MAX_REQUESTS_PER_MINUTE`
- Retorna `X-RateLimit-*` headers

### SecurityHeadersMiddleware
Adiciona headers:
- `X-Content-Type-Options: nosniff` (MIME Sniffing)
- `X-Frame-Options: DENY` (Clickjacking)
- `Content-Security-Policy` (XSS)
- `Strict-Transport-Security` (HTTPS)

### RequestLoggingMiddleware
- Registra todas as requisições
- Tempo de processamento
- IP do cliente
- Status da resposta

## 📝 Logging

Os logs incluem:

```
2026-04-22 10:30:00 - app.security - INFO - Requisição recebida: POST /chat | IP: 192.168.1.1
2026-04-22 10:30:01 - app.main - DEBUG - Chamando OpenAI com modelo: gpt-4-mini
2026-04-22 10:30:05 - app.security - INFO - Resposta: POST /chat | Status: 200 | Tempo: 4.23s | IP: 192.168.1.1
```

## 🧪 Testing

```bash
# Executar testes
pytest

# Com cobertura
pytest --cov=app

# Modo verbose
pytest -v
```

## 📦 Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build:
```bash
docker build -t chatbot-api .
docker run -p 8000:8000 --env-file .env chatbot-api
```

### Ambiente de Produção

1. Use `DEBUG=false`
2. Configure `ALLOWED_ORIGINS` com domínios reais
3. Use HTTPS (Certbot/Let's Encrypt)
4. Configure um reverse proxy (Nginx/Apache)
5. Use um banco de dados para logs (PostgreSQL/MongoDB)
6. Configure monitoramento (Prometheus/Grafana)

## 🐛 Troubleshooting

**Erro: "OPENAI_API_KEY não configurada"**
- Verifique se o arquivo `.env` existe
- Verifique se `OPENAI_API_KEY` está definida
- Reinicie a aplicação após alterar .env

**Erro: "Rate limit excedido"**
- Aguarde 60 segundos
- Aumente `MAX_REQUESTS_PER_MINUTE` se necessário

**Erro: "Serviço OpenAI indisponível"**
- Verifique a conexão com a internet
- Verifique se a chave API é válida
- Verifique o status de OpenAI: https://status.openai.com

## 📚 Referências

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [OpenAI API](https://platform.openai.com/docs)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Pydantic Documentation](https://docs.pydantic.dev)

## 📄 Licença

MIT License

## 👥 Contribuições

Contribuições são bem-vindas! Por favor:

1. Faça um Fork
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

**Desenvolvido com ❤️ para o projeto Chatbot UFG POSIA**
