"""UC7 — SD Untwinning (paper Seccao 3.2.7)."""

from __future__ import annotations

import logging

from egw_controller.clients.ditto_client import DittoClient
from egw_controller.clients.fabric_client import FabricClient
from egw_controller.models import UCResponse, UntwinRequest
from egw_controller.transaction import TransactionManager

logger = logging.getLogger(__name__)


async def execute(
    request: UntwinRequest,
    ditto_client: DittoClient,
    fabric_client: FabricClient,
    tx_manager: TransactionManager,
) -> UCResponse:
    tx = tx_manager.create(use_case="UC7-Untwinning", device_id=request.device_id)
    tx.add_step("stop", "Parar streaming MQTT")
    tx.add_step("ditto", "Remover Digital Twin do Ditto")
    tx.add_step("ledger", "Transicionar para Claimed no ledger")

    thing_id = f"org.c2dta:{request.device_id}"

    try:
        tx.start_step("stop")
        tx.complete_step("stop", {"streaming": "stopped"})

        tx.start_step("ditto")
        ditto_client.delete_thing(thing_id)
        tx.complete_step("ditto", {"thing_id": thing_id, "deleted": True})

        tx.start_step("ledger")
        result = fabric_client.untwin_device(request.device_id)
        tx.complete_step("ledger", result)

        return UCResponse(
            success=True, use_case="UC7", device_id=request.device_id,
            message=f"Dispositivo {request.device_id} untwinned",
            data={"transaction_id": tx.transaction_id},
        )
    except Exception as e:
        logger.error("UC7 falhou: %s", e)
        return UCResponse(success=False, use_case="UC7", device_id=request.device_id, message=str(e))
