# Notas de pesquisa: Blockchain-powered Personal AI

Embora o foco esteja no *EdgeGateway_Paper.pdf*, este resumo complementa referências sobre IA
pessoal e blockchain utilizadas no projeto.

## Tópicos principais
- **Identidade descentralizada**: uso de DID/VC para autenticação de usuários e dispositivos.
- **Gêmeo digital**: representação do usuário e de ativos físicos como contratos inteligentes.
- **Governança de dados**: políticas de consentimento e rastreabilidade auditadas no ledger.
- **Interoperabilidade**: padrões para integrar múltiplas redes blockchain e serviços de IA.

## Relação com o Edge Gateway
- O gateway atua como guardião dos dados, aplicando políticas antes de enviar informações ao
  Digital Twin.
- A inferência local reduz exposição de dados sensíveis e garante respostas em tempo real.
- Logs e métricas sincronizados com o ledger fornecem trilhas de auditoria imutáveis.

## Próximos passos
- Mapear requisitos legais (LGPD/GDPR) a controles técnicos do gateway.
- Prototipar smart contracts específicos para consentimento e monetização de dados.
- Integrar ferramentas de análise de risco e detecção de anomalias.
