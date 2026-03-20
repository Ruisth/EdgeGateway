# Arquitetura de Sistema do Edge Gateway

Este documento consolida a visão macro, os componentes e os requisitos não-funcionais do Edge Gateway descrito no paper `EdgeGateway_Paper.pdf`. Ele serve como referência para decisões de engenharia e deve ser mantido alinhado aos experimentos conduzidos no laboratório e em campo.

## Visão macro
1. **Dispositivos IoT** – sensores industriais e residenciais, atuadores, wearables e controladores legados.
2. **Edge Gateway** – plataforma Linux (Yocto) com suporte a containers OCI, aceleradores de IA e TPM.
3. **Digital Twin + Blockchain** – contratos inteligentes que guardam identidades, políticas e auditoria.
4. **Nuvem/Laboratório** – pipelines de IA pesada, dashboards e integrações corporativas.

```
+-------------+        +-----------------+        +-------------------+
| Dispositivos|<-----> | Edge Gateway    |<-----> | Digital Twin /    |
| IoT         |        | (Yocto + OCI)   |        | Blockchain + Nuvem|
+-------------+        +-----------------+        +-------------------+
```

## Módulos principais
| Módulo | Responsabilidades | Observações |
| --- | --- | --- |
| Gestão de conectividade | Drivers, adaptadores industriais/residenciais, roteamento seguro | Integrar protocolos Modbus, OPC-UA, BLE, Thread, Wi-Fi 6/6E e 5G/LTE. |
| Barramento de eventos (MQTT) | Eclipse Mosquitto 2.0 com TLS (porta 8883), ACL por dispositivo | QoS 1 para telemetria a 1Hz, tópicos `egw/<uuid>/telemetry`. Ver `docs/architecture/mqtt-architecture.md`. |
| Digital Twin (Eclipse Ditto) | Plataforma DT com conectividade MQTT e WoT TD | Things `org.c2dta:<uuid>`, features heartbeat/geo/timestamp. Ver `docs/architecture/ditto-architecture.md`. |
| Blockchain Ecossistema (Fabric) | Hyperledger Fabric 2.5 — ciclo de vida 6 estados, dataset tracking | Chaincodes Go: `device-lifecycle`, `dataset-tracking`. Ver `docs/architecture/fabric-architecture.md`. |
| Blockchain Identidade (Indy) | Hyperledger Indy (von-network) — DIDs, schemas VC | Enrollment VC, Genesis VC, Ownership VC. Ver `docs/architecture/indy-architecture.md`. |
| Agentes SSI (ACA-Py) | 5 agentes ACA-Py (1@C, 1@O, 1@A, 1@egw, 1@sd) | Protocolos: OOB, Issue Credential v2, Present Proof v2. Ver `docs/architecture/indy-architecture.md`. |
| Armazenamento Descentralizado (IPFS) | IPFS Kubo — snapshots DT, CIDs ancorados no Fabric | Ver `docs/architecture/ipfs-architecture.md`. |
| EGW Controller | Orquestrador central FastAPI — 8 use cases (UC1-UC8) | Coordena Fabric, Ditto, ACA-Py, IPFS, MQTT. Ver `docs/architecture/egw-controller-architecture.md`. |
| Camada de IA | Inferência local (TensorFlow Lite/ONNX Runtime) com aceleradores (GPU/NPU) | Modelos versionados e atualizados OTA; checkpoints para retomada. |
| Orquestração de containers | Container engine (Docker/Podman) + sistema supervisor (k3s, systemd, supervisord) | Deve suportar atualizações atômicas e rollback. |
| Observabilidade e DevSecOps | Telemetria (Prometheus), logs estruturados, tracing, OTA | Integra com CI/CD e políticas de segurança derivadas do ledger. |

## Requisitos transversais
- **Segurança**: boot seguro, criptografia de disco, gestão de certificados via TPM/HSM, mTLS em todos os serviços e política de rotação automática de chaves.
- **Confiabilidade**: watchdogs de software/hardware, atualizações A/B (swupdate ou Mender), detecção de auto-recuperação e limites de uso de recursos.
- **Gerenciamento remoto**: APIs para provisionamento, configuração, coleta de inventário e atualizações OTA controladas.
- **Compliance**: aderência a LGPD/GDPR com retenção seletiva e trilhas de auditoria assinadas na blockchain.

## Critérios de desempenho
| Métrica | Meta inicial | Notas |
| --- | --- | --- |
| Latência de inferência | < 100 ms para modelos críticos | Medida do evento MQTT ao comando aplicado. |
| Disponibilidade do broker | >= 99,5% | Exige replicação ativa/passiva e detecção de falhas. |
| Tempo de sincronização do Twin | < 5 s para estados críticos | Depende do SLA da blockchain escolhida. |
| Consumo máximo de CPU | < 75% em operação nominal | Garante headroom para bursts e OTA. |

## Roadmap técnico (alto nível)
1. **BSP e hardware** – validar suporte a TPM, aceleração de IA e conectividade (Fase 0 do roadmap).
2. **Base Yocto** – consolidar `meta-edgegateway`, configurar `edgegateway-image` e automatizar builds.
3. **Pipelines CI/CD** – executar testes de integração de containers, inferência e contratos inteligentes.
4. **Observabilidade** – instrumentar métrica/log/tracing e conectar dashboards.
5. **Documentação viva** – manter diagramas PlantUML/Draw.io em `docs/architecture/diagrams/` (a criar) com versão controlada.

## Checklist de atualização do documento
- [ ] Diagrama atualizado após cada alteração estrutural significativa.
- [ ] Tabela de métricas revisada quando novos SLAs forem definidos.
- [ ] Links para decisões de arquitetura registrados na pasta `docs/adr/` (a ser criada).

> Última revisão: 2026-03-20

