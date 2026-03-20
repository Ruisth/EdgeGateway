#!/usr/bin/env bash
# =============================================================================
# Para a rede Hyperledger Fabric C2DTA
# =============================================================================

set -euo pipefail

FABRIC_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "======================================================"
echo "  C2DTA — Parar rede Hyperledger Fabric"
echo "======================================================"

cd "$FABRIC_DIR"
docker compose down -v

echo "[OK] Rede Fabric C2DTA parada e volumes removidos."
