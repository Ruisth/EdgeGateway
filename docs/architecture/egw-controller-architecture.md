# Arquitetura EGW Controller (Orquestrador Central)

## Visao Geral

O EGW Controller e o orquestrador central da arquitetura C2DTA, coordenando os 8 use cases do ciclo de vida dos dispositivos. Expoe uma API REST (FastAPI) e comunica com todos os servicos do ecossistema.

## Stack Tecnologico

| Componente | Tecnologia |
|---|---|
| Framework | FastAPI |
| HTTP Client | httpx |
| Modelos | Pydantic v2 |
| Runtime | Python 3.12 |
| Container | `python:3.12-slim` |
| Porta | 8090 |

## Estrutura do Codigo

```
egw_controller/
  api.py              # FastAPI — endpoints REST
  config.py           # Configuracao via env vars (14 variaveis)
  models.py           # Modelos de dominio Pydantic
  transaction.py      # Gestor de transacoes multi-step (key-pair table)
  use_cases/          # Logica de cada UC (UC1-UC8)
    uc1_oem_enrollment.py
    uc2_model_registration.py
    uc3_device_registration.py
    uc4_device_purchase.py
    uc5_device_claiming.py
    uc6_device_twinning.py
    uc7_device_untwinning.py
    uc8_device_selling.py
  clients/            # Adaptadores para servicos externos
    fabric_client.py  # Hyperledger Fabric (chaincode invocations)
    aca_py_client.py  # ACA-Py (SSI/DIDComm — OOB, Issue Credential, Present Proof)
    ditto_client.py   # Eclipse Ditto (CRUD things)
    ipfs_client.py    # IPFS (add/cat/pin)
```

## Endpoints API

### Use Cases

| Metodo | Endpoint | UC | Descricao |
|---|---|---|---|
| POST | `/uc/enrollment` | UC1 | OEM Enrollment |
| POST | `/uc/register-model` | UC2 | Registo de modelo |
| POST | `/uc/register-device` | UC3 | Auto-registo de dispositivo |
| POST | `/uc/purchase` | UC4 | Compra de dispositivo |
| POST | `/uc/claim` | UC5 | Claiming de dispositivo |
| POST | `/uc/twin` | UC6 | Twinning |
| POST | `/uc/untwin` | UC7 | Untwinning |
| POST | `/uc/sell` | UC8 | Venda |

### Consulta

| Metodo | Endpoint | Descricao |
|---|---|---|
| GET | `/devices/{id}` | Estado do dispositivo no Fabric |
| GET | `/devices?state=` | Listar por estado |
| GET | `/devices?owner=` | Listar por proprietario |
| GET | `/transactions` | Todas as transacoes |
| GET | `/health` | Health check |

## Transaction Manager

Implementa a key-pair table descrita no paper (Seccao 3.1) para preservar estado em operacoes multi-step que envolvem multiplos agentes SSI.

- Cada UC cria uma `Transaction` com passos (`TransactionStep`)
- Estados dos passos: `pending` → `in_progress` → `completed` | `failed`
- A transacao so e `completed` quando todos os passos estao completos

## Integracao com Servicos

```
                    ┌─────────────────┐
                    │  EGW Controller │
                    │    (FastAPI)    │
                    └────┬──┬──┬──┬──┘
                         │  │  │  │
              ┌──────────┘  │  │  └──────────┐
              ↓             ↓  ↓             ↓
        ┌──────────┐ ┌──────┐ ┌────┐ ┌──────────┐
        │  Fabric  │ │Ditto │ │IPFS│ │  ACA-Py  │
        │(chaincode│ │(HTTP)│ │(API│ │ (admin   │
        │  CLI)    │ │      │ │    │ │  API)    │
        └──────────┘ └──────┘ └────┘ └──────────┘
```

## Dependencias

O EGW Controller depende de todos os servicos infraestruturais:
- Mosquitto (MQTT broker) — healthy
- Ditto (nginx) — healthy
- IPFS — healthy
- Fabric (peers) — disponivel
- ACA-Py (agentes) — disponivel
- Indy (pool) — disponivel (via ACA-Py)

> Ultima revisao: 2026-03-19
