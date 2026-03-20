#!/usr/bin/env bash
set -euo pipefail

# SPDX-License-Identifier: Apache-2.0
#
# Bootstrap script for initialising the Yocto build environment for the
# Edge Gateway project. It aligns with the recommendations from EdgeGateway_Paper.pdf,
# preparing a dedicated build directory and guiding inclusion of the
# meta-edgegateway layer.

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

Yocto environment ready. Next steps suggested by the paper:
  - Update conf/bblayers.conf to include meta-edgegateway and BSP layers.
  - Configure conf/local.conf with security options (TPM, encryption) and AI packages.
  - Run: bitbake edgegateway-image
MSG
