# Communication and Dataflow

Blueprint for how the Edge Gateway routes data between IoT devices, local services and the blockchain-backed Digital Twin.

## Data sources and sinks
- Sensors/actuators: MQTT/AMQP, Modbus, OPC-UA, BLE, Thread, Wi-Fi 6/6E, 5G/LTE.
- Embedded AI pipelines: containers with TensorFlow Lite or ONNX Runtime.
- Digital Twin and blockchain: smart contracts storing identities, policies and audit trails.
- Cloud/laboratory: dashboards, heavy training pipelines, corporate integrations.

## Message flows
1. Device publishes raw telemetry via MQTT → queued with QoS.
2. Edge service enriches/normalises payloads → routes to inference pipeline.
3. Inference result triggers actuation and updates the Digital Twin via blockchain agent.
4. Cloud dashboards subscribe to curated topics; sensitive data remains local unless policies allow replication.

```text
[Sensor] --MQTT--> [Event bus] --Filter/Normalise--> [AI pipeline] --Result--> [Actuator]
                                                           |                     |
                                                           v                     v
                                                  [Blockchain agent]      [Digital Twin]
```

## QoS and routing rules
- Use topic namespaces per logical domain (e.g. `factory/line1/*`, `home/living-room/*`).
- Retain messages where replay is essential; expire transient topics quickly.
- Apply backpressure with persistent queues for critical paths.
- Isolate tenant domains with authentication and authorisation tied to the blockchain identity layer.

## Reliability and resilience
- Watchdogs and health checks for brokers and AI containers.
- A/B updates with rollback for the MQTT broker and blockchain agent containers.
- Offline-first: buffer telemetry locally and reconcile with the Digital Twin when connectivity returns.

## Security controls
- mTLS for all services; certificates anchored in TPM/HSM.
- Encrypted storage for persistent queues and AI artefacts.
- DIDComm used for secure agent-to-agent messaging and key rotation.
- Audit events signed and anchored to the blockchain ledger.

> Last reviewed: 2025-11-18
