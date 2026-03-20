"""Cliente MQTT com TLS para publicacao de telemetria do Smart Device.

Publica leituras de sensores no topico ``egw/<uuid>/telemetry`` com QoS 1,
conforme a hierarquia de topicos definida na arquitetura C2DTA.
"""

from __future__ import annotations

import logging
import signal
import ssl
import time

import paho.mqtt.client as mqtt

from smart_device_simulator.simulator import SmartDeviceSimulator

logger = logging.getLogger(__name__)


class MQTTPublisher:
    """Publica telemetria do SD via MQTT/TLS."""

    def __init__(
        self,
        simulator: SmartDeviceSimulator,
        broker_host: str = "localhost",
        broker_port: int = 8883,
        ca_cert: str | None = None,
        client_cert: str | None = None,
        client_key: str | None = None,
        publish_interval_ms: int = 1000,
    ) -> None:
        self.simulator = simulator
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.publish_interval_ms = publish_interval_ms
        self._running = False

        self._client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"sd-{simulator.device_uuid}",
        )

        # Configurar TLS se certificados fornecidos
        if ca_cert:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.load_verify_locations(ca_cert)
            if client_cert and client_key:
                ctx.load_cert_chain(certfile=client_cert, keyfile=client_key)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_REQUIRED
            self._client.tls_set_context(ctx)

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_publish = self._on_publish

        self._topic = f"egw/{simulator.device_uuid}/telemetry"

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            logger.info("Conectado ao broker MQTT %s:%d", self.broker_host, self.broker_port)
        else:
            logger.error("Falha na conexao MQTT, codigo: %d", rc)

    def _on_disconnect(self, client, userdata, flags, rc, properties=None):
        logger.warning("Desconectado do broker MQTT (rc=%s)", rc)

    def _on_publish(self, client, userdata, mid, rc=None, properties=None):
        logger.debug("Mensagem publicada (mid=%d)", mid)

    def start(self) -> None:
        """Inicia publicacao de telemetria em loop."""
        self._running = True

        # Graceful shutdown
        def _handle_signal(signum, frame):
            logger.info("Sinal %d recebido, a parar...", signum)
            self._running = False

        signal.signal(signal.SIGTERM, _handle_signal)
        signal.signal(signal.SIGINT, _handle_signal)

        self._client.connect(self.broker_host, self.broker_port)
        self._client.loop_start()

        interval_s = self.publish_interval_ms / 1000.0
        logger.info(
            "A publicar telemetria em %s a cada %.1fs",
            self._topic,
            interval_s,
        )

        try:
            while self._running:
                reading = self.simulator.read_sensors()
                payload = reading.to_mqtt_payload()
                result = self._client.publish(self._topic, payload, qos=1)
                logger.debug(
                    "Publicado: bpm=%d lat=%.7f lon=%.7f",
                    reading.heartbeat_bpm,
                    reading.geolocation.lat,
                    reading.geolocation.lon,
                )
                time.sleep(interval_s)
        finally:
            self._client.disconnect()
            self._client.loop_stop()
            logger.info("Publicador MQTT parado.")

    def stop(self) -> None:
        """Para a publicacao de telemetria."""
        self._running = False
