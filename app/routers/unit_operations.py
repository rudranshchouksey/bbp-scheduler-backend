from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_session
from app.repositories.unit_operation_repo import UnitOperationRepository
from app.schemas.unit_operation import UnitOperationCreate, UnitOperationUpdate, UnitOperationRead

router = APIRouter(prefix="/api/unit_operations", tags=["Unit Operations"])


def get_repo(session: Session = Depends(get_session)) -> UnitOperationRepository:
    return UnitOperationRepository(session)


@router.post("", response_model=UnitOperationRead, status_code=status.HTTP_201_CREATED)
def create_unit_operation(
    payload: UnitOperationCreate,
    repo: UnitOperationRepository = Depends(get_repo),
):
    return repo.create(payload)


@router.put("/{op_id}", response_model=UnitOperationRead)
def update_unit_operation(
    op_id: int,
    payload: UnitOperationUpdate,
    repo: UnitOperationRepository = Depends(get_repo),
):
    op = repo.get_by_id(op_id)
    if not op:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"UnitOperation id={op_id} not found.",
        )
    return repo.update(op, payload)


@router.delete("/{op_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_unit_operation(
    op_id: int,
    repo: UnitOperationRepository = Depends(get_repo),
):
    op = repo.get_by_id(op_id)
    if not op:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"UnitOperation id={op_id} not found.",
        )
    repo.delete(op)