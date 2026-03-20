# Plano de Marcos para o Edge Gateway

Derivado das fases do `EdgeGateway_Paper.pdf` e expandido para orientar planejamento tático. Atualize sempre que datas ou critérios mudarem.

## Visão resumida
| Fase | Período sugerido | Critério de saída |
| --- | --- | --- |
| Fase 1 — Infraestrutura MQTT + Simulador SD | Mês 1 | Mosquitto TLS operacional, simulador publicando a 1Hz |
| Fase 2 — Digital Twin (Ditto + WoT) | Mês 1-2 | Ditto a receber telemetria via MQTT, WoT TD definido |
| Fase 3 — Blockchain (Fabric + Chaincodes) | Mês 1-2 | Rede Fabric operacional, chaincodes deployados |
| Fase 4 — Identidade (Indy + ACA-Py) | Mês 1-2 | Pool Indy operacional, 5 agentes ACA-Py ativos |
| Fase 5 — IPFS | Mês 2 | Kubo operacional, add/pin/cat funcional |
| Fase 6 — EGW Controller | Mês 3 | Orquestrador com 8 UCs, 24 testes a passar |
| Fase 7 — Integração, CI/CD, Documentação | Mês 3-4 | Docker Compose raiz, CI verde, docs completos |

## Detalhamento

### Fase 1 — Infraestrutura MQTT + Simulador SD
- **1A. Eclipse Mosquitto**: Broker MQTT com TLS (porta 8883), ACL por dispositivo, persistência ativa
- **1B. SD Simulator**: Simulador Python de smartwatch com heartbeat (random walk), geolocation (drift gaussiano), timestamp a 1Hz via paho-mqtt

**Estado**: Completo. Servicos em `services/mosquitto/` e `services/smart-device-simulator/`.

### Fase 2 — Digital Twin (Eclipse Ditto + WoT)
- **2A. Eclipse Ditto 3.5.6**: Stack completa (MongoDB + 5 servicos + nginx), conectividade MQTT com payload mapping JavaScript
- **2B. WoT Thing Description**: W3C WoT TD v1.1 para smartwatch (heartbeat, geolocation, timestamp)

**Estado**: Completo. Servicos em `services/ditto/`.

### Fase 3 — Blockchain (Hyperledger Fabric + Chaincodes)
- Rede Fabric 2.5 (1 orderer, 2 orgs, CouchDB, 2 CAs)
- Chaincode `device-lifecycle` (Go): 6 estados, todas as transicoes
- Chaincode `dataset-tracking` (Go): registo e transferencia de datasets IPFS

**Estado**: Completo. Servicos em `services/fabric/`.

### Fase 4 — Identidade (Hyperledger Indy + ACA-Py)
- Pool Indy (von-network, 4 nos) com Web UI
- 3 schemas VC: Enrollment, Genesis, Ownership
- 5 agentes ACA-Py: Consortium, OEM, Consumer A, EGW, SD
- Plugins C2DTA com goal codes para automacao DIDComm

**Estado**: Completo. Servicos em `services/indy/` e `services/aca-py/`.

### Fase 5 — IPFS (Kubo)
- No IPFS local para snapshots do DT
- CIDs ancorados no Fabric via dataset-tracking

**Estado**: Completo. Servico em `services/ipfs/`.

### Fase 6 — EGW Controller
- FastAPI com endpoints para 8 use cases
- Clientes para Fabric, Ditto, ACA-Py, IPFS
- Transaction Manager (key-pair table)
- 24 testes (unitarios + API)

**Estado**: Completo. Servico em `services/egw-controller/`.

### Fase 7 — Integração, CI/CD e Documentação
- **7A**: Docker Compose raiz (~20 containers), GitHub Actions (CI + Yocto)
- **7B**: 7 documentos de arquitetura (MQTT, Ditto, Fabric, Indy, IPFS, EGW Controller, UC flows)
- **7C**: Atualizacao de README, system-architecture, milestone-plan, .gitignore, edgegateway-image.bb, tasks.json

**Estado**: Completo.

## Próximos Passos
1. Conectar dispositivos reais e validar fluxo end-to-end
2. Instrumentar observabilidade (Prometheus, Grafana)
3. Preparar pilotos com utilizadores selecionados
4. Auditorias de seguranca e compliance

> Última revisão: 2026-03-20
