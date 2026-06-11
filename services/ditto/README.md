# Eclipse Ditto — Plataforma Digital Twin C2DTA

Plataforma de Digital Twin baseada em Eclipse Ditto 3.x, conforme o paper `EdgeGateway_Paper.pdf` (Seccoes 3.2.6, 4). Recebe dados sensoriais via MQTT e mantem o estado virtual dos Smart Devices.

## Estrutura

```text
services/ditto/
  docker-compose.yml          Stack completa Ditto 3.x (7 servicos)
  nginx/
    nginx.conf                Reverse proxy com autenticacao basica
    nginx.htpasswd            Gerado por generate-htpasswd.sh (gitignored)
    nginx.htpasswd.example    Placeholder versionado
    generate-htpasswd.sh      Gera nginx.htpasswd a partir do .env da raiz
  connectivity/
    mqtt-connection.json      Configuracao da conexao MQTT source
  wot/
    smartwatch-td.jsonld      W3C WoT Thing Description do smartwatch
  tests/
    test_ditto_api.py         Testes de integracao (CRUD things)
  README.md                   Este ficheiro
```

## Servicos

| Servico | Imagem | Porta | Funcao |
|---|---|---|---|
| mongodb | mongo:6.0 | — | Persistencia de dados |
| ditto-policies | eclipse/ditto-policies:3.5.6 | — | Controlo de acesso |
| ditto-things | eclipse/ditto-things:3.5.6 | — | Gestao de estado dos DTs |
| ditto-things-search | eclipse/ditto-things-search:3.5.6 | — | Pesquisa sobre DTs |
| ditto-connectivity | eclipse/ditto-connectivity:3.5.6 | — | Conexoes externas (MQTT) |
| ditto-gateway | eclipse/ditto-gateway:3.5.6 | — | API gateway |
| nginx | nginx:1.27-alpine | 8080 | Reverse proxy |

## Como usar

### 1. Iniciar o stack

```bash
cd services/ditto
docker compose up -d
```

### 2. Verificar saude

```bash
curl -u ditto:c2dta http://localhost:8080/status
```

### 3. Criar um thing (exemplo)

```bash
curl -X PUT -u ditto:c2dta \
  -H 'Content-Type: application/json' \
  -d '{"thingId":"org.c2dta:test-device","features":{"heartbeat":{"properties":{"bpm":72}}}}' \
  http://localhost:8080/api/2/things/org.c2dta:test-device
```

### 4. Configurar conexao MQTT

O script injeta a CA gerada por `generate-certs.sh` no JSON da conexao
(`validateCertificates: true`) e aplica-a via API devops, lendo as
credenciais do `.env` da raiz:

```bash
bash connectivity/create-connection.sh
```

## Modelo Thing

Thing ID: `org.c2dta:<device_uuid>`

Features:
- `heartbeat.properties.bpm` — batimentos por minuto (int)
- `geolocation.properties.latitude` — latitude WGS84 (float)
- `geolocation.properties.longitude` — longitude WGS84 (float)
- `timestamp.properties.value` — timestamp ISO 8601 (string)

## WoT Thing Description

O ficheiro `wot/smartwatch-td.jsonld` define o modelo W3C WoT do smartwatch, referenciado no UC2 (registo de modelo de dispositivo).

## Credenciais

Lidas do `.env` da raiz (copia-se `.env.example` e preenche-se). Utilizadores
expostos pelo nginx (uma linha htpasswd por cada):

| Variavel `.env`           | Utilizador | Permissoes                              |
|---------------------------|------------|-----------------------------------------|
| `DITTO_USER`/`DITTO_PASS` | `ditto`    | API de things (CRUD)                    |
| `DITTO_DEVOPS_USER`/`DITTO_DEVOPS_PASSWORD` | `devops` | DevOps API (conectividade, metricas) |

Para gerar/regenerar o `nginx.htpasswd` localmente:

```bash
bash nginx/generate-htpasswd.sh
```
