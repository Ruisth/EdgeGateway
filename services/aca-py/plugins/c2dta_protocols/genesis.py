"""Handler de protocolo para Genesis VC (UC3).

Gere o fluxo de emissao de Genesis VC durante o auto-registo de dispositivos:
1. Dispositivo (EGW/SD) arranca e gera identidade (DID publico / UUID)
2. Dispositivo conecta-se ao agente OEM via DIDComm
3. OEM propoe Genesis VC ao dispositivo
4. OEM emite Genesis VC

Ver paper Seccao 3.2.3 — Device Self-Registration.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


async def handle_genesis_request(
    connection_id: str,
    device_uuid: str,
    model_id: str,
    manufacturer_did: str,
    firmware_version: str = "1.0.0",
    wot_td_hash: str = "",
    serial_number: str = "",
) -> dict[str, Any]:
    """Cria a proposta de Genesis VC para um dispositivo."""
    credential_proposal = {
        "connection_id": connection_id,
        "filter": {
            "indy": {
                "schema_name": "GenesisCredential",
                "schema_version": "1.0",
            }
        },
        "credential_preview": {
            "@type": "issue-credential/2.0/credential-preview",
            "attributes": [
                {"name": "device_uuid", "value": device_uuid},
                {"name": "model_id", "value": model_id},
                {"name": "manufacturer_did", "value": manufacturer_did},
                {"name": "manufacture_date", "value": datetime.now(UTC).isoformat()},
                {"name": "firmware_version", "value": firmware_version},
                {"name": "wot_td_hash", "value": wot_td_hash},
                {"name": "serial_number", "value": serial_number},
            ],
        },
    }

    logger.info("Genesis VC proposta para dispositivo %s (connection=%s)", device_uuid, connection_id)
    return credential_proposal
