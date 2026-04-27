# 🎓 Guia Completo para Iniciantes - Como Usar a API Chatbot

Este guia ensina passo a passo como:
1. Abrir o terminal/console
2. Ativar o ambiente virtual
3. Iniciar o servidor da API
4. Fazer requisições aos endpoints

Leia TUDO com atenção! Cada passo é importante.

## PARTE 1: ABRIR O TERMINAL

### WINDOWS (PowerShell):

#### Opção A - Usando VS Code:
1. Abra VS Code
2. Pressione: `Ctrl + ` (Control + acento grave)
3. Um terminal deve aparecer na parte inferior
4. Você deve ver algo como:
   ```
   PS C:\Users\Win11\OneDrive\Documents\Projetos\chatbot>
   ```

#### Opção B - Usando Menu Windows:
1. Clique no ícone do Windows no canto inferior esquerdo
2. Digite: "PowerShell"
3. Clique em "Windows PowerShell" (o azul)
4. Uma janela preta deve abrir

#### Opção C - Usando Executar:
1. Pressione: `Win + R` (tecla Windows + R)
2. Digite: `powershell`
3. Pressione Enter
4. Uma janela preta deve abrir

### MAC/LINUX:
1. Pressione: `Cmd + Space` (Command + espaço)
2. Digite: `terminal`
3. Pressione Enter
4. Um terminal deve abrir

### O QUE É O TERMINAL?
É uma janela onde você digita comandos de texto para controlar o computador. Em vez de clicar com mouse, você escreve instruções.

---

## PARTE 2: NAVEGAR PARA A PASTA DO PROJETO

Agora você deve estar no terminal. Vamos ir para a pasta do projeto.

⚠️ **IMPORTANTE:** Substitua os caminhos se sua pasta estiver em local diferente!

### WINDOWS (PowerShell):
Digite este comando e pressione Enter:
```powershell
cd C:\Users\Win11\OneDrive\Documents\Projetos\chatbot
```

**Explicação:**
- `cd` = "change directory" (mudar pasta)
- `C:\Users\...` = o caminho até a pasta chatbot

Depois de pressionar Enter, você deve ver:
```
PS C:\Users\Win11\OneDrive\Documents\Projetos\chatbot>
```

Se vir isso, **PERFEITO!** ✓ Você está na pasta certa.

### MAC/LINUX:
Digite:
```bash
cd ~/Documents/Projetos/chatbot
```
*(Note: Use `/` em vez de `\\` no Mac/Linux)*

### ❌ SE VOCÊ VIR UM ERRO:
**Erro comum:** "O caminho não foi encontrado"

**Solução:**
1. No seu computador, abra a pasta chatbot
2. Na barra de endereço, copie o caminho completo
3. No terminal, digite: `cd [cole o caminho aqui]`
4. Pressione Enter

---

## PARTE 3: ATIVAR O AMBIENTE VIRTUAL (venv)

⚠️ **MUITO IMPORTANTE:** Você **DEVE** ativar o ambiente virtual antes de continuar!

### O que é ambiente virtual?
É uma "bolha" isolada no seu computador onde instalamos as dependências Python. Pense como um "mini computador dentro do computador" com suas próprias bibliotecas.

### Por que fazer isso?
Se você tem vários projetos Python, cada um pode ter versões diferentes das mesmas bibliotecas. O ambiente virtual evita conflitos entre eles.

### WINDOWS (PowerShell):
Copie e cole este comando:
```powershell
venv_new\Scripts\Activate.ps1
```

Ou se você quiser ativar o `.venv` (ambiente anterior):
```powershell
.venv\Scripts\Activate.ps1
```

Depois de pressionar Enter, você deve ver no início da linha:
```
(venv_new) PS C:\Users\Win11\...
```

Viu "(venv_new)"? **PERFEITO!** ✓ O ambiente está ativado!

