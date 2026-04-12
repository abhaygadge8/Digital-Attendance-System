from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.database import db
from app.face_utils import encode_student_faces
from app.models import FaceEncoding, Student


app = create_app()


with app.app_context():
    FaceEncoding.query.delete()
    db.session.commit()

    generated = 0
    for student in Student.query.all():
        files = encode_student_faces(student)
        generated += len(files)

    print(f"Encoding generation complete. Created {generated} encoding files.")
