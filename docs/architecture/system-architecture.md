# Edge Gateway System Architecture

This document consolidates the macro view, components and non-functional requirements of the Edge Gateway described in `EdgeGateway_Paper.pdf`. It serves as a reference for engineering decisions and must stay aligned with experiments conducted in the lab and in the field.

## Macro view
1. **IoT devices** – industrial and residential sensors, actuators, wearables and legacy controllers.
2. **Edge Gateway** – Linux platform (Yocto) with support for OCI containers, AI accelerators and TPM.
3. **Digital Twin + Blockchain** – smart contracts that store identities, policies and audit data.
4. **Cloud/Laboratory** – heavy AI pipelines, dashboards and corporate integrations.

```
+-------------+        +-----------------+        +-------------------+
| IoT         |<-----> | Edge Gateway    |<-----> | Digital Twin /    |
| devices     |        | (Yocto + OCI)   |        | Blockchain + Cloud|
+-------------+        +-----------------+        +-------------------+
```

## Core modules
| Module | Responsibilities | Notes |
| --- | --- | --- |
| Connectivity management | Drivers, industrial/residential adapters, secure routing | Integrate Modbus, OPC-UA, BLE, Thread, Wi-Fi 6/6E and 5G/LTE protocols. |
| Event bus | MQTT/AMQP + persistent queues | Configurable QoS, topics segregated by logical domain and retry queue integration. |
| AI layer | Local inference (TensorFlow Lite/ONNX Runtime) with accelerators (GPU/NPU) | Versioned models with OTA updates; checkpoints for resumption. |
| Container orchestration | Container engine (Docker/Podman) + supervisor system (k3s, systemd, supervisord) | Must support atomic updates and rollback. |
| Blockchain synchronisation | Agents that sign transactions, update the Digital Twin and expose APIs | Integrates DIDComm and smart contracts for governance. |
| Observability and DevSecOps | Telemetry (Prometheus), structured logs, tracing, OTA | Integrates with CI/CD and security policies derived from the ledger. |

## Cross-cutting requirements
- **Security**: secure boot, disk encryption, certificate management via TPM/HSM, mTLS on all services and automatic key rotation policies.
- **Reliability**: software/hardware watchdogs, A/B updates (swupdate or Mender), self-healing detection and resource usage limits.
- **Remote management**: APIs for provisioning, configuration, inventory collection and controlled OTA updates.
- **Compliance**: adherence to LGPD/GDPR with selective retention and audit trails signed on the blockchain.

## Performance criteria
| Metric | Initial target | Notes |
| --- | --- | --- |
| Inference latency | < 100 ms for critical models | Measured from MQTT event to command applied. |
| Broker availability | >= 99.5% | Requires active/passive replication and fault detection. |
| Twin synchronisation time | < 5 s for critical states | Depends on the SLA of the chosen blockchain. |
| Maximum CPU consumption | < 75% in nominal operation | Ensures headroom for bursts and OTA. |

## Technical roadmap (high level)
1. **BSP and hardware** – validate support for TPM, AI acceleration and connectivity (Roadmap Phase 0).
2. **Yocto base** – consolidate `meta-edgegateway`, configure `edgegateway-image` and automate builds.
3. **CI/CD pipelines** – run integration tests for containers, inference and smart contracts.
4. **Observability** – instrument metrics/log/tracing and connect dashboards.
5. **Living documentation** – keep PlantUML/Draw.io diagrams in `docs/architecture/diagrams/` (to be created) under version control.

## Document update checklist
- [ ] Diagram updated after each significant structural change.
- [ ] Metrics table reviewed when new SLAs are defined.
- [ ] Links to architectural decisions recorded in `docs/adr/` (to be created).

> Last reviewed: 2025-11-18
