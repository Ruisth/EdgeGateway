"""Cliente HTTP para a API admin ACA-Py.

Gere conexoes DIDComm, emissao de VCs e verificacao de provas.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class AcaPyClient:
    """Cliente para a API admin do ACA-Py."""

    def __init__(self, admin_url: str) -> None:
        self.admin_url = admin_url.rstrip("/")

    def get_status(self) -> dict:
        """Verifica o estado do agente."""
        with httpx.Client(timeout=10) as c:
            r = c.get(f"{self.admin_url}/status")
            r.raise_for_status()
            return r.json()

    def create_oob_invitation(
        self, goal_code: str = "", label: str = ""
    ) -> dict:
        """Cria um convite Out-of-Band."""
        body: dict[str, Any] = {
            "handshake_protocols": ["https://didcomm.org/didexchange/1.0"],
        }
        if goal_code:
            body["goal_code"] = goal_code
        if label:
            body["my_label"] = label

        with httpx.Client(timeout=10) as c:
            r = c.post(
                f"{self.admin_url}/out-of-band/create-invitation",
                json=body,
            )
            r.raise_for_status()
            return r.json()

    def receive_oob_invitation(self, invitation: dict) -> dict:
        """Aceita um convite Out-of-Band recebido."""
        with httpx.Client(timeout=10) as c:
            r = c.post(
                f"{self.admin_url}/out-of-band/receive-invitation",
                json=invitation,
            )
            r.raise_for_status()
            return r.json()

    def list_connections(self) -> list[dict]:
        """Lista todas as conexoes."""
        with httpx.Client(timeout=10) as c:
            r = c.get(f"{self.admin_url}/connections")
            r.raise_for_status()
            return r.json().get("results", [])

    def issue_credential(self, credential_data: dict) -> dict:
        """Emite uma Verifiable Credential (Issue Credential v2)."""
        with httpx.Client(timeout=10) as c:
            r = c.post(
                f"{self.admin_url}/issue-credential-2.0/send",
                json=credential_data,
            )
            r.raise_for_status()
            return r.json()

    def request_proof(self, proof_request: dict) -> dict:
        """Solicita uma prova (Present Proof v2)."""
        with httpx.Client(timeout=10) as c:
            r = c.post(
                f"{self.admin_url}/present-proof-2.0/send-request",
                json=proof_request,
            )
            r.raise_for_status()
            return r.json()

    def create_public_did(self, method: str = "sov") -> dict:
        """Cria um DID publico no ledger."""
        with httpx.Client(timeout=15) as c:
            r = c.post(
                f"{self.admin_url}/wallet/did/create",
                json={"method": method},
            )
            r.raise_for_status()
            return r.json()
