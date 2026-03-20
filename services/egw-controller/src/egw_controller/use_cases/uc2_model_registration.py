"""UC2 — Device Model Registration (paper Seccao 3.2.2).

Fluxo:
1. OEM solicita action menu ao consorcio
2. OEM submete informacao do modelo (nome, descricao, WoT TD)
3. Consorcio regista modelo no ecosystem ledger (Fabric)
4. Consorcio armazena WoT TD no source control
"""

from __future__ import annotations

import logging

from egw_controller.clients.fabric_client import FabricClient
from egw_controller.models import ModelRegistrationRequest, UCResponse
from egw_controller.transaction import TransactionManager

logger = logging.getLogger(__name__)


async def execute(
    request: ModelRegistrationRequest,
    fabric_client: FabricClient,
    tx_manager: TransactionManager,
) -> UCResponse:
    """Executa o UC2 — Device Model Registration."""
    tx = tx_manager.create(use_case="UC2-Model-Registration")
    tx.add_step("ledger", "Registar modelo no ecosystem ledger")

    try:
        tx.start_step("ledger")
        result = fabric_client.register_device_model(
            model_id=request.model_id,
            manufacturer=request.manufacturer,
            wot_td_hash=request.wot_td_hash,
        )
        tx.complete_step("ledger", result)

        return UCResponse(
            success=True,
            use_case="UC2",
            message=f"Modelo {request.model_id} registado",
            data={"transaction_id": tx.transaction_id},
        )
    except Exception as e:
        logger.error("UC2 falhou: %s", e)
        return UCResponse(success=False, use_case="UC2", message=str(e))
