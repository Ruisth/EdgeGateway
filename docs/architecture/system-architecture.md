# Arquitectura de Sistema — Consumer-Controlled Digital Twin Architecture (C2DTA)

Este documento descreve a arquitectura do Edge Gateway tal como definida no paper:
> Pinto et al., *"Consumer-Controlled Digital Twin Architecture"*, Blockchain: Research and Applications, 2025. DOI: 10.1016/j.bcra.2025.100342

---

## 5 Camadas C2DTA (Figura 9 do paper)

```
┌──────────────────────────────────────────────────────────────────────┐
│  BUSINESS EDGE                                                        │
│  Consortium (SSIaaS provider) · OEM agents (ACA-py, cloud)           │
│  SSIaaS: Digital Wallet providers · Mediator services                │
├──────────────────────────────────────────────────────────────────────┤
│  ECOSYSTEM LAYER                                                      │
│  Consortium Marketing Website · Decentralized Marketplace App        │
├──────────────────────────────────────────────────────────────────────┤
│  PEER-TO-PEER LAYER                                                   │
│  DIDComm v2 (Hyperledger Aries RFCs)                                 │
│  OOB invitations · Goal codes · Action menus · Credential exchange   │
├──────────────────────────────────────────────────────────────────────┤
│  RECORDS LAYER                                                        │
│  Ecosystem Ledger (Hyperledger Fabric) ← device lifecycle + datasets │
│  Identity Ledger (Hyperledger Indy)   ← DIDs + VCs                  │
│  Decentralized Storage (IPFS)         ← dataset files (off-chain)   │
├──────────────────────────────────────────────────────────────────────┤
│  CONSUMER EDGE                                                        │
│  Edge Gateway (EGW) · Smart Device (SD) · Digital Twin (Ditto)      │
│  EGW hosts: ACA-py agent · Eclipse Ditto · Eclipse Mosquitto         │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Tipos de dispositivos

### Edge Gateway (EGW)
- Plataforma Linux embarcada (Yocto Project + OCI containers)
- **Funções**:
  1. Hub de conectividade — liga SDs ao ecossistema via DIDComm
  2. Hospeda o Digital Twin platform (Eclipse Ditto 3.0)
  3. Corre o broker MQTT (Eclipse Mosquitto 2.0) para dados de sensores
  4. Interface com Ecosystem Ledger (Hyperledger Fabric) — actualizações de estado
  5. Interface com Identity Ledger (Hyperledger Indy) — emissão/verificação de VCs
  6. Transfere datasets históricos para IPFS em intervalos configuráveis
- **Identidade**: gera DID público no 1.º boot; âncora na Identity Ledger
- **Agent notation**: `1@egw` (SSI notation per Aries RFC 0006)

### Smart Device (SD)
- Qualquer dispositivo IoT com firmware C2DTA
- Gera UUID no 1.º boot
- Corre agente SSI (ACA-py) com mediator service na cloud
- Transmite dados de sensores via MQTT/SSL para o EGW
- Possui QR code com OOB URI para o seu agente
- **Agent notation**: `1@sd`, mediator: `2@sd`

---

## Ciclo de vida do Smart Device (6 estados)

```
              Register (1st boot)
Manufactured ──────────────────> Available
                                     │
                              Sold   │
                                     ▼
                               In-Transit
                                     │
                              Claim  │
                                     ▼
                                 Claimed
                                     │
                              Twin   │  Untwin
                                     ▼         \
                                  Twinned ──────> Claimed
                                     │
                           End-of-life│
                                     ▼
                              Decommissioned
```

| Estado | Trigger | Actor | Ledger update |
| --- | --- | --- | --- |
| Manufactured | 1.º boot + Genesis VC | OEM | `status: AVAILABLE` |
| Available | SD registada → listada para venda | OEM | marketplace listing |
| In-Transit | Venda concluída, Ownership VC emitida | OEM | `status: IN-TRANSIT` |
| Claimed | Consumidor valida Ownership VC + Genesis VC | EGW | `status: CLAIMED, controllerId` |
| Twinned | Consumidor inicia twinning (WoT + MQTT) | EGW | `status: TWINNED` |
| Decommissioned | Fim de vida | EGW / Consortium | `status: DECOMMISSIONED` |

---

## Verifiable Credentials

| VC | Emissor | Portador | Atributos principais |
| --- | --- | --- | --- |
| **Enrollment VC** | Consortium agent (`1@C`) | OEM agent (`1@O`) | `name`, `type: OEM`, `enrollDate` |
| **Genesis VC** | OEM agent (`1@O`) | EGW / SD agent | `deviceId`, `deviceModelId`, `manufacturerDate` |
| **Ownership VC** | OEM / EGW agent | Consumer agent (`1@A`) | `deviceId`, `deviceModelId`, `acquisitionDate` |

---

## Estruturas de dados no Ecosystem Ledger (Hyperledger Fabric)

```go
DeviceModel struct {
    name          string
    deviceModelId string
    description   string
    features      []string
    timestamp     time.Time
}

