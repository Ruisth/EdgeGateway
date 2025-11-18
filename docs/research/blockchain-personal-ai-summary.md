# Notas de Pesquisa: Blockchain-powered Personal AI

Resumo das referências utilizadas para IA pessoal com governança em blockchain.

## Tópicos principais
- **Identidade descentralizada (DID/VC)** – autenticação de usuários/dispositivos e consentimento.
- **Gêmeo digital orientado a contratos inteligentes** – representação auditável do usuário e dos ativos.
- **Governança de dados** – políticas de consentimento, rastreabilidade e monetização de dados.
- **Interoperabilidade** – padrões para cruzar múltiplas redes blockchain e serviços de IA.

## Relação com o Edge Gateway
| Necessidade | Solução proposta | Referências |
| --- | --- | --- |
| Guardião local de dados | Gateway aplica políticas antes de enviar dados ao Twin | Paper principal + W3C DID/VC. |
| Inferência privada | Modelos locais reduzem exposição e permitem respostas de baixa latência | Estudos sobre TinyML e Federated Learning citados no PDF. |
| Auditoria imutável | Logs/métricas sincronizados com o ledger para trilhas de auditoria | Hyperledger Fabric, PolygonID, entre outros. |

## Próximos passos de pesquisa
1. Mapear requisitos legais (LGPD/GDPR) para controles técnicos específicos (tokenização, anonimização).
2. Prototipar smart contracts para consentimento, monetização e revogação.
3. Integrar ferramentas de análise de risco e detecção de anomalias (AI/ML + blockchain).
4. Registrar bibliografia utilizando padrão ABNT/APA nesta pasta (`references.bib`).

## Referências iniciais
1. W3C. *Decentralized Identifiers (DIDs) v1.0*, 2022.
2. W3C. *Verifiable Credentials Data Model v1.1*, 2022.
3. Hyperledger Foundation. *Hyperledger Fabric Architecture Reference*, 2024.
4. Polygon Labs. *Polygon ID: Architecture Overview*, 2024.
5. Smith, J. et al. *Secure Decentralized Identity Channels for Edge Gateways*. Journal of Intelligent Systems, 2025.

> Última revisão: 2025-11-18

