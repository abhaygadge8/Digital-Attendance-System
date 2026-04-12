from __future__ import annotations

import pickle
import time
from datetime import date, datetime
from pathlib import Path

import numpy as np
from flask import current_app
from werkzeug.utils import secure_filename

from .database import db
from .models import Attendance, FaceEncoding, Student

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None

FACE_IMPORT_ERROR = None

try:
    import face_recognition
except BaseException as exc:  # pragma: no cover
    face_recognition = None
    FACE_IMPORT_ERROR = str(exc)


def is_face_stack_available() -> bool:
    return cv2 is not None and face_recognition is not None


def create_student_image_folder(student_identifier: str) -> str:
    folder = Path(current_app.config["DATASET_FOLDER"]) / student_identifier
    folder.mkdir(parents=True, exist_ok=True)
    return str(folder)


def save_uploaded_images(student: Student, uploaded_files) -> list[str]:
    saved_paths = []
    folder = Path(student.image_folder or create_student_image_folder(student.student_id))
    folder.mkdir(parents=True, exist_ok=True)

    for file in uploaded_files:
        if not file or not file.filename:
            continue
        path = folder / secure_filename(file.filename)
        file.save(path)
        saved_paths.append(str(path))

    return saved_paths


def capture_faces_from_webcam(student: Student, image_count: int = 5) -> dict:
    if not is_face_stack_available():
        raise RuntimeError("OpenCV and face_recognition must be installed for webcam capture.")

    folder = Path(student.image_folder or create_student_image_folder(student.student_id))
    folder.mkdir(parents=True, exist_ok=True)

    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        raise RuntimeError("Unable to access webcam.")

    captured_paths = []
    last_saved = 0.0

    try:
        while len(captured_paths) < image_count:
            success, frame = camera.read()
            if not success:
                continue

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            locations = face_recognition.face_locations(rgb_frame)

            for top, right, bottom, left in locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            cv2.putText(
                frame,
                f"Captured: {len(captured_paths)}/{image_count}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )
            cv2.imshow("Capture Faces - Press Q to stop", frame)

            if locations and time.time() - last_saved > 0.7:
                image_path = folder / f"{student.student_id}_{len(captured_paths) + 1}.jpg"
                cv2.imwrite(str(image_path), frame)
                captured_paths.append(str(image_path))
                last_saved = time.time()

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()

    FaceEncoding.query.filter_by(student_id=student.id).delete()
    db.session.commit()
    encode_student_faces(student)

    return {"captured_count": len(captured_paths), "saved_paths": captured_paths}


def encode_student_faces(student: Student) -> list[str]:
    if face_recognition is None:
        raise RuntimeError("face_recognition must be installed to generate encodings.")

    folder = Path(student.image_folder or "")
    if not folder.exists():
        return []

    encodings_dir = Path(current_app.config["ENCODINGS_FOLDER"])
    encodings_dir.mkdir(parents=True, exist_ok=True)
    created_files = []

    for image_path in folder.glob("*"):
        if image_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue

        image = face_recognition.load_image_file(str(image_path))
        encodings = face_recognition.face_encodings(image)
        if not encodings:
            continue

        encoding_file = encodings_dir / f"{student.student_id}_{image_path.stem}.pkl"
        with encoding_file.open("wb") as handle:
            pickle.dump(encodings[0], handle)

        db.session.add(
            FaceEncoding(
                student_id=student.id,
                encoding_file_path=str(encoding_file),
                image_path=str(image_path),
            )
        )
        created_files.append(str(encoding_file))

    db.session.commit()
    return created_files


def load_all_known_encodings() -> dict:
    known_encodings = []
    labels = []
    students = []

    for record in FaceEncoding.query.join(Student).all():
        encoding_path = Path(record.encoding_file_path)
        if not encoding_path.exists():
            continue

        with encoding_path.open("rb") as handle:
            known_encodings.append(pickle.load(handle))
            labels.append(record.student.full_name)
            students.append(record.student)

    return {"encodings": known_encodings, "labels": labels, "students": students}


def recognize_faces_from_frame(frame, known_data: dict, tolerance: float | None = None) -> list[dict]:
    if not is_face_stack_available():
        raise RuntimeError("OpenCV and face_recognition must be installed for recognition.")

    tolerance = tolerance or current_app.config["FACE_RECOGNITION_TOLERANCE"]

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    matches = []
    known_encodings = known_data.get("encodings", [])

    for encoding, location in zip(face_encodings, face_locations):
        result = {
            "location": location,
            "label": "Unknown",
            "student": None,
            "confidence": None,
            "matched": False,
        }

        if known_encodings:
            distances = face_recognition.face_distance(known_encodings, encoding)
            best_match_index = int(np.argmin(distances))
            best_distance = float(distances[best_match_index])
            if best_distance <= tolerance:
                confidence = round(max(0.0, 1.0 - best_distance) * 100, 2)
                result.update(
                    {
                        "label": known_data["labels"][best_match_index],
                        "student": known_data["students"][best_match_index],
                        "confidence": confidence,
                        "matched": True,
                    }
                )

        matches.append(result)

    return matches


def mark_attendance_if_not_exists(student: Student, class_id: int, confidence: float | None, attendance_date=None):
    attendance_date = attendance_date or date.today()
    existing_record = Attendance.query.filter_by(
        student_id=student.id,
        class_id=class_id,
        attendance_date=attendance_date,
    ).first()
    if existing_record:
        return existing_record, False

    new_record = Attendance(
        student_id=student.id,
        class_id=class_id,
        attendance_date=attendance_date,
        attendance_time=datetime.now().time().replace(microsecond=0),
        status="Present",
        recognized_confidence=confidence,
    )
    db.session.add(new_record)
    db.session.commit()
    return new_record, True
