import os
import cv2
import numpy as np
import django
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_refrigerator_v2.settings')
django.setup()

from user.models import FaceID
from user.models import User
import insightface
from insightface.app import FaceAnalysis

# Initialize InsightFace (load only once globally)
app = FaceAnalysis(name='buffalo_s', providers=['CUDAExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 480))


def preprocess_image(cv_image):
    """Uniformly scale to longest edge 640, simplify preprocessing"""
    h, w = cv_image.shape[:2]
    scale = 640 / max(h, w)
    new_w, new_h = int(w * scale), int(h * scale)
    resized = cv2.resize(cv_image, (new_w, new_h))
    return resized


def cosine_similarity(a, b):
    """Calculate cosine similarity, a, b must be normalized"""
    return np.dot(a, b)


def detect_face(image, similarity_threshold=0.5):
    """
    Detect face and return the most similar one (matched_name, box)
    Parameters:
      - image: File path (str) or Django uploaded file object (request.FILES['profile_image'])
    Returns:
      - matched_name: str ("unknown" or name)
      - box: list[int] (x1, y1, x2, y2)
    """
    # --- Read image ---
    if isinstance(image, str):
        cv_image = cv2.imread(image)
        if cv_image is None:
            raise FileNotFoundError(f"Cannot read image: {image}")
    elif isinstance(image, (InMemoryUploadedFile, TemporaryUploadedFile)):
        file_bytes = np.frombuffer(image.read(), np.uint8)
        cv_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        image.seek(0)
    else:
        raise TypeError("image must be str (path) or request.FILES['image']")

    # --- Preprocessing ---
    cv_image = preprocess_image(cv_image)

    # --- Face detection (detect only once) ---
    faces = app.get(cv_image)
    if len(faces) == 0:
        return None, None

    # --- Get database embeddings (load once) ---
    face_identity_list = FaceID.objects.all()
    db_embeddings, db_user_ids = [], []
    for f in face_identity_list:
        emb = f.get_embedding()
        if emb is not None:
            emb = emb / np.linalg.norm(emb)  # Normalize
            db_embeddings.append(emb)
            db_user_ids.append(f.user_id)

    if not db_embeddings:
        return None, None

    db_embeddings = np.array(db_embeddings)  # shape: (N, 512)

    # --- Match all detected faces ---
    best_match = {"name": "unknown", "box": faces[0].bbox.astype(int), "similarity": -1.0}

    for face in faces:
        detect_face_embedding = face.normed_embedding  # InsightFace already normalized
        box = face.bbox.astype(int)

        # Batch calculate similarity
        sims = np.dot(db_embeddings, detect_face_embedding)  # shape: (N,)
        best_idx = np.argmax(sims)
        best_sim = sims[best_idx]

        if best_sim >= similarity_threshold and best_sim > best_match["similarity"]:
            user = User.objects.filter(id=db_user_ids[best_idx]).first()
            best_match["name"] = user.username if user else "unknown"
            best_match["box"] = box
            best_match["similarity"] = best_sim

    return best_match["name"], best_match["box"]

# import ctypes
# ctypes.WinDLL("cublasLt64_12.dll")

