from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from flask import current_app

from ..models import Attendance, Student


def build_attendance_query(filters: dict) -> list[Attendance]:
    query = Attendance.query.order_by(
        Attendance.attendance_date.desc(), Attendance.attendance_time.desc()
    )

    if filters.get("attendance_date"):
        query = query.filter(Attendance.attendance_date == filters["attendance_date"])
    if filters.get("class_id"):
        query = query.filter(Attendance.class_id == filters["class_id"])
    if filters.get("student_id"):
        query = query.filter(Attendance.student_id == filters["student_id"])

    return query.all()


def export_attendance_to_csv(records: list[Attendance], filename_prefix: str = "attendance_report") -> Path:
    export_folder = Path(current_app.config["EXPORT_FOLDER"])
    export_folder.mkdir(parents=True, exist_ok=True)
    file_path = export_folder / f"{filename_prefix}_{date.today().isoformat()}.csv"

    with file_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Student ID", "Student Name", "Class", "Section", "Date", "Time", "Status", "Confidence"])
        for record in records:
            writer.writerow([
                record.student.student_id,
                record.student.full_name,
                record.classroom.class_name,
                record.classroom.section,
                record.attendance_date.isoformat(),
                record.attendance_time.strftime("%H:%M:%S"),
                record.status,
                record.recognized_confidence or "",
            ])

    return file_path


def build_daily_summary(target_date) -> dict:
    present_records = Attendance.query.filter_by(attendance_date=target_date).all()
    present_student_ids = {record.student_id for record in present_records}
    total_students = Student.query.count()
    return {
        "present_count": len(present_student_ids),
        "absent_count": max(total_students - len(present_student_ids), 0),
        "records_count": len(present_records),
    }
