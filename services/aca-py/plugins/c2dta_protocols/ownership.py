"""Handler de protocolo para Ownership VC (UC4/UC5/UC8).

Gere o fluxo de emissao e transferencia de Ownership VCs:
- UC4: OEM emite Ownership VC ao consumidor apos compra
- UC5: EGW valida Ownership VC durante claiming
- UC8: EGW revoga e re-emite Ownership VC durante venda

Ver paper Seccoes 3.2.4, 3.2.5, 3.2.8.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


async def handle_ownership_issuance(
    connection_id: str,
    device_uuid: str,
    owner_did: str,
    previous_owner_did: str = "",
    transfer_tx_hash: str = "",
) -> dict[str, Any]:
    """Cria a proposta de Ownership VC para um consumidor."""
    credential_proposal = {
        "connection_id": connection_id,
        "filter": {
            "indy": {
                "schema_name": "OwnershipCredential",
                "schema_version": "1.0",
            }
        },
        "credential_preview": {
            "@type": "issue-credential/2.0/credential-preview",
            "attributes": [
                {"name": "device_uuid", "value": device_uuid},
                {"name": "owner_did", "value": owner_did},
                {"name": "acquisition_date", "value": datetime.now(timezone.utc).isoformat()},
                {"name": "previous_owner_did", "value": previous_owner_did},
                {"name": "transfer_tx_hash", "value": transfer_tx_hash},
            ],
        },
    }

    logger.info("Ownership VC proposta para %s, dispositivo %s", owner_did, device_uuid)
    return credential_proposal


async def handle_ownership_verification(
    connection_id: str,
    device_uuid: str,
) -> dict[str, Any]:
    """Cria um pedido de prova de Ownership VC (UC5 — claiming)."""
    proof_request = {
        "connection_id": connection_id,
        "proof_request": {
            "name": "Ownership Verification",
            "version": "1.0",
            "requested_attributes": {
                "ownership_attrs": {
                    "names": ["device_uuid", "owner_did", "acquisition_date"],
                    "restrictions": [
                        {"schema_name": "OwnershipCredential", "schema_version": "1.0"}
                    ],
                }
            },
            "requested_predicates": {},
        },
    }

    logger.info("Prova de Ownership solicitada para dispositivo %s", device_uuid)
    return proof_request
