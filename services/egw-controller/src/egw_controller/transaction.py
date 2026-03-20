"""Gestor de transacoes multi-step para o EGW Controller.

Implementa a key-pair table descrita no paper (Seccao 3.1 — Transaction Control)
para preservar estado em operacoes que envolvem multiplos agentes SSI.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class StepStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TransactionStep:
    """Passo individual de uma transacao."""

    step_id: str
    description: str
    status: StepStatus = StepStatus.PENDING
    result: Optional[dict] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class Transaction:
    """Transacao multi-step com controlo de estado."""

    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    use_case: str = ""
    device_id: str = ""
    steps: list[TransactionStep] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    status: StepStatus = StepStatus.PENDING

    def add_step(self, step_id: str, description: str) -> TransactionStep:
        step = TransactionStep(step_id=step_id, description=description)
        self.steps.append(step)
        return step

    def start_step(self, step_id: str) -> None:
        for step in self.steps:
            if step.step_id == step_id:
                step.status = StepStatus.IN_PROGRESS
                step.started_at = datetime.now(timezone.utc).isoformat()
                self.status = StepStatus.IN_PROGRESS
                return

    def complete_step(self, step_id: str, result: dict | None = None) -> None:
        for step in self.steps:
            if step.step_id == step_id:
                step.status = StepStatus.COMPLETED
                step.result = result
                step.completed_at = datetime.now(timezone.utc).isoformat()
                # Verificar se todos os passos estao completos
                if all(s.status == StepStatus.COMPLETED for s in self.steps):
                    self.status = StepStatus.COMPLETED
                return

    def fail_step(self, step_id: str, error: str) -> None:
        for step in self.steps:
            if step.step_id == step_id:
                step.status = StepStatus.FAILED
                step.error = error
                step.completed_at = datetime.now(timezone.utc).isoformat()
                self.status = StepStatus.FAILED
                return


class TransactionManager:
    """Gere transacoes ativas e historico."""

    def __init__(self) -> None:
        self._transactions: dict[str, Transaction] = {}

    def create(self, use_case: str, device_id: str = "") -> Transaction:
        tx = Transaction(use_case=use_case, device_id=device_id)
        self._transactions[tx.transaction_id] = tx
        return tx

    def get(self, transaction_id: str) -> Transaction | None:
        return self._transactions.get(transaction_id)

    def list_active(self) -> list[Transaction]:
        return [
            tx
            for tx in self._transactions.values()
            if tx.status in (StepStatus.PENDING, StepStatus.IN_PROGRESS)
        ]

    def list_all(self) -> list[Transaction]:
        return list(self._transactions.values())
