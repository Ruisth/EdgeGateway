"""Goal codes C2DTA para automacao de protocolos DIDComm.

Conforme o paper EdgeGateway_Paper.pdf (Seccao 3.1 — Automation):
os goal codes permitem que agentes identifiquem automaticamente o contexto
de uma interacao DIDComm e tomem decisoes sem intervencao humana.
"""

# UC1 — OEM Enrollment
ENROLL_OEM = "c2dta.consortium.enroll.OEM"

# UC2 — Device Model Registration
REGISTER_MODEL = "c2dta.consortium.register.model"

# UC3 — Device Self-Registration
REGISTER_DEVICE = "c2dta.consortium.registerdevice"

# UC4 — Consumer Buys Device
BUY_DEVICE = "c2dta.consortium.buydevice"

# UC5 — Device Claiming
CLAIM_DEVICE = "c2dta.consortium.claim"

# UC6 — SD Twinning
TWIN_DEVICE = "c2dta.egw.twin"

# UC7 — SD Untwinning
UNTWIN_DEVICE = "c2dta.egw.untwin"

# UC8 — SD Selling
SELL_DEVICE = "c2dta.egw.sell"

# Mapa de goal codes para descricoes humanas
GOAL_CODE_DESCRIPTIONS = {
    ENROLL_OEM: "Inscricao de OEM no consorcio",
    REGISTER_MODEL: "Registo de modelo de dispositivo",
    REGISTER_DEVICE: "Auto-registo de dispositivo",
    BUY_DEVICE: "Compra de dispositivo",
    CLAIM_DEVICE: "Reivindicacao de dispositivo",
    TWIN_DEVICE: "Twinning de smart device",
    UNTWIN_DEVICE: "Untwinning de smart device",
    SELL_DEVICE: "Venda de smart device",
}
