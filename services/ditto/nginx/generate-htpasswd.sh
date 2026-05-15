#!/usr/bin/env bash
set -euo pipefail

# Generates services/ditto/nginx/nginx.htpasswd from credentials in the
# repo-root .env file. Run before `docker compose up`.
#
# Required vars in .env:
#   DITTO_USER, DITTO_PASS
#   DITTO_DEVOPS_USER, DITTO_DEVOPS_PASSWORD

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/../../../.env"
OUT_FILE="${SCRIPT_DIR}/nginx.htpasswd"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing ${ENV_FILE}. Copy .env.example to .env and fill in credentials." >&2
  exit 1
fi

# shellcheck disable=SC1090
set -a; source "${ENV_FILE}"; set +a

: "${DITTO_USER:?DITTO_USER not set in .env}"
: "${DITTO_PASS:?DITTO_PASS not set in .env}"
: "${DITTO_DEVOPS_USER:?DITTO_DEVOPS_USER not set in .env}"
: "${DITTO_DEVOPS_PASSWORD:?DITTO_DEVOPS_PASSWORD not set in .env}"

if ! command -v htpasswd >/dev/null 2>&1; then
  echo "htpasswd not found. Install apache2-utils (Debian/Ubuntu) or httpd-tools (RHEL)." >&2
  exit 1
fi

umask 077
htpasswd -nbB "${DITTO_USER}"        "${DITTO_PASS}"             >  "${OUT_FILE}"
htpasswd -nbB "${DITTO_DEVOPS_USER}" "${DITTO_DEVOPS_PASSWORD}"  >> "${OUT_FILE}"

echo "Wrote ${OUT_FILE}"
