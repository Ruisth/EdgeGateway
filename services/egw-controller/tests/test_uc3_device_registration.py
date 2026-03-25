"""Testes para UC3 — Device Self-Registration."""

import pytest

from egw_controller.models import DeviceRegistrationRequest, DeviceType
from egw_controller.use_cases import uc3_device_registration


@pytest.mark.asyncio
async def test_uc3_success(oem_client, fabric_client, tx_manager):
    request = DeviceRegistrationRequest(
        device_id="sd-001",
        model_id="smartwatch-v1",
        device_type=DeviceType.SD,
        manufacturer_did="did:sov:oem123",
    )
    result = await uc3_device_registration.execute(
        request, oem_client, fabric_client, tx_manager,
    )

    assert result.success is True
    assert result.use_case == "UC3"
    assert result.device_id == "sd-001"


def test_uc3_api(test_client):
    resp = test_client.post("/uc/register-device", json={
        "device_id": "sd-api-001",
        "model_id": "smartwatch-v1",
        "device_type": "SmartDevice",
        "manufacturer_did": "did:sov:oem-api",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["device_id"] == "sd-api-001"
