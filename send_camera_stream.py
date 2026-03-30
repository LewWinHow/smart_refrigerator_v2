import cv2
import requests
import time

# 替换为你的 Django 服务器地址
DJANGO_URL = "http://127.0.0.1:8000/item/receive_and_detect_image/"

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

FRAME_INTERVAL = 0.2  # 每秒发送10帧

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法读取摄像头画面")
            break

        # 编码图像为 JPEG
        _, img_encoded = cv2.imencode('.jpg', frame)
        img_bytes = img_encoded.tobytes()

        try:
            files = {'image': ('frame.jpg', img_bytes, 'image/jpeg')}
            data = {'connect': '1'}
            response = requests.post(DJANGO_URL, files=files, data=data)
            print(f"状态码: {response.status_code}, 返回: {response.text}")
        except Exception as e:
            print("发送失败:", e)
        time.sleep(FRAME_INTERVAL)

except KeyboardInterrupt:
    # 通知断开连接
    try:
        response = requests.post(DJANGO_URL, data={'connect': '0'})
        print("中断发送成功")
    except Exception as e:
        print("断开连接失败:", e)
finally:
    cap.release()
