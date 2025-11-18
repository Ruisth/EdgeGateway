# Arquitetura DIDComm do Edge Gateway

Especifica o subsistema DIDComm alinhado ao paper `EdgeGateway_Paper.pdf`, aos padrões DIDComm v2 e às referências de identidade descentralizada utilizadas no projeto.

## Objetivos
- **Mensageria segura** entre Edge Gateway e Digital Twin (provisionamento, telemetria crítica, comandos).
- **Gestão de DIDs** com chaves X25519/Ed25519 guardadas em TPM/HSM quando disponível.
- **Políticas governadas por smart contracts** (convites, revogações, rotação de chaves, auditoria).
- **Compatibilidade DIDComm v2** para interoperar com agentes externos e redes SSI.

## Componentes
| Componente | Descrição | Stack atual |
| --- | --- | --- |
| Edge DIDComm Agent | Residente no gateway; encapsula chaves, sessões e API local (REST/gRPC). | FastAPI + libsodium (protótipo em `services/didcomm-agent/`). |
| Twin DIDComm Agent | Executa na nuvem, espelhando o Digital Twin e integrando contratos inteligentes. | Python/FastAPI provisório; alvo é container K8s. |
| Resolver de DIDs | Consulta diretórios locais, contratos blockchain ou serviços externos. | Modo in-memory + sincronização eventual com ledger. |
| Bridge MQTT/DIDComm | Opcional; consome tópicos internos e publica envelopes assinados. | A definir conforme caso de uso. |
| Observabilidade | Métricas/Logs protegidos (ID pseudonimizados). | Prometheus + Fluent Bit. |

## Fluxo de estabelecimento do canal
1. `create_invitation()` – Edge gera DID, endpoint e chave pública temporária.
2. `accept_invitation()` – Twin responde com DID/endpoint/chave e políticas exigidas.
3. `store_peer()` – ambas as partes registram o par e sincronizam no ledger (opcional).
4. `pack_encrypted()`/`unpack()` – troca de envelopes criptografados para telemetria/comandos.
5. Rotação automática de chaves com base em contagem de mensagens, tempo ou eventos de segurança.

## Fluxos de erro
- **Falha de validação**: rejeitar convite/mensagem, registrar evento e notificar serviço de governança.
- **Twin indisponível**: enfileirar mensagens localmente (persistência opcional) com assinatura e contador.
- **Revogação**: smart contract sinaliza DIDs inválidos; agentes encerram sessões e limpam chaves.

## Segurança
- Chaves privadas no TPM quando suportado; fallback criptografado em disco usando libsodium (XChaCha20-Poly1305).
- AAD inclui IDs do remetente/destinatário e versão do contrato para impedir replay cross-context.
- Logs mascaram conteúdos sensíveis, preservando apenas hashes/IDs para auditoria.
- Testes de rotação de chaves devem ser automatizados (pipeline CI/CD) e executados ao menos semanalmente.

## Integração com smart contracts
1. Registro e revogação de convites.
2. Emissão de tokens efêmeros para APIs HTTP do agente.
3. Armazenamento de trilhas de auditoria (hash dos envelopes + timestamp).

## Próximas evoluções
- Suporte a DIDComm Routing (mediadores) para múltiplos Twins ou domínios.
- Assinatura/transferência de anexos binários (modelos IA, pacotes OTA).
- CLI para operações administrativas (listar pares, forçar rotação, exportar logs).
- Receitas Yocto para empacotar o agente como serviço do sistema.

> Última revisão: 2025-11-18

