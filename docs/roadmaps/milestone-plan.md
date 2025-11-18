# Milestone plan for the Edge Gateway

High-level phases to align the Yocto image, DIDComm agent and blockchain integration.

## Phase 0 – Foundation
- Select target hardware (TPM, AI accelerator, connectivity matrix).
- Pull BSP layers and validate boot + secure boot chain.
- Define compliance requirements (GDPR/LGPD) and logging/audit scope.

## Phase 1 – Core platform
- Stabilise `meta-edgegateway` with container runtime, MQTT broker and OTA base.
- Package initial blockchain/DIDComm agents and expose health endpoints.
- Set up CI for BitBake linting and container image scans.

## Phase 2 – Observability and governance
- Add Prometheus exporters, log pipeline and tracing for core services.
- Implement policy engine linked to smart contracts for data access and OTA.
- Create rollback procedures and chaos tests for connectivity/interference.

## Phase 3 – Pilot and audit readiness
- Deploy to lab devices; measure inference latency and broker availability.
- Run security assessments (TLS posture, key management, firmware integrity).
- Prepare audit artefacts and documentation for regulators/stakeholders.

> Keep updating this plan alongside `docs/architecture/` diagrams and ADRs.
> Last reviewed: 2025-11-18