Se aparecer um erro sobre ExecutionPolicy:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```
Cole este comando acima, depois tente ativar novamente.

### MAC/LINUX:
Digite:
```bash
source venv_new/bin/activate
```

Você deve ver:
```
(venv_new) $
```

---

## PARTE 4: INICIAR O SERVIDOR DA API (Uvicorn)

⚠️ **Pré-requisito:** Você **DEVE** ter ativado o ambiente virtual (veja Parte 3)

Agora vamos iniciar o servidor FastAPI.

### WINDOWS:
Copie este comando inteiro e cole no terminal:
```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Explicação de cada parte:**
- `python` = executar Python
- `-m uvicorn` = com o módulo uvicorn
- `app.main:app` = arquivo: `app/main.py`, variável: `app`
- `--reload` = reiniciar servidor quando detectar mudanças
- `--host 127.0.0.1` = servidor disponível em localhost
- `--port 8000` = na porta 8000

### MAC/LINUX:
Digite:
```bash
python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
*(Use `python3` em vez de `python`)*

### O QUE VOCÊ DEVE VER NO TERMINAL:
Se tudo funcionou, você verá algo assim:
```
INFO:     Will watch for changes in these directories: [...]
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

✓ Se vir isso: **O SERVIDOR ESTÁ RODANDO!** 🎉

✗ Se vir erro vermelho: Veja a seção "SOLUÇÃO DE PROBLEMAS" no final

⚠️ **NÃO** feche este terminal! O servidor precisa continuar rodando.

### PRÓXIMO PASSO: Abra OUTRO TERMINAL
Você vai deixar este terminal aberto (onde o servidor está rodando). Abra **UM NOVO** terminal para fazer as requisições à API.

Então você terá:
- **Terminal 1:** [servidor rodando - NÃO FECHA]
- **Terminal 2:** [novo - onde você vai fazer requisições]

---

## PARTE 5: FAZER REQUISIÇÕES AOS ENDPOINTS

Agora vamos fazer requisições à API em um **NOVO** terminal.

⚠️ **Lembre-se:** O primeiro terminal (com o servidor) deve continuar rodando!

### ▼▼▼ OPÇÃO A: USANDO CURL (LINHA DE COMANDO) ▼▼▼

#### O que é CURL?
É uma ferramenta de linha de comando que permite fazer requisições HTTP. (HTTP = a linguagem que navegadores usam para falar com servidores)

**Vantagem:** Não precisa instalar nada extra  
**Desvantagem:** Mais complicado de ler

#### TESTE 1: Health Check (endpoint /health)

##### WINDOWS:
Copie e cole este comando em um **NOVO** terminal:
```powershell
curl http://127.0.0.1:8000/health
```

Você deve ver:
```json
{"status":"healthy","version":"1.0.0","openai_configured":true}
```

✓ Se viu isso: **O servidor está respondendo!**

##### MAC/LINUX:
```bash
curl http://127.0.0.1:8000/health
```
Mesmo resultado acima.

#### TESTE 2: Chat Endpoint (POST /chat)

Agora vamos enviar uma mensagem para o chatbot.

##### WINDOWS:
Copie este comando **INTEIRO** e cole no PowerShell:
```powershell
$body = @{
    messages = @(
        @{ role = "system"; content = "Você é um assistente útil." },
        @{ role = "user"; content = "Qual é o propósito da Resolução 175?" }
    )
    temperature = 0.7
} | ConvertTo-Json

curl -X POST http://127.0.0.1:8000/chat `
  -ContentType "application/json" `
  -Body $body
```

Você deve ver:
```json
{"response":"(uma longa resposta do chatbot)","model":"gpt-3.5-turbo",...}
```

##### MAC/LINUX:
Cole este comando:
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "Você é um assistente útil."},
      {"role": "user", "content": "Qual é o propósito da Resolução 175?"}
    ],
    "temperature": 0.7
  }'
