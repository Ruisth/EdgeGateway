"""Custom exceptions for the DIDComm agent."""

class UnknownPeerError(RuntimeError):
    """Raised when an operation references an unknown peer DID."""


class MessageTamperingError(RuntimeError):
    """Raised when a message fails authentication checks."""


class InvalidMessageError(ValueError):
    """Raised when an incoming message payload cannot be parsed.

    Carries a stable ``reason`` for callers to map to HTTP 400 without
    leaking parser internals.
    """

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason
