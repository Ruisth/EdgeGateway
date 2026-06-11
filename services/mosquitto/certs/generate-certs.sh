#!/usr/bin/env bash
# =============================================================================
# Gera certificados self-signed para desenvolvimento
# =============================================================================
# Cria:
#   ca.crt / ca.key             — Autoridade Certificadora (CA)
#   server.crt / server.key     — Certificado do broker Mosquitto (com SAN)
#   edgegateway.crt / .key      — Certificado do Edge Gateway
#   ditto-connectivity.crt/.key — Certificado do Eclipse Ditto
#   <uuid>.crt / <uuid>.key     — Certificado de um Smart Device (argumento $1)
#
# O certificado do broker inclui subjectAltName (DNS:mosquitto,
# DNS:localhost, IP:127.0.0.1) para que clientes com verificacao de
# hostname ativa (default do simulador) validem a ligacao tanto dentro
# da rede compose como em execucao local.
#
# Utilizacao:
#   ./generate-certs.sh                     # gera CA + servidor + EGW + Ditto
#   ./generate-certs.sh <device-uuid>       # gera tambem certificado do SD

set -euo pipefail
umask 077

CERT_DIR="$(cd "$(dirname "$0")" && pwd)"
DAYS=3650
KEY_BITS=4096
SUBJ_BASE="/O=C2DTA/OU=EdgeGateway"
SERVER_SAN="DNS:mosquitto,DNS:localhost,IP:127.0.0.1"

# ---- CA -------------------------------------------------------------------
if [ ! -f "$CERT_DIR/ca.key" ]; then
  echo "[+] A gerar CA..."
  openssl genrsa -out "$CERT_DIR/ca.key" $KEY_BITS
  openssl req -new -x509 -days $DAYS -key "$CERT_DIR/ca.key" \
    -out "$CERT_DIR/ca.crt" \
    -subj "$SUBJ_BASE/CN=C2DTA-CA"
fi

# ---- Funcao utilitaria para gerar certificado assinado pela CA -----------
# generate_cert <nome-ficheiro> <CN> [SAN]
generate_cert() {
  local name="$1"
  local cn="$2"
  local san="${3:-}"
  if [ -f "$CERT_DIR/${name}.crt" ]; then
    if [ -n "$san" ] && ! openssl x509 -in "$CERT_DIR/${name}.crt" -noout -text \
        | grep -q "Subject Alternative Name"; then
      echo "[!] ${name}.crt existe mas NAO tem SAN — apagar e re-executar" \
           "este script para regenerar com hostname verification." >&2
    else
      echo "[=] Certificado ${name} ja existe, a saltar."
    fi
    return
  fi
  echo "[+] A gerar certificado: ${name} (CN=${cn})..."
  openssl genrsa -out "$CERT_DIR/${name}.key" $KEY_BITS
  openssl req -new -key "$CERT_DIR/${name}.key" \
    -out "$CERT_DIR/${name}.csr" \
    -subj "$SUBJ_BASE/CN=${cn}"
  if [ -n "$san" ]; then
    openssl x509 -req -days $DAYS \
      -in "$CERT_DIR/${name}.csr" \
      -CA "$CERT_DIR/ca.crt" -CAkey "$CERT_DIR/ca.key" -CAcreateserial \
      -extfile <(printf "subjectAltName=%s" "$san") \
      -out "$CERT_DIR/${name}.crt"
  else
    openssl x509 -req -days $DAYS \
      -in "$CERT_DIR/${name}.csr" \
      -CA "$CERT_DIR/ca.crt" -CAkey "$CERT_DIR/ca.key" -CAcreateserial \
      -out "$CERT_DIR/${name}.crt"
  fi
  rm -f "$CERT_DIR/${name}.csr"
  chmod 600 "$CERT_DIR/${name}.key"
  chmod 644 "$CERT_DIR/${name}.crt"
}

# ---- Servidor (broker Mosquitto) — SAN para hostname verification --------
generate_cert "server" "mosquitto" "$SERVER_SAN"

# ---- Edge Gateway --------------------------------------------------------
generate_cert "edgegateway" "edgegateway"

# ---- Eclipse Ditto Connectivity ------------------------------------------
generate_cert "ditto-connectivity" "ditto-connectivity"

# ---- Smart Device (opcional, UUID passado como argumento) ----------------
if [ -n "${1:-}" ]; then
  generate_cert "$1" "$1"
  echo "[OK] Certificado do SD $1 gerado em $CERT_DIR/$1.crt"
fi

chmod 600 "$CERT_DIR"/ca.key 2>/dev/null || true

echo "[OK] Certificados gerados em $CERT_DIR"
ls -la "$CERT_DIR"/*.crt 2>/dev/null || true
