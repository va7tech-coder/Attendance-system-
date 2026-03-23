# Face Attendance Prototype

This is a simple face recognition + blink liveness attendance system.

## Setup

1. Create a Python venv and install dependencies:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Download `shape_predictor_68_face_landmarks.dat` and place it in the project root.
3. Add known faces under `dataset/<Name>/image.jpg`.

## Run

```bash
python project.py --dataset dataset --model shape_predictor_68_face_landmarks.dat --output attendance.csv
```

Controls:
- `q`: quit
- `r`: reload known faces
- `s`: show marked names today

## Notes
- Attendance is marked once per person per day.
- If face recognition fails, adjust `--tolerance` (default `0.5`).
