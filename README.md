# Edge Gateway — Consumer-Controlled Digital Twin Architecture (C2DTA)

<<<<<<< HEAD
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
=======
Implementacao completa da arquitetura **C2DTA** descrita no paper `EdgeGateway_Paper.pdf`. O Edge Gateway transfere o Digital Twin (DT) do smart device para o edge sob controlo do consumidor, usando blockchain dual (Hyperledger Fabric + Indy), SSI/DIDComm (ACA-Py), Eclipse Ditto, Eclipse Mosquitto e IPFS.

## Quick Start

```bash
# 1. Clonar e abrir no VS Code
git clone <repo-url> && cd EdgeGateway
code .

# 2. Gerar certificados TLS para MQTT
cd services/mosquitto/certs && bash generate-certs.sh && cd -

# 3. Lancar todos os servicos (~20 containers)
docker compose up -d

# 4. Verificar health
curl http://localhost:8090/health

# 5. Executar demo do ciclo de vida completo (UC1-UC8)
python services/egw-controller/examples/run_full_lifecycle.py
```

## Estrutura do Repositorio

```text
.github/workflows/           CI/CD (GitHub Actions)
.vscode/                     Tasks, lint, extensoes
docs/
  architecture/              Arquitetura de sistema, MQTT, Ditto, Fabric, Indy, IPFS, EGW Controller, fluxos UC
  paper/                     Resumo do EdgeGateway_Paper.pdf
  roadmaps/                  Marcos tecnicos
services/
  mosquitto/                 MQTT Broker (Eclipse Mosquitto 2.0, TLS)
  smart-device-simulator/    Simulador de smartwatch (1Hz heartbeat/geo/timestamp)
  ditto/                     Digital Twin (Eclipse Ditto 3.5.6 + WoT TD)
  fabric/                    Blockchain ecossistema (Hyperledger Fabric 2.5 + chaincodes Go)
  indy/                      Blockchain identidade (Hyperledger Indy, von-network)
  aca-py/                    Agentes SSI (ACA-Py 1.2.2, 5 instancias)
  ipfs/                      Armazenamento descentralizado (IPFS Kubo 0.28)
  egw-controller/            Orquestrador central (FastAPI, 8 use cases)
  didcomm-agent/             Agente DIDComm MVP
yocto/
  layers/meta-edgegateway/   Receitas Yocto para deploy no edge
docker-compose.yml           Orquestracao de todos os servicos
EdgeGateway_Paper.pdf        Paper de referencia
```

## Tabela de Portas

| Servico | Porta | Descricao |
|---|---|---|
| DIDComm Agent | 8000 | API REST DIDComm MVP |
| ACA-Py Consortium | 8020/8021 | HTTP/Admin SSI |
| ACA-Py OEM | 8030/8031 | HTTP/Admin SSI |
| ACA-Py Consumer A | 8040/8041 | HTTP/Admin SSI |
| ACA-Py EGW | 8060/8061 | HTTP/Admin SSI |
| ACA-Py SD | 8070/8071 | HTTP/Admin SSI |
| Ditto (nginx) | 8080 | API Digital Twin |
| IPFS Gateway | 8081 | Gateway HTTP IPFS |
| EGW Controller | 8090 | API Orquestrador (FastAPI) |
| Fabric Orderer | 7050 | Orderer Raft |
| Fabric Peer (Consortium) | 7051 | Peer ConsortiumOrg |
| Fabric CA (Consortium) | 7054 | Certificate Authority |
| Fabric CA (OEM) | 8054 | Certificate Authority |
| Mosquitto MQTT | 8883 | Broker MQTT (TLS) |
| Fabric Peer (OEM) | 9051 | Peer OEMOrg |
| Indy Pool | 9000 | Web UI Indy |
| IPFS API | 5001 | API IPFS |
| IPFS Swarm | 4001 | Swarm P2P |

## Use Cases (UC1-UC8)

| UC | Nome | Descricao |
|---|---|---|
| UC1 | OEM Enrollment | Inscricao de OEM no consorcio via DIDComm |
| UC2 | Model Registration | Registo de modelo de dispositivo no Fabric |
| UC3 | Device Self-Registration | Auto-registo de EGW/SD com Genesis VC |
| UC4 | Consumer Buys Device | Compra com Ownership VC |
| UC5 | Device Claiming | Reivindicacao via prova de Ownership VC |
| UC6 | SD Twinning | Criacao de DT no Ditto + streaming MQTT |
| UC7 | SD Untwinning | Remocao do DT |
| UC8 | SD Selling | Transferencia de propriedade entre consumidores |

Ver detalhes em `docs/architecture/use-case-flows.md`.

## Stack Tecnologico

| Componente | Tecnologia | Versao |
|---|---|---|
| MQTT Broker | Eclipse Mosquitto | 2.0.x |
| Digital Twin | Eclipse Ditto | 3.5.6 |
| Blockchain Ecossistema | Hyperledger Fabric | 2.5.x |
| Blockchain Identidade | Hyperledger Indy (von-network) | — |
| Agentes SSI | ACA-Py | 1.2.2 |
| Armazenamento Descentralizado | IPFS (Kubo) | 0.28.0 |
| Simulador SD | Python + paho-mqtt | 3.12 |
| Controller EGW | Python + FastAPI | 3.12 |
| Chaincode | Go | 1.21+ |
| Orquestracao | Docker Compose v2 | — |
| CI/CD | GitHub Actions | — |

## Documentacao

| Tema | Ficheiro |
|---|---|
| Arquitetura de sistema | `docs/architecture/system-architecture.md` |
| Arquitetura MQTT | `docs/architecture/mqtt-architecture.md` |
| Arquitetura Ditto (DT) | `docs/architecture/ditto-architecture.md` |
| Arquitetura Fabric | `docs/architecture/fabric-architecture.md` |
| Arquitetura Indy/SSI | `docs/architecture/indy-architecture.md` |
| Arquitetura IPFS | `docs/architecture/ipfs-architecture.md` |
| Arquitetura EGW Controller | `docs/architecture/egw-controller-architecture.md` |
| Fluxos UC1-UC8 | `docs/architecture/use-case-flows.md` |
| DIDComm | `docs/architecture/didcomm-architecture.md` |
| Roadmap | `docs/roadmaps/milestone-plan.md` |

## Testes

```bash
# Testes do SD Simulator
cd services/smart-device-simulator && python -m pytest tests/ -v

# Testes do EGW Controller (24 testes)
cd services/egw-controller && python -m pytest tests/ -v

# Testes do DIDComm Agent
cd services/didcomm-agent && python -m pytest tests/ -v
```

## Guia Yocto

1. Adicionar submodulos Yocto/BSP: `git submodule add git://git.yoctoproject.org/poky yocto/poky`
2. Inicializar ambiente: `source scripts/setup-env.sh`
3. Construir imagem: `bitbake edgegateway-image`

Detalhes em `yocto/README.md`.

## Licenca

Distribuido sob a licenca MIT — consulte `LICENSE` para detalhes.

> Ultima revisao: 2026-03-20
>>>>>>> 02ed0cf0233d25fdf43da200d6f31c53d0813984
