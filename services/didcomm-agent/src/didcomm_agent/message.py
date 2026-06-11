"""Message definitions for the DIDComm agent."""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from .exceptions import InvalidMessageError

logger = logging.getLogger(__name__)


def _decode_json(raw: str) -> dict[str, Any]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.warning("Falha a descodificar JSON DIDComm: %s", exc)
        raise InvalidMessageError("malformed-json") from exc
    if not isinstance(data, dict):
        logger.warning("Payload DIDComm nao e um objecto JSON: %s", type(data).__name__)
        raise InvalidMessageError("not-a-json-object")
    return data


def _require(data: dict[str, Any], *keys: str) -> None:
    missing = [k for k in keys if k not in data]
    if missing:
        logger.warning("Campos DIDComm em falta: %s", missing)
        raise InvalidMessageError(f"missing-fields:{','.join(missing)}")


@dataclass(slots=True)
class DIDCommMessage:
    """A simplified DIDComm v2 message representation."""

    type: str
    body: dict[str, Any]
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
    def from_json(cls, raw: str) -> DIDCommMessage:
        data = _decode_json(raw)
        _require(data, "id", "type", "body", "to", "from", "created_time")
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
    def from_json(cls, raw: str) -> EncryptedDIDCommMessage:
        data = _decode_json(raw)
        _require(data, "ciphertext", "nonce", "to", "from", "created_time")
        return cls(
            ciphertext=data["ciphertext"],
            nonce=data["nonce"],
            typ=data.get("typ", "application/didcomm-encrypted+json"),
            to=data["to"],
            frm=data["from"],
            created_time=data["created_time"],
        )
