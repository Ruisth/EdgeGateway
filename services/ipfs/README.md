# IPFS (Kubo) — Armazenamento Descentralizado C2DTA

No IPFS local para armazenamento de snapshots do Digital Twin, conforme descrito no paper `EdgeGateway_Paper.pdf` (Seccao 3.1 — Device Storage).

## Estrutura

```text
services/ipfs/
  docker-compose.yml        No Kubo IPFS
  tests/
    test_ipfs_storage.py    Testes de integracao (add/cat/pin)
  README.md                 Este ficheiro
```

## Fluxo de dados

1. EGW Controller recolhe snapshots periodicos do Digital Twin (Eclipse Ditto)
2. Snapshot JSON e adicionado ao IPFS via API (`/api/v0/add`)
3. CID (Content Identifier) retornado e registado no Hyperledger Fabric via `dataset-tracking` chaincode
4. Consumidor pode verificar integridade dos dados comparando CID no ledger com conteudo no IPFS

## Portas

| Porta | Servico | Descricao |
|---|---|---|
| 5001 | API | Interface HTTP para adicionar/recuperar conteudo |
| 8081 | Gateway | Gateway HTTP para acesso publico (porta 8081 para nao conflitar com Ditto) |
| 4001 | Swarm | Comunicacao entre nos IPFS |

## Como usar

```bash
# Iniciar no IPFS
docker compose up -d

# Adicionar ficheiro
curl -X POST -F file=@dataset.json http://localhost:5001/api/v0/add

# Recuperar por CID
curl -X POST http://localhost:5001/api/v0/cat?arg=<CID>

# Listar pins
curl -X POST http://localhost:5001/api/v0/pin/ls
```

> Ultima revisao: 2026-03-19
