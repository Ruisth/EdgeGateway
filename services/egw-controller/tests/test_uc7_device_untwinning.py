"""Testes para UC7 — SD Untwinning."""

import pytest

from egw_controller.models import UntwinRequest
from egw_controller.use_cases import uc7_device_untwinning


@pytest.mark.asyncio
async def test_uc7_success(ditto_client, fabric_client, tx_manager):
    request = UntwinRequest(device_id="sd-001")
    result = await uc7_device_untwinning.execute(
        request, ditto_client, fabric_client, tx_manager,
    )

    assert result.success is True
    assert result.use_case == "UC7"
    ditto_client.delete_thing.assert_called_once()


def test_uc7_api(test_client):
    resp = test_client.post("/uc/untwin", json={"device_id": "sd-api-001"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
