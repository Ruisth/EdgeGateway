# Resumo do paper "EdgeGateway_Paper.pdf"

Este documento destaca os pontos essenciais extraídos do paper *EdgeGateway_Paper.pdf*, que
apresenta uma arquitetura de Edge Gateway para suportar um ecossistema de IA pessoal
sincronizado com blockchain.

## Visão geral
- O gateway é responsável por interligar sensores e atuadores locais com serviços de IA na
  nuvem e com um Digital Twin residente na blockchain.
- A solução enfatiza confiabilidade, privacidade e governança de dados, combinando edge
  computing, contratos inteligentes e sincronização contínua do gêmeo digital.
- O documento descreve um ciclo de vida completo que vai desde a aquisição de dados, passando
  por inferência local, até a persistência de estados e eventos no ledger distribuído.

## Componentes principais
1. **Camada de Dispositivos IoT** – sensores, atuadores e wearables fornecem eventos em tempo
   real que são normalizados pelo gateway.
2. **Edge Gateway** – executa um sistema Linux embarcado com containers para microsserviços,
   pipeline de IA, broker de mensagens (MQTT), armazenamento de curto prazo e agentes de
   sincronização com a blockchain.
3. **Digital Twin & Blockchain** – cada identidade digital mantém metadados, políticas de
   acesso e histórico de interações em contratos inteligentes, permitindo auditoria e
   rastreabilidade.
4. **Serviços de Nuvem** – pipelines de treinamento, dashboards e serviços de IA pesada são
   acionados quando necessário, recebendo dados do gateway por canais seguros.

## Requisitos de arquitetura
- **Segurança ponta a ponta** com módulos TPM, autenticação baseada em certificados e
  criptografia TLS/DTLS.
- **Alta disponibilidade** via containers redundantes, monitoramento e atualizações OTA.
- **Observabilidade** com coleta de métricas, logs estruturados e rastreamento distribuído.
- **Gerenciamento de dados** contemplando retenção local, replicação seletiva e anonimização
  antes do envio à blockchain ou nuvem.

## Pipeline funcional
1. **Aquisição**: drivers e agentes normalizam dados vindos de múltiplos protocolos industriais
   e de consumo.
2. **Processamento local**: modelos de IA embarcados realizam inferência para decisões em tempo
   real, reduzindo latência e custo de comunicação.
3. **Orquestração**: um barramento de eventos e um service mesh leve coordenam microsserviços e
   executam políticas derivadas de contratos inteligentes.
4. **Sincronização**: somente deltas relevantes são enviados ao Digital Twin na blockchain para
   garantir consistência com baixo custo.
5. **Supervisão**: dashboards e APIs fornecem visibilidade do estado do gateway, integrando-se a
   sistemas de gestão externos.

## Implicações para o desenvolvimento
- A plataforma Yocto deve agregar camadas BSP específicas do hardware-alvo e incluir suporte a
  containers, brokers MQTT, agentes blockchain e toolchains de IA.
- Estratégias de DevSecOps englobam integração com registries privados, varredura de imagens e
  testes de conformidade com políticas do ledger.
- A documentação recomenda manter trilhas claras de versionamento e políticas de backup para
  dados sensíveis gerados no edge.

