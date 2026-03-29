from datetime import datetime
from sqlmodel import Session, select
from app.models.unit_operation import UnitOperation
from app.schemas.unit_operation import UnitOperationCreate, UnitOperationUpdate


class UnitOperationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, op_id: int) -> UnitOperation | None:
        return self.session.get(UnitOperation, op_id)

    def get_all(self) -> list[UnitOperation]:
        return list(self.session.exec(select(UnitOperation)).all())

    def get_in_date_range(self, start: datetime, end: datetime) -> list[UnitOperation]:
        stmt = select(UnitOperation).where(
            UnitOperation.start >= start,
            UnitOperation.end <= end,
        )
        return list(self.session.exec(stmt).all())

    def create(self, payload: UnitOperationCreate) -> UnitOperation:
        op = UnitOperation(**payload.model_dump())
        self.session.add(op)
        self.session.commit()
        self.session.refresh(op)
        return op

    def update(self, op: UnitOperation, payload: UnitOperationUpdate) -> UnitOperation:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(op, field, value)
        self.session.add(op)
        self.session.commit()
        self.session.refresh(op)
        return op

    def delete(self, op: UnitOperation) -> None:
        self.session.delete(op)
        self.session.commit()