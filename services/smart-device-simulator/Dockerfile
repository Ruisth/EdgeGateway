FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY examples/ examples/

ENV SD_PUBLISH_INTERVAL_MS=1000
ENV MQTT_BROKER_HOST=mosquitto
ENV MQTT_BROKER_PORT=8883

CMD ["python", "examples/run_simulator.py"]
