FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend /app/backend
COPY dataset /app/dataset
COPY shape_predictor_68_face_landmarks.dat /app/shape_predictor_68_face_landmarks.dat

ENV DATABASE_URL=sqlite+aiosqlite:///./attendance.db
ENV MODEL_PATH=/app/shape_predictor_68_face_landmarks.dat
ENV DATASET_PATH=/app/dataset

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
