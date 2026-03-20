# Fluxos dos Use Cases (UC1-UC8)

Descricao detalhada dos 8 use cases da arquitetura C2DTA conforme o paper (Seccao 3.2).

---

## UC1 — OEM Enrollment (Seccao 3.2.1)

**Atores**: Consorcio (1@C), OEM (1@O)

**Fluxo**:
1. Consorcio cria OOB invitation com goal code `c2dta.consortium.enroll.OEM`
2. OEM aceita invitation → conexao DIDComm estabelecida
3. Consorcio propoe Enrollment VC ao OEM
4. OEM submete provas documentais
5. Consorcio emite Enrollment VC

**Resultado**: OEM inscrito no consorcio com Enrollment VC no wallet.

---

## UC2 — Device Model Registration (Seccao 3.2.2)

**Atores**: OEM (1@O), Consorcio (1@C)

**Fluxo**:
1. OEM solicita action menu ao consorcio
2. OEM submete informacao do modelo (nome, descricao, WoT TD)
3. OEM prova posse da Enrollment VC (Present Proof v2)
4. Consorcio regista modelo no ecosystem ledger (Fabric): `RegisterDeviceModel`
5. WoT TD armazenado

**Resultado**: Modelo registado no Fabric, WoT TD disponivel.

---

## UC3 — Device Self-Registration (Seccao 3.2.3)

**Atores**: EGW (1@egw) ou SD (1@sd), OEM (1@O)

**Fluxo EGW**:
1. EGW arranca → gera DID publico (primeiro boot)
2. EGW conecta-se ao OEM via DIDComm (OOB)
3. OEM emite Genesis VC ao EGW
4. OEM regista dispositivo no Fabric: `ManufactureDevice` → `MakeAvailable`

**Fluxo SD**:
1. SD arranca → gera UUID (primeiro boot)
2. SD conecta-se ao OEM via DIDComm (mediado pelo EGW)
3. OEM emite Genesis VC ao SD
4. OEM regista SD no Fabric

**Resultado**: Dispositivo no estado Available com Genesis VC.

---

## UC4 — Consumer Buys Device (Seccao 3.2.4)

**Atores**: Consumidor (1@A), OEM (1@O)

**Fluxo**:
1. Consumidor conecta-se ao OEM via OOB (goal code `c2dta.consortium.buydevice`)
2. OEM propoe Ownership VC ao consumidor
3. Apos confirmacao de pagamento, OEM emite Ownership VC
4. Fabric: `InitiateTransit` (Available → In-Transit)

**Resultado**: Dispositivo em transito, consumidor com Ownership VC.

---

## UC5 — Device Claiming (Seccao 3.2.5)

**Atores**: Consumidor (1@A), EGW (1@egw)

**Fluxo**:
1. Consumidor faz scan do QR code no SD/EGW
2. Conexao DIDComm via OOB (goal code `c2dta.consortium.claim`)
3. Consumidor prova posse da Ownership VC (Present Proof v2)
4. EGW valida Genesis VC + Ownership VC
5. Fabric: `ClaimDevice` (In-Transit → Claimed)

**Resultado**: Dispositivo reivindicado pelo consumidor, estado Claimed.

---

## UC6 — SD Twinning (Seccao 3.2.6)

**Atores**: EGW Controller, Ditto, Mosquitto, Fabric, IPFS

**Fluxo**:
1. EGW Controller cria Digital Twin no Ditto (thing ID: `org.c2dta:<uuid>`)
2. Configura conectividade MQTT (Ditto ← Mosquitto ← SD)
3. SD inicia streaming de telemetria a 1 Hz
4. EGW Controller inicia snapshots periodicos: Ditto → JSON → IPFS → CID no Fabric
5. Fabric: `TwinDevice` (Claimed → Twinned)

**Resultado**: Digital Twin ativo, streaming em tempo real, snapshots IPFS ancorados no Fabric.

---

## UC7 — SD Untwinning (Seccao 3.2.7)

**Atores**: EGW Controller, Ditto, Fabric

**Fluxo**:
1. EGW Controller para streaming MQTT
2. Snapshot final enviado ao IPFS
3. EGW Controller remove thing do Ditto
4. Fabric: `UntwinDevice` (Twinned → Claimed)

**Resultado**: Digital Twin removido, dados preservados no IPFS, dispositivo retorna a Claimed.

---

## UC8 — SD Selling (Seccao 3.2.8)

**Atores**: Consumidor vendedor (1@A), Consumidor comprador (1@B), EGW Controller

**Fluxo**:
1. Untwin se twinned (executa UC7)
2. Revogar Ownership VC do vendedor
3. Emitir nova Ownership VC ao comprador
4. Transferir propriedade de datasets no Fabric: `TransferDatasetOwnership`
5. Fabric: `InitiateTransit` (Claimed → In-Transit)

**Resultado**: Dispositivo transferido para novo proprietario, datasets transferidos, pronto para novo claiming (UC5).

---

## Tabela Resumo

| UC | Nome | Estados Fabric | VCs Envolvidas | Servicos |
|---|---|---|---|---|
| UC1 | OEM Enrollment | — | Enrollment VC (emitida) | ACA-Py |
| UC2 | Model Registration | — | Enrollment VC (verificada) | ACA-Py, Fabric |
| UC3 | Device Self-Registration | → Manufactured → Available | Genesis VC (emitida) | ACA-Py, Fabric |
| UC4 | Consumer Buys Device | → In-Transit | Ownership VC (emitida) | ACA-Py, Fabric |
| UC5 | Device Claiming | → Claimed | Ownership VC (verificada) | ACA-Py, Fabric |
| UC6 | SD Twinning | → Twinned | — | Ditto, MQTT, IPFS, Fabric |
| UC7 | SD Untwinning | → Claimed | — | Ditto, MQTT, IPFS, Fabric |
| UC8 | SD Selling | → In-Transit | Ownership VC (revogada + emitida) | ACA-Py, Fabric |

> Ultima revisao: 2026-03-19
