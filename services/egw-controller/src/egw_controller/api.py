"""API FastAPI do EGW Controller.

Endpoints REST para orquestrar os 8 use cases da arquitetura C2DTA.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from egw_controller.clients.aca_py_client import AcaPyClient
from egw_controller.clients.ditto_client import DittoClient
from egw_controller.clients.fabric_client import FabricClient
from egw_controller.clients.ipfs_client import IPFSClient
from egw_controller.config import get_config
from egw_controller.models import (
    ClaimRequest,
    DeviceRegistrationRequest,
    EnrollmentRequest,
    ModelRegistrationRequest,
    PurchaseRequest,
    SellRequest,
    TwinRequest,
    UCResponse,
    UntwinRequest,
)
from egw_controller.transaction import TransactionManager
from egw_controller.use_cases import (
    uc1_oem_enrollment,
    uc2_model_registration,
    uc3_device_registration,
    uc4_device_purchase,
    uc5_device_claiming,
    uc6_device_twinning,
    uc7_device_untwinning,
    uc8_device_selling,
)

logger = logging.getLogger(__name__)

# --- Singletons inicializados no lifespan ---
_config: dict = {}
_tx_manager: TransactionManager = TransactionManager()
_fabric_client: FabricClient | None = None
_ditto_client: DittoClient | None = None
_ipfs_client: IPFSClient | None = None
_consortium_client: AcaPyClient | None = None
_oem_client: AcaPyClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa clientes no arranque."""
    global _config, _fabric_client, _ditto_client, _ipfs_client
    global _consortium_client, _oem_client

    _config = get_config()
    _fabric_client = FabricClient(
        peer_url=_config["fabric_peer_url"],
        channel=_config["fabric_channel"],
    )
    _ditto_client = DittoClient(
        base_url=_config["ditto_url"],
        username=_config["ditto_user"],
        password=_config["ditto_pass"],
    )
    _ipfs_client = IPFSClient(api_url=_config["ipfs_api_url"])
    _consortium_client = AcaPyClient(admin_url=_config["acapy_consortium_url"])
    _oem_client = AcaPyClient(admin_url=_config["acapy_oem_url"])

    logger.info("EGW Controller inicializado")
    yield
    logger.info("EGW Controller a encerrar")


app = FastAPI(
    title="EGW Controller",
    description="Orquestrador dos 8 use cases da arquitetura C2DTA",
    version="0.1.0",
    lifespan=lifespan,
)


# ---------- Use Case Endpoints ----------


@app.post("/uc/enrollment", response_model=UCResponse)
async def enrollment(request: EnrollmentRequest):
    """UC1 — OEM Enrollment no consorcio."""
    return await uc1_oem_enrollment.execute(
        request=request,
        consortium_client=_consortium_client,
        tx_manager=_tx_manager,
    )


@app.post("/uc/register-model", response_model=UCResponse)
async def register_model(request: ModelRegistrationRequest):
    """UC2 — Registo de modelo de dispositivo."""
    return await uc2_model_registration.execute(
        request=request,
        fabric_client=_fabric_client,
        tx_manager=_tx_manager,
    )


@app.post("/uc/register-device", response_model=UCResponse)
async def register_device(request: DeviceRegistrationRequest):
    """UC3 — Auto-registo de dispositivo."""
    return await uc3_device_registration.execute(
        request=request,
        oem_client=_oem_client,
        fabric_client=_fabric_client,
        tx_manager=_tx_manager,
    )


@app.post("/uc/purchase", response_model=UCResponse)
async def purchase(request: PurchaseRequest):
    """UC4 — Compra de dispositivo."""
    return await uc4_device_purchase.execute(
        request=request,
        fabric_client=_fabric_client,
        tx_manager=_tx_manager,
    )


@app.post("/uc/claim", response_model=UCResponse)
async def claim(request: ClaimRequest):
    """UC5 — Reivindicacao de dispositivo."""
    return await uc5_device_claiming.execute(
        request=request,
        fabric_client=_fabric_client,
        tx_manager=_tx_manager,
    )


@app.post("/uc/twin", response_model=UCResponse)
async def twin(request: TwinRequest):
    """UC6 — Twinning de smart device."""
    return await uc6_device_twinning.execute(
        request=request,
        ditto_client=_ditto_client,
        fabric_client=_fabric_client,
        tx_manager=_tx_manager,
    )


@app.post("/uc/untwin", response_model=UCResponse)
async def untwin(request: UntwinRequest):
    """UC7 — Untwinning de smart device."""
    return await uc7_device_untwinning.execute(
        request=request,
        ditto_client=_ditto_client,
        fabric_client=_fabric_client,
        tx_manager=_tx_manager,
    )


@app.post("/uc/sell", response_model=UCResponse)
async def sell(request: SellRequest):
    """UC8 — Venda de smart device."""
    return await uc8_device_selling.execute(
        request=request,
        fabric_client=_fabric_client,
        tx_manager=_tx_manager,
    )


# ---------- Query Endpoints ----------


@app.get("/devices/{device_id}")
async def get_device(device_id: str):
    """Consulta estado de um dispositivo no Fabric."""
    result = _fabric_client.query_device(device_id)
    return result


@app.get("/devices")
async def list_devices(state: str | None = None, owner: str | None = None):
    """Lista dispositivos (por estado ou proprietario)."""
    if state:
        return _fabric_client.invoke_chaincode(
            _fabric_client.cc_lifecycle, "QueryDevicesByState", [state],
        )
    if owner:
        return _fabric_client.invoke_chaincode(
            _fabric_client.cc_lifecycle, "QueryDevicesByOwner", [owner],
        )
    return {"message": "Especifique ?state= ou ?owner= para filtrar"}


@app.get("/transactions")
async def list_transactions():
    """Lista todas as transacoes do EGW Controller."""
    txs = _tx_manager.list_all()
    return [
        {
            "transaction_id": tx.transaction_id,
            "use_case": tx.use_case,
            "device_id": tx.device_id,
            "status": tx.status.value,
            "created_at": tx.created_at,
            "steps": [
                {
                    "step_id": s.step_id,
                    "status": s.status.value,
                    "description": s.description,
                }
                for s in tx.steps
            ],
        }
        for tx in txs
    ]


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "ok", "service": "egw-controller"}
