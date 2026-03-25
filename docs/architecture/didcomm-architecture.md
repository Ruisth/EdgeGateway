# Arquitectura DIDComm — Hyperledger Aries / ACA-py (C2DTA)

Este documento descreve a camada de identidade auto-soberana (SSI) e comunicação peer-to-peer do Edge Gateway, conforme definida no paper:
> Pinto et al., *"Consumer-Controlled Digital Twin Architecture"*, Blockchain: Research and Applications, 2025. DOI: 10.1016/j.bcra.2025.100342

O stack definitivo usa **Hyperledger Aries / ACA-py** e **DIDComm v2**. O serviço em `services/didcomm-agent/` é um protótipo experimental de criptografia (X25519+ChaCha20-Poly1305) e **não** representa o stack do paper.

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

**Nota sobre agentes não-self-sovereign**: O EGW e o SD hospedam agentes ACA-py localmente mas dependem do mediator para receber mensagens quando offline. O DID público é gerado no 1.º boot e ancorado no Identity Ledger (Hyperledger Indy / BC Gov Test Network).

---

## Aries RFCs utilizados

| RFC | Nome | Utilização no C2DTA |
| --- | --- | --- |
| **RFC 0434** | Out-of-Band Invitations | Descoberta inicial entre agentes (QR code no SD, deep link) |
| **RFC 0160** | Connection Protocol | Estabelecimento de conexão DIDComm entre dois agentes |
| **RFC 0453** | Issue Credential v2 | Emissão de Enrollment VC, Genesis VC e Ownership VC |
| **RFC 0454** | Present Proof v2 | Verificação de VCs (claim, compra, twinning) |
| **RFC 0509** | Action Menu | Menu de acções interactivas (list devices, claim, twin, sell...) |
| **RFC 0028** | Introduce | Apresentação de um agente a outro (ex: OEM apresenta EGW ao SD) |
| **RFC 0214** | Help Me Discover | Resolução de serviços/endpoints desconhecidos |
| **RFC 0095** | Basic Message | Mensagens de texto simples (notificações, debug) |
| **RFC 0046** | Mediators and Relays | Suporte a mediadores para agentes sem endpoint público (SD, consumer mobile) |
| **RFC 0183** | Revocation Notification | Notificação de revogação de VC (ex: SD selling, untwinning) |

---

## Goal Codes (C2DTA)

Os goal codes identificam o propósito de uma invitação OOB (RFC 0434) e determinam o fluxo DIDComm a executar.

| Goal Code | Actor iniciador | Fluxo resultante |
| --- | --- | --- |
| `c2dt.consortium.enroll.OEM` | Consortium (`1@C`) → OEM (`1@O`) | Emissão de Enrollment VC |
| `c2dt.oem.register.devicemodel` | OEM (`1@O`) → Consortium/Ledger | Registo de DeviceModel no Fabric |
| `c2dt.oem.register.device` | OEM (`1@O`) → EGW/SD (`1@egw`/`1@sd`) | Emissão de Genesis VC + registo no Fabric |
| `c2dt.consumer.buydevice` | OEM (`1@O`) → Consumer (`1@A`) | Emissão de Ownership VC |
| `c2dt.consumer.claim` | Consumer (`1@A`) → EGW (`1@egw`) | Verificação de VCs + `status: CLAIMED` no Fabric |
| `c2dt.consumer.twin` | Consumer (`1@A`) → EGW (`1@egw`) | Twinning (WoT + MQTT + Ditto) + `status: TWINNED` |
| `c2dt.consumer.untwin` | Consumer (`1@A`) → EGW (`1@egw`) | Untwinning + `status: CLAIMED` |
| `c2dt.consumer.sell` | Consumer (`1@A`) → EGW (`1@egw`) + OEM | Revogação de Ownership VC + nova Ownership VC para comprador |

---

## Verifiable Credentials

### Enrollment VC
- **Emissor**: Consortium agent (`1@C`)
- **Portador**: OEM agent (`1@O`)
- **Atributos**: `name`, `type: OEM`, `enrollDate`
- **RFC**: 0453 Issue Credential v2
- **Propósito**: prova que o OEM é membro do consórcio; necessária para registar DeviceModels e emitir Genesis VCs

### Genesis VC
- **Emissor**: OEM agent (`1@O`)
- **Portador**: EGW agent (`1@egw`) ou SD agent (`1@sd`)
- **Atributos**: `deviceId`, `deviceModelId`, `manufacturerDate`
- **RFC**: 0453 Issue Credential v2
- **Propósito**: prova de proveniência do dispositivo; apresentada pelo consumidor no "claim"

### Ownership VC
- **Emissor**: OEM agent (`1@O`) ou EGW agent (`1@egw`)
- **Portador**: Consumer agent (`1@A` / `1@B`)
- **Atributos**: `deviceId`, `deviceModelId`, `acquisitionDate`
- **RFC**: 0453 Issue Credential v2; revogação via RFC 0183
- **Propósito**: comprova que o consumidor é o dono do dispositivo; necessária para claim, twinning e selling

---

## Fluxos DIDComm por cenário

### Cenário 1 — OEM enroll no consórcio
```
1@C ──OOB invitation (goal: enroll.OEM)──> 1@O
1@C ──RFC 0160 Connection──> 1@O
1@C ──RFC 0453 Issue Credential (Enrollment VC)──> 1@O
```

