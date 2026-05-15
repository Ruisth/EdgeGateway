"""Testes para o TransactionManager."""

from egw_controller.transaction import StepStatus


def test_create_transaction(tx_manager):
    tx = tx_manager.create(use_case="UC1-Test", device_id="dev-001")
    assert tx.use_case == "UC1-Test"
    assert tx.device_id == "dev-001"
    assert tx.status == StepStatus.PENDING


def test_add_and_complete_steps(tx_manager):
    tx = tx_manager.create(use_case="UC-Test")
    tx.add_step("s1", "Passo 1")
    tx.add_step("s2", "Passo 2")

    tx.start_step("s1")
    assert tx.status == StepStatus.IN_PROGRESS

    tx.complete_step("s1", {"ok": True})
    assert tx.steps[0].status == StepStatus.COMPLETED
    assert tx.status == StepStatus.IN_PROGRESS  # s2 ainda pendente

    tx.start_step("s2")
    tx.complete_step("s2", {"ok": True})
    assert tx.status == StepStatus.COMPLETED


def test_fail_step(tx_manager):
    tx = tx_manager.create(use_case="UC-Fail")
    tx.add_step("s1", "Passo que falha")

    tx.start_step("s1")
    tx.fail_step("s1", "Erro de teste")
    assert tx.steps[0].status == StepStatus.FAILED
    assert tx.status == StepStatus.FAILED
    assert tx.steps[0].error == "Erro de teste"


def test_list_active(tx_manager):
    tx1 = tx_manager.create(use_case="UC-Active")
    tx1.add_step("s1", "Passo")
    tx1.start_step("s1")

    tx2 = tx_manager.create(use_case="UC-Done")
    tx2.add_step("s1", "Passo")
    tx2.start_step("s1")
    tx2.complete_step("s1")

    active = tx_manager.list_active()
    assert len(active) == 1
    assert active[0].use_case == "UC-Active"


def test_list_all(tx_manager):
    tx_manager.create(use_case="UC-A")
    tx_manager.create(use_case="UC-B")
    assert len(tx_manager.list_all()) == 2


def test_get_transaction(tx_manager):
    tx = tx_manager.create(use_case="UC-Get")
    found = tx_manager.get(tx.transaction_id)
    assert found is tx
    assert tx_manager.get("inexistente") is None
