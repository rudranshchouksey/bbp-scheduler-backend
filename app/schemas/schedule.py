from pydantic import BaseModel
from app.schemas.equipment import EquipmentRead
from app.schemas.batch import BatchRead
from app.schemas.unit_operation import UnitOperationRead


class ViolationRead(BaseModel):
    unit_op_id: int
    type: str
    message: str


class ScheduleResponse(BaseModel):
    equipment: list[EquipmentRead]
    batches: list[BatchRead]
    unit_ops: list[UnitOperationRead]
    violations: list[ViolationRead]