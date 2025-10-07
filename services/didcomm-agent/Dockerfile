# Simple container for the DIDComm API
FROM python:3.12-slim

WORKDIR /app

# System deps (none required beyond Python stdlib)

COPY ./pyproject.toml ./README.md ./
COPY ./src ./src
COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir .[api]

ENV DIDCOMM_DB_PATH=/data/didcomm.sqlite
RUN mkdir -p /data
VOLUME ["/data"]

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "didcomm_agent.api:app", "--host", "0.0.0.0", "--port", "8000"]
