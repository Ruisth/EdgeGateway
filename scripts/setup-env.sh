#!/usr/bin/env bash
set -euo pipefail

# SPDX-License-Identifier: MIT
#
# Bootstrap script for initializing the Yocto build environment for the
# Edge Gateway project. It aligns with as recomendações do EdgeGateway_Paper.pdf,
# preparando um diretório de build dedicado e orientando a inclusão da camada
# meta-edgegateway.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POKY_DIR="${REPO_ROOT}/yocto/poky"
BUILD_DIR="${REPO_ROOT}/yocto/build"

if [[ ! -d "${POKY_DIR}" ]]; then
  echo "Poky directory not found at ${POKY_DIR}." >&2
  echo "Clone Yocto Poky: git submodule add git://git.yoctoproject.org/poky yocto/poky" >&2
  exit 1
fi

source "${POKY_DIR}/oe-init-build-env" "${BUILD_DIR}"

cat <<"MSG"

Yocto environment ready. Next steps sugeridos pelo paper:
  - Atualize conf/bblayers.conf para incluir meta-edgegateway e camadas BSP.
  - Configure conf/local.conf com opções de segurança (TPM, criptografia) e pacotes de IA.
  - Execute: bitbake edgegateway-image
MSG
