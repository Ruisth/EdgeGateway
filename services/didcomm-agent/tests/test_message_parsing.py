"""Tests for the message parsing safety added to message.py."""

from __future__ import annotations

import pytest

from didcomm_agent import InvalidMessageError
from didcomm_agent.message import DIDCommMessage, EncryptedDIDCommMessage


def test_didcomm_message_roundtrip():
    msg = DIDCommMessage(
        type="https://didcomm.org/basic-message/2.0/message",
        body={"content": "hi"},
        to="did:edge:a",
        frm="did:edge:b",
    )
    parsed = DIDCommMessage.from_json(msg.to_json())
    assert parsed.id == msg.id
    assert parsed.body == {"content": "hi"}


@pytest.mark.parametrize(
    "raw,reason_prefix",
    [
        ("not-json", "malformed-json"),
        ("[]", "not-a-json-object"),
        ('{"id":"1"}', "missing-fields:"),
    ],
)
def test_didcomm_message_invalid(raw, reason_prefix):
    with pytest.raises(InvalidMessageError) as excinfo:
        DIDCommMessage.from_json(raw)
    assert excinfo.value.reason.startswith(reason_prefix)


def test_encrypted_message_missing_fields_raises():
    payload = '{"ciphertext":"x"}'
    with pytest.raises(InvalidMessageError) as excinfo:
        EncryptedDIDCommMessage.from_json(payload)
    assert excinfo.value.reason.startswith("missing-fields:")
