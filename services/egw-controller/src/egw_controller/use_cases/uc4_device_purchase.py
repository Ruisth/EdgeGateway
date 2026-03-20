"""UC4 — Consumer Buys Device (paper Seccao 3.2.4)."""

from __future__ import annotations

import logging

from egw_controller.clients.fabric_client import FabricClient
from egw_controller.models import PurchaseRequest, UCResponse
from egw_controller.transaction import TransactionManager

logger = logging.getLogger(__name__)


async def execute(
    request: PurchaseRequest,
    fabric_client: FabricClient,
    tx_manager: TransactionManager,
) -> UCResponse:
    tx = tx_manager.create(use_case="UC4-Purchase", device_id=request.device_id)
    tx.add_step("transit", "Transicionar para In-Transit")

    try:
        tx.start_step("transit")
        result = fabric_client.initiate_transit(request.device_id, request.buyer_did)
        tx.complete_step("transit", result)

        return UCResponse(
            success=True, use_case="UC4", device_id=request.device_id,
            message=f"Dispositivo {request.device_id} em transito para {request.buyer_did}",
            data={"transaction_id": tx.transaction_id},
        )
    except Exception as e:
        logger.error("UC4 falhou: %s", e)
        return UCResponse(success=False, use_case="UC4", device_id=request.device_id, message=str(e))
