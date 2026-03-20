"""
Testes de conectividade MQTT para o broker Mosquitto C2DTA.

Requisitos:
    - pip install paho-mqtt pytest
    - Certificados gerados via certs/generate-certs.sh
    - Broker Mosquitto em execucao (docker compose up)

Execucao:
    pytest services/mosquitto/tests/test_mqtt_connectivity.py -v
"""

from __future__ import annotations

import json
import os
import ssl
import threading
import time
import uuid

import pytest

BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "8883"))

CERTS_DIR = os.path.join(os.path.dirname(__file__), "..", "certs")
CA_CERT = os.path.join(CERTS_DIR, "ca.crt")
EGW_CERT = os.path.join(CERTS_DIR, "edgegateway.crt")
EGW_KEY = os.path.join(CERTS_DIR, "edgegateway.key")


def _certs_exist() -> bool:
    return all(os.path.isfile(p) for p in (CA_CERT, EGW_CERT, EGW_KEY))


def _make_tls_context(certfile: str, keyfile: str) -> ssl.SSLContext:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.load_verify_locations(CA_CERT)
    ctx.load_cert_chain(certfile=certfile, keyfile=keyfile)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_REQUIRED
    return ctx


skip_no_certs = pytest.mark.skipif(
    not _certs_exist(),
    reason="Certificados TLS nao encontrados — execute certs/generate-certs.sh",
)


@skip_no_certs
class TestMQTTConnectivity:
    """Testes de conectividade TLS contra o broker Mosquitto."""

    def test_tls_connection(self):
        """Verifica que o EGW consegue conectar-se via TLS."""
        import paho.mqtt.client as mqtt

        connected = threading.Event()

        def on_connect(client, userdata, flags, rc, properties=None):
            assert rc == 0, f"Conexao falhou com codigo {rc}"
            connected.set()

        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id="test-egw",
        )
        client.tls_set_context(_make_tls_context(EGW_CERT, EGW_KEY))
        client.on_connect = on_connect
        client.connect(BROKER_HOST, BROKER_PORT)
        client.loop_start()

        assert connected.wait(timeout=10), "Timeout na conexao TLS"
        client.disconnect()
        client.loop_stop()

    def test_publish_subscribe_telemetry(self):
        """Verifica pub/sub no topico egw/<uuid>/telemetry."""
        import paho.mqtt.client as mqtt

        device_uuid = str(uuid.uuid4())
        topic = f"egw/{device_uuid}/telemetry"
        payload = json.dumps(
            {
                "device_uuid": device_uuid,
                "heartbeat_bpm": 72,
                "geolocation": {"lat": 38.7223, "lon": -9.1393},
                "timestamp": "2025-01-01T00:00:00Z",
            }
        )
        received = threading.Event()
        received_msg: dict = {}

        def on_message(client, userdata, msg):
            received_msg["topic"] = msg.topic
            received_msg["payload"] = json.loads(msg.payload.decode())
            received.set()

        # Subscriber (EGW)
        sub = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id="test-sub-egw",
        )
        sub.tls_set_context(_make_tls_context(EGW_CERT, EGW_KEY))
        sub.on_message = on_message
        sub.connect(BROKER_HOST, BROKER_PORT)
        sub.subscribe(topic, qos=1)
        sub.loop_start()

        time.sleep(1)  # garantir que a subscricao esta ativa

        # Publisher (SD) — usa certificado EGW para simplicidade nos testes
        pub = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id="test-pub-sd",
        )
        pub.tls_set_context(_make_tls_context(EGW_CERT, EGW_KEY))
        pub.connect(BROKER_HOST, BROKER_PORT)
        pub.loop_start()
        pub.publish(topic, payload, qos=1)

        assert received.wait(timeout=10), "Timeout a receber mensagem"
        assert received_msg["topic"] == topic
        assert received_msg["payload"]["heartbeat_bpm"] == 72
        assert received_msg["payload"]["device_uuid"] == device_uuid

        pub.disconnect()
        pub.loop_stop()
        sub.disconnect()
        sub.loop_stop()
