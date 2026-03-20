# Hyperledger Indy — Identity Ledger C2DTA

Pool de nos Hyperledger Indy (via von-network) que serve como identity ledger da arquitetura C2DTA, conforme descrito no paper `EdgeGateway_Paper.pdf` (Seccao 3.1 — Dual Blockchain).

## Estrutura

```text
services/indy/
  docker-compose.yml        Pool de 4 nos Indy (von-network)
  schemas/
    enrollment_vc.json      Schema VC de inscricao no consorcio
    genesis_vc.json         Schema VC de proveniencia do dispositivo
    ownership_vc.json       Schema VC de propriedade do dispositivo
  tests/
  README.md                 Este ficheiro
```

## Schemas de Verifiable Credentials

| VC | Emissor | Titular | Referencia Paper |
|---|---|---|---|
| EnrollmentCredential | Consorcio (1@C) | OEM (1@O) | Seccao 3.2.1 |
| GenesisCredential | OEM (1@O) | EGW (1@egw) / SD (1@sd) | Seccao 3.2.3 |
| OwnershipCredential | OEM (1@O) / EGW (1@egw) | Consumidor (1@A) | Seccao 3.2.4 |

## Como usar

```bash
# Iniciar pool Indy
docker compose up -d

# Web UI disponivel em http://localhost:9000
# Genesis file em http://localhost:9000/genesis
```

## Seed de desenvolvimento

O Steward seed de desenvolvimento e: `C2DTA000000000000000000Steward1`

> Ultima revisao: 2026-03-19
