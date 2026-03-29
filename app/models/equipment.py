from __future__ import annotations
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.models.unit_operation import UnitOperation


class Equipment(SQLModel, table=True):
    __tablename__ = "equipment"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)