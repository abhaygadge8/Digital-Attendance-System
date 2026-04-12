from __future__ import annotations

from pathlib import Path

from werkzeug.utils import secure_filename

from ..database import db
from ..face_utils import create_student_image_folder, encode_student_faces
from ..models import FaceEncoding, Student


def create_student(student: Student, uploaded_files=None) -> Student:
    db.session.add(student)
    db.session.commit()

    student.image_folder = create_student_image_folder(student.student_id)
    db.session.commit()

    if uploaded_files:
        _save_student_uploads(student, uploaded_files)

    return student


def update_student(student: Student, form_data: dict, uploaded_files=None) -> Student:
    for key, value in form_data.items():
        setattr(student, key, value)

    if not student.image_folder:
        student.image_folder = create_student_image_folder(student.student_id)

    db.session.commit()

    if uploaded_files:
        _save_student_uploads(student, uploaded_files)

    return student


def delete_student(student: Student) -> None:
    if student.image_folder:
        folder_path = Path(student.image_folder)
        if folder_path.exists():
            for file in folder_path.glob("*"):
                if file.is_file():
                    file.unlink()
            try:
                folder_path.rmdir()
            except OSError:
                pass

    for encoding in student.face_encodings:
        encoding_path = Path(encoding.encoding_file_path)
        if encoding_path.exists():
            encoding_path.unlink()

    db.session.delete(student)
    db.session.commit()


def _save_student_uploads(student: Student, uploaded_files) -> None:
    folder_path = Path(student.image_folder)
    folder_path.mkdir(parents=True, exist_ok=True)

    for file in uploaded_files:
        if not file or not file.filename:
            continue
        file.save(folder_path / secure_filename(file.filename))

    FaceEncoding.query.filter_by(student_id=student.id).delete()
    db.session.commit()
    encode_student_faces(student)
