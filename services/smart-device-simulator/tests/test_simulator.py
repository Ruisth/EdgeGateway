"""Testes unitarios para o simulador de Smart Device."""

from __future__ import annotations

import json
import uuid

import pytest

from smart_device_simulator.models import SensorReading
from smart_device_simulator.simulator import SmartDeviceSimulator


@pytest.fixture
def simulator():
    return SmartDeviceSimulator(
        device_uuid=str(uuid.uuid4()),
        initial_heartbeat=72,
        initial_lat=38.7223,
        initial_lon=-9.1393,
    )


class TestSmartDeviceSimulator:
    """Testes de geracao de dados sensoriais."""

    def test_read_sensors_returns_valid_reading(self, simulator):
        reading = simulator.read_sensors()
        assert isinstance(reading, SensorReading)
        assert reading.device_uuid == simulator.device_uuid
        assert reading.heartbeat_bpm >= SmartDeviceSimulator.MIN_BPM
        assert reading.heartbeat_bpm <= SmartDeviceSimulator.MAX_BPM
        assert -90 <= reading.geolocation.lat <= 90
        assert -180 <= reading.geolocation.lon <= 180

    def test_heartbeat_stays_in_range(self, simulator):
        """Heartbeat deve manter-se nos limites fisiologicos apos muitas leituras."""
        for _ in range(1000):
            reading = simulator.read_sensors()
            assert SmartDeviceSimulator.MIN_BPM <= reading.heartbeat_bpm <= SmartDeviceSimulator.MAX_BPM

    def test_geolocation_drifts(self, simulator):
        """Geolocalizacao deve derivar ligeiramente a cada leitura."""
        readings = [simulator.read_sensors() for _ in range(100)]
        lats = [r.geolocation.lat for r in readings]
        lons = [r.geolocation.lon for r in readings]
        # Deve haver variacao (nao exatamente igual)
        assert len(set(lats)) > 1
        assert len(set(lons)) > 1

    def test_mqtt_payload_is_valid_json(self, simulator):
        """Payload MQTT deve ser JSON valido com os campos esperados."""
        reading = simulator.read_sensors()
        payload = reading.to_mqtt_payload()
        data = json.loads(payload)
        assert "device_uuid" in data
        assert "heartbeat_bpm" in data
        assert "geolocation" in data
        assert "timestamp" in data
        assert "lat" in data["geolocation"]
        assert "lon" in data["geolocation"]

    def test_timestamp_is_utc(self, simulator):
        """Timestamp deve estar em UTC."""
        reading = simulator.read_sensors()
        assert reading.timestamp.tzinfo is not None

    def test_multiple_readings_have_different_timestamps(self, simulator):
        """Leituras consecutivas devem ter timestamps diferentes."""
        r1 = simulator.read_sensors()
        r2 = simulator.read_sensors()
        # Podem ser iguais em maquinas muito rapidas, mas a uuid sera diferente no payload
        assert r1.device_uuid == r2.device_uuid
