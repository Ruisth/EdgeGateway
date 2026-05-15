"""Modelos de dominio do EGW Controller.

Representam os conceitos centrais da arquitetura C2DTA conforme
o paper EdgeGateway_Paper.pdf.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class DeviceState(StrEnum):
    """Estados do ciclo de vida de um dispositivo (paper Seccao 3.1)."""

    MANUFACTURED = "Manufactured"
    AVAILABLE = "Available"
    IN_TRANSIT = "In-Transit"
    CLAIMED = "Claimed"
    TWINNED = "Twinned"
    DECOMMISSIONED = "Decommissioned"


class DeviceType(StrEnum):
    """Tipos de dispositivo C2DTA."""

    EGW = "EdgeGateway"
    SD = "SmartDevice"


class DeviceInfo(BaseModel):
    """Informacao de um dispositivo no ecossistema."""

    device_id: str
    model_id: str = ""
    device_type: DeviceType
    state: DeviceState = DeviceState.MANUFACTURED
    manufacturer_id: str = ""
    owner_did: str = ""
    controller_did: str = ""
    ditto_thing_id: str = ""
    genesis_vc_hash: str = ""
    ownership_vc_hash: str = ""


class DatasetInfo(BaseModel):
    """Informacao de um dataset (snapshot DT) armazenado no IPFS."""

    dataset_id: str
    device_id: str
    ipfs_hash: str
    owner_did: str
    size_bytes: int = 0
    record_count: int = 0
    start_time: str = ""
    end_time: str = ""


# ---------- Request/Response para a API ----------


class EnrollmentRequest(BaseModel):
    """Pedido de inscricao de OEM no consorcio (UC1)."""

    organization_name: str
    organization_did: str


class ModelRegistrationRequest(BaseModel):
    """Pedido de registo de modelo de dispositivo (UC2)."""

    model_id: str
    manufacturer: str
    wot_td_hash: str


class DeviceRegistrationRequest(BaseModel):
    """Pedido de auto-registo de dispositivo (UC3)."""

    device_id: str
    model_id: str
    device_type: DeviceType
    manufacturer_did: str


class PurchaseRequest(BaseModel):
    """Pedido de compra de dispositivo (UC4)."""

    device_id: str
    buyer_did: str


class ClaimRequest(BaseModel):
    """Pedido de reivindicacao de dispositivo (UC5)."""

    device_id: str
    controller_did: str
    ownership_vc_hash: str


class TwinRequest(BaseModel):
    """Pedido de twinning de smart device (UC6)."""

    device_id: str
    twin_config: dict = Field(default_factory=dict)


class UntwinRequest(BaseModel):
    """Pedido de untwinning de smart device (UC7)."""

    device_id: str


class SellRequest(BaseModel):
    """Pedido de venda de smart device (UC8)."""

    device_id: str
    buyer_did: str
    sale_config: dict = Field(default_factory=dict)


class UCResponse(BaseModel):
    """Resposta generica de um use case."""

    success: bool
    use_case: str
    device_id: str = ""
    message: str = ""
    data: dict | None = None
