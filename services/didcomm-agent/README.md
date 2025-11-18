# DIDComm Agent Service

Protótipo do agente DIDComm do Edge Gateway. Implementa um MVP para troca de mensagens seguras entre o Edge Gateway e o Digital Twin usando X25519 (acordo de chaves), ChaCha20-Poly1305 (criptografia autenticada) e envelopes compatíveis com DIDComm v2.

## Estrutura
```
services/didcomm-agent/
  README.md
  requirements.txt
  pyproject.toml
  Dockerfile
  docker-compose.yml
  src/didcomm_agent/
    api.py          # FastAPI / HTTP
    crypto.py       # X25519 + HKDF + ChaCha20-Poly1305
    service.py      # Lógica principal
    message.py      # Dataclasses de mensagens/envelopes
    storage.py      # Persistência opcional (SQLite)
  tests/
    test_*.py
  examples/
    demo_exchange.py
    smoke_api.py
```

## Variáveis de ambiente
| Variável | Descrição | Default |
| --- | --- | --- |
| `DIDCOMM_DB_PATH` | Caminho do SQLite para persistir agentes/peers. | vazio (memória) |
| `DIDCOMM_AGENT_HOST` | Host de binding do FastAPI/Uvicorn. | `0.0.0.0` |
| `DIDCOMM_AGENT_PORT` | Porta da API. | `8000` |
| `DIDCOMM_LOG_LEVEL` | Nível de log (`info`, `debug`, etc.). | `info` |
| `DIDCOMM_ENCRYPTION_BACKEND` | `libsodium` (atual) – reservado para futuros backends. | `libsodium` |

## Início rápido (local)
1. (Opcional) Criar venv e instalar dependências: `python -m pip install -r requirements.txt`.
2. Executar testes: `python -m pytest`.
3. Rodar exemplo local (sem HTTP): `python examples/demo_exchange.py`.
4. Subir API: `uvicorn didcomm_agent.api:app --host 0.0.0.0 --port 8000`.

> Dica Windows: se encontrar problemas ao usar cURL no PowerShell, utilize `python examples/smoke_api.py` para validar o fluxo HTTP.

## API HTTP (FastAPI)
Endpoints principais:
- `POST /agent` – cria/recupera um agente local (idempotente).
- `POST /accept` – aceita convite e devolve contra-convite.
- `POST /complete` – finaliza handshake com o contra-convite.
- `GET /peers?agent_id=...` – lista DIDs pareados.
- `POST /send` – envia mensagem segura para um peer.
- `POST /receive` – recebe/desempacota envelope.
- `GET /health` – healthcheck `{"status":"ok"}`.

Contrato mínimo:
- Cada chamada inclui ou deriva `agent_id` para suportar múltiplos agentes.
- Mensagens cifradas com chaves derivadas via X25519 + HKDF (AAD inclui remetente/destinatário).
- Persistência (SQLite) é opcional e controlada por `DIDCOMM_DB_PATH`.

## Execução com Docker
### Docker Compose (desenvolvimento)
```
docker compose up --build
```
- Base: `python:3.12-slim`.
- API exposta em `http://localhost:8000`.
- Mapeia `./data -> /data` para persistência.

### Docker CLI puro
```
docker build -t didcomm-agent:dev .
docker run --rm -p 8000:8000 ^
  -e DIDCOMM_DB_PATH=/data/didcomm.sqlite ^
  -v %cd%/data:/data didcomm-agent:dev
```

## Segurança e limites atuais
- MVP para POCs: chaves X25519 voláteis quando não há persistência.
- Não há autenticação HTTP; coloque atrás de rede confiável/mTLS.
- Sem anexos DIDComm, revogação ou reenvio offline garantido (fila básica apenas).
- libsodium precisa estar instalado (já incluído nas dependências do projeto).

## Próximos passos
1. Integrar armazenamento de chaves via TPM/HSM.
2. Adicionar autenticação/autorização (mTLS, OAuth2 ou tokens emitidos pelo ledger).
3. Suporte a anexos DIDComm e filas confiáveis para reenvio offline.
4. Criar receitas Yocto/containers para deployment automatizado no Edge Gateway.
5. Automatizar hardening (CIS Docker benchmark, dependabot, varredura SAST/DAST).

> Última revisão: 2025-11-18

