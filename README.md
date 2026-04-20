# EdgeGateway — Consumer-Controlled Digital Twin Architecture (C2DTA)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Go 1.21+](https://img.shields.io/badge/Go-1.21+-00ADD8.svg)](https://go.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose%20v2-2496ED.svg)](https://docs.docker.com/compose/)
[![CI](https://github.com/Ruisth/EdgeGateway/actions/workflows/ci.yml/badge.svg)](../../actions/workflows/ci.yml)

Full implementation of the **C2DTA architecture** — a consumer-controlled digital twin system that moves smart device data sovereignty from manufacturers to end users, using dual blockchain, self-sovereign identity, and edge computing.

---

## Paper

> **Consumer-Controlled Digital Twin Architecture: How blockchain technology gives consumers control over their smart devices' digital twins and data**
>
> Filipe Pinto, Catarina Ferreira da Silva, Sergio Moro, Pedro Aquino
>
> *Blockchain: Research and Applications*, Elsevier, 2025
> DOI: [10.1016/j.bcra.2025.100342](https://doi.org/10.1016/j.bcra.2025.100342)
> Received: 24 January 2024 · Revised: 14 June 2025 · Accepted: 16 June 2025

This repository is the reference implementation accompanying the paper above. All 8 use cases described in Section 3.2 are fully implemented and runnable via Docker Compose.

---

## Overview

Today, when a consumer buys a smart device (e.g. a smartwatch), the manufacturer controls the device's digital twin and all sensor data in a centralised cloud. The **C2DTA** architecture reverses this:

- The **Edge Gateway (EGW)** runs on the consumer's local network and hosts the device's Digital Twin at the edge.
- **Hyperledger Fabric** anchors the full device lifecycle on an immutable ecosystem ledger.
- **Hyperledger Indy** provides a decentralised identity ledger for DIDs and credential schemas.
- **ACA-Py** issues and verifies Verifiable Credentials (VCs) that govern device ownership and registration.
- **Eclipse Ditto** manages the Digital Twin with full Web of Things (WoT) compatibility.
- **Eclipse Mosquitto** delivers real-time MQTT telemetry over TLS from the device to the twin.
- **IPFS** stores dataset snapshots with content-addressed hashes anchored on Fabric.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Consumer Edge                                │
│                                                                     │
│  ┌─────────────┐    MQTT/TLS    ┌──────────────┐                   │
│  │ Smart Device│───────────────▶│  Mosquitto   │                   │
│  │ (Smartwatch)│                │  MQTT Broker │                   │
│  └─────────────┘                └──────┬───────┘                   │
│                                        │                            │
│  ┌─────────────────────────────────────▼─────────────────────────┐ │
│  │                    EGW Controller (FastAPI)                    │ │
│  │          Orchestrates UC1–UC8 · REST API :8090                │ │
│  └──────┬──────────┬──────────┬──────────┬───────────┬───────────┘ │
│         │          │          │          │           │              │
│  ┌──────▼──┐ ┌─────▼────┐ ┌──▼──────┐ ┌─▼──────┐ ┌─▼────────┐   │
│  │  Ditto  │ │  ACA-Py  │ │ Fabric  │ │  Indy  │ │   IPFS   │   │
│  │   DT    │ │ 5 agents │ │ 2 peers │ │  Pool  │ │  Kubo    │   │
│  │  :8080  │ │ :8020-71 │ │ :7050-51│ │  :9000 │ │  :8081   │   │
│  └─────────┘ └──────────┘ └─────────┘ └────────┘ └──────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---
Implementação do Edge Gateway descrito no paper **"Consumer-Controlled Digital Twin Architecture: How blockchain technology gives consumers control over their smart devices' digital twins and data"** (Pinto et al., *Blockchain: Research and Applications*, 2025, DOI: [10.1016/j.bcra.2025.100342](https://doi.org/10.1016/j.bcra.2025.100342)).

O objetivo é transferir o Digital Twin (DT) do dispositivo inteligente da cloud para o edge sob controlo efectivo do consumidor, usando uma arquitectura de identidade auto-soberana (SSI) e blockchain dual.

---

## Stack tecnológico (C2DTA)

| Componente | Tecnologia | Papel |
| --- | --- | --- |
| Digital Twin platform | **Eclipse Ditto 3.0** | Hospeda e gere os DTs dos dispositivos inteligentes |
| MQTT broker | **Eclipse Mosquitto 2.0** | Recebe dados de sensores dos SDs via MQTT/SSL |
| Ecosystem ledger | **Hyperledger Fabric** | Rastreia ciclo de vida dos dispositivos e datasets |
| Identity ledger | **Hyperledger Indy** | Ancora DIDs e Verifiable Credentials |
| SSI agents | **Hyperledger Aries / ACA-py** | Agentes DIDComm para todos os stakeholders |
| DIDComm protocols | **Aries RFCs** (0434, 0453, 0509, 0160…) | Comunicação P2P segura e estruturada |
| Decentralized storage | **IPFS (Kubo)** | Armazena datasets históricos do DT |
| Device definition | **W3C WoT Thing Description** | Define o modelo de twinning de cada SD |
| OS / containers | **Yocto Project + OCI** | Imagem Linux embarcada para o EGW |

---

## Arquitectura C2DTA (5 camadas)

```
┌─────────────────────────────────────────────────────────┐
│  Business Edge                                           │
│  Consortium · OEM agents (ACA-py) · SSIaaS providers    │
├─────────────────────────────────────────────────────────┤
│  Ecosystem Layer                                         │
│  Consortium website · Decentralized Marketplace app      │
├─────────────────────────────────────────────────────────┤
│  Peer-to-Peer Layer                                      │
│  DIDComm v2 (Aries RFCs) · Goal codes · OOB URIs        │
├─────────────────────────────────────────────────────────┤
│  Records Layer                                           │
│  Ecosystem Ledger (Fabric) · Identity Ledger (Indy)     │
│  Decentralized Storage (IPFS)                            │
├─────────────────────────────────────────────────────────┤
│  Consumer Edge                                           │
│  Edge Gateway (EGW) · Smart Device (SD) · Eclipse Ditto │
└─────────────────────────────────────────────────────────┘
```

### Edge Gateway (EGW)
- Hospeda os agentes SSI (ACA-py) com DID público auto-gerado no 1.º boot
- Corre Eclipse Ditto + Eclipse Mosquitto em containers OCI
- Liga ao Hyperledger Fabric para actualizações de estado do dispositivo
- Liga ao Hyperledger Indy para emissão/verificação de VCs
- Transfere datasets para IPFS em intervalos configuráveis

### Ciclo de vida do Smart Device (6 estados)
```
Manufactured → Available → In-Transit → Claimed → Twinned → Decommissioned
```

### Verifiable Credentials
| VC | Emissor | Portador | Propósito |
| --- | --- | --- | --- |
| **Enrollment VC** | Consortium | OEM | Membros do consórcio |
| **Genesis VC** | OEM | EGW / SD | Proveniência do dispositivo |
| **Ownership VC** | OEM / EGW | Consumidor | Controlo sobre o dispositivo |

---

## Como começar

1. **Clonar e abrir no VS Code** — extensões sugeridas em `.vscode/extensions.json`.
2. **Adicionar submódulos Yocto/BSP**
   ```bash
   git submodule add git://git.yoctoproject.org/poky yocto/poky
   git submodule update --init --recursive
   ```
3. **Inicializar ambiente Yocto**
   ```bash
   source scripts/setup-env.sh
   ```
4. **Dev local (DIDComm protótipo)**
   ```bash
   cd services/didcomm-agent
   docker compose up --build
   ```
5. **Construir imagem de referência**
   ```bash
   bitbake edgegateway-image
   ```

---

## Estrutura do repositório

```text
.vscode/                     Definições de tarefas, lint e extensões recomendadas
docs/
  architecture/              Arquitectura C2DTA (5 camadas, DIDComm, dataflow)
  paper/                     Resumo detalhado do paper C2DTA
  research/                  Estudos complementares sobre IA pessoal e blockchain
  roadmaps/                  Marcos técnicos alinhados com os 8 cenários C2DTA
scripts/                     Scripts utilitários (setup-env.sh)
services/
  didcomm-agent/             Protótipo experimental de cripto DIDComm (X25519)
                             NOTA: stack definitivo usa Hyperledger Aries/ACA-py
yocto/
  README.md                  Guia de camadas e receitas Yocto
  layers/meta-edgegateway/   Receita edgegateway-image (ACA-py, Ditto, Fabric, IPFS)
EdgeGateway_Paper.pdf        Paper C2DTA completo (Pinto et al., 2025)
LICENSE                      Licença MIT
```

---

## Documentação recomendada

| Tema | Ficheiro | Conteúdo |
| --- | --- | --- |
| Arquitectura C2DTA | `docs/architecture/system-architecture.md` | 5 camadas, structs Fabric, state machine |
| Pipeline de dados | `docs/architecture/communication-and-dataflow.md` | SD→MQTT→Ditto→IPFS |
| SSI e DIDComm | `docs/architecture/didcomm-architecture.md` | Aries RFCs, VCs, goal codes, agentes |
| Resumo do paper | `docs/paper/edgegateway-paper-summary.md` | 8 cenários, benchmarks, tecnologias |
| Roadmap | `docs/roadmaps/milestone-plan.md` | Fases de implementação com KPIs |

---

## 8 Cenários funcionais (C2DTA)

1. OEM enroll no consórcio
2. Registo de modelo de dispositivo (com WoT file)
3. Auto-registo do dispositivo no ecosystem ledger (EGW + SD)
4. Consumidor compra dispositivo (Ownership VC)
5. Consumidor "claims" dispositivo (EGW + SD)
6. SD twinning (WoT + MQTT + Eclipse Ditto + IPFS)
7. SD untwinning
8. SD selling (com revogação de VC)

---

## Roadmap resumido

| Fase | Foco |
| --- | --- |
| **Fase 0** | Hardware-alvo, BSP, requisitos de segurança/compliance |
| **Fase 1** | Hyperledger Fabric + Indy, ACA-py agents, Eclipse Ditto + Mosquitto |
| **Fase 2** | IPFS, W3C WoT, 8 cenários funcionais completos |
| **Fase 3** | Pilotos com dispositivos reais, auditoria, federated learning |

Ver `docs/roadmaps/milestone-plan.md` para detalhes.

---

## Licença

Distribuído sob a licença MIT — consulte `LICENSE` para detalhes.

## Quick Start

### Prerequisites

- Docker & Docker Compose v2
- Python 3.12+
- Go 1.21+ (for chaincode development only)

### Setup

```bash
# 1. Clone the repository
git clone <repo-url> && cd EdgeGateway

# 2. Generate TLS certificates for MQTT
cd services/mosquitto/certs && bash generate-certs.sh && cd -

# 3. Start all services (~20 containers)
docker compose up -d

# 4. Verify the EGW Controller is healthy
curl http://localhost:8090/health
# Expected: {"status": "ok", "service": "egw-controller"}

# 5. Run the full lifecycle demo (UC1–UC8)
python services/egw-controller/examples/run_full_lifecycle.py
```

---

## Repository Structure

```text
EdgeGateway/
├── .github/workflows/           GitHub Actions CI/CD (ci.yml, build-yocto.yml)
├── .vscode/                     VS Code tasks, linting, recommended extensions
├── docs/
│   ├── architecture/            11 detailed architecture documents
│   ├── paper/                   Paper summary and research notes
│   └── roadmaps/                Development milestone plan
├── services/
│   ├── egw-controller/          Central orchestrator (FastAPI, 8 use cases)
│   ├── smart-device-simulator/  Smartwatch simulator (1 Hz telemetry over MQTT)
│   ├── mosquitto/               MQTT broker (Eclipse Mosquitto 2.0, TLS)
│   ├── ditto/                   Digital Twin platform (Eclipse Ditto 3.5.6 + WoT TD)
│   ├── fabric/                  Ecosystem blockchain (Hyperledger Fabric 2.5, Go chaincodes)
│   ├── indy/                    Identity blockchain (Hyperledger Indy, von-network)
│   ├── aca-py/                  SSI agents (ACA-Py 1.2.2, 5 instances)
│   ├── ipfs/                    Decentralised storage (IPFS Kubo 0.28)
│   └── didcomm-agent/           DIDComm 2.0 MVP agent (FastAPI)
├── yocto/
│   └── layers/meta-edgegateway/ Custom Yocto layer for edge device deployment
├── docker-compose.yml           Orchestrates all ~20 containers on network c2dta-net
├── EdgeGateway_Paper.pdf        Reference paper (pre-print)
└── LICENSE                      MIT
```

---

## Architecture

### Component Roles

| Component | Technology | Version | Role in C2DTA |
|-----------|-----------|---------|---------------|
| EGW Controller | Python + FastAPI | 3.12 | Central orchestrator; exposes UC1–UC8 REST API |
| Smart Device Simulator | Python + paho-mqtt | 3.12 | Simulates 1 Hz smartwatch telemetry (heartbeat, GPS) |
| MQTT Broker | Eclipse Mosquitto | 2.0.x | TLS-secured MQTT relay; topic ACLs per device |
| Digital Twin | Eclipse Ditto | 3.5.6 | WoT-compatible twin; receives MQTT telemetry |
| Ecosystem Ledger | Hyperledger Fabric | 2.5.x | Immutable device lifecycle and dataset provenance |
| Identity Ledger | Hyperledger Indy (von-network) | — | DID registry; VC schema and credential definitions |
| SSI Agents | ACA-Py | 1.2.2 | Issues/verifies VCs; manages DIDComm connections |
| Decentralised Storage | IPFS (Kubo) | 0.28.0 | Content-addressed dataset snapshots |
| DIDComm Agent | Python + FastAPI | 3.12 | Lightweight DIDComm 2.0 message encryption/decryption |
| Orchestration | Docker Compose v2 | — | Single-command local deployment |
| Edge OS | Yocto Linux | — | Custom image for physical edge device deployment |

### Device Lifecycle State Machine

The Fabric chaincode (`services/fabric/chaincode/device-lifecycle/device_lifecycle.go`) enforces a strict state machine across the device's life:

```
                UC3                 UC3
  [start] ──────────▶ Manufactured ──────▶ Available
                                               │
                                           UC4 │ InitiateTransit
                                               ▼
                                          In-Transit
                                               │
                                           UC5 │ ClaimDevice
                                               ▼
                                ┌──────────  Claimed  ◀──────────┐
                                │               │                 │
                             UC6│ TwinDevice  UC7│ UntwinDevice   │
                                ▼               │                 │
                              Twinned ──────────┘                 │
                                                                   │
                         UC8 (re-enters In-Transit via UC4/UC5) ──┘
                                │
                                ▼
                          Decommissioned  (terminal state)
```

| Transition | Chaincode function | Triggered by |
|------------|-------------------|-------------|
| → Manufactured | `ManufactureDevice` | UC3 |
| Manufactured → Available | `MakeAvailable` | UC3 |
| Available → In-Transit | `InitiateTransit` | UC4 |
| In-Transit → Claimed | `ClaimDevice` | UC5 |
| Claimed → Twinned | `TwinDevice` | UC6 |
| Twinned → Claimed | `UntwinDevice` | UC7 |
| Any → Decommissioned | `DecommissionDevice` | — |

### ACA-Py Agent Instances

Five ACA-Py instances serve different actors in the ecosystem:

| Agent | Admin Port | HTTP Port | Role |
|-------|-----------|-----------|------|
| Consortium | 8021 | 8020 | Issues Enrollment VCs to OEMs; governs ecosystem membership |
| OEM | 8031 | 8030 | Issues Genesis VCs to devices; registers models on Fabric |
| Consumer A | 8041 | 8040 | Receives Ownership VCs; proves ownership during claiming |
| EGW | 8061 | 8060 | Validates credentials during device claiming (UC5) |
| Smart Device | 8071 | 8070 | Holds Genesis VC; authenticates with EGW |

### Verifiable Credential Schemas

Three VC schemas are registered on Hyperledger Indy (`services/indy/schemas/`):

| Schema | Issued by | Issued to | Used in | Purpose |
|--------|----------|-----------|---------|---------|
| Enrollment VC | Consortium | OEM | UC1, UC2 | Proves OEM is a trusted ecosystem member |
| Genesis VC | OEM | EGW / Smart Device | UC3, UC5 | Proves device provenance and authenticity |
| Ownership VC | OEM | Consumer | UC4, UC5, UC8 | Proves consumer purchased the device |

---

## Use Cases (UC1–UC8)

All 8 use cases are implemented in `services/egw-controller/src/egw_controller/use_cases/`.

| UC | Name | Actors | Fabric Transition | VCs Involved | Services |
|----|------|--------|------------------|-------------|---------|
| UC1 | OEM Enrollment | Consortium, OEM | — | Enrollment VC (issued) | ACA-Py |
| UC2 | Model Registration | OEM, Consortium | — | Enrollment VC (verified) | ACA-Py, Fabric |
| UC3 | Device Self-Registration | OEM, EGW/SD | → Manufactured → Available | Genesis VC (issued) | ACA-Py, Fabric |
| UC4 | Consumer Buys Device | Consumer, OEM | Available → In-Transit | Ownership VC (issued) | ACA-Py, Fabric |
| UC5 | Device Claiming | Consumer, EGW | In-Transit → Claimed | Ownership VC (verified) | ACA-Py, Fabric |
| UC6 | SD Twinning | EGW Controller | Claimed → Twinned | — | Ditto, MQTT, IPFS, Fabric |
| UC7 | SD Untwinning | EGW Controller | Twinned → Claimed | — | Ditto, MQTT, IPFS, Fabric |
| UC8 | SD Selling | Consumer A→B | → In-Transit | Ownership VC (revoked + re-issued) | ACA-Py, Fabric |

For detailed step-by-step flows per use case, see [`docs/architecture/use-case-flows.md`](docs/architecture/use-case-flows.md).

---

## API Reference — EGW Controller

Base URL: `http://localhost:8090`
Full OpenAPI docs: `http://localhost:8090/docs`

| Endpoint | Method | Use Case | Description |
|----------|--------|----------|-------------|
| `/uc/enrollment` | POST | UC1 | OEM enrollment into consortium via DIDComm |
| `/uc/register-model` | POST | UC2 | Register device model on Hyperledger Fabric |
| `/uc/register-device` | POST | UC3 | Device self-registration with Genesis VC issuance |
| `/uc/purchase` | POST | UC4 | Consumer purchases device; Ownership VC issued |
| `/uc/claim` | POST | UC5 | Consumer claims device via Ownership VC proof |
| `/uc/twin` | POST | UC6 | Create Digital Twin in Ditto + start MQTT streaming |
| `/uc/untwin` | POST | UC7 | Remove Digital Twin; final snapshot to IPFS |
| `/uc/sell` | POST | UC8 | Transfer device ownership to new consumer |
| `/devices/{device_id}` | GET | — | Query device state from Fabric ledger |
| `/devices` | GET | — | List devices filtered by `?state=` or `?owner=` |
| `/transactions` | GET | — | List all multi-step transactions with step status |
| `/health` | GET | — | Health check |

---

## Port Mappings

| Service | Port | Protocol | Description |
|---------|------|----------|-------------|
| DIDComm Agent | 8000 | HTTP | DIDComm 2.0 MVP REST API |
| ACA-Py Consortium | 8020 / 8021 | HTTP | HTTP / Admin API |
| ACA-Py OEM | 8030 / 8031 | HTTP | HTTP / Admin API |
| ACA-Py Consumer A | 8040 / 8041 | HTTP | HTTP / Admin API |
| ACA-Py EGW | 8060 / 8061 | HTTP | HTTP / Admin API |
| ACA-Py Smart Device | 8070 / 8071 | HTTP | HTTP / Admin API |
| Ditto (nginx) | 8080 | HTTP | Digital Twin REST API |
| IPFS Gateway | 8081 | HTTP | IPFS HTTP gateway |
| EGW Controller | 8090 | HTTP | Main orchestration API (FastAPI) |
| Fabric Orderer | 7050 | gRPC | Raft ordering service |
| Fabric Peer (Consortium) | 7051 | gRPC | ConsortiumOrg peer |
| Fabric CA (Consortium) | 7054 | HTTP | Certificate Authority |
| Fabric CA (OEM) | 8054 | HTTP | Certificate Authority |
| Mosquitto MQTT | 8883 | MQTT/TLS | MQTT broker (TLS required) |
| Fabric Peer (OEM) | 9051 | gRPC | OEMOrg peer |
| Indy Pool (Web UI) | 9000 | HTTP | Hyperledger Indy pool explorer |
| IPFS API | 5001 | HTTP | IPFS Kubo API |
| IPFS Swarm | 4001 | TCP/UDP | IPFS P2P swarm |

---

## Tests

```bash
# EGW Controller — 24 unit tests (UC1–UC8 + transaction manager)
cd services/egw-controller && python -m pytest tests/ -v

# Smart Device Simulator — sensor data generation + MQTT connectivity
cd services/smart-device-simulator && python -m pytest tests/ -v

# DIDComm Agent — REST API + message encryption/decryption
cd services/didcomm-agent && python -m pytest tests/ -v
```

---

## Documentation

| Topic | File |
|-------|------|
| System architecture overview | [`docs/architecture/system-architecture.md`](docs/architecture/system-architecture.md) |
| MQTT architecture | [`docs/architecture/mqtt-architecture.md`](docs/architecture/mqtt-architecture.md) |
| Digital Twin (Ditto) | [`docs/architecture/ditto-architecture.md`](docs/architecture/ditto-architecture.md) |
| Hyperledger Fabric | [`docs/architecture/fabric-architecture.md`](docs/architecture/fabric-architecture.md) |
| Hyperledger Indy / SSI | [`docs/architecture/indy-architecture.md`](docs/architecture/indy-architecture.md) |
| IPFS storage | [`docs/architecture/ipfs-architecture.md`](docs/architecture/ipfs-architecture.md) |
| EGW Controller design | [`docs/architecture/egw-controller-architecture.md`](docs/architecture/egw-controller-architecture.md) |
| DIDComm agent | [`docs/architecture/didcomm-architecture.md`](docs/architecture/didcomm-architecture.md) |
| Use case flows (UC1–UC8) | [`docs/architecture/use-case-flows.md`](docs/architecture/use-case-flows.md) |
| Communication & data flow | [`docs/architecture/communication-and-dataflow.md`](docs/architecture/communication-and-dataflow.md) |
| Development roadmap | [`docs/roadmaps/milestone-plan.md`](docs/roadmaps/milestone-plan.md) |

---

## Yocto Edge Deployment

A custom Yocto layer (`yocto/layers/meta-edgegateway/`) packages the EGW Controller, DIDComm Agent, and Mosquitto broker as a ready-to-flash Linux image for physical edge devices.

```bash
# 1. Add Yocto/BSP submodules
git submodule add git://git.yoctoproject.org/poky yocto/poky

# 2. Initialise the build environment
source scripts/setup-env.sh

# 3. Build the edge image
bitbake edgegateway-image
```

See [`yocto/README.md`](yocto/README.md) for supported boards and BSP configuration.

---

## License

Distributed under the MIT License — see [`LICENSE`](LICENSE) for details.

---

> Reference paper: Filipe Pinto et al., "Consumer-Controlled Digital Twin Architecture", *Blockchain: Research and Applications*, Elsevier, 2025. DOI: [10.1016/j.bcra.2025.100342](https://doi.org/10.1016/j.bcra.2025.100342)

