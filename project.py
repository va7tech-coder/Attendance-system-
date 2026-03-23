import argparse
import os
import sys
from datetime import datetime

import cv2
import dlib
import face_recognition
import numpy as np
import pandas as pd
from scipy.spatial import distance


def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C) if C != 0 else 0.0


def detect_ear(gray, rect, predictor):
    shape = predictor(gray, rect)
    shape = np.array([[p.x, p.y] for p in shape.parts()])
    left_eye = eye_aspect_ratio(shape[list(range(36, 42))])
    right_eye = eye_aspect_ratio(shape[list(range(42, 48))])
    return (left_eye + right_eye) / 2.0


def load_known_faces(dataset_dir):
    known_encodings = []
    known_names = []
    if not os.path.isdir(dataset_dir):
        raise FileNotFoundError(f"Dataset folder not found: {dataset_dir}")
    for person_name in sorted(os.listdir(dataset_dir)):
        person_folder = os.path.join(dataset_dir, person_name)
        if not os.path.isdir(person_folder):
            continue
        for image_name in sorted(os.listdir(person_folder)):
            image_path = os.path.join(person_folder, image_name)
            if not os.path.isfile(image_path):
                continue
            try:
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    known_encodings.append(encodings[0])
                    known_names.append(person_name)
            except Exception as e:
                print(f"Could not load {image_path}: {e}")
    return known_encodings, known_names


def mark_attendance(name, attendance_file):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    if not os.path.exists(attendance_file):
        pd.DataFrame(columns=["Name", "Date", "Time"]).to_csv(attendance_file, index=False)
    df = pd.read_csv(attendance_file)
    if not ((df["Name"] == name) & (df["Date"] == date_str)).any():
        row = pd.DataFrame([{"Name": name, "Date": date_str, "Time": time_str}])
        df = pd.concat([df, row], ignore_index=True)
        df.to_csv(attendance_file, index=False)
        print(f"✅ Attendance marked for {name} at {date_str} {time_str}")
        return date_str, time_str, True
    return None, None, False


def calibrate_blink_threshold(cap, predictor, fallback=0.22, frames=5):
    open_ears = []
    for _ in range(frames):
        ret, frame = cap.read()
        if not ret:
            continue
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_locations = face_recognition.face_locations(rgb, model="hog")
        if not face_locations:
            continue
        top, right, bottom, left = face_locations[0]
        ear = detect_ear(gray, dlib.rectangle(left, top, right, bottom), predictor)
        if ear > 0:
            open_ears.append(ear)
    if open_ears:
        return max(0.10, np.mean(open_ears) * 0.75)
    return fallback


def parse_args():
    parser = argparse.ArgumentParser(description="Face + blink attendance")
    parser.add_argument("--dataset", default="dataset", help="Known faces folder")
    parser.add_argument("--model", default="shape_predictor_68_face_landmarks.dat", help="Dlib model file")
    parser.add_argument("--output", default="attendance.csv", help="Output attendance CSV")
    parser.add_argument("--camera", type=int, default=0, help="Camera index")
    parser.add_argument("--tolerance", type=float, default=0.5, help="Face matching tolerance")
    parser.add_argument("--consecutive", type=int, default=2, help="Consecutive blink frames")
    parser.add_argument("--calibrate", type=int, default=5, help="Calibration frames")
    return parser.parse_args()


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    args = parse_args()
    if not os.path.exists(args.model):
        print(f"Missing model file: {args.model}")
        return
    predictor = dlib.shape_predictor(args.model)
    known_encodings, known_names = load_known_faces(args.dataset)
    print(f"Loaded {len(known_names)} known faces.")
    if not known_encodings:
        print("No known encodings found. Add dataset images and rerun.")
        return
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"Cannot open camera {args.camera}")
        return
    print("Calibrating blink threshold... Keep eyes open")
    blink_threshold = calibrate_blink_threshold(cap, predictor, frames=args.calibrate)
    print(f"Blink threshold = {blink_threshold:.2f}")
    blink_counters = {}
    marked_today = set()
    last_attendance_text = ""
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Red instruction box at the top-left
        cv2.rectangle(frame, (10, 10), (310, 90), (0, 0, 255), 2)
        cv2.putText(frame, 'Blink to mark attendance', (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, 'Show your face and blink', (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 1)

        locations = face_recognition.face_locations(rgb, model='hog')
        encodings = face_recognition.face_encodings(rgb, locations)
        for i, ((top, right, bottom, left), encoding) in enumerate(zip(locations, encodings)):
            name = 'Unknown'
            if known_encodings:
                distances = face_recognition.face_distance(known_encodings, encoding)
                best_idx = np.argmin(distances)
                if distances[best_idx] <= args.tolerance:
                    name = known_names[best_idx]
            key = name if name != 'Unknown' else (left, top, right, bottom)
            ear = detect_ear(gray, dlib.rectangle(left, top, right, bottom), predictor)
            blink_counters.setdefault(key, 0)
            blinked = False
            if ear < blink_threshold:
                blink_counters[key] += 1
            else:
                if blink_counters[key] >= args.consecutive and name != 'Unknown':
                    blinked = True
                    if name not in marked_today:
                        date_str, time_str, marked = mark_attendance(name, args.output)
                        if marked:
                            marked_today.add(name)
                            last_attendance_text = f"Last marked: {name} {date_str} {time_str}"
                blink_counters[key] = 0
            color = (0, 255, 0) if name != 'Unknown' else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            box_label = f"{name} {'BLINK' if blinked else 'No Blink'} {ear:.2f}"
            cv2.putText(frame, box_label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            if name != 'Unknown' and not blinked:
                cv2.putText(frame, 'Please blink now', (left, bottom + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        if last_attendance_text:
            cv2.putText(frame, last_attendance_text, (10, frame.shape[0] - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.imshow("Attendance System", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == ord('r'):
            known_encodings, known_names = load_known_faces(args.dataset)
            print(f"Reloaded {len(known_names)} known faces.")
        if key == ord('s'):
            print("Marked today:", sorted(marked_today))
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
