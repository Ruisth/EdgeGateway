# syntax=docker/dockerfile:1.7

# ---------- build stage ----------
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt pyproject.toml ./
COPY src/ ./src/

RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ---------- runtime stage ----------
FROM python:3.12-slim

RUN groupadd --system app \
    && useradd --system --gid app --home-dir /app --shell /usr/sbin/nologin app

COPY --from=builder /opt/venv /opt/venv
COPY src/ /app/src/
COPY examples/ /app/examples/

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH=/app/src \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SD_PUBLISH_INTERVAL_MS=1000 \
    MQTT_BROKER_HOST=mosquitto \
    MQTT_BROKER_PORT=8883

WORKDIR /app
USER app

CMD ["python", "examples/run_simulator.py"]
