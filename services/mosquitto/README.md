# Eclipse Mosquitto — Broker MQTT C2DTA

Broker MQTT com TLS obrigatorio para comunicacao segura entre Smart Devices (SD) e o Edge Gateway (EGW), conforme descrito no paper `EdgeGateway_Paper.pdf` (Seccao 3.2.6 — SD Twinning).

## Estrutura

```text
services/mosquitto/
  config/
    mosquitto.conf        Configuracao principal (TLS, persistencia, limites)
    acl.conf              Controlo de acesso por topico
  certs/
    generate-certs.sh     Gera certificados self-signed para desenvolvimento
  tests/
    test_mqtt_connectivity.py   Testes de conectividade TLS e pub/sub
  docker-compose.yml      Orquestracao do container Mosquitto
  README.md               Este ficheiro
```

## Hierarquia de topicos

| Topico | Direção | QoS | Descricao |
|---|---|---|---|
| `egw/<uuid>/telemetry` | SD → EGW | 1 | Dados sensoriais (heartbeat, geo, timestamp) |
| `egw/<uuid>/command` | EGW → SD | 2 | Comandos para o SD (start/stop streaming) |
| `egw/<uuid>/status` | Bidirecional | 1 | Estado do dispositivo |
| `egw/system/#` | EGW interno | 0 | Topicos de sistema |

## Como usar

### 1. Gerar certificados

```bash
cd services/mosquitto
chmod +x certs/generate-certs.sh
./certs/generate-certs.sh
# Para gerar certificado de um SD:
./certs/generate-certs.sh <device-uuid>
```

### 2. Iniciar o broker

```bash
docker compose up -d
```

### 3. Verificar saude

```bash
docker compose ps
# O healthcheck verifica a resposta do broker a cada 10s
```

### 4. Executar testes

```bash
pip install paho-mqtt pytest
pytest tests/test_mqtt_connectivity.py -v
```

## Variaveis de ambiente

| Variavel | Descricao | Default |
|---|---|---|
| `MQTT_BROKER_HOST` | Host do broker (testes) | `localhost` |
| `MQTT_BROKER_PORT` | Porta TLS do broker (testes) | `8883` |

## Seguranca

- TLS 1.2+ obrigatorio em todas as conexoes externas
- Autenticacao mútua por certificado (`require_certificate true`)
- O CN do certificado cliente e usado como username para ACL
- Listener interno (porta 1883) restrito a `127.0.0.1` apenas para healthcheck

## Integracao com outros servicos

- **Smart Device Simulator**: publica em `egw/<uuid>/telemetry` com certificado proprio
- **Eclipse Ditto**: subscreve `egw/+/telemetry` com certificado `ditto-connectivity`
- **EGW Controller**: subscreve/publica em `egw/#` com certificado `edgegateway`

> Ultima revisao: 2026-03-19
