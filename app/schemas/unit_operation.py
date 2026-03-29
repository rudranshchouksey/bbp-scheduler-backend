from typing import Literal
from datetime import datetime
from pydantic import BaseModel, ConfigDict, model_validator

OP_NAMES = Literal["Seed", "Bioreactor", "TFF", "Spray", "Sum"]
STATUS = Literal["draft", "confirmed", "completed"]

OP_COLORS: dict[str, str] = {
    "Seed": "#6366f1",
    "Bioreactor": "#0ea5e9",
    "TFF": "#10b981",
    "Spray": "#f59e0b",
    "Sum": "#ef4444",
}


class UnitOperationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    color: str
    status: str
    start: datetime
    end: datetime
    batch_id: int
    equipment_id: int


class UnitOperationCreate(BaseModel):
    name: OP_NAMES
    status: STATUS = "draft"
    start: datetime
    end: datetime
    batch_id: int
    equipment_id: int
    color: str | None = None

    @model_validator(mode="after")
    def auto_set_color(self) -> "UnitOperationCreate":
        if not self.color:
            self.color = OP_COLORS.get(self.name, "#6366f1")
        return self

    @model_validator(mode="after")
    def end_must_be_after_start(self) -> "UnitOperationCreate":
        if self.end <= self.start:
            raise ValueError("end datetime must be strictly after start datetime")
        return self


class UnitOperationUpdate(BaseModel):
    name: OP_NAMES | None = None
    status: STATUS | None = None
    start: datetime | None = None
    end: datetime | None = None
    equipment_id: int | None = None
    color: str | None = None

    @model_validator(mode="after")
    def end_after_start_if_both(self) -> "UnitOperationUpdate":
        if self.start and self.end and self.end <= self.start:
            raise ValueError("end must be after start")
        return self