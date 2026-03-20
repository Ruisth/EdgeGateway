# EGW Controller

Orquestrador central da arquitetura **C2DTA (Consumer-Controlled Digital Twin Architecture)**.

Gere os **8 use cases** do ciclo de vida de dispositivos inteligentes, coordenando interacoes entre Hyperledger Fabric, ACA-Py (SSI), Eclipse Ditto, MQTT e IPFS.

## Use Cases

| Endpoint | UC | Descricao |
|---|---|---|
| `POST /uc/enrollment` | UC1 | OEM Enrollment no consorcio |
| `POST /uc/register-model` | UC2 | Registo de modelo de dispositivo |
| `POST /uc/register-device` | UC3 | Auto-registo de dispositivo (EGW/SD) |
| `POST /uc/purchase` | UC4 | Compra de dispositivo |
| `POST /uc/claim` | UC5 | Reivindicacao de dispositivo |
| `POST /uc/twin` | UC6 | Twinning de smart device |
| `POST /uc/untwin` | UC7 | Untwinning de smart device |
| `POST /uc/sell` | UC8 | Venda de smart device |

## Endpoints de Consulta

| Endpoint | Descricao |
|---|---|
| `GET /devices/{id}` | Estado de um dispositivo no Fabric |
| `GET /devices?state=` | Listar dispositivos por estado |
| `GET /devices?owner=` | Listar dispositivos por proprietario |
| `GET /transactions` | Todas as transacoes do controller |
| `GET /health` | Health check |

## Requisitos

- Python 3.12+
- FastAPI, httpx, Pydantic

## Instalacao

```bash
pip install -e ".[dev]"
```

## Execucao

```bash
# Desenvolvimento
uvicorn egw_controller.api:app --reload --port 8090

# Docker
docker compose up -d
```

## Testes

```bash
pytest
```

## Demo Ciclo Completo

```bash
# Com o controller a correr:
python examples/run_full_lifecycle.py --base-url http://localhost:8090
```

## Variaveis de Ambiente

| Variavel | Default | Descricao |
|---|---|---|
| `DITTO_URL` | `http://localhost:8080` | URL da API Ditto |
| `DITTO_USER` | `ditto` | Utilizador Ditto |
| `DITTO_PASS` | `c2dta` | Password Ditto |
| `MQTT_BROKER_HOST` | `localhost` | Host Mosquitto |
| `MQTT_BROKER_PORT` | `8883` | Porta TLS Mosquitto |
| `IPFS_API_URL` | `http://localhost:5001` | URL API IPFS |
| `ACAPY_CONSORTIUM_URL` | `http://localhost:8021` | URL admin ACA-Py consorcio |
| `ACAPY_OEM_URL` | `http://localhost:8031` | URL admin ACA-Py OEM |
| `ACAPY_EGW_URL` | `http://localhost:8061` | URL admin ACA-Py EGW |
| `FABRIC_PEER_URL` | `localhost:7051` | URL peer Fabric |
| `FABRIC_CHANNEL` | `c2dta-channel` | Canal Fabric |
| `DIDCOMM_AGENT_URL` | `http://localhost:8000` | URL agente DIDComm |

## Arquitetura

```
egw_controller/
  api.py              # FastAPI — endpoints REST
  config.py           # Configuracao via env vars
  models.py           # Modelos Pydantic do dominio
  transaction.py      # Gestor de transacoes multi-step
  use_cases/          # Logica de cada UC (UC1-UC8)
  clients/            # Adaptadores para servicos externos
    fabric_client.py  # Hyperledger Fabric (chaincode)
    aca_py_client.py  # ACA-Py (SSI/DIDComm)
    ditto_client.py   # Eclipse Ditto (Digital Twin)
    ipfs_client.py    # IPFS (armazenamento descentralizado)
```

> Ultima revisao: 2026-03-19
