import logging
from pathlib import Path

import face_recognition
from fastapi import UploadFile
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models.user import User, UserEmbedding
from backend.utils.image import ensure_rgb, serialize_embedding, upload_file_to_image


logger = logging.getLogger(__name__)


class UserService:
    async def list_users(self, session: AsyncSession) -> list[User]:
        result = await session.scalars(select(User).options(selectinload(User.embeddings)).order_by(User.name))
        return list(result.unique().all())

    async def get_user_by_id(self, session: AsyncSession, user_id: int) -> User | None:
        return await session.get(User, user_id, options=[selectinload(User.embeddings)])

    async def get_or_create_user(self, session: AsyncSession, name: str) -> User:
        existing = await session.scalar(select(User).where(User.name == name))
        if existing:
            return existing
        user = User(name=name)
        session.add(user)
        await session.flush()
        return user

    async def add_user_from_uploads(self, session: AsyncSession, name: str, files: list[UploadFile]) -> User:
        user = await self.get_or_create_user(session, name)
        created_embeddings = 0
        for file in files:
            image = await upload_file_to_image(file)
            encodings = face_recognition.face_encodings(ensure_rgb(image))
            if not encodings:
                logger.warning("No face found in upload %s for user %s.", file.filename, name)
                continue
            session.add(
                UserEmbedding(
                    user_id=user.id,
                    source_label=file.filename or f"upload-{created_embeddings + 1}",
                    embedding=serialize_embedding(encodings[0]),
                )
            )
            created_embeddings += 1
        if created_embeddings == 0:
            raise ValueError("No valid faces found in uploaded images.")
        await session.commit()
        await session.refresh(user)
        return user

    async def reload_from_dataset(self, session: AsyncSession, dataset_path: str) -> int:
        root = Path(dataset_path)
        if not root.exists():
            raise FileNotFoundError(f"Dataset folder not found: {dataset_path}")

        await session.execute(delete(UserEmbedding))
        await session.execute(delete(User))
        await session.commit()

        added = 0
        for person_dir in sorted(root.iterdir()):
            if not person_dir.is_dir():
                continue
            user = User(name=person_dir.name)
            session.add(user)
            await session.flush()
            for image_path in sorted(person_dir.iterdir()):
                if not image_path.is_file():
                    continue
                try:
                    image = face_recognition.load_image_file(str(image_path))
                    encodings = face_recognition.face_encodings(image)
                    if not encodings:
                        continue
                    session.add(
                        UserEmbedding(
                            user_id=user.id,
                            source_label=image_path.name,
                            embedding=serialize_embedding(encodings[0]),
                        )
                    )
                    added += 1
                except Exception as exc:  # pragma: no cover
                    logger.warning("Failed to ingest %s: %s", image_path, exc)
        await session.commit()
        return added
