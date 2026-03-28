import logging
from pathlib import Path

import dlib
import face_recognition
import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import get_settings
from backend.models.user import User, UserEmbedding
from backend.utils.image import ensure_rgb


logger = logging.getLogger(__name__)


class FaceRecognitionService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.model_path = Path(self.settings.model_path)
        self.predictor = dlib.shape_predictor(str(self.model_path))
        self._cached_embeddings: list[np.ndarray] = []
        self._cached_metadata: list[dict[str, object]] = []

    async def refresh_cache(self, session: AsyncSession) -> int:
        result = await session.scalars(select(UserEmbedding).join(UserEmbedding.user))
        embeddings = list(result.unique().all())
        self._cached_embeddings = [np.asarray(item.embedding, dtype=np.float64) for item in embeddings]
        self._cached_metadata = [
            {"user_id": item.user_id, "name": item.user.name, "source_label": item.source_label}
            for item in embeddings
        ]
        logger.info("Loaded %s face embeddings into memory.", len(self._cached_embeddings))
        return len(self._cached_embeddings)

    def detect_faces(self, frame: np.ndarray) -> tuple[list[tuple[int, int, int, int]], list[np.ndarray]]:
        rgb = ensure_rgb(frame)
        locations = face_recognition.face_locations(rgb, model="hog")
        encodings = face_recognition.face_encodings(rgb, locations)
        return locations, encodings

    def match_face(self, encoding: np.ndarray) -> dict[str, object] | None:
        if not self._cached_embeddings:
            return None
        distances = face_recognition.face_distance(self._cached_embeddings, encoding)
        best_index = int(np.argmin(distances))
        best_distance = float(distances[best_index])
        if best_distance > self.settings.face_match_tolerance:
            return None
        confidence = max(0.0, min(1.0, 1.0 - best_distance))
        matched = dict(self._cached_metadata[best_index])
        matched["confidence"] = confidence
        matched["distance"] = best_distance
        return matched
