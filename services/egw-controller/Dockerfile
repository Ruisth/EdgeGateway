FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY pyproject.toml .

RUN pip install --no-cache-dir -e .

EXPOSE 8090

CMD ["uvicorn", "egw_controller.api:app", "--host", "0.0.0.0", "--port", "8090"]
