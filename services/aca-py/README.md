# ACA-Py — Agentes SSI C2DTA

Instancias ACA-Py (Aries Cloud Agent Python) para cada stakeholder do ecossistema C2DTA, conforme descrito no paper `EdgeGateway_Paper.pdf` (Seccao 3.1 — Agents).

## Estrutura

```text
services/aca-py/
  docker-compose.yml          5 instancias ACA-Py
  plugins/
    c2dta_protocols/
      __init__.py
      goal_codes.py           Goal codes para automacao DIDComm
      enrollment.py           Handler Enrollment VC (UC1)
      genesis.py              Handler Genesis VC (UC3)
      ownership.py            Handler Ownership VC (UC4/UC5/UC8)
  tests/
  README.md                   Este ficheiro
```

## Agentes

| Agente | Notacao SSI | Papel | Admin API | HTTP Endpoint |
|---|---|---|---|---|
| Consorcio | 1@C | Issuer (Enrollment VC), Steward | :8021 | :8020 |
| OEM | 1@O | Issuer (Genesis VC), Holder (Enrollment) | :8031 | :8030 |
| Consumidor A | 1@A | Holder (Ownership VC), Verifier | :8041 | :8040 |
| Edge Gateway | 1@egw | Holder (Genesis VC), Verifier | :8061 | :8060 |
| Smart Device | 1@sd | Holder (Genesis VC) | :8071 | :8070 |

## Goal Codes (automacao)

| Goal Code | Use Case | Descricao |
|---|---|---|
| `c2dta.consortium.enroll.OEM` | UC1 | Inscricao de OEM no consorcio |
| `c2dta.consortium.registerdevice` | UC3 | Auto-registo de dispositivo |
| `c2dta.consortium.buydevice` | UC4 | Compra de dispositivo |
| `c2dta.consortium.claim` | UC5 | Reivindicacao de dispositivo |
| `c2dta.egw.twin` | UC6 | Twinning de smart device |
| `c2dta.egw.untwin` | UC7 | Untwinning de smart device |
| `c2dta.egw.sell` | UC8 | Venda de smart device |

## Protocolos DIDComm utilizados

- **Out-of-Band (RFC 0434)**: Convites iniciais entre agentes
- **Issue Credential v2 (RFC 0453)**: Emissao de VCs (Enrollment, Genesis, Ownership)
- **Present Proof v2 (RFC 0454)**: Verificacao de VCs (claiming, enrollment)
- **Action Menu (RFC 0509)**: Menus interativos para consumidores
- **Basic Message (RFC 0095)**: Mensagens simples entre agentes

## Como usar

```bash
# Iniciar todos os agentes (requer pool Indy ativo)
docker compose up -d

# Verificar saude do agente do consorcio
curl http://localhost:8021/status

# Criar convite OOB
curl -X POST http://localhost:8021/out-of-band/create-invitation \
  -H 'Content-Type: application/json' \
  -d '{"handshake_protocols":["https://didcomm.org/didexchange/1.0"]}'
```

> Ultima revisao: 2026-03-19
