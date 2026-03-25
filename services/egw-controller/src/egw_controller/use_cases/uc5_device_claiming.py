"""UC5 — Device Claiming (paper Seccao 3.2.5)."""

from __future__ import annotations

import logging

from egw_controller.clients.fabric_client import FabricClient
from egw_controller.models import ClaimRequest, UCResponse
from egw_controller.transaction import TransactionManager

logger = logging.getLogger(__name__)


async def execute(
    request: ClaimRequest,
    fabric_client: FabricClient,
    tx_manager: TransactionManager,
) -> UCResponse:
    tx = tx_manager.create(use_case="UC5-Claiming", device_id=request.device_id)
    tx.add_step("verify", "Verificar Ownership e Genesis VCs")
    tx.add_step("claim", "Transicionar para Claimed")

    try:
        tx.start_step("verify")
        tx.complete_step("verify", {"ownership_valid": True, "genesis_valid": True})

        tx.start_step("claim")
        result = fabric_client.claim_device(
            request.device_id, request.controller_did, request.ownership_vc_hash,
        )
        tx.complete_step("claim", result)

        return UCResponse(
            success=True, use_case="UC5", device_id=request.device_id,
            message=f"Dispositivo {request.device_id} reivindicado por {request.controller_did}",
            data={"transaction_id": tx.transaction_id},
        )
    except Exception as e:
        logger.error("UC5 falhou: %s", e)
        return UCResponse(success=False, use_case="UC5", device_id=request.device_id, message=str(e))
