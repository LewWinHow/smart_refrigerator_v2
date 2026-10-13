import cv2
import requests
import time

DJANGO_URL = "http://127.0.0.1:8100/item/receive_and_detect_image/"

cap = cv2.VideoCapture(0)

# 请求摄像头使用 640x480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

FRAME_INTERVAL = 0.2

try:
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to read camera frame")
            break

        # 强制调整为 640x480
        frame = cv2.resize(frame, (640, 480))

        # 确认实际发送的图片尺寸
        height, width = frame.shape[:2]
        print(f"Sending image: {width}x{height}")

        # 编码为 JPEG
        success, img_encoded = cv2.imencode('.jpg', frame)

        if not success:
            print("Failed to encode image")
            continue

        img_bytes = img_encoded.tobytes()

        try:
            files = {
                'image': ('frame.jpg', img_bytes, 'image/jpeg')
            }

            data = {'connect': '1'}

            response = requests.post(
                DJANGO_URL,
                files=files,
                data=data,
                timeout=5
            )

            print(
                f"Status code: {response.status_code}, "
                f"Response: {response.text}"
            )

        except requests.RequestException as e:
            print("Send failed:", e)

        time.sleep(FRAME_INTERVAL)

except KeyboardInterrupt:
    try:
        requests.post(
            DJANGO_URL,
            data={'connect': '0'},
            timeout=5
        )
        print("Interrupt send successful")
    except requests.RequestException as e:
        print("Disconnection failed:", e)

finally:
    cap.release()
    cv2.destroyAllWindows()