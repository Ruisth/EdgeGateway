"""Low-level cryptographic helpers for the DIDComm agent."""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

HKDF_INFO = b"edge-gateway-didcomm"


@dataclass(frozen=True)
class KeyPair:
    """Represents an X25519 key pair."""

    private_key: x25519.X25519PrivateKey
    public_key: x25519.X25519PublicKey

    @property
    def public_bytes(self) -> bytes:
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    @property
    def private_bytes(self) -> bytes:
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )

    def public_b64(self) -> str:
        return base64.urlsafe_b64encode(self.public_bytes).decode("ascii")


def generate_keypair() -> KeyPair:
    """Generate a fresh X25519 key pair."""

    private = x25519.X25519PrivateKey.generate()
    return KeyPair(private, private.public_key())


def load_public_key(data_b64: str) -> x25519.X25519PublicKey:
    return x25519.X25519PublicKey.from_public_bytes(
        base64.urlsafe_b64decode(data_b64.encode("ascii"))
    )


def derive_shared_key(our_private: x25519.X25519PrivateKey, peer_public: x25519.X25519PublicKey) -> bytes:
    shared_secret = our_private.exchange(peer_public)
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=HKDF_INFO,
    )
    return hkdf.derive(shared_secret)


def encrypt(shared_key: bytes, plaintext: bytes, aad: bytes) -> tuple[str, str]:
    """Encrypt data with ChaCha20-Poly1305 returning nonce/ciphertext in base64 urlsafe."""

    nonce = os.urandom(12)
    cipher = ChaCha20Poly1305(shared_key)
    ciphertext = cipher.encrypt(nonce, plaintext, aad)
    return (
        base64.urlsafe_b64encode(nonce).decode("ascii"),
        base64.urlsafe_b64encode(ciphertext).decode("ascii"),
    )


def decrypt(shared_key: bytes, nonce_b64: str, ciphertext_b64: str, aad: bytes) -> bytes:
    cipher = ChaCha20Poly1305(shared_key)
    nonce = base64.urlsafe_b64decode(nonce_b64.encode("ascii"))
    ciphertext = base64.urlsafe_b64decode(ciphertext_b64.encode("ascii"))
    return cipher.decrypt(nonce, ciphertext, aad)
