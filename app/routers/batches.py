from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_session
from app.repositories.batch_repo import BatchRepository
from app.schemas.batch import BatchCreate, BatchUpdate, BatchRead

# ✅ FIX: removed /api from prefix — main.py already mounts with /api
router = APIRouter(prefix="/batches", tags=["batches"])


@router.get("/", response_model=list[BatchRead])
def list_batches(session: Session = Depends(get_session)):
    repo = BatchRepository(session)
    return repo.get_all()


@router.get("/{batch_id}", response_model=BatchRead)
def get_batch(batch_id: int, session: Session = Depends(get_session)):
    repo = BatchRepository(session)
    batch = repo.get_by_id(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch


@router.post("/", response_model=BatchRead, status_code=status.HTTP_201_CREATED)
def create_batch(payload: BatchCreate, session: Session = Depends(get_session)):
    repo = BatchRepository(session)
    return repo.create(payload)


@router.put("/{batch_id}", response_model=BatchRead)
def update_batch(
    batch_id: int,
    payload: BatchUpdate,
    session: Session = Depends(get_session),
):
    repo = BatchRepository(session)
    batch = repo.get_by_id(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return repo.update(batch, payload)


@router.delete("/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_batch(batch_id: int, session: Session = Depends(get_session)):
    repo = BatchRepository(session)
    batch = repo.get_by_id(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    repo.delete(batch)