```

---

### ▼▼▼ OPÇÃO B: USANDO PYTHON (MAIS FÁCIL) ▼▼▼

Se achar CURL confuso, use Python (é bem mais simples!)

#### TESTE 1: Health Check

Em um **NOVO** terminal, vá para a pasta do projeto:
```powershell
cd C:\Users\Win11\OneDrive\Documents\Projetos\chatbot
```

Ative o ambiente virtual:
```powershell
venv_new\Scripts\Activate.ps1
```

Agora, abra Python interativo:
```powershell
python
```

Você deve ver:
```
>>>
```

Agora copie estes comandos (um por um):
```python
import httpx
response = httpx.get("http://127.0.0.1:8000/health")
print(response.json())
```

Você deve ver:
```python
{'status': 'healthy', 'version': '1.0.0', 'openai_configured': True}
```

**Ótimo!** 🎉

#### TESTE 2: Chat (em Python)

Dentro do Python, copie estes comandos:
```python
messages = [
    {"role": "system", "content": "Você é um assistente útil."},
    {"role": "user", "content": "Qual é o propósito da Resolução 175?"}
]

data = {
    "messages": messages,
    "temperature": 0.7
}

response = httpx.post("http://127.0.0.1:8000/chat", json=data)

print(response.json())
```

Você deve ver:
```python
{'response': '(uma longa resposta)...', 'model': 'gpt-3.5-turbo', 'usage': {...}}
```

✓ **SE VIU ISSO: TUDO FUNCIONANDO!** 🎉🎉🎉

#### SAIR DO PYTHON:
Digite:
```python
exit()
```

---

### ▼▼▼ OPÇÃO C: USAR UM SCRIPT PYTHON (O JEITO MAIS FÁCIL) ▼▼▼

Se você quer apenas copiar e colar uma vez, use o script que já preparamos!

Em um **NOVO** terminal:
```powershell
cd C:\Users\Win11\OneDrive\Documents\Projetos\chatbot
venv_new\Scripts\Activate.ps1
python test_endpoints.py
```

Ele vai fazer todos os testes automaticamente e mostrar os resultados.

---

## SOLUÇÃO DE PROBLEMAS

### ❌ ERRO: "python: comando não encontrado"
**Cause:** Python não está instalado ou não está no PATH

**Solução:**
1. Verifique se Python está instalado:
   ```bash
   python --version
   ```
2. Se disser "command not found", instale Python em: https://www.python.org/downloads/
3. Ao instalar, **MARQUE** "Add Python to PATH"

### ❌ ERRO: "O módulo venv_new não existe"
**Cause:** Você não está na pasta certa ou o ambiente não foi criado

**Solução:**
1. Verifique se está na pasta correta:
   ```bash
   pwd  # (Mac/Linux)
   ```
   ou
   ```powershell
   cd  # (Windows)
   ```
2. Recrie o ambiente:
   ```bash
   python -m venv venv_new
   ```

### ❌ ERRO: "Porta 8000 já está em uso"
**Cause:** Outro programa ou servidor está usando a porta 8000

**Solução:**
- **Opção A:** Use uma porta diferente:
  ```bash
  python -m uvicorn app.main:app --port 9000
  ```
- **Opção B:** Feche o programa que está usando a porta 8000
  - **WINDOWS:** Pressione `Ctrl + C` no terminal do servidor

### ❌ ERRO: "Connection refused" ao fazer requisição
**Cause:** O servidor não está rodando

**Solução:**
1. Verifique se o servidor está rodando (Terminal 1)
2. Se não estiver, execute:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

### ❌ ERRO: 404 ou 429 do OpenAI
**Cause:** Problema com a chave API

**Solução:**
Execute o diagnóstico:
```bash
python diagnose_api.py
```

Ele vai te dizer exatamente qual é o problema.

---

## RESUMO RÁPIDO

### PARA USAR A API:

1️⃣ **Abra Terminal 1:**
```powershell
cd C:\Users\Win11\OneDrive\Documents\Projetos\chatbot
venv_new\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
⚠️ **NÃO** feche este terminal!

2️⃣ **Abra Terminal 2 (NOVO):**
```powershell
cd C:\Users\Win11\OneDrive\Documents\Projetos\chatbot
venv_new\Scripts\Activate.ps1
python test_endpoints.py
```

3️⃣ **Veja os resultados!**

---

**FIM DO GUIA!** 🎓

**Dúvidas?** Verifique:
- Os logs no Terminal 1 (servidor)
- A saída no Terminal 2 (requisições)
- Execute: `python diagnose_api.py`