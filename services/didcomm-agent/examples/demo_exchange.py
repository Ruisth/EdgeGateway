"""Small demo showcasing a DIDComm exchange between Edge Gateway and Digital Twin."""

from didcomm_agent import DIDCommAgent


def main() -> None:
    edge = DIDCommAgent("did:edge:gateway", "https://edge.local/inbox", label="Edge Gateway")
    twin = DIDCommAgent("did:twin:digital", "https://twin.cloud/inbox", label="Digital Twin")

    invitation = edge.create_invitation()
    response = twin.accept_invitation(invitation)
    edge.complete_handshake(response)

    print("Peers registered:")
    print("- Edge peers:", tuple(edge.list_peers()))
    print("- Twin peers:", tuple(twin.list_peers()))

    envelope = edge.send_message(
        to_did=twin.did,
        body={"telemetry": {"temperature": 20.8, "unit": "C"}},
        msg_type="https://didcomm.org/telemetry/1.0/report",
    )

    decoded = twin.receive_message(envelope)
    print("Twin received message:")
    print(decoded.to_json())


if __name__ == "__main__":
    main()
