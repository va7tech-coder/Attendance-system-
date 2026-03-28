from dataclasses import dataclass

import dlib
import numpy as np
from scipy.spatial import distance

from backend.config import get_settings


@dataclass
class BlinkState:
    closed_frames: int = 0


class BlinkService:
    def __init__(self) -> None:
        settings = get_settings()
        self.threshold = settings.blink_ear_threshold
        self.consecutive_frames = settings.blink_consecutive_frames
        self._states: dict[str, BlinkState] = {}

    @staticmethod
    def eye_aspect_ratio(eye: np.ndarray) -> float:
        vertical_a = distance.euclidean(eye[1], eye[5])
        vertical_b = distance.euclidean(eye[2], eye[4])
        horizontal = distance.euclidean(eye[0], eye[3])
        return (vertical_a + vertical_b) / (2.0 * horizontal) if horizontal else 0.0

    def detect_ear(self, gray: np.ndarray, rect: dlib.rectangle, predictor: dlib.shape_predictor) -> float:
        shape = predictor(gray, rect)
        points = np.array([[part.x, part.y] for part in shape.parts()])
        left_eye = self.eye_aspect_ratio(points[list(range(36, 42))])
        right_eye = self.eye_aspect_ratio(points[list(range(42, 48))])
        return float((left_eye + right_eye) / 2.0)

    def evaluate(self, session_id: str, gray: np.ndarray, rect: dlib.rectangle, predictor: dlib.shape_predictor) -> tuple[bool, float]:
        state = self._states.setdefault(session_id, BlinkState())
        ear = self.detect_ear(gray, rect, predictor)
        blink_detected = False
        if ear < self.threshold:
            state.closed_frames += 1
        else:
            if state.closed_frames >= self.consecutive_frames:
                blink_detected = True
            state.closed_frames = 0
        return blink_detected, ear
