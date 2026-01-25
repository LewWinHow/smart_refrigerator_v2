import os
import uuid
import cv2
import numpy as np
from django.conf import settings
from ultralytics import YOLO
import django
import torch
from torchvision import models, transforms

# 初始化 Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_refrigerator_v2.settings')
django.setup()

# -----------------------------
# 1. 加载 YOLO 模型 (水果检测)
# -----------------------------
model = YOLO(os.path.join(settings.BASE_DIR, 'ai_model', 'yolo_model', 'best.pt'))

# -----------------------------
# 2. 加载 EfficientNet (新鲜度分类)
# -----------------------------
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#
# efficientnet = models.efficientnet_b3(weights=None)
# efficientnet.classifier[1] = torch.nn.Linear(efficientnet.classifier[1].in_features, 8)
# efficientnet.load_state_dict(torch.load(
#     os.path.join(settings.BASE_DIR, 'ai_model', 'yolo_model', 'efficientnet_freshness_best.pth'),
#     map_location=device
# ))
# efficientnet = efficientnet.to(device)
# efficientnet.eval()

# # 支持的新鲜度类别
# freshness_classes = [
#     "Apple_Fresh", "Apple_NotFresh",
#     "Banana_Fresh", "Banana_NotFresh",
#     "Grape_Fresh", "Grape_NotFresh",
#     "Orange_Fresh", "Orange_NotFresh"
# ]

# 图像预处理
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# def classify_freshness(img, fruit_name):
#     """裁剪水果图像并用 EfficientNet 预测新鲜度"""
#     img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#     pil_img = transforms.ToPILImage()(img)
#     input_tensor = transform(pil_img).unsqueeze(0).to(device)
#
#     with torch.no_grad():
#         outputs = efficientnet(input_tensor)
#         probs = torch.nn.functional.softmax(outputs, dim=1)[0].cpu().numpy()
#
#     # 找到该水果对应的 2 个类别
#     if fruit_name == "Apple":
#         fresh, notfresh = probs[0], probs[1]
#     elif fruit_name == "Banana":
#         fresh, notfresh = probs[2], probs[3]
#     elif fruit_name == "Grape":
#         fresh, notfresh = probs[4], probs[5]
#     elif fruit_name == "Orange":
#         fresh, notfresh = probs[6], probs[7]
#     else:
#         return None, None  # 没有训练过的新鲜度
#
#     if fresh >= notfresh:
#         return "Fresh", fresh
#     else:
#         return "Not Fresh", notfresh

# -----------------------------
# 3. 主函数：YOLO 检测 + 新鲜度分类
# -----------------------------
def detect_item(image):
    """
    uploaded_input 可以是：
    1. request.FILES['image'] (InMemoryUploadedFile 或 TemporaryUploadedFile)
    2. 本地文件路径 (str)
    """

    # 获取文件扩展名
    if hasattr(image, 'name'):  # request.FILES['image']
        ext = os.path.splitext(image.name)[1]
    elif isinstance(image, str):  # 路径字符串
        ext = os.path.splitext(image)[1]
    else:
        raise ValueError("Invalid input type")

    unique_name = f"{uuid.uuid4().hex}{ext}"

    # 读取图像
    if hasattr(image, 'read'):  # request.FILES
        image_bytes = image.read()
        np_arr = np.frombuffer(image_bytes, np.uint8)
        cv_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        image.seek(0)  # 复位文件指针
    elif isinstance(image, str):  # 路径
        cv_image = cv2.imread(image)
        if cv_image is None:
            raise FileNotFoundError(f"Image not found at {image}")
    else:
        raise ValueError("Unsupported input type for image")

    # 运行 YOLO 检测
    results = model(cv_image)[0]

    if len(results.boxes) == 0:
        return None, None  # 没有检测到

    # 筛选置信度最高的框
    best_box, max_conf = None, 0
    for box in results.boxes:
        conf = float(box.conf.item())
        if conf > max_conf and conf >= 0.5:
            max_conf = conf
            best_box = box

    if best_box is None:
        return None, None

    # 获取标签
    label_index = int(best_box.cls.item())
    label = model.names[label_index]
    xyxy = best_box.xyxy[0].cpu().numpy().astype(int).tolist()

    # -----------------------------
    # 新鲜度检测
    # -----------------------------
    # freshness_label, freshness_prob = None, None
    # if label in ["Apple", "Banana", "Grape", "Orange"]:
    #     x1, y1, x2, y2 = xyxy
    #     crop_img = cv_image[y1:y2, x1:x2]
    #     if crop_img.size != 0:
    #         freshness_label, freshness_prob = classify_freshness(crop_img, label)
    #         if freshness_label is not None:
    #             freshness_prob = round(freshness_prob * 100, 2)  # 转成百分比
    #
    # if label == "Apple":
    #     return label, xyxy, 1 if freshness_label == 'Fresh' else 0, freshness_prob if freshness_prob else 0
    # else:
    return  label,xyxy

if __name__ == '__main__':
    label, box, freshness, freshness_percentage = detect_item(r"C:\Users\xiaoh\Downloads\apple_158989157.jpg")
    print(label)
    print(box)
    print(freshness)
    print(freshness_percentage)

