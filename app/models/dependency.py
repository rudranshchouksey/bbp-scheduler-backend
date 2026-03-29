from __future__ import annotations
from typing import Optional
from sqlmodel import SQLModel, Field


class UnitOperationDependency(SQLModel, table=True):
    __tablename__ = "unit_operation_dependencies"

    id: Optional[int] = Field(default=None, primary_key=True)
    from_unitop_id: int = Field(foreign_key="unit_operations.id", index=True)
    to_unitop_id: int = Field(foreign_key="unit_operations.id", index=True)