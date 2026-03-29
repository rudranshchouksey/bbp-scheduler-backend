from datetime import datetime
from sqlmodel import Session, select

from app.models.equipment import Equipment
from app.models.batch import Batch
from app.repositories.unit_operation_repo import UnitOperationRepository
from app.services.constraint_service import ConstraintService, OpSnapshot, BatchSnapshot
from app.schemas.schedule import ScheduleResponse, ViolationRead
from app.schemas.equipment import EquipmentRead
from app.schemas.batch import BatchRead
from app.schemas.unit_operation import UnitOperationRead


class ScheduleService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.unit_op_repo = UnitOperationRepository(session)
        self.constraint_svc = ConstraintService()

    def get_schedule(self, start: datetime, end: datetime) -> ScheduleResponse:
        equipment = list(self.session.exec(select(Equipment)).all())
        batches = list(self.session.exec(select(Batch)).all())
        unit_ops = self.unit_op_repo.get_in_date_range(start, end)

        op_snapshots = [
            OpSnapshot(
                id=op.id,
                name=op.name,
                start=op.start,
                end=op.end,
                equipment_id=op.equipment_id,
                batch_id=op.batch_id,
            )
            for op in unit_ops
        ]

        batch_snapshots = [
            BatchSnapshot(id=b.id, start=b.start, end=b.end)
            for b in batches
        ]

        raw_violations = self.constraint_svc.validate(op_snapshots, batch_snapshots)

        return ScheduleResponse(
            equipment=[EquipmentRead.model_validate(e) for e in equipment],
            batches=[BatchRead.model_validate(b) for b in batches],
            unit_ops=[UnitOperationRead.model_validate(op) for op in unit_ops],
            violations=[
                ViolationRead(
                    unit_op_id=v.unit_op_id,
                    type=v.type.value,
                    message=v.message,
                )
                for v in raw_violations
            ],
        )