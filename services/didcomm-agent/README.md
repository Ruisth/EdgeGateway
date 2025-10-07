# DIDComm Agent Service

Este diretório contém o protótipo do agente DIDComm do Edge Gateway. O objetivo é
fornecer uma implementação mínima viável (MVP) para troca de mensagens seguras entre o
Edge Gateway e o Digital Twin utilizando X25519 para acordo de chaves, ChaCha20-Poly1305
para criptografia autenticada e envelopes JSON compatíveis com o espírito do DIDComm v2.

## Estrutura
```
services/didcomm-agent/
├── README.md
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── src/
│   └── didcomm_agent/
│       ├── __init__.py
│       ├── api.py              # API FastAPI (HTTP)
│       ├── crypto.py           # X25519 + ChaCha20-Poly1305 + HKDF
│       ├── exceptions.py
│       ├── message.py          # Dataclasses de mensagem/envelope
│       ├── service.py          # Lógica do agente DIDComm
│       └── storage.py          # Persistência opcional (SQLite)
├── tests/
│   ├── conftest.py
│   ├── test_didcomm_agent.py   # Núcleo do agente
│   └── test_api.py             # Fluxo E2E via HTTP (FastAPI)
└── examples/
    ├── demo_exchange.py        # Demonstração local (sem HTTP)
    └── smoke_api.py            # Smoke test HTTP (para o container/API)
```

## Início rápido (local)
1. (Opcional) Criar venv e instalar dependências:
   - python -m pip install -r requirements.txt
2. Executar testes:
   - python -m pytest
3. Rodar o exemplo local (sem HTTP):
   - python examples/demo_exchange.py
4. Subir a API localmente (modo desenvolvimento):
   - uvicorn didcomm_agent.api:app --host 0.0.0.0 --port 8000

Observação Windows: se tiver problemas com cURL/PowerShell ao enviar JSON com aspas, use o script `examples/smoke_api.py` para validar o fluxo HTTP.

## API HTTP (FastAPI)
Endpoints principais (corpo/respostas simplificados):
- POST /agent: cria/recupera um agente local (idempotente)
- POST /accept: aceita convite de outro agente e devolve contra‑convite
- POST /complete: completa handshake com o contra‑convite
- GET  /peers?agent_id=...: lista DIDs pareados
- POST /send: envia mensagem segura para um peer
- POST /receive: recebe/desempacota envelope
- GET  /health: healthcheck {"status":"ok"}

Contrato mínimo:
- Cada chamada inclui ou deriva um `agent_id` para suportar múltiplos agentes.
- Mensagens são cifradas com chaves derivadas via X25519 + HKDF, e AAD vincula remetente/destinatário.
- Persistência (SQLite) é opcional e controlada por variável de ambiente (veja abaixo).

## Executar com Docker
Opção 1: Docker Compose (recomendado para desenvolvimento)
- docker compose up --build

Isto irá:
- construir a imagem baseada em python:3.12‑slim,
- expor a API em http://localhost:8000,
- mapear ./data -> /data (para persistência SQLite se habilitada).

Opção 2: Docker puro
- docker build -t didcomm-agent:dev .
- docker run --rm -p 8000:8000 -e DIDCOMM_DB_PATH=/data/didcomm.sqlite -v %cd%/data:/data didcomm-agent:dev

Healthcheck:
- GET http://localhost:8000/health → {"status":"ok"}

## Smoke test HTTP (container)
Para validar o fluxo fim‑a‑fim (convite, handshake, envio/recebimento):
- Certifique-se de que o container está rodando e ouvindo em :8000.
- Execute: python examples/smoke_api.py

Saída esperada (resumo):
- health: {"status":"ok"}
- message: objeto JSON com o corpo recebido pelo par.

Em Windows/PowerShell, preferimos este script em vez de invocações cURL complexas devido a questões de quoting.

## Persistência (SQLite)
- Defina DIDCOMM_DB_PATH para habilitar persistência: por exemplo, 
  /data/didcomm.sqlite (já montado no compose).
- O serviço persiste agentes (chave privada base64 + metadados) e peers (chave pública base64, DID, endpoint, label).
- No boot da API, se um agente existir em storage, ele é restaurado.

## Segurança e limites atuais
- MVP para POCs: chaves X25519 voláteis a menos que a persistência esteja ativa.
- Não há autenticação HTTP ainda (p/ laboratório). Coloque atrás de rede confiável.
- Sem anexos DIDComm, revogação ou reenvio offline ainda.

## Próximos passos
- Integrar armazenamento de chaves via TPM/HSM.
- Autenticação e autorização da API (mTLS, OAuth2).
- Suporte a anexos DIDComm e filas para reenvio offline.
- Receitas Yocto para empacotar o serviço na imagem final do Edge Gateway.
