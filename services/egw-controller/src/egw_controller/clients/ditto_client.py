"""Cliente HTTP para a API Eclipse Ditto.

Gere things (Digital Twins) e conexoes MQTT no Ditto.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class DittoClient:
    """Cliente para a API HTTP do Eclipse Ditto."""

    def __init__(self, base_url: str, username: str, password: str) -> None:
        self.base_url = base_url.rstrip("/")
        self._auth = httpx.BasicAuth(username, password)

    def create_thing(self, thing_id: str, features: dict[str, Any]) -> dict:
        """Cria um thing no Ditto (UC6)."""
        body = {"thingId": thing_id, "features": features}
        with httpx.Client(base_url=self.base_url, auth=self._auth, timeout=10) as c:
            r = c.put(f"/api/2/things/{thing_id}", json=body)
            r.raise_for_status()
        logger.info("Thing criado: %s", thing_id)
        return body

    def get_thing(self, thing_id: str) -> dict | None:
        """Retorna um thing por ID."""
        with httpx.Client(base_url=self.base_url, auth=self._auth, timeout=10) as c:
            r = c.get(f"/api/2/things/{thing_id}")
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r.json()

    def delete_thing(self, thing_id: str) -> None:
        """Remove um thing (UC7 — untwinning)."""
        with httpx.Client(base_url=self.base_url, auth=self._auth, timeout=10) as c:
            r = c.delete(f"/api/2/things/{thing_id}")
            r.raise_for_status()
        logger.info("Thing removido: %s", thing_id)

    def get_thing_features(self, thing_id: str) -> dict:
        """Retorna as features de um thing (para snapshot)."""
        with httpx.Client(base_url=self.base_url, auth=self._auth, timeout=10) as c:
            r = c.get(f"/api/2/things/{thing_id}/features")
            r.raise_for_status()
            return r.json()
