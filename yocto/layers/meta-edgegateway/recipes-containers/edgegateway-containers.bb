DESCRIPTION = "Placeholder recipe for EdgeGateway container packages"
LICENSE = "MIT"

SRC_URI = ""

inherit core-image

SUMMARY = "Example recipe for container meta-packages (placeholder)"

do_install() {
    install -d ${D}${datadir}/edgegateway
    echo "This is a placeholder for EdgeGateway container packages." > ${D}${datadir}/edgegateway/README-containers.txt
}

