# get_face_embedding.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_refrigerator_v2.settings')
django.setup()
import cv2
import numpy as np
from insightface.app import FaceAnalysis

from user.models import FaceID

# Use buffalo_l model combination

app = FaceAnalysis(
    name='buffalo_s',
    providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
)
# ctx_id=0 means use GPU; ctx_id=-1 means use CPU
app.prepare(ctx_id=0, det_size=(640, 640))


def get_face_embedding(image):
    """
    Extract face embedding from image file
    Parameters can be:
      - File path (str)
      - Django uploaded file object (request.FILES['profile_image'])
    """
    # If it's a file path
    if image is None:
        return None

    if isinstance(image, str):
        img = cv2.imread(image)

    # If it's a Django uploaded file object
    else:
        file_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        image.seek(0)  # Reset after reading, otherwise request.FILES might not be able to use the file later

    faces = app.get(img)

    if len(faces) == 0:
        return None  # No face detected

    # Take the first face
    face = faces[0]
    return face.normed_embedding  # 512-dimensional vector


def is_same_person(emb1, emb2, threshold=0.6):
    # Euclidean distance
    dist = np.linalg.norm(emb1 - emb2)
    return dist < threshold, dist


if __name__ == '__main__':
    embedding = get_face_embedding(
        r"C:\Users\xiaoh\Downloads\WhatsApp Unknown 2025-08-25 at 1.00.25 PM\WhatsApp Image 2025-08-24 at 6.51.29 PM.jpeg")
    face_identity = FaceIdentity(embedding=embedding, user_id=1)
    face_identity.set_embedding(embedding)
    face_identity.save()
