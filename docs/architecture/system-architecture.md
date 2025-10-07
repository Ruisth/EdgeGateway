# Arquitetura de sistema do Edge Gateway

Este documento resume a arquitetura proposta no *EdgeGateway_Paper.pdf* e serve como guia de alto
nível para as decisões de engenharia.

## Visão macro
- **Dispositivos IoT**: sensores industriais, wearables e atuadores conectados ao gateway via
  protocolos heterogêneos.
- **Edge Gateway**: plataforma Linux embarcada (Yocto) com suporte a containers, aceleradores de
  IA e módulo TPM.
- **Digital Twin**: contratos inteligentes em blockchain mantêm o estado autorizado dos ativos,
  políticas e histórico de eventos.
- **Nuvem**: provedores de IA pesada, painéis de visualização e pipelines de treinamento.

## Módulos do gateway
1. **Gestão de conectividade** – drivers, adaptadores e roteamento para redes cabeadas e sem fio.
2. **Barramento de eventos** – broker MQTT/AMQP com políticas derivadas do ledger.
3. **Camada de IA** – inferência embarcada usando TensorFlow Lite/ONNX Runtime, com modelos
   atualizados OTA.
4. **Orquestração de containers** – engine container (Docker/Podman) combinada com supervisord ou
   Kubernetes leve (k3s) para garantir disponibilidade.
5. **Sincronização blockchain** – agentes que assinam transações, atualizam o Digital Twin e
   expõem APIs para auditoria.
6. **Monitoramento e observabilidade** – stack Prometheus/Grafana, logs estruturados, alertas.

## Requisitos de plataforma
- **Segurança**: boot seguro, discos criptografados, gestão de certificados por TPM.
- **Resiliência**: updates atômicos, rollback e watchdogs de saúde.
- **Gerenciamento remoto**: APIs para provisionamento, configuração e atualização OTA.
- **Conformidade**: aderência a LGPD/GDPR com trilhas de auditoria fornecidas pela blockchain.

## Roadmap técnico
- Priorizar integração com BSP do hardware-alvo, drivers de conectividade e módulos de segurança.
- Construir pipelines de CI/CD para validar receitas Yocto, testes de integração de containers e
  políticas de smart contracts.
- Implementar dashboards e trilhas de logs seguindo requisitos de observabilidade do paper.
- Expandir documentação na pasta `docs/architecture/` com diagramas detalhados.
