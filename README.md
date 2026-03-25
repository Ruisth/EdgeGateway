# Edge Gateway — Consumer-Controlled Digital Twin Architecture (C2DTA)

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
