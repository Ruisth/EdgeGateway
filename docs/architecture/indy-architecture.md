# Arquitetura Hyperledger Indy (Identity Ledger)

## Visao Geral

O Hyperledger Indy serve como identity ledger da arquitetura C2DTA, suportando Self-Sovereign Identity (SSI) para todos os stakeholders. Utiliza a distribuicao von-network (BCGov) com 4 nos locais.

## Topologia

| Componente | Container | Porta |
|---|---|---|
| Indy Pool (4 nos) | `c2dta-indy-pool` | 9701-9704 |
| Web UI | — | 9000 |

- **Steward Seed**: `C2DTA000000000000000000Steward1`
- **Genesis**: Auto-gerado pelo von-network

## Agentes ACA-Py

Cada stakeholder tem um agente ACA-Py (Aries Cloud Agent Python) dedicado:

| Agente | Notacao RFC 0006 | Admin API | HTTP Endpoint | Papel |
|---|---|---|---|---|
| Consortium | 1@C | 8021 | 8020 | Issuer Enrollment VC, Steward |
| OEM | 1@O | 8031 | 8030 | Issuer Genesis VC, Holder Enrollment |
| Consumer A | 1@A | 8041 | 8040 | Holder Ownership VC |
| Edge Gateway | 1@egw | 8061 | 8060 | Holder Genesis VC |
| Smart Device | 1@sd | 8071 | 8070 | UUID-based identity |

## Schemas de Verifiable Credentials

### Enrollment VC (UC1)

Emitida pelo Consorcio ao OEM apos aprovacao de inscricao.

| Atributo | Tipo | Descricao |
|---|---|---|
| `organization_name` | string | Nome da organizacao |
| `organization_did` | string | DID publico da org |
| `role` | string | Papel no consorcio (OEM, Retailer) |
| `enrollment_date` | string | Data de inscricao (ISO 8601) |
| `consortium_id` | string | ID do consorcio |
| `expiry_date` | string | Data de expiracao |

### Genesis VC (UC3)

Emitida pelo OEM ao dispositivo (EGW ou SD) no primeiro boot.

| Atributo | Tipo | Descricao |
|---|---|---|
| `device_uuid` | string | UUID unico do dispositivo |
| `model_id` | string | ID do modelo |
| `manufacturer_did` | string | DID do fabricante |
| `manufacture_date` | string | Data de fabrico |
| `firmware_version` | string | Versao do firmware |
| `wot_td_hash` | string | Hash do WoT TD |
| `serial_number` | string | Numero de serie |

### Ownership VC (UC4/UC5/UC8)

Emitida ao consumidor na compra, verificada no claiming, transferida na venda.

| Atributo | Tipo | Descricao |
|---|---|---|
| `device_uuid` | string | UUID do dispositivo |
| `owner_did` | string | DID do proprietario |
| `acquisition_date` | string | Data de aquisicao |
| `previous_owner_did` | string | DID do proprietario anterior |
| `transfer_tx_hash` | string | Hash da transacao de transferencia |

## Goal Codes (Automacao DIDComm)

| Goal Code | UC | Descricao |
|---|---|---|
| `c2dta.consortium.enroll.OEM` | UC1 | Enrollment de OEM |
| `c2dta.consortium.registermodel` | UC2 | Registo de modelo |
| `c2dta.consortium.registerdevice` | UC3 | Registo de dispositivo |
| `c2dta.consortium.buydevice` | UC4 | Compra de dispositivo |
| `c2dta.consortium.claim` | UC5 | Claiming |
| `c2dta.consortium.twin` | UC6 | Twinning |
| `c2dta.consortium.untwin` | UC7 | Untwinning |
| `c2dta.consortium.sell` | UC8 | Venda |

## Protocolos DIDComm

- **Out-of-Band (OOB)**: Estabelecimento de conexao inicial
- **Issue Credential v2**: Emissao de VCs (Enrollment, Genesis, Ownership)
- **Present Proof v2**: Verificacao de VCs (autenticacao, claiming)
- **Action Menu**: Interacao guiada (registo de modelo)
- **Basic Message**: Comunicacao livre

> Ultima revisao: 2026-03-19
