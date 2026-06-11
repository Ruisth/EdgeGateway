"""UC3 — Device Self-Registration (paper Seccao 3.2.3).

Fluxo EGW:
1. EGW arranca e gera DID publico (primeiro boot)
2. EGW conecta-se ao OEM via DIDComm
3. OEM propoe e emite Genesis VC
4. OEM regista dispositivo no ecosystem ledger (Manufactured → Available)

Fluxo SD:
1. SD arranca e gera UUID (primeiro boot)
2. SD conecta-se ao OEM via DIDComm (mediado pelo EGW)
3. OEM propoe e emite Genesis VC
4. OEM regista SD no ecosystem ledger
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime

from egw_controller.clients.aca_py_client import AcaPyClient
from egw_controller.clients.fabric_client import FabricClient
from egw_controller.models import DeviceRegistrationRequest, UCResponse
from egw_controller.transaction import TransactionManager

logger = logging.getLogger(__name__)


def _genesis_vc_hash(credential: dict) -> str:
    """SHA-256 sobre o JSON canonico da credencial (chaves ordenadas)."""
    canonical = json.dumps(credential, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


async def execute(
    request: DeviceRegistrationRequest,
    oem_client: AcaPyClient,
    fabric_client: FabricClient,
    tx_manager: TransactionManager,
) -> UCResponse:
    """Executa o UC3 — Device Self-Registration."""
    tx = tx_manager.create(use_case="UC3-Device-Registration", device_id=request.device_id)
    tx.add_step("identity", "Gerar identidade do dispositivo")
    tx.add_step("genesis", "Emitir Genesis VC")
    tx.add_step("ledger", "Registar no ecosystem ledger")
    tx.add_step("available", "Transicionar para Available")

    try:
        # Passo 1: Identidade
        tx.start_step("identity")
        tx.complete_step("identity", {"device_id": request.device_id, "type": request.device_type.value})

        # Passo 2: Genesis VC — o hash ancorado no ledger e o SHA-256 do
        # conteudo canonico da credencial (emissao ACA-Py real pendente;
        # ver docs/reviews/repo-improvement-plan.md item 3.4)
        tx.start_step("genesis")
        genesis_credential = {
            "type": "GenesisVC",
            "device_id": request.device_id,
            "model_id": request.model_id,
            "manufacturer_did": request.manufacturer_did,
            "device_type": request.device_type.value,
            "issued_at": datetime.now(UTC).isoformat(),
        }
        genesis_vc_hash = _genesis_vc_hash(genesis_credential)
        tx.complete_step(
            "genesis",
            {"genesis_vc": genesis_credential, "genesis_vc_hash": genesis_vc_hash},
        )

        # Passo 3: Registo no ledger (Manufactured)
        tx.start_step("ledger")
        result = fabric_client.manufacture_device(
            device_id=request.device_id,
            model_id=request.model_id,
            manufacturer_id=request.manufacturer_did,
            genesis_vc_hash=genesis_vc_hash,
        )
        tx.complete_step("ledger", result)

        # Passo 4: Available
        tx.start_step("available")
        result = fabric_client.make_available(request.device_id)
        tx.complete_step("available", result)

        return UCResponse(
            success=True,
            use_case="UC3",
            device_id=request.device_id,
            message=f"Dispositivo {request.device_id} registado e disponivel",
            data={"transaction_id": tx.transaction_id},
        )
    except Exception as e:
        logger.error("UC3 falhou: %s", e)
        return UCResponse(success=False, use_case="UC3", device_id=request.device_id, message=str(e))
