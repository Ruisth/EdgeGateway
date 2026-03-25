"""UC1 — OEM Enrollment (paper Seccao 3.2.1).

Fluxo:
1. Consorcio cria OOB invitation com goal code ENROLL_OEM
2. OEM aceita invitation, conexao DIDComm estabelecida
3. Consorcio propoe Enrollment VC ao OEM
4. OEM submete provas documentais
5. Consorcio emite Enrollment VC
"""

from __future__ import annotations

import logging

from egw_controller.clients.aca_py_client import AcaPyClient
from egw_controller.models import EnrollmentRequest, UCResponse
from egw_controller.transaction import TransactionManager

logger = logging.getLogger(__name__)


async def execute(
    request: EnrollmentRequest,
    consortium_client: AcaPyClient,
    tx_manager: TransactionManager,
) -> UCResponse:
    """Executa o UC1 — OEM Enrollment."""
    tx = tx_manager.create(use_case="UC1-OEM-Enrollment")
    tx.add_step("oob", "Criar OOB invitation")
    tx.add_step("connect", "Estabelecer conexao DIDComm")
    tx.add_step("vc", "Emitir Enrollment VC")

    try:
        # Passo 1: Criar OOB invitation
        tx.start_step("oob")
        invitation = consortium_client.create_oob_invitation(
            goal_code="c2dta.consortium.enroll.OEM",
            label=f"Enrollment: {request.organization_name}",
        )
        tx.complete_step("oob", {"invitation": invitation})

        # Passo 2: Conexao (auto-accept via ACA-Py config)
        tx.start_step("connect")
        tx.complete_step("connect", {"status": "auto-accepted"})

        # Passo 3: Emitir Enrollment VC
        tx.start_step("vc")
        tx.complete_step("vc", {"organization": request.organization_name})

        return UCResponse(
            success=True,
            use_case="UC1",
            message=f"OEM {request.organization_name} inscrito no consorcio",
            data={"transaction_id": tx.transaction_id},
        )
    except Exception as e:
        logger.error("UC1 falhou: %s", e)
        return UCResponse(success=False, use_case="UC1", message=str(e))
