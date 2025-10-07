"""Message definitions for the DIDComm agent."""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class DIDCommMessage:
    """A simplified DIDComm v2 message representation."""

    type: str
    body: Dict[str, Any]
    to: str
    frm: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_time: int = field(default_factory=lambda: int(time.time()))

    def to_json(self) -> str:
        payload = {
            "id": self.id,
            "type": self.type,
            "body": self.body,
            "to": self.to,
            "from": self.frm,
            "created_time": self.created_time,
        }
        return json.dumps(payload, separators=(",", ":"), sort_keys=True)

    @classmethod
    def from_json(cls, raw: str) -> "DIDCommMessage":
        data = json.loads(raw)
        return cls(
            id=data["id"],
            type=data["type"],
            body=data["body"],
            to=data["to"],
            frm=data["from"],
            created_time=data["created_time"],
        )


@dataclass(slots=True)
class EncryptedDIDCommMessage:
    """Encrypted envelope conforming to DIDComm semantics."""

    ciphertext: str
    nonce: str
    to: str
    frm: str
    created_time: int
    typ: str = "application/didcomm-encrypted+json"

    def to_json(self) -> str:
        payload = {
            "ciphertext": self.ciphertext,
            "nonce": self.nonce,
            "typ": self.typ,
            "to": self.to,
            "from": self.frm,
            "created_time": self.created_time,
        }
        return json.dumps(payload, separators=(",", ":"), sort_keys=True)

    @classmethod
    def from_json(cls, raw: str) -> "EncryptedDIDCommMessage":
        data = json.loads(raw)
        return cls(
            ciphertext=data["ciphertext"],
            nonce=data["nonce"],
            typ=data.get("typ", "application/didcomm-encrypted+json"),
            to=data["to"],
            frm=data["from"],
            created_time=data["created_time"],
        )
