from __future__ import annotations

from pathlib import Path

from flask import Flask

from config import Config

from .database import db


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    _ensure_directories(app)
    db.init_app(app)

    from .auth import auth_bp
    from .attendance import attendance_bp
    from .routes import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(attendance_bp)

    with app.app_context():
        db.create_all()

    return app


def _ensure_directories(app: Flask) -> None:
    for key in ("UPLOAD_FOLDER", "DATASET_FOLDER", "ENCODINGS_FOLDER", "EXPORT_FOLDER"):
        Path(app.config[key]).mkdir(parents=True, exist_ok=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
