"""High-level DIDComm agent orchestration."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Iterable

from .crypto import (
    KeyPair,
    derive_shared_key,
    decrypt,
    encrypt,
    generate_keypair,
    load_public_key,
)
from .exceptions import MessageTamperingError, UnknownPeerError
from .message import DIDCommMessage, EncryptedDIDCommMessage


@dataclass(slots=True)
class DIDCommInvitation:
    """Invitation envelope used during pairwise channel setup."""

    did: str
    endpoint: str
    public_key: str
    label: str | None = None
    created_time: int = field(default_factory=lambda: int(time.time()))


@dataclass(slots=True)
class _Peer:
    did: str
    endpoint: str
    public_key_b64: str
    label: str | None

    def public_key(self):
        return load_public_key(self.public_key_b64)


class DIDCommAgent:
    """Simplified DIDComm agent for the Edge Gateway."""

    def __init__(self, did: str, endpoint: str, *, label: str | None = None, keypair: KeyPair | None = None):
        self.did = did
        self.endpoint = endpoint
        self.label = label or did
        self._keypair = keypair or generate_keypair()
        self._peers: Dict[str, _Peer] = {}

    @property
    def public_key_b64(self) -> str:
        return self._keypair.public_b64()

    def create_invitation(self) -> DIDCommInvitation:
        """Create an invitation payload that can be shared with a peer agent."""

        return DIDCommInvitation(
            did=self.did,
            endpoint=self.endpoint,
            public_key=self.public_key_b64,
            label=self.label,
        )

    def accept_invitation(self, invitation: DIDCommInvitation) -> DIDCommInvitation:
        """Accept a peer invitation and return a counter-invitation for mutual onboarding."""

        self._store_peer(invitation)
        return self.create_invitation()

    def complete_handshake(self, invitation: DIDCommInvitation) -> None:
        """Store peer data received after our invitation was accepted."""

        self._store_peer(invitation)

    def list_peers(self) -> Iterable[str]:
        return tuple(self._peers.keys())

    def send_message(self, to_did: str, body: dict, *, msg_type: str = "https://didcomm.org/basic-message/2.0/message") -> EncryptedDIDCommMessage:
        peer = self._peers.get(to_did)
        if peer is None:
            raise UnknownPeerError(f"Unknown DID: {to_did}")

        message = DIDCommMessage(type=msg_type, body=body, to=to_did, frm=self.did)
        shared_key = derive_shared_key(self._keypair.private_key, peer.public_key())
        aad = self._build_aad(message)
        nonce, ciphertext = encrypt(shared_key, message.to_json().encode("utf-8"), aad)
        return EncryptedDIDCommMessage(
            ciphertext=ciphertext,
            nonce=nonce,
            to=to_did,
            frm=self.did,
            created_time=message.created_time,
        )

    def receive_message(self, envelope: EncryptedDIDCommMessage) -> DIDCommMessage:
        peer = self._peers.get(envelope.frm)
        if peer is None:
            raise UnknownPeerError(f"Unknown DID: {envelope.frm}")

        shared_key = derive_shared_key(self._keypair.private_key, peer.public_key())
        aad = self._build_aad_from_envelope(envelope)
        try:
            raw = decrypt(shared_key, envelope.nonce, envelope.ciphertext, aad)
        except Exception as exc:  # noqa: BLE001 - map any AEAD error to MessageTamperingError
            raise MessageTamperingError("Failed to authenticate DIDComm message") from exc
        return DIDCommMessage.from_json(raw.decode("utf-8"))

    def _store_peer(self, invitation: DIDCommInvitation) -> None:
        self._peers[invitation.did] = _Peer(
            did=invitation.did,
            endpoint=invitation.endpoint,
            public_key_b64=invitation.public_key,
            label=invitation.label,
        )

    def _build_aad(self, message: DIDCommMessage) -> bytes:
        return f"{message.frm}|{message.to}|{message.created_time}".encode("utf-8")

    def _build_aad_from_envelope(self, envelope: EncryptedDIDCommMessage) -> bytes:
        return f"{envelope.frm}|{envelope.to}|{envelope.created_time}".encode("utf-8")
