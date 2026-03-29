from sqlmodel import Session, select
from app.models.equipment import Equipment


class EquipmentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all(self) -> list[Equipment]:
        return list(self.session.exec(select(Equipment)).all())

    def get_by_id(self, eq_id: int) -> Equipment | None:
        return self.session.get(Equipment, eq_id)