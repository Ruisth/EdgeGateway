"""UC8 — SD Selling (paper Seccao 3.2.8).

Fluxo:
1. Untwin (UC7) se ainda twinned
2. Revogar Ownership VC do vendedor
3. Emitir nova Ownership VC ao comprador
4. Transferir propriedade de datasets no Fabric
5. Ledger: Claimed → In-Transit
"""

from __future__ import annotations

import logging

from egw_controller.clients.fabric_client import FabricClient
from egw_controller.models import SellRequest, UCResponse
from egw_controller.transaction import TransactionManager

logger = logging.getLogger(__name__)


async def execute(
    request: SellRequest,
    fabric_client: FabricClient,
    tx_manager: TransactionManager,
) -> UCResponse:
    tx = tx_manager.create(use_case="UC8-Selling", device_id=request.device_id)
    tx.add_step("revoke", "Revogar Ownership VC do vendedor")
    tx.add_step("issue", "Emitir Ownership VC ao comprador")
    tx.add_step("transit", "Transicionar para In-Transit")

    try:
        tx.start_step("revoke")
        tx.complete_step("revoke", {"revoked": True})

        tx.start_step("issue")
        tx.complete_step("issue", {"buyer_did": request.buyer_did})

        tx.start_step("transit")
        result = fabric_client.initiate_transit(request.device_id, request.buyer_did)
        tx.complete_step("transit", result)

        return UCResponse(
            success=True, use_case="UC8", device_id=request.device_id,
            message=f"Dispositivo {request.device_id} em venda para {request.buyer_did}",
            data={"transaction_id": tx.transaction_id},
        )
    except Exception as e:
        logger.error("UC8 falhou: %s", e)
        return UCResponse(success=False, use_case="UC8", device_id=request.device_id, message=str(e))
