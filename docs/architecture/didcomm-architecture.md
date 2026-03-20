# DIDComm Architecture

Conceptual architecture for the DIDComm agent used by the Edge Gateway.

## Objectives
- Provide secure agent-to-agent messaging between the Edge Gateway and services (cloud or peer devices).
- Support key rotation, authentication and authorisation tied to blockchain identities.
- Offer a reference implementation using FastAPI + libsodium.

## Components
| Component | Function | Notes |
| --- | --- | --- |
| DID Document store | Persists DIDs, verification methods and service endpoints | Can mirror to blockchain for auditability. |
| Key management | X25519 keypairs stored in TPM/HSM; rotation policies enforced | Enrolment via out-of-band channel. |
| Messaging API | REST/gRPC interface for sending/receiving DIDComm messages | Backed by persistent queue for retries. |
| Crypto layer | ChaCha20-Poly1305 for authenticated encryption | Implement double-ratchet for session security. |
| Policy engine | Maps identities to permissions (topics, commands, OTA) | Policies anchored to smart contracts. |

## Message lifecycle (example)
1. Device enrols and publishes DID document to the Edge Gateway agent.
2. Edge Gateway fetches peer DID, derives shared secret (X25519) and establishes a session.
3. Encrypted payload is placed on the event bus with metadata for routing.
4. Recipient agent decrypts, validates policy and forwards to the target service.

## Threat model considerations
- Protect private keys with hardware (TPM/HSM) and restrict export.
- Enforce mutual authentication on every channel (mTLS + DID signature).
- Rate-limit message ingress to mitigate DoS and replay buffers.
- Log all key rotations and policy changes for blockchain anchoring.

## Implementation references
- Code: `services/didcomm-agent/` (FastAPI, PyNaCl/libsodium).
- Example: `services/didcomm-agent/examples/demo_exchange.py`.
- Tests: `services/didcomm-agent/tests/`.

> Last reviewed: 2025-11-18
