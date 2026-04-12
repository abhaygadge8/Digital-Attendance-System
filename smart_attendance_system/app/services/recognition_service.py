from datetime import date

from ..face_utils import load_all_known_encodings, mark_attendance_if_not_exists
from .attendance_service import build_daily_summary


def recognize_and_mark(student, confidence: float):
    return mark_attendance_if_not_exists(
        student=student,
        class_id=student.class_id,
        confidence=confidence,
        attendance_date=date.today(),
    )


def get_known_faces():
    return load_all_known_encodings()


def get_today_summary():
    return build_daily_summary(date.today())
