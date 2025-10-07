"""Simple SQLite storage for DIDComm agents and peers."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from .crypto import KeyPair, keypair_from_private_b64
from .service import DIDCommInvitation


class Storage:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS agents (
                    agent_id TEXT PRIMARY KEY,
                    did TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    label TEXT,
                    private_key_b64 TEXT NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS peers (
                    agent_id TEXT NOT NULL,
                    did TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    public_key_b64 TEXT NOT NULL,
                    label TEXT,
                    PRIMARY KEY (agent_id, did)
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def upsert_agent(self, agent_id: str, did: str, endpoint: str, label: Optional[str], keypair: KeyPair) -> None:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO agents(agent_id, did, endpoint, label, private_key_b64)
                VALUES(?,?,?,?,?)
                ON CONFLICT(agent_id) DO UPDATE SET did=excluded.did, endpoint=excluded.endpoint, label=excluded.label, private_key_b64=excluded.private_key_b64
                """,
                (agent_id, did, endpoint, label, keypair.private_b64()),
            )
            conn.commit()
        finally:
            conn.close()

    def get_agent(self, agent_id: str) -> Optional[tuple[str, str, Optional[str], KeyPair]]:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT did, endpoint, label, private_key_b64 FROM agents WHERE agent_id=?", (agent_id,))
            row = cur.fetchone()
            if not row:
                return None
            did, endpoint, label, priv_b64 = row
            return did, endpoint, label, keypair_from_private_b64(priv_b64)
        finally:
            conn.close()

    def upsert_peer(self, agent_id: str, invitation: DIDCommInvitation) -> None:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO peers(agent_id, did, endpoint, public_key_b64, label)
                VALUES(?,?,?,?,?)
                ON CONFLICT(agent_id, did) DO UPDATE SET endpoint=excluded.endpoint, public_key_b64=excluded.public_key_b64, label=excluded.label
                """,
                (agent_id, invitation.did, invitation.endpoint, invitation.public_key, invitation.label),
            )
            conn.commit()
        finally:
            conn.close()

    def list_peers(self, agent_id: str) -> list[str]:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT did FROM peers WHERE agent_id=?", (agent_id,))
            return [r[0] for r in cur.fetchall()]
        finally:
            conn.close()

    def load_peers(self, agent_id: str) -> list[DIDCommInvitation]:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT did, endpoint, public_key_b64, label FROM peers WHERE agent_id=?", (agent_id,))
            rows = cur.fetchall()
            return [
                DIDCommInvitation(did=r[0], endpoint=r[1], public_key=r[2], label=r[3]) for r in rows
            ]
        finally:
            conn.close()

    def export_state(self, agent_id: str) -> dict:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT did, endpoint, label, private_key_b64 FROM agents WHERE agent_id=?", (agent_id,))
            agent = cur.fetchone()
            cur.execute("SELECT did, endpoint, public_key_b64, label FROM peers WHERE agent_id=?", (agent_id,))
            peers = cur.fetchall()
            return {
                "agent": agent,
                "peers": peers,
            }
        finally:
            conn.close()
