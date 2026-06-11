#!/usr/bin/env bash
set -euo pipefail

# Aplica a conexao MQTT do Ditto com validacao TLS ativa.
#
# Substitui o placeholder __CA_PEM__ em mqtt-connection.json pelo conteudo
# de services/mosquitto/certs/ca.crt (gerado por generate-certs.sh) e faz
# POST ao endpoint devops do Ditto.
#
# Variaveis (todas opcionais):
#   DITTO_URL                http://localhost:8080 por omissao
#   DITTO_DEVOPS_USER        devops por omissao
#   DITTO_DEVOPS_PASSWORD    lido do .env da raiz se nao definido

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
CA_CERT="${REPO_ROOT}/services/mosquitto/certs/ca.crt"
CONN_JSON="${SCRIPT_DIR}/mqtt-connection.json"

if [[ ! -f "${CA_CERT}" ]]; then
  echo "CA nao encontrada em ${CA_CERT}." >&2
  echo "Gerar primeiro: bash services/mosquitto/certs/generate-certs.sh" >&2
  exit 1
fi

if [[ -z "${DITTO_DEVOPS_PASSWORD:-}" && -f "${REPO_ROOT}/.env" ]]; then
  # shellcheck disable=SC1091
  set -a; source "${REPO_ROOT}/.env"; set +a
fi

: "${DITTO_URL:=http://localhost:8080}"
: "${DITTO_DEVOPS_USER:=devops}"
: "${DITTO_DEVOPS_PASSWORD:?DITTO_DEVOPS_PASSWORD not set (define no .env da raiz)}"

payload="$(CA_CERT="${CA_CERT}" CONN_JSON="${CONN_JSON}" python3 - <<'PY'
import json
import os

with open(os.environ["CA_CERT"]) as f:
    ca_pem = f.read()
with open(os.environ["CONN_JSON"]) as f:
    conn = f.read()

doc = json.loads(conn)
connection = doc["piggybackCommand"]["connection"]
if connection.get("ca") == "__CA_PEM__":
    connection["ca"] = ca_pem
print(json.dumps(doc))
PY
)"

echo "[+] A criar conexao MQTT no Ditto (${DITTO_URL}) com validateCertificates=true..."
curl -fsS -X POST \
  -u "${DITTO_DEVOPS_USER}:${DITTO_DEVOPS_PASSWORD}" \
  -H "Content-Type: application/json" \
  -d "${payload}" \
  "${DITTO_URL}/devops/piggyback/connectivity"
echo
echo "[OK] Conexao aplicada."
