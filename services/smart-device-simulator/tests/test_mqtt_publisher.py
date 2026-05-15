"""Testes de integracao para o publicador MQTT.

Requer broker Mosquitto em execucao e certificados gerados.
"""

from __future__ import annotations

import os

import pytest

from smart_device_simulator.mqtt_publisher import MQTTPublisher
from smart_device_simulator.simulator import SmartDeviceSimulator

CERTS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "mosquitto", "certs"
)

skip_no_broker = pytest.mark.skipif(
    not os.path.isfile(os.path.join(CERTS_DIR, "ca.crt")),
    reason="Certificados ou broker nao disponiveis",
)


@skip_no_broker
class TestMQTTPublisher:
    """Testes de integracao com o broker MQTT."""

    def test_publisher_initializes(self):
        sim = SmartDeviceSimulator(device_uuid="test-uuid")
        pub = MQTTPublisher(
            simulator=sim,
            broker_host="localhost",
            broker_port=8883,
            ca_cert=os.path.join(CERTS_DIR, "ca.crt"),
            client_cert=os.path.join(CERTS_DIR, "edgegateway.crt"),
            client_key=os.path.join(CERTS_DIR, "edgegateway.key"),
        )
        assert pub._topic == "egw/test-uuid/telemetry"
        assert pub._running is False
