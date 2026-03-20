"""Cliente HTTP para a API IPFS (Kubo).

Armazena e recupera snapshots de dados do Digital Twin.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class IPFSClient:
    """Cliente para a API HTTP do IPFS."""

    def __init__(self, api_url: str) -> None:
        self.api_url = api_url.rstrip("/")

    def add_json(self, data: dict[str, Any], filename: str = "dataset.json") -> str:
        """Adiciona um JSON ao IPFS e retorna o CID."""
        payload = json.dumps(data).encode()
        with httpx.Client(timeout=30) as c:
            r = c.post(
                f"{self.api_url}/api/v0/add",
                files={"file": (filename, payload)},
                params={"pin": "true"},
            )
            r.raise_for_status()
            cid = r.json()["Hash"]
        logger.info("Adicionado ao IPFS: %s (CID=%s)", filename, cid)
        return cid

    def cat(self, cid: str) -> bytes:
        """Recupera conteudo por CID."""
        with httpx.Client(timeout=30) as c:
            r = c.post(f"{self.api_url}/api/v0/cat", params={"arg": cid})
            r.raise_for_status()
            return r.content

    def pin(self, cid: str) -> None:
        """Pina um CID para persistencia."""
        with httpx.Client(timeout=10) as c:
            r = c.post(f"{self.api_url}/api/v0/pin/add", params={"arg": cid})
            r.raise_for_status()
        logger.info("Pinado: %s", cid)
