# Edge Gateway — Consumer-Controlled Digital Twin Architecture (C2DTA)

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
