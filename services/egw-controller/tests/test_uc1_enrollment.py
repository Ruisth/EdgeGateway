"""Testes para UC1 — OEM Enrollment."""

import pytest

from egw_controller.models import EnrollmentRequest
from egw_controller.use_cases import uc1_oem_enrollment


@pytest.mark.asyncio
async def test_uc1_success(consortium_client, tx_manager):
    request = EnrollmentRequest(
        organization_name="OEM-Test",
        organization_did="did:sov:oem123",
    )
    result = await uc1_oem_enrollment.execute(request, consortium_client, tx_manager)

    assert result.success is True
    assert result.use_case == "UC1"
    assert "OEM-Test" in result.message
    consortium_client.create_oob_invitation.assert_called_once()


@pytest.mark.asyncio
async def test_uc1_failure(consortium_client, tx_manager):
    consortium_client.create_oob_invitation.side_effect = Exception("Connection refused")
    request = EnrollmentRequest(
        organization_name="OEM-Fail",
        organization_did="did:sov:fail",
    )
    result = await uc1_oem_enrollment.execute(request, consortium_client, tx_manager)

    assert result.success is False
    assert "Connection refused" in result.message


def test_uc1_api(test_client):
    resp = test_client.post("/uc/enrollment", json={
        "organization_name": "OEM-API",
        "organization_did": "did:sov:api123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["use_case"] == "UC1"
