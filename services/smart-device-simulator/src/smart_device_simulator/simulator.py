"""Simulador de Smart Device (smartwatch) para a arquitetura C2DTA.

Gera dados sensoriais realistas a 1 Hz conforme o paper:
- heartbeat_bpm: random walk em torno de baseline (55-180 bpm)
- geolocation: drift gaussiano em torno de posicao inicial
- timestamp: UTC ISO 8601
"""

from __future__ import annotations

import random
from datetime import UTC, datetime

from smart_device_simulator.models import GeoLocation, SensorReading


class SmartDeviceSimulator:
    """Simula um smartwatch com sensor de heartbeat e GPS."""

    # Limites fisiologicos
    MIN_BPM = 40
    MAX_BPM = 200

    # Parametros de drift
    BPM_STEP_MAX = 3
    GEO_DRIFT_STD = 0.00005  # ~5.5 metros

    def __init__(
        self,
        device_uuid: str,
        initial_heartbeat: int = 72,
        initial_lat: float = 38.7223,
        initial_lon: float = -9.1393,
    ) -> None:
        self.device_uuid = device_uuid
        self._heartbeat = initial_heartbeat
        self._lat = initial_lat
        self._lon = initial_lon

    def _next_heartbeat(self) -> int:
        """Random walk com mean-reversion suave."""
        step = random.randint(-self.BPM_STEP_MAX, self.BPM_STEP_MAX)
        # Mean-reversion suave para o centro do range normal
        if self._heartbeat > 100:
            step -= 1
        elif self._heartbeat < 60:
            step += 1
        self._heartbeat = max(self.MIN_BPM, min(self.MAX_BPM, self._heartbeat + step))
        return self._heartbeat

    def _next_geolocation(self) -> GeoLocation:
        """Drift gaussiano simulando movimento de pedestrian."""
        self._lat += random.gauss(0, self.GEO_DRIFT_STD)
        self._lon += random.gauss(0, self.GEO_DRIFT_STD)
        # Clamp aos limites validos
        self._lat = max(-90.0, min(90.0, self._lat))
        self._lon = max(-180.0, min(180.0, self._lon))
        return GeoLocation(lat=round(self._lat, 7), lon=round(self._lon, 7))

    def read_sensors(self) -> SensorReading:
        """Gera uma leitura de sensores."""
        return SensorReading(
            device_uuid=self.device_uuid,
            heartbeat_bpm=self._next_heartbeat(),
            geolocation=self._next_geolocation(),
            timestamp=datetime.now(UTC),
        )
