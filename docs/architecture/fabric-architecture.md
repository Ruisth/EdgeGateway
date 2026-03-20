# Arquitetura Hyperledger Fabric (Ecosystem Ledger)

## Visao Geral

O Hyperledger Fabric 2.5 funciona como o ecosystem ledger da arquitetura C2DTA, registando o ciclo de vida dos dispositivos e os datasets de dados do Digital Twin.

## Topologia de Rede (Dev)

| Componente | Container | Porta |
|---|---|---|
| Orderer (Raft, single) | `c2dta-orderer` | 7050, 7053 (admin) |
| Peer ConsortiumOrg | `c2dta-peer0-consortium` | 7051 |
| Peer OEMOrg | `c2dta-peer0-oem` | 9051 |
| CouchDB (Consortium) | `c2dta-couchdb0` | 5984 |
| CouchDB (OEM) | `c2dta-couchdb1` | 5984 |
| CA Consortium | `c2dta-ca-consortium` | 7054 |
| CA OEM | `c2dta-ca-oem` | 8054 |
| CLI | `c2dta-fabric-cli` | — |

## Canal

- **Nome**: `c2dta-channel`
- **Organizacoes**: ConsortiumOrg, OEMOrg
- **Politica de endorsement**: Majority (ambas as orgs)

## Ciclo de Vida do Dispositivo (6 Estados)

```
Manufactured → Available → In-Transit → Claimed → Twinned
                                                      ↓
                                                  Claimed ← (Untwinning)
                                                      ↓
                                               Decommissioned
```

### Transicoes

| De | Para | Funcao Chaincode | UC |
|---|---|---|---|
| (novo) | Manufactured | `ManufactureDevice` | UC3 |
| Manufactured | Available | `MakeAvailable` | UC3 |
| Available | In-Transit | `InitiateTransit` | UC4 |
| In-Transit | Claimed | `ClaimDevice` | UC5 |
| Claimed | Twinned | `TwinDevice` | UC6 |
| Twinned | Claimed | `UntwinDevice` | UC7 |
| Claimed | In-Transit | `InitiateTransit` | UC8 |
| * | Decommissioned | `DecommissionDevice` | — |

## Chaincodes

### device-lifecycle (Go)

Modelo de dados:

```go
type Device struct {
    DeviceID, ModelID, State               string
    ManufacturerID, OwnerDID, ControllerDID string
    GenesisVCHash, OwnershipVCHash         string
    DittoThingID, CreatedAt, UpdatedAt     string
}
```

Funcoes: `RegisterDeviceModel`, `ManufactureDevice`, `MakeAvailable`, `InitiateTransit`, `ClaimDevice`, `TwinDevice`, `UntwinDevice`, `DecommissionDevice`, `QueryDevice`, `QueryDevicesByState`, `QueryDevicesByOwner`

### dataset-tracking (Go)

Modelo de dados:

```go
type Dataset struct {
    DatasetID, DeviceID, IPFSHash string
    OwnerDID, Timestamp, Metadata string
}
```

Funcoes: `RegisterDataset`, `QueryDataset`, `QueryDatasetsByDevice`, `TransferDatasetOwnership`

## Integracao com IPFS

Snapshots periodicos do Digital Twin sao armazenados no IPFS, e o CID resultante e registado no Fabric via `RegisterDataset`, criando uma trilha de auditoria imutavel.

## Scripts

- `scripts/network-up.sh` — Inicia a rede Fabric
- `scripts/network-down.sh` — Para a rede Fabric
- `scripts/deploy-chaincode.sh` — Deploya chaincodes no canal

> Ultima revisao: 2026-03-19
