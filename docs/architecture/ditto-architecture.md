# Arquitetura Eclipse Ditto (Digital Twin Platform)

## Visao Geral

O Eclipse Ditto 3.5.6 serve como plataforma de Digital Twin, gerindo representacoes virtuais (things) dos Smart Devices. Cada thing e identificado pelo padrao `org.c2dta:<device_uuid>` e mantem features atualizadas via MQTT.

## Modelo do Thing

```json
{
  "thingId": "org.c2dta:550e8400-e29b-41d4-a716-446655440000",
  "features": {
    "heartbeat": {
      "properties": {
        "bpm": 72
      }
    },
    "geolocation": {
      "properties": {
        "latitude": 38.7223,
        "longitude": -9.1393
      }
    },
    "timestamp": {
      "properties": {
        "value": "2026-03-19T10:30:00Z"
      }
    }
  }
}
```

## Stack de Servicos

| Servico | Imagem | Funcao |
|---|---|---|
| MongoDB 6.0 | `mongo:6.0` | Persistencia de things, policies, connections |
| ditto-policies | `eclipse/ditto-policies:3.5.6` | Gestao de politicas de acesso |
| ditto-things | `eclipse/ditto-things:3.5.6` | CRUD de things |
| ditto-things-search | `eclipse/ditto-things-search:3.5.6` | Pesquisa de things |
| ditto-connectivity | `eclipse/ditto-connectivity:3.5.6` | Conectividade MQTT/HTTP |
| ditto-gateway | `eclipse/ditto-gateway:3.5.6` | Gateway HTTP/WebSocket |
| nginx | `nginx:1.27-alpine` | Reverse proxy com autenticacao |

## Conectividade MQTT

A conexao MQTT esta configurada em `services/ditto/connectivity/mqtt-connection.json`:

- **Source**: `egw/+/telemetry` (subscreve telemetria de todos os SDs)
- **Mapper**: JavaScript que extrai `heartbeat_bpm`, `geolocation`, `timestamp` do payload JSON e mapeia para features do thing
- **Thing ID**: Derivado do UUID no topico MQTT

## WoT Thing Description

O modelo de smartwatch esta descrito em W3C WoT TD v1.1 (`services/ditto/wot/smartwatch-td.jsonld`):

| Property | Tipo | Unidade |
|---|---|---|
| `heartbeat` | integer | bpm |
| `geolocation.latitude` | number | WGS84 |
| `geolocation.longitude` | number | WGS84 |
| `timestamp` | dateTime | ISO 8601 |

## API

- **Base URL**: `http://localhost:8080`
- **Autenticacao**: Basic Auth (`ditto:c2dta`)
- **Endpoints principais**:
  - `PUT /api/2/things/{thingId}` — Criar/atualizar thing
  - `GET /api/2/things/{thingId}` — Consultar thing
  - `DELETE /api/2/things/{thingId}` — Remover thing (untwinning)
  - `GET /api/2/things/{thingId}/features` — Consultar features (para snapshot)

## Ciclo de Vida

1. **UC6 (Twinning)**: EGW Controller cria thing via API → configura MQTT connectivity → SD inicia streaming
2. **UC7 (Untwinning)**: EGW Controller remove thing via API → para streaming MQTT

> Ultima revisao: 2026-03-19
