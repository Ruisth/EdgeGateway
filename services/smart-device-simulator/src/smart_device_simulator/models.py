"""Modelos de dados para o simulador de Smart Device.

Alinhados com o paper EdgeGateway_Paper.pdf (Seccao 4) — o simulador
gera heartbeat, geolocalizacao e timestamp a 1 Hz.
"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class GeoLocation(BaseModel):
    """Coordenadas WGS84."""

    lat: float = Field(..., ge=-90, le=90, description="Latitude WGS84")
    lon: float = Field(..., ge=-180, le=180, description="Longitude WGS84")


class SensorReading(BaseModel):
    """Leitura de sensores do smartwatch — payload MQTT."""

    device_uuid: str = Field(..., description="UUID do Smart Device")
    heartbeat_bpm: int = Field(..., ge=0, le=300, description="Batimento cardiaco (bpm)")
    geolocation: GeoLocation = Field(..., description="Localizacao GPS")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp UTC ISO 8601",
    )

    def to_mqtt_payload(self) -> str:
        """Serializa para JSON (payload MQTT)."""
        return self.model_dump_json()
