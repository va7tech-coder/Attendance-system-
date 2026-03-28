import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.database import Base, AsyncSessionLocal, engine
from backend.routes.attendance import router as attendance_router
from backend.routes.recognition import face_service, router as recognition_router
from backend.routes.system import router as system_router
from backend.routes.users import router as users_router
from backend.utils.logging import configure_logging


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    logger = logging.getLogger(__name__)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        try:
            await face_service.refresh_cache(session)
        except Exception as exc:  # pragma: no cover
            logger.warning("Could not warm face cache on startup: %s", exc)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recognition_router, prefix=settings.api_prefix)
app.include_router(attendance_router, prefix=settings.api_prefix)
app.include_router(users_router, prefix=settings.api_prefix)
app.include_router(system_router, prefix=settings.api_prefix)

