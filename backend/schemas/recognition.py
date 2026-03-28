from pydantic import BaseModel, Field


class RecognitionRequest(BaseModel):
    image_base64: str = Field(..., description="Base64 encoded image or data URL")
    session_id: str = Field(default="default")
    auto_mark_attendance: bool = True


class RecognitionResponse(BaseModel):
    detected: bool
    live: bool
    blink_detected: bool
    name: str | None = None
    confidence: float | None = None
    user_id: int | None = None
    attendance_marked: bool = False
    message: str