Device struct {
    deviceId          string
    controllerId      string
    deviceModelId     string
    type              string  // "EDGE_GATEWAY" | "SMART_DEVICE"
    status            string  // 6-state lifecycle
    OTId              string
    allowedTransactions []string
    timestamp         time.Time
}

Transaction struct {
    type      string  // "sale", etc.
    details   []string
    timestamp time.Time
}

DataSet struct {
    datasetId    string
    datasetURL   string  // IPFS CID
    id           string
    controllerId string
    deviceId     string
    hash         string
    timestamp    time.Time
}
```

---

## Agentes SSI (Aries RFC 0006 notation)

| Notação | Actor | Tipo | Hospedagem |
| --- | --- | --- | --- |
| `1@C` | Consortium agent | Self-sovereign | Cloud (Consortium) |
| `1@O` | OEM agent | Self-sovereign | Cloud (OEM) |
| `1@D` | OEM employee (Dave) | Self-sovereign | Mobile wallet |
| `1@A` / `1@B` | Consumer agents (Alice, Bob) | Self-sovereign | Mobile wallet + mediator |
| `2@A` | Alice cloud agent | Mediator | SSIaaS provider |
| `1@egw` | EGW agent | Non-self-sovereign | Consumer edge (EGW) |
| `2@egw` | EGW mediator agent | Mediator | SSIaaS provider |
| `1@sd` | SD agent | Non-self-sovereign | Smart Device |
| `2@sd` | SD mediator agent | Mediator | SSIaaS provider |

---

## Stack de implementação

| Componente | Tecnologia | Versão |
| --- | --- | --- |
| Digital Twin platform | Eclipse Ditto | 3.0.0 |
| MQTT broker | Eclipse Mosquitto | 2.0.15 |
| Ecosystem ledger | Hyperledger Fabric | 2.x |
| Identity ledger | Hyperledger Indy | BC Gov Test Network |
| SSI agents | ACA-py (Hyperledger Aries) | latest |
| Decentralized storage | IPFS (Kubo) | latest |
| Device definition | W3C WoT Thing Description | 1.1 |
| OS base | Yocto Project (Kirkstone) | 4.0 |
| Container runtime | Docker / Podman | - |
| Sensor simulator | Python (heartbeat, geoloc, timestamp @ 1 Hz) | - |

---

## Requisitos transversais

- **Segurança**: boot seguro, TPM para armazenamento de chaves, mTLS entre serviços, MQTT sobre SSL
- **Identidade**: DIDs auto-gerados no 1.º boot, sem dependência de identidades pré-configuradas pelo fabricante
- **Privacidade**: dados permanecem no consumer edge; apenas hashes dos datasets são ancorados no Fabric
- **Compliance**: GDPR/LGPD — dados não saem do edge sem consentimento explícito do consumidor
- **Auditabilidade**: todas as transacções de ciclo de vida registadas no Ecosystem Ledger (imutável)

---

## Critérios de desempenho (benchmarks do paper)

| Operação | Tempo medido | Notas |
| --- | --- | --- |
| Ligação OOB DIDComm | ~50 ms | Sem acesso ao ledger |
| Ligação implícita (resolve DIDDoc) | ~1.7 s | Requer acesso ao Identity Ledger |
| Criação de DID público | ~1.3 s | Operação criptográfica + ledger |
| Escrita no Ecosystem Ledger (Fabric) | ~2 s | Operação mais lenta (ledger write) |
| Emissão de VC | ~1 s | Assinatura digital |
| Boot Eclipse Ditto | ~38 s | Apenas no 1.º twinning |
| Configuração MQTT client | ~66 s | Apenas no 1.º twinning |
| Latência máxima adicionada por DIDComm | < 2 s | Aceitável para interacções com utilizador |

---

## Checklist de actualização

- [ ] Diagrama actualizado após alterações estruturais
- [ ] Tabela de métricas revista com dados de hardware real
- [ ] Links para ADRs em `docs/adr/` (a criar)

> Última revisão: 2026-03-19
