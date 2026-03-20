#!/usr/bin/env bash
# =============================================================================
# Inicia a rede Hyperledger Fabric C2DTA
# =============================================================================
# 1. Gera material criptografico (se nao existir)
# 2. Cria o bloco genesis
# 3. Inicia os containers
# 4. Cria e junta peers ao canal c2dta-channel

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FABRIC_DIR="$(dirname "$SCRIPT_DIR")"
CHANNEL_NAME="c2dta-channel"

echo "======================================================"
echo "  C2DTA — Iniciar rede Hyperledger Fabric"
echo "======================================================"

# 1. Iniciar containers
echo "[1/3] A iniciar containers..."
cd "$FABRIC_DIR"
docker compose up -d

echo "[2/3] A aguardar que os peers arranquem..."
sleep 5

# 3. Criar canal (via osnadmin)
echo "[3/3] A criar canal ${CHANNEL_NAME}..."
echo "NOTA: Execute os comandos de criacao de canal manualmente ou"
echo "      use o script deploy-chaincode.sh apos a rede estar pronta."
echo ""
echo "Comandos de referencia:"
echo "  # Gerar bloco genesis:"
echo "  configtxgen -profile C2DTAGenesis -outputBlock ./channel-artifacts/${CHANNEL_NAME}.block -channelID ${CHANNEL_NAME}"
echo ""
echo "  # Criar canal via osnadmin:"
echo "  osnadmin channel join --channelID ${CHANNEL_NAME} --config-block ./channel-artifacts/${CHANNEL_NAME}.block -o localhost:7053 --ca-file ..."
echo ""
echo "[OK] Rede Fabric C2DTA iniciada."
docker compose ps
