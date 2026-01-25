# get_face_embedding.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_refrigerator_v2.settings')
django.setup()
import cv2
import numpy as np
from insightface.app import FaceAnalysis

from user.models import FaceID

# 使用 buffalo_l 模型组合

app = FaceAnalysis(
    name='buffalo_s',
    providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
)
# ctx_id=0 表示用 GPU；ctx_id=-1 表示用 CPU
app.prepare(ctx_id=0, det_size=(640, 640))


def get_face_embedding(image):
    """
    从图像文件提取人脸 embedding
    参数可以是:
      - 文件路径 (str)
      - Django 上传文件对象 (request.FILES['profile_image'])
    """
    # 如果传的是文件路径
    if image is None:
        return None

    if isinstance(image, str):
        img = cv2.imread(image)

    # 如果传的是 Django 的上传文件对象
    else:
        file_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        image.seek(0)  # 读完后复位，否则后面request.FILES可能用不到文件

    faces = app.get(img)

    if len(faces) == 0:
        return None  # 没检测到人脸

    # 取第一张人脸
    face = faces[0]
    return face.normed_embedding  # 512维向量


def is_same_person(emb1, emb2, threshold=0.6):
    # 欧氏距离
    dist = np.linalg.norm(emb1 - emb2)
    return dist < threshold, dist


if __name__ == '__main__':
    embedding = get_face_embedding(
        r"C:\Users\xiaoh\Downloads\WhatsApp Unknown 2025-08-25 at 1.00.25 PM\WhatsApp Image 2025-08-24 at 6.51.29 PM.jpeg")
    face_identity = FaceIdentity(embedding=embedding, user_id=1)
    face_identity.set_embedding(embedding)
    face_identity.save()
