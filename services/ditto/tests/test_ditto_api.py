"""Testes de integracao para a API Eclipse Ditto.

Requer o stack Ditto em execucao (docker compose up).

Execucao:
    pytest services/ditto/tests/test_ditto_api.py -v
"""

from __future__ import annotations

import os
import uuid

import pytest

DITTO_URL = os.getenv("DITTO_URL", "http://localhost:8080")
DITTO_USER = os.getenv("DITTO_USER", "ditto")
DITTO_PASS = os.getenv("DITTO_PASS", "c2dta")

skip_no_ditto = pytest.mark.skipif(
    os.getenv("CI") != "true" and not os.getenv("DITTO_URL"),
    reason="Stack Ditto nao disponivel — defina DITTO_URL ou CI=true",
)


@skip_no_ditto
class TestDittoAPI:
    """Testes CRUD de things via API Ditto."""

    def _auth(self):
        import httpx
        return httpx.BasicAuth(DITTO_USER, DITTO_PASS)

    def test_create_and_get_thing(self):
        """Cria um thing e verifica que e retornado."""
        import httpx

        device_uuid = str(uuid.uuid4())
        thing_id = f"org.c2dta:{device_uuid}"
        thing_body = {
            "thingId": thing_id,
            "features": {
                "heartbeat": {"properties": {"bpm": 72}},
                "geolocation": {"properties": {"latitude": 38.7223, "longitude": -9.1393}},
                "timestamp": {"properties": {"value": "2026-01-01T00:00:00Z"}},
            },
        }

        client = httpx.Client(base_url=DITTO_URL, auth=self._auth(), timeout=10)

        # Criar
        r = client.put(f"/api/2/things/{thing_id}", json=thing_body)
        assert r.status_code in (201, 204), f"Falha ao criar thing: {r.status_code} {r.text}"

        # Ler
        r = client.get(f"/api/2/things/{thing_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["thingId"] == thing_id
        assert data["features"]["heartbeat"]["properties"]["bpm"] == 72

        # Limpar
        client.delete(f"/api/2/things/{thing_id}")
        client.close()

    def test_update_thing_features(self):
        """Atualiza features de um thing existente."""
        import httpx

        device_uuid = str(uuid.uuid4())
        thing_id = f"org.c2dta:{device_uuid}"
        thing_body = {
            "thingId": thing_id,
            "features": {
                "heartbeat": {"properties": {"bpm": 60}},
            },
        }

        client = httpx.Client(base_url=DITTO_URL, auth=self._auth(), timeout=10)

        client.put(f"/api/2/things/{thing_id}", json=thing_body)

        # Atualizar bpm
        r = client.put(
            f"/api/2/things/{thing_id}/features/heartbeat/properties/bpm",
            content="85",
            headers={"Content-Type": "application/json"},
        )
        assert r.status_code in (200, 204)

        # Verificar
        r = client.get(f"/api/2/things/{thing_id}/features/heartbeat/properties/bpm")
        assert r.status_code == 200
        assert r.json() == 85

        client.delete(f"/api/2/things/{thing_id}")
        client.close()
