# Simulador de Smart Device (Smartwatch) — C2DTA

Simulador Python de um smartwatch com sensor de heartbeat e GPS, conforme descrito no paper `EdgeGateway_Paper.pdf` (Seccao 4). Gera dados sensoriais a 1 Hz e publica via MQTT/TLS.

## Estrutura

```text
services/smart-device-simulator/
  src/smart_device_simulator/
    __init__.py
    simulator.py          Logica de geracao de dados (heartbeat random walk, geo drift)
    mqtt_publisher.py     Cliente MQTT com TLS (paho-mqtt)
    models.py             Modelos Pydantic (SensorReading, GeoLocation)
    config.py             Configuracao via variaveis de ambiente
  tests/
    conftest.py           Configuracao pytest
    test_simulator.py     Testes unitarios de geracao de dados
    test_mqtt_publisher.py Testes de integracao MQTT
  examples/
    run_simulator.py      Ponto de entrada CLI
  Dockerfile
  docker-compose.yml
  pyproject.toml
  requirements.txt
  README.md               Este ficheiro
```

## Dados gerados

| Campo | Tipo | Descricao |
|---|---|---|
| `device_uuid` | string | UUID unico do dispositivo (gerado no primeiro boot) |
| `heartbeat_bpm` | int | Batimento cardiaco (40-200 bpm), random walk com mean-reversion |
| `geolocation.lat` | float | Latitude WGS84 com drift gaussiano (~5.5m/leitura) |
| `geolocation.lon` | float | Longitude WGS84 com drift gaussiano (~5.5m/leitura) |
| `timestamp` | datetime | UTC ISO 8601 |

## Como usar

### Localmente

```bash
cd services/smart-device-simulator
pip install -r requirements.txt
SD_UUID=meu-uuid python examples/run_simulator.py
```

### Docker

```bash
docker compose up --build
```

### Testes

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## Variaveis de ambiente

| Variavel | Descricao | Default |
|---|---|---|
| `SD_UUID` | UUID do dispositivo | Auto-gerado |
| `MQTT_BROKER_HOST` | Host do broker MQTT | `localhost` |
| `MQTT_BROKER_PORT` | Porta TLS do broker | `8883` |
| `MQTT_CA_CERT` | Caminho do certificado CA | `certs/ca.crt` |
| `MQTT_CLIENT_CERT` | Caminho do certificado cliente | — |
| `MQTT_CLIENT_KEY` | Caminho da chave privada cliente | — |
| `SD_PUBLISH_INTERVAL_MS` | Intervalo de publicacao (ms) | `1000` |
| `SD_INITIAL_HEARTBEAT` | Heartbeat inicial (bpm) | `72` |
| `SD_INITIAL_LAT` | Latitude inicial | `38.7223` |
| `SD_INITIAL_LON` | Longitude inicial | `-9.1393` |

## Topico MQTT

Publica em `egw/<device_uuid>/telemetry` com QoS 1.

Payload JSON de exemplo:
```json
{
  "device_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "heartbeat_bpm": 74,
  "geolocation": {"lat": 38.7223012, "lon": -9.1393045},
  "timestamp": "2026-01-15T10:30:00.123456Z"
}
```

> Ultima revisao: 2026-03-19
