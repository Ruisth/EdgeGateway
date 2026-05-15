#!/usr/bin/env python3
"""Ponto de entrada CLI para o simulador de smartwatch C2DTA.

Exemplo:
    SD_UUID=abc-123 MQTT_BROKER_HOST=localhost python run_simulator.py
"""

from __future__ import annotations

import logging
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from smart_device_simulator.config import get_config
from smart_device_simulator.mqtt_publisher import MQTTPublisher
from smart_device_simulator.simulator import SmartDeviceSimulator


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    )
    cfg = get_config()
    logger = logging.getLogger("smart-device-simulator")

    logger.info("UUID do dispositivo: %s", cfg["device_uuid"])

    simulator = SmartDeviceSimulator(
        device_uuid=cfg["device_uuid"],
        initial_heartbeat=cfg["initial_heartbeat"],
        initial_lat=cfg["initial_lat"],
        initial_lon=cfg["initial_lon"],
    )

    publisher = MQTTPublisher(
        simulator=simulator,
        broker_host=cfg["broker_host"],
        broker_port=cfg["broker_port"],
        ca_cert=cfg["ca_cert"],
        client_cert=cfg["client_cert"],
        client_key=cfg["client_key"],
        publish_interval_ms=cfg["publish_interval_ms"],
    )

    logger.info("A iniciar publicacao MQTT...")
    publisher.start()


if __name__ == "__main__":
    main()
