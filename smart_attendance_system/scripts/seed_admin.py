from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.database import db
from app.models import Admin


DEFAULT_USERNAME = "admin"
DEFAULT_EMAIL = "admin@example.com"
DEFAULT_PASSWORD = "admin123"


app = create_app()


with app.app_context():
    admin = Admin.query.filter_by(username=DEFAULT_USERNAME).first()
    if admin:
        print("Admin user already exists.")
    else:
        admin = Admin(username=DEFAULT_USERNAME, email=DEFAULT_EMAIL)
        admin.set_password(DEFAULT_PASSWORD)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user created. Username: {DEFAULT_USERNAME} | Password: {DEFAULT_PASSWORD}")
