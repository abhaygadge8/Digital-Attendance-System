# Cloud-Based Smart Attendance System with Face Recognition

This project is a Flask-based smart attendance system with:

- Admin login
- Student and class management
- Face image upload and webcam capture
- Face encoding generation
- Live face recognition
- Automatic attendance marking
- Attendance reports and CSV export

This README is written so anyone can set up and run the project on their own PC.

## Project Folder

Run the project from:

```text
smart_attendance_system
```

## Requirements

Install these on your PC first:

- Python 3.10 or Python 3.11
- Git Bash or PowerShell
- Webcam for face capture and recognition

For Windows face recognition support, you may also need:

- Visual Studio Build Tools
- CMake

## Setup Using Git Bash

Open Git Bash and go to the project folder:

```bash
cd "/c/amar doc/Digital-Attendance-System/smart_attendance_system"
```

## Create Virtual Environment

Create a virtual environment inside the project folder named `venv`:

```bash
python -m venv venv
```

Activate it:

```bash
source venv/Scripts/activate
```

If activation works, your terminal will show something like:

```text
(venv)
```

## Install Dependencies

Run these commands:

```bash
python -m pip install --upgrade pip wheel
python -m pip install "setuptools<81"
python -m pip install cmake
python -m pip install -r requirements.txt
```

Why `setuptools<81` is used:

- `face_recognition_models` depends on `pkg_resources`
- newer setuptools versions can break that import on Windows

## Create Environment File

Copy the sample environment file:

```bash
cp .env.example .env
```

## Initialize Database

Create the SQLite database:

```bash
python scripts/init_db.py
```

Create the default admin user:

```bash
python scripts/seed_admin.py
```

Default login:

- Username: `admin`
- Password: `admin123`

## Run the Project

Start the Flask app:

```bash
python app.py
```

Then open this URL in your browser:

```text
http://127.0.0.1:5000
```

## How to Use the Project

### 1. Login

Use the default admin account:

- Username: `admin`
- Password: `admin123`

### 2. Create a class

- Open `Classes`
- Add class name, section, and optional subject

### 3. Add a student

- Open `Students`
- Click `Add Student`
- Fill in student details
- Upload student face images

### 4. Generate face encodings

After adding student images, run:

```bash
python scripts/generate_encodings.py
```

### 5. Start face recognition

- Open `Camera`
- Click `Start Recognition`
- Show the registered face to the webcam

### 6. View attendance

- Open `Attendance`
- Open `Reports`
- Export CSV when needed

## Full Command List

If you want the complete setup and run flow in one place, use this exact order:

```bash
cd "/c/amar doc/Digital-Attendance-System/smart_attendance_system"
python -m venv venv
source venv/Scripts/activate
python -m pip install --upgrade pip wheel
python -m pip install "setuptools<81"
python -m pip install cmake
python -m pip install -r requirements.txt
cp .env.example .env
python scripts/init_db.py
python scripts/seed_admin.py
python scripts/generate_encodings.py
python app.py
```

## Run Again Later

Next time, you do not need full setup again. Just run:

```bash
cd "/c/amar doc/Digital-Attendance-System/smart_attendance_system"
source venv/Scripts/activate
python app.py
```

If you added new student images, run this before starting the app:

```bash
python scripts/generate_encodings.py
```

## Common Errors

### `source venv/Scripts/activate: No such file or directory`

The virtual environment does not exist yet. Create it first:

```bash
python -m venv venv
```

### `No module named flask_sqlalchemy`

Dependencies are not installed in the active virtual environment. Run:

```bash
python -m pip install -r requirements.txt
```

### `Please install face_recognition_models`

Usually fixed by:

```bash
python -m pip install "setuptools<81"
python -m pip install -r requirements.txt
```

### `dlib` fails to install on Windows

Install:

- Visual Studio Build Tools
- Desktop development with C++
- CMake

Then reinstall requirements.

# Cloud-Based Smart Attendance System with Face Recognition

This project is a beginner-friendly Flask application for managing student attendance using face recognition. It runs locally on Windows with SQLite, Flask, OpenCV, and `face_recognition`, while keeping the structure modular so it can later move to cloud-hosted databases and storage.

## Features

- Admin login and logout
- Dashboard with student, class, and attendance summary
- Student registration with class assignment
- Manual image upload for face dataset collection
- Webcam capture for student face registration
- Real-time face recognition camera page
- Automatic attendance marking with duplicate prevention
- Attendance filtering by date, class, and student
- CSV export for attendance reports
- SQLAlchemy ORM models for future database migration
- Environment-based configuration for cloud readiness

