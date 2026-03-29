from datetime import datetime
from app.services.constraint_service import (
    ConstraintService, OpSnapshot, BatchSnapshot, ViolationType
)

svc = ConstraintService()


def op(id, name, start, end, equipment_id=1, batch_id=1) -> OpSnapshot:
    return OpSnapshot(
        id=id, name=name,
        start=datetime.fromisoformat(start),
        end=datetime.fromisoformat(end),
        equipment_id=equipment_id,
        batch_id=batch_id,
    )


def batch(id, start, end) -> BatchSnapshot:
    return BatchSnapshot(
        id=id,
        start=datetime.fromisoformat(start),
        end=datetime.fromisoformat(end),
    )


# ── Constraint 3: Sequence order ─────────────────────────────────────────────

def test_valid_sequence_passes():
    ops = [
        op(1, "Seed",       "2026-03-01", "2026-03-03", equipment_id=1),
        op(2, "Bioreactor", "2026-03-04", "2026-03-10", equipment_id=2),
        op(3, "TFF",        "2026-03-11", "2026-03-14", equipment_id=3),
    ]
    assert svc.validate(ops) == []


def test_sequence_violation_detected():
    ops = [
        op(1, "Seed",       "2026-03-01", "2026-03-05", equipment_id=1),
        op(2, "Bioreactor", "2026-03-03", "2026-03-10", equipment_id=2),
    ]
    violations = svc.validate(ops)
    assert any(v.type == ViolationType.SEQUENCE_ORDER for v in violations)
    assert violations[0].unit_op_id == 2


def test_partial_sequence_allowed():
    ops = [
        op(1, "Seed", "2026-03-01", "2026-03-03", equipment_id=1),
        op(2, "TFF",  "2026-03-04", "2026-03-07", equipment_id=2),
    ]
    assert svc.validate(ops) == []


# ── Constraint 4: Equipment overlap ──────────────────────────────────────────

def test_equipment_overlap_detected():
    ops = [
        op(1, "Seed",       "2026-03-01", "2026-03-05", equipment_id=1, batch_id=1),
        op(2, "Bioreactor", "2026-03-03", "2026-03-08", equipment_id=1, batch_id=2),
    ]
    violations = svc.validate(ops)
    assert any(v.type == ViolationType.EQUIPMENT_OVERLAP for v in violations)


def test_same_time_different_equipment_no_violation():
    ops = [
        op(1, "Seed",       "2026-03-01", "2026-03-05", equipment_id=1, batch_id=1),
        op(2, "Bioreactor", "2026-03-01", "2026-03-05", equipment_id=2, batch_id=2),
    ]
    assert svc.validate(ops) == []


# ── Constraints 1 & 2: Batch date range ──────────────────────────────────────

def test_op_within_batch_range_passes():
    ops = [op(1, "Seed", "2026-03-02", "2026-03-04", equipment_id=1, batch_id=1)]
    batches = [batch(1, "2026-03-01", "2026-03-10")]
    assert svc.validate(ops, batches) == []


def test_op_starts_before_batch_detected():
    ops = [op(1, "Seed", "2026-02-28", "2026-03-04", equipment_id=1, batch_id=1)]
    batches = [batch(1, "2026-03-01", "2026-03-10")]
    violations = svc.validate(ops, batches)
    assert any(v.type == ViolationType.OUT_OF_BATCH_RANGE for v in violations)


def test_op_ends_after_batch_detected():
    ops = [op(1, "Seed", "2026-03-02", "2026-03-12", equipment_id=1, batch_id=1)]
    batches = [batch(1, "2026-03-01", "2026-03-10")]
    violations = svc.validate(ops, batches)
    assert any(v.type == ViolationType.OUT_OF_BATCH_RANGE for v in violations)


def test_multiple_violations_returned():
    ops = [
        op(1, "Seed",       "2026-03-01", "2026-03-05", equipment_id=1, batch_id=1),
        op(2, "Bioreactor", "2026-03-03", "2026-03-08", equipment_id=1, batch_id=1),
    ]
    violations = svc.validate(ops)
    types = {v.type for v in violations}
    assert ViolationType.SEQUENCE_ORDER in types
    assert ViolationType.EQUIPMENT_OVERLAP in types