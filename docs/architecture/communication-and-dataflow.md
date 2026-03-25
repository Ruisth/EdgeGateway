# Fluxos de Comunicação e Dados — C2DTA

Este documento descreve os pipelines de dados do Edge Gateway conforme definidos no paper:
> Pinto et al., *"Consumer-Controlled Digital Twin Architecture"*, Blockchain: Research and Applications, 2025. DOI: 10.1016/j.bcra.2025.100342

Existem dois planos de comunicação completamente separados:
1. **Plano de dados de sensores** — SD → MQTT → Mosquitto → Eclipse Ditto
2. **Plano de identidade/controlo** — DIDComm v2 via Hyperledger Aries/ACA-py

---

## Visão geral da topologia

```
┌──────────────────────────────────────────────────────────────────────┐
│  SMART DEVICE (SD)                                                    │
│  Sensor simulator (Python, 1 Hz)                                      │
│  heartbeat · geolocation · timestamp                                  │
│  └─ MQTT/SSL ──────────────────────────────────────────────────────┐ │
│  ACA-py agent (1@sd) ─ DIDComm ─────────────────────────────────┐ │ │
└──────────────────────────────────────────────────────────────────│─┘ │
                                                                   │   │
┌──────────────────────────────────────────────────────────────────│───┘
│  EDGE GATEWAY (EGW)                                               │
│                                                                   │
│  ┌─────────────────────────┐   ┌──────────────────────────────┐  │
│  │  Eclipse Mosquitto 2.0  │   │  ACA-py agent (1@egw)        │  │
│  │  MQTT broker (SSL/TLS)  │   │  DIDComm v2                  │◄─┘
│  │  tópico: sd/{id}/data   │   │  Goal codes, RFCs, VCs       │
│  └────────────┬────────────┘   └──────────────┬───────────────┘
│               │ Ditto Protocol                │
│               ▼                               │ Fabric SDK
│  ┌─────────────────────────┐   ┌──────────────▼───────────────┐
│  │  Eclipse Ditto 3.0      │   │  Hyperledger Fabric client   │
│  │  Things service         │   │  (Ecosystem Ledger)          │
│  │  WebSocket / HTTP API   │   │  device lifecycle updates    │
│  └────────────┬────────────┘   └──────────────────────────────┘
│               │ dataset export (intervalos)
│               ▼
│  ┌─────────────────────────┐
│  │  IPFS (Kubo)            │
│  │  dataset upload         │
│  │  CID → Fabric DataSet   │
│  └─────────────────────────┘
└──────────────────────────────────────────────────────────────────────┘
```

---

## Pipeline 1 — Dados de sensores (SD → Ditto)

### Fluxo passo a passo

```
SD (sensor simulator, 1 Hz)
  │ MQTT PUBLISH  QoS 1
  │ tópico: sd/{deviceId}/sensors
  │ payload: { heartbeat, geolocation, timestamp }
  │ transporte: MQTT sobre SSL (porta 8883)
  ▼
Eclipse Mosquitto 2.0 (EGW)
  │ autenticação: certificado cliente do SD
  │ ACL: apenas o SD autenticado pode publicar no seu tópico
  ▼
Eclipse Ditto 3.0 — Connectivity service
  │ Ditto Protocol: mapeamento tópico MQTT → Thing attribute
  │ Thing ID: {deviceId}:{namespace}
  ▼
Eclipse Ditto — Things service
  │ actualiza Thing state
  │ emite change event (SSE / WebSocket)
  ▼
Consumidor / aplicação externa
  (subscreve via Ditto WebSocket ou HTTP SSE)
```

### Formato de mensagem (Ditto Protocol)

```json
{
  "topic": "{namespace}/{deviceId}/things/twin/commands/modify",
  "headers": { "content-type": "application/json" },
  "path": "/features/sensors/properties",
  "value": {
    "heartbeat": 72,
    "geolocation": { "lat": 38.736, "lon": -9.142 },
    "timestamp": "2026-03-19T10:00:00Z"
  }
}
```

### Configuração de twinning (Cenário 6)

O twinning é iniciado pelo EGW agent (1@egw) após verificação de VCs:
1. Carrega **W3C WoT Thing Description** do modelo do SD (de `services/wot/`)
2. Cria o Thing no Ditto via REST API (`PUT /api/2/things/{thingId}`)
3. Cria a **Ditto Connection** para o Mosquitto broker (MQTT source)
4. A partir deste momento, mensagens MQTT do SD chegam automaticamente ao Ditto

**Benchmark (paper)**: configuração de MQTT client no primeiro twinning ≈ 66 s; Eclipse Ditto boot ≈ 38 s.

---

## Pipeline 2 — Actualizações de ciclo de vida (EGW → Fabric)

O EGW agent (ACA-py) faz chamadas ao Hyperledger Fabric em cada transição de estado:

