import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_refrigerator_v2.settings')
django.setup()
import uuid
import cv2
import numpy as np
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile


def draw_and_save_image(image, face_name, face_box, item_label, item_box, folders=None):
    """
    Read image (supports path or request.FILES['image']), draw boxes and labels, and save

    Parameters:
        image_input : str or request.FILES['image']
        x1, y1, x2, y2 : Box coordinates
        label_name : Label text
        folder : Subdirectory to save (default monitoring_display)

    Returns:
        Relative path (relative to MEDIA_ROOT), can be stored in database or returned to frontend
    """

    # --- Read image ---
    if isinstance(image, str):  # Path
        cv_image = cv2.imread(image)
        if cv_image is None:
            raise FileNotFoundError(f"Can not read image: {image}")
    elif isinstance(image, (InMemoryUploadedFile, TemporaryUploadedFile)):  # Uploaded file
        file_bytes = np.frombuffer(image.read(), np.uint8)
        cv_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        image.seek(0)  # Reset file pointer
    else:
        raise TypeError("image_input must be str (path) or request.FILES['image']")

    # --- Draw boxes and text ---
    if face_name is not None and face_box is not None:
        cv2.rectangle(cv_image, (face_box[0], face_box[1]), (face_box[2], face_box[3]), (0, 255, 0), 2)
        cv2.putText(cv_image, face_name, (face_box[0], face_box[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    if item_label is not None and item_box is not None:
        cv2.rectangle(cv_image, (item_box[0], item_box[1]), (item_box[2], item_box[3]), (0, 165, 255), 2)
        cv2.putText(cv_image, item_label, (item_box[0], item_box[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 165, 255), 2)

    # --- Save ---
    image_paths = {}
    for folder in folders:
        filename = f"{uuid.uuid4().hex}.jpg"
        save_dir = os.path.join(settings.MEDIA_ROOT, folder)
        os.makedirs(save_dir, exist_ok=True)
        abs_path = os.path.join(save_dir, filename)
        cv2.imwrite(abs_path, cv_image)

        # Return relative path (for database/frontend)
        rel_path = os.path.join(folder, filename).replace("\\", "/")
        image_paths[folder] = rel_path
    return image_paths

if __name__ == "__main__":
    face_box = [201,248,640,855]
    folders = ["item"]
    print(draw_and_save_image(r"C:\Users\xiaoh\Downloads\WhatsApp Unknown 2025-08-25 at 1.00.25 PM\WhatsApp Image 2025-08-24 at 6.51.29 PM.jpeg"
                              ,"Win How Lew",face_box,None,None,folders))
