#!/usr/bin/env bash
# =============================================================================
# Inicia a rede Hyperledger Fabric C2DTA
# =============================================================================
# 1. Gera material criptografico (cryptogen)
# 2. Gera bloco genesis (configtxgen)
# 3. Pode ser chamado antes de `docker compose up` na raiz

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FABRIC_DIR="$(dirname "$SCRIPT_DIR")"
CHANNEL_NAME="c2dta-channel"

echo "======================================================"
echo "  C2DTA — Gerar material criptografico Fabric"
echo "======================================================"

# ---- 1. Gerar crypto material via cryptogen ----
ORGS_DIR="${FABRIC_DIR}/organizations"
if [ -d "${ORGS_DIR}/ordererOrganizations/c2dta.example.com/orderers/orderer.c2dta.example.com/msp/signcerts" ]; then
    echo "[1/2] Material criptografico ja existe, a saltar..."
else
    echo "[1/2] A gerar material criptografico com cryptogen..."

    # Limpar diretorio de organizacoes existente (apenas estrutura vazia)
    rm -rf "${ORGS_DIR}"

    # Executar cryptogen dentro do container fabric-tools
    docker run --rm \
        -v "${FABRIC_DIR}/configtx:/configtx" \
        -v "${ORGS_DIR}:/organizations" \
        -w /configtx \
        hyperledger/fabric-tools:2.5 \
        cryptogen generate --config=crypto-config.yaml --output=/organizations

    echo "    Material criptografico gerado em ${ORGS_DIR}"
fi

# ---- 2. Gerar bloco genesis ----
ARTIFACTS_DIR="${FABRIC_DIR}/channel-artifacts"
mkdir -p "${ARTIFACTS_DIR}"

if [ -f "${ARTIFACTS_DIR}/${CHANNEL_NAME}.block" ]; then
    echo "[2/2] Bloco genesis ja existe, a saltar..."
else
    echo "[2/2] A gerar bloco genesis com configtxgen..."

    docker run --rm \
        -v "${FABRIC_DIR}/configtx:/configtx" \
        -v "${ORGS_DIR}:/configtx/../organizations" \
        -v "${ARTIFACTS_DIR}:/channel-artifacts" \
        -w /configtx \
        -e FABRIC_CFG_PATH=/configtx \
        hyperledger/fabric-tools:2.5 \
        configtxgen -profile C2DTAGenesis \
            -outputBlock /channel-artifacts/${CHANNEL_NAME}.block \
            -channelID ${CHANNEL_NAME}

    echo "    Bloco genesis gerado em ${ARTIFACTS_DIR}/${CHANNEL_NAME}.block"
fi

echo ""
echo "[OK] Material criptografico e bloco genesis prontos."
echo "     Execute 'docker compose up -d' na raiz do projeto."