| Evento | Transição | Fabric operation |
| --- | --- | --- |
| Registo inicial | MANUFACTURED → AVAILABLE | `CreateDevice(deviceId, controllerId, status)` |
| Venda | AVAILABLE → IN-TRANSIT | `UpdateDeviceStatus(deviceId, IN-TRANSIT)` |
| Claim | IN-TRANSIT → CLAIMED | `UpdateDeviceStatus(deviceId, CLAIMED, controllerId)` |
| Twinning | CLAIMED → TWINNED | `UpdateDeviceStatus(deviceId, TWINNED)` |
| Untwinning | TWINNED → CLAIMED | `UpdateDeviceStatus(deviceId, CLAIMED)` |
| Selling | CLAIMED → IN-TRANSIT | `TransferDevice(deviceId, newControllerId)` |
| Fim de vida | any → DECOMMISSIONED | `UpdateDeviceStatus(deviceId, DECOMMISSIONED)` |

**Benchmark (paper)**: escrita no Fabric ≈ 2 s (operação mais lenta).

---

## Pipeline 3 — Datasets históricos (Ditto → IPFS → Fabric)

Em intervalos configuráveis (ex: diário), o EGW exporta dados históricos do Ditto para IPFS:

```
Eclipse Ditto
  │ exporta snapshot do Thing state (JSON/CSV)
  │ assina com chave privada do EGW
  ▼
IPFS (Kubo) — HTTP API /api/v0/add
  │ retorna CID (Content Identifier)
  ▼
ACA-py agent (1@egw)
  │ cria registo DataSet no Fabric:
  │   { datasetId, datasetURL: CID, deviceId,
  │     controllerId, hash, timestamp }
  ▼
Hyperledger Fabric (Ecosystem Ledger)
  (imutável — apenas o hash é ancorado, dados ficam no IPFS)
```

**Nota de privacidade**: apenas o hash do dataset é ancorado no Fabric. Os dados brutos ficam no IPFS, acessíveis apenas a quem tem o CID — que permanece sob controlo do consumidor.

---

## Pipeline 4 — Identidade e controlo (DIDComm P2P)

O plano DIDComm é **completamente separado** do pipeline de sensores. Corre sobre o ACA-py agent e usa o Identity Ledger (Hyperledger Indy) para resolver DIDs e verificar VCs.

```
Consumer mobile wallet (1@A)
  │ DIDComm v2 (HTTPS / WebSocket)
  │ via mediator 2@A (SSIaaS)
  ▼
2@egw mediator (SSIaaS)
  │ forward para EGW
  ▼
ACA-py agent (1@egw)  ←──── Hyperledger Indy (DID resolve, VC verify)
  │
  ├─ controla Eclipse Ditto (REST API)
  ├─ actualiza Hyperledger Fabric (SDK)
  └─ gere IPFS uploads
```

Ver [didcomm-architecture.md](didcomm-architecture.md) para detalhe dos fluxos DIDComm por cenário.

---

## Segurança dos canais

| Canal | Protocolo | Autenticação |
| --- | --- | --- |
| SD → Mosquitto | MQTT over TLS (porta 8883) | Certificado cliente X.509 do SD |
| Mosquitto → Ditto | MQTT interno (localhost) | ACL interna |
| ACA-py → Fabric | gRPC + TLS | Certificado MSP do Fabric |
| ACA-py → Ditto | HTTPS REST | API key / Basic Auth (local) |
| ACA-py → IPFS | HTTP (localhost) | N/A (IPFS local node) |
| Consumer → EGW | DIDComm v2 (HTTPS) | DID authcrypt / anoncrypt |
| EGW → Indy | TCP pool | Indy node credentials |

---

## QoS e latências (benchmarks do paper)

| Operação | Latência medida | Notas |
| --- | --- | --- |
| Ligação OOB DIDComm | ~50 ms | Sem acesso ao ledger |
| Ligação implícita (resolve DIDDoc) | ~1.7 s | Requer acesso ao Indy |
| Criação de DID público | ~1.3 s | Criptografia + ledger write |
| Escrita no Fabric | ~2 s | Operação mais lenta |
| Emissão de VC | ~1 s | Assinatura digital |
| Boot Eclipse Ditto | ~38 s | Apenas no 1.º twinning |
| Configuração MQTT client | ~66 s | Apenas no 1.º twinning |
| Latência adicional DIDComm | < 2 s | Aceitável para interacções utilizador |
| Telemetria MQTT (SD → Ditto) | < 200 ms | Operação normal contínua |

---

## Observabilidade

- **Mosquitto**: métricas via `$SYS/` topics (connected clients, messages/s, bytes/s)
- **Eclipse Ditto**: `/status` endpoint + Prometheus metrics (throughput, errors, latency)
- **ACA-py**: logs estruturados (JSON); webhook para eventos de credencial/conexão
- **Fabric**: peer metrics (Prometheus); chaincode logs
- **IPFS**: `/api/v0/stats/bw` para bandwidth; `/api/v0/repo/stat` para storage

---

## Checklist de actualização

- [ ] Criar `communication-flow.puml` (sequence diagram PlantUML)
- [ ] Definir JSON Schema para payload MQTT do SD (heartbeat, geoloc, timestamp)
- [ ] Documentar procedimento de failover do Mosquitto broker
- [ ] Testar pipeline completo SD → Mosquitto → Ditto em ambiente Docker local

> Última revisão: 2026-03-19
