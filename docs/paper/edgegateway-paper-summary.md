# Resumo do paper "EdgeGateway_Paper.pdf"

Síntese dos principais pontos do documento original. Use-o como índice rápido antes de consultar o PDF completo.

## 1. Visão geral
- Gateway conecta sensores/atuadores locais, pipelines de IA na nuvem e um Digital Twin na blockchain.
- Foco em confiabilidade, privacidade e governança de dados.
- Ciclo de vida: aquisição → inferência local → sincronização → observabilidade/auditoria.

## 2. Componentes principais
| Camada | Destaques | Cross-refs |
| --- | --- | --- |
| Dispositivos IoT | Sensores industriais, residenciais e wearables. | `docs/architecture/communication-and-dataflow.md` |
| Edge Gateway | Containers, broker MQTT, storage efêmero, agentes blockchain e IA embarcada. | `yocto/README.md`, `README.md` |
| Digital Twin/Blockchain | Contratos inteligentes com identidades, políticas e trilhas de auditoria. | `docs/architecture/didcomm-architecture.md` |
| Serviços de Nuvem | Treinamento pesado, dashboards, data lakes privados/públicos. | `docs/research/blockchain-personal-ai-summary.md` |

## 3. Requisitos de arquitetura
- Segurança ponta a ponta (TPM, TLS/DTLS, DIDComm, controle de acesso por contratos).
- Alta disponibilidade (containers redundantes, monitoramento, atualizações OTA).
- Observabilidade com métricas, logs e tracing.
- Governança de dados (retenção local, replicação seletiva, anonimização pré-envio).

## 4. Pipeline funcional
1. **Aquisição** – drivers normalizam protocolos heterogêneos.
2. **Processamento local** – inferência embarcada reduz latência e custo de tráfego.
3. **Orquestração** – barramento de eventos + service mesh aplicam políticas.
4. **Sincronização** – apenas deltas relevantes atingem o Digital Twin.
5. **Supervisão** – dashboards/APIs expõem estado e integração com sistemas externos.

## 5. Implicações para o desenvolvimento
- Yocto deve agregar BSPs do hardware escolhido, containers, brokers MQTT, agentes blockchain e toolchains de IA.
- DevSecOps: integração com registries privados, varredura de imagens, testes de conformidade com políticas do ledger.
- Versionamento rigoroso e backup/restore para dados sensíveis gerados no edge.

## 6. Conteúdos recomendados no PDF
| Seção do PDF | Descrição | Onde aplicar |
| --- | --- | --- |
| Cap. 2 | Requisitos funcionais e não funcionais | Atualizar ADMs/ADRs em `docs/architecture/`. |
| Cap. 3 | Arquitetura lógica e física | Modelar diagramas no repositório. |
| Cap. 4 | Estratégias de IA e pipelines | Expandir `docs/research/`. |
| Cap. 5 | Blockchain e governança | Alimentar contratos e políticas do DIDComm. |
| Apêndice | Métricas e SLAs | Atualizar tabelas de requisitos. |

> Para dúvidas específicas, registre uma issue com a referência da página do PDF.

> Última revisão: 2025-11-18

