"""Testes para UC5 — Device Claiming."""

import pytest

from egw_controller.models import ClaimRequest
from egw_controller.use_cases import uc5_device_claiming


@pytest.mark.asyncio
async def test_uc5_success(fabric_client, tx_manager):
    request = ClaimRequest(
        device_id="sd-001",
        controller_did="did:sov:consumer123",
        ownership_vc_hash="sha256:own789",
    )
    result = await uc5_device_claiming.execute(request, fabric_client, tx_manager)

    assert result.success is True
    assert result.use_case == "UC5"
    assert result.device_id == "sd-001"


def test_uc5_api(test_client):
    resp = test_client.post("/uc/claim", json={
        "device_id": "sd-001",
        "controller_did": "did:sov:consumer-api",
        "ownership_vc_hash": "sha256:api-own",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
