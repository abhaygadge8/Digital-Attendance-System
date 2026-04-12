from __future__ import annotations

from datetime import date, datetime

from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for
from sqlalchemy import or_

from .auth import login_required
from .database import db
from .forms import ClassRoomForm, StudentForm
from .models import Attendance, ClassRoom, Student
from .services.attendance_service import build_attendance_query, build_daily_summary, export_attendance_to_csv
from .services.student_service import create_student, delete_student, update_student


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    today = date.today()
    summary = build_daily_summary(today)
    stats = {
        "total_students": Student.query.count(),
        "total_classes": ClassRoom.query.count(),
        "today_attendance": summary["present_count"],
        "absent_count": summary["absent_count"],
    }
    recent_attendance = Attendance.query.order_by(Attendance.created_at.desc()).limit(10).all()
    return render_template("dashboard.html", stats=stats, recent_attendance=recent_attendance, summary=summary)


@main_bp.route("/students")
@login_required
def students():
    search = request.args.get("search", "").strip()
    class_filter = request.args.get("class_id", type=int)

    query = Student.query.join(ClassRoom)
    if search:
        query = query.filter(
            or_(
                Student.full_name.ilike(f"%{search}%"),
                Student.student_id.ilike(f"%{search}%"),
            )
        )
    if class_filter:
        query = query.filter(Student.class_id == class_filter)

    students_list = query.order_by(Student.created_at.desc()).all()
    classes = ClassRoom.query.order_by(ClassRoom.class_name.asc()).all()
    return render_template("students.html", students=students_list, classes=classes, search=search, selected_class=class_filter)


@main_bp.route("/students/add", methods=["GET", "POST"])
@login_required
def add_student():
    form = StudentForm()
    form.class_id.choices = [(c.id, c.display_name) for c in ClassRoom.query.all()]

    if not form.class_id.choices:
        flash("Create a class before adding students.", "warning")
        return redirect(url_for("main.classes"))

    if form.validate_on_submit():
        student = Student(
            student_id=form.student_id.data.strip(),
            full_name=form.full_name.data.strip(),
            email=form.email.data.strip().lower(),
            phone=form.phone.data.strip(),
            class_id=form.class_id.data,
        )
        create_student(student, form.images.data)
        flash("Student created successfully.", "success")
        return redirect(url_for("main.students"))

    return render_template("add_student.html", form=form)


@main_bp.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
@login_required
def edit_student(student_id: int):
    student = Student.query.get_or_404(student_id)
    form = StudentForm(obj=student)
    form.class_id.choices = [(c.id, c.display_name) for c in ClassRoom.query.all()]

    if form.validate_on_submit():
        update_student(
            student,
            {
                "student_id": form.student_id.data.strip(),
                "full_name": form.full_name.data.strip(),
                "email": form.email.data.strip().lower(),
                "phone": form.phone.data.strip(),
                "class_id": form.class_id.data,
            },
            form.images.data,
        )
        flash("Student updated successfully.", "success")
        return redirect(url_for("main.students"))

    return render_template("edit_student.html", form=form, student=student)


@main_bp.route("/students/<int:student_id>/delete", methods=["POST"])
@login_required
def remove_student(student_id: int):
    student = Student.query.get_or_404(student_id)
    delete_student(student)
    flash("Student deleted successfully.", "info")
    return redirect(url_for("main.students"))


@main_bp.route("/classes", methods=["GET", "POST"])
@login_required
def classes():
    form = ClassRoomForm()
    if form.validate_on_submit():
        classroom = ClassRoom(
            class_name=form.class_name.data.strip(),
            section=form.section.data.strip(),
            subject=form.subject.data.strip() if form.subject.data else None,
        )
        db.session.add(classroom)
        db.session.commit()
        flash("Class created successfully.", "success")
        return redirect(url_for("main.classes"))

    classes_list = ClassRoom.query.order_by(ClassRoom.created_at.desc()).all()
    return render_template("classes.html", form=form, classes=classes_list)


@main_bp.route("/classes/<int:class_id>/delete", methods=["POST"])
@login_required
def delete_class(class_id: int):
    classroom = ClassRoom.query.get_or_404(class_id)
    if classroom.students:
        flash("Cannot delete a class that still has students assigned.", "danger")
        return redirect(url_for("main.classes"))

    db.session.delete(classroom)
    db.session.commit()
    flash("Class removed successfully.", "info")
    return redirect(url_for("main.classes"))


@main_bp.route("/attendance")
@login_required
def attendance_records():
    filters = _extract_report_filters()
    records = build_attendance_query(filters)
    classes = ClassRoom.query.order_by(ClassRoom.class_name.asc()).all()
    students = Student.query.order_by(Student.full_name.asc()).all()
    return render_template("attendance.html", records=records, classes=classes, students=students, filters=filters)


@main_bp.route("/reports")
@login_required
def reports():
    filters = _extract_report_filters()
    records = build_attendance_query(filters)
    classes = ClassRoom.query.order_by(ClassRoom.class_name.asc()).all()
    students = Student.query.order_by(Student.full_name.asc()).all()
    summary = build_daily_summary(filters.get("attendance_date") or date.today())
    return render_template("reports.html", records=records, classes=classes, students=students, filters=filters, summary=summary)


@main_bp.route("/reports/export")
@login_required
def export_report():
    filters = _extract_report_filters()
    records = build_attendance_query(filters)
    if not records:
        flash("No attendance data found for the selected filters.", "warning")
        return redirect(url_for("main.reports"))

    export_path = export_attendance_to_csv(records)
    return send_file(export_path, as_attachment=True)


def _extract_report_filters() -> dict:
    attendance_date = request.args.get("attendance_date", "").strip()
    parsed_date = None
    if attendance_date:
        try:
            parsed_date = datetime.strptime(attendance_date, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "danger")

    return {
        "attendance_date": parsed_date,
        "class_id": request.args.get("class_id", type=int),
        "student_id": request.args.get("student_id", type=int),
    }
