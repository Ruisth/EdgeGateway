"""Handler de protocolo para Enrollment VC (UC1).

Gere o fluxo de inscricao de um OEM no consorcio C2DTA:
1. Consorcio (1@C) cria convite OOB com goal code ENROLL_OEM
2. OEM (1@O) aceita convite e estabelece conexao DIDComm
3. Consorcio propoe Enrollment VC ao OEM
4. OEM submete provas documentais
5. Consorcio emite Enrollment VC

Ver paper Seccao 3.2.1 — OEM Enrollment.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


async def handle_enrollment_request(
    admin_url: str,
    connection_id: str,
    organization_name: str,
    organization_did: str,
    consortium_id: str = "c2dta-default",
) -> dict[str, Any]:
    """Processa um pedido de enrollment e retorna os dados da VC proposta.

    Este handler e invocado pelo EGW Controller quando deteta o goal code
    ENROLL_OEM numa conexao DIDComm recebida.
    """
    credential_proposal = {
        "connection_id": connection_id,
        "filter": {
            "indy": {
                "schema_name": "EnrollmentCredential",
                "schema_version": "1.0",
            }
        },
        "credential_preview": {
            "@type": "issue-credential/2.0/credential-preview",
            "attributes": [
                {"name": "organization_name", "value": organization_name},
                {"name": "organization_did", "value": organization_did},
                {"name": "role", "value": "OEM"},
                {"name": "enrollment_date", "value": datetime.now(UTC).isoformat()},
                {"name": "consortium_id", "value": consortium_id},
                {"name": "expiry_date", "value": ""},
            ],
        },
    }

    logger.info(
        "Enrollment VC proposta para %s (connection=%s)",
        organization_name,
        connection_id,
    )
    return credential_proposal
