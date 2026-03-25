# SPDX-License-Identifier: Apache-2.0

require recipes-core/images/core-image-minimal.bb

SUMMARY = "Imagem de referência do Edge Gateway — Consumer-Controlled Digital Twin Architecture (C2DTA)"
DESCRIPTION = "Imagem alinhada ao paper C2DTA (Pinto et al., 2025, DOI: 10.1016/j.bcra.2025.100342). \
Inclui: ACA-py (Hyperledger Aries), Eclipse Ditto, Eclipse Mosquitto, Hyperledger Fabric SDK, \
IPFS (Kubo) e W3C WoT — stack definitivo do paper. \
NOTA: didcomm-agent-compose foi removido; é substituído pelo agente ACA-py (aries-egw-agent)."

IMAGE_FEATURES += "ssh-server-dropbear package-management"

CORE_IMAGE_EXTRA_INSTALL += " \
    containerd \
    docker \
    docker-compose \
    \
    python3 \
    python3-pip \
    python3-aries-cloudagent \
    python3-fabric-sdk \
    \
    eclipse-mosquitto \
    \
    eclipse-ditto \
    \
    kubo \
    \
    chrony \
    curl \
    jq \
    rsync \
    iproute2 \
    iptables \
    coreutils \
    openssl \
    openssh-sftp-server \
    \
    tpm2-tools \
    tpm2-abrmd \
    \
    prometheus-node-exporter \
    fluent-bit \
"

# Componentes removidos vs versão anterior:
#   didcomm-agent-compose → substituído por python3-aries-cloudagent (ACA-py)
#   nats-server            → não usado no stack C2DTA
#   onnxruntime            → movido para Fase 3 (federated learning, opcional)
#   tensorflow-lite        → movido para Fase 3 (federated learning, opcional)
#   grafana-agent          → substituído por fluent-bit + prometheus-node-exporter

# Notas de implementação:
#   python3-aries-cloudagent: receita a criar em recipes-python/python3-aries-cloudagent_*.bb
#   python3-fabric-sdk:       receita a criar em recipes-python/python3-fabric-sdk_*.bb
#   eclipse-mosquitto:        disponível em meta-openembedded/meta-networking
#   eclipse-ditto:            receita a criar em recipes-connectivity/eclipse-ditto_*.bb
#                             (docker-compose com Ditto services: things, connectivity, gateway, search, policies)
#   kubo (IPFS):              receita a criar em recipes-connectivity/kubo_*.bb

LICENSE = "Apache-2.0"
