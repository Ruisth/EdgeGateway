"""Custom exceptions for the DIDComm agent."""

class UnknownPeerError(RuntimeError):
    """Raised when an operation references an unknown peer DID."""


class MessageTamperingError(RuntimeError):
    """Raised when a message fails authentication checks."""
