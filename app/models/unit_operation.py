from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime


class UnitOperation(SQLModel, table=True):
    __tablename__ = "unit_operations"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    color: str = Field(default="#6366f1")
    status: str = Field(default="draft")
    start: datetime = Field(sa_column=Column(DateTime, nullable=False))
    end: datetime = Field(sa_column=Column(DateTime, nullable=False))
    batch_id: int = Field(foreign_key="batches.id", index=True)
    equipment_id: int = Field(foreign_key="equipment.id", index=True)