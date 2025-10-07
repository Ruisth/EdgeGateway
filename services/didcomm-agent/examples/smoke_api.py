"""Smoke test the running DIDComm API container on localhost:8000.
Creates two agents (edge, twin), completes handshake, sends and receives a message.
"""
from __future__ import annotations

import json

import httpx

BASE = "http://localhost:8000"


def post(path: str, data: dict) -> dict:
    resp = httpx.post(BASE + path, json=data, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get(path: str) -> dict:
    resp = httpx.get(BASE + path, timeout=10)
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    # Health
    print("health:", get("/health"))

    # Edge and Twin agents
    edge_inv = post(
        "/agent",
        {"agent_id": "edge", "did": "did:edge:gateway", "endpoint": "https://edge.local/inbox", "label": "Edge"},
    )
    post(
        "/agent",
        {"agent_id": "twin", "did": "did:twin:digital", "endpoint": "https://twin.cloud/inbox", "label": "Twin"},
    )

    # Twin accepts Edge's invitation, generates counter-invitation
    twin_inv = post("/accept", {"agent_id": "twin", "invitation": edge_inv})

    # Edge completes with Twin invitation
    post("/complete", {"agent_id": "edge", "invitation": twin_inv})

    # Send and receive
    env = post("/send", {"agent_id": "edge", "to_did": "did:twin:digital", "body": {"ping": True}})
    msg = post("/receive", {"agent_id": "twin", "envelope": env})

    print("message:")
    print(json.dumps(msg, ensure_ascii=False))


if __name__ == "__main__":
    main()
