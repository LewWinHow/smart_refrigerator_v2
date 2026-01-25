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

# 初始化 InsightFace（全局只加载一次）
app = FaceAnalysis(name='buffalo_s', providers=['CUDAExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 480))


def preprocess_image(cv_image):
    """统一缩放到最长边 640，简化预处理"""
    h, w = cv_image.shape[:2]
    scale = 640 / max(h, w)
    new_w, new_h = int(w * scale), int(h * scale)
    resized = cv2.resize(cv_image, (new_w, new_h))
    return resized


def cosine_similarity(a, b):
    """计算余弦相似度，a, b 必须归一化"""
    return np.dot(a, b)


def detect_face(image, similarity_threshold=0.5):
    """
    检测人脸并返回最相似的一个 (matched_name, box)
    参数:
      - image: 文件路径 (str) 或 Django 上传文件对象 (request.FILES['profile_image'])
    返回:
      - matched_name: str ("unknown" 或 姓名)
      - box: list[int] (x1, y1, x2, y2)
    """
    # --- 读取图像 ---
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

    # --- 预处理 ---
    cv_image = preprocess_image(cv_image)

    # --- 人脸检测（只检测一次） ---
    faces = app.get(cv_image)
    if len(faces) == 0:
        return None, None

    # --- 取数据库 embeddings（一次性加载） ---
    face_identity_list = FaceID.objects.all()
    db_embeddings, db_user_ids = [], []
    for f in face_identity_list:
        emb = f.get_embedding()
        if emb is not None:
            emb = emb / np.linalg.norm(emb)  # 归一化
            db_embeddings.append(emb)
            db_user_ids.append(f.user_id)

    if not db_embeddings:
        return None, None

    db_embeddings = np.array(db_embeddings)  # shape: (N, 512)

    # --- 匹配所有检测到的人脸 ---
    best_match = {"name": "unknown", "box": faces[0].bbox.astype(int), "similarity": -1.0}

    for face in faces:
        detect_face_embedding = face.normed_embedding  # InsightFace 已归一化
        box = face.bbox.astype(int)

        # 批量计算相似度
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

