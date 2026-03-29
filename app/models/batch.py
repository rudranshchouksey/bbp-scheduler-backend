from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import DateTime
from sqlalchemy import Column


class Batch(SQLModel, table=True):
    __tablename__ = "batches"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    start: datetime = Field(sa_column=Column(DateTime, nullable=False))
    end: datetime = Field(sa_column=Column(DateTime, nullable=False))