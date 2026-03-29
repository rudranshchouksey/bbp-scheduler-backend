from dataclasses import dataclass
from datetime import datetime
from enum import Enum

SEQUENCE_ORDER = ["Seed", "Bioreactor", "TFF", "Spray", "Sum"]


class ViolationType(str, Enum):
    SEQUENCE_ORDER = "sequence_order"
    EQUIPMENT_OVERLAP = "equipment_overlap"
    OUT_OF_BATCH_RANGE = "out_of_batch_range"


@dataclass(frozen=True)
class OpSnapshot:
    id: int
    name: str
    start: datetime
    end: datetime
    equipment_id: int
    batch_id: int


@dataclass(frozen=True)
class BatchSnapshot:
    id: int
    start: datetime
    end: datetime


@dataclass(frozen=True)
class Violation:
    unit_op_id: int
    type: ViolationType
    message: str


class ConstraintService:
    """
    Pure business logic — zero DB access, fully unit-testable.
    Enforces all 4 scheduling constraints from the BBP spec.
    """

    def validate(
        self,
        ops: list[OpSnapshot],
        batches: list[BatchSnapshot] | None = None,
    ) -> list[Violation]:
        violations: list[Violation] = []
        violations.extend(self._check_sequence_order(ops))
        violations.extend(self._check_equipment_overlap(ops))
        if batches:
            violations.extend(self._check_batch_range(ops, batches))
        return violations

    # ── Constraint 3: Sequence order within each batch ───────────────────────
    def _check_sequence_order(self, ops: list[OpSnapshot]) -> list[Violation]:
        violations: list[Violation] = []
        batches: dict[int, list[OpSnapshot]] = {}

        for op in ops:
            batches.setdefault(op.batch_id, []).append(op)

        for batch_id, batch_ops in batches.items():
            known = [o for o in batch_ops if o.name in SEQUENCE_ORDER]
            sorted_ops = sorted(known, key=lambda o: SEQUENCE_ORDER.index(o.name))

            for i in range(1, len(sorted_ops)):
                prev, curr = sorted_ops[i - 1], sorted_ops[i]
                if curr.start < prev.end:
                    violations.append(Violation(
                        unit_op_id=curr.id,
                        type=ViolationType.SEQUENCE_ORDER,
                        message=(
                            f"'{curr.name}' (id={curr.id}) must start after "
                            f"'{prev.name}' (id={prev.id}) ends in Batch {batch_id}. "
                            f"'{prev.name}' ends {prev.end.date()}, "
                            f"but '{curr.name}' starts {curr.start.date()}."
                        ),
                    ))
        return violations

    # ── Constraint 4: No equipment double-booking ────────────────────────────
    def _check_equipment_overlap(self, ops: list[OpSnapshot]) -> list[Violation]:
        violations: list[Violation] = []
        by_eq: dict[int, list[OpSnapshot]] = {}

        for op in ops:
            by_eq.setdefault(op.equipment_id, []).append(op)

        for eq_id, eq_ops in by_eq.items():
            sorted_ops = sorted(eq_ops, key=lambda o: o.start)
            for i in range(1, len(sorted_ops)):
                prev, curr = sorted_ops[i - 1], sorted_ops[i]
                if curr.start < prev.end:
                    violations.append(Violation(
                        unit_op_id=curr.id,
                        type=ViolationType.EQUIPMENT_OVERLAP,
                        message=(
                            f"Equipment {eq_id} is double-booked: "
                            f"'{prev.name}' (id={prev.id}, ends {prev.end.date()}) "
                            f"overlaps '{curr.name}' (id={curr.id}, "
                            f"starts {curr.start.date()})."
                        ),
                    ))
        return violations

    # ── Constraints 1 & 2: UnitOps must be within Batch date range ───────────
    def _check_batch_range(
        self,
        ops: list[OpSnapshot],
        batches: list[BatchSnapshot],
    ) -> list[Violation]:
        violations: list[Violation] = []
        batch_map: dict[int, BatchSnapshot] = {b.id: b for b in batches}

        for op in ops:
            batch = batch_map.get(op.batch_id)
            if not batch:
                continue
            if op.start < batch.start or op.end > batch.end:
                violations.append(Violation(
                    unit_op_id=op.id,
                    type=ViolationType.OUT_OF_BATCH_RANGE,
                    message=(
                        f"'{op.name}' (id={op.id}) falls outside Batch {op.batch_id} "
                        f"range ({batch.start.date()} → {batch.end.date()}). "
                        f"Op runs {op.start.date()} → {op.end.date()}."
                    ),
                ))
        return violations