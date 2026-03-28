from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import get_settings
from backend.database import get_db_session
from backend.routes.recognition import face_service
from backend.services.user_service import UserService


router = APIRouter(prefix="/system", tags=["system"])
settings = get_settings()
user_service = UserService()


@router.post("/reload-dataset")
async def reload_dataset(session: AsyncSession = Depends(get_db_session)) -> dict[str, int | str]:
    embeddings_created = await user_service.reload_from_dataset(session, settings.dataset_path)
    cached_embeddings = await face_service.refresh_cache(session)
    return {
        "message": "Dataset reloaded successfully.",
        "embeddings_created": embeddings_created,
        "cached_embeddings": cached_embeddings,
    }


@router.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
