from __future__ import annotations

from threading import Lock

from flask import Blueprint, Response, current_app, flash, jsonify, redirect, render_template, stream_with_context, url_for

from .auth import login_required
from .face_utils import capture_faces_from_webcam, is_face_stack_available, recognize_faces_from_frame
from .models import Student
from .services.recognition_service import get_known_faces, get_today_summary, recognize_and_mark

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None


attendance_bp = Blueprint("attendance_module", __name__, url_prefix="/camera")

recognition_state = {"running": False, "last_event": "Recognition idle."}
state_lock = Lock()


@attendance_bp.route("/")
@login_required
def camera_page():
    return render_template(
        "capture.html",
        recognition_available=is_face_stack_available(),
        recognition_state=recognition_state,
        summary=get_today_summary(),
    )


@attendance_bp.route("/capture/<int:student_id>", methods=["POST"])
@login_required
def capture_student_faces(student_id: int):
    student = Student.query.get_or_404(student_id)
    try:
        result = capture_faces_from_webcam(student)
        flash(f"Captured {result['captured_count']} face images for {student.full_name}.", "success")
    except Exception as exc:  # pragma: no cover
        flash(str(exc), "danger")
    return redirect(url_for("main.students"))


@attendance_bp.route("/start", methods=["POST"])
@login_required
def start_recognition():
    with state_lock:
        recognition_state["running"] = True
        recognition_state["last_event"] = "Recognition started."
    return jsonify({"status": "started"})


@attendance_bp.route("/stop", methods=["POST"])
@login_required
def stop_recognition():
    with state_lock:
        recognition_state["running"] = False
        recognition_state["last_event"] = "Recognition stopped."
    return jsonify({"status": "stopped"})


@attendance_bp.route("/status")
@login_required
def recognition_status():
    return jsonify({**recognition_state, "summary": get_today_summary()})


@attendance_bp.route("/stream")
@login_required
def recognition_stream():
    if not is_face_stack_available():
        flash("Recognition stack is not installed. Please install OpenCV and face_recognition.", "danger")
        return redirect(url_for("attendance_module.camera_page"))

    return Response(
        stream_with_context(_frame_generator()),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


def _frame_generator():
    known_data = get_known_faces()
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        raise RuntimeError("Unable to access webcam.")

    try:
        while True:
            with state_lock:
                running = recognition_state["running"]

            success, frame = camera.read()
            if not success:
                continue

            if running:
                matches = recognize_faces_from_frame(
                    frame,
                    known_data=known_data,
                    tolerance=current_app.config["FACE_RECOGNITION_TOLERANCE"],
                )

                for match in matches:
                    top, right, bottom, left = match["location"]
                    color = (0, 180, 0) if match["matched"] else (0, 0, 255)
                    label = match["label"]

                    if match["matched"] and match["student"] is not None:
                        _, created = recognize_and_mark(match["student"], match["confidence"])
                        status_text = "Attendance marked" if created else "Already marked today"
                        label = f"{label} ({match['confidence']}%) - {status_text}"
                    else:
                        label = "Unknown face detected"

                    with state_lock:
                        recognition_state["last_event"] = label

                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                    cv2.putText(
                        frame,
                        label[:45],
                        (left + 6, bottom - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 255, 255),
                        1,
                    )
            else:
                cv2.putText(frame, "Recognition paused", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)

            success, buffer = cv2.imencode(".jpg", frame)
            if not success:
                continue

            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
    finally:
        camera.release()
