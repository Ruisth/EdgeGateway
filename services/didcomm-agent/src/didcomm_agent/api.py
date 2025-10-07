"""FastAPI service exposing DIDComm agent operations."""

from __future__ import annotations

from dataclasses import asdict
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from .service import DIDCommAgent, DIDCommInvitation, EncryptedDIDCommMessage
from .storage import Storage


class CreateAgentRequest(BaseModel):
    agent_id: str
    did: str
    endpoint: str
    label: str | None = None


class InvitationResponse(BaseModel):
    did: str
    endpoint: str
    public_key: str
    label: str | None
    created_time: int


class AcceptInvitationRequest(BaseModel):
    agent_id: str
    invitation: InvitationResponse


class SendMessageRequest(BaseModel):
    agent_id: str
    to_did: str
    body: dict
    msg_type: str | None = None


class EnvelopeModel(BaseModel):
    ciphertext: str
    nonce: str
    to: str
    frm: str
    created_time: int
    typ: str | None = None


class MessageModel(BaseModel):
    id: str
    type: str
    body: dict
    to: str
    frm: str
    created_time: int


class ReceiveMessageRequest(BaseModel):
    agent_id: str
    envelope: EnvelopeModel


class AppState:
    agents: dict[str, DIDCommAgent]
    storage: Storage | None

    def __init__(self) -> None:
        self.agents = {}
        self.storage = None


app = FastAPI(title="EdgeGateway DIDComm Agent")
state = AppState()

# Optional storage activation
_db_path = os.getenv("DIDCOMM_DB_PATH")
if _db_path:
    state.storage = Storage(Path(_db_path))


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/agent", response_model=InvitationResponse)
async def create_agent(req: CreateAgentRequest):
    agent = state.agents.get(req.agent_id)
    if agent is None:
        # Try to restore from storage
        if state.storage:
            restored = state.storage.get_agent(req.agent_id)
        else:
            restored = None

        if restored:
            did, endpoint, label, keypair = restored
            agent = DIDCommAgent(did, endpoint, label=label, keypair=keypair)
            state.agents[req.agent_id] = agent
            # Load known peers
            for inv in state.storage.load_peers(req.agent_id):
                agent.complete_handshake(inv)
        else:
            agent = DIDCommAgent(req.did, req.endpoint, label=req.label)
            state.agents[req.agent_id] = agent
            # Persist new agent
            if state.storage:
                state.storage.upsert_agent(req.agent_id, req.did, req.endpoint, req.label, agent._keypair)  # type: ignore[attr-defined]
    inv = agent.create_invitation()
    return InvitationResponse(**asdict(inv))


@app.post("/accept", response_model=InvitationResponse)
async def accept_invitation(req: AcceptInvitationRequest):
    agent = state.agents.get(req.agent_id)
    if not agent:
        raise HTTPException(status_code=400, detail="Agent not initialized")
    inv = DIDCommInvitation(**req.invitation.model_dump())
    resp = agent.accept_invitation(inv)
    if state.storage:
        state.storage.upsert_peer(req.agent_id, inv)
    return InvitationResponse(**asdict(resp))


@app.post("/complete")
async def complete_handshake(req: AcceptInvitationRequest):
    agent = state.agents.get(req.agent_id)
    if not agent:
        raise HTTPException(status_code=400, detail="Agent not initialized")
    inv = DIDCommInvitation(**req.invitation.model_dump())
    agent.complete_handshake(inv)
    if state.storage:
        state.storage.upsert_peer(req.agent_id, inv)
    return {"status": "ok"}


@app.get("/peers")
async def list_peers(agent_id: str = Query(...)):
    agent = state.agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=400, detail="Agent not initialized")
    return {"peers": list(agent.list_peers())}


@app.post("/send", response_model=EnvelopeModel)
async def send_message(req: SendMessageRequest):
    agent = state.agents.get(req.agent_id)
    if not agent:
        raise HTTPException(status_code=400, detail="Agent not initialized")
    env = agent.send_message(req.to_did, req.body, msg_type=req.msg_type or "https://didcomm.org/basic-message/2.0/message")
    return EnvelopeModel(**asdict(env))


@app.post("/receive", response_model=MessageModel)
async def receive_message(req: ReceiveMessageRequest):
    agent = state.agents.get(req.agent_id)
    if not agent:
        raise HTTPException(status_code=400, detail="Agent not initialized")
    env = EncryptedDIDCommMessage(**req.envelope.model_dump())
    msg = agent.receive_message(env)
    return MessageModel(**asdict(msg))
