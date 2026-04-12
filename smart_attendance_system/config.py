from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        f"sqlite:///{(BASE_DIR / 'instance' / 'attendance.db').as_posix()}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER", str(BASE_DIR / "app" / "static" / "uploads")
    )
    DATASET_FOLDER = os.getenv("DATASET_FOLDER", str(BASE_DIR / "dataset" / "raw"))
    ENCODINGS_FOLDER = os.getenv(
        "ENCODINGS_FOLDER", str(BASE_DIR / "dataset" / "encodings")
    )
    EXPORT_FOLDER = os.getenv("EXPORT_FOLDER", str(BASE_DIR / "exports" / "reports"))
    FACE_RECOGNITION_TOLERANCE = float(
        os.getenv("FACE_RECOGNITION_TOLERANCE", "0.5")
    )
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}
