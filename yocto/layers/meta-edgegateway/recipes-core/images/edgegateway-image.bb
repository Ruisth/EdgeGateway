# SPDX-License-Identifier: MIT

require recipes-core/images/core-image-minimal.bb

SUMMARY = "Imagem de referência do Edge Gateway"
DESCRIPTION = "Imagem alinhada ao EdgeGateway_Paper.pdf com conectividade segura, runtime de IA, \ 
observabilidade e agentes blockchain."

IMAGE_FEATURES += "ssh-server-dropbear package-management"

CORE_IMAGE_EXTRA_INSTALL += " \
    containerd \
    docker \
    docker-compose \
    python3 \
    chrony \
    curl \
    jq \
    rsync \
    iproute2 \
    iptables \
    coreutils \
    mosquitto \
    nats-server \
    onnxruntime \
    tensorflow-lite \
    prometheus-node-exporter \
    grafana-agent \
    fluent-bit \
    tpm2-tools \
    openssl \
    openssh-sftp-server \
"

LICENSE = "MIT"
