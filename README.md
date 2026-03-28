# Face Attendance Web Platform

This repository now contains a production-oriented full-stack attendance platform built from the original OpenCV prototype.

## Folder Structure

```text
.
|-- backend/
|   |-- main.py
|   |-- config.py
|   |-- database.py
|   |-- models/
|   |-- routes/
|   |-- schemas/
|   |-- services/
|   |-- utils/
|   `-- Dockerfile
|-- frontend/
|   |-- components/
|   |-- lib/
|   |-- pages/
|   `-- styles/
|-- dataset/
|-- shape_predictor_68_face_landmarks.dat
|-- docker-compose.yml
|-- project.py
`-- README.md
```

## Architecture

### Backend

- `FastAPI` server with async route handlers.
- `SQLAlchemy + SQLite` by default, ready to switch to PostgreSQL via `DATABASE_URL`.
- Modular services:
  - `backend/services/face_service.py` for face encoding, matching, and cache refresh
  - `backend/services/blink_service.py` for blink-based liveness
  - `backend/services/attendance_service.py` for duplicate-safe attendance marking
  - `backend/services/user_service.py` for dataset import and user enrollment
- Routes:
  - `POST /api/recognize`
  - `POST /api/attendance/mark-attendance`
  - `GET /api/attendance`
  - `POST /api/system/reload-dataset`
  - `POST /api/users`

### Frontend

- `Next.js + Tailwind CSS` dashboard.
- Browser camera feed with `getUserMedia`.
- Frame capture every `1.5s` and REST submission to the backend.
- Pages:
  - `/` dashboard
  - `/attendance` history
  - `/admin` enrollment and dataset reload

## Features

- Face recognition against multiple stored embeddings per user.
- Blink-based liveness verification before attendance is accepted.
- Duplicate attendance prevention per user per day.
- Upload API to add new users with multiple training images.
- Dataset reload endpoint for bulk reindexing local images.
- Attendance history from the database.
- Dockerized backend and environment-based configuration.

## Database Schema

### `users`

- `id`
- `name`

### `user_embeddings`

- `id`
- `user_id`
- `source_label`
- `embedding`

### `attendance`

- `id`
- `user_id`
- `attendance_date`
- `marked_at`

## Backend Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
copy backend\.env.example backend\.env
uvicorn backend.main:app --reload
```

Backend environment variables:

- `DATABASE_URL`
- `MODEL_PATH`
- `DATASET_PATH`
- `CORS_ORIGINS`
- `FACE_MATCH_TOLERANCE`
- `BLINK_EAR_THRESHOLD`
- `BLINK_CONSECUTIVE_FRAMES`

## Frontend Setup

```bash
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

Frontend environment variable:

- `NEXT_PUBLIC_API_BASE_URL`

## Docker

Start both services locally:

```bash
docker compose up --build
```

## Deployment

### Railway or Render for Backend

1. Create a new service from the repo.
2. Point the service root to the repository root.
3. Use `backend/Dockerfile`.
4. Set:
   - `DATABASE_URL`
   - `MODEL_PATH`
   - `DATASET_PATH`
5. For PostgreSQL, use a connection string like:

```text
postgresql+asyncpg://user:password@host:5432/database
```

If you switch to PostgreSQL, add `asyncpg` to `backend/requirements.txt`.

### Vercel for Frontend

1. Import the repo into Vercel.
2. Set the root directory to `frontend`.
3. Add `NEXT_PUBLIC_API_BASE_URL` pointing to the deployed backend API.
4. Deploy.

## API Examples

### Recognize Face

```bash
curl -X POST http://localhost:8000/api/recognize ^
  -H "Content-Type: application/json" ^
  -d "{\"image_base64\":\"data:image/jpeg;base64,...\",\"session_id\":\"browser-1\",\"auto_mark_attendance\":true}"
```

### Mark Attendance

```bash
curl -X POST http://localhost:8000/api/attendance/mark-attendance ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\":1}"
```

### Add User

```bash
curl -X POST http://localhost:8000/api/users ^
  -F "name=Varun" ^
  -F "files=@dataset/Varun/WIN_20260314_11_10_33_Pro.jpg"
```

## Notes

- `project.py` is preserved as the original prototype reference.
- The new backend keeps the original face-recognition and blink logic, but moves it into reusable services.
- `shape_predictor_68_face_landmarks.dat` must remain available to the backend through `MODEL_PATH`.