## Technology Stack

- Python 3.x
- Flask
- Flask-SQLAlchemy
- Flask-WTF
- SQLite
- OpenCV
- face_recognition
- NumPy
- HTML, CSS, JavaScript, Bootstrap 5

## Folder Structure

```text
smart_attendance_system/
│
├── app.py
├── requirements.txt
├── README.md
├── config.py
├── .env.example
├── instance/
│   └── attendance.db
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── auth.py
│   ├── attendance.py
│   ├── face_utils.py
│   ├── forms.py
│   ├── database.py
│   ├── services/
│   │   ├── student_service.py
│   │   ├── attendance_service.py
│   │   └── recognition_service.py
│   ├── templates/
│   └── static/
├── dataset/
│   ├── raw/
│   └── encodings/
├── scripts/
│   ├── init_db.py
│   ├── seed_admin.py
│   ├── generate_encodings.py
│   └── test_camera.py
└── exports/
    └── reports/
```

## Installation on Windows

1. Open the project folder in Visual Studio Code.
2. Open a terminal in:

```powershell
cd "c:\amar doc\Digital-Attendance-System\smart_attendance_system"
```

3. Create a virtual environment:

```powershell
python -m venv .venv
```

4. Activate it:

```powershell
.venv\Scripts\activate
```

5. Install dependencies:

```powershell
pip install -r requirements.txt
```

6. Copy environment variables:

```powershell
copy .env.example .env
```

## Database Setup

Initialize the SQLite database:

```powershell
python scripts\init_db.py
```

Seed the default admin account:

```powershell
python scripts\seed_admin.py
```

Default admin credentials:

- Username: `admin`
- Password: `admin123`

## Run the Project

```powershell
python app.py
```

Open in browser:

```text
http://127.0.0.1:5000
```

## How to Use

### 1. Create classes

- Login as admin
- Open `Classes`
- Add class name, section, and optional subject

### 2. Register students

- Open `Students`
- Click `Add Student`
- Fill in student details
- Upload multiple face images if available
- Save the student

### 3. Capture face images from webcam

- Open `Students`
- Click `Capture Face` for the student
- The desktop webcam window opens
- The app saves multiple images automatically when a face is detected
- Press `Q` to stop early if needed

### 4. Generate or refresh encodings manually

```powershell
python scripts\generate_encodings.py
```

### 5. Mark attendance using live recognition

- Open `Camera`
- Click `Start Recognition`
- The page streams annotated webcam frames
- When a known face is matched, attendance is marked once per student per day
- Unknown faces are labeled and ignored

### 6. View reports

- Open `Attendance` or `Reports`
- Filter by date, class, or student
- Export filtered records to CSV

## Configuration

Main settings are stored in `config.py` and can be overridden with `.env`:

- `SECRET_KEY`
- `SQLALCHEMY_DATABASE_URI`
- `UPLOAD_FOLDER`
- `DATASET_FOLDER`
- `ENCODINGS_FOLDER`
- `EXPORT_FOLDER`
- `FACE_RECOGNITION_TOLERANCE`

## Common Errors and Fixes

### 1. `face_recognition` fails to install on Windows

This package depends on `dlib`, which can be difficult on Windows.

Try:

```powershell
python -m pip install --upgrade pip wheel
python -m pip install "setuptools<81"
pip install cmake
pip install -r requirements.txt
```

If installation still fails, install Visual Studio Build Tools with `Desktop development with C++`, then retry. This project pins `setuptools<81` because `face_recognition_models` currently depends on `pkg_resources`.

### 2. Camera does not open

- Check that no other application is using the webcam
- Run `python scripts\test_camera.py`
- Confirm Windows camera permissions are enabled for desktop apps

### 3. No faces are recognized

- Make sure uploaded or captured images clearly show one face
- Run `python scripts\generate_encodings.py` after adding images
- Adjust `FACE_RECOGNITION_TOLERANCE` in `.env` if matching is too strict or too loose

### 4. Attendance not marked

- Attendance is intentionally blocked from duplicating for the same student, class, and day
- Check whether the student has already been marked present today

## Future Improvements

- Replace SQLite with MySQL or PostgreSQL through `SQLALCHEMY_DATABASE_URI`
- Move image storage to S3, Azure Blob, or Google Cloud Storage
- Add role-based access control
- Add scheduled absent marking and richer analytics
- Add REST APIs for mobile apps or remote camera devices
