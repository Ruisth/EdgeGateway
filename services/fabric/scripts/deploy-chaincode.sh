#!/usr/bin/env bash
# =============================================================================
# Deploy dos chaincodes C2DTA na rede Fabric
# =============================================================================
# Instala e aprova os chaincodes device-lifecycle e dataset-tracking
# em ambos os peers (ConsortiumOrg e OEMOrg).

set -euo pipefail

CHANNEL_NAME="c2dta-channel"
CC_LIFECYCLE="device-lifecycle"
CC_DATASET="dataset-tracking"
CC_VERSION="1.0"
CC_SEQUENCE="1"

echo "======================================================"
echo "  C2DTA — Deploy de chaincodes"
echo "======================================================"

echo "[1/4] A empacotar chaincodes..."
echo "NOTA: Execute dentro do container CLI:"
echo ""
echo "  # Device Lifecycle"
echo "  docker exec c2dta-fabric-cli peer lifecycle chaincode package ${CC_LIFECYCLE}.tar.gz \\"
echo "    --path /opt/gopath/src/github.com/chaincode/device-lifecycle \\"
echo "    --lang golang --label ${CC_LIFECYCLE}_${CC_VERSION}"
echo ""
echo "  # Dataset Tracking"
echo "  docker exec c2dta-fabric-cli peer lifecycle chaincode package ${CC_DATASET}.tar.gz \\"
echo "    --path /opt/gopath/src/github.com/chaincode/dataset-tracking \\"
echo "    --lang golang --label ${CC_DATASET}_${CC_VERSION}"
echo ""
echo "[2/4] A instalar nos peers..."
echo "  docker exec c2dta-fabric-cli peer lifecycle chaincode install ${CC_LIFECYCLE}.tar.gz"
echo ""
echo "[3/4] A aprovar e commit..."
echo "  peer lifecycle chaincode approveformyorg ..."
echo "  peer lifecycle chaincode commit ..."
echo ""
echo "[4/4] Verificar instalacao..."
echo "  peer lifecycle chaincode querycommitted --channelID ${CHANNEL_NAME}"
echo ""
echo "[OK] Siga os comandos acima para completar o deploy."
