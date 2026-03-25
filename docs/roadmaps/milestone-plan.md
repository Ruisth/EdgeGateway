# Plano de Marcos — Consumer-Controlled Digital Twin Architecture (C2DTA)

Alinhado com as fases de implementação do paper:
> Pinto et al., *"Consumer-Controlled Digital Twin Architecture"*, Blockchain: Research and Applications, 2025. DOI: 10.1016/j.bcra.2025.100342

Os 8 cenários funcionais do paper são os critérios de aceitação finais.

---

## Visão resumida

| Fase | Foco | Critério de saída |
| --- | --- | --- |
| **Fase 0** | Hardware-alvo, BSP, requisitos de segurança/compliance | Hardware escolhido; matriz de requisitos GDPR/LGPD aprovada |
| **Fase 1** | Hyperledger Fabric + Indy, ACA-py, Eclipse Ditto + Mosquitto | Build `edgegateway-image` reproduzível; cenários 1-3 funcionais |
| **Fase 2** | IPFS, W3C WoT, 8 cenários C2DTA completos | Todos os 8 cenários validados em ambiente local |
| **Fase 3** | Pilotos com dispositivos reais, auditoria, federated learning | >= 2 pilotos concluídos; relatório de auditoria assinado |

---

## Fase 0 — Preparação

**Objectivos**:
- Seleccionar hardware-alvo (SoC com suporte a TPM, memória suficiente para ACA-py + Eclipse Ditto)
- Validar BSP Yocto (Kirkstone / meta-edgegateway) para o hardware escolhido
- Formalizar requisitos de segurança: boot seguro, TPM para chaves privadas, mTLS entre serviços
- Formalizar requisitos de compliance: GDPR/LGPD — dados não saem do edge sem consentimento

**Infra**:
- CI/CD mínimo: lint + build de containers
- Repositório de imagens OCI privado
- Ambiente de desenvolvimento: docker-compose local para Fabric + Indy + ACA-py

**KPIs**:
- Decisão de hardware documentada
- Matriz de requisitos de segurança/compliance aprovada por stakeholders
- Ambiente dev local operacional

---

## Fase 1 — Base de sistema

**Objectivos**:
- Setup do **Hyperledger Fabric** (Ecosystem Ledger): chaincode para device lifecycle (`CreateDevice`, `UpdateDeviceStatus`, `TransferDevice`, `CreateDataSet`)
- Setup do **Hyperledger Indy** (Identity Ledger): BC Gov Test Network ou nó local para desenvolvimento
- Agentes **ACA-py** operacionais para: Consortium (`1@C`), OEM (`1@O`), EGW (`1@egw`)
- **Eclipse Ditto 3.0** + **Eclipse Mosquitto 2.0** em containers OCI no EGW
- Imagem Yocto `edgegateway-image` com todos os componentes acima

**Cenários a validar**:
- ✅ Cenário 1: OEM enroll no consórcio (Enrollment VC)
- ✅ Cenário 2: Registo de modelo de dispositivo (WoT + Fabric)
- ✅ Cenário 3: Auto-registo do dispositivo — EGW/SD gera DID, ancora no Indy, recebe Genesis VC

**KPIs**:
- Build diário estável (`bitbake edgegateway-image`)
- ACA-py agent arranca e gera DID público em < 5 s
- Cenários 1, 2, 3 testados com Aries Test Harness (ATH)
- Escrita no Fabric confirma em < 5 s (benchmark: ~2 s no paper)

---

## Fase 2 — Cenários completos

**Objectivos**:
- Integração **IPFS (Kubo)**: upload de datasets históricos do Eclipse Ditto; CID ancorado no Fabric
- Integração **W3C WoT Thing Description**: definição do modelo do SD para twinning no Ditto
- Agente consumer operacional (`1@A`) com **mediator** (`2@A`)
- Simulador de SD: sensor Python a 1 Hz (heartbeat, geolocation, timestamp) via MQTT/SSL
- Testes de performance: latências alinhadas com benchmarks do paper

