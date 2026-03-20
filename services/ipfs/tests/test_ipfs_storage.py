"""Testes de integracao para o no IPFS C2DTA.

Requer o no IPFS em execucao (docker compose up).

Execucao:
    pytest services/ipfs/tests/test_ipfs_storage.py -v
"""

from __future__ import annotations

import json
import os
import uuid

import pytest

IPFS_API_URL = os.getenv("IPFS_API_URL", "http://localhost:5001")

skip_no_ipfs = pytest.mark.skipif(
    os.getenv("CI") != "true" and not os.getenv("IPFS_API_URL"),
    reason="No IPFS nao disponivel — defina IPFS_API_URL ou CI=true",
)


@skip_no_ipfs
class TestIPFSStorage:
    """Testes de armazenamento no IPFS."""

    def test_add_and_cat_json(self):
        """Adiciona um JSON ao IPFS e recupera-o."""
        import httpx

        dataset = {
            "datasetID": str(uuid.uuid4()),
            "deviceID": "test-device",
            "records": [
                {"heartbeat_bpm": 72, "timestamp": "2026-01-01T00:00:00Z"},
                {"heartbeat_bpm": 75, "timestamp": "2026-01-01T00:00:01Z"},
            ],
        }
        payload = json.dumps(dataset).encode()

        # Adicionar
        r = httpx.post(
            f"{IPFS_API_URL}/api/v0/add",
            files={"file": ("dataset.json", payload)},
            timeout=10,
        )
        assert r.status_code == 200
        result = r.json()
        cid = result["Hash"]
        assert cid, "CID nao retornado"

        # Recuperar
        r = httpx.post(
            f"{IPFS_API_URL}/api/v0/cat",
            params={"arg": cid},
            timeout=10,
        )
        assert r.status_code == 200
        recovered = json.loads(r.content)
        assert recovered["datasetID"] == dataset["datasetID"]
        assert len(recovered["records"]) == 2

    def test_pin_persistence(self):
        """Verifica que um ficheiro pinado persiste."""
        import httpx

        content = json.dumps({"test": "pin", "id": str(uuid.uuid4())}).encode()

        # Adicionar (auto-pin)
        r = httpx.post(
            f"{IPFS_API_URL}/api/v0/add",
            files={"file": ("test.json", content)},
            params={"pin": "true"},
            timeout=10,
        )
        cid = r.json()["Hash"]

        # Verificar pin
        r = httpx.post(
            f"{IPFS_API_URL}/api/v0/pin/ls",
            params={"arg": cid, "type": "recursive"},
            timeout=10,
        )
        assert r.status_code == 200
