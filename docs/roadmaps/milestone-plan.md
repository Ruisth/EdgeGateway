# Plano de Marcos para o Edge Gateway

Derivado das fases do `EdgeGateway_Paper.pdf` e expandido para orientar planejamento tático. Atualize sempre que datas ou critérios mudarem.

## Visão resumida
| Fase | Período sugerido | Responsável primário | Critério de saída |
| --- | --- | --- | --- |
| Fase 0 – Preparação | Mês 1 | Equipe de Plataforma | Hardware escolhido, BSP avaliado, requisitos de segurança/compliance aprovados. |
| Fase 1 – Base de sistema | Meses 2-3 | Equipe Yocto/Infra | Build do `edgegateway-image` reproduzível + testes de smoke. |
| Fase 2 – Observabilidade e governança | Meses 4-5 | Equipe DevSecOps | Stack de observabilidade ativa e políticas automatizadas. |
| Fase 3 – Pilotos e integração | Meses 6-7 | Equipe de Produto/Field | Pilotos com dispositivos reais e documentação para auditorias. |

## Detalhamento
### Fase 0 – Preparação
- Selecionar hardware (SoC, memória, conectividade) e validar suporte a TPM/aceleradores.
- Configurar CI/CD mínimo (lint + build de containers) e repositórios privados.
- Formalizar requisitos de segurança, privacidade e compliance (LGPD/GDPR, políticas do ledger).

**KPIs**: decisão de hardware registrada; matriz de requisitos revisada com stakeholders.

### Fase 1 – Base de sistema
- Montar ambiente Yocto com `meta-edgegateway` + BSP.
- Habilitar containers, broker MQTT, agentes blockchain e DIDComm MVP.
- Criar pipelines de teste (unitários e integração) para inferência local e contratos inteligentes.

**KPIs**: build diário estável, cobertura mínima 70% nos testes do agente DIDComm, documentação atualizada.

### Fase 2 – Observabilidade e governança
- Instrumentar métricas, logs e dashboards (Prometheus, Grafana, Loki/Fluent Bit).
- Automatizar políticas de retenção e anonimização baseadas no ledger.
- Integrar monitoramento com alertas vinculados ao Digital Twin.

**KPIs**: tempo médio de detecção < 5 min, plano de resposta documentado, testes de auditoria aprovados.

### Fase 3 – Pilotos e integração completa
- Conectar dispositivos reais seguindo `communication-and-dataflow.md`.
- Rodar pilotos com usuários selecionados e coletar feedback (latência, UX, confiabilidade).
- Preparar documentação para certificações/auditorias e ajustar contratos inteligentes conforme feedback.

**KPIs**: >= 2 pilotos concluídos, SLA de latência cumprido, relatório de auditoria assinado.

## Próximos passos
1. Atribuir responsáveis nomeados e datas reais para cada marco.
2. Criar issues/épicos correspondentes no tracker do projeto.
3. Revisar este plano mensalmente ou quando ocorrer mudança relevante de escopo.

> Última revisão: 2025-11-18

