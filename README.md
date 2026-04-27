# 🤖 Chatbot API - UFG POSIA

Uma API FastAPI robusta para chatbot com integração OpenAI e RAG (Retrieval-Augmented Generation), especializada em legislação da Comissão de Valores Mobiliários (CVM) - Resolução 175 consolidada.

## 📋 Visão Geral

Este projeto implementa um chatbot inteligente que responde perguntas fundamentadas exclusivamente no conteúdo da Resolução 175 consolidada da CVM. Utiliza técnicas de RAG para extrair contexto relevante de um PDF oficial e enriquecer os prompts enviados à API OpenAI.

### 🏗️ Arquitetura

```
Frontend (Streamlit/Gradio)
    ↓ HTTP/JSON
FastAPI Backend
    ↓
Controller → Service → Repository (RAG/PDF)
    ↓
OpenAI API + Base de Conhecimento (PDF)
```

## 🚀 Instalação Rápida

### Pré-requisitos
- Python 3.9+
- Chave API OpenAI

### Passos
1. **Clone o repositório:**
   ```bash
   git clone https://github.com/senisem/CHATBOT-UFG-POSIA-20260420.git
   cd CHATBOT-UFG-POSIA-20260420
   ```

2. **Configure o ambiente:**
   ```bash
   python -m venv venv_new
   venv_new\Scripts\activate  # Windows
   # source venv_new/bin/activate  # macOS/Linux
   ```

3. **Instale dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure variáveis de ambiente:**
   ```bash
   cp .env.example .env
   # Edite .env com sua OPENAI_API_KEY
   ```

5. **Execute a API:**
   ```bash
   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

## 📖 Uso Rápido

### Health Check
```bash
curl http://127.0.0.1:8000/health
```

### Chat com o Bot
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Qual é o propósito da Resolução 175?"}
    ],
    "temperature": 0.7
  }'
```

### Documentação Interativa
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

## 📚 Documentação

### 📖 Guias
- **[Guia para Iniciantes](DOCs/guides/GUIA_INICIANTES.md)** - Tutorial passo a passo para usar a API
- **[Documentação da API](DOCs/API.md)** - Referência completa dos endpoints, configurações e segurança

### 🏛️ Arquitetura
- **[Arquitetura Detalhada](DOCs/architecture/ARQUITETURA_API.md)** - Explicação técnica dos componentes e fluxos
- **[Diagrama de Componentes](DOCs/architecture/diagrama_componentes.puml)** - Diagrama C4 da arquitetura

### 📝 Desenvolvimento
- **[Changelog](DOCs/dev-logs/CHANGELOG.md)** - Histórico de mudanças e desenvolvimento

## 🔒 Segurança

Implementa controles OWASP:
- Rate limiting (60 req/min por IP)
- Validação rigorosa de entrada (Pydantic)
- Headers de segurança HTTP
- Logging estruturado
- CORS configurado

## 🧪 Testes

```bash
# Executar todos os testes
python -m pytest tests/

# Com cobertura
pytest --cov=app
```

**Status atual:** ✅ 29 testes passando

## 🐳 Docker

```bash
# Build
docker build -t chatbot-api .

# Run
docker run -p 8000:8000 --env-file .env chatbot-api
```

## 📦 Tecnologias

- **Backend:** FastAPI, Pydantic
- **IA:** OpenAI API, RAG com PyMuPDF
- **Segurança:** OWASP compliant
- **Testes:** pytest, httpx
- **Documentação:** Swagger/OpenAPI

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

MIT License

## 👨‍🎓 Projeto Acadêmico

Desenvolvido para a disciplina POSIA da UFG (Universidade Federal de Goiás).

---

**Desenvolvido com ❤️ para o projeto Chatbot UFG POSIA**