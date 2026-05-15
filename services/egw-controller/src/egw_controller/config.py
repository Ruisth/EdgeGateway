"""Configuracao do EGW Controller via variaveis de ambiente."""

from __future__ import annotations

import os


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Required environment variable {name} is not set. "
            "Copy .env.example to .env and fill in the credentials."
        )
    return value


def get_config() -> dict:
    """Retorna configuracao do EGW Controller."""
    return {
        # Ditto
        "ditto_url": os.getenv("DITTO_URL", "http://localhost:8080"),
        "ditto_user": _require("DITTO_USER"),
        "ditto_pass": _require("DITTO_PASS"),
        # MQTT
        "mqtt_broker_host": os.getenv("MQTT_BROKER_HOST", "localhost"),
        "mqtt_broker_port": int(os.getenv("MQTT_BROKER_PORT", "8883")),
        # IPFS
        "ipfs_api_url": os.getenv("IPFS_API_URL", "http://localhost:5001"),
        # ACA-Py
        "acapy_consortium_url": os.getenv("ACAPY_CONSORTIUM_URL", "http://localhost:8021"),
        "acapy_oem_url": os.getenv("ACAPY_OEM_URL", "http://localhost:8031"),
        "acapy_egw_url": os.getenv("ACAPY_EGW_URL", "http://localhost:8061"),
        # Fabric
        "fabric_peer_url": os.getenv("FABRIC_PEER_URL", "localhost:7051"),
        "fabric_channel": os.getenv("FABRIC_CHANNEL", "c2dta-channel"),
        # DIDComm
        "didcomm_agent_url": os.getenv("DIDCOMM_AGENT_URL", "http://localhost:8000"),
        # Persistencia
        "db_path": os.getenv("EGW_DB_PATH", ""),
        # Dataset
        "dataset_interval_s": int(os.getenv("EGW_DATASET_INTERVAL_S", "86400")),
    }
