from sqlmodel import Session, select
from app.models.batch import Batch


class BatchRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all(self) -> list[Batch]:
        return list(self.session.exec(select(Batch)).all())

    def get_by_id(self, batch_id: int) -> Batch | None:
        return self.session.get(Batch, batch_id)