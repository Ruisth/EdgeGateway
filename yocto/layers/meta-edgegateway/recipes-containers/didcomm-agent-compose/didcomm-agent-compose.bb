SUMMARY = "Deploy DIDComm Agent via docker-compose with systemd"
DESCRIPTION = "Installs docker-compose manifest and a systemd unit to run the EdgeGateway DIDComm Agent container at boot."
LICENSE = "CLOSED"

inherit systemd

SRC_URI = " \
    file://didcomm-agent/docker-compose.yml \
    file://didcomm-agent.service \
"

S = "${WORKDIR}"

SYSTEMD_SERVICE:${PN} = "didcomm-agent.service"

RDEPENDS:${PN} = "docker docker-compose"

do_install() {
    # Compose manifest location
    install -d ${D}/opt/didcomm-agent
    install -m 0644 ${WORKDIR}/didcomm-agent/docker-compose.yml ${D}/opt/didcomm-agent/docker-compose.yml

    # Data directory for persistent state
    install -d ${D}/var/lib/didcomm-agent

    # Systemd unit
    install -d ${D}${systemd_system_unitdir}
    install -m 0644 ${WORKDIR}/didcomm-agent.service ${D}${systemd_system_unitdir}/didcomm-agent.service
}

FILES:${PN} += " \
    /opt/didcomm-agent/docker-compose.yml \
    ${systemd_system_unitdir}/didcomm-agent.service \
    /var/lib/didcomm-agent \
"

SYSTEMD_AUTO_ENABLE:${PN} = "enable"
