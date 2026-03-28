from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db_session
from backend.routes.recognition import face_service
from backend.schemas.user import UserCreateResponse, UserResponse
from backend.services.user_service import UserService


router = APIRouter(prefix="/users", tags=["users"])
user_service = UserService()


@router.get("", response_model=list[UserResponse])
async def list_users(session: AsyncSession = Depends(get_db_session)) -> list[UserResponse]:
    users = await user_service.list_users(session)
    return [
        UserResponse(id=user.id, name=user.name, embedding_count=len(user.embeddings))
        for user in users
    ]


@router.post("", response_model=UserCreateResponse)
async def create_user(
    name: str = Form(...),
    files: list[UploadFile] = File(...),
    session: AsyncSession = Depends(get_db_session),
) -> UserCreateResponse:
    try:
        user = await user_service.add_user_from_uploads(session, name, files)
        await face_service.refresh_cache(session)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    refreshed = await user_service.get_user_by_id(session, user.id)
    embedding_count = len(refreshed.embeddings) if refreshed else 0
    return UserCreateResponse(
        id=user.id,
        name=user.name,
        embedding_count=embedding_count,
        message="User created and embeddings indexed.",
    )
