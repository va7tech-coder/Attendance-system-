from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (UniqueConstraint("user_id", "attendance_date", name="uq_user_attendance_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    attendance_date: Mapped[date] = mapped_column(Date, index=True)
    marked_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), index=True)

    user: Mapped["User"] = relationship(back_populates="attendances")


from backend.models.user import User  # noqa: E402
