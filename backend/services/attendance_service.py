from datetime import date, datetime

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.attendance import Attendance
from backend.models.user import User


class AttendanceService:
    async def mark_attendance(self, session: AsyncSession, user: User) -> tuple[Attendance, bool]:
        today = date.today()
        query = select(Attendance).where(
            Attendance.user_id == user.id,
            Attendance.attendance_date == today,
        )
        existing = await session.scalar(query)
        if existing:
            return existing, False

        record = Attendance(user_id=user.id, attendance_date=today, marked_at=datetime.now())
        session.add(record)
        await session.commit()
        await session.refresh(record)
        return record, True

    async def list_attendance(self, session: AsyncSession, limit: int = 100) -> list[Attendance]:
        query = (
            select(Attendance)
            .join(Attendance.user)
            .order_by(desc(Attendance.marked_at))
            .limit(limit)
        )
        result = await session.scalars(query)
        return list(result.unique().all())
