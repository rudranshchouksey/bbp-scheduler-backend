from pydantic import BaseModel, ConfigDict, model_validator
from datetime import datetime


class BatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    start: datetime
    end: datetime


class BatchCreate(BaseModel):
    name: str
    start: datetime
    end: datetime

    @model_validator(mode="after")
    def end_after_start(self) -> "BatchCreate":
        if self.end <= self.start:
            raise ValueError("Batch end must be after start")
        return self


class BatchUpdate(BaseModel):
    name: str | None = None
    start: datetime | None = None
    end: datetime | None = None