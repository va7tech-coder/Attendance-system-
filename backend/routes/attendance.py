from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db_session
from backend.schemas.attendance import AttendanceMarkRequest, AttendanceRecord
from backend.services.attendance_service import AttendanceService
from backend.services.user_service import UserService


router = APIRouter(prefix="/attendance", tags=["attendance"])
attendance_service = AttendanceService()
user_service = UserService()


@router.get("", response_model=list[AttendanceRecord])
async def get_attendance(
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_db_session),
) -> list[AttendanceRecord]:
    records = await attendance_service.list_attendance(session, limit=limit)
    return [
        AttendanceRecord(
            id=record.id,
            user_id=record.user_id,
            user_name=record.user.name,
            attendance_date=record.attendance_date,
            marked_at=record.marked_at,
        )
        for record in records
    ]


@router.post("/mark", response_model=AttendanceRecord)
@router.post("/mark-attendance", response_model=AttendanceRecord)
async def mark_attendance(
    payload: AttendanceMarkRequest,
    session: AsyncSession = Depends(get_db_session),
) -> AttendanceRecord:
    user = await user_service.get_user_by_id(session, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    record, _ = await attendance_service.mark_attendance(session, user)
    return AttendanceRecord(
        id=record.id,
        user_id=record.user_id,
        user_name=user.name,
        attendance_date=record.attendance_date,
        marked_at=record.marked_at,
    )
