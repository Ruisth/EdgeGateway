# Hyperledger Fabric — Ecosystem Ledger C2DTA

Rede Hyperledger Fabric 2.5 que serve como ecosystem ledger da arquitetura C2DTA, conforme descrito no paper `EdgeGateway_Paper.pdf` (Seccao 3.1 — Dual Blockchain).

## Estrutura

```text
services/fabric/
  docker-compose.yml              Rede Fabric (orderer, peers, CAs, CouchDB, CLI)
  configtx/
    configtx.yaml                 Configuracao do canal e organizacoes
  chaincode/
    device-lifecycle/             Chaincode ciclo de vida (Go)
      device_lifecycle.go         6 estados: Manufactured→Available→In-Transit→Claimed→Twinned→Decommissioned
      go.mod
    dataset-tracking/             Chaincode rastreamento de datasets (Go)
      dataset_tracking.go         Ancora hashes IPFS no ledger
      go.mod
  scripts/
    network-up.sh                 Iniciar rede
    network-down.sh               Parar rede
    deploy-chaincode.sh           Deploy dos chaincodes
  tests/
  README.md                       Este ficheiro
```

## Topologia

| Componente | Container | Porta |
|---|---|---|
| Orderer (Raft) | c2dta-orderer | 7050, 7053 |
| Peer ConsortiumOrg | c2dta-peer0-consortium | 7051 |
| Peer OEMOrg | c2dta-peer0-oem | 9051 |
| CouchDB (Consortium) | c2dta-couchdb0 | — |
| CouchDB (OEM) | c2dta-couchdb1 | — |
| CA Consortium | c2dta-ca-consortium | 7054 |
| CA OEM | c2dta-ca-oem | 8054 |
| CLI | c2dta-fabric-cli | — |

## Chaincodes

### device-lifecycle

Gere os 6 estados do ciclo de vida de dispositivos:

| Funcao | Transicao | Use Case |
|---|---|---|
| `RegisterDeviceModel` | — | UC2 |
| `ManufactureDevice` | → Manufactured | UC3 |
| `MakeAvailable` | Manufactured → Available | UC3 |
| `InitiateTransit` | Available → In-Transit | UC4 |
| `ClaimDevice` | In-Transit → Claimed | UC5 |
| `TwinDevice` | Claimed → Twinned | UC6 |
| `UntwinDevice` | Twinned → Claimed | UC7 |
| `DecommissionDevice` | * → Decommissioned | — |
| `QueryDevice` | Leitura | — |
| `QueryDevicesByState` | Rich query (CouchDB) | — |
| `QueryDevicesByOwner` | Rich query (CouchDB) | — |

### dataset-tracking

Ancora hashes de datasets IPFS no ledger:

| Funcao | Descricao | Use Case |
|---|---|---|
| `RegisterDataset` | Regista snapshot DT + hash IPFS | UC6 |
| `QueryDatasetsByDevice` | Lista datasets de um dispositivo | — |
| `TransferDatasetOwnership` | Transfere propriedade | UC8 |

## Como usar

```bash
# Iniciar rede
./scripts/network-up.sh

# Parar rede
./scripts/network-down.sh

# Deploy chaincodes (seguir instrucoes)
./scripts/deploy-chaincode.sh
```

> Ultima revisao: 2026-03-19
