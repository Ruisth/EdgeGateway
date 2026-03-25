"""Fixtures partilhadas para testes do EGW Controller."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

# Adicionar src/ ao path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from egw_controller import api
from egw_controller.clients.aca_py_client import AcaPyClient
from egw_controller.clients.ditto_client import DittoClient
from egw_controller.clients.fabric_client import FabricClient
from egw_controller.clients.ipfs_client import IPFSClient
from egw_controller.transaction import TransactionManager


@pytest.fixture()
def tx_manager():
    """TransactionManager limpo."""
    return TransactionManager()


@pytest.fixture()
def fabric_client():
    """FabricClient mock — invocacoes retornam resultado de sucesso."""
    return FabricClient(peer_url="localhost:7051", channel="test-channel")


@pytest.fixture()
def ditto_client():
    """DittoClient mock."""
    client = MagicMock(spec=DittoClient)
    client.create_thing.return_value = {"thingId": "org.c2dta:test-device"}
    client.delete_thing.return_value = None
    client.get_thing.return_value = {"thingId": "org.c2dta:test-device"}
    client.get_thing_features.return_value = {"heartbeat": {"properties": {"bpm": 72}}}
    return client


@pytest.fixture()
def ipfs_client():
    """IPFSClient mock."""
    client = MagicMock(spec=IPFSClient)
    client.add_json.return_value = "QmTestCID123"
    client.cat.return_value = b'{"test": true}'
    return client


@pytest.fixture()
def consortium_client():
    """AcaPyClient mock para o consorcio."""
    client = MagicMock(spec=AcaPyClient)
    client.create_oob_invitation.return_value = {
        "invitation": {"@id": "test-inv-id"},
    }
    client.issue_credential.return_value = {"credential_exchange_id": "cred-123"}
    return client


@pytest.fixture()
def oem_client():
    """AcaPyClient mock para o OEM."""
    client = MagicMock(spec=AcaPyClient)
    client.create_oob_invitation.return_value = {
        "invitation": {"@id": "oem-inv-id"},
    }
    client.issue_credential.return_value = {"credential_exchange_id": "cred-456"}
    return client


@pytest.fixture()
def test_client(fabric_client, ditto_client, ipfs_client, consortium_client, oem_client, tx_manager):
    """TestClient FastAPI com clientes injetados."""
    api._fabric_client = fabric_client
    api._ditto_client = ditto_client
    api._ipfs_client = ipfs_client
    api._consortium_client = consortium_client
    api._oem_client = oem_client
    api._tx_manager = tx_manager
    return TestClient(api.app)