**Cenários a validar**:
- ✅ Cenário 4: Consumidor compra dispositivo (Ownership VC)
- ✅ Cenário 5: Consumidor "claims" dispositivo (verificação Genesis VC + Ownership VC)
- ✅ Cenário 6: SD twinning (WoT + MQTT + Eclipse Ditto + IPFS)
- ✅ Cenário 7: SD untwinning
- ✅ Cenário 8: SD selling (revogação de VC + nova Ownership VC)

**KPIs**:
- Todos os 8 cenários funcionais validados end-to-end
- Latência DIDComm < 2 s para todas as interacções com utilizador
- Dados históricos correctamente armazenados no IPFS e referenciados no Fabric
- Cobertura de testes >= 70% nos componentes críticos (ACA-py agent, chaincode)

---

## Fase 3 — Pilotos e produção

**Objectivos**:
- Pilotos com dispositivos IoT reais (hardware-alvo da Fase 0)
- Auditoria de segurança: boot seguro, TPM, mTLS, DIDComm envelope security
- Compliance GDPR/LGPD: verificar que dados não saem do edge sem consentimento explícito
- Extensão opcional: Federated Learning sobre dados dos DTs (investigação futura)

**KPIs**:
- >= 2 pilotos completos com utilizadores reais
- SLA de latência cumprido (todos os benchmarks do paper)
- Relatório de auditoria de segurança assinado
- Documentação para certificação GDPR/LGPD

---

## 8 Cenários funcionais — Critérios de aceitação

| # | Cenário | Fase alvo | Actor principal | Resultado esperado |
| --- | --- | --- | --- | --- |
| 1 | OEM enroll no consórcio | Fase 1 | Consortium + OEM | Enrollment VC emitida e válida |
| 2 | Registo de modelo de dispositivo | Fase 1 | OEM | DeviceModel no Fabric; WoT file registado |
| 3 | Auto-registo do dispositivo | Fase 1 | EGW/SD | DID no Indy; Genesis VC; status AVAILABLE no Fabric |
| 4 | Consumidor compra dispositivo | Fase 2 | OEM + Consumer | Ownership VC emitida; status IN-TRANSIT |
| 5 | Consumer "claims" dispositivo | Fase 2 | Consumer + EGW | VCs verificadas; status CLAIMED; controllerId definido |
| 6 | SD twinning | Fase 2 | Consumer + EGW | Thing criado no Ditto; MQTT activo; status TWINNED |
| 7 | SD untwinning | Fase 2 | Consumer + EGW | Thing removido do Ditto; MQTT desligado; status CLAIMED |
| 8 | SD selling | Fase 2 | Consumer + OEM | Ownership VC revogada; nova Ownership VC; status IN-TRANSIT |

---

## Stack por fase

| Componente | Fase 1 | Fase 2 | Fase 3 |
| --- | --- | --- | --- |
| Hyperledger Fabric | ✅ Setup + chaincode básico | ✅ DataSet chaincode | ✅ Produção |
| Hyperledger Indy | ✅ BC Gov Test / dev node | ✅ VC revocation | ✅ Produção |
| ACA-py (Aries) | ✅ Agentes C+O+EGW | ✅ Agente consumer + mediator | ✅ Produção |
| Eclipse Ditto 3.0 | ✅ Container no EGW | ✅ WoT integration | ✅ Produção |
| Eclipse Mosquitto 2.0 | ✅ Broker SSL | ✅ SD → Ditto pipeline | ✅ Produção |
| IPFS (Kubo) | ❌ | ✅ Dataset export | ✅ Produção |
| W3C WoT | ❌ | ✅ Thing Description | ✅ Produção |
| Yocto image | ✅ Base + Ditto + Mosquitto + ACA-py | ✅ + IPFS + WoT | ✅ Hardware real |

---

## Próximos passos

1. Atribuir responsáveis e datas reais para cada fase
2. Criar issues/épicos no tracker (Fabric chaincode, ACA-py agents, Ditto config, IPFS integration)
3. Configurar ambiente local docker-compose para Fabric + Indy + ACA-py (pré-requisito Fase 1)
4. Avaliar hardware candidato (Raspberry Pi 4 / BeagleBone AI-64 / custom SOM com TPM)

> Última revisão: 2026-03-19
