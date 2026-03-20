"""Configuracao do simulador via variaveis de ambiente."""

from __future__ import annotations

import os
import uuid


def get_config() -> dict:
    """Retorna configuracao do simulador a partir de variaveis de ambiente."""
    return {
        "device_uuid": os.getenv("SD_UUID", str(uuid.uuid4())),
        "broker_host": os.getenv("MQTT_BROKER_HOST", "localhost"),
        "broker_port": int(os.getenv("MQTT_BROKER_PORT", "8883")),
        "ca_cert": os.getenv("MQTT_CA_CERT", "certs/ca.crt"),
        "client_cert": os.getenv("MQTT_CLIENT_CERT"),
        "client_key": os.getenv("MQTT_CLIENT_KEY"),
        "publish_interval_ms": int(os.getenv("SD_PUBLISH_INTERVAL_MS", "1000")),
        "initial_heartbeat": int(os.getenv("SD_INITIAL_HEARTBEAT", "72")),
        "initial_lat": float(os.getenv("SD_INITIAL_LAT", "38.7223")),
        "initial_lon": float(os.getenv("SD_INITIAL_LON", "-9.1393")),
    }
