SUMMARY = "EGW Controller Docker Compose"
DESCRIPTION = "Orquestrador central dos 8 use cases da arquitetura C2DTA."
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = " \
    file://docker-compose.yml \
    file://egw-controller.service \
"

inherit systemd

SYSTEMD_SERVICE:${PN} = "egw-controller.service"

do_install() {
    # Compose file
    install -d ${D}/opt/edgegateway/egw-controller
    install -m 0644 ${WORKDIR}/docker-compose.yml ${D}/opt/edgegateway/egw-controller/

    # Systemd unit
    install -d ${D}${systemd_unitdir}/system
    install -m 0644 ${WORKDIR}/egw-controller.service ${D}${systemd_unitdir}/system/
}

FILES:${PN} += " \
    /opt/edgegateway/egw-controller/* \
"

RDEPENDS:${PN} = "docker-compose"
