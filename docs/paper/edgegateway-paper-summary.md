# Resumo do paper C2DTA

**Título**: "Consumer-Controlled Digital Twin Architecture: How blockchain technology gives consumers control over their smart devices' digital twins and data"
**Autores**: Filipe Pinto et al. (ISCTE-IUL, Lisboa)
**Publicação**: *Blockchain: Research and Applications*, Elsevier, 2025
**DOI**: [10.1016/j.bcra.2025.100342](https://doi.org/10.1016/j.bcra.2025.100342)

---

## 1. Visão geral

O paper propõe a **Consumer-Controlled Digital Twin Architecture (C2DTA)** — uma arquitectura que transfere o Digital Twin (DT) do dispositivo inteligente da cloud para o edge sob controlo efectivo do consumidor.

Problemas resolvidos:
- Digital Twins actuais são controlados pelo fabricante (OEM) ou pelo provedor de cloud, não pelo consumidor
- Dados dos dispositivos saem do edge sem consentimento explícito
- Não existe mecanismo de prova de proveniência do dispositivo verificável

Solução: arquitectura de 5 camadas com identidade auto-soberana (SSI), blockchain dual (Fabric + Indy) e Digital Twin local no edge.

---

## 2. Arquitectura C2DTA (5 camadas — Figura 9 do paper)

```
Business Edge        → Consortium agent, OEM agents (ACA-py), SSIaaS providers
Ecosystem Layer      → Consortium website, Decentralized Marketplace app
Peer-to-Peer Layer   → DIDComm v2 (Hyperledger Aries RFCs)
Records Layer        → Fabric (device lifecycle) + Indy (DIDs/VCs) + IPFS (datasets)
Consumer Edge        → Edge Gateway (EGW) + Smart Device (SD) + Eclipse Ditto
```

---

## 3. Stack tecnológico

| Componente | Tecnologia | Versão |
| --- | --- | --- |
| Digital Twin platform | Eclipse Ditto | 3.0.0 |
| MQTT broker | Eclipse Mosquitto | 2.0.15 |
| Ecosystem ledger | Hyperledger Fabric | 2.x |
| Identity ledger | Hyperledger Indy | BC Gov Test Network |
| SSI agents | ACA-py (Hyperledger Aries) | latest |
| Decentralized storage | IPFS (Kubo) | latest |
| Device definition | W3C WoT Thing Description | 1.1 |
| OS | Yocto Project (Kirkstone) | 4.0 |
| Sensor simulator | Python (heartbeat, geoloc, timestamp @ 1 Hz) | — |

---

## 4. Tipos de dispositivos

### Edge Gateway (EGW)
- Plataforma Linux embarcada (Yocto + OCI containers)
- Hospeda: ACA-py agent (`1@egw`), Eclipse Ditto 3.0, Eclipse Mosquitto 2.0
- Gera DID público no 1.º boot, ancorado no Indy
- Interface com Ecosystem Ledger (Fabric) e Identity Ledger (Indy)
- Transfere datasets históricos para IPFS em intervalos configuráveis

### Smart Device (SD)
- Dispositivo IoT com firmware C2DTA
- Agente SSI (`1@sd`) com mediator cloud (`2@sd`)
- Transmite dados via MQTT/SSL para o EGW
- QR code com OOB URI para o seu agente

---

## 5. Ciclo de vida do Smart Device (6 estados)

```
Manufactured → Available → In-Transit → Claimed → Twinned → Decommissioned
```

| Estado | Trigger | Actor | Ledger update |
| --- | --- | --- | --- |
| Manufactured | 1.º boot + Genesis VC | OEM | `status: AVAILABLE` |
| Available | Registado → listado para venda | OEM | marketplace listing |
| In-Transit | Venda concluída, Ownership VC emitida | OEM | `status: IN-TRANSIT` |
| Claimed | Consumidor valida Ownership VC + Genesis VC | EGW | `status: CLAIMED, controllerId` |
| Twinned | Consumidor inicia twinning (WoT + MQTT) | EGW | `status: TWINNED` |
| Decommissioned | Fim de vida | EGW / Consortium | `status: DECOMMISSIONED` |

---

## 6. Verifiable Credentials

| VC | Emissor | Portador | Propósito |
| --- | --- | --- | --- |
| **Enrollment VC** | Consortium (`1@C`) | OEM (`1@O`) | Membros do consórcio |
| **Genesis VC** | OEM (`1@O`) | EGW / SD | Proveniência do dispositivo |
| **Ownership VC** | OEM / EGW | Consumidor (`1@A`) | Controlo sobre o dispositivo |

---

## 7. Dual Blockchain

### Ecosystem Ledger (Hyperledger Fabric — permissioned)
- Rastreia ciclo de vida dos dispositivos: `DeviceModel`, `Device`, `Transaction`, `DataSet`
- Imutável e auditável
- Apenas membros do consórcio têm acesso de escrita

### Identity Ledger (Hyperledger Indy — public permissioned)
- Ancora DIDs públicos (EGW, SD, Consortium, OEM, Consumers)
- Anchora schemas e credential definitions para AnonCreds
- Permite verificação universal de VCs sem contactar o emissor

---

## 8. Cenários funcionais (8 cenários do paper)

| # | Cenário | Actores | VCs envolvidas |
| --- | --- | --- | --- |
| 1 | OEM enroll no consórcio | Consortium + OEM | Enrollment VC |
| 2 | Registo de modelo de dispositivo | OEM + Fabric | — |
| 3 | Auto-registo do dispositivo (1.º boot) | OEM + EGW/SD + Indy | Genesis VC |
| 4 | Consumidor compra dispositivo | OEM + Consumer | Ownership VC |
| 5 | Consumidor "claims" dispositivo | Consumer + EGW | Genesis VC + Ownership VC |
| 6 | SD twinning (WoT + MQTT + Ditto + IPFS) | Consumer + EGW + SD | — |
| 7 | SD untwinning | Consumer + EGW | — |
| 8 | SD selling (com revogação de VC) | Consumer + OEM + EGW | Ownership VC (revogação + nova) |

---

## 9. Benchmarks de desempenho (Tabela do paper)

| Operação | Tempo medido | Notas |
| --- | --- | --- |
| Ligação OOB DIDComm | ~50 ms | Sem acesso ao ledger |
| Ligação implícita (resolve DIDDoc) | ~1.7 s | Requer acesso ao Identity Ledger |
| Criação de DID público | ~1.3 s | Criptografia + ledger write |
| Escrita no Ecosystem Ledger (Fabric) | ~2 s | Operação mais lenta |
| Emissão de VC | ~1 s | Assinatura digital |
| Boot Eclipse Ditto | ~38 s | Apenas no 1.º twinning |
| Configuração MQTT client | ~66 s | Apenas no 1.º twinning |
| Latência máxima adicional DIDComm | < 2 s | Aceitável para interacções utilizador |

---

## 10. Requisitos transversais

- **Segurança**: boot seguro, TPM para chaves privadas, mTLS entre serviços, MQTT sobre SSL
- **Privacidade**: dados ficam no consumer edge; apenas hashes dos datasets são ancorados no Fabric
- **GDPR/LGPD**: dados não saem do edge sem consentimento explícito do consumidor
- **Auditabilidade**: todas as transacções de ciclo de vida registadas no Fabric (imutável)
- **Identidade**: DIDs auto-gerados no 1.º boot, sem dependência de identidades pré-configuradas pelo fabricante

---

## 11. Documentação relacionada

| Ficheiro | Conteúdo |
| --- | --- |
| `docs/architecture/system-architecture.md` | 5 camadas, structs Fabric, state machine, benchmarks |
| `docs/architecture/didcomm-architecture.md` | Aries RFCs, VCs, goal codes, 8 cenários DIDComm |
| `docs/architecture/communication-and-dataflow.md` | SD→MQTT→Ditto→IPFS pipeline detalhado |
| `docs/roadmaps/milestone-plan.md` | Fases de implementação com 8 cenários como KPIs |

> Última revisão: 2026-03-19
