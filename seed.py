from datetime import datetime
from sqlalchemy import text
from sqlmodel import Session
from app.database import engine, init_db
from app.models import Equipment, Batch, UnitOperation, UnitOperationDependency

COLORS: dict[str, str] = {
    "Seed": "#6366f1",
    "Bioreactor": "#0ea5e9",
    "TFF": "#10b981",
    "Spray": "#f59e0b",
    "Sum": "#ef4444",
}


def seed() -> None:
    init_db()
    with Session(engine) as s:

        # ── Wipe existing data cleanly ────────────────────────────────────
        s.exec(text("TRUNCATE unit_operation_dependencies, unit_operations, batches, equipment RESTART IDENTITY CASCADE"))
        s.commit()
        print("🗑️  Cleared existing data")

        # ── Equipment ─────────────────────────────────────────────────────
        eq_names = ["1.5L", "15L", "20L", "75L", "1500L"]
        equipment: list[Equipment] = []
        for name in eq_names:
            eq = Equipment(name=name)
            s.add(eq); s.commit(); s.refresh(eq)
            equipment.append(eq)

        # ── Batch 1: fully valid ──────────────────────────────────────────
        b1 = Batch(
            name="Batch-001",
            start=datetime(2026, 3, 1),
            end=datetime(2026, 3, 17),
        )
        s.add(b1); s.commit(); s.refresh(b1)

        b1_ops_raw = [
            ("Seed",       "2026-03-01", "2026-03-03", equipment[0].id, "confirmed"),
            ("Bioreactor", "2026-03-04", "2026-03-10", equipment[1].id, "confirmed"),
            ("TFF",        "2026-03-11", "2026-03-14", equipment[2].id, "confirmed"),
            ("Spray",      "2026-03-15", "2026-03-17", equipment[3].id, "draft"),
        ]
        b1_ops: list[UnitOperation] = []
        for name, start, end, eq_id, status in b1_ops_raw:
            op = UnitOperation(
                name=name, color=COLORS[name], status=status,
                start=datetime.fromisoformat(start),
                end=datetime.fromisoformat(end),
                batch_id=b1.id, equipment_id=eq_id,
            )
            s.add(op); s.commit(); s.refresh(op)
            b1_ops.append(op)

        for i in range(len(b1_ops) - 1):
            s.add(UnitOperationDependency(
                from_unitop_id=b1_ops[i].id,
                to_unitop_id=b1_ops[i + 1].id,
            ))
        s.commit()

        # ── Batch 2: equipment overlap violation on 20L ───────────────────
        b2 = Batch(
            name="Batch-002",
            start=datetime(2026, 3, 5),
            end=datetime(2026, 3, 20),
        )
        s.add(b2); s.commit(); s.refresh(b2)

        b2_ops_raw = [
            ("Seed",       "2026-03-05", "2026-03-07", equipment[4].id, "draft"),
            ("Bioreactor", "2026-03-08", "2026-03-15", equipment[3].id, "draft"),
            # ⚠️ 20L double-booked: Batch-001 TFF uses 20L from Mar 11-14
            ("TFF",        "2026-03-12", "2026-03-16", equipment[2].id, "draft"),
        ]
        b2_ops: list[UnitOperation] = []
        for name, start, end, eq_id, status in b2_ops_raw:
            op = UnitOperation(
                name=name, color=COLORS[name], status=status,
                start=datetime.fromisoformat(start),
                end=datetime.fromisoformat(end),
                batch_id=b2.id, equipment_id=eq_id,
            )
            s.add(op); s.commit(); s.refresh(op)
            b2_ops.append(op)

        for i in range(len(b2_ops) - 1):
            s.add(UnitOperationDependency(
                from_unitop_id=b2_ops[i].id,
                to_unitop_id=b2_ops[i + 1].id,
            ))
        s.commit()

    print("✅ Seeded: 5 equipment, 2 batches with date ranges, 7 unit ops, 1 equipment overlap violation.")


if __name__ == "__main__":
    seed()