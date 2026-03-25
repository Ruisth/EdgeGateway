# Arquitetura MQTT (Eclipse Mosquitto)

## Visao Geral

O broker MQTT Eclipse Mosquitto 2.0 serve como canal de comunicacao entre os Smart Devices (SD) e o Edge Gateway (EGW), transportando dados de telemetria em tempo real a 1 Hz.

## Hierarquia de Topicos

| Topico | Publicador | Subscritor | QoS | Descricao |
|---|---|---|---|---|
| `egw/<uuid>/telemetry` | SD | EGW, Ditto | 1 | Dados sensoriais (heartbeat, geo, timestamp) |
| `egw/+/telemetry` | — | Ditto Connectivity | 1 | Wildcard para todos os dispositivos |
| `egw/#` | — | EGW Controller | 1 | Wildcard global para o EGW |

## Formato da Mensagem

```json
{
  "device_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "heartbeat_bpm": 72,
  "geolocation": {
    "lat": 38.7223,
    "lon": -9.1393
  },
  "timestamp": "2026-03-19T10:30:00Z"
}
```

## Seguranca TLS

- **Porta**: 8883 (TLS obrigatorio)
- **Protocolo**: TLS 1.2+
- **Autenticacao**: Certificado de cliente (mTLS)
- **Certificados**:
  - `ca.crt` — Autoridade de certificacao raiz
  - `server.crt/key` — Certificado do broker
  - `client.crt/key` — Certificado por dispositivo/servico

## ACL (Access Control List)

| Identidade | Permissao | Topicos |
|---|---|---|
| Smart Device (`sd-*`) | write | `egw/%u/telemetry` |
| Edge Gateway (`edgegateway`) | read | `egw/#` |
| Ditto (`ditto-connectivity`) | read | `egw/+/telemetry` |

## Configuracao

- **Persistencia**: Ativa (`persistence true`)
- **QoS 1**: Entrega fiavel (at least once) para telemetria
- **Max message size**: 1 KB
- **Max connections**: 100

## Integracao com Ditto

O Ditto Connectivity subscreve `egw/+/telemetry` e mapeia o payload JSON para features do thing via JavaScript mapper, atualizando o Digital Twin em tempo real.

## Receita Yocto

`yocto/layers/meta-edgegateway/recipes-containers/mosquitto-compose/`

> Ultima revisao: 2026-03-19
