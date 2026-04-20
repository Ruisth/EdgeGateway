# Guia Completo — EdgeGateway / C2DTA

> **Para quem é este guia?** Para qualquer pessoa — mesmo sem experiência em programação, blockchain ou IoT — que queira perceber o que é o projeto **EdgeGateway**, como está organizado, como funciona por dentro, e como o pôr a correr do zero.
>
> Este documento é longo de propósito. Lê-se de cima para baixo ou salta-se pelas secções através do índice. Cada conceito é explicado na primeira vez que aparece, com uma analogia simples sempre que possível.

**Projeto:** Consumer-Controlled Digital Twin Architecture (C2DTA)
**Autor da dissertação:** Rui Duarte (ISCTE)
**Paper de referência:** Pinto et al., *"Consumer-Controlled Digital Twin Architecture: How blockchain technology gives consumers control over their smart devices' digital twins and data"*, Blockchain: Research and Applications, Elsevier, 2025. DOI: [10.1016/j.bcra.2025.100342](https://doi.org/10.1016/j.bcra.2025.100342)
**Licença:** MIT

---

## Índice

1. [Para que serve este projeto?](#1-para-que-serve-este-projeto)
2. [Conceitos fundamentais (sem pré-requisitos)](#2-conceitos-fundamentais-sem-pré-requisitos)
3. [Arquitetura C2DTA em visão geral](#3-arquitetura-c2dta-em-visão-geral)
4. [Os 9 serviços, um a um](#4-os-9-serviços-um-a-um)
5. [Ciclo de vida do dispositivo (6 estados)](#5-ciclo-de-vida-do-dispositivo-6-estados)
6. [Credenciais Verificáveis (VCs)](#6-credenciais-verificáveis-vcs)
7. [Os 8 Use Cases passo a passo](#7-os-8-use-cases-passo-a-passo)
8. [API REST do EGW Controller](#8-api-rest-do-egw-controller)
9. [Como instalar e correr (do zero)](#9-como-instalar-e-correr-do-zero)
10. [Como testar](#10-como-testar)
11. [Mapa completo de portas](#11-mapa-completo-de-portas)
12. [Verificação código-vs-paper (auditoria de conformidade)](#12-verificação-código-vs-paper-auditoria-de-conformidade)
13. [Deployment em edge (Yocto Linux)](#13-deployment-em-edge-yocto-linux)
14. [Resolução de problemas (troubleshooting)](#14-resolução-de-problemas-troubleshooting)
15. [Glossário de termos](#15-glossário-de-termos)
16. [Referências e leitura adicional](#16-referências-e-leitura-adicional)
17. [Referência de funções por ficheiro](#17-referência-de-funções-por-ficheiro)

---

## 1. Para que serve este projeto?

### O problema em linguagem simples

Imagine que comprou um smartwatch que mede batimentos cardíacos e localização GPS. O que acontece hoje nos dispositivos comerciais?

1. O smartwatch envia os dados para a **cloud do fabricante** (ex.: Apple, Xiaomi, Garmin).
2. O fabricante guarda esses dados em **servidores dele**, controlados por ele.
3. Existe um "digital twin" (gémeo digital) do seu relógio **nos servidores do fabricante**, não nos seus.
4. Se mudar de fabricante, perde os dados. Se o fabricante fechar, perde os dados. Se vender o dispositivo, o comprador herda dados de uma conta que não é dele.
5. O fabricante pode vender dados agregados, mudar os termos de utilização, ou fechar a API quando quiser.

Na prática: **o dono do relógio é o consumidor, mas o dono dos dados é o fabricante**. Esta assimetria é exatamente o que a arquitetura C2DTA pretende corrigir.

### A solução proposta (C2DTA)

**C2DTA** significa *Consumer-Controlled Digital Twin Architecture* — arquitetura de gémeos digitais controlados pelo consumidor. A ideia central:

- Em vez do gémeo digital viver na cloud do fabricante, **vive num pequeno computador na rede de casa do consumidor** — a **Edge Gateway (EGW)**. Pode ser um Raspberry Pi, um mini-PC industrial, ou qualquer dispositivo Linux com alguns GB de memória.
- Essa Edge Gateway corre localmente todos os serviços necessários: receção de telemetria, armazenamento, gestão de identidade, e ancoragem em blockchain.
- A **posse** (ownership) do dispositivo é representada por um **cartão de identidade digital assinado criptograficamente** (uma Credencial Verificável, VC), que só o consumidor controla.
- Todo o **ciclo de vida** do dispositivo (fabrico → venda → reivindicação → uso → revenda) é registado de forma imutável num **blockchain partilhado** entre o fabricante (OEM) e um consórcio de certificação.
- Os **dados brutos** do dispositivo ficam na Edge Gateway do consumidor. Apenas **resumos periódicos (snapshots)** são guardados em IPFS (armazenamento descentralizado), com a assinatura criptográfica desses snapshots ancorada no blockchain — para que mais tarde se possa provar que os dados não foram alterados.

### O que está neste repositório

Este repositório é a **implementação de referência** do paper. Não é um protótipo parcial — todos os 8 casos de uso (UC1 a UC8) descritos no paper estão implementados e podem ser corridos localmente com um único comando (`docker compose up`). Inclui:

- Um **simulador de smartwatch** que publica batimentos e GPS a cada segundo.
- Um **broker MQTT** (Mosquitto) com TLS mútuo para receber a telemetria.
- Uma **plataforma de Digital Twin** (Eclipse Ditto) que mantém o estado atual do dispositivo.
- Um **blockchain de ecossistema** (Hyperledger Fabric) com dois chaincodes Go para ciclo de vida e tracking de datasets.
- Um **blockchain de identidade** (Hyperledger Indy) para registar DIDs e schemas de credenciais.
- **5 agentes SSI** (ACA-Py) — um por cada ator do ecossistema.
- **Armazenamento descentralizado** (IPFS Kubo) para snapshots.
- Um **orquestrador central** (EGW Controller, FastAPI) com API REST que expõe todos os UCs.
- Uma **camada Yocto** (`meta-edgegateway`) para empacotar tudo numa imagem Linux para dispositivos físicos.

### Em que é que estas tecnologias são usadas?

| Necessidade | Tecnologia escolhida |
|---|---|
| Telemetria rápida e leve (1 Hz) entre smartwatch e gateway | MQTT sobre TLS (Eclipse Mosquitto) |
| Manter o "retrato" atualizado do dispositivo | Eclipse Ditto (plataforma de Digital Twin) |
| Registar de forma imutável o ciclo de vida do dispositivo | Hyperledger Fabric (blockchain permissionada) |
| Registar identidades digitais de pessoas/organizações/dispositivos | Hyperledger Indy (blockchain de identidades) |
| Emitir e verificar credenciais (cartões digitais assinados) | ACA-Py (Aries Cloud Agent Python) |
| Guardar snapshots dos dados sem confiar num servidor central | IPFS (armazenamento endereçado por conteúdo) |
| Mensagens encriptadas ponto-a-ponto entre agentes | DIDComm 2.0 |
| Correr tudo junto com um comando | Docker Compose |
| Empacotar tudo numa imagem de Linux para edge | Yocto |

---

## 2. Conceitos fundamentais (sem pré-requisitos)

Se já conhece estes conceitos, pode saltar para a secção 3. Caso contrário, leia por ordem — cada um constrói sobre o anterior.

### 2.1 IoT e smart devices

**IoT** (*Internet of Things*) é a ideia de ligar objetos do dia-a-dia (relógios, frigoríficos, sensores industriais, carros) à Internet, para enviarem dados e receberem comandos. Um **smart device (SD)** é um desses objetos. Neste projeto, o smart device de exemplo é um **smartwatch** que publica batimento cardíaco e coordenadas GPS a cada segundo.

### 2.2 Edge computing e Edge Gateway

**Edge computing** significa "processar os dados perto de onde são gerados", em vez de mandar tudo para a cloud. A **Edge Gateway (EGW)** é o computador que fica **entre** os smart devices e a Internet. Neste projeto, é um mini-computador com Linux que:

- Recebe a telemetria dos smart devices na rede local.
- Corre localmente o gémeo digital (Ditto).
- Guarda localmente os snapshots (IPFS).
- Comunica apenas o estritamente necessário com o exterior (para o blockchain Fabric e Indy).

**Analogia:** se os smart devices são os "empregados" que reportam o que observam, a Edge Gateway é o "supervisor" que trabalha no mesmo edifício — em vez de enviar cada relatório para uma sede longínqua.

### 2.3 Digital Twin (gémeo digital)

Um **Digital Twin (DT)** é uma representação digital, **sempre atualizada**, de um objeto físico. No caso do smartwatch, o DT contém:

- Último batimento cardíaco medido
- Última coordenada GPS
- Timestamp (carimbo temporal) da última atualização

**Analogia:** é como uma ficha Excel do dispositivo que se atualiza sozinha sempre que chega informação nova. Se o fabricante precisar de saber o estado do relógio (para manutenção remota, por exemplo), não pergunta ao relógio — consulta o DT.

Neste projeto o DT é gerido pelo **Eclipse Ditto**, uma plataforma open-source da fundação Eclipse. O DT segue o padrão **Web of Things (WoT)** do W3C, que normaliza a descrição de "things" para serem interoperáveis.

### 2.4 Blockchain, ledger, chaincode (smart contract)

Um **blockchain** (ou **ledger distribuído**, **DLT**) é um "caderno" partilhado entre vários participantes, com três propriedades importantes:

1. **Imutabilidade:** uma vez escrita, uma linha não pode ser apagada nem editada. Só se pode acrescentar uma nova linha.
2. **Replicação:** todos os participantes têm uma cópia completa do caderno.
3. **Consenso:** só se escreve uma nova linha quando a maioria (ou um quórum configurável) concorda que a linha é válida.

Um **chaincode** (no vocabulário do Hyperledger Fabric) — também chamado de **smart contract** — é um pequeno programa que corre **dentro** do blockchain. Sempre que alguém quer escrever no caderno, tem de chamar uma função do chaincode, que decide se a escrita é válida.

**Analogia:** o chaincode é como o regulamento interno de uma biblioteca — só se pode requisitar um livro se estiver disponível; só se pode devolver se estiver requisitado; e há um funcionário (o chaincode) que verifica isso antes de alterar o registo.

Neste projeto existem **dois blockchains distintos**:

- **Hyperledger Fabric** (blockchain do ecossistema) → regista o ciclo de vida dos dispositivos (fabricado, vendido, reivindicado, etc.) e os snapshots IPFS.
- **Hyperledger Indy** (blockchain de identidade) → regista os **DIDs** e as **VCs schemas** (ver a seguir).

### 2.5 SSI, DID e VC

**SSI** (*Self-Sovereign Identity*, identidade autossoberana) é um modelo de identidade digital em que **o utilizador é o único dono das suas credenciais** — nem uma empresa nem um governo as pode revogar à distância sem o seu consentimento.

Duas peças centrais da SSI:

- **DID** (*Decentralized Identifier*): é um identificador único, criado pelo próprio titular, sem precisar de uma autoridade central. Parece-se com uma string tipo `did:sov:2ABCdef123`. A chave criptográfica associada ao DID está só no titular (no "wallet" dele).
- **VC** (*Verifiable Credential*, credencial verificável): é um **cartão digital assinado** que uma entidade (o *emissor*) dá a outra (o *titular*). Um VC tem três características:
  1. É **assinado criptograficamente** pelo emissor → prova que é autêntico.
  2. Pode ser **verificado offline** por qualquer pessoa que tenha o DID público do emissor → não precisa de perguntar ao emissor se o cartão é válido.
  3. Pode ser **revogado** pelo emissor (publicando uma revogação no blockchain Indy) se, por exemplo, a pessoa deixar de cumprir os requisitos.

**Analogia para VC:** é como o cartão de cidadão digital. A Autoridade Tributária (emissor) dá-lhe um cartão com o seu NIF assinado. Quando alguém (verificador) precisa de confirmar o seu NIF, não liga à AT — verifica a assinatura do cartão com a chave pública da AT.

No C2DTA existem **três VCs diferentes** (ver secção 6):

- **Enrollment VC:** atesta que uma empresa é fabricante aprovado no consórcio.
- **Genesis VC:** atesta que um dispositivo foi genuinamente fabricado por um OEM aprovado.
- **Ownership VC:** atesta que um consumidor é dono de um dispositivo específico.

### 2.6 DIDComm

**DIDComm** é um protocolo de **mensagens encriptadas ponto-a-ponto** entre dois agentes SSI, usando os seus DIDs como destinatários. Em vez de enviarmos um email (que o servidor lê) ou um pedido HTTP (que o servidor lê), mandamos uma mensagem encriptada com a chave pública do destinatário — só ele consegue desencriptar.

Neste projeto, o DIDComm é o "tubo" por onde passam as propostas de credenciais (Enrollment, Genesis, Ownership) e as provas de posse dessas credenciais.

### 2.7 MQTT e o modelo pub/sub

**MQTT** (*Message Queuing Telemetry Transport*) é um protocolo leve, pensado para IoT, baseado num modelo **publish/subscribe (pub/sub)**:

- Os **produtores** de mensagens (publishers) mandam-nas para um **tópico** (ex.: `egw/abc123/telemetry`).
- Os **consumidores** (subscribers) dizem ao broker quais os tópicos que querem receber.
- O **broker** (neste caso, Eclipse Mosquitto) encaminha cada mensagem de cada publisher para todos os subscribers interessados.

**Níveis de qualidade (QoS):**

- **QoS 0:** entrega no melhor esforço (pode perder-se).
- **QoS 1:** pelo menos uma entrega garantida (pode duplicar).
- **QoS 2:** exatamente uma entrega garantida (mais caro em recursos).

Neste projeto, a telemetria do smartwatch usa **QoS 1** — perder um ponto de batimento cardíaco não é grave, mas queremos garantir que a maioria chega.

**TLS mútuo (mTLS):** nesta implementação, o Mosquitto está configurado a exigir certificado do cliente *e* do servidor. Não chega ter utilizador e palavra-passe — cada smart device tem o seu próprio certificado X.509 assinado pela autoridade certificadora (CA) local.

### 2.8 IPFS (armazenamento endereçado por conteúdo)

**IPFS** (*InterPlanetary File System*) é um sistema de armazenamento distribuído peer-to-peer. Em vez de identificar um ficheiro por caminho (`/home/user/file.json`), identifica-o por um **hash criptográfico** do conteúdo — chamado **CID** (*Content Identifier*).

Duas propriedades importantes:

- **Determinístico:** o mesmo conteúdo gera sempre o mesmo CID.
- **À prova de adulteração:** se alguém alterar 1 byte no ficheiro, o CID muda. Logo, publicar um CID no blockchain é equivalente a publicar uma "impressão digital" do conteúdo.

Neste projeto, o EGW Controller tira periodicamente "fotografias" (snapshots) do estado do Digital Twin → guarda o JSON no IPFS → recebe um CID → regista esse CID no Fabric. Isto cria uma cadeia de custódia auditável: qualquer pessoa pode pegar no CID do blockchain, ir buscar o JSON ao IPFS, e confirmar que o conteúdo corresponde ao hash.

### 2.9 Web of Things (WoT)

**Web of Things** é um padrão do W3C que define como descrever um "thing" (dispositivo IoT) de forma interoperável. A peça central é o **Thing Description (TD)** — um ficheiro JSON-LD que diz: "este dispositivo tem estas propriedades, aceita estas ações, emite estes eventos".

Neste projeto, o smartwatch é descrito pelo ficheiro [services/ditto/wot/smartwatch-td.jsonld](../services/ditto/wot/smartwatch-td.jsonld), que define propriedades `heartbeat` e `geolocation`. O Ditto usa esta descrição para validar as mensagens recebidas.

### 2.10 Yocto Linux

**Yocto** é um sistema de construção de distribuições Linux customizadas para **sistemas embebidos**. Em vez de instalar Ubuntu num Raspberry Pi, a Yocto permite criar uma imagem minimal, com apenas os pacotes necessários, para um dispositivo específico. É muito usada em IoT industrial.

O Yocto organiza-se em **layers** (camadas):

- `poky` é a base (fornecida pela Yocto Project).
- `meta-<board>` são camadas para hardware específico (ex.: `meta-raspberrypi`).
- `meta-edgegateway` (a camada deste projeto) adiciona os pacotes e a configuração do C2DTA.

---

## 3. Arquitetura C2DTA em visão geral

### Diagrama do sistema

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Edge do Consumidor                           │
│                                                                     │
│  ┌─────────────┐    MQTT/TLS    ┌──────────────┐                    │
│  │ Smart Device│───────────────▶│  Mosquitto   │                    │
│  │ (Smartwatch)│   egw/UUID/    │  MQTT Broker │                    │
│  └─────────────┘   telemetry    └──────┬───────┘                    │
│                                        │                            │
│  ┌─────────────────────────────────────▼──────────────────────────┐ │
│  │                    EGW Controller (FastAPI)                    │ │
│  │          Orquestra UC1–UC8 · REST API :8090                    │ │
│  └──────┬──────────┬──────────┬──────────┬───────────┬────────────┘ │
│         │          │          │          │           │              │
│  ┌──────▼──┐ ┌─────▼────┐ ┌──▼──────┐ ┌─▼──────┐ ┌─▼────────┐      │
│  │  Ditto  │ │  ACA-Py  │ │ Fabric  │ │  Indy  │ │   IPFS   │      │
│  │   DT    │ │ 5 agents │ │ 2 peers │ │  Pool  │ │  Kubo    │      │
│  │  :8080  │ │:8020-71  │ │ :7050-51│ │ :9000  │ │  :8081   │      │
│  └─────────┘ └──────────┘ └─────────┘ └────────┘ └──────────┘      │
│                                                                     │
│  ┌──────────────────────────┐                                       │
│  │  DIDComm Agent (MVP)     │                                       │
│  │  :8000 (encriptação P2P) │                                       │
│  └──────────────────────────┘                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Legenda caixa a caixa

- **Smart Device**: dispositivo físico simulado (ou real, no futuro). Publica telemetria a cada segundo.
- **Mosquitto**: broker MQTT com TLS. Recebe as publicações e encaminha-as para os subscribers (Ditto).
- **EGW Controller**: servidor Python (FastAPI) que é o "cérebro" do Edge Gateway. Recebe pedidos REST (por exemplo: "reivindica este dispositivo") e coordena todos os outros serviços.
- **Ditto**: plataforma de Digital Twin. Mantém o estado atual ("last seen") do dispositivo. Escuta MQTT e atualiza-se automaticamente.
- **ACA-Py**: 5 agentes SSI, um por ator do ecossistema (Consortium, OEM, Consumer A, EGW, Smart Device). Emitem e verificam credenciais.
- **Fabric**: blockchain permissionada com 2 orgs (Consortium e OEM) + 1 orderer + 2 peers + 2 CouchDB + 2 CAs. Guarda o ciclo de vida dos dispositivos.
- **Indy**: blockchain de identidade com 4 nós (von-network). Guarda os schemas das VCs e as definições de credencial.
- **IPFS**: armazenamento descentralizado. Guarda snapshots do Digital Twin.
- **DIDComm Agent**: MVP autónomo para enviar mensagens DIDComm 2.0 encriptadas entre agentes (função secundária; o ACA-Py já faz DIDComm v1/v2 para as operações principais).

### Fluxo de dados resumido

1. O smart device publica telemetria em MQTT.
2. O Mosquitto entrega ao Ditto (configurado via "connection" MQTT).
3. O Ditto atualiza o "thing" correspondente ao dispositivo.
4. Periodicamente, o EGW Controller lê o thing do Ditto → serializa JSON → envia para IPFS → recebe CID → regista o CID no Fabric.
5. Para operações do ciclo de vida (comprar, vender, reivindicar), o EGW Controller chama a API do ACA-Py (para credenciais) e do Fabric (para estado do dispositivo).

---

## 4. Os 9 serviços, um a um

Esta secção detalha cada serviço: **para que serve**, **tecnologia usada**, **portas expostas**, e **ficheiros-chave**. Todos os serviços correm como containers Docker, orquestrados pelo [docker-compose.yml](../docker-compose.yml) na raiz do projeto.

### 4.1 Mosquitto (MQTT Broker)

**Para que serve:** recebe a telemetria dos smart devices e entrega-a ao Ditto. É o "servidor de correio" de mensagens IoT.

**Tecnologia:** [Eclipse Mosquitto 2.0](https://mosquitto.org/) — broker MQTT open-source leve, muito usado em IoT. Configurado com **TLS mútuo obrigatório** (cada cliente tem certificado próprio).

**Porta externa:** `8883` (MQTT sobre TLS).

**Tópicos principais:**
- `egw/<device_uuid>/telemetry` — sensor → gateway (QoS 1)
- `egw/<device_uuid>/command` — gateway → sensor (QoS 2)
- `egw/<device_uuid>/status` — bidirecional (QoS 1)
- `egw/system/#` — eventos internos (QoS 0)

**Ficheiros-chave:**
- [services/mosquitto/config/mosquitto.conf](../services/mosquitto/config/mosquitto.conf) — configuração do broker
- [services/mosquitto/config/acl.conf](../services/mosquitto/config/acl.conf) — controlo de acesso por tópico
- [services/mosquitto/certs/generate-certs.sh](../services/mosquitto/certs/generate-certs.sh) — gera a CA, o certificado do servidor e os certificados dos clientes
- [services/mosquitto/README.md](../services/mosquitto/README.md)

### 4.2 Smart Device Simulator

**Para que serve:** simula um smartwatch físico que publica batimento cardíaco e GPS a cada segundo. Permite testar toda a arquitetura sem hardware real.

**Tecnologia:** Python 3.12 com [paho-mqtt](https://pypi.org/project/paho-mqtt/) (cliente MQTT mais popular em Python) e Pydantic (validação de dados).

**Porta exposta:** nenhuma (é apenas um cliente MQTT que estabelece ligação de saída para o broker).

**Dados gerados (1 Hz):**
```json
{
  "device_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "heartbeat_bpm": 74,
  "geolocation": {"lat": 38.7223012, "lon": -9.1393045},
  "timestamp": "2026-04-19T10:30:00.123456Z"
}
```

**Modelo de geração:**
- Batimentos: passeio aleatório com reversão à média (70 bpm), limitado entre 40 e 200.
- GPS: ligeira deriva aleatória (~5 m por leitura) à volta de coordenadas iniciais (default: 38.7223, -9.1393 — Lisboa).

**Variáveis de ambiente relevantes:**
- `SD_UUID` — UUID do dispositivo (gerado automaticamente se não definido).
- `MQTT_BROKER_HOST`, `MQTT_BROKER_PORT` — endereço do broker.
- `MQTT_CA_CERT`, `MQTT_CLIENT_CERT`, `MQTT_CLIENT_KEY` — caminhos para certificados TLS.
- `SD_PUBLISH_INTERVAL_MS` — intervalo entre publicações (default: 1000 ms).
- `SD_INITIAL_HEARTBEAT`, `SD_INITIAL_LAT`, `SD_INITIAL_LON` — valores iniciais.

**Ficheiros-chave:**
- [services/smart-device-simulator/src/smart_device_simulator/simulator.py](../services/smart-device-simulator/src/smart_device_simulator/simulator.py)
- [services/smart-device-simulator/src/smart_device_simulator/mqtt_publisher.py](../services/smart-device-simulator/src/smart_device_simulator/mqtt_publisher.py)
- [services/smart-device-simulator/examples/run_simulator.py](../services/smart-device-simulator/examples/run_simulator.py)
- [services/smart-device-simulator/README.md](../services/smart-device-simulator/README.md)

### 4.3 Eclipse Ditto (Digital Twin Platform)

**Para que serve:** mantém o estado atualizado ("twin") de cada dispositivo. Recebe atualizações via MQTT e expõe uma API REST para consultar/modificar o estado.

**Tecnologia:** [Eclipse Ditto 3.5.6](https://www.eclipse.org/ditto/) — conjunto de microserviços Java sobre Akka. Armazena estado em **MongoDB 6.0**. Compatível com **Web of Things (WoT) TD v1.1**.

**Arquitetura interna (7 containers):**
1. `mongodb` — persistência.
2. `ditto-policies` — controlo de acesso (policies).
3. `ditto-things` — CRUD de things.
4. `ditto-things-search` — queries ricas.
5. `ditto-connectivity` — conectores externos (MQTT, AMQP, Kafka).
6. `ditto-gateway` — gateway API.
7. `nginx` — reverse proxy com autenticação Basic.

**Porta externa:** `8080` (via nginx, autenticação `ditto:c2dta` para API, `devops:c2dta-devops` para DevOps).

**Modelo do thing (smartwatch):**
```json
{
  "thingId": "org.c2dta:<device_uuid>",
  "features": {
    "heartbeat":    {"properties": {"bpm": 72}},
    "geolocation":  {"properties": {"latitude": 38.7223, "longitude": -9.1393}},
    "timestamp":    {"properties": {"value": "2026-04-19T10:30:00Z"}}
  }
}
```

**Ficheiros-chave:**
- [services/ditto/docker-compose.yml](../services/ditto/docker-compose.yml) — stack Ditto
- [services/ditto/nginx/nginx.conf](../services/ditto/nginx/nginx.conf) — reverse proxy
- [services/ditto/connectivity/mqtt-connection.json](../services/ditto/connectivity/mqtt-connection.json) — source MQTT
- [services/ditto/wot/smartwatch-td.jsonld](../services/ditto/wot/smartwatch-td.jsonld) — WoT Thing Description
- [services/ditto/tests/test_ditto_api.py](../services/ditto/tests/test_ditto_api.py) — testes de integração
- [services/ditto/README.md](../services/ditto/README.md)

### 4.4 Hyperledger Fabric (Blockchain do ecossistema)

**Para que serve:** regista de forma imutável o ciclo de vida de cada dispositivo (fabricado → disponível → em trânsito → reivindicado → gemeado → descomissionado) e os snapshots IPFS de datasets.

**Tecnologia:** [Hyperledger Fabric 2.5](https://hyperledger-fabric.readthedocs.io/) — blockchain permissionada (consórcio). Chaincodes (smart contracts) em **Go 1.21**. State database em **CouchDB 3.3** (permite queries ricas).

**Topologia (dev):**
- 1 orderer Raft (`c2dta-orderer`, porta 7050)
- 2 organizações: Consortium e OEM
- 2 peers: `peer0.consortium.c2dta.example.com` (7051) e `peer0.oem.c2dta.example.com` (9051)
- 2 CouchDB state DBs: `couchdb0`, `couchdb1`
- 2 CAs: Consortium CA (7054), OEM CA (8054)
- 1 canal: `c2dta-channel`
- Endorsement policy: ambos os peers têm de aprovar

**Dois chaincodes:**

1. **device-lifecycle** ([services/fabric/chaincode/device-lifecycle/device_lifecycle.go](../services/fabric/chaincode/device-lifecycle/device_lifecycle.go)):
   - `RegisterDeviceModel(modelID, manufacturer, wotTDHash)`
   - `ManufactureDevice(deviceID, modelID, manufacturerID, genesisVCHash)`
   - `MakeAvailable(deviceID)`
   - `InitiateTransit(deviceID, buyerDID)`
   - `ClaimDevice(deviceID, controllerDID, ownershipVCHash)`
   - `TwinDevice(deviceID, dittoThingID)`
   - `UntwinDevice(deviceID)`
   - `DecommissionDevice(deviceID)`
   - `QueryDevice(deviceID)`
   - `QueryDevicesByState(state)` — rich query CouchDB
   - `QueryDevicesByOwner(ownerDID)` — rich query CouchDB

2. **dataset-tracking** (tracking de snapshots IPFS):
   - `RegisterDataset(datasetID, deviceID, ipfsHash, ownerDID, sizeBytes, recordCount, startTime, endTime)`
   - `QueryDatasetsByDevice(deviceID)`
   - `TransferDatasetOwnership(datasetID, newOwnerDID)`

**Ficheiros-chave:**
- [services/fabric/docker-compose.yml](../services/fabric/docker-compose.yml)
- [services/fabric/configtx/](../services/fabric/configtx/) — configuração de canal
- [services/fabric/chaincode/](../services/fabric/chaincode/)
- [services/fabric/scripts/network-up.sh](../services/fabric/scripts/network-up.sh)
- [services/fabric/scripts/network-down.sh](../services/fabric/scripts/network-down.sh)
- [services/fabric/scripts/deploy-chaincode.sh](../services/fabric/scripts/deploy-chaincode.sh)
- [services/fabric/README.md](../services/fabric/README.md)

### 4.5 Hyperledger Indy (Blockchain de identidade)

**Para que serve:** é o registo público de DIDs e de schemas de credenciais. Quando um OEM emite uma Enrollment VC, a definição dessa VC está guardada no Indy, para qualquer verificador poder consultá-la.

**Tecnologia:** [Hyperledger Indy](https://www.hyperledger.org/projects/hyperledger-indy) distribuído pelo [von-network](https://github.com/bcgov/von-network) (Governo da Colúmbia Britânica, Canadá). 4 nós locais.

**Porta externa:** `9000` (Web UI / explorador do pool), `9701-9708` (portas internas dos nós).

**Steward seed (apenas desenvolvimento):** `C2DTA000000000000000000Steward1`

**Schemas de credencial (em [services/indy/schemas/](../services/indy/schemas/)):**
- `enrollment_vc.json` — schema da Enrollment VC.
- `genesis_vc.json` — schema da Genesis VC.
- `ownership_vc.json` — schema da Ownership VC.

**Ficheiros-chave:**
- [services/indy/docker-compose.yml](../services/indy/docker-compose.yml)
- [services/indy/README.md](../services/indy/README.md)

### 4.6 ACA-Py (5 agentes SSI)

**Para que serve:** cada ator do ecossistema (Consórcio, OEM, Consumidor, EGW, SD) precisa de um "agente" que faça as operações SSI: criar DIDs, emitir credenciais, responder a pedidos de prova, estabelecer conexões DIDComm. O ACA-Py é esse agente.

**Tecnologia:** [ACA-Py 1.2.2](https://github.com/openwallet-foundation/acapy) (Aries Cloud Agent Python) — implementação de referência dos protocolos Aries/DIDComm, mantida pela OpenWallet Foundation.

**5 instâncias:**

| Agente | Ator | Papel | HTTP | Admin | VCs que emite | VCs que guarda |
|---|---|---|---|---|---|---|
| `aca-py-consortium` | Consórcio (1@C) | Steward | 8020 | 8021 | Enrollment VC | — |
| `aca-py-oem` | OEM (1@O) | Fabricante | 8030 | 8031 | Genesis VC, Ownership VC | Enrollment VC |
| `aca-py-consumer-a` | Consumidor A (1@A) | Comprador | 8040 | 8041 | — | Ownership VC |
| `aca-py-egw` | Edge Gateway (1@egw) | Gateway | 8060 | 8061 | — | Genesis VC |
| `aca-py-sd` | Smart Device (1@sd) | Dispositivo | 8070 | 8071 | — | Genesis VC |

**Goal codes (automatização de fluxos DIDComm):**

| Goal code | Usado em |
|---|---|
| `c2dta.consortium.enroll.OEM` | UC1 |
| `c2dta.consortium.registermodel` | UC2 |
| `c2dta.consortium.registerdevice` | UC3 |
| `c2dta.consortium.buydevice` | UC4 |
| `c2dta.consortium.claim` | UC5 |
| `c2dta.egw.twin` | UC6 |
| `c2dta.egw.untwin` | UC7 |
| `c2dta.egw.sell` | UC8 |

**Protocolos Aries usados:**
- **Out-of-Band (RFC 0434)** — convites iniciais (frequentemente em QR code)
- **Issue Credential v2 (RFC 0453)** — emissão de VC
- **Present Proof v2 (RFC 0454)** — apresentação de prova
- **Action Menu (RFC 0509)** — menu de ações interativas
- **Basic Message (RFC 0095)** — mensagens livres

**Ficheiros-chave:**
- [services/aca-py/docker-compose.yml](../services/aca-py/docker-compose.yml) — 5 containers ACA-Py
- [services/aca-py/plugins/c2dta_protocols/](../services/aca-py/plugins/c2dta_protocols/) — plugins C2DTA:
  - `enrollment.py` — protocolo de inscrição
  - `genesis.py` — protocolo Genesis VC
  - `goal_codes.py` — definições de goal codes
  - `ownership.py` — protocolo Ownership VC
- [services/aca-py/README.md](../services/aca-py/README.md)

### 4.7 IPFS (Kubo)

**Para que serve:** armazenamento descentralizado de snapshots do Digital Twin. Cada snapshot recebe um CID (hash criptográfico), que depois é registado no Fabric como âncora.

**Tecnologia:** [IPFS Kubo v0.28.0](https://github.com/ipfs/kubo) — implementação em Go do IPFS, a mais usada.

**Portas externas:**
- `5001` — API HTTP (add, cat, pin)
- `8081` — gateway HTTP público (substituído do 8080 para não colidir com o Ditto)
- `4001` — swarm P2P

**Fluxo típico:**
1. EGW Controller lê o thing do Ditto: `GET /api/2/things/<id>/features`
2. Serializa como JSON.
3. POST `/api/v0/add?pin=true` → IPFS guarda e devolve CID.
4. EGW Controller chama `RegisterDataset(...)` no chaincode `dataset-tracking`.

**Formato do snapshot:**
```json
{
  "device_id": "550e8400-e29b-41d4-a716-446655440000",
  "thing_id": "org.c2dta:550e8400-e29b-41d4-a716-446655440000",
  "snapshot_time": "2026-04-19T10:30:00Z",
  "features": {...}
}
```

**Ficheiros-chave:**
- [services/ipfs/docker-compose.yml](../services/ipfs/docker-compose.yml)
- [services/ipfs/tests/](../services/ipfs/tests/)
- [services/ipfs/README.md](../services/ipfs/README.md)

### 4.8 EGW Controller (orquestrador central)

**Para que serve:** é o **cérebro** do Edge Gateway. Recebe pedidos REST dos utilizadores/aplicações, e coordena todos os outros serviços para executar os 8 use cases.

**Tecnologia:** Python 3.12 + [FastAPI](https://fastapi.tiangolo.com/) + [httpx](https://www.python-httpx.org/) (cliente HTTP async) + [Pydantic](https://docs.pydantic.dev/) (validação).

**Porta externa:** `8090`. Documentação OpenAPI automática em `http://localhost:8090/docs`.

**Estrutura de código:**

```
services/egw-controller/
├── src/egw_controller/
│   ├── api.py                      # FastAPI app + endpoints
│   ├── config.py                   # leitura de variáveis de ambiente
│   ├── models.py                   # modelos Pydantic (DeviceState, requests/responses)
│   ├── transaction.py              # TransactionManager: transações multi-passo
│   ├── clients/
│   │   ├── fabric_client.py        # chamadas ao chaincode Fabric
│   │   ├── aca_py_client.py        # chamadas à admin API do ACA-Py
│   │   ├── ditto_client.py         # CRUD de things no Ditto
│   │   └── ipfs_client.py          # add/cat/pin IPFS
│   └── use_cases/
│       ├── uc1_oem_enrollment.py
│       ├── uc2_model_registration.py
│       ├── uc3_device_registration.py
│       ├── uc4_device_purchase.py
│       ├── uc5_device_claiming.py
│       ├── uc6_device_twinning.py
│       ├── uc7_device_untwinning.py
│       └── uc8_device_selling.py
├── tests/                          # 24 testes unitários
├── examples/
│   └── run_full_lifecycle.py       # demo completa UC1→UC8
├── Dockerfile
├── pyproject.toml
└── requirements.txt
```

**Transaction Manager:** cada use case é uma **transação** com vários **passos**. O `TransactionManager` mantém o estado de cada passo (`pending` → `in_progress` → `completed`/`failed`). Assim, se um UC6 falhar a meio da configuração do MQTT, sabe-se em que passo foi o erro e o que já estava feito.

**Variáveis de ambiente principais:**

| Variável | Default | Descrição |
|---|---|---|
| `DITTO_URL` | `http://localhost:8080` | URL do Ditto |
| `DITTO_USER` / `DITTO_PASS` | `ditto` / `c2dta` | credenciais Basic |
| `MQTT_BROKER_HOST` / `MQTT_BROKER_PORT` | `localhost` / `8883` | MQTT |
| `IPFS_API_URL` | `http://localhost:5001` | API IPFS |
| `ACAPY_CONSORTIUM_URL` | `http://localhost:8021` | admin API Consórcio |
| `ACAPY_OEM_URL` | `http://localhost:8031` | admin API OEM |
| `ACAPY_EGW_URL` | `http://localhost:8061` | admin API EGW |
| `FABRIC_PEER_URL` | `localhost:7051` | peer Fabric |
| `FABRIC_CHANNEL` | `c2dta-channel` | canal Fabric |
| `DIDCOMM_AGENT_URL` | `http://localhost:8000` | agente DIDComm |
| `EGW_DB_PATH` | — | BD local opcional |
| `EGW_DATASET_INTERVAL_S` | `86400` | intervalo entre snapshots IPFS |

**Ficheiros-chave:**
- [services/egw-controller/src/egw_controller/api.py](../services/egw-controller/src/egw_controller/api.py)
- [services/egw-controller/src/egw_controller/use_cases/](../services/egw-controller/src/egw_controller/use_cases/)
- [services/egw-controller/src/egw_controller/transaction.py](../services/egw-controller/src/egw_controller/transaction.py)
- [services/egw-controller/examples/run_full_lifecycle.py](../services/egw-controller/examples/run_full_lifecycle.py)
- [services/egw-controller/README.md](../services/egw-controller/README.md)

### 4.9 DIDComm Agent (MVP)

**Para que serve:** implementação MVP (*Minimum Viable Product*) de um agente DIDComm 2.0 autónomo. Complementa o ACA-Py para casos em que se queira uma comunicação DIDComm mais leve, sem o peso completo do ACA-Py.

**Tecnologia:** Python 3.12 + FastAPI + [libsodium](https://doc.libsodium.org/) (via [PyNaCl](https://pynacl.readthedocs.io/)) para criptografia — **X25519** (acordo de chave) + **HKDF** (derivação) + **ChaCha20-Poly1305** (encriptação autenticada).

**Porta externa:** `8000`.

**Endpoints da API:**
- `POST /agent` — cria/obtém agente (idempotente)
- `POST /accept` — aceita invitação → contra-invitation
- `POST /complete` — finaliza handshake
- `GET /peers?agent_id=...` — lista DIDs pareados
- `POST /send` — envia mensagem encriptada
- `POST /receive` — recebe/desencripta envelope
- `GET /health` — health check

**Limitações atuais (MVP):**
- Chaves X25519 voláteis (perdem-se no restart) a menos que se configure `DIDCOMM_DB_PATH`.
- Sem autenticação HTTP (usar atrás de mTLS).
- Sem fila offline, sem attachments, sem revogação.

**Ficheiros-chave:**
- [services/didcomm-agent/src/didcomm_agent/api.py](../services/didcomm-agent/src/didcomm_agent/api.py)
- [services/didcomm-agent/src/didcomm_agent/crypto.py](../services/didcomm-agent/src/didcomm_agent/crypto.py)
- [services/didcomm-agent/src/didcomm_agent/service.py](../services/didcomm-agent/src/didcomm_agent/service.py)
- [services/didcomm-agent/examples/demo_exchange.py](../services/didcomm-agent/examples/demo_exchange.py)
- [services/didcomm-agent/examples/smoke_api.py](../services/didcomm-agent/examples/smoke_api.py)
- [services/didcomm-agent/README.md](../services/didcomm-agent/README.md)

---

## 5. Ciclo de vida do dispositivo (6 estados)

O coração do C2DTA é a **máquina de estados** que cada dispositivo percorre desde o fabrico até à descomissionação. Está implementada em Go no chaincode [device_lifecycle.go](../services/fabric/chaincode/device-lifecycle/device_lifecycle.go).

### Os 6 estados

| Estado | Significado |
|---|---|
| **Manufactured** | Dispositivo foi fabricado pelo OEM mas ainda não está à venda. |
| **Available** | Disponível no catálogo para compra. |
| **In-Transit** | Vendido, a caminho do consumidor. |
| **Claimed** | Consumidor recebeu e "reivindicou" o dispositivo. |
| **Twinned** | Digital Twin ativo — a enviar telemetria e a gerar snapshots. |
| **Decommissioned** | Estado terminal — dispositivo desativado definitivamente. |

### Diagrama de transições

```
                UC3                    UC3
  [start] ─────────▶ Manufactured ────────▶ Available
                                                │
                                          UC4   │ InitiateTransit
                                                ▼
                                           In-Transit
                                                │
                                          UC5   │ ClaimDevice
                                                ▼
                                 ┌────────── Claimed ◀──────────┐
                                 │              │                │
                             UC6 │ TwinDevice   │ UntwinDevice   │ UC7
                                 ▼              │                │
                              Twinned ──────────┘                │
                                                                 │
                         UC8 (re-entra via UC4/UC5) ─────────────┘
                                │
                                ▼
                          Decommissioned (terminal)
```

### Tabela de transições

| Transição | Função chaincode | Acionada pelo UC |
|---|---|---|
| (inexistente) → Manufactured | `ManufactureDevice` | UC3 |
| Manufactured → Available | `MakeAvailable` | UC3 |
| Available → In-Transit | `InitiateTransit` | UC4 |
| In-Transit → Claimed | `ClaimDevice` | UC5 |
| Claimed → Twinned | `TwinDevice` | UC6 |
| Twinned → Claimed | `UntwinDevice` | UC7 |
| Claimed → In-Transit | `InitiateTransit` | UC8 |
| Qualquer → Decommissioned | `DecommissionDevice` | (manual) |

### Exemplo narrativo

> **Cenário:** a SmartWatch Corp acabou de fabricar um relógio novo.
>
> 1. A SmartWatch Corp chama `ManufactureDevice` → o dispositivo entra no estado **Manufactured**.
> 2. Depois de controlo de qualidade, chama `MakeAvailable` → estado **Available**. O dispositivo aparece no catálogo online.
> 3. A Alice compra o relógio. O OEM chama `InitiateTransit` com o DID da Alice → estado **In-Transit**.
> 4. O pacote chega a casa da Alice. Ela faz scan do QR code na caixa; a Edge Gateway dela chama `ClaimDevice` com a prova de Ownership VC → estado **Claimed**.
> 5. A Alice decide ativar o Digital Twin. A EGW chama `TwinDevice` → estado **Twinned**. O relógio começa a enviar telemetria a 1 Hz para o Mosquitto → Ditto.
> 6. Um ano depois, a Alice vende o relógio ao Bob. Primeiro a EGW chama `UntwinDevice` → **Claimed**. Depois o OEM revoga a Ownership VC da Alice, emite uma nova para o Bob e chama `InitiateTransit` → **In-Transit** outra vez. O Bob reivindica o relógio → **Claimed** com o DID dele.
> 7. Mais tarde, o relógio avaria irreparavelmente. O OEM chama `DecommissionDevice` → estado final **Decommissioned**.

---

## 6. Credenciais Verificáveis (VCs)

### As 3 schemas do C2DTA

| Schema | Emissor | Titular | Usado em |
|---|---|---|---|
| **Enrollment VC** | Consórcio | OEM | UC1 (emissão), UC2 (verificação) |
| **Genesis VC** | OEM | EGW ou Smart Device | UC3 (emissão), UC5 (verificação) |
| **Ownership VC** | OEM | Consumidor | UC4 (emissão), UC5 (verificação), UC8 (revogação + reemissão) |

### Enrollment VC (atributos)

Prova que uma empresa é fabricante aprovado no consórcio.

| Atributo | Tipo | Descrição |
|---|---|---|
| `organization_name` | string | Nome legal da empresa |
| `organization_did` | string | DID público do OEM |
| `role` | string | Papel no consórcio (ex.: "OEM") |
| `enrollment_date` | string | ISO 8601 |
| `consortium_id` | string | Identificador do consórcio |
| `expiry_date` | string | Data de expiração |

### Genesis VC (atributos)

Prova que um dispositivo foi genuinamente fabricado por um OEM aprovado.

| Atributo | Tipo | Descrição |
|---|---|---|
| `device_uuid` | string | UUID único do dispositivo |
| `model_id` | string | Modelo registado em UC2 |
| `manufacturer_did` | string | DID do OEM |
| `manufacture_date` | string | ISO 8601 |
| `firmware_version` | string | Versão do firmware |
| `wot_td_hash` | string | Hash do WoT TD |
| `serial_number` | string | Número de série físico |

### Ownership VC (atributos)

Prova que um consumidor é dono de um dispositivo específico.

| Atributo | Tipo | Descrição |
|---|---|---|
| `device_uuid` | string | Identificador do dispositivo |
| `owner_did` | string | DID do consumidor |
| `acquisition_date` | string | Data da compra (ISO 8601) |
| `previous_owner_did` | string | DID do dono anterior (vazio na primeira venda) |
| `transfer_tx_hash` | string | Hash da transação Fabric |

Os ficheiros JSON-LD destas schemas estão em [services/indy/schemas/](../services/indy/schemas/).

---

## 7. Os 8 Use Cases passo a passo

Esta secção descreve cada UC em detalhe: atores, fluxo narrativo, diagrama de sequência simplificado, endpoint REST, exemplo de `curl` e ficheiro de código.

### UC1 — OEM Enrollment

**O que é:** uma nova empresa candidata-se a ser reconhecida como fabricante aprovado no consórcio C2DTA.

**Atores:** Consórcio (1@C), OEM (1@O).

**Fluxo narrativo:**
1. O Consórcio cria um convite Out-of-Band (OOB) com o goal code `c2dta.consortium.enroll.OEM` (pode ser um QR code mostrado numa reunião).
2. O OEM aceita o convite → estabelece conexão DIDComm com o Consórcio.
3. O Consórcio envia uma proposta de Enrollment VC ao OEM.
4. O OEM responde com provas documentais (ex.: registo comercial).
5. O Consórcio verifica as provas e emite a Enrollment VC.
6. O OEM guarda a Enrollment VC no wallet do seu agente ACA-Py.

**Sequência:**
```
Consorcio                  OEM                  Indy
   │──── OOB invite ───────▶│                     │
   │                        │                     │
   │◀─── accept ────────────│                     │
   │                        │                     │
   │──── propose VC ───────▶│                     │
   │                        │                     │
   │◀─── docs prova ────────│                     │
   │                        │                     │
   │──── issue VC ─────────▶│──── store DID ─────▶│
```

**Endpoint:** `POST /uc/enrollment`

**Payload:**
```json
{
  "organization_name": "SmartWatch Corp",
  "organization_did": "did:sov:oem-smartwatch-001"
}
```

**Exemplo curl:**
```bash
curl -X POST http://localhost:8090/uc/enrollment \
  -H "Content-Type: application/json" \
  -d '{"organization_name":"SmartWatch Corp","organization_did":"did:sov:oem-smartwatch-001"}'
```

**Código:** [services/egw-controller/src/egw_controller/use_cases/uc1_oem_enrollment.py](../services/egw-controller/src/egw_controller/use_cases/uc1_oem_enrollment.py)

**Resultado esperado:**
```json
{
  "success": true,
  "use_case": "UC1",
  "message": "OEM SmartWatch Corp inscrito no consorcio",
  "data": {"transaction_id": "uuid-..."}
}
```

---

### UC2 — Device Model Registration

**O que é:** o OEM regista um novo modelo de dispositivo (ex.: "SmartWatch X1") no blockchain Fabric, para poder começar a fabricar unidades desse modelo.

**Atores:** OEM (1@O), Consórcio (1@C).

**Fluxo narrativo:**
1. O OEM pede ao Consórcio o menu de ações disponíveis.
2. O OEM envia a informação do modelo (nome, descrição, hash do WoT TD).
3. O OEM apresenta prova da sua Enrollment VC (protocolo Present Proof v2).
4. O Consórcio valida a prova.
5. O Consórcio invoca `RegisterDeviceModel(modelID, manufacturer, wotTDHash)` no chaincode Fabric.
6. O WoT TD fica armazenado (hash no Fabric; ficheiro completo opcionalmente no IPFS).

**Endpoint:** `POST /uc/register-model`

**Payload:**
```json
{
  "model_id": "smartwatch-v1",
  "manufacturer": "SmartWatch Corp",
  "wot_td_hash": "sha256:td-smartwatch-v1"
}
```

**Código:** [services/egw-controller/src/egw_controller/use_cases/uc2_model_registration.py](../services/egw-controller/src/egw_controller/use_cases/uc2_model_registration.py)

---

### UC3 — Device Self-Registration

**O que é:** quando um dispositivo físico sai da linha de produção (ou um EGW arranca pela primeira vez), ele auto-regista-se no ecossistema.

**Atores:** EGW (1@egw) *ou* SD (1@sd), OEM (1@O).

**Fluxo narrativo (EGW):**
1. EGW arranca pela primeira vez → gera um DID público.
2. EGW conecta-se ao OEM via DIDComm OOB.
3. OEM verifica que o EGW é genuíno e emite-lhe uma Genesis VC.
4. OEM chama `ManufactureDevice(...)` no Fabric → estado **Manufactured**.
5. OEM chama `MakeAvailable(deviceID)` → estado **Available**.

**Fluxo narrativo (SD):** idêntico, com a diferença de que o SD usa o EGW como relay DIDComm (o SD tem menos recursos).

**Endpoint:** `POST /uc/register-device`

**Payload:**
```json
{
  "device_id": "sd-demo-001",
  "model_id": "smartwatch-v1",
  "device_type": "SmartDevice",
  "manufacturer_did": "did:sov:oem-smartwatch-001"
}
```

**Código:** [services/egw-controller/src/egw_controller/use_cases/uc3_device_registration.py](../services/egw-controller/src/egw_controller/use_cases/uc3_device_registration.py)

---

### UC4 — Consumer Buys Device

**O que é:** um consumidor compra um dispositivo. A compra transfere a posse: o OEM emite ao consumidor uma Ownership VC e marca o dispositivo como "In-Transit".

**Atores:** Consumidor (1@A), OEM (1@O).

**Fluxo narrativo:**
1. Consumidor navega o catálogo e escolhe um dispositivo em **Available**.
2. Consumidor conecta-se ao OEM via OOB (goal code `c2dta.consortium.buydevice`).
3. OEM propõe a Ownership VC ao consumidor.
4. Pagamento processado (fora do âmbito do paper).
5. OEM emite a Ownership VC.
6. OEM chama `InitiateTransit(deviceID, buyerDID)` → estado **In-Transit**.

**Endpoint:** `POST /uc/purchase`

**Payload:**
```json
{
  "device_id": "sd-demo-001",
  "buyer_did": "did:sov:consumer-alice"
}
```

**Código:** [services/egw-controller/src/egw_controller/use_cases/uc4_device_purchase.py](../services/egw-controller/src/egw_controller/use_cases/uc4_device_purchase.py)

---

### UC5 — Device Claiming

**O que é:** o consumidor recebe fisicamente o dispositivo em casa e "reivindica-o" — liga-o à sua identidade digital.

**Atores:** Consumidor (1@A), EGW (1@egw).

**Fluxo narrativo:**
1. Consumidor tira o dispositivo da caixa, faz scan de um QR code (OOB invite) embutido no SD/EGW.
2. Agente do consumidor conecta-se ao agente do EGW via DIDComm.
3. Consumidor apresenta prova da Ownership VC (Present Proof v2).
4. EGW valida:
   - Genesis VC (dispositivo é autêntico).
   - Ownership VC (consumidor é o dono).
   - Estado do dispositivo no Fabric = `In-Transit`.
5. EGW chama `ClaimDevice(deviceID, controllerDID, ownershipVCHash)` → estado **Claimed**.

**Endpoint:** `POST /uc/claim`

**Payload:**
```json
{
  "device_id": "sd-demo-001",
  "controller_did": "did:sov:consumer-alice",
  "ownership_vc_hash": "sha256:ownership-alice-001"
}
```

**Código:** [services/egw-controller/src/egw_controller/use_cases/uc5_device_claiming.py](../services/egw-controller/src/egw_controller/use_cases/uc5_device_claiming.py)

---

### UC6 — SD Twinning

**O que é:** ativa-se o Digital Twin. O dispositivo começa a enviar telemetria em tempo real para o Ditto, que passa a ter sempre o "retrato" atualizado.

**Atores:** EGW Controller (automatizado), Eclipse Ditto, Mosquitto, IPFS, Fabric.

**Fluxo narrativo:**
1. EGW Controller recebe pedido de twinning.
2. Cria o thing no Ditto com ID `org.c2dta:<device_uuid>` e as features (heartbeat, geolocation, timestamp).
3. Configura a connection MQTT no Ditto (source `egw/+/telemetry`, payload mapper JavaScript que mapeia JSON para features).
4. SD começa a publicar telemetria a 1 Hz.
5. Ditto recebe e atualiza o thing.
6. EGW Controller começa um loop de snapshots periódicos (default 86400 s):
   - `GET /api/2/things/<id>/features` → Ditto
   - `POST /api/v0/add?pin=true` → IPFS → CID
   - `RegisterDataset(...)` no chaincode `dataset-tracking`
7. EGW chama `TwinDevice(deviceID, dittoThingID)` → estado **Twinned**.

**Endpoint:** `POST /uc/twin`

**Payload:**
```json
{
  "device_id": "sd-demo-001"
}
```

**Código:** [services/egw-controller/src/egw_controller/use_cases/uc6_device_twinning.py](../services/egw-controller/src/egw_controller/use_cases/uc6_device_twinning.py)

---

### UC7 — SD Untwinning

**O que é:** desativa graciosamente o Digital Twin, preservando o histórico. Útil para poupança de energia, manutenção, ou preparação para venda.

**Atores:** EGW Controller, Eclipse Ditto, IPFS, Fabric.

**Fluxo narrativo:**
1. EGW recebe pedido de untwin.
2. Para o streaming MQTT (unsubscribe do tópico).
3. Tira snapshot final → envia ao IPFS → regista CID no Fabric.
4. Apaga o thing do Ditto: `DELETE /api/2/things/<id>`.
5. Chama `UntwinDevice(deviceID)` → estado volta a **Claimed**.

**Endpoint:** `POST /uc/untwin`

**Payload:**
```json
{
  "device_id": "sd-demo-001"
}
```

**Código:** [services/egw-controller/src/egw_controller/use_cases/uc7_device_untwinning.py](../services/egw-controller/src/egw_controller/use_cases/uc7_device_untwinning.py)

---

### UC8 — SD Selling (revenda)

**O que é:** o consumidor atual vende o dispositivo a um novo consumidor, transferindo também os datasets históricos.

**Atores:** Consumidor A (vendedor, 1@A), Consumidor B (comprador, 1@B), EGW Controller, OEM.

**Fluxo narrativo:**
1. Se o dispositivo está **Twinned**, executa-se primeiro UC7 (untwin).
2. OEM revoga a Ownership VC do vendedor (publicado na rede Indy).
3. OEM emite nova Ownership VC ao comprador (similar ao UC4).
4. `TransferDatasetOwnership(...)` no chaincode `dataset-tracking` → todos os CIDs históricos ficam associados ao novo dono.
5. `InitiateTransit(deviceID, buyerDID)` → estado **In-Transit**.
6. O novo consumidor executa UC5 (claiming) quando receber o dispositivo.

**Endpoint:** `POST /uc/sell`

**Payload:**
```json
{
  "device_id": "sd-demo-001",
  "buyer_did": "did:sov:consumer-bob"
}
```

**Código:** [services/egw-controller/src/egw_controller/use_cases/uc8_device_selling.py](../services/egw-controller/src/egw_controller/use_cases/uc8_device_selling.py)

---

## 8. API REST do EGW Controller

### Endpoints principais

Base URL: `http://localhost:8090`
Documentação Swagger interativa: `http://localhost:8090/docs`
Documentação ReDoc: `http://localhost:8090/redoc`

| Método | Endpoint | UC | Descrição |
|---|---|---|---|
| POST | `/uc/enrollment` | UC1 | Inscrever novo OEM no consórcio |
| POST | `/uc/register-model` | UC2 | Registar modelo de dispositivo no Fabric |
| POST | `/uc/register-device` | UC3 | Auto-registo de dispositivo (Manufactured → Available) |
| POST | `/uc/purchase` | UC4 | Compra: emite Ownership VC + InitiateTransit |
| POST | `/uc/claim` | UC5 | Reivindicação: ClaimDevice |
| POST | `/uc/twin` | UC6 | Ativar Digital Twin |
| POST | `/uc/untwin` | UC7 | Desativar Digital Twin |
| POST | `/uc/sell` | UC8 | Revenda a novo consumidor |
| GET | `/devices/{device_id}` | — | Consultar estado de um dispositivo |
| GET | `/devices?state=<estado>` | — | Listar dispositivos por estado |
| GET | `/devices?owner=<did>` | — | Listar dispositivos por dono |
| GET | `/transactions` | — | Listar todas as transações com passos |
| GET | `/health` | — | Health check |

### Resposta padronizada

Todos os endpoints de use case devolvem um `UCResponse`:

```json
{
  "success": true,
  "use_case": "UC6",
  "device_id": "sd-demo-001",
  "message": "Dispositivo sd-demo-001 twinned (thing=org.c2dta:sd-demo-001)",
  "data": {
    "transaction_id": "3f2b1a8e-...",
    "thing_id": "org.c2dta:sd-demo-001"
  }
}
```

### Transações multi-passo

Cada UC é executado como uma transação. Pode inspecionar o progresso:

```bash
curl http://localhost:8090/transactions | jq
```

Exemplo de saída:
```json
[
  {
    "transaction_id": "3f2b1a8e-...",
    "use_case": "UC6-Twinning",
    "device_id": "sd-demo-001",
    "status": "completed",
    "steps": [
      {"step_id": "ditto",  "status": "completed", "description": "Criar Digital Twin no Ditto"},
      {"step_id": "mqtt",   "status": "completed", "description": "Configurar streaming MQTT"},
      {"step_id": "ledger", "status": "completed", "description": "Transicionar para Twinned no ledger"}
    ]
  }
]
```

---

## 9. Como instalar e correr (do zero)

### 9.1 Pré-requisitos

| Software | Versão mínima | Finalidade |
|---|---|---|
| Docker | 24.0+ | Correr os containers |
| Docker Compose | v2 | Orquestrar o stack |
| Python | 3.12+ | Correr scripts clientes e testes |
| Go | 1.21+ | *Opcional* — desenvolvimento de chaincode |
| Git | 2.30+ | Clonar repo |
| OpenSSL | 1.1+ | Gerar certificados TLS |
| `curl` | — | Testar endpoints REST |
| `jq` | — | *Opcional* — formatar JSON |

**Recursos recomendados para a máquina de desenvolvimento:**
- CPU: 4 cores ou mais
- RAM: 8 GB (mínimo 4 GB)
- Disco: 20 GB livres

### 9.2 Instalação passo a passo

#### Windows (com WSL2)

1. **Instalar WSL2 e Ubuntu** (se ainda não tiver):
   ```powershell
   wsl --install -d Ubuntu-22.04
   ```

2. **Instalar Docker Desktop** (com integração WSL2 ativada).

3. **Abrir um terminal Ubuntu** e continuar com os passos Linux/macOS.

#### Linux / macOS

1. **Clonar o repositório:**
   ```bash
   git clone <url-do-repo> EdgeGateway
   cd EdgeGateway
   ```

2. **Gerar certificados TLS para o Mosquitto:**
   ```bash
   cd services/mosquitto/certs
   bash generate-certs.sh
   cd ../../..
   ```
   Este script cria uma CA local, um certificado de servidor para o broker, e certificados de cliente para o Edge Gateway e o Smart Device.

3. **Arrancar todo o stack:**
   ```bash
   docker compose up -d
   ```
   Na primeira vez pode demorar 5-15 minutos (download de ~6 GB de imagens).

4. **Verificar que tudo está saudável:**
   ```bash
   docker compose ps
   ```
   Deve ver todos os containers com status `running` ou `healthy`. Se algum estiver `unhealthy`, ver a secção 14 (Troubleshooting).

5. **Health check do EGW Controller:**
   ```bash
   curl http://localhost:8090/health
   # Esperado: {"status":"ok","service":"egw-controller"}
   ```

6. **Abrir a documentação OpenAPI interativa:**
   Abrir no browser: `http://localhost:8090/docs`

### 9.3 Correr a demo completa (UC1 → UC8)

A demo executa sequencialmente todos os 8 use cases, mostrando o payload e a resposta de cada um.

```bash
# Opção 1 — usar o Python local (precisa httpx instalado)
pip install httpx
python services/egw-controller/examples/run_full_lifecycle.py

# Opção 2 — correr dentro do container
docker compose exec egw-controller python examples/run_full_lifecycle.py
```

Saída esperada (resumida):
```
EGW Controller: http://localhost:8090
Health: {'status': 'ok', 'service': 'egw-controller'}

============================================================
  UC1 — OEM Enrollment
============================================================
POST /uc/enrollment
Payload: {
  "organization_name": "SmartWatch Corp",
  "organization_did": "did:sov:oem-smartwatch-001"
}
Resultado: [OK] OEM SmartWatch Corp inscrito no consorcio
...

Demo concluida — 8 transacoes executadas.
```

### 9.4 Inspecionar os serviços em execução

**Ver logs em tempo real de um serviço:**
```bash
docker compose logs -f egw-controller
docker compose logs -f mosquitto
docker compose logs -f ditto-gateway
```

**Entrar num container:**
```bash
docker compose exec egw-controller bash
docker compose exec fabric-cli bash
```

**Consultar o estado do Ditto:**
```bash
curl -u ditto:c2dta http://localhost:8080/api/2/things/org.c2dta:sd-demo-001
```

**Consultar um dispositivo no Fabric:**
```bash
curl http://localhost:8090/devices/sd-demo-001
```

**Explorar o Indy pool:**
Abrir no browser: `http://localhost:9000`

### 9.5 Parar e limpar

**Parar sem apagar dados:**
```bash
docker compose stop
```

**Parar e remover containers (preserva volumes):**
```bash
docker compose down
```

**Remover tudo (containers + volumes):**
```bash
docker compose down -v
```

**Limpeza completa (apaga também imagens construídas localmente):**
```bash
docker compose down -v --rmi local
```

---

## 10. Como testar

### 10.1 Testes unitários Python

**EGW Controller (24 testes):**
```bash
cd services/egw-controller
pip install -e ".[dev]"
pytest tests/ -v
```

Os testes cobrem:
- `test_transaction.py` — TransactionManager (criação, passos, estados).
- `test_uc1_enrollment.py` até `test_uc8_device_selling.py` — um ficheiro por UC, a mockar os clientes externos.

**Smart Device Simulator:**
```bash
cd services/smart-device-simulator
pip install -e ".[dev]"
pytest tests/ -v
```

Cobre a geração de batimentos (passeio aleatório), deriva GPS, e o cliente MQTT TLS.

**DIDComm Agent:**
```bash
cd services/didcomm-agent
pip install -e ".[dev]"
pytest tests/ -v
```

Cobre a criptografia (X25519 + HKDF + ChaCha20-Poly1305) e os endpoints REST.

### 10.2 Validação do chaincode Go

```bash
cd services/fabric/chaincode/device-lifecycle
go vet ./...
go test ./...

cd ../dataset-tracking
go vet ./...
go test ./...
```

### 10.3 Testes de integração

**Ditto API:**
```bash
cd services/ditto/tests
pytest test_ditto_api.py -v
```

**IPFS storage:**
```bash
cd services/ipfs/tests
pytest -v
```

**MQTT connectivity:**
```bash
cd services/mosquitto/tests
pytest -v
```

### 10.4 CI automatizado

O workflow [.github/workflows/ci.yml](../.github/workflows/ci.yml) corre em cada push e PR:
1. **lint** — `ruff check services/`
2. **test-sd-simulator** — pytest
3. **test-egw-controller** — pytest (24 testes)
4. **test-didcomm-agent** — pytest
5. **test-chaincode** — `go vet` nos dois chaincodes
6. **docker-build** (depende dos anteriores) — constrói 3 imagens Docker

O workflow [.github/workflows/build-yocto.yml](../.github/workflows/build-yocto.yml) corre a build da imagem Yocto (self-hosted runner necessário, pois a toolchain é pesada).

---

## 11. Mapa completo de portas

Lista de todas as portas expostas no host, ordenadas numericamente.

| Porta | Protocolo | Serviço | Descrição |
|---|---|---|---|
| 4001 | TCP/UDP | IPFS | Swarm P2P (ligação entre nós IPFS) |
| 5001 | HTTP | IPFS | API Kubo (add, cat, pin) |
| 7050 | gRPC | Fabric | Orderer (Raft) |
| 7051 | gRPC | Fabric | Peer ConsortiumOrg |
| 7053 | gRPC | Fabric | Orderer Admin |
| 7054 | HTTP | Fabric | CA Consortium |
| 8000 | HTTP | DIDComm Agent | API REST DIDComm 2.0 MVP |
| 8020 | HTTP | ACA-Py Consortium | Endpoint HTTP (para convites, webhooks) |
| 8021 | HTTP | ACA-Py Consortium | Admin API |
| 8030 | HTTP | ACA-Py OEM | Endpoint HTTP |
| 8031 | HTTP | ACA-Py OEM | Admin API |
| 8040 | HTTP | ACA-Py Consumer A | Endpoint HTTP |
| 8041 | HTTP | ACA-Py Consumer A | Admin API |
| 8054 | HTTP | Fabric | CA OEM |
| 8060 | HTTP | ACA-Py EGW | Endpoint HTTP |
| 8061 | HTTP | ACA-Py EGW | Admin API |
| 8070 | HTTP | ACA-Py Smart Device | Endpoint HTTP |
| 8071 | HTTP | ACA-Py Smart Device | Admin API |
| 8080 | HTTP | Ditto (via nginx) | API REST Digital Twin (Basic auth: ditto/c2dta) |
| 8081 | HTTP | IPFS | Gateway HTTP público |
| 8090 | HTTP | EGW Controller | API principal (FastAPI) |
| 8883 | MQTT/TLS | Mosquitto | MQTT broker (mTLS obrigatório) |
| 9000 | HTTP | Indy | Web UI / genesis file explorer |
| 9051 | gRPC | Fabric | Peer OEMOrg |
| 9701-9708 | TCP | Indy | Nós do pool von-network |

Se alguma destas portas colidir com outro serviço na sua máquina, edite o [docker-compose.yml](../docker-compose.yml) e altere o `ports:` — por exemplo, `"18090:8090"` para mapear a API do EGW Controller para a porta 18090 do host.

---

## 12. Verificação código-vs-paper (auditoria de conformidade)

### Nota de transparência

O ficheiro `uni/paper/EdgeGateway_Paper.pdf` está **protegido por palavra-passe**, pelo que não foi possível ler diretamente o texto do paper para confrontar linha a linha com o código. Esta verificação baseia-se:

1. Nos **documentos derivados** incluídos no repositório — [docs/architecture/](architecture/) (11 documentos) e [docs/paper/edgegateway-paper-summary.md](paper/edgegateway-paper-summary.md) — que foram escritos a partir do paper e replicam a sua arquitetura.
2. Nas **referências diretas ao paper** presentes no código — por exemplo, `uc1_oem_enrollment.py` diz `"paper Seccao 3.2.1"`, `device_lifecycle.go` diz `"Seccao 3.1"`, etc.
3. No [milestone-plan.md](roadmaps/milestone-plan.md) que marca as 7 fases de implementação como completas.

Para uma auditoria ainda mais rigorosa (linha a linha do paper), será necessário abrir o PDF sem palavra-passe e repetir o exercício.

### Tabela de conformidade

Legenda: **OK** = implementado, **Parcial** = implementado com limitações conhecidas, **Em falta** = não encontrado.

#### Casos de uso (Secção 3.2 do paper)

| Requisito | Ficheiro que o implementa | Estado | Notas |
|---|---|---|---|
| UC1 — OEM Enrollment | [uc1_oem_enrollment.py](../services/egw-controller/src/egw_controller/use_cases/uc1_oem_enrollment.py) | OK | Goal code `c2dta.consortium.enroll.OEM`, emissão Enrollment VC, transação com 3 passos (oob, connect, vc) |
| UC2 — Model Registration | [uc2_model_registration.py](../services/egw-controller/src/egw_controller/use_cases/uc2_model_registration.py) | OK | Invoca `RegisterDeviceModel` no chaincode |
| UC3 — Device Self-Registration | [uc3_device_registration.py](../services/egw-controller/src/egw_controller/use_cases/uc3_device_registration.py) | OK | `ManufactureDevice` + `MakeAvailable`, Genesis VC emitida |
| UC4 — Consumer Buys Device | [uc4_device_purchase.py](../services/egw-controller/src/egw_controller/use_cases/uc4_device_purchase.py) | OK | `InitiateTransit` + Ownership VC |
| UC5 — Device Claiming | [uc5_device_claiming.py](../services/egw-controller/src/egw_controller/use_cases/uc5_device_claiming.py) | OK | Present Proof v2 da Ownership VC + `ClaimDevice` |
| UC6 — SD Twinning | [uc6_device_twinning.py](../services/egw-controller/src/egw_controller/use_cases/uc6_device_twinning.py) | OK | Cria thing no Ditto, configura MQTT, `TwinDevice` |
| UC7 — SD Untwinning | [uc7_device_untwinning.py](../services/egw-controller/src/egw_controller/use_cases/uc7_device_untwinning.py) | OK | Snapshot final + delete thing + `UntwinDevice` |
| UC8 — SD Selling | [uc8_device_selling.py](../services/egw-controller/src/egw_controller/use_cases/uc8_device_selling.py) | OK | Revoga Ownership VC, emite nova, `TransferDatasetOwnership`, `InitiateTransit` |

#### Máquina de estados (Secção 3.1 do paper)

| Estado / transição | Implementação | Estado | Notas |
|---|---|---|---|
| 6 estados: Manufactured, Available, In-Transit, Claimed, Twinned, Decommissioned | [device_lifecycle.go L17-26](../services/fabric/chaincode/device-lifecycle/device_lifecycle.go) | OK | Constantes alinhadas com [models.py L16-24](../services/egw-controller/src/egw_controller/models.py) |
| Transições (ManufactureDevice, MakeAvailable, InitiateTransit, ClaimDevice, TwinDevice, UntwinDevice, DecommissionDevice) | [device_lifecycle.go](../services/fabric/chaincode/device-lifecycle/device_lifecycle.go) | OK | Todas presentes |
| Rich queries (por estado, por dono) | `QueryDevicesByState`, `QueryDevicesByOwner` em device_lifecycle.go + CouchDB indexes | OK | Usam CouchDB para queries ricas |
| Dataset tracking (CIDs IPFS no ledger) | [chaincode/dataset-tracking/](../services/fabric/chaincode/dataset-tracking/) | OK | `RegisterDataset`, `QueryDatasetsByDevice`, `TransferDatasetOwnership` |

#### Schemas VC (Secção 3.3 do paper)

| Schema | Localização | Estado | Notas |
|---|---|---|---|
| Enrollment VC | [services/indy/schemas/enrollment_vc.json](../services/indy/schemas/enrollment_vc.json) | OK | 6 atributos documentados |
| Genesis VC | [services/indy/schemas/genesis_vc.json](../services/indy/schemas/genesis_vc.json) | OK | 7 atributos (device_uuid, model_id, manufacturer_did, manufacture_date, firmware_version, wot_td_hash, serial_number) |
| Ownership VC | [services/indy/schemas/ownership_vc.json](../services/indy/schemas/ownership_vc.json) | OK | 5 atributos (device_uuid, owner_did, acquisition_date, previous_owner_did, transfer_tx_hash) |

#### 5 agentes ACA-Py

| Agente | DID notação | Portas | Estado |
|---|---|---|---|
| Consórcio | 1@C | 8020 / 8021 | OK |
| OEM | 1@O | 8030 / 8031 | OK |
| Consumer A | 1@A | 8040 / 8041 | OK |
| EGW | 1@egw | 8060 / 8061 | OK |
| Smart Device | 1@sd | 8070 / 8071 | OK |

Definições e plugins em [services/aca-py/](../services/aca-py/) e [services/aca-py/plugins/c2dta_protocols/](../services/aca-py/plugins/c2dta_protocols/).

#### 8 goal codes

| Goal code | UC | Estado |
|---|---|---|
| `c2dta.consortium.enroll.OEM` | UC1 | OK (uc1_oem_enrollment.py L37) |
| `c2dta.consortium.registermodel` | UC2 | OK |
| `c2dta.consortium.registerdevice` | UC3 | OK |
| `c2dta.consortium.buydevice` | UC4 | OK |
| `c2dta.consortium.claim` | UC5 | OK |
| `c2dta.egw.twin` | UC6 | OK |
| `c2dta.egw.untwin` | UC7 | OK |
| `c2dta.egw.sell` | UC8 | OK |

Todas definidas em [goal_codes.py](../services/aca-py/plugins/c2dta_protocols/goal_codes.py).

#### MQTT (Secção sobre arquitetura IoT)

| Requisito | Implementação | Estado |
|---|---|---|
| Broker Mosquitto 2.0 com TLS 1.2+ | [docker-compose.yml](../docker-compose.yml) L22-40 | OK |
| Tópicos `egw/<uuid>/telemetry` / `/command` / `/status` | [docs/architecture/mqtt-architecture.md](architecture/mqtt-architecture.md) + ACLs | OK |
| mTLS (certificado do cliente obrigatório) | [services/mosquitto/certs/generate-certs.sh](../services/mosquitto/certs/generate-certs.sh) + mosquitto.conf | OK |
| QoS 1 para telemetria | Cliente paho-mqtt no simulator | OK |
| ACL por tópico | [services/mosquitto/config/acl.conf](../services/mosquitto/config/acl.conf) | OK |
| Persistência de mensagens | Volume `mosquitto-data` no compose | OK |

#### Digital Twin (Eclipse Ditto)

| Requisito | Implementação | Estado |
|---|---|---|
| Ditto 3.5.6 com MongoDB | [docker-compose.yml](../docker-compose.yml) (7 containers Ditto) | OK |
| Thing ID pattern `org.c2dta:<uuid>` | uc6_device_twinning.py L34 | OK |
| Features heartbeat + geolocation + timestamp | uc6_device_twinning.py L39-43 + smartwatch-td.jsonld | OK |
| WoT TD v1.1 | [services/ditto/wot/smartwatch-td.jsonld](../services/ditto/wot/smartwatch-td.jsonld) | OK |
| Conectividade MQTT com payload mapper | [services/ditto/connectivity/mqtt-connection.json](../services/ditto/connectivity/mqtt-connection.json) | OK |
| Autenticação nginx Basic | [services/ditto/nginx/nginx.conf](../services/ditto/nginx/nginx.conf) + htpasswd | OK |

#### IPFS

| Requisito | Implementação | Estado |
|---|---|---|
| IPFS Kubo 0.28.0 | docker-compose.yml | OK |
| Snapshots periódicos DT → IPFS | EGW Controller (`EGW_DATASET_INTERVAL_S`, default 86400s) | OK |
| CID registado no Fabric | Chaincode `dataset-tracking`.`RegisterDataset` | OK |
| Pinning automático | `IPFSClient.add_json` com parâmetro pin | OK |
| Formato JSON snapshot (device_id, thing_id, snapshot_time, features) | docs/architecture/ipfs-architecture.md | OK |

#### Yocto / Edge deployment

| Requisito | Implementação | Estado |
|---|---|---|
| Camada `meta-edgegateway` | [yocto/layers/meta-edgegateway/](../yocto/layers/meta-edgegateway/) | OK |
| Recipe de imagem | `yocto/layers/meta-edgegateway/recipes-core/images/edgegateway-image.bb` | OK |
| Script de bootstrap | [scripts/setup-env.sh](../scripts/setup-env.sh) | OK |
| Workflow CI de build Yocto | [.github/workflows/build-yocto.yml](../.github/workflows/build-yocto.yml) | OK |
| Suporte a container runtime (Docker/Podman) | Documentado em docs/architecture/system-architecture.md; recipes a completar | Parcial |
| OTA updates (swupdate/Mender) | Documentado; integração específica ainda não implementada | Parcial |

#### DIDComm 2.0

| Requisito | Implementação | Estado |
|---|---|---|
| Agente DIDComm 2.0 | [services/didcomm-agent/](../services/didcomm-agent/) | OK (MVP) |
| X25519 + HKDF + ChaCha20-Poly1305 | [crypto.py](../services/didcomm-agent/src/didcomm_agent/crypto.py) | OK |
| API REST para send/receive | [api.py](../services/didcomm-agent/src/didcomm_agent/api.py) | OK |
| Persistência de DIDs | SQLite opcional (DIDCOMM_DB_PATH) | Parcial (MVP: chaves voláteis por omissão) |
| Offline queue, attachments, revogação | Não implementado (explicitamente fora de âmbito do MVP) | Em falta |
| Integração com TPM/HSM | Documentado em didcomm-architecture.md como trabalho futuro | Em falta |

#### CI/CD

| Requisito | Implementação | Estado |
|---|---|---|
| Lint (ruff) | `ci.yml` job `lint` | OK |
| Testes unitários Python | 3 jobs (sd-simulator, egw-controller, didcomm-agent) | OK |
| `go vet` para chaincodes | `ci.yml` job `test-chaincode` | OK |
| Build de imagens Docker | `ci.yml` job `docker-build` | OK |
| Build Yocto | [.github/workflows/build-yocto.yml](../.github/workflows/build-yocto.yml) | OK |

### Resumo

| Categoria | Implementado / Total |
|---|---|
| Use cases | 8 / 8 (OK) |
| Estados Fabric | 6 / 6 (OK) |
| Transições Fabric | 7 / 7 (OK) |
| Schemas VC | 3 / 3 (OK) |
| Agentes ACA-Py | 5 / 5 (OK) |
| Goal codes | 8 / 8 (OK) |
| Chaincodes | 2 / 2 (OK) |
| Serviços infraestrutura | 9 / 9 (OK) |
| Testes unitários | 24+ testes (OK) |
| CI workflows | 2 / 2 (OK) |

**Conclusão:** baseado nos documentos internos e no próprio código, **a implementação está em conformidade com a arquitetura descrita no paper**. As áreas marcadas como **Parcial** (Yocto OTA, DIDComm MVP, integração HSM) são explicitamente identificadas no próprio repositório como trabalho futuro — consistentes com o estatuto de "implementação de referência" e não com defeitos de conformidade.

### Recomendação

Para elevar a verificação acima a "total" (linha a linha do paper), é necessário:

1. Abrir o PDF `uni/paper/EdgeGateway_Paper.pdf` numa versão sem palavra-passe.
2. Confrontar cada Secção 3.X do paper com os ficheiros aqui referenciados.
3. Confirmar que a numeração dos atributos das VCs, os goal codes, e as transições Fabric correspondem exatamente ao texto publicado.

---

## 13. Deployment em edge (Yocto Linux)

O objetivo final é produzir uma **imagem Linux minimalista** que corra num Raspberry Pi, Intel NUC, ou placa industrial, com todos os serviços do C2DTA pré-instalados e pré-configurados.

### 13.1 Pré-requisitos para build Yocto

- Linux (Ubuntu 22.04 recomendado) ou WSL2
- 100 GB de espaço em disco livre
- 16 GB de RAM (8 GB mínimo, mais lento)
- Pacotes Yocto (`build-essential`, `chrpath`, `diffstat`, `gawk`, `texinfo`, `wget`, etc.)

### 13.2 Preparar os layers

O repositório **não inclui** o `poky` (é submódulo). Adicione-o:

```bash
git submodule add git://git.yoctoproject.org/poky yocto/poky
```

Para uma placa específica (ex.: Raspberry Pi 4), adicione o BSP correspondente:

```bash
git submodule add git://git.yoctoproject.org/meta-raspberrypi yocto/layers/meta-raspberrypi
```

### 13.3 Inicializar o ambiente de build

```bash
source scripts/setup-env.sh
```

Isto faz `source oe-init-build-env` do poky e posiciona-o em `yocto/build/`.

### 13.4 Configurar os layers e a máquina alvo

Edite `yocto/build/conf/bblayers.conf` para incluir:
```
BBLAYERS ?= " \
  ${TOPDIR}/../poky/meta \
  ${TOPDIR}/../poky/meta-poky \
  ${TOPDIR}/../layers/meta-raspberrypi \
  ${TOPDIR}/../layers/meta-edgegateway \
"
```

Edite `yocto/build/conf/local.conf` para definir a máquina alvo:
```
MACHINE ?= "raspberrypi4-64"
```

### 13.5 Construir a imagem

```bash
bitbake edgegateway-image
```

A primeira build demora 1-4 horas conforme a máquina. O resultado fica em `yocto/build/tmp/deploy/images/<MACHINE>/`.

### 13.6 Gravar a imagem no cartão SD

```bash
sudo dd if=yocto/build/tmp/deploy/images/raspberrypi4-64/edgegateway-image-raspberrypi4-64.wic.bz2 \
       of=/dev/sdX bs=4M status=progress
```

**Atenção:** substitua `/dev/sdX` pelo nome correto do cartão (`lsblk` para confirmar). Um erro aqui apaga o seu disco principal.

### 13.7 Pacotes recomendados na imagem

A imagem deve incluir:
- Container runtime (Docker ou Podman) + OCI (runc/crun)
- Mosquitto broker
- Bibliotecas criptográficas (libsodium, OpenSSL)
- Runtimes de AI (TensorFlow Lite, ONNX Runtime — placeholders)
- Ferramentas de observabilidade (Node Exporter, Fluent Bit)
- Sistema de OTA (swupdate ou Mender) com atualização atómica A/B

Mais detalhe em [yocto/README.md](../yocto/README.md).

---

## 14. Resolução de problemas (troubleshooting)

### 14.1 "Port already in use" ao arrancar

**Sintoma:** `docker compose up` falha com "address already in use".

**Causa:** outra aplicação já está a usar uma das portas (ver secção 11).

**Resolução:**
1. Descobrir quem usa a porta:
   ```bash
   # Linux / macOS
   lsof -i :8090
   # Windows (PowerShell)
   netstat -ano | findstr :8090
   ```
2. Parar esse processo OU editar o [docker-compose.yml](../docker-compose.yml) e mudar o mapeamento, ex.: `"18090:8090"`.

### 14.2 Containers em estado "unhealthy"

**Sintoma:** `docker compose ps` mostra algum serviço como `unhealthy`.

**Resolução:**
1. Ver logs detalhados:
   ```bash
   docker compose logs <nome-serviço> --tail=100
   ```
2. Causas comuns:
   - **Mosquitto unhealthy:** certificados em falta em `services/mosquitto/certs/`. Correr `bash services/mosquitto/certs/generate-certs.sh`.
   - **Ditto unhealthy:** MongoDB ainda a arrancar. Esperar 30-60 s e verificar novamente.
   - **Fabric peers unhealthy:** orderer não arrancou primeiro. Reiniciar: `docker compose restart orderer.c2dta.example.com`.

### 14.3 `401 Unauthorized` ao chamar o Ditto

**Sintoma:** `curl http://localhost:8080/api/2/things/...` devolve 401.

**Causa:** falta autenticação Basic.

**Resolução:** incluir credenciais:
```bash
curl -u ditto:c2dta http://localhost:8080/api/2/things/...
```

### 14.4 UC6 falha no passo "ditto"

**Sintoma:** resposta com `"success": false` no passo `ditto`.

**Causa:** o Ditto ainda não está pronto ou há erro de policy.

**Resolução:**
1. Verificar se o thing pode ser criado manualmente:
   ```bash
   curl -u ditto:c2dta -X PUT http://localhost:8080/api/2/things/org.c2dta:teste \
     -H "Content-Type: application/json" \
     -d '{"features":{"heartbeat":{"properties":{"bpm":0}}}}'
   ```
2. Se falhar, consultar logs do `ditto-things` e `ditto-gateway`.

### 14.5 O simulador não consegue ligar ao Mosquitto

**Sintoma:** logs do `sd-simulator` mostram `SSL: CERTIFICATE_VERIFY_FAILED` ou `Connection refused`.

**Causa:** certificados em falta ou errados.

**Resolução:**
1. Regerar certificados:
   ```bash
   rm -rf services/mosquitto/certs/*.crt services/mosquitto/certs/*.key
   bash services/mosquitto/certs/generate-certs.sh
   ```
2. Reiniciar o stack: `docker compose restart mosquitto sd-simulator`.

### 14.6 `docker compose up` demora muito

**Normal na primeira vez:** download de ~6 GB de imagens. Correr em rede rápida se possível.

**Após a primeira vez:** se continuar lento, verificar se Docker Desktop tem recursos suficientes (Settings → Resources: pelo menos 4 CPU, 8 GB RAM).

### 14.7 Erro de DNS entre containers

**Sintoma:** um serviço não consegue resolver `mosquitto`, `ditto-gateway`, etc.

**Causa:** rede `c2dta-net` partida.

**Resolução:**
```bash
docker compose down
docker network prune
docker compose up -d
```

### 14.8 Testes Python falham com `ModuleNotFoundError`

**Causa:** pacote não instalado em modo dev.

**Resolução:**
```bash
cd services/<serviço>
pip install -e ".[dev]"
```

### 14.9 Apagar todo o estado e começar do zero

```bash
docker compose down -v --rmi local
rm -rf services/mosquitto/certs/*.crt services/mosquitto/certs/*.key
bash services/mosquitto/certs/generate-certs.sh
docker compose up -d
```

---

## 15. Glossário de termos

| Termo / Acrónimo | Definição |
|---|---|
| **ACA-Py** | Aries Cloud Agent Python — agente SSI que implementa os protocolos DIDComm/Aries. |
| **ACL** | Access Control List — regras de controlo de acesso (neste projeto, por tópico MQTT). |
| **Aries** | Conjunto de protocolos SSI (emissão VC, prova de posse, etc.) sob a OpenWallet Foundation. |
| **Basic Auth** | Esquema simples de autenticação HTTP com utilizador e palavra-passe. |
| **BSP** | Board Support Package — recipes Yocto específicos para uma placa de hardware. |
| **C2DTA** | Consumer-Controlled Digital Twin Architecture — a arquitetura proposta no paper. |
| **CA** | Certificate Authority — entidade que assina certificados X.509. |
| **Chaincode** | Smart contract no Hyperledger Fabric (escrito em Go, Java ou JavaScript). |
| **CID** | Content Identifier — hash criptográfico que identifica um ficheiro no IPFS. |
| **ChaCha20-Poly1305** | Algoritmo de encriptação autenticada usado em DIDComm 2.0. |
| **CouchDB** | Base de dados NoSQL; state database do Fabric para queries ricas. |
| **DID** | Decentralized Identifier — identificador digital descentralizado, criado pelo titular. |
| **DIDComm** | Protocolo de mensagens encriptadas ponto-a-ponto entre agentes SSI. |
| **DLT** | Distributed Ledger Technology — sinónimo de blockchain no sentido lato. |
| **DT** | Digital Twin — gémeo digital, representação sempre atualizada de um objeto físico. |
| **EGW** | Edge Gateway — o dispositivo físico que corre localmente os serviços C2DTA. |
| **Fabric** | Hyperledger Fabric — blockchain permissionada da Linux Foundation. |
| **FastAPI** | Framework Python para construir APIs REST de alta performance. |
| **GDPR** | General Data Protection Regulation — regulamento europeu de proteção de dados. |
| **HDKF** | HMAC-based Key Derivation Function — função para derivar chaves de sessão. |
| **HSM** | Hardware Security Module — módulo físico para guardar chaves criptográficas. |
| **Indy** | Hyperledger Indy — blockchain especializada em identidade (DIDs e VCs). |
| **IoT** | Internet of Things — objetos físicos ligados à Internet. |
| **IPFS** | InterPlanetary File System — sistema de ficheiros P2P endereçado por conteúdo. |
| **JSON-LD** | JSON for Linked Data — formato JSON com contexto semântico (usado no WoT TD). |
| **Kubo** | A implementação Go do IPFS, a mais usada. |
| **LGPD** | Lei Geral de Proteção de Dados — equivalente brasileiro do GDPR. |
| **MongoDB** | Base de dados NoSQL orientada a documentos; persistência do Ditto. |
| **MQTT** | Message Queuing Telemetry Transport — protocolo pub/sub leve para IoT. |
| **mTLS** | Mutual TLS — TLS em que ambos os lados apresentam certificado. |
| **OCI** | Open Container Initiative — padrão para runtimes de containers (runc, crun). |
| **OEM** | Original Equipment Manufacturer — fabricante do dispositivo. |
| **OOB** | Out-of-Band — protocolo DIDComm para iniciar conexões (p.ex. via QR code). |
| **OTA** | Over-The-Air — atualizações de software remotas. |
| **Pub/Sub** | Publish/Subscribe — modelo de mensagens onde produtores publicam em tópicos e consumidores subscrevem. |
| **QoS** | Quality of Service — nível de garantia de entrega em MQTT (0, 1, 2). |
| **Raft** | Algoritmo de consenso usado pelo orderer do Fabric. |
| **REST** | Representational State Transfer — estilo de API HTTP (GET, POST, PUT, DELETE). |
| **SD** | Smart Device — o dispositivo IoT (neste projeto, o smartwatch simulado). |
| **SSI** | Self-Sovereign Identity — identidade autossoberana. |
| **Steward** | Papel no Indy: nó com autoridade para escrever certos tipos de transações. |
| **TD** | Thing Description — descritor WoT do dispositivo. |
| **TLS** | Transport Layer Security — protocolo de cifragem de ligações (sucessor do SSL). |
| **TPM** | Trusted Platform Module — chip em hardware para guardar chaves de forma segura. |
| **UC** | Use Case — caso de uso (UC1 a UC8 neste projeto). |
| **UUID** | Universally Unique Identifier — identificador único de 128 bits. |
| **VC** | Verifiable Credential — credencial digital assinada criptograficamente. |
| **von-network** | Distribuição do Hyperledger Indy mantida pelo governo da Colúmbia Britânica. |
| **WoT** | Web of Things — padrão W3C para descrição de dispositivos IoT interoperáveis. |
| **X25519** | Algoritmo de acordo de chaves baseado em curvas elípticas (usado em DIDComm). |
| **Yocto** | Projeto para construir distribuições Linux customizadas para sistemas embebidos. |

---

## 16. Referências e leitura adicional

### Paper de referência
- Pinto, F., Ferreira da Silva, C., Moro, S., Aquino, P. (2025). *Consumer-Controlled Digital Twin Architecture: How blockchain technology gives consumers control over their smart devices' digital twins and data*. Blockchain: Research and Applications, Elsevier. DOI: [10.1016/j.bcra.2025.100342](https://doi.org/10.1016/j.bcra.2025.100342)

### Documentos internos do repositório
- [README.md](../README.md) — visão geral do projeto
- [docs/architecture/system-architecture.md](architecture/system-architecture.md) — arquitetura de alto nível
- [docs/architecture/mqtt-architecture.md](architecture/mqtt-architecture.md)
- [docs/architecture/ditto-architecture.md](architecture/ditto-architecture.md)
- [docs/architecture/fabric-architecture.md](architecture/fabric-architecture.md)
- [docs/architecture/indy-architecture.md](architecture/indy-architecture.md)
- [docs/architecture/ipfs-architecture.md](architecture/ipfs-architecture.md)
- [docs/architecture/egw-controller-architecture.md](architecture/egw-controller-architecture.md)
- [docs/architecture/didcomm-architecture.md](architecture/didcomm-architecture.md)
- [docs/architecture/use-case-flows.md](architecture/use-case-flows.md) — fluxos UC1–UC8 em PT
- [docs/architecture/communication-and-dataflow.md](architecture/communication-and-dataflow.md)
- [docs/paper/edgegateway-paper-summary.md](paper/edgegateway-paper-summary.md)
- [docs/research/blockchain-personal-ai-summary.md](research/blockchain-personal-ai-summary.md)
- [docs/roadmaps/milestone-plan.md](roadmaps/milestone-plan.md)

### Documentação externa (por tecnologia)
- **Eclipse Ditto:** https://www.eclipse.org/ditto/
- **Hyperledger Fabric:** https://hyperledger-fabric.readthedocs.io/
- **Hyperledger Indy:** https://hyperledger.github.io/indy-sdk/
- **ACA-Py:** https://github.com/openwallet-foundation/acapy
- **Eclipse Mosquitto:** https://mosquitto.org/documentation/
- **IPFS:** https://docs.ipfs.tech/
- **DIDComm 2.0:** https://identity.foundation/didcomm-messaging/spec/
- **W3C Web of Things:** https://www.w3.org/WoT/
- **W3C Verifiable Credentials:** https://www.w3.org/TR/vc-data-model/
- **W3C DIDs:** https://www.w3.org/TR/did-core/
- **Yocto Project:** https://docs.yoctoproject.org/
- **FastAPI:** https://fastapi.tiangolo.com/

### Termos de pesquisa úteis
Se quiser ir mais fundo em cada área:
- `"Consumer-Controlled Digital Twin" Pinto 2025`
- `"Aries RFC" credential issuance`
- `"Hyperledger Indy" "DID" "verifiable credential"`
- `"Eclipse Ditto" "Web of Things" MQTT`
- `"IPFS" "content-addressed storage" blockchain anchor`
- `"Yocto" "meta layer" embedded Linux`

---

## 17. Referência de funções por ficheiro

Esta secção documenta, **ficheiro a ficheiro**, todas as funções, métodos e classes do código-fonte do projeto. Está organizada por domínio lógico:

- **17.1** EGW Controller — núcleo (API, modelos, configuração, transações, clientes)
- **17.2** EGW Controller — Use Cases UC1 a UC8
- **17.3** Smart Device Simulator
- **17.4** Hyperledger Fabric — chaincodes Go
- **17.5** DIDComm Agent
- **17.6** ACA-Py — plugins de protocolo C2DTA

Cada ficheiro indica o seu caminho relativo ao repositório (clicável) e descreve a finalidade do módulo. Para cada função/método há uma explicação em 2-4 frases do que faz, que dependências usa, e (quando relevante) o estado que altera no ledger ou no Digital Twin.

---

### 17.1 EGW Controller — núcleo

#### [services/egw-controller/src/egw_controller/api.py](../services/egw-controller/src/egw_controller/api.py)

Módulo que define a API FastAPI do EGW Controller. Expõe endpoints REST que orquestram os oito use cases da arquitetura C2DTA e disponibiliza consultas sobre dispositivos e transações.

##### `lifespan(app: FastAPI)`
Context manager assíncrono que corre no arranque e encerramento da aplicação FastAPI. Carrega a configuração via `get_config()` e instancia os singletons `FabricClient`, `DittoClient`, `IPFSClient` e dois `AcaPyClient` (consórcio e OEM). Regista mensagens de arranque e de encerramento no logger.

##### `POST /uc/enrollment` — `enrollment(request: EnrollmentRequest) -> UCResponse`
Endpoint que executa o UC1 (OEM Enrollment no consórcio). Valida o corpo com `EnrollmentRequest` e delega em `uc1_oem_enrollment.execute`, injetando o cliente ACA-Py do consórcio e o `TransactionManager` partilhado.

##### `POST /uc/register-model` — `register_model(request: ModelRegistrationRequest) -> UCResponse`
Endpoint que executa o UC2 (Registo de modelo de dispositivo). Valida o corpo com `ModelRegistrationRequest` e delega em `uc2_model_registration.execute`, injetando o `FabricClient` e o `TransactionManager`.

##### `POST /uc/register-device` — `register_device(request: DeviceRegistrationRequest) -> UCResponse`
Endpoint que executa o UC3 (auto-registo de dispositivo). Valida o corpo com `DeviceRegistrationRequest` e delega em `uc3_device_registration.execute`, injetando o cliente ACA-Py do OEM, o `FabricClient` e o `TransactionManager`.

##### `POST /uc/purchase` — `purchase(request: PurchaseRequest) -> UCResponse`
Endpoint que executa o UC4 (Compra de dispositivo). Valida o corpo com `PurchaseRequest` e delega em `uc4_device_purchase.execute` com o `FabricClient` e o `TransactionManager`.

##### `POST /uc/claim` — `claim(request: ClaimRequest) -> UCResponse`
Endpoint que executa o UC5 (Reivindicação de dispositivo). Valida o corpo com `ClaimRequest` e delega em `uc5_device_claiming.execute` com o `FabricClient` e o `TransactionManager`.

##### `POST /uc/twin` — `twin(request: TwinRequest) -> UCResponse`
Endpoint que executa o UC6 (Twinning de smart device). Valida o corpo com `TwinRequest` e delega em `uc6_device_twinning.execute`, injetando o `DittoClient`, o `FabricClient` e o `TransactionManager`.

##### `POST /uc/untwin` — `untwin(request: UntwinRequest) -> UCResponse`
Endpoint que executa o UC7 (Untwinning de smart device). Valida o corpo com `UntwinRequest` e delega em `uc7_device_untwinning.execute`, injetando o `DittoClient`, o `FabricClient` e o `TransactionManager`.

##### `POST /uc/sell` — `sell(request: SellRequest) -> UCResponse`
Endpoint que executa o UC8 (Venda de smart device). Valida o corpo com `SellRequest` e delega em `uc8_device_selling.execute` com o `FabricClient` e o `TransactionManager`.

##### `GET /devices/{device_id}` — `get_device(device_id: str)`
Endpoint que consulta o estado de um dispositivo no ledger Fabric. Invoca `FabricClient.query_device` com o identificador recebido no path e devolve o resultado em bruto.

##### `GET /devices` — `list_devices(state: str | None = None, owner: str | None = None)`
Endpoint que lista dispositivos filtrando por estado ou por proprietário. Usa `QueryDevicesByState` ou `QueryDevicesByOwner` no chaincode de ciclo de vida consoante o query parameter; se nenhum for fornecido, devolve uma mensagem a indicar os filtros disponíveis.

##### `GET /transactions` — `list_transactions()`
Endpoint que lista todas as transações orquestradas pelo EGW Controller. Chama `TransactionManager.list_all` e serializa cada transação com o identificador, use case, dispositivo, estado, timestamp de criação e a sequência de passos.

##### `GET /health` — `health()`
Endpoint de health check. Devolve um dicionário com estado `ok` e o nome do serviço `egw-controller`.

---

#### [services/egw-controller/src/egw_controller/models.py](../services/egw-controller/src/egw_controller/models.py)

Módulo que define os modelos de domínio e os DTOs de pedido/resposta usados pela API. Traduz os conceitos centrais da arquitetura C2DTA descrita no paper para classes Pydantic e Enum.

##### `class DeviceState(str, Enum)`
Enumeração dos estados do ciclo de vida de um dispositivo (Secção 3.1 do paper).

- **`MANUFACTURED = "Manufactured"`** — dispositivo acabado de fabricar.
- **`AVAILABLE = "Available"`** — dispositivo disponível para venda.
- **`IN_TRANSIT = "In-Transit"`** — dispositivo em trânsito para o comprador.
- **`CLAIMED = "Claimed"`** — dispositivo reivindicado por um controlador.
- **`TWINNED = "Twinned"`** — dispositivo com Digital Twin ativo.
- **`DECOMMISSIONED = "Decommissioned"`** — dispositivo descomissionado.

##### `class DeviceType(str, Enum)`
Enumeração dos tipos de dispositivo suportados pelo C2DTA.

- **`EGW = "EdgeGateway"`** — Edge Gateway.
- **`SD = "SmartDevice"`** — Smart Device.

##### `class DeviceInfo(BaseModel)`
Modelo que representa a informação de um dispositivo no ecossistema.

- **`device_id: str`** — identificador único do dispositivo.
- **`model_id: str = ""`** — identificador do modelo.
- **`device_type: DeviceType`** — tipo de dispositivo (EGW ou SD).
- **`state: DeviceState = MANUFACTURED`** — estado atual no ciclo de vida.
- **`manufacturer_id: str = ""`** — identificador do fabricante.
- **`owner_did: str = ""`** — DID do proprietário.
- **`controller_did: str = ""`** — DID do controlador.
- **`ditto_thing_id: str = ""`** — identificador do thing correspondente no Ditto.
- **`genesis_vc_hash: str = ""`** — hash da VC genesis emitida pelo OEM.
- **`ownership_vc_hash: str = ""`** — hash da VC de propriedade.

##### `class DatasetInfo(BaseModel)`
Modelo que representa um snapshot de Digital Twin persistido no IPFS.

- **`dataset_id: str`** — identificador único do dataset.
- **`device_id: str`** — dispositivo de origem.
- **`ipfs_hash: str`** — CID IPFS onde o dataset está armazenado.
- **`owner_did: str`** — DID do proprietário dos dados.
- **`size_bytes: int = 0`** — tamanho em bytes.
- **`record_count: int = 0`** — número de registos.
- **`start_time: str = ""`** — timestamp inicial da janela temporal.
- **`end_time: str = ""`** — timestamp final da janela temporal.

##### `class EnrollmentRequest(BaseModel)`
Pedido de inscrição de um OEM no consórcio (UC1).

- **`organization_name: str`** — nome da organização.
- **`organization_did: str`** — DID da organização.

##### `class ModelRegistrationRequest(BaseModel)`
Pedido de registo de modelo de dispositivo (UC2).

- **`model_id: str`** — identificador do modelo.
- **`manufacturer: str`** — fabricante responsável.
- **`wot_td_hash: str`** — hash da Thing Description Web of Things.

##### `class DeviceRegistrationRequest(BaseModel)`
Pedido de auto-registo de dispositivo (UC3).

- **`device_id: str`** — identificador do dispositivo.
- **`model_id: str`** — identificador do modelo.
- **`device_type: DeviceType`** — tipo de dispositivo.
- **`manufacturer_did: str`** — DID do fabricante.

##### `class PurchaseRequest(BaseModel)`
Pedido de compra de dispositivo (UC4).

- **`device_id: str`** — identificador do dispositivo.
- **`buyer_did: str`** — DID do comprador.

##### `class ClaimRequest(BaseModel)`
Pedido de reivindicação de dispositivo (UC5).

- **`device_id: str`** — identificador do dispositivo.
- **`controller_did: str`** — DID do controlador que reivindica.
- **`ownership_vc_hash: str`** — hash da VC de propriedade.

##### `class TwinRequest(BaseModel)`
Pedido de twinning de smart device (UC6).

- **`device_id: str`** — identificador do dispositivo.
- **`twin_config: dict`** — configuração opcional do Digital Twin; inicializada por defeito como dicionário vazio.

##### `class UntwinRequest(BaseModel)`
Pedido de untwinning de smart device (UC7).

- **`device_id: str`** — identificador do dispositivo.

##### `class SellRequest(BaseModel)`
Pedido de venda de smart device (UC8).

- **`device_id: str`** — identificador do dispositivo.
- **`buyer_did: str`** — DID do novo comprador.
- **`sale_config: dict`** — configuração opcional da venda; inicializada por defeito como dicionário vazio.

##### `class UCResponse(BaseModel)`
Resposta genérica de qualquer endpoint de use case.

- **`success: bool`** — indica se a operação teve sucesso.
- **`use_case: str`** — nome do use case executado.
- **`device_id: str = ""`** — identificador do dispositivo afetado.
- **`message: str = ""`** — mensagem textual.
- **`data: Optional[dict] = None`** — dados adicionais devolvidos pelo use case.

---

#### [services/egw-controller/src/egw_controller/config.py](../services/egw-controller/src/egw_controller/config.py)

Módulo que concentra a leitura de configuração a partir de variáveis de ambiente. Disponibiliza defaults razoáveis para ambiente local de desenvolvimento.

##### `get_config() -> dict`
Lê variáveis de ambiente e devolve um dicionário com todos os parâmetros necessários ao EGW Controller. Cobre os URLs e credenciais do Ditto, parâmetros do broker MQTT, URL da API IPFS, endereços admin dos três agentes ACA-Py (consórcio, OEM, EGW), endpoint e canal do Fabric, URL do agente DIDComm, caminho opcional de base de dados e o intervalo (em segundos) de geração de datasets. Se uma variável não estiver definida, aplica o valor por defeito correspondente.

---

#### [services/egw-controller/src/egw_controller/transaction.py](../services/egw-controller/src/egw_controller/transaction.py)

Módulo que implementa o gestor de transações multi-step do EGW Controller. Materializa a key-pair table descrita na Secção 3.1 (Transaction Control) do paper, preservando o estado das operações que envolvem múltiplos agentes SSI.

##### `class StepStatus(str, Enum)`
Enumeração dos estados possíveis de um passo ou transação.

- **`PENDING = "pending"`** — passo ainda não iniciado.
- **`IN_PROGRESS = "in_progress"`** — passo em execução.
- **`COMPLETED = "completed"`** — passo concluído com sucesso.
- **`FAILED = "failed"`** — passo falhou.

##### `class TransactionStep`
Dataclass que representa um passo individual de uma transação.

- **`step_id: str`** — identificador do passo.
- **`description: str`** — descrição textual.
- **`status: StepStatus`** — estado atual, com valor inicial `PENDING`.
- **`result: Optional[dict]`** — resultado produzido pelo passo.
- **`error: Optional[str]`** — mensagem de erro, caso o passo falhe.
- **`started_at: Optional[str]`** — timestamp ISO-8601 de início.
- **`completed_at: Optional[str]`** — timestamp ISO-8601 de conclusão.

##### `class Transaction`
Dataclass que representa uma transação multi-step e o respetivo controlo de estado.

- **`transaction_id: str`** — UUID gerado automaticamente.
- **`use_case: str`** — nome do use case associado.
- **`device_id: str`** — dispositivo envolvido.
- **`steps: list[TransactionStep]`** — lista ordenada de passos.
- **`created_at: str`** — timestamp ISO-8601 de criação em UTC.
- **`status: StepStatus`** — estado global da transação.
- **`add_step(step_id: str, description: str) -> TransactionStep`** — cria um novo `TransactionStep`, adiciona-o à lista `steps` e devolve-o.
- **`start_step(step_id: str) -> None`** — marca o passo com o id indicado como `IN_PROGRESS`, regista o timestamp de início e coloca a transação em `IN_PROGRESS`.
- **`complete_step(step_id: str, result: dict | None = None) -> None`** — marca o passo como `COMPLETED`, guarda o resultado e o timestamp; se todos os passos estiverem concluídos, promove a transação a `COMPLETED`.
- **`fail_step(step_id: str, error: str) -> None`** — marca o passo como `FAILED`, regista o erro e o timestamp e coloca a transação em `FAILED`.

##### `class TransactionManager`
Gere o conjunto de transações ativas e o histórico, mantendo-as em memória num dicionário indexado pelo `transaction_id`.

- **`__init__() -> None`** — inicializa o dicionário interno `_transactions` vazio.
- **`create(use_case: str, device_id: str = "") -> Transaction`** — cria uma nova `Transaction`, regista-a e devolve-a.
- **`get(transaction_id: str) -> Transaction | None`** — devolve a transação associada ao identificador, ou `None` se não existir.
- **`list_active() -> list[Transaction]`** — devolve as transações em estado `PENDING` ou `IN_PROGRESS`.
- **`list_all() -> list[Transaction]`** — devolve todas as transações registadas.

---

#### [services/egw-controller/src/egw_controller/clients/aca_py_client.py](../services/egw-controller/src/egw_controller/clients/aca_py_client.py)

Módulo que expõe um cliente HTTP para a API admin do ACA-Py (Hyperledger Aries). Permite gerir conexões DIDComm, emitir Verifiable Credentials e solicitar provas ZKP.

##### `class AcaPyClient`
Cliente síncrono que encapsula chamadas à API admin de um agente ACA-Py.

- **`__init__(admin_url: str) -> None`** — guarda o URL admin do agente, removendo a barra final caso exista.
- **`get_status() -> dict`** — faz `GET /status` e devolve o JSON com o estado do agente.
- **`create_oob_invitation(goal_code: str = "", label: str = "") -> dict`** — faz `POST /out-of-band/create-invitation` com o protocolo `didexchange/1.0`, incluindo opcionalmente `goal_code` e `my_label`, e devolve o convite gerado. Usado nos passos de estabelecimento de conexão DIDComm.
- **`receive_oob_invitation(invitation: dict) -> dict`** — faz `POST /out-of-band/receive-invitation` com o payload do convite recebido e devolve o resultado. Permite que o agente aceite um convite criado por outro.
- **`list_connections() -> list[dict]`** — faz `GET /connections` e devolve a lista em `results`.
- **`issue_credential(credential_data: dict) -> dict`** — faz `POST /issue-credential-2.0/send` para emitir uma Verifiable Credential segundo o protocolo Issue Credential v2. Usado, por exemplo, para a Genesis VC no UC3 ou a Ownership VC no UC4.
- **`request_proof(proof_request: dict) -> dict`** — faz `POST /present-proof-2.0/send-request` para solicitar a apresentação de uma prova segundo Present Proof v2. Suporta a verificação de credenciais nos use cases.
- **`create_public_did(method: str = "sov") -> dict`** — faz `POST /wallet/did/create` para criar um DID público no ledger com o método indicado (por defeito `sov`).

---

#### [services/egw-controller/src/egw_controller/clients/fabric_client.py](../services/egw-controller/src/egw_controller/clients/fabric_client.py)

Módulo que fornece o cliente para o Hyperledger Fabric (ecosystem ledger). Invoca os chaincodes `device-lifecycle` e `dataset-tracking`, atualmente via simulação local com previsão futura de chamadas CLI ou SDK.

##### `class FabricClient`
Cliente para interação com o Fabric. Mantém referências ao peer, canal e nomes dos chaincodes de ciclo de vida e de datasets.

- **`__init__(peer_url, channel, chaincode_lifecycle, chaincode_dataset) -> None`** — guarda o URL do peer, o canal e os nomes dos dois chaincodes, aplicando defaults locais (`localhost:7051`, `c2dta-channel`, `device-lifecycle`, `dataset-tracking`).
- **`invoke_chaincode(chaincode: str, function: str, args: list[str]) -> dict[str, Any]`** — serializa os argumentos para JSON, regista a invocação e devolve um dicionário simulado com `status: ok` e o eco dos parâmetros. Em produção, delegaria no SDK Python ou numa chamada `subprocess` ao container CLI.
- **`register_device_model(model_id, manufacturer, wot_td_hash) -> dict`** — invoca `RegisterDeviceModel` no chaincode de ciclo de vida. Suporta o UC2.
- **`manufacture_device(device_id, model_id, manufacturer_id, genesis_vc_hash) -> dict`** — invoca `ManufactureDevice` para registar o nascimento de um dispositivo. Usado no UC3.
- **`make_available(device_id: str) -> dict`** — invoca `MakeAvailable` para transitar o dispositivo para o estado `Available`.
- **`initiate_transit(device_id: str, buyer_did: str) -> dict`** — invoca `InitiateTransit` para marcar o dispositivo como em trânsito para um comprador. Passo central do UC4.
- **`claim_device(device_id, controller_did, ownership_vc_hash) -> dict`** — invoca `ClaimDevice` para registar a reivindicação por um controlador. Passo central do UC5.
- **`twin_device(device_id: str, ditto_thing_id: str) -> dict`** — invoca `TwinDevice` para associar um Thing Ditto ao dispositivo. Passo central do UC6.
- **`untwin_device(device_id: str) -> dict`** — invoca `UntwinDevice` para desfazer a ligação ao Digital Twin. Passo central do UC7.
- **`decommission_device(device_id: str) -> dict`** — invoca `DecommissionDevice` para marcar o dispositivo como descomissionado.
- **`query_device(device_id: str) -> dict`** — invoca `QueryDevice` para consultar o estado atual de um dispositivo; suporta o endpoint `GET /devices/{id}`.
- **`register_dataset(dataset_id, device_id, ipfs_hash, owner_did, size_bytes, record_count, start_time, end_time) -> dict`** — invoca `RegisterDataset` no chaincode `dataset-tracking` para registar um snapshot IPFS, convertendo os inteiros para string.
- **`query_datasets(device_id: str) -> dict`** — invoca `QueryDatasetsByDevice` no chaincode `dataset-tracking` para listar os datasets associados a um dispositivo.

---

#### [services/egw-controller/src/egw_controller/clients/ditto_client.py](../services/egw-controller/src/egw_controller/clients/ditto_client.py)

Módulo que expõe um cliente HTTP para a API do Eclipse Ditto. Gere things (Digital Twins) e respetivas features.

##### `class DittoClient`
Cliente síncrono para a API HTTP do Ditto, autenticado via Basic Auth.

- **`__init__(base_url: str, username: str, password: str) -> None`** — guarda a base URL (sem barra final) e prepara o objeto `httpx.BasicAuth` com as credenciais.
- **`create_thing(thing_id: str, features: dict[str, Any]) -> dict`** — faz `PUT /api/2/things/{thing_id}` com o corpo `{thingId, features}` para criar um novo thing. Passo central do UC6 (twinning).
- **`get_thing(thing_id: str) -> dict | None`** — faz `GET /api/2/things/{thing_id}` e devolve o thing em JSON, ou `None` se o servidor responder com 404.
- **`delete_thing(thing_id: str) -> None`** — faz `DELETE /api/2/things/{thing_id}` para remover o thing. Passo central do UC7 (untwinning).
- **`get_thing_features(thing_id: str) -> dict`** — faz `GET /api/2/things/{thing_id}/features` e devolve as features atuais. Útil para capturar snapshots antes de os enviar para IPFS.

---

#### [services/egw-controller/src/egw_controller/clients/ipfs_client.py](../services/egw-controller/src/egw_controller/clients/ipfs_client.py)

Módulo que expõe um cliente HTTP para a API do IPFS (Kubo). Armazena e recupera snapshots de dados produzidos pelos Digital Twins.

##### `class IPFSClient`
Cliente síncrono para a API HTTP do IPFS.

- **`__init__(api_url: str) -> None`** — guarda a URL da API IPFS, removendo a barra final caso exista.
- **`add_json(data: dict[str, Any], filename: str = "dataset.json") -> str`** — serializa o dicionário para JSON, faz `POST /api/v0/add` com `pin=true` e devolve o CID devolvido pelo IPFS. Usado para persistir snapshots do Digital Twin.
- **`cat(cid: str) -> bytes`** — faz `POST /api/v0/cat?arg={cid}` para recuperar o conteúdo binário associado ao CID indicado.
- **`pin(cid: str) -> None`** — faz `POST /api/v0/pin/add?arg={cid}` para fixar um CID e garantir a sua persistência no nó IPFS local.

---

### 17.2 EGW Controller — Use Cases (UC1–UC8)

#### [use_cases/uc1_oem_enrollment.py](../services/egw-controller/src/egw_controller/use_cases/uc1_oem_enrollment.py)

Implementa o UC1 — OEM Enrollment, referenciado à Secção 3.2.1 do paper, no qual o consórcio inscreve um OEM emitindo-lhe uma Enrollment VC após estabelecer uma conexão DIDComm.

##### `execute(request: EnrollmentRequest, consortium_client: AcaPyClient, tx_manager: TransactionManager) -> UCResponse`

A função orquestra a inscrição do OEM no consórcio através de três passos sequenciais registados numa transação.

1. Cria a transação com `tx_manager.create(use_case="UC1-OEM-Enrollment")` e adiciona os passos `"oob"`, `"connect"` e `"vc"`.
2. Passo `"oob"`: invoca `consortium_client.create_oob_invitation(...)` com o `goal_code="c2dta.consortium.enroll.OEM"` e `label=f"Enrollment: {request.organization_name}"`, completando o passo com o convite gerado.
3. Passo `"connect"`: marca a conexão DIDComm como estabelecida com `status="auto-accepted"` (auto-aceite via configuração do ACA-Py).
4. Passo `"vc"`: completa o passo registando a emissão da Enrollment VC com o nome da organização.
5. Retorna `UCResponse` com `success=True`, `use_case="UC1"`, mensagem de inscrição e o `transaction_id` no campo `data`.

Erros: o bloco `except Exception` regista o erro em log e devolve `UCResponse` com `success=False`, `use_case="UC1"` e a mensagem da exceção (`str(e)`).

---

#### [use_cases/uc2_model_registration.py](../services/egw-controller/src/egw_controller/use_cases/uc2_model_registration.py)

Implementa o UC2 — Device Model Registration, referenciado à Secção 3.2.2 do paper, registando um modelo de dispositivo no ecosystem ledger Hyperledger Fabric.

##### `execute(request: ModelRegistrationRequest, fabric_client: FabricClient, tx_manager: TransactionManager) -> UCResponse`

A função realiza um único passo de registo do modelo no ledger.

1. Cria a transação com `tx_manager.create(use_case="UC2-Model-Registration")` e adiciona o passo `"ledger"`.
2. Passo `"ledger"`: invoca `fabric_client.register_device_model(model_id=request.model_id, manufacturer=request.manufacturer, wot_td_hash=request.wot_td_hash)` e completa o passo com o resultado devolvido pelo Fabric.
3. Retorna `UCResponse` com `success=True`, `use_case="UC2"`, mensagem confirmando o registo do modelo e o `transaction_id` no campo `data`.

Erros: o bloco `except Exception` regista o erro em log e devolve `UCResponse` com `success=False`, `use_case="UC2"` e `message=str(e)`.

---

#### [use_cases/uc3_device_registration.py](../services/egw-controller/src/egw_controller/use_cases/uc3_device_registration.py)

Implementa o UC3 — Device Self-Registration, referenciado à Secção 3.2.3 do paper, cobrindo a emissão da Genesis VC e a transição do dispositivo de Manufactured para Available no ledger.

##### `execute(request: DeviceRegistrationRequest, oem_client: AcaPyClient, fabric_client: FabricClient, tx_manager: TransactionManager) -> UCResponse`

A função executa quatro passos que identificam, creditam e disponibilizam o dispositivo no ecossistema.

1. Cria a transação com `tx_manager.create(use_case="UC3-Device-Registration", device_id=request.device_id)` e adiciona os passos `"identity"`, `"genesis"`, `"ledger"` e `"available"`.
2. Passo `"identity"`: completa o passo com o `device_id` e o valor de `request.device_type.value`.
3. Passo `"genesis"`: completa o passo registando `{"genesis_vc": "issued"}` (marca simbólica da emissão da Genesis VC).
4. Passo `"ledger"`: invoca `fabric_client.manufacture_device(device_id, model_id, manufacturer_id=request.manufacturer_did, genesis_vc_hash="genesis-vc-hash-placeholder")` e completa o passo com o resultado.
5. Passo `"available"`: invoca `fabric_client.make_available(request.device_id)` e completa o passo com o resultado, transitando o dispositivo para Available.
6. Retorna `UCResponse` com `success=True`, `use_case="UC3"`, `device_id`, mensagem confirmando o registo e disponibilização e o `transaction_id` no campo `data`.

Erros: o bloco `except Exception` regista o erro em log e devolve `UCResponse` com `success=False`, `use_case="UC3"`, o `device_id` da requisição e `message=str(e)`.

---

#### [use_cases/uc4_device_purchase.py](../services/egw-controller/src/egw_controller/use_cases/uc4_device_purchase.py)

Implementa o UC4 — Consumer Buys Device, referenciado à Secção 3.2.4 do paper, colocando o dispositivo em estado In-Transit após a compra pelo consumidor.

##### `execute(request: PurchaseRequest, fabric_client: FabricClient, tx_manager: TransactionManager) -> UCResponse`

A função executa um único passo que desencadeia a transição para In-Transit no ledger.

1. Cria a transação com `tx_manager.create(use_case="UC4-Purchase", device_id=request.device_id)` e adiciona o passo `"transit"`.
2. Passo `"transit"`: invoca `fabric_client.initiate_transit(request.device_id, request.buyer_did)` e completa o passo com o resultado devolvido pelo Fabric.
3. Retorna `UCResponse` com `success=True`, `use_case="UC4"`, `device_id`, mensagem indicando que o dispositivo segue em trânsito para o `buyer_did` e o `transaction_id` no campo `data`.

Erros: o bloco `except Exception` regista o erro em log e devolve `UCResponse` com `success=False`, `use_case="UC4"`, o `device_id` e `message=str(e)`.

---

#### [use_cases/uc5_device_claiming.py](../services/egw-controller/src/egw_controller/use_cases/uc5_device_claiming.py)

Implementa o UC5 — Device Claiming, referenciado à Secção 3.2.5 do paper, permitindo ao controlador reivindicar o dispositivo após verificação das credenciais Ownership e Genesis.

##### `execute(request: ClaimRequest, fabric_client: FabricClient, tx_manager: TransactionManager) -> UCResponse`

A função desenrola dois passos: verificação das VCs e transição para Claimed.

1. Cria a transação com `tx_manager.create(use_case="UC5-Claiming", device_id=request.device_id)` e adiciona os passos `"verify"` e `"claim"`.
2. Passo `"verify"`: completa o passo marcando `{"ownership_valid": True, "genesis_valid": True}` (verificação das Ownership e Genesis VCs).
3. Passo `"claim"`: invoca `fabric_client.claim_device(request.device_id, request.controller_did, request.ownership_vc_hash)` e completa o passo com o resultado.
4. Retorna `UCResponse` com `success=True`, `use_case="UC5"`, `device_id`, mensagem confirmando a reivindicação pelo `controller_did` e o `transaction_id` no campo `data`.

Erros: o bloco `except Exception` regista o erro em log e devolve `UCResponse` com `success=False`, `use_case="UC5"`, o `device_id` e `message=str(e)`.

---

#### [use_cases/uc6_device_twinning.py](../services/egw-controller/src/egw_controller/use_cases/uc6_device_twinning.py)

Implementa o UC6 — SD Twinning, referenciado à Secção 3.2.6 do paper, criando o Digital Twin no Eclipse Ditto, configurando o streaming MQTT e transitando o dispositivo para Twinned no ledger.

##### `execute(request: TwinRequest, ditto_client: DittoClient, fabric_client: FabricClient, tx_manager: TransactionManager) -> UCResponse`

A função executa três passos que ligam o dispositivo físico à sua réplica digital.

1. Cria a transação com `tx_manager.create(use_case="UC6-Twinning", device_id=request.device_id)` e adiciona os passos `"ditto"`, `"mqtt"` e `"ledger"`. Calcula `thing_id = f"org.c2dta:{request.device_id}"`.
2. Passo `"ditto"`: constrói o dicionário `features` com `"heartbeat"` (`{"properties": {"bpm": 0}}`), `"geolocation"` (`{"properties": {"latitude": 0.0, "longitude": 0.0}}`) e `"timestamp"` (`{"properties": {"value": ""}}`), invoca `ditto_client.create_thing(thing_id, features)` e completa o passo com o `thing_id`.
3. Passo `"mqtt"`: completa o passo registando o tópico `f"egw/{request.device_id}/telemetry"` (o SD começa a publicar telemetria).
4. Passo `"ledger"`: invoca `fabric_client.twin_device(request.device_id, thing_id)` e completa o passo com o resultado.
5. Retorna `UCResponse` com `success=True`, `use_case="UC6"`, `device_id`, mensagem indicando que o dispositivo está twinned com o `thing_id` e `data` contendo `transaction_id` e `thing_id`.

Erros: o bloco `except Exception` regista o erro em log e devolve `UCResponse` com `success=False`, `use_case="UC6"`, o `device_id` e `message=str(e)`.

---

#### [use_cases/uc7_device_untwinning.py](../services/egw-controller/src/egw_controller/use_cases/uc7_device_untwinning.py)

Implementa o UC7 — SD Untwinning, referenciado à Secção 3.2.7 do paper, revertendo a gemelização ao parar o streaming, remover o Digital Twin do Ditto e transitar o dispositivo para Claimed no ledger.

##### `execute(request: UntwinRequest, ditto_client: DittoClient, fabric_client: FabricClient, tx_manager: TransactionManager) -> UCResponse`

A função reverte o twinning em três passos coordenados.

1. Cria a transação com `tx_manager.create(use_case="UC7-Untwinning", device_id=request.device_id)` e adiciona os passos `"stop"`, `"ditto"` e `"ledger"`. Calcula `thing_id = f"org.c2dta:{request.device_id}"`.
2. Passo `"stop"`: completa o passo marcando `{"streaming": "stopped"}` (terminação do streaming MQTT).
3. Passo `"ditto"`: invoca `ditto_client.delete_thing(thing_id)` e completa o passo com `{"thing_id": thing_id, "deleted": True}`.
4. Passo `"ledger"`: invoca `fabric_client.untwin_device(request.device_id)` e completa o passo com o resultado, retornando o dispositivo a Claimed.
5. Retorna `UCResponse` com `success=True`, `use_case="UC7"`, `device_id`, mensagem confirmando o untwinning e o `transaction_id` no campo `data`.

Erros: o bloco `except Exception` regista o erro em log e devolve `UCResponse` com `success=False`, `use_case="UC7"`, o `device_id` e `message=str(e)`.

---

#### [use_cases/uc8_device_selling.py](../services/egw-controller/src/egw_controller/use_cases/uc8_device_selling.py)

Implementa o UC8 — SD Selling, referenciado à Secção 3.2.8 do paper, revogando a Ownership VC do vendedor, emitindo uma nova ao comprador e colocando o dispositivo em trânsito.

##### `execute(request: SellRequest, fabric_client: FabricClient, tx_manager: TransactionManager) -> UCResponse`

A função executa três passos que transferem a propriedade do dispositivo.

1. Cria a transação com `tx_manager.create(use_case="UC8-Selling", device_id=request.device_id)` e adiciona os passos `"revoke"`, `"issue"` e `"transit"`.
2. Passo `"revoke"`: completa o passo marcando `{"revoked": True}` (revogação da Ownership VC do vendedor).
3. Passo `"issue"`: completa o passo registando `{"buyer_did": request.buyer_did}` (emissão da nova Ownership VC ao comprador).
4. Passo `"transit"`: invoca `fabric_client.initiate_transit(request.device_id, request.buyer_did)` e completa o passo com o resultado, passando o dispositivo para In-Transit.
5. Retorna `UCResponse` com `success=True`, `use_case="UC8"`, `device_id`, mensagem indicando que o dispositivo segue em venda para o `buyer_did` e o `transaction_id` no campo `data`.

Erros: o bloco `except Exception` regista o erro em log e devolve `UCResponse` com `success=False`, `use_case="UC8"`, o `device_id` e `message=str(e)`.

---

### 17.3 Smart Device Simulator

#### [services/smart-device-simulator/src/smart_device_simulator/simulator.py](../services/smart-device-simulator/src/smart_device_simulator/simulator.py)

Implementa o simulador de um smartwatch C2DTA. Gera leituras de batimento cardíaco e de geolocalização a 1 Hz segundo o modelo descrito na Secção 4 do paper.

##### `class SmartDeviceSimulator`
Simula um smartwatch com sensor de ritmo cardíaco e GPS. Mantém estado interno entre leituras para aplicar random walk ao BPM e drift gaussiano à posição.

Constantes de classe:
- `MIN_BPM` (int): limite inferior fisiológico do batimento cardíaco (40).
- `MAX_BPM` (int): limite superior fisiológico do batimento cardíaco (200).
- `BPM_STEP_MAX` (int): variação máxima absoluta do BPM entre leituras (3).
- `GEO_DRIFT_STD` (float): desvio-padrão do drift geográfico em graus, equivalente a cerca de 5,5 metros.

Campos de instância:
- `device_uuid` (str): identificador único do dispositivo simulado.
- `_heartbeat` (int) *(privado)*: valor atual do BPM.
- `_lat` (float) *(privado)*: latitude atual em WGS84.
- `_lon` (float) *(privado)*: longitude atual em WGS84.

##### `__init__(device_uuid: str, initial_heartbeat: int = 72, initial_lat: float = 38.7223, initial_lon: float = -9.1393) -> None`
Inicializa o simulador com UUID e valores iniciais de BPM e coordenadas. Os valores por omissão correspondem a Lisboa e a um BPM de repouso típico.

##### `_next_heartbeat(self) -> int` *(privado)*
Calcula o próximo valor de BPM através de uma random walk com mean-reversion. Adiciona um passo aleatório entre `-BPM_STEP_MAX` e `+BPM_STEP_MAX` e aplica uma correção suave para puxar o valor para o intervalo normal (60–100). O resultado é limitado ao intervalo fisiológico `[MIN_BPM, MAX_BPM]`.

##### `_next_geolocation(self) -> GeoLocation` *(privado)*
Aplica drift gaussiano à latitude e longitude atuais, simulando movimento pedestre. Limita as coordenadas aos intervalos válidos `[-90, 90]` e `[-180, 180]` e devolve um `GeoLocation` com 7 casas decimais.

##### `read_sensors(self) -> SensorReading`
Gera uma nova leitura de sensores. Avança o estado interno (BPM e GPS) e devolve um `SensorReading` completo com `device_uuid`, valores de sensores e timestamp UTC corrente.

---

#### [services/smart-device-simulator/src/smart_device_simulator/models.py](../services/smart-device-simulator/src/smart_device_simulator/models.py)

Define os modelos de dados Pydantic usados pelo simulador. Os modelos alinham com o payload MQTT especificado na Secção 4 do paper.

##### `class GeoLocation(BaseModel)`
Representa coordenadas WGS84.

Campos:
- `lat` (float): latitude em WGS84. Validador: `ge=-90`, `le=90`.
- `lon` (float): longitude em WGS84. Validador: `ge=-180`, `le=180`.

##### `class SensorReading(BaseModel)`
Representa uma leitura completa de sensores do smartwatch e corresponde ao payload MQTT publicado.

Campos:
- `device_uuid` (str): UUID do Smart Device emissor.
- `heartbeat_bpm` (int): batimento cardíaco em bpm. Validador: `ge=0`, `le=300`.
- `geolocation` (GeoLocation): localização GPS atual.
- `timestamp` (datetime): timestamp UTC ISO 8601. Tem `default_factory` que devolve `datetime.now(timezone.utc)`.

##### `to_mqtt_payload(self) -> str`
Serializa a leitura para JSON através de `model_dump_json()`, pronto para ser publicado como payload MQTT.

---

#### [services/smart-device-simulator/src/smart_device_simulator/mqtt_publisher.py](../services/smart-device-simulator/src/smart_device_simulator/mqtt_publisher.py)

Implementa o cliente MQTT com TLS que publica as leituras geradas pelo simulador no tópico `egw/<uuid>/telemetry` com QoS 1, conforme a hierarquia de tópicos C2DTA.

##### `class MQTTPublisher`
Publica telemetria do Smart Device via MQTT sobre TLS. Configura o cliente Paho MQTT, opcionalmente com mutual TLS, e mantém um loop de publicação.

Campos de instância:
- `simulator` (SmartDeviceSimulator): origem das leituras de sensores.
- `broker_host` (str): host do broker MQTT.
- `broker_port` (int): porta do broker MQTT (tipicamente 8883 para TLS).
- `publish_interval_ms` (int): intervalo entre publicações em milissegundos.
- `_running` (bool) *(privado)*: flag que controla o loop de publicação.
- `_client` (mqtt.Client) *(privado)*: cliente Paho MQTT com `client_id` derivado do UUID.
- `_topic` (str) *(privado)*: tópico de publicação `egw/<uuid>/telemetry`.

##### `__init__(simulator, broker_host="localhost", broker_port=8883, ca_cert=None, client_cert=None, client_key=None, publish_interval_ms=1000) -> None`
Cria o cliente MQTT e regista os callbacks de conexão, desconexão e publicação. Se for fornecido `ca_cert`, cria um `SSLContext` TLS, carrega a CA e opcionalmente o par certificado/chave do cliente para mTLS. Desativa `check_hostname` e exige verificação obrigatória do par.

##### `_on_connect(self, client, userdata, flags, rc, properties=None)` *(privado)*
Callback Paho disparado ao conectar ao broker. Regista em log se a conexão foi bem-sucedida (`rc == 0`) ou regista o código de erro caso contrário.

##### `_on_disconnect(self, client, userdata, flags, rc, properties=None)` *(privado)*
Callback Paho disparado ao desconectar do broker. Regista um aviso com o código de retorno.

##### `_on_publish(self, client, userdata, mid, rc=None, properties=None)` *(privado)*
Callback Paho disparado após cada publicação. Regista no nível `debug` o `mid` da mensagem publicada.

##### `start(self) -> None`
Inicia o loop de publicação. Regista handlers para `SIGTERM` e `SIGINT` para terminar a execução graciosamente, conecta ao broker, arranca a thread de rede Paho (`loop_start()`) e entra num ciclo que, a cada `publish_interval_ms`, gera uma leitura, serializa-a e publica-a com QoS 1. Em `finally`, desconecta e para a thread de rede.

##### `stop(self) -> None`
Sinaliza a paragem do loop de publicação definindo `_running` como `False`.

---

#### [services/smart-device-simulator/src/smart_device_simulator/config.py](../services/smart-device-simulator/src/smart_device_simulator/config.py)

Centraliza a leitura de configuração do simulador a partir de variáveis de ambiente.

##### `get_config() -> dict`
Devolve um dicionário com a configuração do simulador. Lê as variáveis `SD_UUID` (gera um UUID aleatório se ausente), `MQTT_BROKER_HOST`, `MQTT_BROKER_PORT`, `MQTT_CA_CERT` (omissão: `certs/ca.crt`), `MQTT_CLIENT_CERT`, `MQTT_CLIENT_KEY`, `SD_PUBLISH_INTERVAL_MS`, `SD_INITIAL_HEARTBEAT`, `SD_INITIAL_LAT` e `SD_INITIAL_LON`. Converte para os tipos apropriados (`int`, `float`).

---

#### [services/smart-device-simulator/examples/run_simulator.py](../services/smart-device-simulator/examples/run_simulator.py)

Ponto de entrada CLI que instancia o simulador e o publicador MQTT a partir da configuração de ambiente.

##### `main()`
Configura o logging no nível `INFO`, carrega a configuração via `get_config()`, cria um `SmartDeviceSimulator` e um `MQTTPublisher` com os parâmetros lidos e chama `publisher.start()`, bloqueando o processo no loop de publicação. Ajusta também `sys.path` para permitir importar o pacote quando executado diretamente a partir de `examples/`.

---

### 17.4 Hyperledger Fabric — Chaincodes Go

#### [services/fabric/chaincode/device-lifecycle/device_lifecycle.go](../services/fabric/chaincode/device-lifecycle/device_lifecycle.go)

Implementa o chaincode Hyperledger Fabric que gere o ciclo de vida dos dispositivos C2DTA. Modela os 6 estados do paper (Secção 3.1): `Manufactured → Available → In-Transit → Claimed → Twinned → Decommissioned`.

Constantes de estado: `StateManufactured`, `StateAvailable`, `StateInTransit`, `StateClaimed`, `StateTwinned`, `StateDecommissioned`.

##### `type DeviceModel struct`
Representa um modelo de dispositivo registado.

Campos:
- `ModelID` (`string`, tag `modelID`): identificador único do modelo.
- `Manufacturer` (`string`, tag `manufacturer`): identidade do fabricante.
- `WoTTDHash` (`string`, tag `wotTDHash`): hash do Thing Description Web of Things.
- `CreatedAt` (`string`, tag `createdAt`): timestamp RFC3339 de criação.

##### `type Device struct`
Representa um dispositivo individual no ecossistema C2DTA.

Campos:
- `DeviceID` (`string`, tag `deviceID`): identificador único do dispositivo.
- `ModelID` (`string`, tag `modelID`): referência ao `DeviceModel`.
- `State` (`string`, tag `state`): estado atual do ciclo de vida.
- `ManufacturerID` (`string`, tag `manufacturerID`): identidade do fabricante que o produziu.
- `OwnerDID` (`string`, tag `ownerDID`): DID do proprietário atual.
- `ControllerDID` (`string`, tag `controllerDID`): DID do controlador (consumidor final).
- `GenesisVCHash` (`string`, tag `genesisVCHash`): hash da Genesis Verifiable Credential.
- `OwnershipVCHash` (`string`, tag `ownershipVCHash`): hash da Ownership Verifiable Credential.
- `DittoThingID` (`string`, tag `dittoThingID`): identificador da Thing no Eclipse Ditto.
- `CreatedAt` (`string`, tag `createdAt`): timestamp RFC3339 de criação.
- `UpdatedAt` (`string`, tag `updatedAt`): timestamp RFC3339 da última atualização.

##### `type DeviceLifecycleChaincode struct{}`
Struct sem campos que agrupa os métodos do contrato inteligente.

##### `(t *DeviceLifecycleChaincode) Init(stub) *pb.Response`
Inicializa o chaincode na instanciação. Devolve `shim.Success(nil)` sem escrever no ledger.

##### `(t *DeviceLifecycleChaincode) Invoke(stub) *pb.Response`
Despacha as chamadas externas para o método correspondente consoante o nome da função. Suporta `RegisterDeviceModel`, `ManufactureDevice`, `MakeAvailable`, `InitiateTransit`, `ClaimDevice`, `TwinDevice`, `UntwinDevice`, `DecommissionDevice`, `QueryDevice`, `QueryDevicesByState` e `QueryDevicesByOwner`. Devolve erro se a função for desconhecida.

##### `(t *DeviceLifecycleChaincode) RegisterDeviceModel(stub, args) *pb.Response`
Regista um novo `DeviceModel` (UC2). Recebe `[modelID, manufacturer, wotTDHash]`, valida a aridade (3), constrói o modelo com `CreatedAt` atual, cria uma chave composta `DeviceModel~modelID` e escreve no ledger (`PutState`). Emite o evento `ModelRegistered`.

##### `(t *DeviceLifecycleChaincode) ManufactureDevice(stub, args) *pb.Response`
Regista um dispositivo fabricado (UC3). Recebe `[deviceID, modelID, manufacturerID, genesisVCHash]`, valida a aridade (4) e cria um `Device` com estado **Manufactured**. Escreve no ledger (`PutState`) indexado por `DeviceID` e emite o evento `DeviceManufactured`. Estado origem: *(inexistente)*; estado destino: `Manufactured`.

##### `(t *DeviceLifecycleChaincode) MakeAvailable(stub, args) *pb.Response`
Torna o dispositivo disponível para venda. Recebe `[deviceID]` e delega em `transition`. Transição: **Manufactured → Available**. Lê (`GetState`) e escreve (`PutState`). Devolve erro se o dispositivo não existir ou estiver noutro estado.

##### `(t *DeviceLifecycleChaincode) InitiateTransit(stub, args) *pb.Response`
Marca o início do transporte para um comprador (UC4). Recebe `[deviceID, buyerDID]` e atualiza `OwnerDID`. Transição: **Available → In-Transit**. Lê e escreve no ledger.

##### `(t *DeviceLifecycleChaincode) ClaimDevice(stub, args) *pb.Response`
Reivindica a posse física do dispositivo (UC5). Recebe `[deviceID, controllerDID, ownershipVCHash]` e atualiza `ControllerDID` e `OwnershipVCHash`. Transição: **In-Transit → Claimed**. Lê e escreve no ledger.

##### `(t *DeviceLifecycleChaincode) TwinDevice(stub, args) *pb.Response`
Cria o Digital Twin associando-o a uma Thing no Eclipse Ditto (UC6). Recebe `[deviceID, dittoThingID]` e atualiza `DittoThingID`. Transição: **Claimed → Twinned**. Lê e escreve no ledger.

##### `(t *DeviceLifecycleChaincode) UntwinDevice(stub, args) *pb.Response`
Dissocia o Digital Twin da Thing Ditto (UC7). Recebe `[deviceID]` e limpa `DittoThingID`. Transição: **Twinned → Claimed**. Lê e escreve no ledger.

##### `(t *DeviceLifecycleChaincode) DecommissionDevice(stub, args) *pb.Response`
Descomissiona permanentemente um dispositivo. Recebe `[deviceID]`, lê o dispositivo atual (`GetState`) e define `State = Decommissioned`, aceitando como origem **qualquer estado**. Escreve no ledger (`PutState`) e emite o evento `DeviceDecommissioned`.

##### `(t *DeviceLifecycleChaincode) QueryDevice(stub, args) *pb.Response`
Devolve o estado serializado de um dispositivo. Recebe `[deviceID]` e executa `GetState`. Devolve erro se o dispositivo não existir ou se a leitura falhar.

##### `(t *DeviceLifecycleChaincode) QueryDevicesByState(stub, args) *pb.Response`
Pesquisa todos os dispositivos num estado específico. Recebe `[state]`, constrói um seletor CouchDB `{"selector":{"state":"..."}}` e executa uma rich query (`GetQueryResult`) via o helper `richQuery`.

##### `(t *DeviceLifecycleChaincode) QueryDevicesByOwner(stub, args) *pb.Response`
Pesquisa dispositivos por DID do proprietário. Recebe `[ownerDID]`, constrói um seletor CouchDB `{"selector":{"ownerDID":"..."}}` e delega em `richQuery` (`GetQueryResult`).

##### `(t *DeviceLifecycleChaincode) getDevice(stub, deviceID) (*Device, error)` *(privado)*
Helper que lê um dispositivo do ledger (`GetState`) e o desserializa de JSON. Devolve erros descritivos se o dispositivo não existir ou a desserialização falhar.

##### `(t *DeviceLifecycleChaincode) transition(stub, deviceID, fromState, toState, modify) *pb.Response` *(privado)*
Helper genérico que aplica uma transição de estado. Lê o dispositivo, valida que o estado atual é `fromState` (caso contrário devolve erro `transicao invalida`), executa a função `modify` para alterar campos adicionais, define o novo estado e atualiza `UpdatedAt`. Escreve no ledger (`PutState`) e emite o evento `Device<toState>`.

##### `(t *DeviceLifecycleChaincode) richQuery(stub, query) *pb.Response` *(privado)*
Helper que executa uma rich query CouchDB (`GetQueryResult`). Itera os resultados, acumula os valores em `[]json.RawMessage` e devolve-os serializados. Garante o fecho do iterador via `defer`.

##### `main()`
Ponto de entrada do binário do chaincode. Inicia o shim com `shim.Start(new(DeviceLifecycleChaincode))` e regista qualquer erro em `stdout`.

---

#### [services/fabric/chaincode/dataset-tracking/dataset_tracking.go](../services/fabric/chaincode/dataset-tracking/dataset_tracking.go)

Implementa o chaincode Hyperledger Fabric que ancora hashes de datasets IPFS no ecosystem ledger. Garante proveniência e integridade dos dados do Digital Twin, conforme a Secção 3.2.6 do paper.

##### `type Dataset struct`
Representa um snapshot de dados do Digital Twin armazenado no IPFS.

Campos:
- `DatasetID` (`string`, tag `datasetID`): identificador único do dataset.
- `DeviceID` (`string`, tag `deviceID`): dispositivo de origem.
- `IPFSHash` (`string`, tag `ipfsHash`): CID IPFS do conteúdo ancorado.
- `OwnerDID` (`string`, tag `ownerDID`): DID do proprietário atual do dataset.
- `SizeBytes` (`int64`, tag `sizeBytes`): tamanho do dataset em bytes.
- `RecordCount` (`int`, tag `recordCount`): número de registos contidos.
- `StartTime` (`string`, tag `startTime`): instante inicial coberto pelo dataset.
- `EndTime` (`string`, tag `endTime`): instante final coberto pelo dataset.
- `CreatedAt` (`string`, tag `createdAt`): timestamp RFC3339 do registo no ledger.

##### `type DatasetTrackingChaincode struct{}`
Struct sem campos que agrupa os métodos do contrato inteligente de rastreamento de datasets.

##### `(t *DatasetTrackingChaincode) Init(stub) *pb.Response`
Inicializa o chaincode na instanciação. Devolve `shim.Success(nil)` sem escrever no ledger.

##### `(t *DatasetTrackingChaincode) Invoke(stub) *pb.Response`
Despacha as chamadas externas para o método correspondente. Suporta `RegisterDataset`, `QueryDataset`, `QueryDatasetsByDevice` e `TransferDatasetOwnership`. Devolve erro se a função for desconhecida.

##### `(t *DatasetTrackingChaincode) RegisterDataset(stub, args) *pb.Response`
Regista um novo dataset no ledger (UC6). Recebe `[datasetID, deviceID, ipfsHash, ownerDID, sizeBytes, recordCount, startTime, endTime]`, valida a aridade (8) e faz parsing de `sizeBytes` (int64) e `recordCount` (int) via `Sscanf`. Constrói o `Dataset` com `CreatedAt` atual, cria uma chave composta `Dataset~deviceID~datasetID` e escreve no ledger (`PutState`). Emite o evento `DatasetRegistered`.

##### `(t *DatasetTrackingChaincode) QueryDataset(stub, args) *pb.Response`
Devolve o dataset identificado pelo par `[deviceID, datasetID]`. Reconstrói a chave composta e lê (`GetState`). Devolve erro se não existir ou se a leitura falhar.

##### `(t *DatasetTrackingChaincode) QueryDatasetsByDevice(stub, args) *pb.Response`
Lista todos os datasets associados a um `deviceID`. Usa `GetStateByPartialCompositeKey("Dataset", []{deviceID})` para iterar todas as entradas com o prefixo do dispositivo e acumula os valores em `[]json.RawMessage`. Não é uma rich query CouchDB — usa iteração por chave composta parcial.

##### `(t *DatasetTrackingChaincode) TransferDatasetOwnership(stub, args) *pb.Response`
Transfere a propriedade de um dataset para um novo DID (UC8). Recebe `[deviceID, datasetID, newOwnerDID]`, lê o dataset pela chave composta (`GetState`), desserializa, atualiza `OwnerDID`, volta a serializar e escreve (`PutState`). Emite o evento `DatasetOwnershipTransferred`. Devolve erro se o dataset não existir.

##### `main()`
Ponto de entrada do binário do chaincode. Inicia o shim com `shim.Start(new(DatasetTrackingChaincode))` e regista qualquer erro em `stdout`.

---

### 17.5 DIDComm Agent

#### [services/didcomm-agent/src/didcomm_agent/service.py](../services/didcomm-agent/src/didcomm_agent/service.py)

Orquestra o agente DIDComm de alto nível: gere o par de chaves local, mantém o conjunto de pares conhecidos e executa o envio/receção de mensagens cifradas.

##### `@dataclass DIDCommInvitation`
Envelope de convite usado na criação de canal par-a-par.

- `did: str` — DID do agente que emite o convite.
- `endpoint: str` — endpoint HTTP/DIDComm a contactar.
- `public_key: str` — chave pública X25519 em base64 urlsafe.
- `label: str | None` — etiqueta humana opcional.
- `created_time: int` — timestamp UNIX de criação.

##### `@dataclass _Peer` *(privado)*
Representa um par registado localmente.

- `did: str` — DID do par.
- `endpoint: str` — endpoint do par.
- `public_key_b64: str` — chave pública X25519 serializada em base64.
- `label: str | None` — etiqueta associada.

- **`public_key() -> X25519PublicKey`** — descodifica e devolve a chave pública X25519 do par a partir do campo base64 guardado.

##### `class DIDCommAgent`
Agente DIDComm simplificado do Edge Gateway. Mantém identidade (DID, endpoint, label), par de chaves X25519 e dicionário interno de pares.

- **`__init__(did, endpoint, *, label=None, keypair=None)`** — inicializa o agente; se nenhum `KeyPair` for fornecido, gera um par X25519 novo via `generate_keypair`.
- **`public_key_b64 -> str`** — devolve a chave pública X25519 local em base64 urlsafe.
- **`create_invitation() -> DIDCommInvitation`** — constrói um convite com DID, endpoint, chave pública e label para partilhar com outro agente.
- **`accept_invitation(invitation) -> DIDCommInvitation`** — regista o par do convite recebido e devolve um contra-convite para onboarding mútuo.
- **`complete_handshake(invitation) -> None`** — armazena os dados do par após o convite local ter sido aceite pelo outro agente.
- **`list_peers() -> Iterable[str]`** — devolve um tuplo com os DIDs dos pares conhecidos.
- **`send_message(to_did, body, *, msg_type=...) -> EncryptedDIDCommMessage`** — cria uma `DIDCommMessage`, deriva a chave partilhada por X25519 ECDH + HKDF-SHA256 e cifra o JSON com ChaCha20-Poly1305 usando AAD `frm|to|created_time`. Devolve o envelope cifrado.
- **`receive_message(envelope) -> DIDCommMessage`** — deriva a chave partilhada X25519/HKDF-SHA256 com o par remetente, decifra com ChaCha20-Poly1305 e valida a AAD. Qualquer falha AEAD é traduzida em `MessageTamperingError`.
- **`_store_peer(invitation) -> None`** *(privado)* — regista ou atualiza o par no dicionário interno a partir de um convite.
- **`_build_aad(message) -> bytes`** *(privado)* — gera o AAD da mensagem local como `frm|to|created_time` codificado em UTF-8.
- **`_build_aad_from_envelope(envelope) -> bytes`** *(privado)* — gera o AAD equivalente a partir de um envelope cifrado recebido.

---

#### [services/didcomm-agent/src/didcomm_agent/crypto.py](../services/didcomm-agent/src/didcomm_agent/crypto.py)

Concentra as primitivas criptográficas do agente: X25519 para ECDH, HKDF-SHA256 para derivação de chave e ChaCha20-Poly1305 para cifra autenticada.

##### `@dataclass(frozen=True) KeyPair`
Representa um par de chaves X25519.

- `private_key: X25519PrivateKey` — chave privada X25519.
- `public_key: X25519PublicKey` — chave pública correspondente.

- **`public_bytes -> bytes`** — serializa a chave pública em formato bruto (Raw/Raw).
- **`private_bytes -> bytes`** — serializa a chave privada em formato bruto sem cifragem.
- **`public_b64() -> str`** — codifica `public_bytes` em base64 urlsafe ASCII.
- **`private_b64() -> str`** — codifica `private_bytes` em base64 urlsafe ASCII.

##### `generate_keypair() -> KeyPair`
Gera um par X25519 novo através de `X25519PrivateKey.generate()` e devolve-o encapsulado num `KeyPair`.

##### `load_public_key(data_b64) -> X25519PublicKey`
Descodifica a string base64 urlsafe e reconstrói a chave pública X25519 a partir dos bytes brutos.

##### `load_private_key(data_b64) -> X25519PrivateKey`
Descodifica a string base64 urlsafe e reconstrói a chave privada X25519 a partir dos bytes brutos.

##### `keypair_from_private_b64(priv_b64) -> KeyPair`
Carrega uma chave privada X25519 a partir de base64 e deriva a chave pública correspondente, devolvendo um `KeyPair` completo.

##### `derive_shared_key(our_private, peer_public) -> bytes`
Executa um ECDH X25519 entre a chave privada local e a pública do par. Passa o segredo partilhado por HKDF-SHA256 com `info=b"edge-gateway-didcomm"` e `salt=None`, produzindo 32 bytes adequados para ChaCha20-Poly1305.

##### `encrypt(shared_key, plaintext, aad) -> tuple[str, str]`
Gera um nonce de 12 bytes com `os.urandom` e cifra o `plaintext` com ChaCha20-Poly1305 autenticando a AAD fornecida. Devolve `(nonce_b64, ciphertext_b64)` em base64 urlsafe.

##### `decrypt(shared_key, nonce_b64, ciphertext_b64, aad) -> bytes`
Descodifica nonce e criptograma de base64 urlsafe e executa `ChaCha20Poly1305.decrypt`. Se o tag Poly1305 ou a AAD não validarem, a biblioteca lança `InvalidTag` e a chamada propaga o erro.

---

#### [services/didcomm-agent/src/didcomm_agent/message.py](../services/didcomm-agent/src/didcomm_agent/message.py)

Define as representações de mensagem DIDComm (simplificada) em texto claro e do envelope cifrado correspondente.

##### `@dataclass DIDCommMessage`
Representação simplificada de mensagem DIDComm v2.

- `type: str` — URI de tipo da mensagem.
- `body: Dict[str, Any]` — corpo aplicacional.
- `to: str` — DID destinatário.
- `frm: str` — DID remetente (serializado como `from`).
- `id: str` — identificador UUID gerado por omissão.
- `created_time: int` — timestamp UNIX gerado por omissão.

- **`to_json() -> str`** — serializa a mensagem em JSON canónico (chaves ordenadas, sem espaços) incluindo `id`, `type`, `body`, `to`, `from`, `created_time`.
- **`from_json(raw) -> DIDCommMessage`** *(classmethod)* — reconstrói a mensagem a partir de JSON, mapeando o campo `from` para o atributo `frm`.

##### `@dataclass EncryptedDIDCommMessage`
Envelope cifrado segundo a semântica DIDComm.

- `ciphertext: str` — criptograma em base64 urlsafe.
- `nonce: str` — nonce ChaCha20-Poly1305 em base64 urlsafe.
- `to: str` — DID destinatário.
- `frm: str` — DID remetente.
- `created_time: int` — timestamp UNIX do envelope.
- `typ: str` — tipo de conteúdo, por omissão `application/didcomm-encrypted+json`.

- **`to_json() -> str`** — serializa o envelope em JSON canónico com os campos do transporte.
- **`from_json(raw) -> EncryptedDIDCommMessage`** *(classmethod)* — reconstrói o envelope a partir de JSON, com `typ` opcional.

---

#### [services/didcomm-agent/src/didcomm_agent/storage.py](../services/didcomm-agent/src/didcomm_agent/storage.py)

Implementa persistência SQLite para agentes e pares DIDComm. A base de dados é criada em `_init_db` com duas tabelas: `agents` (colunas `agent_id` PK, `did`, `endpoint`, `label`, `private_key_b64`) e `peers` (PK composta por `agent_id` + `did`, mais `endpoint`, `public_key_b64`, `label`).

##### `class Storage`
Camada de acesso a SQLite para estado do agente.

- **`__init__(db_path)`** — guarda o caminho e invoca `_init_db` para garantir o esquema.
- **`_connect() -> sqlite3.Connection`** *(privado)* — abre uma nova ligação SQLite ao ficheiro indicado.
- **`_init_db() -> None`** *(privado)* — cria, se necessário, as tabelas `agents` e `peers` com os esquemas descritos acima.
- **`upsert_agent(agent_id, did, endpoint, label, keypair) -> None`** — insere ou atualiza um agente, guardando a chave privada X25519 em base64 urlsafe via `keypair.private_b64()`.
- **`get_agent(agent_id) -> Optional[tuple[str, str, Optional[str], KeyPair]]`** — carrega o agente e reconstrói o `KeyPair` X25519 a partir da chave privada persistida.
- **`upsert_peer(agent_id, invitation) -> None`** — insere ou atualiza a linha `peers` associada ao agente com os dados do convite.
- **`list_peers(agent_id) -> list[str]`** — devolve os DIDs dos pares registados para um agente.
- **`load_peers(agent_id) -> list[DIDCommInvitation]`** — materializa todos os pares como objetos `DIDCommInvitation`, úteis para reidratar o agente em memória.
- **`export_state(agent_id) -> dict`** — devolve um `dict` com o registo do agente e a lista de pares, para exportação/diagnóstico.

---

#### [services/didcomm-agent/src/didcomm_agent/api.py](../services/didcomm-agent/src/didcomm_agent/api.py)

Expõe o agente DIDComm via FastAPI. Ao arranque, consulta `DIDCOMM_DB_PATH` para ativar persistência SQLite opcional e mantém os agentes em memória em `AppState.agents`.

##### `class CreateAgentRequest(BaseModel)`
Modelo de pedido com `agent_id`, `did`, `endpoint`, `label` opcional.

##### `class InvitationResponse(BaseModel)`
Modelo de resposta com `did`, `endpoint`, `public_key`, `label`, `created_time`.

##### `class AcceptInvitationRequest(BaseModel)`
Modelo de pedido com `agent_id` e `invitation: InvitationResponse`.

##### `class SendMessageRequest(BaseModel)`
Modelo de pedido com `agent_id`, `to_did`, `body: dict`, `msg_type` opcional.

##### `class EnvelopeModel(BaseModel)`
Modelo do envelope cifrado com `ciphertext`, `nonce`, `to`, `frm`, `created_time`, `typ` opcional.

##### `class MessageModel(BaseModel)`
Modelo da mensagem em texto claro com `id`, `type`, `body`, `to`, `frm`, `created_time`.

##### `class ReceiveMessageRequest(BaseModel)`
Modelo de pedido com `agent_id` e `envelope: EnvelopeModel`.

##### `class AppState`
Estado partilhado em memória.

- `agents: dict[str, DIDCommAgent]` — agentes ativos indexados por `agent_id`.
- `storage: Storage | None` — camada de persistência opcional.
- **`__init__() -> None`** — inicializa dicionário vazio e `storage=None`.

##### Endpoints

- **`GET /health`** — responde `{"status": "ok"}`. Sem request/response models específicos.
- **`POST /agent`** — request `CreateAgentRequest`, response `InvitationResponse`. Restaura o agente a partir de `Storage` se disponível, reidrata pares via `complete_handshake`, e de outra forma cria um novo agente e persiste-o. Devolve sempre um convite atual.
- **`POST /accept`** — request `AcceptInvitationRequest`, response `InvitationResponse`. Reconstrói a `DIDCommInvitation`, chama `agent.accept_invitation`, persiste o par e devolve o contra-convite. Lança 400 se o agente não existir.
- **`POST /complete`** — request `AcceptInvitationRequest`, response `{"status": "ok"}`. Conclui o handshake registando o par e persistindo-o se houver storage.
- **`GET /peers?agent_id=...`** — query param `agent_id`, response `{"peers": [...]}`. Devolve os DIDs dos pares conhecidos.
- **`POST /send`** — request `SendMessageRequest`, response `EnvelopeModel`. Invoca `agent.send_message`, obtendo o envelope cifrado com ChaCha20-Poly1305.
- **`POST /receive`** — request `ReceiveMessageRequest`, response `MessageModel`. Reconstrói `EncryptedDIDCommMessage` e decifra via `agent.receive_message`.

---

#### [services/didcomm-agent/src/didcomm_agent/exceptions.py](../services/didcomm-agent/src/didcomm_agent/exceptions.py)

Define as exceções específicas do agente DIDComm.

##### `class UnknownPeerError(RuntimeError)`
É lançada quando uma operação referencia um DID de par que não está registado no agente.

##### `class MessageTamperingError(RuntimeError)`
É lançada quando uma mensagem recebida falha a verificação AEAD (tag Poly1305 ou AAD inválidos), sinalizando adulteração ou chave incorreta.

---

#### [services/didcomm-agent/src/didcomm_agent/__init__.py](../services/didcomm-agent/src/didcomm_agent/__init__.py)

Expõe a API pública do pacote. Reexporta as classes e exceções principais em `__all__`: `DIDCommAgent`, `DIDCommInvitation`, `DIDCommMessage`, `EncryptedDIDCommMessage`, `UnknownPeerError`, `MessageTamperingError`.

---

### 17.6 ACA-Py — plugins de protocolo C2DTA

#### [services/aca-py/plugins/c2dta_protocols/goal_codes.py](../services/aca-py/plugins/c2dta_protocols/goal_codes.py)

Define as constantes de goal codes C2DTA que permitem aos agentes ACA-Py identificar automaticamente o contexto de uma interação DIDComm e encaminhar o fluxo sem intervenção humana (ver Secção 3.1 do paper base).

##### Constantes de goal codes

- **`ENROLL_OEM = "c2dta.consortium.enroll.OEM"`** — UC1: inscrição de um OEM no consórcio C2DTA.
- **`REGISTER_MODEL = "c2dta.consortium.register.model"`** — UC2: registo de um modelo de dispositivo junto do consórcio.
- **`REGISTER_DEVICE = "c2dta.consortium.registerdevice"`** — UC3: auto-registo de um dispositivo (emissão da Genesis VC).
- **`BUY_DEVICE = "c2dta.consortium.buydevice"`** — UC4: compra de um dispositivo pelo consumidor.
- **`CLAIM_DEVICE = "c2dta.consortium.claim"`** — UC5: reivindicação/claiming do dispositivo pelo proprietário.
- **`TWIN_DEVICE = "c2dta.egw.twin"`** — UC6: twinning de um smart device no Edge Gateway.
- **`UNTWIN_DEVICE = "c2dta.egw.untwin"`** — UC7: untwinning de um smart device.
- **`SELL_DEVICE = "c2dta.egw.sell"`** — UC8: venda/transferência de um smart device.

##### `GOAL_CODE_DESCRIPTIONS: dict[str, str]`
Dicionário que mapeia cada goal code para a sua descrição humana em português (ex.: `ENROLL_OEM → "Inscricao de OEM no consorcio"`, `TWIN_DEVICE → "Twinning de smart device"`). Serve para logs e mensagens de interface.

---

#### [services/aca-py/plugins/c2dta_protocols/enrollment.py](../services/aca-py/plugins/c2dta_protocols/enrollment.py)

Handler ACA-Py para o UC1 (OEM Enrollment). Prepara a proposta de emissão da **Enrollment VC** que o consórcio (1@C) envia ao OEM (1@O) após receber a conexão DIDComm com o goal code `ENROLL_OEM` (paper, Secção 3.2.1).

##### `handle_enrollment_request(admin_url, connection_id, organization_name, organization_did, consortium_id="c2dta-default") -> dict[str, Any]`
Constrói e devolve o `dict` da proposta `issue-credential/2.0` para o schema Indy `EnrollmentCredential` v1.0. Os atributos incluídos na `credential_preview` são: `organization_name`, `organization_did`, `role` (fixado em `"OEM"`), `enrollment_date` (UTC ISO-8601 atual), `consortium_id` e `expiry_date` (vazio por omissão). É invocado pelo EGW Controller quando deteta `ENROLL_OEM` numa conexão recebida e regista um log informativo com o nome da organização e o `connection_id`.

---

#### [services/aca-py/plugins/c2dta_protocols/genesis.py](../services/aca-py/plugins/c2dta_protocols/genesis.py)

Handler ACA-Py para o UC3 (Device Self-Registration). Prepara a proposta de emissão da **Genesis VC** que o agente OEM envia ao dispositivo (EGW/SD) após este arrancar, gerar identidade e conectar-se via DIDComm (paper, Secção 3.2.3).

##### `handle_genesis_request(connection_id, device_uuid, model_id, manufacturer_did, firmware_version="1.0.0", wot_td_hash="", serial_number="") -> dict[str, Any]`
Constrói e devolve o `dict` da proposta `issue-credential/2.0` para o schema Indy `GenesisCredential` v1.0. A `credential_preview` contém os atributos: `device_uuid`, `model_id`, `manufacturer_did`, `manufacture_date` (UTC ISO-8601 atual), `firmware_version`, `wot_td_hash` (hash da Thing Description WoT) e `serial_number`. Emite log informativo com o UUID do dispositivo e o `connection_id`.

---

#### [services/aca-py/plugins/c2dta_protocols/ownership.py](../services/aca-py/plugins/c2dta_protocols/ownership.py)

Handler ACA-Py para os casos de uso de propriedade do dispositivo: emissão após compra (UC4), verificação no claiming (UC5) e revogação/reemissão na venda (UC8). Suporta a **Ownership VC** descrita nas Secções 3.2.4, 3.2.5 e 3.2.8 do paper.

##### `handle_ownership_issuance(connection_id, device_uuid, owner_did, previous_owner_did="", transfer_tx_hash="") -> dict[str, Any]`
Constrói a proposta `issue-credential/2.0` para o schema Indy `OwnershipCredential` v1.0, usada em UC4 e UC8. A `credential_preview` inclui: `device_uuid`, `owner_did`, `acquisition_date` (UTC ISO-8601 atual), `previous_owner_did` (preenchido em revenda) e `transfer_tx_hash` (referência à transação de transferência no ledger). Emite log com o novo proprietário e o dispositivo.

##### `handle_ownership_verification(connection_id, device_uuid) -> dict[str, Any]`
Constrói um `proof_request` Indy para UC5 (claiming) que solicita prova de posse da `OwnershipCredential` v1.0, pedindo os atributos `device_uuid`, `owner_did` e `acquisition_date` sob `ownership_attrs` com restrição ao schema respetivo. Não inclui predicados. Emite log informativo com o UUID do dispositivo em verificação.

---

#### [services/aca-py/plugins/c2dta_protocols/__init__.py](../services/aca-py/plugins/c2dta_protocols/__init__.py)

Marca o diretório como pacote Python `c2dta_protocols`. Contém apenas a docstring `"Protocolos C2DTA para agentes ACA-Py."` e não exporta símbolos adicionais nem tem lógica.

---

*Última revisão: 2026-04-20. Documento gerado para a dissertação de mestrado de Rui Duarte (ISCTE). Para feedback ou correções, contactar: ruimfduarte94@gmail.com.*
