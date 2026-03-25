SUMMARY = "Deploy Eclipse Mosquitto via docker-compose with systemd"
DESCRIPTION = "Installs docker-compose manifest and a systemd unit to run the C2DTA MQTT broker at boot."
LICENSE = "CLOSED"

inherit systemd

SRC_URI = " \
    file://mosquitto/docker-compose.yml \
    file://mosquitto.service \
"

S = "${WORKDIR}"

SYSTEMD_SERVICE:${PN} = "mosquitto.service"

RDEPENDS:${PN} = "docker docker-compose"

do_install() {
    # Compose manifest location
    install -d ${D}/opt/mosquitto
    install -m 0644 ${WORKDIR}/mosquitto/docker-compose.yml ${D}/opt/mosquitto/docker-compose.yml

    # Data directory for persistent state
    install -d ${D}/var/lib/mosquitto

    # Systemd unit
    install -d ${D}${systemd_system_unitdir}
    install -m 0644 ${WORKDIR}/mosquitto.service ${D}${systemd_system_unitdir}/mosquitto.service
}

FILES:${PN} += " \
    /opt/mosquitto/docker-compose.yml \
    ${systemd_system_unitdir}/mosquitto.service \
    /var/lib/mosquitto \
"

SYSTEMD_AUTO_ENABLE:${PN} = "enable"
