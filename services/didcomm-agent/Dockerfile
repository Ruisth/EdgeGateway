# syntax=docker/dockerfile:1.7

# ---------- build stage ----------
FROM python:3.12-slim AS builder

WORKDIR /build

COPY pyproject.toml README.md requirements.txt ./
COPY src/ ./src/

RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt \
    && /opt/venv/bin/pip install --no-cache-dir .[api]

# ---------- runtime stage ----------
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app \
    && useradd --system --gid app --home-dir /app --shell /usr/sbin/nologin app \
    && mkdir -p /data \
    && chown app:app /data

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DIDCOMM_DB_PATH=/data/didcomm.sqlite

VOLUME ["/data"]

WORKDIR /app
USER app
EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=3 \
    CMD curl --fail --silent http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "didcomm_agent.api:app", "--host", "0.0.0.0", "--port", "8000"]