### Cenário 2 — Registo de modelo de dispositivo
```
1@O ──RFC 0454 Present Proof (Enrollment VC)──> Fabric gateway
Fabric ──record DeviceModel──> Ecosystem Ledger
```

### Cenário 3 — Auto-registo do dispositivo (1.º boot)
```
EGW/SD: gera DID público + ancora no Indy
EGW/SD: regista no Fabric (status: MANUFACTURED)
1@O ──RFC 0453 Issue Credential (Genesis VC)──> 1@egw / 1@sd
Fabric: status → AVAILABLE
```

### Cenário 4 — Consumidor compra dispositivo
```
1@O ──OOB invitation (goal: buydevice)──> 1@A
1@O ──RFC 0453 Issue Credential (Ownership VC)──> 1@A
Fabric: status → IN-TRANSIT
```

### Cenário 5 — Consumidor "claims" dispositivo
```
1@A ──OOB scan (QR code do EGW)──> 1@egw
1@A ──RFC 0454 Present Proof (Ownership VC + Genesis VC)──> 1@egw
1@egw ──verifica VCs no Indy──> OK
1@egw ──Fabric update──> status: CLAIMED, controllerId: A
```

### Cenário 6 — SD twinning
```
1@A ──RFC 0509 Action Menu (twin)──> 1@egw
1@egw: carrega WoT Thing Description do SD
1@egw: cria Thing no Eclipse Ditto
1@egw: configura MQTT client (SD → Mosquitto → Ditto)
1@egw ──Fabric update──> status: TWINNED
```

### Cenário 7 — SD untwinning
```
1@A ──RFC 0509 Action Menu (untwin)──> 1@egw
1@egw: remove Thing do Eclipse Ditto + desliga MQTT client
1@egw ──Fabric update──> status: CLAIMED
```

### Cenário 8 — SD selling
```
1@A ──RFC 0509 Action Menu (sell)──> 1@egw + 1@O
1@O ──RFC 0183 Revocation Notification──> 1@A  (revoga Ownership VC de A)
1@O ──RFC 0453 Issue Credential (nova Ownership VC)──> 1@B  (novo dono)
1@egw ──Fabric update──> status: IN-TRANSIT
```

---

## DID e Identity Ledger

- **Identity Ledger**: Hyperledger Indy (BC Gov Test Network)
- **DID method**: `did:indy`
- **Criação**: no 1.º boot do EGW/SD, o agente ACA-py gera um par de chaves Ed25519, cria um DID e publica o DID Document no Indy
- **Resolução**: agentes resolvem DIDs via Universal Resolver ou conexão directa ao Indy pool
- **Tempo de criação de DID público**: ~1.3 s (benchmark do paper)
- **Chaves**: Ed25519 para assinatura de VCs; X25519 para envelope DIDComm (ECDH-1PU / anoncrypt)
- **Armazenamento seguro**: TPM para chaves privadas quando disponível; ACA-py wallet encriptada (Indy SDK / Askar wallet)

---

## Mediadores

Os mediadores permitem que agentes sem endpoint público (SD embarcado, consumer mobile) recebam mensagens DIDComm:

| Agente | Mediador | Protocolo |
| --- | --- | --- |
| `1@egw` | `2@egw` (SSIaaS) | RFC 0046 |
| `1@sd` | `2@sd` (SSIaaS) | RFC 0046 |
| `1@A` | `2@A` (SSIaaS) | RFC 0046 |

O EGW regista `2@egw` como mediador default no arranque. Mensagens para `1@egw` chegam via `2@egw` → forward → EGW local.

---

## Segurança

- **DIDComm envelope**: anoncrypt (X25519 ECDH-ES + A256CBC-HS512) para mensagens sem autenticação prévia; authcrypt (ECDH-1PU) para mensagens autenticadas
- **Chaves privadas**: armazenadas na Askar wallet (ACA-py), cifrada em repouso; idealmente delegada ao TPM via PKCS#11
- **mTLS**: entre serviços internos (ACA-py ↔ Fabric gateway, ACA-py ↔ Ditto REST API)
- **VC revogation**: Indy revocation registry (AnonCreds); agentes verificam o estado de revogação antes de aceitar provas
- **Replay prevention**: nonce por mensagem DIDComm; timestamps validados

---

## Integração com outros componentes

| Componente | Interface | Propósito |
| --- | --- | --- |
| Eclipse Ditto | REST API (HTTP) | Criar/remover Things, ler estado do DT |
| Hyperledger Fabric | Fabric SDK (Python) | Actualizar ciclo de vida do dispositivo |
| Hyperledger Indy | ACA-py built-in | Resolver DIDs, publicar credencials, verificar provas |
| Eclipse Mosquitto | MQTT client (paho) | Subscrever tópicos do SD para alimentar o Ditto |
| IPFS (Kubo) | HTTP API (`/api/v0/add`) | Fazer upload de datasets históricos |

---

## Checklist de actualização

- [ ] Testar fluxo de OOB invitation (RFC 0434) com ACA-py em ambiente local
- [ ] Confirmar goal codes com equipa de produto
- [ ] Integrar VC revocation registry no Indy pool
- [ ] Automatizar testes de cada cenário com Aries Test Harness (ATH)

> Última revisão: 2026-03-19
