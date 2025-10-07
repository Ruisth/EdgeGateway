# Fluxos de comunicação e dados do Edge Gateway

Este documento adapta os fluxos descritos no *EdgeGateway_Paper.pdf* para orientar a implementação.
Ele detalha como os componentes do gateway interagem com dispositivos IoT, serviços de IA e a
blockchain que mantém o Digital Twin.

## Camadas de conectividade
1. **Camada de campo** – protocolos como Modbus, OPC-UA, BLE e Zigbee. Os dados são convertidos
   para um formato interno (JSON/Avro) por adaptadores executados em containers leves.
2. **Barramento de mensagens interno** – broker MQTT com tópicos segregados por domínio lógico
   (telemetria, comandos, eventos de gêmeo digital). Uma fila persistente complementa o broker
   para garantir entrega após falhas.
3. **Edge Service Mesh** – sidecars tratam descoberta, mTLS e políticas derivadas do ledger. Eles
   expõem APIs REST/gRPC para microsserviços responsáveis por IA, armazenamento e sincronização.
4. **Canais externos** – conexões seguras (TLS 1.3, VPN ou QUIC) para a nuvem e para nós
   validadores da blockchain. Para o intercâmbio com o Digital Twin é estabelecida uma sessão
   DIDComm par-a-par, encapsulada nesses túneis quando necessário.

## Pipeline de dados
1. **Ingestão**: adaptadores coletam dados e publicam no broker MQTT.
2. **Normalização**: serviços de stream process convertem unidades, aplicam filtros e geram
   eventos com metadados de qualidade.
3. **Inferência**: modelos embarcados (TensorFlow Lite, ONNX Runtime) consomem eventos e produzem
   decisões ou previsões.
4. **Ação local**: controladores escrevem comandos de volta aos dispositivos ou ajustam políticas
   do gateway.
5. **Persistência e sincronização**: apenas estados relevantes são enviados ao Digital Twin via
   smart contracts, enquanto dados brutos são encaminhados a data lakes quando permitido. O
   tráfego operacional sensível usa envelopes DIDComm encriptados antes de atingir o ledger ou
   qualquer serviço cloud.

## Considerações operacionais
- **QoS e latência**: use QoS 1 ou 2 no MQTT para eventos críticos e defina filas de prioridade.
- **Segurança**: certifique-se de que todos os tópicos críticos exigem certificados gerenciados
   pelo módulo TPM. Tokens efêmeros são emitidos pelos contratos inteligentes. Para mensagens
   DIDComm, valide a rotação de chaves pairwise e sincronize revogações com o ledger.
- **Resiliência**: configure replicação ativa-passiva do broker e mantenha checkpoints de inferência
  para recuperação rápida.
- **Compliance**: aplique políticas de retenção descritas no paper, garantindo anonimização antes
   de enviar dados sensíveis à nuvem. Metadados DIDComm devem ser agregados com identificadores
   pseudonimizados para fins de auditoria.

## Próximos passos
- Modelar diagramas sequence/PlantUML baseados neste texto.
- Codificar testes de carga focados nos tópicos MQTT críticos.
- Automatizar validações de esquema usando JSON Schema ou Avro IDL.
