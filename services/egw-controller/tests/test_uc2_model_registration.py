"""Testes para UC2 — Device Model Registration."""

import pytest

from egw_controller.models import ModelRegistrationRequest
from egw_controller.use_cases import uc2_model_registration


@pytest.mark.asyncio
async def test_uc2_success(fabric_client, tx_manager):
    request = ModelRegistrationRequest(
        model_id="smartwatch-v1",
        manufacturer="OEM-Test",
        wot_td_hash="sha256:abc123",
    )
    result = await uc2_model_registration.execute(request, fabric_client, tx_manager)

    assert result.success is True
    assert result.use_case == "UC2"
    assert "smartwatch-v1" in result.message


def test_uc2_api(test_client):
    resp = test_client.post("/uc/register-model", json={
        "model_id": "smartwatch-v2",
        "manufacturer": "OEM-API",
        "wot_td_hash": "sha256:def456",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["use_case"] == "UC2"
