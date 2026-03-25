# Notes on Blockchain for Personal AI

Concise notes linking personal AI use cases with blockchain and DIDComm patterns.

## Use case drivers
- Data ownership and selective sharing with verifiable consent.
- Low-latency inference near the user, with optional cloud offload.
- Auditability of model updates and policy changes.
- Secure identity and messaging across devices and services.

## Blockchain/DIDComm angles
- Use smart contracts to encode consent policies and data retention windows.
- DIDComm for secure peer-to-peer messaging and key rotation.
- Token-based incentives for sharing model updates or federated learning contributions.
- Anchoring audit logs to a tamper-evident ledger for compliance.

## Open research questions
- Best balance between on-chain anchoring and off-chain storage for telemetry.
- How to measure privacy leakage when combining local inference with selective replication.
- Impact of intermittent connectivity on DIDComm session management.
- Regulatory alignment (GDPR/LGPD) when personal AI models are shared across jurisdictions.

> Last reviewed: 2025-11-18
