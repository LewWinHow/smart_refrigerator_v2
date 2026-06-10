import os
import uuid
import cv2
import numpy as np
from django.conf import settings
from ultralytics import YOLO
import django

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_refrigerator_v2.settings')
django.setup()

# -----------------------------
# 1. Load YOLO model (fruit detection)
# -----------------------------
model = YOLO(os.path.join(settings.BASE_DIR, 'ai_model', 'yolo_model', 'yolo26m.pt'))

# -----------------------------
# 2. Specify classes to detect only
# -----------------------------
ALLOWED_CLASSES = [46, 47, 48, 49, 50, 51, 52, 53, 54, 55]

def detect_item(image):
    """
    Returns:
        label: Detected class name
        xyxy: Bounding box coordinates [x1, y1, x2, y2]
    If nothing is detected, returns (None, None)
    """

    # -----------------------------
    # Read image
    # -----------------------------
    if hasattr(image, 'read'):
        image_bytes = image.read()
        np_arr = np.frombuffer(image_bytes, np.uint8)
        cv_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        image.seek(0)
    elif isinstance(image, str):
        cv_image = cv2.imread(image)
        if cv_image is None:
            raise FileNotFoundError(f"Image not found at {image}")
    else:
        raise ValueError("Unsupported input type for image")

    # -----------------------------
    # YOLO inference (limit classes)
    # -----------------------------
    results = model(cv_image, classes=ALLOWED_CLASSES)[0]

    if len(results.boxes) == 0:
        return None, None

    # -----------------------------
    # Find the box with highest confidence
    # -----------------------------
    best_box, max_conf = None, 0
    for box in results.boxes:
        conf = float(box.conf.item())
        if conf >= 0.5 and conf > max_conf:
            max_conf = conf
            best_box = box

    if best_box is None:
        return None, None

    # -----------------------------
    # Get label and coordinates
    # -----------------------------
    label_index = int(best_box.cls.item())
    label = model.names[label_index]
    xyxy = best_box.xyxy[0].cpu().numpy().astype(int).tolist()

    return label, xyxy


# -----------------------------
# Test
# -----------------------------
if __name__ == '__main__':
    label, box = detect_item(r"C:\Users\xiaoh\Downloads\apple_158989157.jpg")
    print(label)
    print(box)