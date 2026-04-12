from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    import cv2
except ImportError:
    cv2 = None


if cv2 is None:
    print("OpenCV is not installed.")
else:
    camera = cv2.VideoCapture(0)
    if camera.isOpened():
        print("Camera opened successfully.")
        camera.release()
    else:
        print("Unable to open camera.")
