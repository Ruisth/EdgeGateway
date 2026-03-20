"""Testes para UC6 — SD Twinning."""

import pytest

from egw_controller.models import TwinRequest
from egw_controller.use_cases import uc6_device_twinning


@pytest.mark.asyncio
async def test_uc6_success(ditto_client, fabric_client, tx_manager):
    request = TwinRequest(device_id="sd-001")
    result = await uc6_device_twinning.execute(
        request, ditto_client, fabric_client, tx_manager,
    )

    assert result.success is True
    assert result.use_case == "UC6"
    assert result.device_id == "sd-001"
    assert "thing_id" in result.data
    ditto_client.create_thing.assert_called_once()


@pytest.mark.asyncio
async def test_uc6_ditto_failure(ditto_client, fabric_client, tx_manager):
    ditto_client.create_thing.side_effect = Exception("Ditto unavailable")
    request = TwinRequest(device_id="sd-fail")
    result = await uc6_device_twinning.execute(
        request, ditto_client, fabric_client, tx_manager,
    )

    assert result.success is False
    assert "Ditto unavailable" in result.message


def test_uc6_api(test_client):
    resp = test_client.post("/uc/twin", json={"device_id": "sd-api-001"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
