import pytest
from fastapi.testclient import TestClient

from didcomm_agent.api import app, state


@pytest.fixture()
def client():
    # reset state between tests
    state.agents.clear()
    return TestClient(app)


def test_api_handshake_and_send(client: TestClient):
    c = client

    # Initialize Edge agent and get invitation
    edge_inv = c.post(
        "/agent",
        json={"agent_id": "edge", "did": "did:edge:gateway", "endpoint": "https://edge.local/inbox", "label": "Edge"},
    ).json()

    # Switch to Twin agent, accept the Edge invitation and produce a counter-invitation
    c.post(
        "/agent",
        json={"agent_id": "twin", "did": "did:twin:digital", "endpoint": "https://twin.cloud/inbox", "label": "Twin"},
    )
    c.post("/accept", json={"agent_id": "twin", "invitation": edge_inv})
    twin_inv = c.post(
        "/agent",
        json={"agent_id": "twin", "did": "did:twin:digital", "endpoint": "https://twin.cloud/inbox", "label": "Twin"},
    ).json()

    # Switch back to Edge and complete handshake with Twin counter-invitation
    c.post(
        "/complete",
        json={"agent_id": "edge", "invitation": twin_inv},
    )

    # Send from Edge to Twin
    env = c.post("/send", json={"agent_id": "edge", "to_did": "did:twin:digital", "body": {"ping": True}}).json()

    # Receive on Twin
    msg = c.post("/receive", json={"agent_id": "twin", "envelope": env}).json()

    assert msg["body"] == {"ping": True}
