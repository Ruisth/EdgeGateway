# Fluxos de Comunicação e Dados do Edge Gateway

Adaptação prática dos fluxos descritos no `EdgeGateway_Paper.pdf`. Use como guia para implementar integrações entre dispositivos IoT, serviços de IA local, nuvem e blockchain/Digital Twin.

## Camadas de conectividade
| Camada | Protocolos | Responsabilidades |
| --- | --- | --- |
| Campo | Modbus, OPC-UA, BLE, Zigbee, Thread, Wi-Fi, 5G/LTE | Coletores e adaptadores convertem dados para JSON/Avro. |
| Barramento interno | MQTT + fila persistente (RabbitMQ/NATS JetStream) | Segrega tópicos por domínio: telemetria, comandos, eventos do gêmeo. |
| Edge Service Mesh | sidecars com mTLS, descoberta e políticas | Expõe APIs REST/gRPC para IA, armazenamento e sincronização. |
| Canais externos | TLS 1.3, VPN, QUIC, DIDComm encapsulado | Conecta nuvem e validadores blockchain, com QoS/latência controlados. |

## Pipeline de dados
1. **Ingestão** – adaptadores publicam no broker MQTT usando QoS alinhado à criticidade.
2. **Normalização** – funções de stream processing convertem unidades, enriquecem metadados e validam esquemas.
3. **Inferência local** – modelos embarcados (TensorFlow Lite/ONNX Runtime) geram decisões/predições.
4. **Ação local** – controladores escrevem comandos no barramento ou ajustam políticas do gateway.
5. **Persistência & sincronização** – deltas relevantes seguem para o Digital Twin (smart contracts) e data lakes autorizados.

## Políticas de QoS e latência
| Fluxo | QoS MQTT | Latência alvo | Observações |
| --- | --- | --- | --- |
| Telemetria crítica (sensores de segurança) | 1 ou 2 | < 200 ms | Replicação ativa-passiva e janela de reenvio garantida. |
| Comandos de atuação | 2 | < 150 ms | Confirmar recibo antes de aplicar. |
| Eventos de governança (Twin) | 1 | < 5 s | Podem ser agregados antes do envio ao ledger. |
| Telemetria não crítica | 0 | Best effort | Pode ser filtrada localmente. |

## Segurança e resiliência
- Certificados e tokens emitidos pelo módulo TPM e smart contracts; chaves pairwise DIDComm com rotação programada.
- Sidecars validam políticas assinadas no ledger antes de liberar tráfego para cada domínio.
- Broker MQTT configurado com autenticação mTLS e ACLs baseadas em claims.
- Checkpoints de inferência e filas persistentes garantem retomada após falhas.

## Observabilidade
- Métricas: throughput por tópico, latência P50/P95, falhas de entrega, número de envelopes DIDComm processados.
- Logs estruturados com correlação (trace/span ID) e tags de dispositivo/DID.
- Dashboards recomendados: ingestão vs. ação local, saúde do broker, backlog de sincronização do Twin.

## Próximos passos
1. Criar diagramas sequence/PlantUML nesta pasta (`communication-flow.puml`).
2. Definir contratos JSON Schema/Avro para os principais tópicos (telemetria crítica, comandos, auditoria).
3. Automatizar testes de carga focados em MQTT (por exemplo, `locust` ou `mqtt-stresser`).
4. Documentar procedimentos de failover para cada camada (broker, mesh, canais externos).

> Última revisão: 2025-11-18

