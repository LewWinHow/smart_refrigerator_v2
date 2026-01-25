import os
import uuid
from django.core.files.storage import FileSystemStorage
from smart_refrigerator_v2 import settings

def save_image(image_file, sub_folder='uploads'):
    """
    保存上传的图像到 MEDIA_ROOT/sub_folder/ 下
    返回相对路径 (相对于 MEDIA_ROOT)，用于 ImageField 或数据库存储
    """
    # 保存目录
    save_dir = os.path.join(settings.MEDIA_ROOT, sub_folder)
    os.makedirs(save_dir, exist_ok=True)

    # 获取扩展名
    ext = os.path.splitext(image_file.name)[1]  # 用 .name 取文件名
    unique_filename = f"{uuid.uuid4().hex}{ext}"

    # 保存文件
    fs = FileSystemStorage(location=save_dir)
    fs.save(unique_filename, image_file)

    # 返回相对路径（相对于 MEDIA_ROOT）
    return os.path.join(sub_folder, unique_filename).replace("\\", "/")
