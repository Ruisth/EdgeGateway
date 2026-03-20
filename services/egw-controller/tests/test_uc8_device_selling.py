"""Testes para UC8 — SD Selling."""

import pytest

from egw_controller.models import SellRequest
from egw_controller.use_cases import uc8_device_selling


@pytest.mark.asyncio
async def test_uc8_success(fabric_client, tx_manager):
    request = SellRequest(device_id="sd-001", buyer_did="did:sov:newbuyer")
    result = await uc8_device_selling.execute(request, fabric_client, tx_manager)

    assert result.success is True
    assert result.use_case == "UC8"
    assert result.device_id == "sd-001"


def test_uc8_api(test_client):
    resp = test_client.post("/uc/sell", json={
        "device_id": "sd-001",
        "buyer_did": "did:sov:newbuyer-api",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
