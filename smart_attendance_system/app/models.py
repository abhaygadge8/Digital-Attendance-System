from __future__ import annotations

from datetime import date, datetime

from werkzeug.security import check_password_hash, generate_password_hash

from .database import db


class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class ClassRoom(db.Model):
    __tablename__ = "classrooms"

    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(100), nullable=False)
    section = db.Column(db.String(30), nullable=False)
    subject = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    students = db.relationship(
        "Student", back_populates="classroom", cascade="all, delete-orphan"
    )
    attendance_records = db.relationship(
        "Attendance", back_populates="classroom", cascade="all, delete-orphan"
    )

    @property
    def display_name(self) -> str:
        return f"{self.class_name} - {self.section}"


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey("classrooms.id"), nullable=False)
    image_folder = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    classroom = db.relationship("ClassRoom", back_populates="students")
    face_encodings = db.relationship(
        "FaceEncoding", back_populates="student", cascade="all, delete-orphan"
    )
    attendance_records = db.relationship(
        "Attendance", back_populates="student", cascade="all, delete-orphan"
    )


class FaceEncoding(db.Model):
    __tablename__ = "face_encodings"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    encoding_file_path = db.Column(db.String(255), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    student = db.relationship("Student", back_populates="face_encodings")


class Attendance(db.Model):
    __tablename__ = "attendance"
    __table_args__ = (
        db.UniqueConstraint(
            "student_id", "class_id", "attendance_date", name="uq_daily_attendance"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey("classrooms.id"), nullable=False)
    attendance_date = db.Column(db.Date, default=date.today, nullable=False)
    attendance_time = db.Column(
        db.Time, default=lambda: datetime.utcnow().time(), nullable=False
    )
    status = db.Column(db.String(20), default="Present", nullable=False)
    recognized_confidence = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    student = db.relationship("Student", back_populates="attendance_records")
    classroom = db.relationship("ClassRoom", back_populates="attendance_records")
