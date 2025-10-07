# Arquitetura DIDComm do Edge Gateway

Este documento detalha o desenho inicial do módulo DIDComm do Edge Gateway, alinhado às diretrizes
propostas no *EdgeGateway_Paper.pdf* e complementado pelos padrões descritos em estudos recentes
sobre identidade descentralizada e interoperabilidade segura \[1\]. O objetivo é oferecer um
subsistema de mensageria peer-to-peer com confidencialidade, autenticação mútua e governança
derivada do ledger blockchain.

## Objetivos
- **Troca segura de mensagens** entre o Edge Gateway e o Digital Twin, com suporte a canais
  confiáveis para provisionamento, telemetria crítica e comandos.
- **Gestão de identidades descentralizadas (DIDs)** baseada em chaves X25519/Ed25519 armazenadas
  em hardware seguro (TPM) quando disponível.
- **Agendador de políticas** que aplica restrições e auditoria conforme contratos inteligentes.
- **Compatibilidade com DIDComm v2** para permitir integração com agentes externos e redes SSI.

## Componentes principais
1. **Edge DIDComm Agent**: residente no gateway, encapsula chaves, resolução de DIDs e gerenciamento
   de sessões. Expõe uma API gRPC/REST para outros serviços internos publicarem mensagens.
2. **Twin DIDComm Agent**: executa na cloud, representando o Digital Twin. Mantém paridade de chaves,
   políticas de autorização e roteamento para contratos inteligentes.
3. **Resolver de DIDs**: abstrai diretórios locais, contrato blockchain ou serviços externos (como
   checagem Web5). Inicialmente, operará em modo in-memory com sincronização eventual usando o ledger.
4. **Filas/Bridges**: interface opcional para integrar o fluxo DIDComm ao broker MQTT interno quando
   necessário (por exemplo, assinaturas de eventos assinados).
5. **Observabilidade**: métricas e logs estruturados que preservam metadados (DID, tipo de mensagem,
   latência) respeitando privacidade.

## Fluxo de estabelecimento de canal
```
Edge Gateway                  Twin
    |  create_invitation()       |
    |--------------------------->| 1. convite contendo DID, endpoint e chave pública
    |                            |
    |  accept_invitation()       |
    |<---------------------------| 2. resposta com DID/endpoint/chave do Twin
    |                            |
    |  store_peer()              |
    |--------------------------->| 3. confirmação mútua e sincronização opcional no ledger
    |                            |
    |  pack_encrypted()          |
    |--------------------------->| 4. mensagens cifradas (telemetria, comandos)
    |                            |
    |<---------------------------| 5. acknowledgements, states
```

## Políticas de segurança
- Chaves privadas do gateway residem em TPM/HSM sempre que possível. Nesta fase inicial, serão
  armazenadas cifradas no sistema de ficheiros usando libsodium.
- Rotação de chaves baseada em contadores de mensagens ou tempo. O handshake prevê renegociação
  automática.
- Metadados sensíveis (ex.: tipo de mensagem) são minimizados. Dados para observabilidade usam IDs
  derivados de hash.
- Failover: se o Twin estiver indisponível, as mensagens são enfileiradas localmente e assinadas para
  posterior envio.

## Próximas evoluções
1. **Integração com contrato inteligente** para registrar convites e revogações.
2. **Suporte a DIDComm Routing** para operar através de mediadores (cloud hops).
3. **Assinatura de anexos binários** (Modelos IA, pacotes OTA) usando DIDComm attachments.
4. **Modo pairwise múltiplo** para interagir com vários Twins ou orquestradores regionais.

## Referências
[1] Artigo "Secure Decentralized Identity Channels for Edge Gateways" (*Journal of Intelligent Systems*, 2025).
