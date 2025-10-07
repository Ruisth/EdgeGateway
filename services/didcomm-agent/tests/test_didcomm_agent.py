from copy import deepcopy

import pytest

from didcomm_agent import (
    DIDCommAgent,
    MessageTamperingError,
    UnknownPeerError,
)


@pytest.fixture()
def agents():
    edge = DIDCommAgent("did:edge:gateway", "https://edge.local/inbox", label="Edge Gateway")
    twin = DIDCommAgent("did:twin:digital", "https://twin.cloud/inbox", label="Digital Twin")

    invitation = edge.create_invitation()
    response = twin.accept_invitation(invitation)
    edge.complete_handshake(response)

    return edge, twin


def test_successful_message_exchange(agents):
    edge, twin = agents
    payload = {"telemetry": {"temperature": 21.4, "unit": "C"}}

    envelope = edge.send_message("did:twin:digital", payload)
    message = twin.receive_message(envelope)

    assert message.body == payload
    assert message.frm == edge.did
    assert message.to == twin.did


def test_unknown_peer_detection():
    agent = DIDCommAgent("did:edge:gateway", "https://edge.local/inbox")

    with pytest.raises(UnknownPeerError):
        agent.send_message("did:unknown", {"ping": True})


def test_tampering_triggers_error(agents):
    edge, twin = agents
    envelope = edge.send_message("did:twin:digital", {"command": "reboot"})

    tampered = deepcopy(envelope)
    tampered.ciphertext = tampered.ciphertext[:-1] + (
        "A" if tampered.ciphertext[-1] != "A" else "B"
    )

    with pytest.raises(MessageTamperingError):
        twin.receive_message(tampered)
