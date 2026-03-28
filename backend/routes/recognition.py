import logging

import dlib
from fastapi import APIRouter, Depends, HTTPException
from starlette.concurrency import run_in_threadpool
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db_session
from backend.models.user import User
from backend.schemas.recognition import RecognitionRequest, RecognitionResponse
from backend.services.attendance_service import AttendanceService
from backend.services.blink_service import BlinkService
from backend.services.face_service import FaceRecognitionService
from backend.utils.image import decode_base64_image, ensure_gray


logger = logging.getLogger(__name__)
router = APIRouter(tags=["recognition"])

face_service = FaceRecognitionService()
blink_service = BlinkService()
attendance_service = AttendanceService()


@router.post("/recognize", response_model=RecognitionResponse)
async def recognize_face(
    payload: RecognitionRequest,
    session: AsyncSession = Depends(get_db_session),
) -> RecognitionResponse:
    try:
        frame = decode_base64_image(payload.image_base64)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid image payload: {exc}") from exc

    locations, encodings = await run_in_threadpool(face_service.detect_faces, frame)
    if not locations or not encodings:
        return RecognitionResponse(
            detected=False,
            live=False,
            blink_detected=False,
            message="No face detected.",
        )

    gray = ensure_gray(frame)
    top, right, bottom, left = locations[0]
    match = await run_in_threadpool(face_service.match_face, encodings[0])
    rect = dlib.rectangle(left, top, right, bottom)
    blink_detected, ear = await run_in_threadpool(
        blink_service.evaluate,
        payload.session_id,
        gray,
        rect,
        face_service.predictor,
    )

    if not match:
        return RecognitionResponse(
            detected=True,
            live=False,
            blink_detected=blink_detected,
            name="Unknown",
            confidence=0.0,
            message=f"Face detected but not recognized. EAR={ear:.2f}",
        )

    user = await session.scalar(select(User).where(User.id == int(match["user_id"])))
    if not user:
        raise HTTPException(status_code=404, detail="Matched user was not found.")

    attendance_marked = False
    message = f"Recognized {user.name} with confidence {match['confidence']:.2%}."
    if blink_detected and payload.auto_mark_attendance:
        _, attendance_marked = await attendance_service.mark_attendance(session, user)
        message = (
            f"Attendance {'marked' if attendance_marked else 'already exists'} for {user.name}. "
            f"Confidence {match['confidence']:.2%}."
        )

    return RecognitionResponse(
        detected=True,
        live=blink_detected,
        blink_detected=blink_detected,
        name=user.name,
        confidence=float(match["confidence"]),
        user_id=user.id,
        attendance_marked=attendance_marked,
        message=message,
    )
