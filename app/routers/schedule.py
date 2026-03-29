from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.services.schedule_service import ScheduleService
from app.schemas.schedule import ScheduleResponse

router = APIRouter(prefix="/api", tags=["schedule"])


@router.get("/schedule", response_model=ScheduleResponse)
def get_schedule(
    # ✅ FIX: made optional — defaults to today → +30 days
    # Previously required, causing 422 whenever no dates were passed
    start_date: Optional[datetime] = Query(
        default=None,
        description="Start of visible window (ISO 8601). Defaults to today.",
    ),
    end_date: Optional[datetime] = Query(
        default=None,
        description="End of visible window (ISO 8601). Defaults to 30 days from today.",
    ),
    session: Session = Depends(get_session),
):
    # Resolve defaults here so the service always gets concrete values
    resolved_start = start_date or datetime.utcnow().replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    resolved_end = end_date or (resolved_start + timedelta(days=30))

    service = ScheduleService(session)
    return service.get_schedule(resolved_start, resolved_end)