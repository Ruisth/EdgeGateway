# Plano de marcos para o Edge Gateway

O plano abaixo deriva das fases sugeridas no *EdgeGateway_Paper.pdf* e orienta o backlog inicial.

## Fase 0 – Preparação
- Selecionar hardware-alvo, definir BSP e validar suporte a TPM/aceleradores.
- Configurar infraestrutura de CI/CD e repositórios privados de containers.
- Formalizar requisitos de segurança, privacidade e compliance citados no paper.

## Fase 1 – Base de sistema
- Montar ambiente Yocto com camada `meta-edgegateway` e BSP escolhido.
- Habilitar containers, broker MQTT e agentes de sincronização blockchain.
- Criar pipelines de teste para inferência local e validação de contratos inteligentes.

## Fase 2 – Observabilidade e governança
- Implementar coleta de métricas, logs e dashboards.
- Automatizar políticas de retenção de dados e anonimização.
- Integrar monitoramento com alertas baseados no Digital Twin.

## Fase 3 – Pilotos e integração completa
- Conectar dispositivos reais e validar fluxos descritos em
  `docs/architecture/communication-and-dataflow.md`.
- Rodar pilotos com usuários selecionados, recolhendo feedback sobre latência e usabilidade.
- Preparar documentação para certificações e auditorias.

## Próximos passos
- Refinar backlog com tarefas específicas do hardware escolhido.
- Adicionar indicadores de sucesso (KPIs) para cada marco.
- Atualizar este plano conforme decisões de arquitetura evoluírem.
