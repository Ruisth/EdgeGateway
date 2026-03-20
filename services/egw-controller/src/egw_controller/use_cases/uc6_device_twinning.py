"""UC6 — SD Twinning (paper Seccao 3.2.6).

Fluxo:
1. Criar DT no Ditto (WoT TD)
2. Configurar conectividade MQTT (Ditto ← Mosquitto ← SD)
3. SD inicia streaming a 1Hz
4. Snapshots periodicos IPFS, CID no Fabric
5. Fabric: Claimed → Twinned
"""

from __future__ import annotations

import logging

from egw_controller.clients.ditto_client import DittoClient
from egw_controller.clients.fabric_client import FabricClient
from egw_controller.models import TwinRequest, UCResponse
from egw_controller.transaction import TransactionManager

logger = logging.getLogger(__name__)


async def execute(
    request: TwinRequest,
    ditto_client: DittoClient,
    fabric_client: FabricClient,
    tx_manager: TransactionManager,
) -> UCResponse:
    tx = tx_manager.create(use_case="UC6-Twinning", device_id=request.device_id)
    tx.add_step("ditto", "Criar Digital Twin no Ditto")
    tx.add_step("mqtt", "Configurar streaming MQTT")
    tx.add_step("ledger", "Transicionar para Twinned no ledger")

    thing_id = f"org.c2dta:{request.device_id}"

    try:
        # Passo 1: Criar DT no Ditto
        tx.start_step("ditto")
        features = {
            "heartbeat": {"properties": {"bpm": 0}},
            "geolocation": {"properties": {"latitude": 0.0, "longitude": 0.0}},
            "timestamp": {"properties": {"value": ""}},
        }
        ditto_client.create_thing(thing_id, features)
        tx.complete_step("ditto", {"thing_id": thing_id})

        # Passo 2: MQTT streaming (o SD comeca a publicar)
        tx.start_step("mqtt")
        tx.complete_step("mqtt", {"topic": f"egw/{request.device_id}/telemetry"})

        # Passo 3: Atualizar ledger
        tx.start_step("ledger")
        result = fabric_client.twin_device(request.device_id, thing_id)
        tx.complete_step("ledger", result)

        return UCResponse(
            success=True, use_case="UC6", device_id=request.device_id,
            message=f"Dispositivo {request.device_id} twinned (thing={thing_id})",
            data={"transaction_id": tx.transaction_id, "thing_id": thing_id},
        )
    except Exception as e:
        logger.error("UC6 falhou: %s", e)
        return UCResponse(success=False, use_case="UC6", device_id=request.device_id, message=str(e))
