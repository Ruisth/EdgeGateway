# Arquitetura IPFS (Armazenamento Descentralizado)

## Visao Geral

O IPFS (Kubo v0.28.0) fornece armazenamento descentralizado para snapshots periodicos dos dados do Digital Twin. Os Content Identifiers (CIDs) resultantes sao ancorados no Hyperledger Fabric via chaincode `dataset-tracking`.

## Topologia

| Componente | Container | Portas |
|---|---|---|
| IPFS (Kubo) | `c2dta-ipfs` | 5001 (API), 8081 (Gateway), 4001 (Swarm) |

## Fluxo de Dados

```
SD → MQTT → Ditto (DT) → EGW Controller → IPFS (snapshot JSON)
                                              ↓
                                          CID retornado
                                              ↓
                                      Fabric (RegisterDataset)
```

1. EGW Controller le features do thing Ditto via API
2. Serializa o snapshot como JSON
3. Adiciona ao IPFS via `POST /api/v0/add` (com pin)
4. Recebe o CID
5. Regista no Fabric: `RegisterDataset(datasetID, deviceID, CID, ...)`

## Estrategia de Pinning

- **Pin automatico**: Todos os snapshots sao pinados no momento da adição (`pin=true`)
- **Retencao**: Snapshots permanecem pinados indefinidamente (configuravel)
- **Replicacao**: Em producao, replicar para multiplos nos IPFS

## Formato do Snapshot

```json
{
  "device_id": "550e8400-e29b-41d4-a716-446655440000",
  "thing_id": "org.c2dta:550e8400-e29b-41d4-a716-446655440000",
  "snapshot_time": "2026-03-19T10:30:00Z",
  "features": {
    "heartbeat": {"properties": {"bpm": 72}},
    "geolocation": {"properties": {"latitude": 38.7223, "longitude": -9.1393}},
    "timestamp": {"properties": {"value": "2026-03-19T10:30:00Z"}}
  }
}
```

## API

| Operacao | Endpoint | Descricao |
|---|---|---|
| Adicionar | `POST /api/v0/add` | Adiciona ficheiro/JSON ao IPFS |
| Ler | `POST /api/v0/cat?arg=<CID>` | Recupera conteudo por CID |
| Pinar | `POST /api/v0/pin/add?arg=<CID>` | Pina CID para persistencia |

## Configuracao

- **Perfil**: `server` (otimizado para servico persistente)
- **Rede**: Privada em dev (swarm key), publica em producao

## Receita Yocto

`yocto/layers/meta-edgegateway/recipes-containers/ipfs-compose/`

> Ultima revisao: 2026-03-19
