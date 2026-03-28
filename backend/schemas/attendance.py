from datetime import date, datetime

from pydantic import BaseModel


class AttendanceMarkRequest(BaseModel):
    user_id: int


class AttendanceRecord(BaseModel):
    id: int
    user_id: int
    user_name: str
    attendance_date: date
    marked_at: datetime

    class Config:
        from_attributes = True
