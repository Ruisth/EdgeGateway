"""Testes para UC4 — Consumer Buys Device."""

import pytest

from egw_controller.models import PurchaseRequest
from egw_controller.use_cases import uc4_device_purchase


@pytest.mark.asyncio
async def test_uc4_success(fabric_client, tx_manager):
    request = PurchaseRequest(device_id="sd-001", buyer_did="did:sov:buyer123")
    result = await uc4_device_purchase.execute(request, fabric_client, tx_manager)

    assert result.success is True
    assert result.use_case == "UC4"
    assert result.device_id == "sd-001"


def test_uc4_api(test_client):
    resp = test_client.post("/uc/purchase", json={
        "device_id": "sd-001",
        "buyer_did": "did:sov:buyer-api",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
