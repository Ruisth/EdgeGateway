#!/usr/bin/env bash
# =============================================================================
# Gera certificados self-signed para desenvolvimento
# =============================================================================
# Cria:
#   ca.crt / ca.key             — Autoridade Certificadora (CA)
#   server.crt / server.key     — Certificado do broker Mosquitto
#   edgegateway.crt / .key      — Certificado do Edge Gateway
#   ditto-connectivity.crt/.key — Certificado do Eclipse Ditto
#   <uuid>.crt / <uuid>.key     — Certificado de um Smart Device (argumento $1)
#
# Utilizacao:
#   ./generate-certs.sh                     # gera CA + servidor + EGW + Ditto
#   ./generate-certs.sh <device-uuid>       # gera tambem certificado do SD

set -euo pipefail

CERT_DIR="$(cd "$(dirname "$0")" && pwd)"
DAYS=3650
SUBJ_BASE="/O=C2DTA/OU=EdgeGateway"

# ---- CA -------------------------------------------------------------------
if [ ! -f "$CERT_DIR/ca.key" ]; then
  echo "[+] A gerar CA..."
  openssl genrsa -out "$CERT_DIR/ca.key" 4096
  openssl req -new -x509 -days $DAYS -key "$CERT_DIR/ca.key" \
    -out "$CERT_DIR/ca.crt" \
    -subj "$SUBJ_BASE/CN=C2DTA-CA"
fi

# ---- Funcao utilitaria para gerar certificado assinado pela CA -----------
generate_cert() {
  local name="$1"
  local cn="$2"
  if [ -f "$CERT_DIR/${name}.crt" ]; then
    echo "[=] Certificado ${name} ja existe, a saltar."
    return
  fi
  echo "[+] A gerar certificado: ${name} (CN=${cn})..."
  openssl genrsa -out "$CERT_DIR/${name}.key" 2048
  openssl req -new -key "$CERT_DIR/${name}.key" \
    -out "$CERT_DIR/${name}.csr" \
    -subj "$SUBJ_BASE/CN=${cn}"
  openssl x509 -req -days $DAYS \
    -in "$CERT_DIR/${name}.csr" \
    -CA "$CERT_DIR/ca.crt" -CAkey "$CERT_DIR/ca.key" -CAcreateserial \
    -out "$CERT_DIR/${name}.crt"
  rm -f "$CERT_DIR/${name}.csr"
}

# ---- Servidor (broker Mosquitto) -----------------------------------------
generate_cert "server" "mosquitto"

# ---- Edge Gateway --------------------------------------------------------
generate_cert "edgegateway" "edgegateway"

# ---- Eclipse Ditto Connectivity ------------------------------------------
generate_cert "ditto-connectivity" "ditto-connectivity"

# ---- Smart Device (opcional, UUID passado como argumento) ----------------
if [ -n "${1:-}" ]; then
  generate_cert "$1" "$1"
  echo "[OK] Certificado do SD $1 gerado em $CERT_DIR/$1.crt"
fi

echo "[OK] Certificados gerados em $CERT_DIR"
ls -la "$CERT_DIR"/*.crt 2>/dev/null || true
