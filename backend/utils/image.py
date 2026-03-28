import base64
from typing import Any

import cv2
import numpy as np
from fastapi import UploadFile


def _to_image(raw_bytes: bytes) -> np.ndarray:
    image = cv2.imdecode(np.frombuffer(raw_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Unable to decode image bytes.")
    return image


def decode_base64_image(image_base64: str) -> np.ndarray:
    payload = image_base64.split(",", 1)[-1]
    raw_bytes = base64.b64decode(payload)
    return _to_image(raw_bytes)


async def upload_file_to_image(file: UploadFile) -> np.ndarray:
    raw_bytes = await file.read()
    return _to_image(raw_bytes)


def ensure_rgb(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def ensure_gray(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def serialize_embedding(vector: Any) -> list[float]:
    return np.asarray(vector, dtype=np.float64).tolist()
